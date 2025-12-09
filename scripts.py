import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from tabulate import tabulate

yearly_yield_curves_cache = {}
print("Initialized yearly_yield_curves_cache as an empty dictionary.")

col_mapping = {"1 Mo": round(1/12, 4), "1.5 Month": round(1.5/12, 4), "2 Mo": round(2/12, 4), "3 Mo": round(3/12, 4), "4 Mo": round(4/12, 4), "6 Mo": round(6/12, 4),
               "1 Yr" : 1, "2 Yr" : 2, "3 Yr" : 3, "5 Yr" : 5, "7 Yr" : 7, "10 Yr" : 10, "20 Yr" : 20, "30 Yr" : 30}

def get_yield_curve_for_date(date, visual=False, cache=yearly_yield_curves_cache):
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
        if visual:
            plt.figure(figsize=(10, 5))
            plt.plot(yield_curve.index, yield_curve.values, marker='o', linestyle='-')
            plt.title(f"Yield Curve for {date.strftime('%Y-%m-%d')}")
            plt.xlabel("Tenors (in years)")
            plt.ylabel("Annualized Yields")
            plt.legend([f"Yield Curve: {date.strftime('%Y-%m-%d')}"])
            plt.grid(True)
            plt.show()
        return yield_curve
    except KeyError:
        raise ValueError(f"No yield curve data found for date: {date_str}")
    except Exception as e:
        raise ValueError(f"An unexpected error occurred while retrieving data for {date_str}: {e}")
def compare_yield_curves(date1, date2, visual=True):
    """
    Compares the yield curves for two given dates, always printing a formatted table
    and optionally displaying a visual comparison.

    Args:
        date1 (datetime.date): The first date for the yield curve.
        date2 (datetime.date): The second date for the yield curve.
        visual (bool): If True, a visual comparison (plots) will be displayed.
                       Defaults to True.
    """

    # ensure that date1 > date2
    if date1 < date2:
        date1, date2 = date2, date1

    try:
        yc1 = get_yield_curve_for_date(date1)
        yc2 = get_yield_curve_for_date(date2)

        # Ensure both series have the same index (tenors)
        common_tenors = yc1.index.intersection(yc2.index)
        if common_tenors.empty:
            raise ValueError(f"No common tenors found for dates: {date1.strftime('%Y-%m-%d')} and {date2.strftime('%Y-%m-%d')}")

        yc1 = yc1.loc[common_tenors]
        yc2 = yc2.loc[common_tenors]

        # Create a reverse mapping for human-readable tenor labels once
        full_reverse_col_mapping = {v: k for k, v in col_mapping.items()}
        tenor_labels = [full_reverse_col_mapping.get(t, f'{t} Yr') for t in common_tenors]

        # Calculate differences (common for both output types)
        absolute_diff = (yc2 - yc1) * 10000  # Convert to basis points
        # Replace 0 with NA to avoid ZeroDivisionError for relative difference
        relative_diff = ((yc2 - yc1) / yc1.replace(0, pd.NA)) * 100  # in percentage points

        # Tabulation (always printed first)
        data_to_display = pd.DataFrame({
            f'YC {date1.strftime("%Y-%m-%d")}_pct': yc1 * 100,
            f'YC {date2.strftime("%Y-%m-%d")}_pct': yc2 * 100,
            'Absolute Difference (bps)': absolute_diff,
            'Relative Difference (%)': relative_diff
        })
        data_to_display.index = tenor_labels  # Already created above

        print(f"\n--- Yield Curve Comparison: {date1.strftime('%Y-%m-%d')} vs {date2.strftime('%Y-%m-%d')} ---")
        print(tabulate(data_to_display.T, headers='keys', tablefmt='fancy_grid', floatfmt=".2f"))

        # Visualization (now comes after tabulation)
        if visual:
            fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=False)

            # Subplot 1: Two Yield Curves
            axs[0].plot(yc1.index, yc1.values, marker='o', linestyle='-', label=f'YC: {date1.strftime("%Y-%m-%d")}')
            axs[0].plot(yc2.index, yc2.values, marker='x', linestyle='--', color='red', label=f'YC: {date2.strftime("%Y-%m-%d")}')
            axs[0].set_title('Comparison of Daily Treasury Yield Curves')
            axs[0].set_ylabel('Annualized Yields')
            axs[0].legend()
            axs[0].grid(True)
            # Removed explicit set_xticks and set_xticklabels to use default behavior

            # Subplot 2: Changes in Yield Curve (Bar Graph)
            x_positions = range(len(common_tenors))
            axs[1].bar(x_positions, absolute_diff.values, width=0.5, color=['green' if x >= 0 else 'red' for x in absolute_diff.values], label=f'Change ({date2.strftime("%m/%d")}-{date1.strftime("%m/%d")})')
            axs[1].set_title('Change in Yield Curve (Basis Points)')
            axs[1].set_xlabel('Tenors')
            axs[1].set_ylabel('Yield Change (bps)')
            axs[1].legend()
            axs[1].grid(True)
            axs[1].set_xticks(x_positions)
            axs[1].set_xticklabels(tenor_labels, rotation=45, ha='right')

            plt.tight_layout()
            plt.show()

    except ValueError as e:
        print(f"Error comparing yield curves: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    date1 = dt.datetime(*map(int, input("Input Valid date (%Y/%m/%d): ").split("/")))
    date2 = dt.datetime(*map(int, input("Input Valid date (%Y/%m/%d): ").split("/")))
    yc1 = get_yield_curve_for_date(date1, True)
    yc2 = get_yield_curve_for_date(date2)
    compare_yield_curves(date1, date2)