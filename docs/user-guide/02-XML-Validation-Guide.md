# Guia de Validação de XML

Este guia explica como utilizar o MarkAPI para validar documentos XML de acordo com os padrões SciELO.

## O que é a Validação de XML?

A validação de XML no MarkAPI verifica se seus documentos estão em conformidade com:

1. **Estrutura XML**: Se o arquivo está bem-formado
2. **Schema SPS (SciELO Publishing Schema)**: Se segue o padrão de publicação SciELO
3. **Regras de Negócio**: Se atende aos requisitos específicos do SciELO
4. **Conteúdo**: Se os dados estão completos e corretos

## Acessar o Sistema

### 1. Fazer Login

1. Acesse a URL do MarkAPI instalado (ex: `http://seu-servidor:8000`)
2. Clique em **"Login"** ou **"Entrar"**
3. Digite seu **usuário** e **senha**
4. Clique em **"Entrar"**

Se você é administrador, também pode acessar o painel administrativo em `/django-admin/`.

### 2. Navegação Inicial

Após o login, você verá o painel principal com opções para:
- Enviar novos documentos XML
- Visualizar documentos já enviados
- Verificar status de validações e conversões

## Como Validar um Documento XML

### Método 1: Upload Através da Interface Web

#### Passo 1: Acessar a Área de Upload

1. No menu principal, clique em **"XML Documents"** ou **"Documentos XML"**
2. Clique no botão **"Add XML Document"** ou **"Adicionar Documento XML"**

#### Passo 2: Selecionar o Arquivo

1. Clique em **"Choose File"** ou **"Escolher Arquivo"**
2. Navegue até o arquivo XML em seu computador
3. Selecione o arquivo (formato `.xml`)
4. Clique em **"Open"** ou **"Abrir"**

**Requisitos do Arquivo:**
- Formato: `.xml`
- Tamanho máximo: 10 MB (configurável)
- Codificação: UTF-8 recomendada
- Deve ser um XML válido de artigo científico no padrão SPS

#### Passo 3: Enviar o Documento

1. Revise as informações do arquivo
2. Clique em **"Upload"** ou **"Enviar"**
3. Aguarde a confirmação do upload

#### Passo 4: Aguardar o Processamento

Após o upload, o MarkAPI automaticamente:
1. Valida o arquivo XML
2. Gera um relatório de validação
3. Identifica erros e avisos
4. Opcionalmente, inicia a conversão para PDF/HTML (se configurado)

O processamento é feito em segundo plano e pode levar alguns segundos a minutos, dependendo do tamanho do arquivo.

### Método 2: Upload em Lote (Administradores)

Para enviar múltiplos arquivos:

1. Acesse o **painel administrativo** (`/django-admin/`)
2. Vá em **XML Manager** > **XML Documents**
3. Use a opção de importação em massa (se disponível)

## Interpretar os Resultados da Validação

### Acessar o Relatório de Validação

1. Na lista de **"XML Documents"**, localize seu arquivo
2. Clique no nome do documento para ver os detalhes
3. Na página de detalhes, você verá:
   - **Status do documento**
   - **Data de upload**
   - **Links para downloads**

### Arquivos Gerados

Após a validação, você terá acesso a:

#### 1. Arquivo de Validação (CSV)

**Localização**: Campo "Validation File" ou link "Download Validation Report"

**Conteúdo**: Tabela com todos os resultados da validação

**Colunas do CSV:**
- **line**: Número da linha no XML onde ocorreu o problema
- **message**: Descrição do erro ou aviso
- **level**: Nível de severidade (ERROR, WARNING, INFO)
- **type**: Tipo de validação (XML_STRUCTURE, SCHEMA, BUSINESS_RULE, CONTENT)
- **element**: Elemento XML onde ocorreu o problema

**Exemplo:**
```csv
line,message,level,type,element
15,"Missing required element 'article-title'",ERROR,SCHEMA,title-group
23,"Invalid date format",WARNING,CONTENT,pub-date
45,"Author affiliation not found",WARNING,BUSINESS_RULE,contrib
```

