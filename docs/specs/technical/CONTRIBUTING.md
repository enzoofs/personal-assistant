# Guia de Desenvolvimento — ATLAS

## Setup do Ambiente

### Pré-requisitos
- Python 3.12+
- Node.js 18+ (para mobile)
- Conta OpenAI com API key
- Projeto Google Cloud com Calendar API habilitada + `credentials.json`
- (Opcional) Tavily API key

### Backend

```bash
# Clonar e entrar no projeto
git clone https://github.com/enzoofs/personal-assistant.git
cd personal-assistant

# Criar virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -e ".[dev]"

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas API keys

# Rodar servidor
uvicorn atlas.main:app --reload --port 8000
```

### Mobile

```bash
cd mobile
npm install
npx expo start
```

### Variáveis de Ambiente (.env)

```env
OPENAI_API_KEY=sk-...          # Obrigatório
TAVILY_API_KEY=tvly-...        # Opcional (busca web)
GOOGLE_CREDENTIALS_PATH=./credentials.json
VAULT_PATH=./vault
CHROMA_DB_PATH=./chroma_db
ATLAS_API_KEY=sua-chave-secreta
TIMEZONE=America/Sao_Paulo
```

## Testes

### Executar testes

```bash
# Todos os testes
pytest

# Com verbose
pytest -v

# Por marker
pytest -m unit
pytest -m integration
pytest -m api

# Arquivo específico
pytest tests/test_tools.py

# Teste específico
pytest tests/test_tools.py::test_handle_save_note
```

### Estrutura de Testes

- `conftest.py` — Fixtures compartilhadas: `tmp_vault`, `mock_settings`, `mock_openai`, `mock_chroma`, `mock_tavily`
- Todas as APIs externas são mockadas nos testes
- `pytest-asyncio` com `asyncio_mode = auto`
- Markers: `unit`, `integration`, `api`, `slow`

### Adicionar Testes

Seguir o padrão existente: cada arquivo de teste testa um módulo. Usar as fixtures do `conftest.py` para mocks. Sempre mockar chamadas externas.

## Build e Deploy

### Deploy atual
- **Dev:** `uvicorn atlas.main:app --reload` (local)
- **Mobile dev:** ngrok tunnel para expor localhost
- **Produção (planejado):** Oracle Cloud VPS com IP público

### CI/CD (a configurar)
Pipeline planejado para GitHub Actions:
1. Rodar `pytest` em cada push/PR
2. Lint + type check
3. Deploy automático para Oracle Cloud VPS no push para main

## Estrutura de Branches

- `feat/atlas-mvp` — Branch principal de desenvolvimento do MVP
- Feature branches a partir de `feat/atlas-mvp`

## Convenções de Commit

Mensagens descritivas em inglês, prefixo semântico:
- `feat:` nova funcionalidade
- `fix:` correção de bug
- `refactor:` refatoração sem mudança de comportamento
- `test:` adição/modificação de testes
- `docs:` documentação
- `chore:` manutenção
