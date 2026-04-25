import pandas as pd

df = pd.read_excel("dataset/EOD.xlsx")

df['Date'] = pd.to_datetime(df['Trade Date'])


frame = df.sort_values('Trade Date')

frame = frame.dropna()

frame['Avkastning OMXS#='] = frame['Index Value'].pct_change()

frame = frame.drop(columns=["Trade Date"])

for col in ['Index Value', 'Net Change', 'High', 'Low']:
    frame[col] = pd.to_numeric(frame[col]).round(2)

print(frame.head)

# print(frame[['Date', 'Index Value', 'Avkastning OMXS#=']].head)
frame.to_csv('dataset/history.csv',  index=False)