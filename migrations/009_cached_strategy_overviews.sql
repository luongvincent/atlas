-- Cached GET /strategy-overview output, shared across all users with the
-- same (risk_profile, investing_experience) combination - not user data,
-- the generated content is identical for anyone with that combination.
-- Only 3 risk_profile values x 4 investing_experience values = 12 possible
-- rows, ever - same "amortize the Groq cost across the whole user base"
-- design as cached_explanations, just keyed on quiz-answer category
-- instead of (ticker, quarter).
create table if not exists public.cached_strategy_overviews (
    id uuid primary key default gen_random_uuid(),
    risk_profile text not null
        check (risk_profile in ('conservative', 'moderate', 'aggressive')),
    investing_experience text not null
        check (investing_experience in ('none', 'beginner', 'intermediate', 'experienced')),
    sections jsonb not null,
    model text not null,
    generated_at timestamptz not null default now(),
    unique (risk_profile, investing_experience)
);

alter table public.cached_strategy_overviews enable row level security;

-- Public read: this is general education content, not tied to any one
-- user's identity once cached.
create policy "cached_strategy_overviews_select_all"
    on public.cached_strategy_overviews
    for select
    to anon, authenticated
    using (true);

-- Writes require a logged-in caller, same reasoning as
-- cached_explanations: reduces anonymous cache-poisoning surface, and
-- deliberately does NOT use the service role key - the backend writes
-- using the requesting user's own JWT.
create policy "cached_strategy_overviews_insert_authenticated"
    on public.cached_strategy_overviews
    for insert
    to authenticated
    with check (true);

grant select on public.cached_strategy_overviews to anon, authenticated;
grant insert on public.cached_strategy_overviews to authenticated;
grant all on public.cached_strategy_overviews to service_role;
