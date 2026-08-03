# Project structure

```text
flash_llm/
├── .github/                      # CI/CD workflows (GitHub Actions, Docker builds)
├── configs/                      # ZenML YAML configs & environment profiles
│   ├── etl.yaml
│   ├── feature_engineering.yaml
│   └── training.yaml
├── docker/                       # Container setups
│   ├── Dockerfile.zenml
│   └── Dockerfile.api
│
├── src/
│   └── flash_llm/                # Core Python Package
│       ├── __init__.py
│       ├── settings.py           # Centralized Pydantic BaseSettings (.env loader)
│       │
│       ├── domain/               # 🛑 Layer 0: Pure entities & schemas (Zero dependencies)
│       │   ├── __init__.py
│       │   ├── base.py           # Core entity abstractions
│       │   ├── documents.py      # Article, Post, Repository models
│       │   └── dataset.py        # Instruct & DPO dataset definitions
│       │
│       ├── application/          # ⚙️ Layer 1: Business Logic & Pipelines
│       │   ├── __init__.py
│       │   ├── crawlers/         # Polymorphic scrapers (GitHub, Medium, LinkedIn)
│       │   ├── cleaning/         # Text normalizers & chunking
│       │   ├── rag/              # Retrieval & prompt builder logic
│       │   └── evaluation/       # RAG/Model evaluation metrics logic
│       │
│       ├── infrastructure/       # 🔌 Layer 2: External Adapters & Services
│       │   ├── __init__.py
│       │   ├── db/               # MongoDB, Qdrant client wrappers
│       │   ├── clients/          # OpenAI, Anthropic, AWS S3 adapters
│       │   └── tracking/         # Comet ML & Opik loggers
│       │
│       ├── model/                # 🧠 Layer 3: ML Training & Fine-Tuning
│       │   ├── __init__.py
│       │   ├── finetune/         # SFT & DPO training scripts (Unsloth/TRL)
│       │   └── inference/        # vLLM / SageMaker serving handlers
│       │
│       ├── orchestration/        # 🔄 Layer 4: ZenML Pipeline DAGs & Steps
│       │   ├── __init__.py
│       │   ├── steps/            # Modular ZenML steps (@step)
│       │   └── pipelines/        # Composed ZenML DAGs (@pipeline)
│       │
│       └── interface/            # 🌐 Entrypoints (CLI & API)
│           ├── __init__.py
│           ├── cli.py            # Typer/Click CLI commands
│           └── api/              # FastAPI endpoints for inference/ingestion
│
├── tests/                        # Pytest suite
│   ├── unit/                     # Domain & application logic tests (Fast, no DB)
│   ├── integration/              # Infrastructure & DB tests
│   └── e2e/                      # End-to-end pipeline execution tests
│
├── .env.example                  # Environment variable template
├── .gitignore                    # Python/macOS/VS Code exclusions
├── .importlinter                 # Architectural constraints (Prevents domain pollution)
├── justfile                      # Command runner (Replaces poe/make)
├── pyproject.toml                # Managed via uv (Dependencies, ruff, pytest settings)
└── uv.lock                       # Deterministic dependency lockfile
```

### Add **init**.py to every directory inside src/

```
find src -type d -exec touch {}/__init__.py \;
```

# Architecture

```mermaid
classDiagram
    %% ==========================================
    %% DOMAIN LAYER (Pure Python, No DB logic)
    %% ==========================================
    class DocumentDomain {
        <<abstract>>
        + UUID id
        + String title
        + String content
        + HttpUrl source_url
        + get_word_count() int
    }

    class CodebaseDocumentDomain {
        +String codebase_name
        +int stars
        +String link
    }

    class DocumentRepository {
        <<interface>>
        +save_codebase(doc: CodebaseDocumentDomain)
        +get_codebase(url: String) CodebaseDocumentDomain
    }

    DocumentDomain <|-- CodebaseDocumentDomain : Inherits

    %% ==========================================
    %% INFRASTRUCTURE LAYER (MongoDB Specifics)
    %% ==========================================
    class NoSQLBaseDocument {
        <<abstract>>
        +UUID _id
        +datetime created_at
        +save()
        +find()
    }

    class CodebaseDocument {
        +String codebase_name
        +String link
    }

    class MongoRepository {
        +save_codebase(doc: CodebaseDocumentDomain)
    }

    NoSQLBaseDocument <|-- CodebaseDocument : Inherits
    DocumentRepository <|.. MongoRepository : Implements Interface
    MongoRepository ..> CodebaseDocument : Maps Domain to DB Entity

    %% ==========================================
    %% APPLICATION LAYER (Crawlers & ZenML)
    %% ==========================================
    class GithubCrawler {
        -DocumentRepository repository
        +extract(url: String, user_id: UUID)
    }

    class ZenML_FeaturePipeline {
        -DocumentRepository repository
        +extract_and_clean()
    }

    GithubCrawler --> DocumentRepository : Injects & Uses
    GithubCrawler ..> CodebaseDocumentDomain : Scrapes & Creates

    ZenML_FeaturePipeline --> DocumentRepository : Injects & Uses
    ZenML_FeaturePipeline ..> CodebaseDocumentDomain : Processes
```

