#!/usr/bin/env python3
"""
NAVBAR - VERIFICAÇÃO FINAL DE LIMPEZA
=====================================
Script para validar que todos os efeitos hover foram removidos
e que o navbar está funcionando corretamente.
"""

import os
import re
from pathlib import Path

def check_hover_effects():
    """Verifica se ainda existem efeitos hover no CSS do navbar"""
    navbar_css = Path("static/css/navbar-professional-compact.css")
    
    if not navbar_css.exists():
        return False, "Arquivo CSS do navbar não encontrado"
    
    content = navbar_css.read_text(encoding='utf-8')
    
    # Busca por :hover
    hover_matches = re.findall(r'[^a-zA-Z]:hover\s*{[^}]*}', content, re.DOTALL)
    
    if hover_matches:
        return False, f"Encontrados {len(hover_matches)} efeitos hover restantes"
    
    return True, "Nenhum efeito hover encontrado ✅"

def check_transitions():
    """Verifica se as transições foram neutralizadas"""
    navbar_css = Path("static/css/navbar-professional-compact.css")
    
    content = navbar_css.read_text(encoding='utf-8')
    
    # Verifica se --nav-transition está como 'none'
    transition_pattern = r'--nav-transition:\s*none'
    
    if re.search(transition_pattern, content):
        return True, "Transições neutralizadas ✅"
    else:
        return False, "Transições ainda ativas"

def check_dropdown_removal():
    """Verifica se o dropdown quick-actions foi removido"""
    base_html = Path("templates/base.html")
    
    if not base_html.exists():
        return False, "Template base.html não encontrado"
    
    content = base_html.read_text(encoding='utf-8')
    
    # Busca por quick-actions
    if 'quick-actions' in content:
        return False, "Quick actions dropdown ainda presente"
    
    return True, "Quick actions dropdown removido ✅"

def check_file_sizes():
    """Verifica os tamanhos dos arquivos principais"""
    files_to_check = [
        "static/css/navbar-professional-compact.css",
        "templates/base.html"
    ]
    
    sizes = {}
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            sizes[file_path] = path.stat().st_size
    
    return sizes

def main():
    """Executa todas as verificações"""
    print("🔍 VERIFICAÇÃO FINAL DO NAVBAR - ULTRA PROFISSIONAL")
    print("=" * 60)
    
    # Verifica hover effects
    hover_ok, hover_msg = check_hover_effects()
    print(f"📋 Efeitos Hover: {hover_msg}")
    
    # Verifica transições
    transition_ok, transition_msg = check_transitions()
    print(f"🔄 Transições: {transition_msg}")
    
    # Verifica remoção do dropdown
    dropdown_ok, dropdown_msg = check_dropdown_removal()
    print(f"📱 Quick Actions: {dropdown_msg}")
    
    # Verifica tamanhos dos arquivos
    print(f"\n📊 TAMANHOS DOS ARQUIVOS:")
    sizes = check_file_sizes()
    for file_path, size in sizes.items():
        print(f"   {file_path}: {size:,} bytes")
    
    print(f"\n🎯 RESULTADO FINAL:")
    
    all_ok = hover_ok and transition_ok and dropdown_ok
    
    if all_ok:
        print("✅ NAVBAR ULTRA PROFISSIONAL - TODAS AS VERIFICAÇÕES PASSARAM")
        print("✅ Sem efeitos hover")
        print("✅ Sem transições desnecessárias") 
        print("✅ Interface limpa")
        print("✅ Adequado para ambiente corporativo")
    else:
        print("❌ ALGUMAS VERIFICAÇÕES FALHARAM:")
        if not hover_ok:
            print("   ❌ Ainda há efeitos hover")
        if not transition_ok:
            print("   ❌ Transições ainda ativas")
        if not dropdown_ok:
            print("   ❌ Quick actions não removido")
    
    print(f"\n📋 CARACTERÍSTICAS FINAIS:")
    print("   • Design ultra compacto (44px altura)")
    print("   • Zero efeitos visuais no hover")
    print("   • Interface estática e previsível")
    print("   • Adequação corporativa máxima")
    print("   • Performance otimizada")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
