# ADR-002: Markdown no Filesystem como Source of Truth

## Status
Aceito

## Contexto
O ATLAS precisa persistir notas, hábitos e pesquisas do usuário. As alternativas eram: banco de dados relacional (SQLite/Postgres), banco NoSQL, ou arquivos markdown no filesystem.

## Decisão
Usar arquivos markdown com frontmatter YAML no filesystem local, compatíveis com Obsidian.

## Motivo
O vault Obsidian já é o "segundo cérebro" do usuário. Usar markdown mantém compatibilidade total — o usuário pode abrir, editar e navegar suas notas no Obsidian enquanto o ATLAS lê e escreve no mesmo vault.

## Consequências

### Positivas
- Compatibilidade total com Obsidian (leitura simultânea)
- Dados portáveis e legíveis sem ferramenta especial
- Sem schema migrations ou overhead de banco
- Backup simples (git, rsync, etc.)

### Negativas
- Queries complexas dependem de ChromaDB (busca semântica) ou leitura de frontmatter
- Sem transações ACID
- Performance pode degradar com milhares de arquivos
- ATLAS nunca deleta automaticamente (regra de segurança)
