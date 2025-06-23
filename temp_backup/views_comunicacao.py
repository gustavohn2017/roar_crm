import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.conf import settings

from .models import Lead
from .models_comunicacao import TemplateWhatsApp, TemplateEmail, HistoricoContato
from .forms_comunicacao import EnviarWhatsAppForm, EnviarEmailForm, RegistrarContatoForm


@login_required
def enviar_whatsapp(request, lead_id):
    """Envia mensagem de WhatsApp para um lead."""
    lead = get_object_or_404(Lead, id=lead_id)
    
    if not lead.whatsapp:
        messages.error(request, "Este lead não possui número de WhatsApp cadastrado.")
        return redirect('detalhes_lead', lead_id=lead.id)
    
    templates = TemplateWhatsApp.objects.all()
    
    if request.method == 'POST':
        form = EnviarWhatsAppForm(request.POST)
        if form.is_valid():
            template = form.cleaned_data.get('template')
            mensagem = form.cleaned_data.get('mensagem')
            
            if template and not mensagem:
                mensagem = template.conteudo
            
            # Personalizar a mensagem com informações do lead
            mensagem = personalizar_mensagem(mensagem, lead)
            
            # Implementação da API de WhatsApp - neste exemplo usando redirecionamento para WhatsApp Web
            whatsapp_number = lead.whatsapp.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
            
            # Registrar o contato no histórico
            contato = HistoricoContato.objects.create(
                lead=lead,
                tipo='whatsapp',
                conteudo=mensagem,
                responsavel=request.user
            )
            
            # Atualizar informações do lead
            lead.data_ultimo_contato = timezone.now()
            lead.save()
            
            messages.success(request, f"Mensagem de WhatsApp preparada para {lead.nome}.")
            
            # Formato do link do WhatsApp
            whatsapp_link = f"https://wa.me/55{whatsapp_number}?text={requests.utils.quote(mensagem)}"
            
            return render(request, 'leads/whatsapp_redirect.html', {
                'lead': lead,
                'whatsapp_link': whatsapp_link,
                'mensagem': mensagem
            })
    else:
        form = EnviarWhatsAppForm()
    
    return render(request, 'leads/enviar_whatsapp.html', {
        'form': form,
        'lead': lead,
        'templates': templates,
    })


@login_required
def enviar_email(request, lead_id):
    """Envia e-mail para um lead."""
    lead = get_object_or_404(Lead, id=lead_id)
    
    if not lead.email:
        messages.error(request, "Este lead não possui e-mail cadastrado.")
        return redirect('detalhes_lead', lead_id=lead.id)
    
    templates = TemplateEmail.objects.all()
    
    if request.method == 'POST':
        form = EnviarEmailForm(request.POST)
        if form.is_valid():
            template = form.cleaned_data.get('template')
            assunto = form.cleaned_data.get('assunto')
            corpo = form.cleaned_data.get('corpo')
            
            if template:
                if not assunto:
                    assunto = template.assunto
                if not corpo:
                    corpo = template.conteudo_html
                    corpo_texto = template.conteudo_texto
            
            # Personalizar o assunto e corpo com informações do lead
            assunto = personalizar_mensagem(assunto, lead)
            corpo = personalizar_mensagem(corpo, lead)
            
            # Enviar o e-mail
            try:
                email = EmailMultiAlternatives(
                    subject=assunto,
                    body=corpo_texto if 'corpo_texto' in locals() else '',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[lead.email],
                )
                
                if corpo:
                    email.attach_alternative(corpo, "text/html")
                
                email.send()
                
                # Registrar o contato no histórico
                contato = HistoricoContato.objects.create(
                    lead=lead,
                    tipo='email',
                    conteudo=f"Assunto: {assunto}\n\n{corpo}",
                    responsavel=request.user
                )
                
                # Atualizar informações do lead
                lead.data_ultimo_contato = timezone.now()
                lead.save()
                
                messages.success(request, f"E-mail enviado com sucesso para {lead.email}.")
                return redirect('detalhes_lead', lead_id=lead.id)
            except Exception as e:
                messages.error(request, f"Erro ao enviar e-mail: {str(e)}")
    else:
        form = EnviarEmailForm()
    
    return render(request, 'leads/enviar_email.html', {
        'form': form,
        'lead': lead,
        'templates': templates,
    })


@login_required
def historico_contatos(request, lead_id):
    """Exibe o histórico de contatos com um lead."""
    lead = get_object_or_404(Lead, id=lead_id)
    contatos = lead.historico_contatos.all().order_by('-data')
    
    if request.method == 'POST':
        form = RegistrarContatoForm(request.POST)
        if form.is_valid():
            contato = form.save(commit=False)
            contato.lead = lead
            contato.responsavel = request.user
            contato.save()
            
            # Atualizar informações do lead
            lead.data_ultimo_contato = timezone.now()
            lead.save()
            
            messages.success(request, "Contato registrado com sucesso.")
            return redirect('historico_contatos', lead_id=lead.id)
    else:
        form = RegistrarContatoForm()
    
    return render(request, 'leads/historico_contatos.html', {
        'lead': lead,
        'contatos': contatos,
        'form': form,
    })


@login_required
def gerenciar_templates(request, tipo):
    """Gerenciar templates de WhatsApp ou e-mail."""
    if tipo == 'whatsapp':
        templates = TemplateWhatsApp.objects.all()
        titulo = "Gerenciar Templates de WhatsApp"
    elif tipo == 'email':
        templates = TemplateEmail.objects.all()
        titulo = "Gerenciar Templates de E-mail"
    else:
        messages.error(request, "Tipo de template inválido.")
        return redirect('lista_leads')
    
    return render(request, 'leads/gerenciar_templates.html', {
        'templates': templates,
        'tipo': tipo,
        'titulo': titulo,
    })


def personalizar_mensagem(mensagem, lead):
    """Substitui placeholders por informações do lead na mensagem."""
    if not mensagem:
        return ""
    
    # Substitui os placeholders básicos
    substituicoes = {
        '{nome}': lead.nome,
        '{telefone}': lead.telefone or '',
        '{email}': lead.email or '',
        '{empresa}': lead.empresa or '',
        '{interesse}': dict(Lead.INTEREST_CHOICES).get(lead.interesse, ''),
        '{valor_interesse}': str(lead.valor_interesse) if lead.valor_interesse else '',
        '{responsavel}': lead.responsavel.get_full_name() if lead.responsavel else '',
    }
    
    for placeholder, valor in substituicoes.items():
        mensagem = mensagem.replace(placeholder, valor)
    
    return mensagem


@login_required
def get_template_content(request):
    """API para obter o conteúdo de um template."""
    template_id = request.GET.get('id')
    tipo = request.GET.get('tipo')
    
    if not template_id or not tipo:
        return JsonResponse({'error': 'Parâmetros inválidos'}, status=400)
    
    try:
        if tipo == 'whatsapp':
            template = TemplateWhatsApp.objects.get(id=template_id)
            return JsonResponse({
                'conteudo': template.conteudo
            })
        elif tipo == 'email':
            template = TemplateEmail.objects.get(id=template_id)
            return JsonResponse({
                'assunto': template.assunto,
                'conteudo': template.conteudo_html,
                'conteudo_texto': template.conteudo_texto or ''
            })
        else:
            return JsonResponse({'error': 'Tipo de template inválido'}, status=400)
    except (TemplateWhatsApp.DoesNotExist, TemplateEmail.DoesNotExist):
        return JsonResponse({'error': 'Template não encontrado'}, status=404)
