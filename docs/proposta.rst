Proposta do Projeto MarkAPI
======================================================================

Visão Geral
----------------------------------------------------------------------

O **MarkAPI** é uma aplicação para apoiar o fluxo editorial da SciELO,
oferecendo um conjunto de ferramentas para **marcar**, **validar** e
**converter** documentos no contexto de publicação científica. A partir
de um arquivo de texto produzido pelo autor ou pelo editor (DOCX), a
aplicação gera um arquivo XML compatível com o
`SciELO Publishing Schema <https://scielo.github.io/scielo-publishing-schema/>`_
e empacota os ativos digitais do artigo (XML, PDFs, imagens, suplementos)
de acordo com a documentação oficial do SPS.

A ferramenta combina automação assistida por LLM (Large Language Models)
com possibilidade de **ajustes manuais** pelo usuário, permitindo que
equipes editoriais reduzam o tempo de marcação sem perder o controle
sobre o resultado final.


Modos de Instalação
----------------------------------------------------------------------

Apesar de ser uma aplicação web, o MarkAPI foi projetado para ser
flexível quanto à forma de implantação, atendendo desde um único
marcador em sua estação de trabalho até equipes editoriais inteiras
em servidores institucionais:

* **Desktop monousuário**: instalável em um único computador, com a
  interface web acessada pelo navegador local. Indicado para
  marcadores autônomos ou para volumes pequenos de processamento.
* **Servidor em intranet**: instalado em um servidor da rede interna
  da instituição, permitindo uso compartilhado por uma equipe
  editorial, com centralização de configurações, modelos e histórico
  de marcações.
* **Servidor na internet**: instalado em um servidor exposto à
  internet, possibilitando o uso distribuído por equipes em
  diferentes localidades.

Em todos os modos a distribuição é baseada em contêineres Docker.
Para desenvolvimento há um Compose pronto em ``local.yml`` com os
serviços ``django``, ``postgres``, ``redis``, ``celeryworker``,
``celerybeat``, ``flower`` e ``mailhog``. Para produção está
prevista a entrega de um ``production.yml`` análogo (ainda em
construção), além dos manifestos Kubernetes em ``kubernetes/``
(Deployments para Django/Celery e StatefulSets para PostgreSQL e
Redis) para ambientes maiores. Essa padronização simplifica a
instalação em qualquer um dos modos descritos acima.

Requisitos de hardware e opções de LLM
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

O desempenho da marcação assistida por IA depende fortemente do
ambiente em que o MarkAPI é instalado e do modelo de linguagem (LLM)
escolhido:

* **Servidor com GPU**: cenário de melhor desempenho. Permite o uso
  de LLMs maiores, com tempos de resposta mais curtos para a marcação
  de referências e demais tarefas assistidas por IA.
* **Servidor ou desktop sem GPU**: a aplicação continua funcional,
  mas é recomendado o uso de um **modelo LLM pequeno**, executado em
  CPU. O custo computacional é maior por requisição e a velocidade,
  menor; ainda assim, atende cenários de baixo a médio volume.
* **API externa de LLM (opcional)**: é possível configurar o MarkAPI
  para utilizar uma **API de LLM contratada** (provedor externo). Nesse
  caso, o **custo financeiro** da API e a **escolha/responsabilidade
  pelo modelo** ficam a cargo do **usuário ou da instituição** que
  contratou o serviço; o projeto MarkAPI não se responsabiliza por
  esses custos nem pelo conteúdo gerado por modelos de terceiros.


Funcionalidades
----------------------------------------------------------------------

Conversão de DOCX para XML (SPS)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Recebe um arquivo ``.docx`` enviado pelo usuário.
* Aplica regras de marcação para gerar um XML aderente ao
  *SciELO Publishing Schema*.
* Identifica metadados, seções, referências, figuras, tabelas e demais
  elementos estruturais do artigo.

Geração do pacote SPS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Cria um pacote ``.zip`` no formato definido pela documentação do
  *SciELO Publishing Schema*, contendo:

  * o arquivo XML;
  * um PDF para cada idioma do texto;
  * imagens (figuras, gráficos, equações renderizadas);
  * outros ativos digitais (materiais suplementares).

* Os arquivos são nomeados de acordo com a convenção do SPS, garantindo
  rastreabilidade e compatibilidade com os fluxos de ingestão da SciELO.

