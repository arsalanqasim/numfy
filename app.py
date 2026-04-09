import streamlit as st
import requests
from bs4 import BeautifulSoup

# --- Scraper Engine ---
def fetch_sim_data(query):
    session = requests.Session()
    base_url = "https://paksiminfo.org/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }

    try:
        # 1. Get CSRF Token
        response = session.get(base_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Finding the token in the meta tag (per your previous output)
        csrf_tag = soup.find('meta', {'name': 'csrf-token'})
        csrf_token = csrf_tag['content'] if csrf_tag else None

        if not csrf_token:
            return "Error: Could not retrieve security token."

        # 2. Submit the Search
        payload = {
            'csrf_token': csrf_token,
            'query': query
        }
        
        post_response = session.post(base_url, data=payload, headers=headers)
        result_soup = BeautifulSoup(post_response.text, 'html.parser')
        
        # 3. Parse the Table
        table = result_soup.find('table', {'id': 'resultsTable'})
        if not table:
            return "No records found for this number."

        rows = table.find('tbody').find_all('tr')
        results = []
        for row in rows:
            cols = row.find_all('td')
            results.append({
                "Mobile": cols.text.strip(),
                "Name": cols.text.strip(),
                "CNIC": cols.text.strip(),
                "Address": cols.text.strip()
            })
        return results

    except Exception as e:
        return f"Connection Error: {str(e)}"

# --- Web Interface (Streamlit) ---
st.set_page_config(page_title="SIM Finder", page_icon="🔍")

st.title("🇵🇰 Pak SIM Info Lookup")
st.markdown("Enter a phone number or CNIC to retrieve registration details.")

target_input = st.text_input("Number/CNIC", placeholder="e.g. 03331390228")

if st.button("Search Details"):
    if target_input:
        with st.spinner('Accessing database...'):
            data = fetch_sim_data(target_input)
            
            if isinstance(data, list):
                st.success(f"Found {len(data)} record(s)")
                st.table(data)
            else:
                st.error(data)
    else:
        st.warning("Please enter a value first.")