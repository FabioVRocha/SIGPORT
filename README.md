# SIGPORT - Sistema Integrado de Gestão de Portaria

Este repositório contém um esqueleto de aplicação web baseada em Flask para o sistema **SIGPORT**. O banco de dados utilizado é PostgreSQL 9.3 e os modelos principais seguem a descrição abaixo:

- **Registro de Entrada** (`Entry`)
- **Registro de Saída** (`Exit`)
- **Agendamento de Saída** (`Schedule`)
- **Usuários** (`User`)

A aplicação disponibiliza endpoints REST simples para criação de usuários, registros de entrada/saída e agendamentos.

## Como executar

1. Configure a variável `DATABASE_URI` com a string de conexão para o PostgreSQL (exemplo: `postgresql://user:password@localhost/sigport_db`).
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Inicie a aplicação:

```bash
python app.py
```

Ao iniciar, a base de dados é criada automaticamente caso não exista.