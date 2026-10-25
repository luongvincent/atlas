-- "Please explain this stock" requests for tickers outside the supported
-- top 15 (POST /explanation-requests). The operator reads these with the
-- service role (offline) to decide which transcripts to ingest next.
-- One row per (user, ticker): repeat clicks are a no-op, not spam.
create table if not exists public.explanation_requests (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    ticker text not null
        check (ticker ~ '^[A-Z]{1,5}(-[A-Z])?$'),
    created_at timestamptz not null default now(),
    unique (user_id, ticker)
);

alter table public.explanation_requests enable row level security;

create policy "explanation_requests_select_own"
    on public.explanation_requests
    for select
    to authenticated
    using (auth.uid() = user_id);

create policy "explanation_requests_insert_own"
    on public.explanation_requests
    for insert
    to authenticated
    with check (auth.uid() = user_id);

create policy "explanation_requests_delete_own"
    on public.explanation_requests
    for delete
    to authenticated
    using (auth.uid() = user_id);

-- Explicit grants - see 008_grants.sql for why they aren't implicit here.
grant select, insert, delete on public.explanation_requests to authenticated;
grant all on public.explanation_requests to service_role;
