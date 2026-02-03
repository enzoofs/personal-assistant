# ADR-003: ChromaDB como Índice Reconstruível

## Status
Aceito

## Contexto
A busca semântica no vault requer um banco vetorial. Alternativas: Pinecone (cloud), Weaviate, FAISS, ou ChromaDB (local embedded).

## Decisão
Usar ChromaDB em modo persistente local (`PersistentClient`), tratado como índice reconstruível a partir do vault.

## Motivo
Zero custo operacional, sem dependência de serviço externo, e pode ser reconstruído a qualquer momento a partir dos arquivos markdown.

## Consequências

### Positivas
- Zero custo (roda local)
- Sem infra extra para manter
- Reconstruível: se corromper, basta reindexar o vault
- Indexação incremental via hash SHA256

### Negativas
- Não escala horizontalmente (single-node)
- Reindexação completa no startup pode ser lenta com vaults grandes
- Sem features enterprise (replicação, backup automático)
