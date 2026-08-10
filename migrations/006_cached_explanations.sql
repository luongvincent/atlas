-- Cached /explain output, shared across all users for a given
-- (ticker, quarter). Not user data: the LLM-generated content is
-- identical regardless of who requests it. Risk-profile tone/depth
-- adaptation is applied on top of this cached base at serve time, so we
-- don't need one cached row per profile tier.
create table if not exists public.cached_explanations (
    id uuid primary key default gen_random_uuid(),
    ticker text not null references public.tickers (ticker),
    quarter text not null,
    sections jsonb not null,
    citations jsonb not null,
    model text not null,
    generated_at timestamptz not null default now(),
    unique (ticker, quarter)
);

alter table public.cached_explanations enable row level security;

-- Public read: anyone can read a cached explanation once generated.
create policy "cached_explanations_select_all"
    on public.cached_explanations
    for select
    to anon, authenticated
    using (true);

-- Writes require a logged-in caller (reduces anonymous cache-poisoning
-- surface) but deliberately do NOT use the service role key - the backend
-- writes using the requesting user's own JWT. ticker/quarter are
-- constrained by the FK/NOT NULL above; sections/citations shape is
-- validated at the application layer (Pydantic) before insert.
create policy "cached_explanations_insert_authenticated"
    on public.cached_explanations
    for insert
    to authenticated
    with check (true);

create policy "cached_explanations_update_authenticated"
    on public.cached_explanations
    for update
    to authenticated
    using (true)
    with check (true);