#### 2. Arquivo de Exceções

**Localização**: Campo "Exceptions File" ou link "Download Exceptions"

**Conteúdo**: Detalhes técnicos de erros graves que impediram a validação completa

### Níveis de Severidade

#### ERROR (Erro)
- **Cor**: Vermelho
- **Significado**: Problema crítico que impede a publicação
- **Ação necessária**: Corrigir obrigatoriamente

**Exemplos:**
- Estrutura XML mal-formada
- Elementos obrigatórios ausentes
- Valores inválidos em campos obrigatórios

#### WARNING (Aviso)
- **Cor**: Amarelo/Laranja
- **Significado**: Problema que pode afetar a qualidade ou apresentação
- **Ação necessária**: Revisar e corrigir se possível

**Exemplos:**
- Metadados incompletos
- Formatação inconsistente
- Referências sem DOI

#### INFO (Informação)
- **Cor**: Azul
- **Significado**: Sugestão de melhoria ou informação relevante
- **Ação necessária**: Opcional

**Exemplos:**
- Sugestões de otimização
- Informações sobre campos opcionais
- Estatísticas do documento

## Corrigir Problemas e Revalidar

### Passo 1: Baixar o Relatório de Validação

1. Clique no link **"Download Validation Report"**
2. Abra o arquivo CSV em um editor de planilhas (Excel, LibreOffice Calc)
3. Ordene por nível de severidade (ERRORs primeiro)

### Passo 2: Analisar os Erros

Para cada erro:
1. Veja o número da **linha** no XML
2. Leia a **mensagem** de erro
3. Identifique o **elemento** afetado
4. Consulte a documentação SPS se necessário

### Passo 3: Editar o Arquivo XML

1. Abra o arquivo XML original em um editor de texto (VSCode, Notepad++, etc.)
2. Navegue até a linha indicada no relatório
3. Corrija o problema conforme a mensagem de erro
4. Salve o arquivo

**Dica:** Use um editor XML com validação integrada para evitar erros de sintaxe.

### Passo 4: Reenviar o Arquivo

1. Volte ao MarkAPI
2. Faça upload do arquivo XML corrigido
3. Aguarde a nova validação
4. Compare os resultados com a validação anterior

## Validação via API (Usuários Avançados)

Para integração automática, o MarkAPI oferece uma API REST.

### Autenticação

```bash
# Obter token de autenticação
curl -X POST http://seu-servidor:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "seu-usuario", "password": "sua-senha"}'
```

### Enviar XML para Validação

```bash
# Upload e validação
curl -X POST http://seu-servidor:8000/api/xml-documents/ \
  -H "Authorization: Token seu-token-aqui" \
  -F "xml_file=@/caminho/para/arquivo.xml"
```

### Verificar Status

```bash
# Obter status do documento
curl -X GET http://seu-servidor:8000/api/xml-documents/{id}/ \
  -H "Authorization: Token seu-token-aqui"
```

### Baixar Relatório

```bash
# Download do relatório de validação
curl -X GET http://seu-servidor:8000/api/xml-documents/{id}/validation-report/ \
  -H "Authorization: Token seu-token-aqui" \
  -o validation-report.csv
```

## Problemas Comuns e Soluções

### Erro: "XML mal-formado"

**Causa**: Sintaxe XML inválida

**Solução**:
1. Verifique se todas as tags estão fechadas corretamente
2. Verifique caracteres especiais (use entidades XML como `&lt;`, `&gt;`, `&amp;`)
3. Valide a codificação do arquivo (deve ser UTF-8)
4. Use um validador XML online para identificar o problema

### Erro: "Elemento obrigatório ausente"

**Causa**: O XML não contém todos os elementos requeridos pelo padrão SPS

