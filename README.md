# SIGPORT - Sistema Integrado de Gestão de Portaria

![Apresentação](docs/apresentacao.gif)

SIGPORT e um sistema web responsivo para controle de portaria. O sistema foi projetado para uso em dispositivos Android e utiliza um banco de dados PostgreSQL 9.3 instalado localmente. Este reposito rio contem uma implementacao inicial baseada em Flask.

## Funcionalidades Principais

- **Registro de Entrada**: grava data/hora, placa, condutor, passageiros, liberacao, atividade, observacao e fotos.
- **Registro de Saida**: semelhante ao registro de entrada, atrelado sempre a uma entrada existente.
- **Agendamento de Saida**: permite registrar previsoes de saida e posteriormente gera-la.
- **Cadastro de Usuarios**: usuarios podem ser criados, alterados ou removidos via API.

As regras de negocio impedem que uma placa saia sem que haja entrada correspondente e que uma mesma entrada gere multiplas saidas.

## Configuracao do Ambiente

1. Defina a variavel `DATABASE_URI` no arquivo `config.py` ou via ambiente. Exemplo:
   `postgresql://usuario:senha@localhost/sigport_db`
2. A senha pode conter caracteres especiais. Utilize percent-encoding quando necessario.
3. Instale as dependencias Python listadas em `requirements.txt`.

```bash
pip install -r requirements.txt
```

Se atualizar os modelos ou clonar o repositório depois de já possuir tabelas
criadas, execute `upgrade_db.py` para ajustar os tipos de coluna das fotos para
`TEXT`. Isso evita erros de truncamento ao salvar imagens grandes.

## Execucao

Crie as tabelas e inicie o servidor de desenvolvimento:

```bash
python app.py
```

O servidor utiliza a porta `5000` e aceita conexoes de qualquer interface (`0.0.0.0`).

## Endpoints Resumidos

- `POST /users` — cria usuario
- `GET /users` — lista usuarios
- `POST /login` — autentica usuario
- `POST /entries` — registra entrada (uma placa por vez)
- `GET /entries` — lista entradas
- `POST /entries/<id>/exit` — registra saida
- `GET /exits` — lista saidas
- `POST /schedules` — cria agendamento
- `GET /schedules` — lista agendamentos
- `POST /schedules/<id>/create_exit` — gera saida a partir do agendamento
- `GET /schedules/<id>/exit/new` — formulário para registrar saida agendada

Para mais detalhes consulte `app.py` e `models.py`.

## Formulários de Exemplo

O diretório `templates/` contém páginas HTML simples para testar os
principais recursos via navegador. Acesse `http://localhost:5000/` para a tela de
login e utilize os demais links diretos para:

- `/users/new` — cadastro de usuário
- `/entries/new` — registro de entrada
- `/entries/<id>/exit/new` — registrar saída de uma entrada existente
- `/schedules/new` — agendar saída

## Empacotar em APK

Para executar o SIGPORT em dispositivos Android, é possível criar um aplicativo Cordova que apenas exibe a interface web existente. Consulte `docs/cordova_webview.md` para um passo a passo de configuração e geração do APK.