```mermaid
classDiagram
    %% ==========================================
    %% DOMAIN LAYER (Layer 0: No Dependencies)
    %% ==========================================
    class DataCategory {
        <<enumeration>>
        USERS
        CODEBASES
        ARTICLES
        POSTS
    }

    class UserDomain {
        +UUID id
        +DataCategory category
        +str first_name
        +str last_name
        +Optional~str~ bio
        +full_name() str
    }

    class DocumentDomain {
        <<abstract>>
        +UUID id
        +str title
        +DataCategory category
        +HttpUrl source_url
        +str platform
        +UUID author_id
        +str author_full_name
        +str content
        +word_count() int
    }

    class CodebaseDocumentDomain {
        +DataCategory category
        +str name
    }

    class ArticleDocumentDomain {
        +DataCategory category
    }

    class PostDocumentDomain {
        +DataCategory category
        +Optional~str~ image
    }

    class DocumentRepository {
        <<interface>>
        +save_codebase(codebase: CodebaseDocumentDomain)
    }

    DocumentDomain <|-- CodebaseDocumentDomain
    DocumentDomain <|-- ArticleDocumentDomain
    DocumentDomain <|-- PostDocumentDomain

    %% ==========================================
    %% INFRASTRUCTURE LAYER (Layer 1: External Systems)
    %% ==========================================
    class NoSQLBaseDocument {
        <<abstract>>
    }

    class UserDocument {
        +str first_name
        +str last_name
        +full_name() str
    }

    class Document {
        <<abstract>>
        +str title
        +str link
        +str platform
        +UUID4 author_id
        +str author_full_name
        +str content
    }

    class CodebaseDocument {
        +str codebase_name
    }

    class ArticleDocument {
    }

    class PostDocument {
        +Optional~str~ image
    }

    class MongoDocumentRepository {
        +save_codebase(codebase: CodebaseDocumentDomain)
    }

    NoSQLBaseDocument <|-- UserDocument
    NoSQLBaseDocument <|-- Document
    Document <|-- CodebaseDocument
    Document <|-- ArticleDocument
    Document <|-- PostDocument

    DocumentRepository <|.. MongoDocumentRepository : implements

    %% ==========================================
    %% APPLICATION LAYER (Layer 2: Use Cases & Crawlers)
    %% ==========================================
    class BaseCrawler {
        <<abstract>>
        +DocumentRepository repository
        +extract(url: str, user_id: UUID4, user_full_name: str)
    }

    class GithubCrawler {
        -tuple _ignore
        -Github gh
        +extract(url: str, user_id: UUID4, user_full_name: str)
        -_parse_repo_url(url: str) tuple
        -_should_ignore(file_path: str) bool
        -_fetch_file_content(repo, file_path) str
        -_build_content_string(repo, tree) str
    }

    class CrawlerDispatcher {
        +DocumentRepository repository
        +get_crawler(url: str) BaseCrawler
    }

    BaseCrawler <|-- GithubCrawler
    CrawlerDispatcher --> BaseCrawler : instantiates
    BaseCrawler --> DocumentRepository : injects
    GithubCrawler --> CodebaseDocumentDomain : creates

    %% Relationships across layers
    UserDomain ..> DataCategory
    DocumentDomain ..> DataCategory
```
