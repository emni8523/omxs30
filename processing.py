import pandas as pd

START_DATE = "2021-02-19"

files = ["industri.csv", "latour.csv", "investor.csv"]


def main():
    for f in files: 
        df = pd.read_csv("dataset/" + f)
        df = df[df['DATUM'] > START_DATE]
        df['DISCOUNT/PREMIUM'] = (df['BERÄKNAT_SUBSTANSVÄRDE'] - df['PRIS']) / df['PRIS']
        df.drop(columns="BOLAG", inplace=True)
        df.to_csv("dataset/" + f, index=False)




if __name__ == "__main__":
    main()
