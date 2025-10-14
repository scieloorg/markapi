# MarkAPI - Guia de Instalação em Português

Este é um guia simplificado em português para instalação e uso do MarkAPI.

## 📋 Índice

1. [Instalação Rápida](#instalação-rápida)
2. [Instalação Detalhada](INSTALLATION.md)
3. [Guia Rápido de Comandos](QUICK_START.md)
4. [Atualização](#atualização)
5. [Comandos Úteis](#comandos-úteis)

## 🚀 Instalação Rápida

### Pré-requisitos

- Docker e Docker Compose instalados
- Git (opcional, mas recomendado)

### Passos

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/scieloorg/markapi.git
   cd markapi
   ```

2. **Configure as variáveis de ambiente:**
   ```bash
   cp .envs/.local/.django.example .envs/.local/.django
   cp .envs/.local/.postgres.example .envs/.local/.postgres
   ```
   
   **IMPORTANTE**: Edite os arquivos `.envs/.local/.django` e `.envs/.local/.postgres` para alterar as senhas!

3. **Execute a instalação:**
   ```bash
   ./install.sh
   # ou
   make install
   ```

4. **Crie um superusuário:**
   ```bash
   docker compose -f local.yml run --rm django python manage.py createsuperuser
   ```

5. **Acesse a aplicação:**
   - Aplicação: http://localhost:8009
   - Admin: http://localhost:8009/admin

## 🔄 Atualização

Para atualizar para a versão mais recente:

```bash
./update.sh
# ou
make update
```

O script irá:
- Criar backup do banco de dados (opcional)
- Atualizar o código
- Reconstruir as imagens
- Executar migrações

## 📚 Comandos Úteis

### Gerenciamento Básico

```bash
# Iniciar
docker compose -f local.yml up -d

# Parar
docker compose -f local.yml stop

# Reiniciar
docker compose -f local.yml restart

# Ver logs
docker compose -f local.yml logs -f

# Status
docker compose -f local.yml ps
```

### Backup e Restauração

```bash
# Fazer backup
mkdir -p backup
docker exec markapi_local_postgres pg_dumpall -c -U debug > backup/backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
cat backup/seu_arquivo.sql | docker exec -i markapi_local_postgres psql -U debug
```

### Comandos Django

```bash
# Shell Python
docker compose -f local.yml run --rm django python manage.py shell

# Terminal bash
docker compose -f local.yml run --rm django bash

# Executar testes
docker compose -f local.yml run --rm django python manage.py test

# Criar migrações
docker compose -f local.yml run --rm django python manage.py makemigrations

# Aplicar migrações
docker compose -f local.yml run --rm django python manage.py migrate
```

## 🛠️ Solução de Problemas

### Porta já em uso

Se receber erro de porta em uso, você pode:

1. Parar o serviço que está usando a porta
2. Alterar a porta no arquivo `local.yml`

### Erro de permissão

```bash
# Linux/Mac
sudo chown -R $USER:$USER ../scms_data/markapi
```

### Container não inicia

```bash
# Ver logs detalhados
docker compose -f local.yml logs

# Reconstruir sem cache
docker compose -f local.yml build --no-cache
docker compose -f local.yml up -d
```

### Resetar tudo

```bash
# CUIDADO: Isso apagará todos os dados!
docker compose -f local.yml down -v
rm -rf ../scms_data/markapi/data_dev/*
./install.sh
```

## 📖 Documentação Completa

- **[Guia Rápido](QUICK_START.md)** - Comandos essenciais
- **[Instalação Completa](INSTALLATION.md)** - Guia detalhado com troubleshooting
- **[README Principal](README.md)** - Documentação técnica completa

## 🌐 Recursos

- Wiki: https://github.com/scieloorg/markapi/wiki
- Issues: https://github.com/scieloorg/markapi/issues
- Guia de conversão XML para PDF: https://github.com/scieloorg/markapi/wiki/Converter-XML-para-PDF

## 🏭 Produção

Para instalação em ambiente de produção, veja:

- [Seção de Produção no INSTALLATION.md](INSTALLATION.md#instalação-em-produção)
- Script `install-production.sh` (requer production.yml)
- Configurações Kubernetes na pasta `kubernetes/`

## 💡 Dicas

1. **Primeira instalação**: Pode levar 10-20 minutos
2. **Senhas**: Sempre altere as senhas padrão!
3. **Backups**: Configure backups regulares em produção
4. **Logs**: Use `docker compose logs -f` para acompanhar problemas
5. **Recursos**: Monitore uso de CPU/memória com `docker stats`

## 🤝 Contribuindo

Se encontrou um problema ou tem uma sugestão:

1. Verifique se já existe uma issue
2. Crie uma nova issue com detalhes
3. Contribua com melhorias via Pull Request

## 📝 Licença

GPLv3 - Veja arquivo LICENSE para detalhes.

---

**Nota**: Este documento é complementar à documentação em inglês no README.md principal.
