# AI Assistant

This is AI assistant, which will explain how to deploy in preproduction using
AWS AI infra.

## Tech Stack

- Python
- Next.js
- openAI Sdk
- AWS (Bedrok, lambada and Api Gateway)

# Prerequisite

- Node/NPM
- UV
- Python
- Create AWS Free Tier Account
- Create OpenAI key, by paying with minimal $5 upfront

_**Note: Always use non-root aws account and monitor cost**_

## Getting Started

First Next.js project frontend project

```bash
npm create-next-app@latest --frontend --ts --app --no-src-dir
npm run dev
```

Second Create beckend python project

```bash 
uv init 
uv sync 
uv run uvicorn server_v2:app --reload
```
 