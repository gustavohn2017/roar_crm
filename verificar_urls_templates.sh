#!/bin/bash
echo 'Iniciando verificacao de URLs em templates...'
echo
python scan_templates_for_urls.py
echo
read -p 'Pressione Enter para continuar...'
