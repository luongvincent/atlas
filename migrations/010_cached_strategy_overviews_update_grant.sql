-- Follow-up to 009: the upsert in api/routes/strategy.py's _store_cache
-- can resolve to an UPDATE (when a row for that risk_profile +
-- investing_experience combo already exists), which needs both an UPDATE
-- RLS policy and an UPDATE grant - 009 only added INSERT. Caught live via
-- "permission denied for table cached_strategy_overviews" (Postgres error
-- code 42501) when testing the second call for the same combination.
-- cached_explanations (migration 006) already has both policies; this
-- table should have matched it from the start.
create policy "cached_strategy_overviews_update_authenticated"
    on public.cached_strategy_overviews
    for update
    to authenticated
    using (true)
    with check (true);

grant update on public.cached_strategy_overviews to authenticated;
