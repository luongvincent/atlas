-- Which prompt/schema version produced a cached explanation. /explain only
-- serves rows whose prompt_version matches core.explainer_chain.PROMPT_VERSION,
-- so bumping it there regenerates stale rows. Existing rows stay null (= miss).
-- Table-level grants and RLS policies already cover the new column.
alter table public.cached_explanations
    add column if not exists prompt_version text;
