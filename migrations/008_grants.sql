-- Table-level GRANTs. RLS policies only decide *which rows* a role can
-- touch - Postgres still requires a base privilege grant before policies
-- are even evaluated. Supabase's dashboard/SQL-editor flow sets these up
-- implicitly for you; applying migrations over a direct psql connection
-- does not inherit that, so they're made explicit here.
grant select on public.tickers to anon, authenticated;
grant select, insert, update on public.tickers to service_role;

grant select, insert, update on public.profiles to authenticated;
grant all on public.profiles to service_role;

grant select, insert, update, delete on public.risk_profiles to authenticated;
grant all on public.risk_profiles to service_role;

grant select, insert on public.request_logs to authenticated;
grant insert on public.request_logs to anon;
grant all on public.request_logs to service_role;

grant select on public.cached_explanations to anon, authenticated;
grant insert, update on public.cached_explanations to authenticated;
grant all on public.cached_explanations to service_role;
