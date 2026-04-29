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

Em todos os modos a distribuição é baseada em contêineres Docker
(``local.yml`` para desenvolvimento e ``production.yml`` para produção),
o que padroniza o ambiente e simplifica a instalação.

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

O projeto é construído sobre Django/Wagtail, com processamento
assíncrono via Celery e Redis. Os principais módulos são:

* ``xml_manager`` — gerenciamento do ciclo de vida do XML (upload,
  conversão, validação, empacotamento).
* ``reference`` — marcação de referências bibliográficas, incluindo
  integração com modelos de IA.
* ``model_ai`` — abstração para configuração e uso de LLMs.
* ``docx_layouts`` — modelos de layout DOCX usados como referência para
  a marcação.
* ``packtools`` (dependência externa) — validação do XML e geração de
  PDFs no padrão SPS.


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


Referências
----------------------------------------------------------------------

* `SciELO Publishing Schema <https://scielo.github.io/scielo-publishing-schema/>`_
* `packtools <https://github.com/scieloorg/packtools>`_
* `Guia rápido: baixar e configurar o modelo do MarkAPI <https://github.com/scieloorg/markapi/wiki/Guia-r%C3%A1pido:-baixar-e-configurar-o-modelo-do-MarkAPI-para-marca%C3%A7%C3%A3o-de-refer%C3%AAncias-em-PDF>`_
