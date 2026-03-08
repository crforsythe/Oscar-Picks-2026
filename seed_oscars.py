import requests
from bs4 import BeautifulSoup
import toml
from supabase import create_client

# 1. Connect to Supabase
secrets = toml.load(".streamlit/secrets.toml")
url = secrets["supabase"]["url"]
key = secrets["supabase"]["key"] # Service role or anon key
supabase = create_client(url, key)

# 2. Scrape Wikipedia
wiki_url = "https://en.wikipedia.org/wiki/98th_Academy_Awards"
headers = {"User-Agent": "Mozilla/5.0"}
print("Fetching Wikipedia page...")
resp = requests.get(wiki_url, headers=headers)
soup = BeautifulSoup(resp.content, "html.parser")

# Find the main awards table which has the class 'wikitable defaulttop'
# Actually we can just find all <td> that have a <div> with <b> inside
tds = soup.find_all("td")

awards_data = {}

for td in tds:
    # Look for the category title
    div = td.find("div")
    if div and div.find("b"):
        category_name = div.find("b").text.strip()
        
        # Only grab standard Oscar categories
        if "Best" in category_name or "Achievement" in category_name:
            ul = td.find("ul")
            if ul:
                nominees = []
                for li in ul.find_all("li"):
                    text = li.text.strip()
                    # e.g., "Bugonia – Ed Guiney..."
                    # We might want to split by " – " or just save the whole text. 
                    # Let's try to split out the name and the movie context.
                    parts = text.split(" – ")
                    name = parts[0].strip()
                    movie = parts[1].strip() if len(parts) > 1 else ""
                    
                    nominees.append({"name": name, "movie": movie})
                
                awards_data[category_name] = nominees

print(f"Parsed {len(awards_data)} categories.")

# 3. Seed Supabase
print("Clearing existing categories and nominees...")
# Because of foreign keys, deleting categories cascades to nominees and picks.
try:
    # Delete all categories (this will wipe existing data)
    supabase.table("categories").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
except Exception as e:
    print(f"Error clearing table: {e}")

CATEGORY_POINTS = {
    "Best Picture": 10,
    "Best Directing": 8,
    "Best Actor in a Leading Role": 8,
    "Best Actress in a Leading Role": 8,
    "Best Actor in a Supporting Role": 8,
    "Best Actress in a Supporting Role": 8,
    "Best Writing (Original Screenplay)": 8,
    "Best Writing (Adapted Screenplay)": 8,
    "Best Animated Feature Film": 8,
    "Best International Feature Film": 6,
    "Best Documentary Feature Film": 4,
    "Best Documentary Short Film": 2,
    "Best Live Action Short Film": 2,
    "Best Animated Short Film": 2,
    "Best Music (Original Score)": 3,
    "Best Music (Original Song)": 1,
    "Best Sound": 1,
    "Best Production Design": 2,
    "Best Cinematography": 4,
    "Best Makeup and Hairstyling": 2,
    "Best Costume Design": 2,
    "Best Film Editing": 2,
    "Best Visual Effects": 2,
    "Best Casting": 2
}

print("Inserting new data...")
for category, noms in awards_data.items():
    # Insert category
    point_value = CATEGORY_POINTS.get(category, 2)
    try:
        cat_res = supabase.table("categories").insert({"name": category, "point_value": point_value}).execute()
        if cat_res.data:
            cat_id = cat_res.data[0]["id"]
            
            # Insert nominees
            noms_to_insert = []
            for n in noms:
                noms_to_insert.append({
                    "category_id": cat_id,
                    "name": n["name"],
                    "movie": n["movie"]
                })
            supabase.table("nominees").insert(noms_to_insert).execute()
        print(f"Added {category} with {len(noms)} nominees.")
    except Exception as e:
        print(f"Error inserting {category}: {e}")

print("Done seeding database!")
