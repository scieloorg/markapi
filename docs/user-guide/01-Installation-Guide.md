# Guia de Instalação do MarkAPI para Usuários

Este guia apresenta instruções passo a passo para instalar e configurar o MarkAPI em seu servidor, destinado a usuários finais que desejam utilizar a aplicação para validar e converter documentos XML.

## Pré-requisitos

Antes de iniciar a instalação, certifique-se de que seu sistema possui:

1. **Docker** (versão 20.10 ou superior)
2. **Docker Compose** (versão 2.0 ou superior)
3. **Git** (para clonar o repositório)
4. Pelo menos **4GB de RAM** disponível
5. Pelo menos **10GB de espaço em disco**

### Instalação do Docker

#### Linux (Ubuntu/Debian)

```bash
# Atualizar pacotes do sistema
sudo apt-get update

# Instalar dependências
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# Adicionar chave GPG oficial do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório do Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verificar instalação
docker --version
docker compose version
```

#### Windows

1. Baixe o **Docker Desktop** em: https://www.docker.com/products/docker-desktop
2. Execute o instalador e siga as instruções na tela
3. Reinicie o computador quando solicitado
4. Abra o Docker Desktop e aguarde sua inicialização

#### macOS

1. Baixe o **Docker Desktop** em: https://www.docker.com/products/docker-desktop
2. Abra o arquivo `.dmg` baixado
3. Arraste o ícone do Docker para a pasta Aplicativos
4. Abra o Docker Desktop e aguarde sua inicialização

## Instalação do MarkAPI

### Passo 1: Clonar o Repositório

Abra o terminal e execute:

```bash
# Clone o repositório do MarkAPI
git clone https://github.com/scieloorg/markapi.git

# Entre no diretório do projeto
cd markapi
```

### Passo 2: Configurar Variáveis de Ambiente

O MarkAPI utiliza arquivos de configuração para definir parâmetros importantes. Para ambiente de produção:

```bash
# Copiar arquivos de exemplo
cp -r .envs/.production .envs/.production.backup
```

**Importante:** Edite os arquivos em `.envs/.production/` para configurar:

1. **`.envs/.production/.django`**
   - `DJANGO_SECRET_KEY`: Gere uma chave secreta única (use um gerador online)
   - `DJANGO_ALLOWED_HOSTS`: Adicione o domínio do seu servidor (ex: `markapi.example.com`)
   - `DJANGO_ADMIN_URL`: Personalize a URL do painel administrativo (ex: `admin-secreto/`)

2. **`.envs/.production/.postgres`**
   - `POSTGRES_PASSWORD`: Defina uma senha forte para o banco de dados

### Passo 3: Criar Diretórios de Dados

```bash
# Criar diretório para dados do PostgreSQL
mkdir -p ../scms_data/markapi/data_prod
mkdir -p ../scms_data/markapi/data_prod_backup

# Ajustar permissões
chmod 700 ../scms_data/markapi/data_prod
```

### Passo 4: Construir as Imagens Docker

**Nota:** O MarkAPI suporta duas formas de implantação em produção:
1. **Docker Compose** (recomendado para servidores únicos) - usando `production.yml`
2. **Kubernetes** (recomendado para clusters) - veja os arquivos em `kubernetes/hml/`

Para Docker Compose, se o arquivo `production.yml` não existir, você pode criar um baseado no `local.yml` ou usar diretamente o `local.yml` com ajustes nas variáveis de ambiente.

```bash
# Construir as imagens do MarkAPI
# Se production.yml existir:
docker compose -f production.yml build

# Alternativamente, use local.yml para testes ou ambientes menores:
# docker compose -f local.yml build
```

Este processo pode levar alguns minutos na primeira execução.

### Passo 5: Inicializar o Banco de Dados

**Nota:** Substitua `production.yml` por `local.yml` se estiver usando este arquivo.

```bash
# Executar migrações do banco de dados
docker compose -f production.yml run --rm django python manage.py migrate

# Criar superusuário (usuário administrador)
docker compose -f production.yml run --rm django python manage.py createsuperuser
```

Quando solicitado, forneça:
- **Usuário**: seu nome de usuário desejado
- **E-mail**: seu endereço de e-mail
- **Senha**: uma senha forte (será solicitada duas vezes)

### Passo 6: Coletar Arquivos Estáticos

```bash
# Coletar arquivos CSS, JavaScript e imagens
docker compose -f production.yml run --rm django python manage.py collectstatic --noinput
```

### Passo 7: Iniciar a Aplicação

```bash
# Iniciar todos os serviços
docker compose -f production.yml up -d
```

