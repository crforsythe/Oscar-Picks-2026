import toml
from supabase import create_client

with open(".streamlit/secrets.toml", "r") as f:
    secrets = toml.load(f)

supabase_url = secrets["supabase"]["url"]
supabase_key = secrets["supabase"]["key"]

supabase = create_client(supabase_url, supabase_key)

res = supabase.table("nominees").select("*").in_("name", ["Two People Exchanging Saliva", "The Singers"]).execute()
for r in res.data:
    print(f"Name: {r['name']}, Category: {r['category_id']}, ID: {r['id']}")
