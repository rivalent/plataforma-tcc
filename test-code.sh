#!/bin/bash
echo "Instalando dependências e criando ambiente virtual do python:"
python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt

echo "Iniciando testes unitários"
PYTHONPATH=. pytest tests/unit/ -v -W ignore
echo "Testes unitários finalizados"
deactivate