Validação de XML e geração de PDFs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Utiliza a biblioteca
  `packtools <https://github.com/scieloorg/packtools>`_ como dependência
  principal para:

  * **validar** o XML contra o schema, regras de negócio e conteúdo;
  * **gerar PDFs** a partir do XML, em cada idioma disponível.

Marcação automática de referências bibliográficas
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Um dos serviços centrais do MarkAPI é a **marcação automática das
referências bibliográficas** do artigo. Esse serviço é exposto via API
REST (``ReferenceViewSet`` em ``reference/api/v1/views.py``) e também
utilizado internamente pelo fluxo de conversão DOCX → XML.

* **Entrada**: uma referência em texto livre (``mixed-citation``) ou um
  bloco contendo várias referências, uma por linha. A API REST aceita
  requisições ``POST`` autenticadas com o JSON
  ``{"reference": "...", "type": "xml" | "marked"}``.
* **Processamento**:

  * O texto é submetido a um LLM (``LlamaService`` em ``model_ai``,
    com prompts e ``response_format`` definidos em
    ``reference/config.py``).
  * O modelo identifica os elementos da referência — autores, título do
    trabalho, fonte, ano, volume, fascículo, páginas, DOI, tipo de
    publicação (artigo, livro, capítulo, *webpage*, *data*, etc.).
  * O resultado é normalizado e convertido em um elemento
    ``<element-citation>`` no padrão SPS (ver ``reference/data_utils.py``,
    função ``get_xml``), incluindo atributos como ``publication-type`` e
    *namespaces* (por exemplo, ``xlink``) quando aplicável.

* **Persistência e reuso**: cada referência marcada é armazenada nos
  modelos ``Reference`` e ``ElementCitation``, com um ``status``
  controlado (``ReferenceStatus``). Requisições subsequentes para a
  mesma ``mixed-citation`` reaproveitam o resultado, evitando chamadas
  repetidas ao LLM.
* **Saída**: a API devolve, conforme o parâmetro ``type``:

  * ``xml`` — o trecho ``<element-citation>`` pronto para ser embutido
    no XML SPS;
  * ``marked`` — a representação intermediária estruturada (campos
    identificados pelo modelo).

* **Observabilidade e robustez**: erros do LLM
  (``LlamaDisabledError``, ``LlamaNotInstalledError``,
  ``LlamaModelNotFoundError`` e exceções inesperadas) são registrados
  via ``tracker.GeneralEvent``, permitindo auditoria e diagnóstico do
  serviço de marcação.
* **Revisão manual**: o resultado da marcação automática de referências
  pode ser revisado e ajustado pelo usuário antes da geração final do
  pacote SPS, mantendo a qualidade exigida pelo fluxo editorial.

A configuração do modelo de IA usado nesse serviço é descrita no
`Guia rápido: baixar e configurar o modelo do MarkAPI <https://github.com/scieloorg/markapi/wiki/Guia-r%C3%A1pido:-baixar-e-configurar-o-modelo-do-MarkAPI-para-marca%C3%A7%C3%A3o-de-refer%C3%AAncias-em-PDF>`_.

Marcação automatizada com LLM (configurável)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* O uso de modelos de linguagem (LLM) é **opcional e configurável**.
* Permite acelerar a marcação de partes complexas do documento (por
  exemplo, referências bibliográficas) por meio de modelos como os
  disponíveis via Google Generative AI ou modelos locais
  (ver módulo ``model_ai``).
* O administrador pode habilitar, desabilitar ou trocar o provedor do
  LLM conforme a política da instituição.

Ajustes manuais pelo usuário
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Mesmo quando a marcação automatizada está habilitada, o usuário tem
  controle total para **revisar e corrigir** o resultado.
* A interface permite ajustes manuais antes da geração final do pacote,
  garantindo a qualidade exigida pelo fluxo editorial.


Arquitetura em alto nível
----------------------------------------------------------------------

Stack tecnológica
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

O MarkAPI é uma aplicação Python construída sobre o ecossistema
Django, com camadas adicionais para CMS, processamento assíncrono,
API REST e integração com modelos de linguagem (LLMs).

* **Linguagem e runtime**

  * Python 3 (executado em contêineres Docker baseados em imagens
    oficiais; ver ``compose/local/django/Dockerfile`` e
    ``compose/production/``).

