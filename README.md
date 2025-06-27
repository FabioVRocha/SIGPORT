# SIGPORT - Sistema Integrado de Gestão de Portaria

Este repositório contém um esqueleto de aplicação web baseada em Flask para o sistema **SIGPORT**. O banco de dados utilizado é PostgreSQL 9.3 e os modelos principais seguem a descrição abaixo:

- **Registro de Entrada** (`Entry`)
- **Registro de Saída** (`Exit`)
- **Agendamento de Saída** (`Schedule`)
- **Usuários** (`User`)

A aplicação disponibiliza endpoints REST para cadastro de usuários, registros de entrada e saída e agendamentos. A criação da saída só é permitida a partir de uma entrada existente e cada entrada pode possuir apenas uma saída.

## Como executar

1. Configure a variável `DATABASE_URI` com a string de conexão para o PostgreSQL (exemplo: `postgresql://usuario:senha@localhost/sigport_db`). Caso a senha possua caracteres especiais, utilize percent-encoding.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Inicie a aplicação:

```bash
python app.py
```

Por padrão a aplicação executa em `http://localhost:5000`. Ajuste a variável `DATABASE_URI` caso o PostgreSQL esteja em outro host.

Ao iniciar, a base de dados é criada automaticamente caso não exista.

## Endpoints principais

- `POST /users` – cria um usuário
- `POST /login` – autentica usuário
- `POST /entries` – registra uma entrada (placa não pode possuir outra entrada aberta)
- `POST /entries/<id>/exit` – registra a saída a partir de uma entrada
- `POST /schedules` – cria um agendamento de saída
- `POST /schedules/<id>/create_exit` – converte agendamento em saída
- `GET /entries` – lista entradas
- `GET /exits` – lista saídas
- `GET /schedules` – lista agendamentos