**Solução**:
1. Consulte a mensagem de erro para identificar qual elemento está faltando
2. Adicione o elemento no local correto do XML
3. Consulte a documentação SPS: https://docs.scielo.org/

### Erro: "Schema validation failed"

**Causa**: O XML não está em conformidade com o schema SPS

**Solução**:
1. Verifique se está usando a versão correta do SPS
2. Revise a estrutura do documento
3. Compare com exemplos de XML válidos
4. Consulte a documentação: https://docs.scielo.org/

### Aviso: "Referências incompletas"

**Causa**: Referências bibliográficas sem informações completas

**Solução**:
1. Complete os metadados das referências (autores, título, ano, etc.)
2. Adicione DOI quando disponível
3. Verifique a formatação das citações

### Upload falha ou trava

**Causa**: Arquivo muito grande ou problema de rede

**Solução**:
1. Verifique o tamanho do arquivo (máximo configurado)
2. Verifique sua conexão de internet
3. Tente novamente em alguns minutos
4. Contate o administrador se o problema persistir

## Boas Práticas

### Antes de Validar

1. **Verifique o arquivo localmente**: Use um editor XML com validação
2. **Garanta a codificação UTF-8**: Evite problemas com caracteres especiais
3. **Organize seus arquivos**: Use nomes descritivos (ex: `artigo-v01.xml`, `artigo-v02.xml`)
4. **Mantenha backups**: Guarde cópias dos arquivos originais

### Durante a Validação

1. **Documente as correções**: Mantenha um registro das alterações feitas
2. **Valide incrementalmente**: Corrija erros e valide novamente
3. **Priorize ERRORs**: Corrija erros críticos antes dos avisos
4. **Teste diferentes cenários**: Valide com diferentes tipos de conteúdo

### Depois da Validação

1. **Revise o relatório completo**: Não ignore avisos
2. **Mantenha registros**: Guarde os relatórios de validação
3. **Documente problemas recorrentes**: Ajude a melhorar o processo
4. **Compartilhe conhecimento**: Ajude outros usuários com problemas similares

## Recursos Adicionais

### Documentação Técnica

- **SPS (SciELO Publishing Schema)**: https://docs.scielo.org/
- **PMC/JATS**: https://jats.nlm.nih.gov/
- **Packtools**: https://github.com/scieloorg/packtools

### Ferramentas Auxiliares

- **XML Validators Online**: https://www.xmlvalidation.com/
- **Visual Studio Code**: Editor com extensões XML
- **Oxygen XML Editor**: Editor XML profissional
- **LibreOffice Calc**: Para visualizar relatórios CSV

### Exemplos de XML

Consulte o repositório de exemplos:
- https://github.com/scieloorg/scielo_publishing_schema
- Procure por arquivos de exemplo na pasta `tests/fixtures/`

## Suporte

Se você encontrar problemas ou tiver dúvidas:

1. **Consulte a documentação**: https://github.com/scieloorg/markapi/wiki
2. **Abra um issue**: https://github.com/scieloorg/markapi/issues
3. **Contate o suporte**: Através dos canais oficiais SciELO

## Fluxo de Trabalho Recomendado

```
1. Preparar arquivo XML
   ↓
2. Fazer upload no MarkAPI
   ↓
3. Aguardar validação automática
   ↓
4. Baixar relatório de validação
   ↓
5. Analisar erros e avisos
   ↓
6. Corrigir problemas no XML
   ↓
7. Reenviar arquivo corrigido
   ↓
8. Repetir até validação bem-sucedida
   ↓
9. Proceder com conversão para PDF/HTML
```

## Próximos Passos

Após validar seu XML com sucesso:

- **[Converter XML para PDF](./03-XML-to-PDF-Conversion-Guide.md)**: Gere PDFs do seu artigo
- **[Converter XML para HTML](./04-XML-to-HTML-Conversion-Guide.md)**: Gere visualização web
- **[Personalizar Layouts](./05-DOCX-Layout-Configuration.md)**: Customize a aparência dos PDFs
