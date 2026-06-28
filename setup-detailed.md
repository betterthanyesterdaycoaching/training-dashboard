# Setup Guide — AI Sports Dashboard

Complete step-by-step instructions to deploy your Supabase + Vercel + Gemini endurance coaching dashboard.

---

## Accounts you need

- [GitHub](https://github.com) — stores your code
- [Supabase](https://supabase.com) — your free PostgreSQL database
- [Vercel](https://vercel.com) — hosts your dashboard and serverless API
- [Google AI Studio](https://aistudio.google.com) — provides your free Gemini API key

---

## Step 1: Create your Supabase account and project

1. Go to [supabase.com](https://supabase.com) and click **Start your project**.
2. Sign up using your GitHub account (easiest — you will need GitHub later anyway).
3. Once logged in, click the green **New project** button.
4. Fill in the details:
   - **Organisation:** your default personal org is fine
   - **Project name:** `ai-sports-dashboard`
   - **Database password:** create a strong password and save it somewhere safe
   - **Region:** `Southeast Asia (Singapore)` — closest free region to Brisbane
5. Click **Create new project** and wait 1–2 minutes for it to provision.

---

## Step 2: Run the schema in Supabase

You do not link `schema.sql` directly from GitHub to Supabase. Instead, copy and paste its contents into the Supabase SQL editor.

1. Open `schema.sql` from this repo in any text editor (Notepad, TextEdit, or VS Code).
2. Select all the text (`Ctrl+A` on Windows, `Cmd+A` on Mac) and copy it.
3. Go back to your Supabase project dashboard.
4. In the left sidebar, click the **SQL Editor** icon — it looks like `>_`. Click it.
5. Click **New query** (top left of the editor).
6. Click inside the empty editor area and paste (`Ctrl+V` / `Cmd+V`) the entire schema.
7. Click the green **Run** button (bottom right, or press `Ctrl+Enter`).
8. You should see a green success message. Your 5 tables and unified view are now created.

### Tables created
| Table | Source |
|---|---|
| `daily_biometrics` | Oura (sleep, HRV, readiness) + Withings (weight) |
| `daily_nutrition` | MyFitnessPal (calories, macros, water) |
| `workouts` | TrainingPeaks (TSS, power, duration, HR) |
| `athlete_goals` | Manual entry (race date, FTP, weight targets) |
| `ai_insights` | AI-generated weekly recommendations |

The schema also creates a unified view `vw_daily_llm_context` that joins all tables into a single daily row used by both the dashboard charts and the Gemini coach chat.

---

## Step 3: Get your Supabase secrets

1. In the Supabase left sidebar, click the **Settings** icon (gear wheel at the very bottom).
2. Click **API** in the settings menu.
3. Copy the following two values into a notepad:
   - **Project URL** — looks like `https://abcdefghij.supabase.co` → save as `SUPABASE_URL`
   - **anon public** key under "Project API Keys" — a long string starting with `eyJ...` → save as `SUPABASE_ANON_KEY`

---

## Step 4: Get your Gemini API key

1. Go to [aistudio.google.com](https://aistudio.google.com) and sign in with a Google account.
2. In the left sidebar, click **Get API key**.
3. Click **Create API key**.
4. If prompted to select a project, click **Create API key in new project**.
5. Copy the generated key into your notepad → save as `GEMINI_API_KEY`.

> **Privacy note:** On the free tier, Google may use API inputs to improve their models.
> The dashboard only sends biometric numbers and workout stats — no names, emails, or GPS data.

---

## Step 5: Put the project files on GitHub

1. Go to [github.com](https://github.com) and sign in (or create a free account).
2. Click the **+** icon (top right) → **New repository**.
3. Name it `ai-sports-dashboard`, set it to **Private**, and click **Create repository**.
4. On the next screen, click the link that says **uploading an existing file**.
5. Unzip the project folder on your computer. You will see:
   ```
   public/
   api/
   .github/
   schema.sql
   vercel.json
   README.md
   setup-detailed.md   ← this file
   ```
6. Drag all of those files and folders into the GitHub upload window in your browser.
7. Scroll down and click **Commit changes**.

---

## Step 6: Deploy on Vercel

1. Go to [vercel.com](https://vercel.com) and click **Sign Up** → **Continue with GitHub**.
2. After signing in, click **Add New** → **Project**.
3. Find your `ai-sports-dashboard` repository and click **Import**.
4. On the configuration screen, leave everything as default. Scroll down to **Environment Variables** and add these three:

| Variable name | Value |
|---|---|
| `SUPABASE_URL` | Your Supabase Project URL from Step 3 |
| `SUPABASE_ANON_KEY` | Your Supabase anon public key from Step 3 |
| `GEMINI_API_KEY` | Your Gemini key from Step 4 |

5. Click **Add** after each one.
6. Click the **Deploy** button.
7. Wait approximately 60 seconds. Vercel will give you a live HTTPS URL like `ai-sports-dashboard.vercel.app`.

---

## Step 7: Test your dashboard

1. Click the Vercel live URL to open your dashboard.
2. Metric cards will show `-` until real data is in Supabase — that is expected.
3. Click **Coach chat** in the sidebar and type: `Hello, are you connected?`
4. If Gemini responds, your entire backend is wired up correctly.

---

## Step 8: Add your first data row

To confirm charts work, go to Supabase → SQL Editor → New query, paste the following, and click Run:

```sql
INSERT INTO daily_biometrics (date, weight_kg, sleep_score, readiness_score, hrv_ms, resting_hr, sleep_duration_hours)
VALUES (CURRENT_DATE, 72.5, 84, 80, 62.0, 48, 7.8);

INSERT INTO daily_nutrition (date, calories_in, protein_g, carbs_g, fat_g, water_ml)
VALUES (CURRENT_DATE, 2850, 158, 320, 72, 2800);
```

Refresh your dashboard URL. The metrics cards and charts should now show real values.

---

## Step 9: Automate daily data ingestion

Your data sources and their recommended sync paths are:

| Data source | App | Sync path |
|---|---|---|
| MyFitnessPal (nutrition) | Apple Health bridge | Health Auto Export → Google Drive → Make.com → Supabase |
| Oura (sleep, HRV, readiness) | Oura API | Make.com HTTP module → Supabase |
| Withings (weight) | Withings API | Make.com HTTP module → Supabase |
| TrainingPeaks (workouts, TSS) | FitnessSyncer | FitnessSyncer → Google Drive CSV → Make.com → Supabase |

Set up a free Make.com account at [make.com](https://make.com) and create a scenario that:
1. Triggers on a daily schedule (e.g., every night at 10 PM).
2. Reads the latest exported CSV or API response from each source.
3. Uses the Supabase HTTP module to `POST` the row via the Supabase REST API.

---

## Step 10: Updating the dashboard

Whenever you push new code to GitHub, Vercel automatically redeploys your dashboard within 30–60 seconds. No manual steps required.

To add new database columns or views in the future, go to Supabase → SQL Editor → New query, run your `ALTER TABLE` or `CREATE VIEW` statements, then update the corresponding JavaScript in `public/index.html` to read the new fields.

---

## Environment variables reference

| Variable | Where to get it | Used by |
|---|---|---|
| `SUPABASE_URL` | Supabase → Settings → API → Project URL | `api/metrics.py`, `api/chat.py` |
| `SUPABASE_ANON_KEY` | Supabase → Settings → API → anon public key | `api/metrics.py`, `api/chat.py` |
| `GEMINI_API_KEY` | Google AI Studio → Get API key | `api/chat.py` |

---
## Auth: Clerk (Free — Best Option for Personal Use)

Clerk is a free authentication service that works perfectly with Vercel. It adds a proper login screen with email/password or Google login. The free tier supports up to 10,000 monthly active users — more than enough for personal use.

Step 1: Create a Clerk account
Go to clerk.com and sign up for free

Click Create application

Name it ai-sports-dashboard

Choose sign-in methods — select Email and/or Google

Click Create application

Step 2: Get your Clerk keys
In the Clerk dashboard, click API Keys

Copy the Publishable key (starts with pk_live_...) — save to notepad as CLERK_PUBLISHABLE_KEY

Step 3: Add Clerk to your HTML
Open public/index.html in GitHub (pencil icon to edit) and add these two things:

In the <head> section, add the Clerk script tag directly after the Plotly script line:

xml
<script
  async
  crossorigin="anonymous"
  data-clerk-publishable-key="YOUR_PUBLISHABLE_KEY_HERE"
  src="https://YOUR_FRONTEND_API.clerk.accounts.dev/npm/@clerk/clerk-js@latest/dist/clerk.browser.js"
  type="text/javascript"
></script>
Replace YOUR_PUBLISHABLE_KEY_HERE with your actual key from Step 2. Clerk's dashboard shows the exact full script tag to copy — use that.

Replace the opening <body> tag with this auth gate:

xml
<body>
<div id="auth-gate" style="display:flex;align-items:center;justify-content:center;height:100vh;background:#0f172a;">
  <div id="sign-in"></div>
</div>
<div id="app-content" class="app" style="display:none;">
  <!-- All your existing sidebar and content goes here, unchanged -->
At the bottom of your <script> block, add the auth initialisation before loadMetrics():

javascript
window.addEventListener('load', async function() {
  await Clerk.load();
  if (Clerk.user) {
    document.getElementById('auth-gate').style.display = 'none';
    document.getElementById('app-content').style.display = 'grid';
    loadMetrics();
  } else {
    Clerk.mountSignIn(document.getElementById('sign-in'));
    Clerk.addListener(({ user }) => {
      if (user) {
        document.getElementById('auth-gate').style.display = 'none';
        document.getElementById('app-content').style.display = 'grid';
        loadMetrics();
      }
    });
  }
});
Remove the standalone loadMetrics(); call that currently sits at the bottom of your script.

Step 4: Add the sign-out button
Inside the sidebar <aside> block at the bottom, add:

xml
<button class="nav-btn" onclick="Clerk.signOut()" style="margin-top:auto;color:#f87171;">Sign out</button>
Step 5: Add environment variable to Vercel
Vercel → your project → Settings → Environment Variables

Add CLERK_PUBLISHABLE_KEY with your key value

Redeploy

Option 3: Supabase Auth (Free — Most Integrated)
Since you already have Supabase, you can use its built-in authentication. This is the most tightly integrated option because the same database handles both your data and your login.

How it works
In Supabase → Authentication → Providers → enable Email

In Supabase → Authentication → Users → click Invite user → enter your email

You receive a magic link email — click it to set your password

Add Supabase Auth JS to your index.html to check for a valid session before showing the dashboard

The trade-off is that Supabase Auth requires slightly more JavaScript code to implement versus Clerk's simpler drop-in approach.
---

## Troubleshooting

**Charts show `-` after deploying**
Run the test INSERT in Step 8 to add sample data. Charts only display if rows exist in `daily_biometrics`.

**Coach chat returns "Gemini API key missing"**
Go to Vercel → your project → Settings → Environment Variables and check that `GEMINI_API_KEY` is saved correctly with no extra spaces.

**Coach chat returns "Supabase error"**
Check that `SUPABASE_URL` ends with `.supabase.co` (no trailing slash) and that `SUPABASE_ANON_KEY` is the `anon` key, not the `service_role` key.

**Vercel deployment failed**
Check that `vercel.json` is in the root of the repository (not inside a subfolder). Re-upload if needed.
