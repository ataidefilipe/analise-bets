This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

Documentação do que foi construído (arquitetura, decisões e progresso por
passo): [`docs/README.md`](./docs/README.md).

## Rodando com a API

Este front vive em `frontend/` do monólito e consome a API em `src/api/`, na
raiz. Com ela no ar em `http://localhost:8000` (ver `docs/backend.md` na raiz):

```bash
cp .env.example .env.local
pnpm install
pnpm dev
```

Entre em `http://localhost:3000` com uma chave de API. As chaves de
demonstração ficam em `data/restrito/chaves_api_poc.json`, na raiz. Detalhes em [`docs/passo-11-integracao-api.md`](./docs/passo-11-integracao-api.md).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
