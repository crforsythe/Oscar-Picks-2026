import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://en.wikipedia.org/wiki/98th_Academy_Awards"
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    print("Successly fetched page.")
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Let's find the Nominees table
    # Usually it's under an h2/h3 like "Awards", "Winners and nominees"
    # It contains a table with wikitable class where each td has a ul of nominees.
    
    tables = soup.find_all("table", class_="wikitable")
    
    print(f"Found {len(tables)} wikitables.")
    for i, table in enumerate(tables):
        # Let's print the headers of the first few tables to identify the correct one
        headers = [th.text.strip() for th in table.find_all("th")]
        print(f"Table {i} headers: {headers[:5]}")
        
    print("-------------------------------------------------")
    # Using pandas as well
    try:
        dfs = pd.read_html(response.content)
        for i, df in enumerate(dfs):
            if any('Best Picture' in col for col in df.columns) or any('Best Picture' in str(df.iloc[0].values) for col in df.columns if not df.empty):
                print(f"\nPandas Table {i} looks like nominees:")
                print(df.head(3))
    except Exception as e:
        print(f"Pandas parsing error: {e}")
        
else:
    print(f"Failed to fetch page. Status code: {response.status_code}")
