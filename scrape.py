import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome()
driver.get("https://indexes.nasdaqomx.com/Index/History/OMXS30")
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "#historyTable tbody tr td:not(.dataTables_empty)"))
)
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

df = pd.read_csv("dataset/history.csv")

latest_date = pd.to_datetime(df.iloc[-1]["Date"])

table = soup.find('table', id='historyTable')  

new_rows = []

print(f"Table {table}")
if table:
    rows = table.find('tbody').find_all('tr')
    print(f'Rows {rows}')
    for row in rows:
        cols = row.find_all('td')

        print(f'cols {cols}')
        if len(cols) < 5:
            continue

        trade_date = pd.to_datetime(cols[0].get_text(strip=True))
        print(trade_date)
        if trade_date > latest_date:
            new_row = {
                "Index Value": cols[1].get_text(strip=True),
                "Net Change":  cols[2].get_text(strip=True),
                "High":        cols[3].get_text(strip=True),
                "Low":         cols[4].get_text(strip=True),
                "Date":        cols[0].get_text(strip=True),
            }
            new_rows.append(new_row)



if new_rows:
    new_df = pd.DataFrame(new_rows)
    for col in ['Index Value', 'Net Change', 'High', 'Low']:
        new_df[col] = new_df[col].astype(str).str.replace(',', '').str.strip()
        new_df[col] = pd.to_numeric(new_df[col], errors='coerce')

    # Strip timestamp from date, keep only YYYY-MM-DD
    new_df['Date'] = pd.to_datetime(new_df['Date']).dt.date


    df['Index Value'] = pd.to_numeric(
        df['Index Value'].astype(str).str.replace(',', '').str.strip(), errors='coerce'
    )
    df = pd.concat([df, new_df], ignore_index=True)
    df['Avkastning OMXS#='] = df['Index Value'].pct_change()
    df.to_csv("dataset/history.csv", index=False)
    print(f"Added {len(new_rows)} new row(s).")
else:
    print("No new data found.")
