from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemplateWhatsApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome do template')),
                ('conteudo', models.TextField(verbose_name='Conteúdo da mensagem')),
                ('pode_personalizar', models.BooleanField(default=True, verbose_name='Permite personalização')),
                ('data_criacao', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Template de WhatsApp',
                'verbose_name_plural': 'Templates de WhatsApp',
            },
        ),
        migrations.CreateModel(
            name='TemplateEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome do template')),
                ('assunto', models.CharField(max_length=200, verbose_name='Assunto')),
                ('conteudo_html', models.TextField(verbose_name='Conteúdo HTML')),
                ('conteudo_texto', models.TextField(blank=True, null=True, verbose_name='Conteúdo em texto plano')),
                ('pode_personalizar', models.BooleanField(default=True, verbose_name='Permite personalização')),
                ('data_criacao', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Template de E-mail',
                'verbose_name_plural': 'Templates de E-mail',
            },
        ),
        migrations.CreateModel(
            name='HistoricoContato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('whatsapp', 'WhatsApp'), ('email', 'E-mail'), ('telefone', 'Telefone'), ('reuniao', 'Reunião'), ('outro', 'Outro')], max_length=20, verbose_name='Tipo de contato')),
                ('data', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data do contato')),
                ('conteudo', models.TextField(verbose_name='Conteúdo da mensagem/conversa')),
                ('foi_respondido', models.BooleanField(default=False, verbose_name='Foi respondido')),
                ('data_resposta', models.DateTimeField(blank=True, null=True, verbose_name='Data da resposta')),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historico_contatos', to='leads.lead')),
                ('responsavel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contatos_realizados', to='auth.user')),
            ],
            options={
                'verbose_name': 'Histórico de Contato',
                'verbose_name_plural': 'Histórico de Contatos',
                'ordering': ['-data'],
            },
        ),
    ]
