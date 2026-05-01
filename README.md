# plataforma-tcc

Projeto de conclusão de curso que implementa uma plataforma composta por serviços independentes para:
- cadastro de clientes
- cadastro de produtos
- cotações de moedas estrangeiras
- controle de vendas

Cada serviço expõe API REST e segue arquitetura em camadas: domínio, serviço, repositório e API.
Todas as respostas são formatadas em JSON com campos de mensagem, timestamp, elapsed e erro quando houver.

## Serviços implementados

1. **Clientes**
   - cadastrar cliente
   - alterar cliente
   - inativar cliente (delete lógico)
   - listar clientes

2. **Produtos**
   - cadastrar produto
   - alterar produto
   - inativar produto
   - listar produtos com preços convertidos em moedas disponíveis
   - filtrar por preço, nome/descrição e quantidade em estoque

3. **Cotações**
   - consultar cotação BRLxEUR, BRLxUSD, BRLxGBP e BRLxCNY
   - consultar cotação de uma moeda específica ou todas as moedas
   - cache diário para reduzir consultas à API externa

4. **Vendas**
   - criar venda para cliente
   - incluir e alterar produtos na venda
   - validar disponibilidade de estoque via API de produtos
   - efetivar venda e atualizar estoque
   - retornar total em todas as moedas disponíveis
   - consultar vendas por produto, estado e cancelar vendas

## Arquitetura e Decisões de Design

- **Isolamento de Contêineres:** Cada microsserviço opera de forma 100% independente em seu próprio contêiner Docker, garantindo que a falha de um não derrube o sistema inteiro.

- **Banco por Serviço:** Para garantir o desacoplamento real, cada API gerencia seu próprio banco de dados de forma isolada.

- **Padronização de Contratos (API):** Todas as requisições retornam um JSON padronizado contendo `mensagem`, `timestamp`, `elapsed` e `erro`, facilitando a integração com qualquer Front-end.

- **Observabilidade:** O sistema conta com logs estruturados em formato tabulado (com timestamp ISO 8601) para rastrear o comportamento dos serviços em tempo real.

- **Arquitetura Limpa:** O código interno separa estritamente as regras de negócio (Domínio/Serviço) das tecnologias externas (Repositório/API).

# Como testar

## Pré-requisitos (Dependências de Sistema)

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas na sua máquina:
- **Git** (para clonar o repositório)
- **Python 3** (para executar os testes localmente)
- **Docker** e **Docker Compose** (para rodar a plataforma)

## Para rodar os testes unitários

Execute o script na raiz do projeto:

```bash
./test-code.sh
```

## Como iniciar o ambiente com Docker

Subir todos os serviços e infraestrutura com o Docker Compose:

```bash
docker compose up
```

## Para rodar os testes de integração (Precisar do Docker ativo)

Execute o script na raiz do projeto:

```bash
./run-tests.sh
```

## Acessando as APIs (Swagger UI)
Com os contêineres rodando, você pode testar cada serviço de maneira simples e interativa pelo navegador através de suas documentações automáticas:

- API Clientes: http://localhost:8001/docs

- API Produtos: http://localhost:8002/docs

- API Cotações: http://localhost:8003/docs

- API Vendas: http://localhost:8004/docs