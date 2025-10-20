# ERP Pessoal

Sistema ERP completo com autenticação JWT, gerenciamento de usuários e permissões.

## Funcionalidades

- ✅ Autenticação JWT completa
- ✅ Sistema de cadastro de usuários
- ✅ Gerenciamento de permissões (Admin/Membro)
- ✅ Upload de foto de perfil
- ✅ Painel administrativo
- ✅ Interface web responsiva
- ✅ API REST completa

## Tecnologias Utilizadas

- **Backend**: FastAPI (Python)
- **Banco de Dados**: SQLAlchemy + SQLite/PostgreSQL
- **Autenticação**: JWT (python-jose)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Upload de Arquivos**: aiofiles

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd erp_pessoal
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente (opcional):
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite as configurações conforme necessário
```

4. Execute o servidor:
```bash
python main.py
```

O servidor estará disponível em: http://localhost:8000

## Uso

### Usuário Administrador Padrão
- **Email**: admin@erp.com
- **Username**: admin
- **Senha**: admin123

### Endpoints da API

#### Autenticação
- `POST /auth/register` - Cadastrar novo usuário
- `POST /auth/login` - Fazer login
- `GET /auth/me` - Obter dados do usuário atual

#### Usuários
- `GET /users/` - Listar todos os usuários (apenas admin)
- `GET /users/{id}` - Obter usuário específico
- `PUT /users/{id}` - Atualizar usuário
- `PUT /users/{id}/role` - Alterar role do usuário (apenas admin)
- `PUT /users/{id}/status` - Ativar/desativar usuário (apenas admin)
- `POST /users/{id}/profile-picture` - Upload de foto de perfil
- `DELETE /users/{id}/profile-picture` - Remover foto de perfil

### Interface Web

- `/` - Página inicial (redireciona para login)
- `/login` - Página de login
- `/dashboard` - Dashboard principal
- `/profile` - Meu perfil
- `/admin` - Painel administrativo (apenas admin)

## Estrutura do Projeto

```
erp_pessoal/
├── main.py                 # Aplicação principal
├── config.py              # Configurações
├── database.py            # Configuração do banco
├── models.py              # Modelos do banco de dados
├── schemas.py             # Schemas Pydantic
├── auth.py                # Sistema de autenticação
├── routers/               # Endpoints da API
│   ├── auth.py           # Autenticação
│   ├── users.py          # Gerenciamento de usuários
│   └── web.py            # Páginas web
├── templates/             # Templates HTML
│   ├── base.html         # Template base
│   ├── login.html        # Página de login
│   ├── dashboard.html    # Dashboard
│   ├── profile.html      # Perfil do usuário
│   └── admin.html        # Painel admin
├── static/               # Arquivos estáticos
├── uploads/              # Uploads de usuários
└── requirements.txt      # Dependências
```

## Permissões

### Admin
- Acesso total ao sistema
- Pode gerenciar todos os usuários
- Pode alterar roles e status de usuários
- Acesso ao painel administrativo

### Membro
- Acesso limitado ao próprio perfil
- Pode atualizar suas informações pessoais
- Pode fazer upload de foto de perfil

## Configuração do Banco de Dados

Por padrão, o sistema usa SQLite. Para usar PostgreSQL:

1. Instale o psycopg2-binary (já incluído no requirements.txt)
2. Configure a variável de ambiente `DATABASE_URL`:
```bash
DATABASE_URL=postgresql://usuario:senha@localhost/nome_do_banco
```

## Segurança

- Senhas são hasheadas com bcrypt
- Tokens JWT com expiração configurável
- Validação de tipos de arquivo para upload
- Limite de tamanho de arquivo
- CORS configurado para desenvolvimento

## Desenvolvimento

Para executar em modo de desenvolvimento:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A documentação interativa da API estará disponível em:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Licença

Este projeto é de código aberto e está disponível sob a licença MIT.
