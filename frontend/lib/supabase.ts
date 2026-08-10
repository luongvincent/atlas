import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "";

// Browser-only client, using the public anon key (safe to expose - it's
// what RLS is for). Never put the service role key here.
export const supabase = createClient(supabaseUrl, supabaseAnonKey);
