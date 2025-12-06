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

if __name__ == "__main__":

    print("Defined get_yield_curve_for_date function.")

    # --- Example Usage ---
    print("\n--- Demonstrating get_yield_curve_for_date function ---")

    # 1. Valid date (2024, already in cache if previous cells ran and assigned df to cache[2024])
    # Assuming 'df' from previous execution is for 2024, let's put it into the cache for a clean start
    if 2024 not in yearly_yield_curves_cache and 'df' in globals():
        yearly_yield_curves_cache[2024] = df

    valid_date_2024 = dt.date(2024, 1, 5)
    try:
        print(f"\nAttempting to retrieve yield curve for {valid_date_2024}:")
        yc_2024 = get_yield_curve_for_date(valid_date_2024, yearly_yield_curves_cache)
        print(f"Yield curve for {valid_date_2024}:\n{yc_2024}")
    except ValueError as e:
        print(f"Error for {valid_date_2024}: {e}")

    # 2. Valid date for a year not yet in the cache (e.g., 2023)
    valid_date_2023 = dt.date(2023, 1, 5)
    try:
        print(f"\nAttempting to retrieve yield curve for {valid_date_2023} (should trigger load):")
        yc_2023 = get_yield_curve_for_date(valid_date_2023, yearly_yield_curves_cache)
        print(f"Yield curve for {valid_date_2023}:\n{yc_2023}")
    except ValueError as e:
        print(f"Error for {valid_date_2023}: {e}")

    # 3. A date for which no data exists (e.g., a weekend)
    no_data_date = dt.date(2024, 1, 7) # A Sunday in 2024
    try:
        print(f"\nAttempting to retrieve yield curve for {no_data_date} (should error - no data):")
        yc_no_data = get_yield_curve_for_date(no_data_date, yearly_yield_curves_cache)
        print(f"Yield curve for {no_data_date}:\n{yc_no_data}")
    except ValueError as e:
        print(f"Error for {no_data_date}: {e}")

    # 4. A date before 1990 to demonstrate the year validation error
    invalid_year_date = dt.date(1989, 12, 25)
    try:
        print(f"\nAttempting to retrieve yield curve for {invalid_year_date} (should error - invalid year):")
        yc_invalid_year = get_yield_curve_for_date(invalid_year_date, yearly_yield_curves_cache)
        print(f"Yield curve for {invalid_year_date}:\n{yc_invalid_year}")
    except ValueError as e:
        print(f"Error for {invalid_year_date}: {e}")

    # 5. A date in the future (no data)
    future_date = dt.date(2025, 12, 15) # Assuming 2025 data isn't available yet
    try:
        print(f"\nAttempting to retrieve yield curve for {future_date} (should error - no data):")
        yc_future = get_yield_curve_for_date(future_date, yearly_yield_curves_cache)
        print(f"Yield curve for {future_date}:\n{yc_future}")
    except ValueError as e:
        print(f"Error for {future_date}: {e}")