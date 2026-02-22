# Kardechat

Chatbot espírita baseado nos 5 livros do Pentateuco Espírita de Allan Kardec. Utiliza **Q-to-Q semantic matching** no Livro dos Espíritos e **RAG tradicional** nos demais livros, com roteamento baseado em confiança.

## Arquitetura

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────┐
│  Next.js (UI)   │────▶│  FastAPI (API)    │────▶│  MongoDB  │
│  + Supabase Auth│     │  + OpenAI         │     │  + Vectors│
└─────────────────┘     └──────────────────┘     └───────────┘
```

### Sistema Multi-Camada (Confidence-Based Routing)

| Similaridade | Confiança | Ação |
|---|---|---|
| > 0.88 | Alta | Resposta direta do Livro dos Espíritos |
| 0.75 – 0.88 | Média | LLM reformula com base nas perguntas encontradas |
| < 0.75 | Baixa | RAG completo nos 5 livros do Pentateuco |

### Q-to-Q Matching (Livro dos Espíritos)

O Livro dos Espíritos é uma obra de perguntas e respostas. Em vez de RAG tradicional:

- **Indexamos apenas as perguntas** (não as respostas)
- Quando o usuário pergunta algo, buscamos a **pergunta mais semelhante**
- Se a similaridade for alta, retornamos a **resposta original** diretamente
- Isso elimina alucinações e reduz custo/latência

### Busca Híbrida

Combina **busca vetorial** (embeddings + similaridade cosseno) com **busca por palavras-chave** (BM25 via MongoDB text index) para maior precisão.

## Stack

- **Frontend:** Next.js 14, Tailwind CSS, TypeScript
- **Backend:** FastAPI, Motor (async MongoDB)
- **Banco:** MongoDB (embeddings + text index)
- **Auth:** Supabase (magic link + OAuth)
- **Embeddings:** OpenAI `text-embedding-3-large`
- **LLM:** OpenAI `gpt-4o-mini`

## Estrutura

```
kardechat/
├── frontend/          # Next.js app
│   └── src/
│       ├── app/       # Pages (landing + chat)
│       ├── components/# UI components
│       └── lib/       # Supabase + API clients
├── backend/           # FastAPI app
│   └── app/
│       ├── main.py    # App entrypoint
│       ├── chat.py    # Chat service + prompts
│       ├── search.py  # Hybrid search engine
│       ├── auth.py    # Supabase JWT auth
│       └── ...
├── scripts/           # Pipeline de ingestão (run once)
│   ├── run_pipeline.py
│   ├── download_books.py
│   ├── parse_le.py    # Parser Q/A do L.E.
│   ├── parse_books.py # Parser chunks dos demais livros
│   └── embed_and_store.py
└── docker-compose.yml
```

## Setup

### 1. Pré-requisitos

- Docker e Docker Compose
- Python 3.12+
- Node.js 20+
- Conta na [OpenAI](https://platform.openai.com/) (API key)
- Projeto no [Supabase](https://supabase.com/) (gratuito)

### 2. Configuração

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/kardechat.git
cd kardechat

# Configure as variáveis de ambiente
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
# Edite os arquivos com suas chaves
```

### 3. MongoDB

```bash
docker-compose up -d mongodb
```

### 4. Pipeline de Ingestão (uma vez)

```bash
cd scripts
pip install -r requirements.txt
python run_pipeline.py
```

Esse comando:
1. Baixa os 5 PDFs (domínio público, FEB)
2. Extrai pares Q/A do Livro dos Espíritos
3. Divide os demais livros em chunks
4. Gera embeddings e armazena no MongoDB

### 5. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API disponível em `http://localhost:8000`

### 6. Frontend

```bash
cd frontend
npm install
npm run dev
```

App disponível em `http://localhost:3000`

### Alternativa: Docker Compose completo

```bash
docker-compose up -d
```

## Configuração do Supabase

1. Crie um projeto em [supabase.com](https://supabase.com/)
2. Em **Authentication > Providers**, habilite:
   - Email (magic link)
   - Google (opcional)
3. Copie a **URL** e **anon key** para os `.env`

## API

### `POST /api/chat`

```json
{
  "question": "O que é a alma?",
  "extensive": false,
  "previous_answer": null
}
```

**Response:**

```json
{
  "answer": "Segundo o Livro dos Espíritos...",
  "citations": [
    {
      "book": "O Livro dos Espíritos",
      "reference": "Pergunta #134",
      "question": "Que é a alma?",
      "answer": "Um Espírito encarnado...",
      "score": 0.92
    }
  ],
  "strategy": "direct",
  "confidence": "high",
  "top_score": 0.92
}
```

## Licença

As obras de Allan Kardec são de domínio público. O código deste projeto é open source sob a licença MIT.
