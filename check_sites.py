import csv
import requests
import concurrent.futures
from operator import itemgetter

CSV_FILE = 'pastebin.csv'
README_FILE = 'README.md'
TIMEOUT_SECONDS = 10
MAX_WORKERS = 20

# essential to find where table should be
START_MARKER = "‎"
END_MARKER = "‎‎"

def check_url(row):
    """Checks a single URL. Returns the modified row."""
    url = row['URL']
    is_down=row['Is Down?']
    
    if is_down.strip().lower() == 'yes':
        return row

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (GitHub Action; Pastebin Monitor)'}
        response = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
        
        # 403 could be good, cause some sites block cloud ips.
        if response.status_code == 404:
            print(f"[-] {url} returned 404.")
            is_down = 'Yes'
        elif response.status_code >= 500:
            print(f"[-] {url} server error {response.status_code}.")
            is_down = 'Yes'
        else:
            print(f"[+] {url} is working ({response.status_code})")
            
    except requests.RequestException as e:
        print(f"[!] {url} connection failed: {e}.")
        is_down = 'Yes'

    return row

def generate_markdown(rows):
    """Generates the Markdown table string."""
    working = []
    others = []

    for row in rows:
        if row['Is Down?'] == 'No' and row['Read Only'] == 'No':
            working.append(row)
        else:
            others.append(row)

    # working sites alphabetical, then others
    working.sort(key=itemgetter('URL'))    
    final_rows = working + others
    
    md = "| URL | Aliases | Read Only | Is Down? |\n"
    md += "| :--- | :--- | :--- | :--- |\n"
    
    for row in final_rows:
        md += f"| {row['URL']} | {row['Aliases']} | {row['Read Only']} | {row['Is Down?']} |\n"
    
    return md

def main():
    rows = []
    
    with open(CSV_FILE, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f"Checking {len(rows)} sites...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(check_url, rows))

    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print("CSV updated.")

    new_table = generate_markdown(results)
    
    with open(README_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace content between markers
    if START_MARKER in content and END_MARKER in content:
        before = content.split(START_MARKER)[0]
        after = content.split(END_MARKER)[1]
        new_content = f"{before}{START_MARKER}\n{new_table}\n{END_MARKER}{after}"
        
        with open(README_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("README updated.")
    else:
        print("WARNING: Markers not found in README.md. Table not updated.")

if __name__ == "__main__":
    main()