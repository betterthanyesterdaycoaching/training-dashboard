# AI Sports Dashboard

A Vercel + Supabase + Gemini dashboard for endurance training, nutrition, sleep, and coach chat.

## What is included
- Sidebar dashboard with overview, training, nutrition, sleep, and coach chat
- Vercel Python serverless API endpoints
- Supabase SQL schema and unified view
- Weekly GitHub Actions workflow starter

## Setup
1. Create a free Supabase project.
2. Open the SQL editor and run `schema.sql`.
3. Create a GitHub repo and upload these files.
4. Import the repo into Vercel.
5. Add these environment variables in Vercel:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `GEMINI_API_KEY`
6. Deploy.

## Accounts you need
- GitHub
- Vercel
- Supabase
- Google AI Studio

## Secrets
### Supabase
- In Supabase: Settings -> API
- Copy Project URL to `SUPABASE_URL`
- Copy anon public key to `SUPABASE_ANON_KEY`

### Gemini
- In Google AI Studio: Get API key
- Copy key to `GEMINI_API_KEY`

## Notes
- The dashboard charts read from `vw_daily_llm_context` via `/api/metrics`.
- The coach chat reads the last 14 days from the same view.
- Training type pie chart is placeholder demo data; replace later with a dedicated session summary endpoint if desired.
