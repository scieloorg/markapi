#!/bin/bash

#############################################
# MarkAPI - Script de Instalação Simplificado
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
echo "   MarkAPI - Instalação Simplificada"
echo "============================================"
echo ""

# Verificar se Docker está instalado
print_message "Verificando dependências..."
if ! command -v docker &> /dev/null; then
    print_error "Docker não está instalado. Por favor, instale Docker primeiro:"
    echo "  https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose não está instalado. Por favor, instale Docker Compose primeiro:"
    echo "  https://docs.docker.com/compose/install/"
    exit 1
fi

print_message "Docker e Docker Compose encontrados ✓"

# Verificar se os arquivos de configuração existem
if [ ! -f ".envs/.local/.django" ] || [ ! -f ".envs/.local/.postgres" ]; then
    print_warning "Arquivos de configuração não encontrados."
    print_message "Criando arquivos de configuração a partir dos exemplos..."
    
    # Criar diretórios se não existirem
    mkdir -p .envs/.local
    
    # Copiar arquivos de exemplo se existirem
    if [ -f ".envs/.local/.django.example" ]; then
        cp .envs/.local/.django.example .envs/.local/.django
        print_message "Arquivo .django criado ✓"
    else
        print_error "Arquivo de exemplo .envs/.local/.django.example não encontrado!"
        exit 1
    fi
    
    if [ -f ".envs/.local/.postgres.example" ]; then
        cp .envs/.local/.postgres.example .envs/.local/.postgres
        print_message "Arquivo .postgres criado ✓"
    else
        print_error "Arquivo de exemplo .envs/.local/.postgres.example não encontrado!"
        exit 1
    fi
    
    print_message "Arquivos de configuração criados."
    print_warning "IMPORTANTE: Revise e ajuste os arquivos em .envs/.local/ conforme necessário."
    print_warning "Especialmente altere as senhas padrão por senhas seguras!"
    echo ""
    read -p "Pressione ENTER para continuar após revisar os arquivos de configuração..."
fi

# Criar diretório de dados se não existir
print_message "Configurando diretórios de dados..."
mkdir -p ../scms_data/markapi/data_dev
mkdir -p ../scms_data/markapi/data_dev_backup

# Construir as imagens Docker
print_message "Construindo as imagens Docker (isso pode levar alguns minutos)..."
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
print_message "Instalação concluída com sucesso!"
echo "============================================"
echo ""
echo "A aplicação está disponível em:"
echo "  - Aplicação principal: http://localhost:8009"
echo "  - MailHog (email): http://localhost:8029"
echo "  - Flower (Celery): http://localhost:5559"
echo ""
echo "Para criar um superusuário (administrador), execute:"
echo "  docker compose -f local.yml run --rm django python manage.py createsuperuser"
echo ""
echo "Para ver os logs da aplicação, execute:"
echo "  docker compose -f local.yml logs -f"
echo ""
echo "Para parar a aplicação, execute:"
echo "  docker compose -f local.yml stop"
echo ""
echo "Para mais comandos úteis, veja o arquivo INSTALLATION.md"
echo "============================================"
