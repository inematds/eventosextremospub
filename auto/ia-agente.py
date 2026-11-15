#!/usr/bin/env python3
"""Executa uma etapa de agente; o modelo precisa ler/escrever e executar ferramentas."""
import argparse, sys
from pathlib import Path
from ia_motor import executar
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('etapa'); p.add_argument('pedido')
p.add_argument('--permission-mode', choices=['bypassPermissions'])
p.add_argument('--add-dir')
a=p.parse_args()
try:
    print(executar(a.etapa, a.pedido, Path.cwd(), agente=True))
except Exception as e:
    print('IA: '+str(e), file=sys.stderr); sys.exit(1)
