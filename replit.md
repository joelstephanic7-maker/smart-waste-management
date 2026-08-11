# VisionX Smart Waste Management

AI-powered waste classification platform where users upload waste images, get smart disposal recommendations, and track their environmental impact.

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the API server (port 8080)
- `pnpm --filter @workspace/visionx run dev` — run the frontend (dynamic port)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string, `SESSION_SECRET` — JWT signing secret

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- Frontend: React + Vite, Wouter (routing), TanStack Query, Recharts, Tailwind CSS
- API: Express 5 + JWT authentication (bcryptjs, jsonwebtoken)
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

- `lib/api-spec/openapi.yaml` — OpenAPI contract (source of truth)
- `lib/db/src/schema/` — Drizzle table definitions (users, waste-uploads, classification-results, feedback)
- `artifacts/api-server/src/routes/` — Express route handlers (auth, uploads, classifications, feedback, dashboard, admin)
- `artifacts/api-server/src/lib/auth.ts` — JWT middleware (requireAuth, requireAdmin, requireOfficer)
- `artifacts/api-server/src/lib/classify.ts` — AI waste classification engine (keyword-based + random fallback)
- `artifacts/visionx/src/` — React frontend (pages, contexts, components)
- `artifacts/visionx/src/contexts/AuthContext.tsx` — JWT auth context with token persistence
- `artifacts/admin-panel/src/` — Officer Panel React frontend (login, dashboard, scanner, history, analytics)
- `artifacts/api-server/src/routes/officer.ts` — Officer API routes (/officer/dashboard, /citizen/:id, /collections, /analytics)

## Architecture decisions

- JWT stored in localStorage; injected via `setAuthTokenGetter` from `@workspace/api-client-react` into all API calls
- AI classification is keyword-based (production would swap in a real vision model call)
- All raw SQL in backend uses `db.execute()` with template literals for aggregate queries (Drizzle doesn't support complex GROUP BY via ORM)
- Admin routes gated by `requireAdmin` middleware (checks role === 'admin')
- Officer routes gated by `requireOfficer` middleware (allows role 'officer' OR 'admin')
- Officer panel uses direct fetch calls (not generated hooks) — token stored in `officer_token` localStorage key
- Points calculation: Bio Waste = 5 pts/kg, Non-Bio Waste = 10 pts/kg
- Waste categories: Biodegradable, Non-Biodegradable, Recyclable, Hazardous, Electronic

## Product

- **User module:** Register/login → upload waste image → get AI classification with disposal tips → view history, profile, feedback
- **Admin module:** Secure admin dashboard with user management, classification reports, analytics charts, feedback management
- **Landing page:** Public marketing page with hero, features, how-it-works, about, CTA sections
- **Officer Panel** (`/admin-panel/`): Login → Dashboard (stats + recent) → Scan & Collect (citizenId lookup + waste form) → Collection History (search/filter/paginate) → Analytics (charts)

## Demo credentials

| Role  | Email                | Password   |
|-------|----------------------|------------|
| Admin   | admin@visionx.com       | (placeholder hash — register via UI for real password) |
| User    | john@example.com        | (same) |
| Officer | officer2@visionx.com    | officer123 |

> **Note:** Seeded admin/user password hashes are placeholders — register new users via the UI. The officer account was created via the register API and has a working password.

## User preferences

- Green sustainability theme
- JWT authentication (explicit user requirement)

## Gotchas

- Always run `pnpm --filter @workspace/api-spec run codegen` after editing `lib/api-spec/openapi.yaml`
- Always run `pnpm run typecheck:libs` after changing any `lib/*` package before leaf artifact typechecks
- `setAuthTokenGetter` must be imported from `@workspace/api-client-react` (not the deep `/src/custom-fetch` path)
- Seed passwords: The seeded `password_hash` values are placeholder hashes — register new users through the UI to get proper bcrypt hashes

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
