import pandas as pd
import scripts

df = pd.read_csv("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rate-archives/par-yield-curve-rates-1990-2022.csv",
                  index_col="Date", parse_dates=True, date_format="%m/%d/%y")
df.rename(columns=scripts.col_mapping, inplace=True)
df = df/100
df.round(6).to_csv("./daily_yield_curves_1990-2022.csv")
df.describe().round(6).to_csv("./daily_yield_curves_1990-2022_summary.csv")