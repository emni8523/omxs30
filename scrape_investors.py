import requests
from datetime import date
import pandas as pd
import os

BOLAG_FILER = {
    "INVE B": "dataset/investor.csv",
    "INDU C": "dataset/industri.csv",
    "LATO B": "dataset/latour.csv",
}

KOLUMNER = ["DATUM", "BOLAG", "PRIS", "SUBSTANSVÄRDE", "BERÄKNAT_SUBSTANSVÄRDE"]


URL = "https://ibindex.se/ibi//index/getProducts.req" 

def getValues():
    headers = {"Accept": "application/json"}
    response = requests.get(URL, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    idag = date.today().isoformat()  

    resultat = {}

    for bolag in data:
        ticker = bolag.get("product")
        if ticker in BOLAG_FILER:
            resultat[ticker] = {
                "DATUM": idag,
                "PRIS": bolag.get("price"),
                "SUBSTANSVÄRDE": bolag.get("netAssetValue"),
                "BERÄKNAT_SUBSTANSVÄRDE": bolag.get("netAssetValueCalculated"),
            }
    return resultat


def addToSet(row, path):
    if not os.path.exists(path):
        pd.DataFrame(columns=KOLUMNER).to_csv(path, index=False)

    df = pd.read_csv(path)

    if df.empty:
        senaste_datum = None
    else:
        senaste_datum = pd.to_datetime(df.iloc[-1]["DATUM"]).date()

    nytt_datum = pd.to_datetime(row["DATUM"]).date()

    if senaste_datum is None or nytt_datum > senaste_datum:
        ny_df = pd.DataFrame([row])
        ny_df['DISCOUNT/PREMIUM'] = (ny_df['BERÄKNAT_SUBSTANSVÄRDE'] - ny_df['PRIS']) / ny_df['PRIS']
        df = pd.concat([df, ny_df], ignore_index=True)
        df.to_csv(path, index=False)
        print("Added to file")

    else:
        print(f" No new data last seen {senaste_datum}, today: {nytt_datum})")


if __name__ == "__main__":
    resultat = getValues()

    for ticker, path in BOLAG_FILER.items():
        if ticker in resultat:
            addToSet(resultat[ticker], path)
        else:
            print(f"{ticker} not found in API")
    

