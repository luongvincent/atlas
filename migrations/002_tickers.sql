-- Reference table mirroring config/tickers.py. Not user data - gives
-- request_logs / cached_explanations a foreign key to validate against
-- instead of trusting a free-text ticker column. Populated by an admin
-- script using the service role key (never by client requests).
create table if not exists public.tickers (
    ticker text primary key,
    company_name text not null,
    avg_daily_volume bigint not null,
    exchange text not null,
    updated_at timestamptz not null default now()
);

alter table public.tickers enable row level security;

-- Public reference data: anyone (including anonymous callers) can read it.
create policy "tickers_select_all"
    on public.tickers
    for select
    to anon, authenticated
    using (true);

-- No insert/update/delete policies for anon/authenticated: this table is
-- only ever written by an admin script using the service role key, which
-- bypasses RLS by design and does not need a policy.
