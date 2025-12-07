import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

yearly_yield_curves_cache = {}
print("Initialized yearly_yield_curves_cache as an empty dictionary.")

col_mapping = {"1 Mo": round(1/12, 4), "1.5 Month": round(1.5/12, 4), "2 Mo": round(2/12, 4), "3 Mo": round(3/12, 4), "4 Mo": round(4/12, 4), "6 Mo": round(6/12, 4),
               "1 Yr" : 1, "2 Yr" : 2, "3 Yr" : 3, "5 Yr" : 5, "7 Yr" : 7, "10 Yr" : 10, "20 Yr" : 20, "30 Yr" : 30}

def get_yield_curve_for_date(date, cache=yearly_yield_curves_cache):
    """
    Retrieves the daily yield curve for a given date, utilizing a cache for yearly data.

    Args:
        date (datetime.date): The date for which to retrieve the yield curve.
        cache (dict): A dictionary to cache yearly DataFrame objects.

    Returns:
        pandas.Series: The yield curve for the specified date.

    Raises:
        ValueError: If the year is before 1990 or no data is available for the specific date.
    """
    date_str = date.strftime("%Y-%m-%d")
    year = date.year

    if year < 1990:
        raise ValueError(f"Data is not available before 1990. Requested year: {year}")

    if year not in cache:
        print(f"Loading data for year {year} into cache...")
        # Construct URL for the given year
        url = f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv"

        try:
            # Load data
            yearly_df = pd.read_csv(url, index_col="Date", parse_dates=True)
            # Rename columns using the global col_mapping
            yearly_df = yearly_df.rename(columns=col_mapping)
            # Convert to decimals
            yearly_df = yearly_df / 100
            cache[year] = yearly_df
            print(f"Successfully loaded and cached data for {year}.")
        except Exception as e:
            raise ValueError(f"Could not load data for year {year}. Error: {e}")

    # Retrieve DataFrame from cache
    df_yearly = cache[year]

    try:
        # Retrieve the specific date's yield curve
        yield_curve = df_yearly.loc[date_str]
        return yield_curve
    except KeyError:
        raise ValueError(f"No yield curve data found for date: {date_str}")
    except Exception as e:
        raise ValueError(f"An unexpected error occurred while retrieving data for {date_str}: {e}")

def visualize_yield_curve(date):
    """
    Visualizes the yield curve for a given date.

    Args:
        date (datetime.date): The date for which to visualize the yield curve.
    """
    try:
        yield_curve_data = get_yield_curve_for_date(date)

        plt.figure(figsize=(10, 5))
        plt.plot(yield_curve_data.index, yield_curve_data.values, marker='o', linestyle='-')
        plt.title(f"Yield Curve for {date.strftime('%Y-%m-%d')}")
        plt.xlabel("Tenors (in years)")
        plt.ylabel("Annualized Yields")
        plt.legend([f"Yield Curve: {date.strftime('%Y-%m-%d')}"])
        plt.grid(True)
        plt.show()
    except ValueError as e:
        print(f"Error visualizing yield curve for {date.strftime('%Y-%m-%d')}: {e}")

if __name__ == "__main__":
    valid_date = dt.datetime(*map(int, input("Input Valid date (%Y/%m/%d): ").split("/")))
    visualize_yield_curve(valid_date)