* **Framework web e CMS**

  * `Django 5 <https://www.djangoproject.com/>`_ — framework web
    principal, ORM, autenticação, *admin* e *settings* organizados
    em ``config/settings/`` (``base.py``, ``local.py``,
    ``production.py``).
  * `Wagtail 6 <https://wagtail.org/>`_ — CMS sobre Django para as
    páginas do site, *snippets* e administração editorial. Apps
    auxiliares: ``wagtail-modeladmin``, ``wagtailmenus``,
    ``wagtail-localize`` (i18n), ``wagtail-autocomplete`` e
    ``wagtail-django-recaptcha``. *Hooks* específicos do projeto
    ficam em ``<app>/wagtail_hooks.py``.
  * ``django-environ`` para configuração via variáveis de ambiente
    (arquivos em ``.envs/.local/`` e ``.envs/.production/``).
  * ``django-compressor`` e ``whitenoise`` para *assets* estáticos.

* **API REST**

  * `Django REST Framework 3.15 <https://www.django-rest-framework.org/>`_
    para a camada de API (``reference/api/v1/views.py``,
    ``config/api_router.py``).
  * `djangorestframework-simplejwt <https://django-rest-framework-simplejwt.readthedocs.io/>`_
    para autenticação JWT dos clientes da API.

* **Banco de dados**

  * `PostgreSQL <https://www.postgresql.org/>`_ como banco
    relacional principal (imagem custom em
    ``compose/production/postgres/Dockerfile``; em produção,
    StatefulSet em ``kubernetes/hml/statefulset-markapi-hml-postgresql.yml``).
  * Driver ``psycopg2-binary`` (em produção).

* **Processamento assíncrono e agendamento**

  * `Celery 5 <https://docs.celeryq.dev/>`_ como *task queue*
    distribuída para as operações de marcação, conversão,
    validação e empacotamento (``model_ai/tasks.py``,
    ``xml_manager/tasks.py``). A configuração da aplicação Celery
    está em ``config/celery_app.py``.
  * `Redis 6 <https://redis.io/>`_ como *broker* e *backend* de
    resultados (``redis``/``hiredis`` no ``requirements/base.txt``;
    StatefulSet em ``kubernetes/hml/statefulset-markapi-hml-redis.yml``).
  * `Kombu 5 <https://kombu.readthedocs.io/>`_ — biblioteca de
    mensageria usada pelo Celery.
  * `django-celery-beat <https://django-celery-beat.readthedocs.io/>`_
    para tarefas agendadas (cron) gerenciáveis pelo *admin*, com
    ``django_celery_results`` para persistência de resultados.
  * `Flower <https://flower.readthedocs.io/>`_ para monitoramento
    de *workers* e tarefas Celery (serviço ``flower`` em
    ``local.yml``).

* **Servidor de aplicação (produção)**

  * `Gunicorn <https://gunicorn.org/>`_ + `gevent <http://www.gevent.org/>`_
    como WSGI server (ver ``requirements/production.txt``).

* **Processamento de XML, DOCX e SPS**

  * `lxml <https://lxml.de/>`_ — parsing/serialização de XML e
    aplicação de XSLT.
  * `python-docx <https://python-docx.readthedocs.io/>`_ — leitura
    e geração de documentos ``.docx``.
  * `packtools <https://github.com/scieloorg/packtools>`_
    (``git+...packtools@4.12.6``) — validação do XML e geração de
    PDFs no padrão SPS.
  * `langdetect <https://pypi.org/project/langdetect/>`_ /
    `langid <https://github.com/saffsd/langid.py>`_ — detecção de
    idioma.
  * `tenacity <https://tenacity.readthedocs.io/>`_ — *retries*
    para operações sujeitas a falhas transitórias (downloads,
    chamadas a serviços externos).

* **Modelos de linguagem (LLM)**

  * `llama-cpp-python <https://llama-cpp-python.readthedocs.io/>`_
    para execução local de modelos LLaMA/GGUF, com suporte a CPU
    e GPU (``model_ai/llama.py``, ``LlamaService``).
  * `huggingface-hub <https://pypi.org/project/huggingface-hub/>`_
    para *download* dos pesos do modelo a partir de repositórios
    Hugging Face (com instalação opcional via
    ``requirements/extra-llama.txt``).
  * `google-generativeai <https://pypi.org/project/google-generativeai/>`_
    como alternativa de provedor externo (Google Gemini), conforme
    ``reference/config_gemini.py``.

