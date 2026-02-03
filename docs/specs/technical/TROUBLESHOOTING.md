# Solução de Problemas — ATLAS

## Problemas Comuns

### Backend não inicia

**Erro: `ModuleNotFoundError: No module named 'atlas.vault.manager'`**
Os módulos vault/ ainda não foram implementados. O startup do FastAPI (`main.py`) tenta inicializar o vault e indexar. Comentar as linhas de startup ou implementar os módulos.

**Erro: `OPENAI_API_KEY not set`**
Variável de ambiente faltando. Verificar se `.env` existe e contém `OPENAI_API_KEY=sk-...`.

**Erro: porta 8000 já em uso**
```bash
# Encontrar processo
lsof -i :8000  # Linux/Mac
netstat -ano | findstr 8000  # Windows

# Ou usar outra porta
uvicorn atlas.main:app --port 8001
```

### Google Calendar não funciona

**Erro: `credentials.json not found`**
Baixar credenciais OAuth2 do Google Cloud Console e salvar como `credentials.json` na raiz do projeto.

**Erro: `token.json expired`**
O token OAuth tem auto-refresh, mas se falhar, deletar `token.json` e re-autenticar. Em servidor headless, copiar `token.json` de uma máquina com navegador.

**Erro: `insufficient permissions`**
Verificar que o escopo `https://www.googleapis.com/auth/calendar` está configurado no Google Cloud Console.

### Classificação de intenção errada

**Sintoma:** ATLAS classifica como `chat` quando deveria ser outra intenção.
- Verificar que o prompt de classificação em `classifier.py` inclui a intenção esperada
- A data/hora atual é injetada no prompt — verificar timezone em `.env`
- Se o texto é muito ambíguo, o fallback para `chat` é intencional (segurança)

### ChromaDB

**Erro: `chromadb.errors.InvalidCollectionException`**
Deletar a pasta `chroma_db/` e deixar reindexar no próximo startup.

**Startup lento com vault grande**
A reindexação completa roda no startup. Para vaults grandes, isso pode demorar. Considerar lazy loading ou indexação em background.

### Mobile

**Erro: `Network request failed`**
- Verificar se o backend está rodando
- Verificar URL em `src/api/atlas.ts` (ngrok URL muda a cada restart)
- Verificar que o header `X-API-Key` está correto

**Áudio não grava no Android**
- Verificar permissões de microfone no app
- Expo AV requer `expo-av` instalado e configurado no `app.json`

## Debugging

### Logs do Backend
O backend usa `logging` do Python configurado em `main.py` (nível INFO). Para mais detalhe:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Inspecionar classificação
Adicionar log no `orchestrator.py` após `classify_intent()` para ver o IntentResult completo (intent, params, confidence).

### Testar endpoints manualmente
```bash
# Health check
curl http://localhost:8000/health

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"message": "O que tenho pra hoje?"}'
```
