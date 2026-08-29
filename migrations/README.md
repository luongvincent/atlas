# Migrations

Plain SQL, applied in filename order. Run them against your Supabase
project via the SQL Editor in the dashboard, or the Supabase CLI:

```
supabase db execute --file migrations/001_extensions.sql
supabase db execute --file migrations/002_tickers.sql
supabase db execute --file migrations/003_profiles.sql
supabase db execute --file migrations/004_risk_profiles.sql
supabase db execute --file migrations/005_request_logs.sql
supabase db execute --file migrations/006_cached_explanations.sql
supabase db execute --file migrations/007_tickers_latest_call.sql
supabase db execute --file migrations/008_grants.sql
supabase db execute --file migrations/009_cached_strategy_overviews.sql
supabase db execute --file migrations/010_cached_strategy_overviews_update_grant.sql
```

After running them, seed the `tickers` reference table from
`config/tickers.py`:

```
python scripts/seed_tickers.py
```

## Tables

| Table                 | Holds                                   | RLS ownership key       |
|------------------------|------------------------------------------|--------------------------|
| `tickers`              | reference data (mirrors `config/tickers.py`) | none - public read, admin-only write |
| `profiles`              | 1 row per Supabase Auth user             | `id = auth.uid()`        |
| `risk_profiles`         | onboarding preferences results                  | `user_id = auth.uid()`   |
| `request_logs`          | per-request latency/status audit trail   | `user_id = auth.uid()` (or `null` for anonymous, write-only) |
| `cached_explanations`   | shared `/explain` cache, keyed on (ticker, quarter) | none - public read, authenticated write |
| `cached_strategy_overviews` | shared `/strategy-overview` cache, keyed on (risk_profile, investing_experience) | none - public read, authenticated write |

Every table has RLS enabled. `tickers` and `cached_explanations` don't hold
per-user data, so their policies aren't ownership-scoped, but RLS is still
on and writes are still restricted (admin-only / authenticated-only
respectively) - see the security notes in the top-level README for the
reasoning, especially around why `cached_explanations` intentionally never
uses the service role key.
