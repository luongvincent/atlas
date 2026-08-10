-- Latest ingested call metadata per ticker, populated by the ingestion
-- pipeline (scripts/run_ingestion.py, admin/service-role only) after each
-- successful Pinecone upsert. Backs GET /tickers (latest call date) and
-- lets /explain resolve "the latest quarter" without querying Pinecone.
alter table public.tickers
    add column if not exists latest_quarter text,
    add column if not exists latest_call_date text;
