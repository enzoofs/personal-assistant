# ADR-005: Oracle Cloud VPS para Deploy

## Status
Aceito

## Contexto
O ATLAS precisa rodar em algum lugar acessível pelo app mobile. Alternativas: máquina local, Railway, Fly.io, Oracle Cloud free tier, AWS/GCP.

## Decisão
Deploy em instância Oracle Cloud VPS, acesso via IP público.

## Motivo
Oracle Cloud oferece instâncias ARM gratuitas (free tier permanente) com recursos suficientes para o ATLAS. Sem custo recorrente para um projeto pessoal.

## Consequências

### Positivas
- Custo zero (free tier)
- IP público fixo para o mobile conectar
- Controle total sobre o ambiente
- Vault Obsidian pode ser sincronizado via rsync/git

### Negativas
- Setup manual (sem PaaS simplificado)
- Manutenção de servidor (updates, segurança)
- Vault Obsidian não fica na mesma máquina (precisa sync)
- CI/CD precisa ser configurado manualmente
