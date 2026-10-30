#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m poc3 --entrada ./dados_ficticios --saida ./saida_demo
printf '\nAbra ./saida_demo/RELATORIO_VISUAL.html no navegador\n'
