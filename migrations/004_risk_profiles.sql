-- Results of the 5-question onboarding preferences (POST /onboarding), one row
-- per user. risk_profile is the derived label the app adapts /explain
-- output to.
create table if not exists public.risk_profiles (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null unique references auth.users (id) on delete cascade,
    investing_experience text not null
        check (investing_experience in ('none', 'beginner', 'intermediate', 'experienced')),
    time_horizon text not null
        check (time_horizon in ('short_term', 'medium_term', 'long_term')),
    risk_comfort smallint not null
        check (risk_comfort between 1 and 5),
    portfolio_size_range text not null
        check (portfolio_size_range in ('under_1k', '1k_10k', '10k_100k', '100k_1m', 'over_1m')),
    goals text not null
        check (goals in ('preserve_capital', 'income', 'growth', 'speculation')),
    risk_profile text not null
        check (risk_profile in ('conservative', 'moderate', 'aggressive')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

alter table public.risk_profiles enable row level security;

create policy "risk_profiles_select_own"
    on public.risk_profiles
    for select
    to authenticated
    using (auth.uid() = user_id);

create policy "risk_profiles_insert_own"
    on public.risk_profiles
    for insert
    to authenticated
    with check (auth.uid() = user_id);

create policy "risk_profiles_update_own"
    on public.risk_profiles
    for update
    to authenticated
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);

create policy "risk_profiles_delete_own"
    on public.risk_profiles
    for delete
    to authenticated
    using (auth.uid() = user_id);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists risk_profiles_set_updated_at on public.risk_profiles;
create trigger risk_profiles_set_updated_at
    before update on public.risk_profiles
    for each row
    execute function public.set_updated_at();
