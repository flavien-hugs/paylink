# PayLink — Plateforme de paiement Kkiapay multi-entités

> Une page de paiement Kkiapay, autant d'entités que vous voulez.

Monorepo d'une **page de paiement** (montant libre) intégrant l'agrégateur
**Kkiapay**, avec enregistrement local des transactions et un **back-office**
(suivi, réconciliation, statistiques, export). Chaque **entité** (école,
association, commerce…) est paramétrable (logo, nom, couleurs, description, clés
Kkiapay) et réutilise la même page de paiement via son `slug`.

## Architecture

```
payment/
├── backend/   FastAPI — architecture hexagonale, PostgreSQL
│   └── src/
│       ├── domain/         modèles & ports (Protocol) — aucun détail technique
│       ├── application/    use cases (orchestration métier)
│       ├── infrastructure/ adapters : postgres (SQLAlchemy async), kkiapay (httpx), security
│       └── interfaces/     API FastAPI + CLI (seed)
├── frontend/payment/       SvelteKit — page de paiement publique (/<slug>)
└── frontend/admin/         SvelteKit — back-office (login JWT, transactions, entités)
```

Les couches `domain → application → infrastructure/interfaces` respectent la
dépendance vers l'intérieur : le domaine ne connaît ni FastAPI, ni SQLAlchemy, ni
Kkiapay. Les implémentations concrètes sont injectées via les `Protocol` de
`domain/ports`.

## Flux de paiement

1. L'utilisateur ouvre `http://localhost:5173/<slug>` → la page charge le branding
   de l'entité (`GET /api/entities/<slug>`, **sans** les clés privées).
2. Il saisit un **montant libre** + ses coordonnées et valide.
3. Le front appelle `POST /api/payments/<slug>/initiate` → une transaction
   `PENDING` est créée, le front reçoit la `reference` + la clé publique Kkiapay.
4. Le widget Kkiapay s'ouvre ; au retour, le front appelle
   `POST /api/payments/<reference>/verify`. Le **backend vérifie côté serveur**
   le statut réel via l'API Kkiapay (clé privée) — la source de vérité.
5. Redirection vers `/<slug>/success` ou `/<slug>/failure`.
6. En parallèle, Kkiapay peut notifier `POST /api/webhooks/kkiapay` ; le statut est
   toujours re-vérifié côté serveur (le payload n'est jamais cru sur parole).

## Démarrage rapide (Docker)

```bash
cp .env.example .env
make fernet-key            # copier la valeur dans FERNET_KEY du .env
#  …renseigner aussi vos clés SEED_KKIAPAY_* (sandbox)
make up                    # build + démarre postgres, api, payment-web, admin-web
```

Au premier démarrage (`SEED_ON_START=true`), un admin et une entité de démo
(`sbbs`) sont créés.

| Service       | URL                              |
| ------------- | -------------------------------- |
| API + docs    | http://localhost:8000/docs       |
| Page paiement | http://localhost:5173/sbbs       |
| Admin         | http://localhost:4173 (login)    |

Identifiants admin par défaut : `admin@sbbs.local` / `admin1234`
(modifiables via `.env`).

## Ajouter / dupliquer une entité

Soit depuis l'admin (**Entités → Nouvelle entité**), soit en base. Une nouvelle
ligne `entities` suffit : la page de paiement est immédiatement disponible sur
`/<nouveau-slug>` avec son propre branding et ses propres clés Kkiapay. Aucun
redéploiement nécessaire.

## Développement

Backend :

```bash
cd backend
poetry install
poetry run alembic upgrade head
poetry run app seed
poetry run uvicorn src.main:app --reload
poetry run pytest
```

Frontends :

```bash
cd frontend/payment && npm install && npm run dev   # :5173
cd frontend/admin   && npm install && npm run dev   # :4173
```

## Variables d'environnement clés

| Variable          | Rôle                                                         |
| ----------------- | ----------------------------------------------------------- |
| `DATABASE_URL`    | DSN PostgreSQL async (`postgresql+asyncpg://…`)             |
| `JWT_SECRET`      | Signature des tokens admin                                  |
| `FERNET_KEY`      | Chiffrement des clés Kkiapay au repos                       |
| `PUBLIC_API_URL`  | URL de l'API vue par le navigateur (payment-web)           |
| `API_URL`         | URL serveur-à-serveur de l'API (admin-web)                  |
| `SEED_KKIAPAY_*`  | Clés Kkiapay de l'entité de démo                            |

> Les clés Kkiapay sont stockées **chiffrées** (Fernet) et ne sont jamais
> exposées par l'endpoint public `GET /api/entities/<slug>`.
