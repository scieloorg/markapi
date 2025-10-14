#!/bin/bash

#############################################
# MarkAPI - Script de Atualização Simplificado
# Para usuários finais (não desenvolvedores)
#############################################

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para imprimir mensagens
print_message() {
    echo -e "${GREEN}[MarkAPI]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# Banner
echo "============================================"
echo "   MarkAPI - Atualização Simplificada"
echo "============================================"
echo ""

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker não está instalado."
    exit 1
fi

if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose não está instalado."
    exit 1
fi

# Backup do banco de dados (opcional)
read -p "Deseja fazer backup do banco de dados antes de atualizar? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    print_message "Criando backup do banco de dados..."
    mkdir -p backup
    docker exec markapi_local_postgres pg_dumpall -c -U debug > "backup/backup_$(date +%Y%m%d_%H%M%S).sql"
    print_message "Backup criado em: backup/backup_$(date +%Y%m%d_%H%M%S).sql"
fi

# Parar os containers
print_message "Parando containers..."
docker compose -f local.yml stop

# Atualizar código (se usando git)
if [ -d ".git" ]; then
    print_message "Atualizando código fonte..."
    git pull origin main || print_warning "Não foi possível atualizar o código automaticamente. Atualize manualmente."
fi

# Reconstruir as imagens Docker
print_message "Reconstruindo as imagens Docker (isso pode levar alguns minutos)..."
docker compose -f local.yml build

# Iniciar os containers
print_message "Iniciando os containers..."
docker compose -f local.yml up -d

# Aguardar o banco de dados estar pronto
print_message "Aguardando banco de dados estar pronto..."
sleep 10

# Executar migrações
print_message "Executando migrações do banco de dados..."
docker compose -f local.yml run --rm django python manage.py migrate

# Sincronizar campos Wagtail
print_message "Sincronizando campos de tradução do Wagtail..."
docker compose -f local.yml run --rm django python manage.py update_translation_fields || true
docker compose -f local.yml run --rm django python manage.py sync_page_translation_fields || true

# Compilar mensagens de tradução
print_message "Compilando mensagens de tradução..."
docker compose -f local.yml run --rm django python manage.py compilemessages || true

# Coletar arquivos estáticos
print_message "Coletando arquivos estáticos..."
docker compose -f local.yml run --rm django python manage.py collectstatic --noinput || true

# Verificar status
print_message "Verificando status dos containers..."
docker compose -f local.yml ps

echo ""
echo "============================================"
print_message "Atualização concluída com sucesso!"
echo "============================================"
echo ""
echo "A aplicação está disponível em:"
echo "  - Aplicação principal: http://localhost:8009"
echo "  - MailHog (email): http://localhost:8029"
echo "  - Flower (Celery): http://localhost:5559"
echo ""
echo "Para ver os logs da aplicação, execute:"
echo "  docker compose -f local.yml logs -f"
echo ""
echo "============================================"