Os seguintes serviços serão iniciados:
- **Django**: Aplicação web principal
- **PostgreSQL**: Banco de dados
- **Redis**: Cache e fila de mensagens
- **Celery Worker**: Processamento de tarefas em segundo plano
- **Celery Beat**: Agendador de tarefas
- **Traefik**: Proxy reverso (se configurado)

### Passo 8: Verificar o Status

```bash
# Verificar se os containers estão rodando
docker compose -f production.yml ps

# Verificar logs em caso de problemas
docker compose -f production.yml logs django
```

## Acessar a Aplicação

Após a instalação bem-sucedida:

1. **Interface Web**: Acesse `http://seu-servidor:8000` (ou o domínio configurado)
2. **Painel Administrativo**: Acesse `http://seu-servidor:8000/django-admin/` (ou a URL personalizada)

Faça login com as credenciais do superusuário criadas no Passo 5.

## Implantação com Kubernetes (Alternativa)

Para ambientes de produção em larga escala, o MarkAPI pode ser implantado usando Kubernetes:

```bash
# Aplicar configurações do Kubernetes
kubectl apply -f kubernetes/hml/

# Verificar os pods
kubectl get pods

# Verificar os serviços
kubectl get services
```

Consulte os arquivos YAML em `kubernetes/hml/` para mais detalhes sobre a configuração.

## Configuração Opcional: Proxy Reverso (Nginx/Traefik)

Para ambiente de produção, é recomendado configurar um proxy reverso com HTTPS.

### Usando Traefik (incluído)

O MarkAPI já vem configurado com Traefik para implantações Docker Compose. Edite o arquivo `.envs/.production/.django` e configure:

```
DJANGO_ALLOWED_HOSTS=seu-dominio.com
```

Certifique-se de que as portas 80 e 443 estão acessíveis.

## Comandos Úteis

### Parar a Aplicação

```bash
docker compose -f production.yml stop
```

### Reiniciar a Aplicação

```bash
docker compose -f production.yml restart
```

### Ver Logs

```bash
# Logs de todos os serviços
docker compose -f production.yml logs -f

# Logs de um serviço específico
docker compose -f production.yml logs -f django
docker compose -f production.yml logs -f celeryworker
```

### Executar Comandos Django

```bash
# Template geral
docker compose -f production.yml run --rm django python manage.py <comando>

# Exemplos
docker compose -f production.yml run --rm django python manage.py shell
docker compose -f production.yml run --rm django python manage.py createsuperuser
```

### Backup do Banco de Dados

```bash
# Fazer backup
docker compose -f production.yml exec postgres backup

# Listar backups
docker compose -f production.yml exec postgres list-backups

# Restaurar backup
docker compose -f production.yml exec postgres restore <nome-do-backup>
```

### Atualizar a Aplicação

```bash
# Parar a aplicação
docker compose -f production.yml down

# Atualizar código
git pull origin main

# Reconstruir imagens
docker compose -f production.yml build

# Executar migrações
docker compose -f production.yml run --rm django python manage.py migrate

# Coletar arquivos estáticos
docker compose -f production.yml run --rm django python manage.py collectstatic --noinput

# Reiniciar aplicação
docker compose -f production.yml up -d
```

## Solução de Problemas

### Containers não iniciam

Verifique os logs:
```bash
docker compose -f production.yml logs
```

### Erro de permissão no banco de dados

Ajuste permissões do diretório de dados:
```bash
sudo chown -R 999:999 ../scms_data/markapi/data_prod
```

### Porta já em uso

Edite o arquivo `production.yml` e altere as portas mapeadas.

### Erro de memória

Aumente a memória disponível para o Docker:
- **Linux**: Aumente a swap do sistema
- **Windows/macOS**: Ajuste nas configurações do Docker Desktop (Resources > Advanced)

## Próximos Passos

Após a instalação, consulte os seguintes guias:

1. **[Guia de Validação de XML](./02-XML-Validation-Guide.md)** - Como validar documentos XML
2. **[Guia de Conversão para PDF](./03-XML-to-PDF-Conversion-Guide.md)** - Como converter XML para PDF
3. **[Configuração de Modelos DOCX](./04-DOCX-Layout-Configuration.md)** - Como personalizar layouts de PDF

## Suporte

Para questões ou problemas:

- **Issues**: https://github.com/scieloorg/markapi/issues
- **Wiki**: https://github.com/scieloorg/markapi/wiki
- **Documentação Técnica**: Consulte o arquivo `README.md` no repositório

## Referências

- [Documentação do Docker](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)
