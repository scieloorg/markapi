# MarkAPI - Guia Rápido

## Instalação (Primeira Vez)

```bash
# 1. Clone ou baixe o repositório
git clone https://github.com/scieloorg/markapi.git
cd markapi

# 2. Configure os arquivos de ambiente
cp .envs/.local/.django.example .envs/.local/.django
cp .envs/.local/.postgres.example .envs/.local/.postgres

# 3. Execute a instalação
./install.sh
# ou
make install

# 4. Crie um superusuário
docker compose -f local.yml run --rm django python manage.py createsuperuser
```

## Atualização

```bash
cd markapi
./update.sh
# ou
make update
```

## Comandos Essenciais

### Iniciar
```bash
docker compose -f local.yml up -d
```

### Parar
```bash
docker compose -f local.yml stop
```

### Ver Logs
```bash
docker compose -f local.yml logs -f
```

### Status
```bash
docker compose -f local.yml ps
```

## Acessos

- **Aplicação**: http://localhost:8009
- **Admin**: http://localhost:8009/admin
- **Email**: http://localhost:8029
- **Celery**: http://localhost:5559

## Backup

```bash
mkdir -p backup
docker exec markapi_local_postgres pg_dumpall -c -U debug > backup/backup_$(date +%Y%m%d_%H%M%S).sql
```

## Problemas?

Consulte o [Guia de Instalação Completo](INSTALLATION.md) para mais detalhes e solução de problemas.