* **E-mail e observabilidade**

  * `MailHog <https://github.com/mailhog/MailHog>`_ para captura
    de e-mails em desenvolvimento (``mailhog`` em ``local.yml``).
  * ``django-anymail`` para envio em produção.
  * `Sentry <https://sentry.io/>`_ (``sentry-sdk[django]``) e
    `Elastic APM <https://pypi.org/project/elastic-apm/>`_ para
    monitoramento e *tracing* em produção.
  * App ``tracker`` interno (``tracker.GeneralEvent``) para
    registro estruturado de eventos do domínio (incluindo erros
    do LLM).

* **Empacotamento e distribuição**

  * **Docker / Docker Compose** para desenvolvimento (``local.yml``).
  * **Kubernetes** para produção, com manifestos em ``kubernetes/``
    (Deployments para ``django``, ``celeryworker``, ``celerybeat``;
    StatefulSets para ``postgresql`` e ``redis``; *Services* e
    *ConfigMaps* correspondentes).

* **Qualidade de código**

  * ``flake8`` (linha máxima de 120 caracteres) e ``isort``,
    configurados em ``setup.cfg`` (migrations excluídas do *lint*).

Organização do código
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A aplicação está dividida em apps Django independentes, registrados
em ``INSTALLED_APPS`` (ver ``config/settings/base.py``):

* ``config`` — projeto Django: ``settings/`` por ambiente,
  ``urls.py``, ``api_router.py``, ``celery_app.py`` e ``wsgi.py``.
* ``core`` — páginas Wagtail (``home``, ``search``), templates,
  *static files* e *hooks* globais.
* ``core_settings`` — *settings* configuráveis pela equipe editorial
  via *admin*.
* ``users`` — modelo de usuário e autenticação.
* ``xml_manager`` — gerenciamento do ciclo de vida do XML (upload,
  conversão DOCX → XML SPS, validação via ``packtools``,
  empacotamento ``.zip`` SPS). Inclui ``models.py``, ``tasks.py``
  (Celery), ``views.py`` e ``utils.py``.
* ``reference`` — marcação de referências bibliográficas:

  * ``api/v1/views.py`` — ``ReferenceViewSet`` (DRF) com
    autenticação JWT;
  * ``marker.py`` — orquestração da chamada ao LLM;
  * ``data_utils.py`` — função ``get_xml`` que serializa o
    resultado em ``<element-citation>`` SPS;
  * ``config.py`` — *prompts* e ``response_format`` do LLM local;
  * ``config_gemini.py`` — *prompts* e configuração para o
    provedor Google Generative AI;
  * ``models.py`` — ``Reference``, ``ElementCitation``,
    ``ReferenceStatus`` (persistência e reuso).

* ``model_ai`` — abstração para configuração e uso de LLMs:
  ``llama.py`` (``LlamaService`` baseado em ``llama-cpp-python``),
  ``exceptions.py`` (``LlamaDisabledError``,
  ``LlamaNotInstalledError``, ``LlamaModelNotFoundError``),
  ``tasks.py`` (Celery) e ``messages.py``.
* ``docx_layouts`` — modelos de layout DOCX usados como referência
  para a marcação automatizada.
* ``tracker`` — registro de eventos (``GeneralEvent``) para
  auditoria e diagnóstico (ex.: falhas do LLM no
  ``ReferenceViewSet``).
* ``django_celery_beat`` — agendamento de tarefas periódicas via
  *admin*.

Fluxo de execução típico
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. O usuário faz *upload* de um ``.docx`` pela interface Wagtail
   (``xml_manager``).
2. Uma tarefa Celery (``xml_manager/tasks.py``) extrai conteúdo via
   ``python-docx`` e produz um XML inicial.
3. As referências bibliográficas são enviadas ao serviço
   ``reference`` (em lote ou via API REST), que invoca o
   ``LlamaService`` (ou Google Generative AI) e armazena o resultado
   em ``Reference``/``ElementCitation``.
4. ``packtools`` valida o XML final e gera os PDFs por idioma.
5. ``xml_manager`` empacota XML, PDFs, imagens e ativos em um
   ``.zip`` SPS pronto para ingestão.
