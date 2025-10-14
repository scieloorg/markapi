# Conteúdo para Wiki do MarkAPI

Este documento contém um resumo do conteúdo da documentação do usuário que pode ser usado para popular as páginas da Wiki do MarkAPI em: https://github.com/scieloorg/markapi/wiki

## Estrutura Sugerida para a Wiki

A documentação do usuário foi criada e está disponível na pasta `docs/user-guide/` do repositório. Recomendamos criar as seguintes páginas na Wiki:

### 1. Home (Página Principal)

Use o conteúdo de: `docs/user-guide/README.md`

**URL sugerida:** https://github.com/scieloorg/markapi/wiki

**Resumo:**
- Visão geral do MarkAPI
- Links para todos os guias
- Fluxo de trabalho típico
- FAQ básico
- Recursos rápidos

---

### 2. Guia de Instalação

Use o conteúdo de: `docs/user-guide/01-Installation-Guide.md`

**URL sugerida:** https://github.com/scieloorg/markapi/wiki/Guia-de-Instalacao

**Conteúdo:**
- Pré-requisitos (Docker, hardware)
- Instalação do Docker (Linux, Windows, macOS)
- Passo a passo da instalação do MarkAPI
- Configuração de variáveis de ambiente
- Inicialização e verificação
- Comandos úteis
- Solução de problemas
- Atualização da aplicação
- Backup e restauração

**Análogo a:** https://github.com/scieloorg/opac_5/wiki/Upload-application-installation (mas adaptado para usuários não-desenvolvedores)

---

### 3. Guia de Validação de XML

Use o conteúdo de: `docs/user-guide/02-XML-Validation-Guide.md`

**URL sugerida:** https://github.com/scieloorg/markapi/wiki/Validacao-de-XML

**Conteúdo:**
- O que é validação de XML
- Como fazer login e acessar o sistema
- Como fazer upload de arquivos XML
- Como interpretar relatórios de validação
- Níveis de severidade (ERROR, WARNING, INFO)
- Como corrigir problemas e revalidar
- Uso da API para validação automatizada
- Problemas comuns e soluções
- Boas práticas
- Fluxo de trabalho recomendado

**Análogo a:** https://github.com/scieloorg/markapi/wiki/Converter-XML-para-PDF (mas focado em validação)

---

## Como Popular a Wiki

### Opção 1: Copiar e Colar (Simples)

1. Acesse https://github.com/scieloorg/markapi/wiki
2. Clique em "New Page" para cada guia
3. Copie o conteúdo dos arquivos `.md` correspondentes
4. Cole no editor da Wiki
5. Ajuste formatação se necessário
6. Salve a página

### Opção 2: Clonar o Wiki (Avançado)

```bash
# Clonar o repositório da Wiki
git clone https://github.com/scieloorg/markapi.wiki.git

# Copiar os arquivos de documentação
cp docs/user-guide/README.md markapi.wiki/Home.md
cp docs/user-guide/01-Installation-Guide.md markapi.wiki/Guia-de-Instalacao.md
cp docs/user-guide/02-XML-Validation-Guide.md markapi.wiki/Validacao-de-XML.md

# Commit e push
cd markapi.wiki
git add .
git commit -m "Adicionar documentação do usuário"
git push origin master
```

## Mapeamento de Páginas

| Arquivo no Repositório | Página na Wiki | URL |
|------------------------|----------------|-----|
| `docs/user-guide/README.md` | Home | `/wiki` |
| `docs/user-guide/01-Installation-Guide.md` | Guia de Instalação | `/wiki/Guia-de-Instalacao` |
| `docs/user-guide/02-XML-Validation-Guide.md` | Validação de XML | `/wiki/Validacao-de-XML` |

## Links Internos a Ajustar

Quando copiar o conteúdo para a Wiki, ajuste os links relativos para links da Wiki:

**De:**
```markdown
[Guia de Instalação](./01-Installation-Guide.md)
```

**Para:**
```markdown
[Guia de Instalação](Guia-de-Instalacao)
```

## Páginas Existentes na Wiki

Mantenha as páginas existentes e adicione links para a nova documentação:

- **Guia rápido: baixar e configurar o modelo do MarkAPI para marcação de referências em PDF**
  - URL: https://github.com/scieloorg/markapi/wiki/Guia-r%C3%A1pido:-baixar-e-configurar-o-modelo-do-MarkAPI-para-marca%C3%A7%C3%A3o-de-refer%C3%AAncias-em-PDF
  - Ação: Adicionar link para o novo Guia de Instalação
  - Relação: Complementar - este guia específico pode ser linkado na seção de configuração avançada

## Navegação Sugerida na Wiki

Adicione uma barra lateral (Sidebar) com navegação:

```markdown
## Documentação do Usuário

### Começando
- [Home](Home)
- [Guia de Instalação](Guia-de-Instalacao)

### Usando o MarkAPI
- [Validação de XML](Validacao-de-XML)

### Avançado
- [Configuração de Modelo PDF](Guia-rápido:-baixar-e-configurar-o-modelo-do-MarkAPI-para-marcação-de-referências-em-PDF)

### Recursos
- [Repositório](https://github.com/scieloorg/markapi)
- [Issues](https://github.com/scieloorg/markapi/issues)
- [Documentação SPS](https://docs.scielo.org/)
```

## Checklist de Publicação

- [ ] Criar página Home na Wiki
- [ ] Criar página Guia de Instalação
- [ ] Criar página Validação de XML
- [ ] Ajustar links internos
- [ ] Adicionar barra lateral de navegação
- [ ] Adicionar links nas páginas existentes
- [ ] Revisar formatação
- [ ] Testar todos os links
- [ ] Anunciar nova documentação

## Manutenção Futura

Os arquivos de documentação estão no repositório em `docs/user-guide/`. Quando atualizar:

1. Edite os arquivos `.md` no repositório
2. Faça commit e push das alterações
3. Copie o conteúdo atualizado para a Wiki
4. Mantenha sincronia entre repositório e Wiki

**Vantagens:**
- Documentação versionada com o código
- Facilita revisões via Pull Requests
- Permite que desenvolvedores contribuam com a documentação

## Tarefas Completadas

✅ Criada documentação de instalação (análogo ao Upload application installation)
✅ Criada documentação de validação de XML (análogo ao Converter XML para PDF)
✅ Documentação em português e adaptada para usuários não-desenvolvedores
✅ Incluídas instruções para Windows, macOS e Linux
✅ Adicionadas seções de solução de problemas
✅ Incluídos exemplos práticos e comandos
✅ Criado índice geral da documentação
✅ Atualizado README principal com links para documentação

## Próximos Passos Recomendados

Para completar ainda mais a documentação:

1. **Guia de Conversão XML para PDF** - Instruções detalhadas sobre conversão
2. **Guia de Conversão XML para HTML** - Como gerar versões web
3. **Configuração Avançada** - Personalização de layouts DOCX
4. **Processamento em Lote** - Como processar múltiplos arquivos
5. **Screenshots/Vídeos** - Adicionar capturas de tela da interface
6. **Tutoriais em Vídeo** - Criar vídeos dos processos principais

## Feedback

Se tiver sugestões para melhorar esta documentação:

1. Abra um issue: https://github.com/scieloorg/markapi/issues
2. Envie um Pull Request com melhorias
3. Entre em contato com a equipe SciELO

---

**Preparado por:** Copilot Agent  
**Data:** Outubro 2025  
**Versão:** 1.0
