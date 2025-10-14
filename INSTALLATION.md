# Guia de Instalação e Atualização - MarkAPI

Este guia foi criado para facilitar a instalação e atualização da aplicação web MarkAPI por usuários finais (não desenvolvedores).

## Pré-requisitos

Antes de instalar o MarkAPI, você precisa ter instalado no seu computador:

1. **Docker** - Sistema de containerização
   - Download: https://docs.docker.com/get-docker/
   - Para Windows/Mac: Instale o Docker Desktop
   - Para Linux: Siga as instruções específicas da sua distribuição

2. **Docker Compose** - Ferramenta para gerenciar múltiplos containers
   - Geralmente já vem incluído no Docker Desktop
   - Para Linux: https://docs.docker.com/compose/install/

3. **Git** (opcional, mas recomendado para facilitar atualizações)
   - Download: https://git-scm.com/downloads

## Instalação Rápida

### Passo 1: Obter o código

Se você tem Git instalado:

```bash
git clone https://github.com/scieloorg/markapi.git
cd markapi
```

Se você não tem Git, baixe o código como arquivo ZIP:
- Vá para https://github.com/scieloorg/markapi
- Clique em "Code" → "Download ZIP"
- Extraia o arquivo ZIP
- Abra o terminal na pasta extraída

### Passo 2: Configurar ambiente

Copie os arquivos de exemplo para criar sua configuração:

```bash
# Para Linux/Mac:
cp .envs/.local/.django.example .envs/.local/.django
cp .envs/.local/.postgres.example .envs/.local/.postgres

# Para Windows (PowerShell):
Copy-Item .envs/.local/.django.example .envs/.local/.django
Copy-Item .envs/.local/.postgres.example .envs/.local/.postgres
```

**IMPORTANTE**: Edite os arquivos `.envs/.local/.django` e `.envs/.local/.postgres` para alterar as senhas padrão por senhas seguras.

### Passo 3: Executar instalação

Execute o script de instalação:

```bash
# Para Linux/Mac:
./install.sh

# Para Windows (usando Git Bash):
bash install.sh

# Ou simplesmente use o Makefile (funciona em todos os sistemas):
make install
```

O script irá:
1. Verificar se Docker e Docker Compose estão instalados
2. Criar diretórios necessários
3. Construir as imagens Docker
4. Iniciar os containers
5. Executar migrações do banco de dados
6. Configurar o Wagtail
7. Preparar a aplicação para uso

**Nota**: A primeira instalação pode levar de 10 a 20 minutos dependendo da velocidade da sua internet e do seu computador.

### Passo 4: Criar um superusuário (administrador)

Após a instalação, crie um usuário administrador:

```bash
docker compose -f local.yml run --rm django python manage.py createsuperuser
```

Siga as instruções na tela para definir:
- Nome de usuário
- Email
- Senha

## Acessando a Aplicação

Após a instalação, você pode acessar:

- **Aplicação principal**: http://localhost:8009
- **Painel administrativo**: http://localhost:8009/admin
- **MailHog (servidor de email local)**: http://localhost:8029
- **Flower (monitoramento Celery)**: http://localhost:5559

## Atualização

Para atualizar o MarkAPI para a versão mais recente:

```bash
# Para Linux/Mac:
./update.sh

# Para Windows (usando Git Bash):
bash update.sh

# Ou simplesmente use o Makefile (funciona em todos os sistemas):
make update
```

O script de atualização irá:
1. Oferecer opção de criar backup do banco de dados
2. Parar os containers
3. Atualizar o código (se estiver usando Git)
4. Reconstruir as imagens Docker
5. Iniciar os containers
6. Executar migrações necessárias
7. Atualizar configurações do Wagtail

## Comandos Úteis

### Iniciar a aplicação

```bash
docker compose -f local.yml up -d
```

### Parar a aplicação

```bash
docker compose -f local.yml stop
```

### Ver logs da aplicação

```bash
docker compose -f local.yml logs -f
```

Para ver logs de um serviço específico:

```bash
# Logs do Django
docker compose -f local.yml logs -f django

# Logs do Celery Worker
docker compose -f local.yml logs -f celeryworker
```

### Verificar status dos containers

```bash
docker compose -f local.yml ps
```

### Reiniciar a aplicação

```bash
docker compose -f local.yml restart
```

### Parar e remover containers

```bash
docker compose -f local.yml down
```

### Fazer backup do banco de dados

```bash
mkdir -p backup
docker exec markapi_local_postgres pg_dumpall -c -U debug > backup/backup_$(date +%Y%m%d_%H%M%S).sql
```

**Nota**: Substitua `debug` pelo usuário configurado em `.envs/.local/.postgres`

### Restaurar backup do banco de dados

```bash
cat backup/seu_arquivo_backup.sql | docker exec -i markapi_local_postgres psql -U debug
```

### Acessar o shell do Django

