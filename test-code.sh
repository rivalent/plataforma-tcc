#!/bin/bash
echo "Instalando dependências do python:"
pip install -q -r requirements.txt

echo "Iniciando testes unitários"
PYTHONPATH=. pytest tests/unit/ -v
echo "Testes unitários finalizados"