6. Eventos de erro/sucesso são registrados em ``tracker`` e
   *workers* podem ser monitorados via Flower.


Público-alvo
----------------------------------------------------------------------

* **Marcadores autônomos**: profissionais que realizam marcação de
  artigos em uma estação de trabalho individual, em modo
  monousuário (instalação desktop).
* **Equipes editoriais de periódicos científicos**: equipes da Rede
  SciELO ou de outras instituições que precisam compartilhar a
  ferramenta em um servidor de intranet, com vários usuários
  simultâneos.
* **Instituições com publicação distribuída**: organizações que
  desejam disponibilizar o MarkAPI em um servidor exposto à internet
  para uso por equipes em diferentes localidades.
* **Editores que produzem conteúdo em DOCX** e precisam publicá-lo
  no formato SPS, com a opção de acelerar a marcação por meio de
  LLMs (locais ou contratados via API externa, conforme as
  possibilidades descritas em *Modos de Instalação*).


Requisitos não funcionais
----------------------------------------------------------------------

Estes requisitos orientam o projeto e a evolução do MarkAPI,
independentemente das funcionalidades específicas:

* **Portabilidade de instalação**: a aplicação deve poder ser
  instalada nos três modos descritos (desktop monousuário, servidor
  em intranet e servidor na internet), reaproveitando o mesmo
  conjunto de imagens Docker e o mesmo código-base.
* **Reprodutibilidade do ambiente**: dependências fixadas em
  ``requirements/base.txt``, ``requirements/local.txt`` e
  ``requirements/production.txt``; ambiente padronizado via Docker
  Compose (``local.yml``, ``production.yml`` previsto) e manifestos
  Kubernetes (``kubernetes/``).
* **Internacionalização (i18n) e localização (l10n)**: suporte a
  múltiplos idiomas via ``django.middleware.locale.LocaleMiddleware``
  e ``wagtail-localize``; conteúdo SPS multilíngue (PDFs por idioma)
  com detecção via ``langdetect``/``langid``.
* **Escalabilidade horizontal**: separação clara entre processo web
  (Django/Gunicorn) e *workers* assíncronos (Celery), permitindo
  escalar cada camada de forma independente em Kubernetes.
* **Resiliência e tolerância a falhas**: tarefas idempotentes em
  Celery, *retries* com ``tenacity`` para operações sujeitas a
  falhas transitórias (downloads, chamadas a serviços externos) e
  *broker* Redis com persistência configurável.
* **Observabilidade**: registro estruturado de eventos do domínio
  via ``tracker.GeneralEvent``, monitoramento de *workers* e tarefas
  via Flower, integração com Sentry e Elastic APM em produção.
* **Segurança**: autenticação JWT na API REST
  (``djangorestframework-simplejwt``), proteção CSRF/clickjacking,
  reCAPTCHA em formulários públicos (``wagtail-django-recaptcha``)
  e gestão de segredos via variáveis de ambiente
  (``django-environ``, arquivos em ``.envs/``); nenhum segredo
  comitado no repositório.
* **Privacidade dos dados**: a marcação pode ser executada
  inteiramente *on-premise* (LLM local), sem envio dos manuscritos
  a serviços externos. Quando o usuário/instituição opta por uma
  API de LLM contratada, a responsabilidade por custo, política
  de privacidade e termos de uso do provedor é do usuário.
* **Desempenho**: aceleração por GPU quando disponível
  (``llama-cpp-python``); processamento assíncrono em segundo plano
  para não bloquear a interface; *cache* e reuso de marcações de
  referências já processadas (``Reference``/``ElementCitation``
  controlados por ``ReferenceStatus``).
* **Conformidade com o SPS**: o XML produzido deve passar nas
  validações do ``packtools`` (versão fixada em
  ``requirements/base.txt``), garantindo aderência ao SciELO
  Publishing Schema.
* **Manutenibilidade**: organização modular em apps Django
  independentes, código sob ``flake8`` (linha máxima de 120
  caracteres) e ``isort``, conforme ``setup.cfg``.
* **Auditabilidade**: histórico de alterações de marcações e
  status (``ReferenceStatus``), tarefas Celery persistidas via
  ``django_celery_results`` e eventos relevantes em ``tracker``.
* **Compatibilidade com navegadores modernos** para a interface
  Wagtail e *assets* servidos via ``whitenoise``/``django-compressor``.


