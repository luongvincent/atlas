-- Structured log of API requests, used for latency tracking and per-user
-- rate limit / abuse auditing. Written by the backend using the caller's
-- own JWT (anon or authenticated) - never the service role key - so RLS
-- enforces that a request can only ever log itself.
create table if not exists public.request_logs (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references auth.users (id) on delete cascade,
    endpoint text not null,
    ticker text references public.tickers (ticker),
    status_code smallint not null,
    latency_ms integer not null,
    created_at timestamptz not null default now()
);

alter table public.request_logs enable row level security;

create policy "request_logs_select_own"
    on public.request_logs
    for select
    to authenticated
    using (auth.uid() = user_id);

create policy "request_logs_insert_own_authenticated"
    on public.request_logs
    for insert
    to authenticated
    with check (auth.uid() = user_id);

-- Unauthenticated requests may still log (for latency/rate-limit visibility)
-- but only with user_id null - they can never be attributed to, or read
-- back as, a specific user via this policy (no anon select policy exists).
create policy "request_logs_insert_anonymous"
    on public.request_logs
    for insert
    to anon
    with check (user_id is null);
