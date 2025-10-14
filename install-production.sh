#!/bin/bash

#############################################
# MarkAPI - Script de Instalação para Produção
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
echo "   MarkAPI - Instalação para PRODUÇÃO"
echo "============================================"
echo ""
print_warning "ATENÇÃO: Este script é para instalação em ambiente de PRODUÇÃO!"
print_warning "Certifique-se de que está executando em um servidor apropriado."
echo ""
read -p "Deseja continuar? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Instalação cancelada."
    exit 0
fi

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

# Verificar se production.yml existe
if [ ! -f "production.yml" ]; then
    print_error "Arquivo production.yml não encontrado!"
    print_warning "Este repositório não possui um arquivo production.yml configurado."
    print_warning "Você precisará criar um arquivo production.yml baseado no local.yml"
    print_warning "ou usar Kubernetes para deploy em produção (veja pasta kubernetes/)."
    exit 1
fi

# Verificar se os arquivos de configuração existem
if [ ! -f ".envs/.production/.django" ] || [ ! -f ".envs/.production/.postgres" ]; then
    print_warning "Arquivos de configuração não encontrados."
    print_message "Criando arquivos de configuração a partir dos exemplos..."
    
    # Criar diretórios se não existirem
    mkdir -p .envs/.production
    
    # Copiar arquivos de exemplo se existirem
    if [ -f ".envs/.production/.django.example" ]; then
        cp .envs/.production/.django.example .envs/.production/.django
        print_message "Arquivo .django criado ✓"
    else
        print_error "Arquivo de exemplo .envs/.production/.django.example não encontrado!"
        exit 1
    fi
    
    if [ -f ".envs/.production/.postgres.example" ]; then
        cp .envs/.production/.postgres.example .envs/.production/.postgres
        print_message "Arquivo .postgres criado ✓"
    else
        print_error "Arquivo de exemplo .envs/.production/.postgres.example não encontrado!"
        exit 1
    fi
    
    print_message "Arquivos de configuração criados."
    echo ""
    print_warning "=========================================="
    print_warning "IMPORTANTE - CONFIGURAÇÃO DE SEGURANÇA"
    print_warning "=========================================="
    print_warning "Você DEVE editar os seguintes arquivos ANTES de continuar:"
    print_warning "  - .envs/.production/.django"
    print_warning "  - .envs/.production/.postgres"
    echo ""
    print_warning "Especialmente, altere:"
    print_warning "  1. DJANGO_SECRET_KEY - para uma string longa e aleatória"
    print_warning "  2. POSTGRES_PASSWORD - para uma senha forte"
    print_warning "  3. DJANGO_ADMIN_URL - para um URL secreto"
    print_warning "  4. CELERY_FLOWER_PASSWORD - para uma senha forte"
    print_warning "  5. DJANGO_ALLOWED_HOSTS - para o domínio do seu servidor"
    print_warning "=========================================="
    echo ""
    read -p "Pressione ENTER SOMENTE após revisar e editar os arquivos de configuração..."
fi

# Verificar configurações críticas
print_message "Verificando configurações de segurança..."
if grep -q "CHANGE_THIS" .envs/.production/.django || grep -q "CHANGE_THIS" .envs/.production/.postgres; then
    print_error "ERRO: Ainda há valores padrão nos arquivos de configuração!"
    print_error "Você DEVE alterar todas as senhas e configurações antes de continuar."
    exit 1
fi

print_message "Configurações básicas verificadas ✓"

# Criar diretório de dados se não existir
print_message "Configurando diretórios de dados..."
mkdir -p ../scms_data/markapi/data_production
mkdir -p ../scms_data/markapi/data_production_backup

# Construir as imagens Docker
print_message "Construindo as imagens Docker (isso pode levar alguns minutos)..."
docker compose -f production.yml build

# Iniciar os containers
print_message "Iniciando os containers..."
docker compose -f production.yml up -d

# Aguardar o banco de dados estar pronto
print_message "Aguardando banco de dados estar pronto..."
sleep 15

# Executar migrações
print_message "Executando migrações do banco de dados..."
docker compose -f production.yml run --rm django python manage.py migrate

# Sincronizar campos Wagtail
print_message "Sincronizando campos de tradução do Wagtail..."
docker compose -f production.yml run --rm django python manage.py update_translation_fields || true
docker compose -f production.yml run --rm django python manage.py sync_page_translation_fields || true

# Compilar mensagens de tradução
print_message "Compilando mensagens de tradução..."
docker compose -f production.yml run --rm django python manage.py compilemessages || true

# Coletar arquivos estáticos
print_message "Coletando arquivos estáticos..."
docker compose -f production.yml run --rm django python manage.py collectstatic --noinput

# Verificar status
print_message "Verificando status dos containers..."
docker compose -f production.yml ps

echo ""
echo "============================================"
print_message "Instalação concluída com sucesso!"
echo "============================================"
echo ""
print_warning "PRÓXIMOS PASSOS IMPORTANTES:"
echo ""
echo "1. Crie um superusuário (administrador):"
echo "   docker compose -f production.yml run --rm django python manage.py createsuperuser"
echo ""
echo "2. Configure seu servidor web reverso (Nginx/Apache) se necessário"
echo ""
echo "3. Configure SSL/TLS para HTTPS"
echo ""
echo "4. Configure backups regulares do banco de dados"
echo ""
echo "5. Configure monitoramento (Sentry, se disponível)"
echo ""
echo "Para ver os logs da aplicação, execute:"
echo "  docker compose -f production.yml logs -f"
echo ""
echo "Para parar a aplicação, execute:"
echo "  docker compose -f production.yml stop"
echo ""
echo "============================================"
