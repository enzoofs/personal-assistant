# Feature: Pesquisa Inteligente

## Propósito
Busca combinada no vault pessoal (semântica) e na web, com resposta sintetizada em linguagem natural.

## Fontes de Busca

| Fonte | Tecnologia | Prioridade |
|---|---|---|
| Vault (Obsidian) | ChromaDB + embeddings | Alta (sempre consultado primeiro) |
| Web | Tavily API | Baixa (complementar) |

## Exemplos
```
"O que anotei sobre o projeto X?" → busca no vault
"Qual a melhor forma de indexar PDFs?" → busca web
"O que eu sei sobre React Server Components?" → vault + web combinados
```

## Valor para o Usuário
- Vault vira memória pesquisável ("segundo cérebro funcional")
- Respostas sintetizadas, não lista de links
- Busca web como fallback automático

## Métricas de Sucesso
- Resultados relevantes do vault quando a informação existe
- Busca web complementa quando vault não tem resposta

## Limitações
- Depende de ChromaDB indexado (vault/indexer.py pendente)
- Tavily opcional (funciona sem, perde busca web)
- Sem busca em PDFs ou imagens (só markdown)