Perspectivas (funcionalidades futuras)
----------------------------------------------------------------------

A seguir, sugestões de evolução do MarkAPI a serem priorizadas
conforme a demanda da comunidade SciELO e dos editores parceiros.
Estas são *propostas*, ainda não implementadas:

* **Suporte a novos provedores de LLM**: além do LLaMA local
  (``llama-cpp-python``) e Google Gemini
  (``google-generativeai``), oferecer integração configurável com
  outros provedores (OpenAI, Anthropic, Mistral, Azure OpenAI,
  modelos locais via Ollama/vLLM), com seleção pelo administrador
  via ``core_settings``.
* **Marcação assistida de outros elementos do SPS**: estender o
  serviço atual de referências para outros blocos do XML SPS, como
  *afiliações*, *autores*, *agradecimentos*, *financiamento*,
  *figuras/tabelas* e *seções do corpo do texto*.
* **Editor visual de XML SPS no navegador**: interface WYSIWYG
  integrada ao Wagtail para revisão e ajuste manual do XML gerado,
  com destaque das diferenças entre versões (LLM × revisão humana).
* **Importação a partir de outros formatos**: além de ``.docx``,
  aceitar ``.odt``, ``.rtf``, LaTeX e PDF (com OCR opcional)
  como entrada para conversão em XML SPS.
* **Validação incremental e diagnósticos amigáveis**: feedback em
  tempo real durante a marcação, com mensagens de erro do
  ``packtools`` traduzidas e contextualizadas para o editor.
* **Integração com fontes externas de metadados**: enriquecimento
  automático de referências a partir de Crossref, PubMed, DOI,
  ORCID, ROR (afiliações) e SciELO, reduzindo erros de marcação
  e padronizando identificadores.
* **Empacotamento e ingestão automatizada**: publicação direta do
  ``.zip`` SPS em sistemas downstream (SciELO PS, OJS, repositórios
  institucionais) via APIs ou *webhooks*.
* **Integração com fluxos editoriais**: conectores com OJS, ScholarOne
  e plataformas similares para importar manuscritos aceitos e
  exportar pacotes SPS de volta ao fluxo editorial.
* **Versionamento e auditoria de marcações**: histórico completo
  por documento e por referência, com diff entre versões e
  possibilidade de *rollback*.
* **Painéis e métricas**: *dashboard* no admin com tempo médio de
  marcação por artigo, taxa de revisão manual sobre marcação
  automática, qualidade do LLM por tipo de referência e custo
  estimado quando usada API externa.
* **Treinamento/ajuste fino do LLM local**: pipeline opcional para
  *fine-tuning* do modelo com exemplos curados pela equipe
  editorial, melhorando a precisão para o vocabulário e o estilo
  de cada periódico.
* **API pública versionada e documentada**: expansão do
  ``ReferenceViewSet`` para uma API REST completa (e/ou GraphQL)
  com documentação OpenAPI/Swagger e versionamento (``/api/v1``,
  ``/api/v2``).
* **SSO e perfis de acesso**: integração com provedores SAML/OIDC
  (Shibboleth, Keycloak, ORCID) e perfis granulares por papel
  (autor, marcador, revisor, administrador).
* **Modo *offline* desktop**: empacotamento *all-in-one* (por
  exemplo via Docker Desktop ou um instalador específico) para o
  modo monousuário, com modelo LLM pequeno embutido e atualizações
  controladas pelo próprio usuário.
* **Acessibilidade (WCAG)**: revisão da interface Wagtail para
  conformidade com diretrizes de acessibilidade.
* **Telemetria opcional e anonimizada**: coleta opt-in de métricas
  agregadas de uso para orientar a evolução do produto, sem
  compartilhamento de conteúdo de manuscritos.


Referências
----------------------------------------------------------------------

* `SciELO Publishing Schema <https://scielo.github.io/scielo-publishing-schema/>`_
* `packtools <https://github.com/scieloorg/packtools>`_
* `Guia rápido: baixar e configurar o modelo do MarkAPI <https://github.com/scieloorg/markapi/wiki/Guia-r%C3%A1pido:-baixar-e-configurar-o-modelo-do-MarkAPI-para-marca%C3%A7%C3%A3o-de-refer%C3%AAncias-em-PDF>`_
