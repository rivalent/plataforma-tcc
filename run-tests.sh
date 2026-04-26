#!/bin/bash
echo "iniciando testes de integração"
sleep 5
pytest tests/integration/ -v -W ignore
echo "testes de integração finalizados"