```bash
docker compose -f local.yml run --rm django python manage.py shell
```

### Acessar o terminal bash do container Django

```bash
docker compose -f local.yml run --rm django bash
```

### Executar testes

```bash
docker compose -f local.yml run --rm django python manage.py test
```

## Solução de Problemas

### A aplicação não inicia

1. Verifique se o Docker está rodando:
   ```bash
   docker ps
   ```

2. Verifique os logs para identificar erros:
   ```bash
   docker compose -f local.yml logs
   ```

3. Tente reconstruir sem cache:
   ```bash
   docker compose -f local.yml build --no-cache
   docker compose -f local.yml up -d
   ```

### Erro de porta já em uso

Se você receber um erro dizendo que uma porta já está em uso (por exemplo, 8009, 5432, 6379), você pode:

1. Parar o serviço que está usando a porta
2. Ou alterar a porta no arquivo `local.yml`

Para alterar portas, edite o arquivo `local.yml` e modifique as linhas de `ports`:

```yaml
ports:
  - "8009:8000"  # Altere 8009 para outra porta disponível
```

### Erro de permissão nos diretórios de dados

Se você receber erros de permissão, execute:

```bash
# Linux/Mac
sudo chown -R $USER:$USER ../scms_data/markapi

# Ou crie os diretórios com permissões adequadas
mkdir -p ../scms_data/markapi/data_dev
chmod -R 755 ../scms_data/markapi
```

### Container do PostgreSQL não inicia

1. Verifique se há processos usando a porta 5432:
   ```bash
   # Linux/Mac
   lsof -i :5432
   
   # Windows
   netstat -ano | findstr :5432
   ```

2. Verifique se há permissões adequadas no diretório de dados:
   ```bash
   ls -la ../scms_data/markapi/data_dev
   ```

### Limpar dados e recomeçar

Se você quiser recomeçar do zero:

```bash
# Parar e remover todos os containers e volumes
docker compose -f local.yml down -v

# Remover diretório de dados (CUIDADO: isso apagará todos os dados)
rm -rf ../scms_data/markapi/data_dev/*

# Executar instalação novamente
./install.sh
```

## Arquitetura da Aplicação

O MarkAPI utiliza os seguintes serviços:

- **Django**: Aplicação web principal (porta 8009)
- **PostgreSQL**: Banco de dados (porta 5439)
- **Redis**: Cache e broker de mensagens (porta 6399)
- **Celery Worker**: Processamento assíncrono de tarefas
- **Celery Beat**: Agendador de tarefas periódicas
- **Flower**: Interface web para monitorar Celery (porta 5559)
- **MailHog**: Servidor SMTP para teste de emails (porta 8029)

## Recursos Adicionais

- **Wiki do projeto**: https://github.com/scieloorg/markapi/wiki
- **Guia de uso**: https://github.com/scieloorg/markapi/wiki
- **Conversão XML para PDF**: https://github.com/scieloorg/markapi/wiki/Converter-XML-para-PDF
- **Configuração do modelo**: https://github.com/scieloorg/markapi/wiki/Guia-rápido:-baixar-e-configurar-o-modelo-do-MarkAPI-para-marcação-de-referências-em-PDF

## Suporte

Se você encontrar problemas não listados aqui:

1. Consulte a documentação completa no repositório
2. Verifique as issues abertas no GitHub: https://github.com/scieloorg/markapi/issues
3. Abra uma nova issue descrevendo o problema em detalhes

## Instalação em Produção

**AVISO**: A instalação em produção requer considerações adicionais de segurança e configuração.

### Opções de Deployment

1. **Docker Compose (Produção)**: Use `install-production.sh` (se disponível production.yml)
2. **Kubernetes**: Veja configurações na pasta `kubernetes/` para deployment em cluster

### Considerações importantes para produção:

- **Segurança**: Altere TODAS as senhas e chaves secretas
- **HTTPS**: Configure SSL/TLS (recomendado: Let's Encrypt)
- **Backup**: Configure backups automáticos do banco de dados
- **Monitoramento**: Configure Sentry ou outra ferramenta de monitoramento
- **Firewall**: Configure regras apropriadas de firewall
- **Domínio**: Configure DNS e ALLOWED_HOSTS corretamente
- **Email**: Configure um servidor SMTP real (não use MailHog)
- **Recursos**: Dimensione adequadamente CPU, memória e disco

Para instruções detalhadas de produção, consulte:
- [Docker deployment guide](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html)
- Configurações de Kubernetes na pasta `kubernetes/`

## Informações Técnicas

- **Python**: 3.11
- **Django**: Versão definida em requirements
- **Wagtail**: CMS utilizado para páginas e conteúdo
- **Base**: cookiecutter-django

Para desenvolvedores ou usuários avançados, consulte o arquivo `README.md` para mais informações sobre desenvolvimento, testes e configurações avançadas.
