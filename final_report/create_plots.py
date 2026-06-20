'''
Create amazing plots with this file. You will read the data from `data_organized` 
(unless your raw data required no reduction, in which case you can read your data from `raw_data`). 
You will do plot-related work such as joins, column filtering, pivots, 
small calculations and other simple organizational work. 
'''
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import numpy as np
import os
import traceback

# ---------------------------------------------------------------------------
# Color configuration
# ---------------------------------------------------------------------------
# Use tab20 for maximum category differentiation (up to 20 distinct colors).
# tab10 only has 10, so repeated colors appear when there are many bill types.
colors = plt.get_cmap('tab20')

# Lighter qualitative palette used specifically for heatmaps so that cells
# with very low values are still readable against the background.
HEATMAP_CMAP = 'YlOrRd'


"""
Uses the colormap defined above to return equally spaced colors
Args:
    count(int): number of colors to return
Returns:
    list[tuple[float, float, float, float]]: list of colors
"""
def get_colors(count: int) -> list[tuple[float, float, float, float]]:
    return [colors(i) for i in np.linspace(0, 1, count)]


"""
Creates a plot of consumer confidence over time
"""
def consumer_confidence_index_plot():
    data = pd.read_csv("data_organized/Consumer_Confidence_Index.csv")
    # Convert Date column to datetime
    data['Date'] = pd.to_datetime(data['Date'])
    
    dates = pd.date_range("2001-04-01", "2025-12-01", freq="YS")
    data = data[data["Date"].isin(dates)]
    # Select a few countries for plotting
    countries = ['United States', 'Germany', 'Japan', 'United Kingdom']
    
    # Melt the data for easier plotting with seaborn
    data_melted = data.melt(id_vars=['Date'], value_vars=countries, var_name='Country', value_name='CCI')
    
    # Create the plot — use a distinct palette for the four countries
    country_palette = ['#E63946', '#457B9D', '#2A9D8F', '#E9C46A']
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=data_melted, x='Date', y='CCI', hue='Country', palette=country_palette)
    
    # Customize the plot
    plt.title('Consumer Confidence Index Over Time')
    plt.xlabel('Date')
    plt.ylabel('Consumer Confidence Index')
    plt.legend(title='Country')
    plt.grid(True, alpha=0.3)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Show the plot
    plt.tight_layout()
    plt.savefig("final_report/CCI.png")
    plt.clf()


"""
Creates a plot of the US GDP over time
"""
def united_states_gdp():
    data = pd.read_csv("data_organized/united_states_outlook.csv")
    
    # Find the row for GDP
    gdp_row = data[data['INDICATOR'] == "Gross domestic product (GDP), Current prices, US dollar"]
    
    # Get the year columns
    year_cols = [str(year) for year in range(1980, 2031)]
    
    # Extract values
    gdp_values = gdp_row[year_cols].iloc[0]
    
    # Create a dataframe for plotting
    gdp_df = pd.DataFrame({'Year': year_cols, 'GDP': gdp_values})
    
    # Convert Year to int
    gdp_df['Year'] = gdp_df['Year'].astype(int)
    
    # Plot with a distinctive teal color
    plt.figure(figsize=(12, 6))
    plt.plot(gdp_df['Year'], gdp_df['GDP'], marker='o', color='#2A9D8F')
    plt.title('United States GDP (Current Prices, US Dollar)')
    plt.xlabel('Year')
    plt.ylabel('GDP (Billions USD)')
    plt.grid(True)
    plt.savefig("final_report/us_gdp.png")
    plt.clf()


"""
Groups bills by year, then averages the proportions by year before returning the new dataset.
Reads from appropriations_catagorized.csv.

Returns:
    DataFrame: the appropriations_catagorized dataset with just year and labels averaged for each year
"""
def bill_prop_by_year_grouping() -> pd.DataFrame:
    appropriations_catagorized = pd.read_csv("data_organized/appropriations_catagorized.csv")
    
    # convert to datetime
    appropriations_catagorized["Date"] = pd.to_datetime(appropriations_catagorized["Date"])

    # keep only needed columns
    appropriations_catagorized = appropriations_catagorized.drop(columns=["url", "short_description", "Bill ID", "Bill Name"])

    # average bill props by year
    by_year = appropriations_catagorized.groupby(appropriations_catagorized.Date.dt.year).mean()
    return by_year.drop(columns=["Date", "Unnamed: 0"])


"""
Generates three different graphs, all of which are saved to the folder 'final_report/prop_by_year'
These plots compare the average scores for each year as an area plot, stacked bar chart, and line plot.

Heatmap uses a PowerNorm to compress the extreme range between many near-zero scores and a few
dominant ones, making low-value cells clearly visible with the lighter YlOrRd palette.
"""
def proportions_over_time() -> None:
    
    # get bills by year
    by_year = bill_prop_by_year_grouping()

    # --- heatmap ---
    # Flatten values to determine a good gamma for PowerNorm
    flat = by_year.values.flatten()
    flat = flat[flat > 0]  # exclude exact zeros for log-safe stats
    vmax = float(np.nanmax(flat))
    vmin = 0.0

    # gamma < 1 compresses high values and expands low values in the colormap
    norm = mcolors.PowerNorm(gamma=0.4, vmin=vmin, vmax=vmax)

    plt.figure(figsize=(max(10, len(by_year.columns)), max(6, len(by_year) // 2)))
    sns.heatmap(
        by_year,
        annot=True,
        fmt=".3f",
        cmap=HEATMAP_CMAP,
        norm=norm,
        linewidths=0.4,
        linecolor='#cccccc',
        annot_kws={"size": 7},
    )
    plt.yticks(rotation=0)  # Make y-axis labels horizontal
    plt.title("Bill Proportions by Year")
    # Using tight helps compress everything but keep it readable
    plt.savefig('final_report/prop_by_year/heatmap.png', bbox_inches='tight')
    plt.clf()

    # area plot
    plot = by_year.plot.area(colormap=colors)
    # makes sure legend doesn't overlap anything
    plot.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.title("Bill Proportions by Year")
    # ensures x ticks are once per year
    plt.xticks(range(2009, 2027, 1), rotation=90, ha='right')
    plt.savefig('final_report/prop_by_year/area.png', bbox_inches='tight')
    plt.clf()
    
    # stacked bar plot
    plot = by_year.plot.bar(stacked=True, colormap=colors)
    plot.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.title("Bill Proportions by Year")
    plt.savefig('final_report/prop_by_year/bar.png', bbox_inches='tight')
    plt.clf()
    
    # line plot
    plot = by_year.plot.line(colormap=colors)
    plot.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.title("Bill Proportions by Year")
    plt.xticks(range(2009, 2027, 1), rotation=90, ha='right')
    plt.savefig('final_report/prop_by_year/line.png', bbox_inches='tight')
    plt.clf()


"""
Creates a line plot with multiple lines with differing y-axes
Args:
    x_label (str): the label of the x axis
    name (str): the name to save the graph as (in final_report)
    title(str): title of the plot
    data_0 ((any, str)): a tuple containing the first line to plot (first value) and the label for that axis
    args: any number of additional plots in the same form as data_0
"""
def plot_lines(x_label:str, name: str, title: str, data_0: tuple[any, str], *args) -> None:
    # set up plot
    fig, host = plt.subplots(figsize=(8,5), layout='constrained')
    axs = [host.twinx() for i in range(len(args))]

    # Colors — use a high-contrast set so each line reads clearly
    c = get_colors(len(args) + 1)
        
    # first dataset
    host.set_xlabel(x_label)
    p = host.plot(data_0[0], color=c[0], label=data_0[1])

    # all the rest
    extra_plots = [axs[i].plot(args[i][0], color=c[i+1], label=args[i][1], linestyle='dashed') for i in range(len(args))]

    # make a list of plots
    for plot in extra_plots:
        p += plot

    host.set_ylabel(data_0[1])
    host.yaxis.label.set_color(c[0])
    for i in range(0, len(args)):
        # offset extra axis
        axs[i].spines['right'].set_position(('outward', 60 * (i)))
        # label
        axs[i].set_ylabel(args[i][1])
        # color
        axs[i].yaxis.label.set_color(c[i+1])

    # legend automatically handles all datasets since p is a list of plots
    host.legend(handles=p, bbox_to_anchor=(1 + (.2 * len(args)), 1), loc=2, borderaxespad=0.)
    host.set_title(title)
    plt.xticks(range(2009, 2027, 1))
    host.tick_params(axis='x', rotation=90)

    # Removed plt.show() to prevent silent crashes in non-interactive terminals
    # save
    plt.savefig("final_report/" + name + ".png", bbox_inches='tight')
    plt.clf()


"""
Returns a dataset normalized between 0 (minimum original value) and 1 (maximum original value)
"""
def normalize(df: pd.DataFrame) -> pd.DataFrame:
    return (df-df.min())/(df.max()-df.min())


# TODO: add other indicators?
"""
Creates a line plot for each bill type, plotting there proportion over time along with economic indicators 
"""
def prop_and_economy():

    # get mean consumer confidence by year
    consumer_confidence = pd.read_csv("data_organized/Consumer_Confidence_Index.csv")
    consumer_confidence = consumer_confidence[93:]

    consumer_confidence["Date"] = pd.to_datetime(consumer_confidence["Date"])
    consumer_confidence = consumer_confidence.groupby(consumer_confidence.Date.dt.year)["United States"].mean()
    
    # get bill proportions by year (reads from appropriations_catagorized.csv via helper)
    bills_by_year = bill_prop_by_year_grouping()

    # economic outlook data
    outlook = pd.read_csv("data_organized/united_states_outlook.csv")

    # remove values before 2009, after 2026 (predictions)
    # get GDP by year
    # make timescale play nice with other datasets
    # Lookup by indicator name, squeeze to a Series
    gdp = outlook[outlook['INDICATOR'] == "Gross domestic product (GDP), Current prices, US dollar"].iloc[:, 36:-4].squeeze()
    gdp.index = pd.to_numeric(pd.to_datetime(gdp.index).strftime('%Y'), errors='coerce')

    # get GDP per capita by year
    gdp_capita = outlook[outlook['INDICATOR'] == "Gross domestic product (GDP), Current prices, Per capita, US dollar"].iloc[:, 36:-4].squeeze()
    gdp_capita.index = pd.to_numeric(pd.to_datetime(gdp_capita.index).strftime('%Y'), errors='coerce')
    
    unemployment = outlook[outlook['INDICATOR'] == "Unemployment rate"].iloc[:, 36:-4].squeeze()
    unemployment.index = pd.to_numeric(pd.to_datetime(unemployment.index).strftime('%Y'), errors='coerce')

    # --- heatmaps ---
    # PowerNorm makes the large spread of GDP values readable while keeping
    # the lighter HEATMAP_CMAP easy to parse.
    def _make_heatmap(data: pd.DataFrame, title: str, fname: str) -> None:
        flat = data.values.flatten()
        flat = flat[~np.isnan(flat) & (flat > 0)]
        vmax = float(np.nanmax(flat)) if len(flat) > 0 else 1.0
        norm = mcolors.PowerNorm(gamma=0.4, vmin=0.0, vmax=vmax)
        plt.figure(figsize=(max(10, len(data.columns)), max(6, len(data) // 2)))
        sns.heatmap(
            data,
            annot=True,
            fmt=".1f",
            cmap=HEATMAP_CMAP,
            norm=norm,
            linewidths=0.4,
            linecolor='#cccccc',
            annot_kws={"size": 7},
        )
        plt.yticks(rotation=0) # Make labels horizontal
        plt.title(title)
        plt.savefig(fname, bbox_inches='tight')
        plt.clf()

    # heatmaps — all heatmaps calculates impact by multiplying the proportion of bills
    # by the economic data for that year (1 row's total = total economic data that year)
    _make_heatmap(
        bills_by_year.mul(gdp.T, axis=0).apply(pd.to_numeric, errors='coerce'),
        "Impact on GDP by Bill type and Year",
        "final_report/prop_and_economy/heatmap.png",
    )

    # GDP per capita heatmap
    _make_heatmap(
        bills_by_year.mul(gdp_capita.T, axis=0).apply(pd.to_numeric, errors='coerce'),
        "Impact on GDP per Capita by Bill type and Year",
        "final_report/prop_and_economy/heatmap_per_capita.png",
    )

    # consumer confidence heatmap
    _make_heatmap(
        bills_by_year.mul(consumer_confidence.T, axis=0).apply(pd.to_numeric, errors='coerce'),
        "Impact on Consumer Confidence by Bill type and Year",
        "final_report/prop_and_economy/heatmap_confidence.png",
    )

    # create line plots for each bill type
    for i in range(len(bills_by_year.columns)):
        plot_lines(
            "year", 
            "prop_and_economy/" + str(bills_by_year.columns[i]),
            "Proportion of " + str(bills_by_year.columns[i]) + " bills per year vs Economic Data",
            (bills_by_year.iloc[:, i], bills_by_year.columns[i]), 
            (consumer_confidence, "Consumer Confidence Index"),
            (gdp, "GDP (billions of dollars)"),
            #(gdp_capita, "GDP per capita (dollars)"),
            (unemployment, "Unemployment Rate")
        )

    # normalized (proportion is a flat line) - may not be accurate so not used
    for i in range(len(bills_by_year.columns)):

        prop = bills_by_year.iloc[:, i]

        #combined = pd.DataFrame([prop.sub(prop), normalize(consumer_confidence).sub(prop), normalize(gdp).sub(prop), normalize(gdp_capita).sub(prop), normalize(unemployment).sub(prop)]).T
        #combined.columns = [bills_by_year.columns[i], "Consumer Confidence Index", "GDP (billions of dollars)", "GDP per capita (dollars)", "Unemployment Rate"]
        combined = pd.DataFrame([prop.sub(prop), normalize(consumer_confidence).sub(prop), normalize(gdp).sub(prop), normalize(unemployment).sub(prop)]).T
        combined.columns = [bills_by_year.columns[i], "Consumer Confidence Index", "GDP (billions of dollars)", "Unemployment Rate"]

        plot = combined.plot.line(colormap=colors)
        plot.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.title("Variance in Economic Data by " + str(bills_by_year.columns[i]) + " bills")
        # TODO: make more dyanmic
        plt.xticks(range(2009, 2027, 1), rotation=90, ha='right')
        plt.savefig('final_report/prop_and_economy/' + str(bills_by_year.columns[i]) + '_normal.png', bbox_inches='tight')
        plt.clf()


"""
Creates a slope plot of the change in bill proportions from 2009 to 2026.

Note: creates overlapping text that was fixed afterwards

Code adapated from https://python-graph-gallery.com/web-slope-chart-matplotlib/
"""
def slope_prop_graph():
    plt.figure(figsize=(6, 8))
    plt.axvline(x=2009, color='black', linestyle='--', linewidth=1)
    plt.axvline(x=2026, color='black', linestyle='--', linewidth=1) 
    plt.text(2008, 11000, 'BEFORE', fontsize=12, color='black', fontweight='bold')
    plt.text(2027, 11000, 'AFTER', fontsize=12, color='black', fontweight='bold')

    bills = bill_prop_by_year_grouping()

    for i in range(len(bills.columns)):
    
        # Color depending on the evolution
        value_before = bills.iloc[0, i]
        value_after = bills.iloc[-1, i]
        
        # Red if the value has decreased, green otherwise
        if value_before > value_after:
            color='#E63946'   # vibrant red
        else:
            color='#2A9D8F'   # teal green
        
        # Add the line to the plot
        plt.plot([2009, 2026], bills.iloc[[0,-1], i], marker='o', label=bills.columns[i], color=color)
        plt.text(2009-3.8, # x-axis position
             bills.iloc[0, i], #y-axis position
             f'{bills.columns[i]}, \n{bills.iloc[0, i]:.3f}', # Text
             fontsize=8, # Text size
             color='black', # Text color
            ) 
        plt.text(2026+0.12, # x-axis position
             bills.iloc[-1, i], #y-axis position
             f'{bills.columns[i]}, \n{bills.iloc[-1, i]:.3f}', # Text
             fontsize=8, # Text size
             color='black', # Text color
            ) 

    # Add a title ('\n' allow us to jump lines)
    plt.title('Slope Chart: Comparing Bill Proportions between 2009 vs 2026') 

    plt.yticks([]) # Remove y-axis
    plt.xticks(range(2009, 2027, 1), rotation=90, ha='right')
    plt.box(False) # Remove the bounding box around plot
    plt.savefig('final_report/slope_prop_plot.png')
    plt.clf()


"""
Plots the number of bills by year.
Reads bill count from appropriations_catagorized.csv.
"""
def count_time():
    appropriations_catagorized = pd.read_csv("data_organized/appropriations_catagorized.csv")
    
    # convert to datetime
    appropriations_catagorized["Date"] = pd.to_datetime(appropriations_catagorized["Date"])

    # keep only needed columns
    appropriations_catagorized = appropriations_catagorized.drop(columns=["url", "short_description", "Bill ID", "Bill Name"])

    # count bills per year
    count = appropriations_catagorized.groupby(appropriations_catagorized.Date.dt.year).size()

    # get mean consumer confidence by year
    consumer_confidence = pd.read_csv("data_organized/Consumer_Confidence_Index.csv")
    consumer_confidence = consumer_confidence[93:]

    consumer_confidence["Date"] = pd.to_datetime(consumer_confidence["Date"])
    consumer_confidence = consumer_confidence.groupby(consumer_confidence.Date.dt.year)["United States"].mean()
    
    # get bill proportions by year (reads from appropriations_catagorized.csv via helper)
    bills_by_year = bill_prop_by_year_grouping()

    outlook = pd.read_csv("data_organized/united_states_outlook.csv")

    # Lookup by indicator name, squeeze to a Series
    gdp = outlook[outlook['INDICATOR'] == "Gross domestic product (GDP), Current prices, US dollar"].iloc[:, 36:-4].squeeze()
    gdp.index = pd.to_numeric(pd.to_datetime(gdp.index).strftime('%Y'), errors='coerce')

    # get GDP per capita by year
    gdp_capita = outlook[outlook['INDICATOR'] == "Gross domestic product (GDP), Current prices, Per capita, US dollar"].iloc[:, 36:-4].squeeze()
    gdp_capita.index = pd.to_numeric(pd.to_datetime(gdp_capita.index).strftime('%Y'), errors='coerce')
    
    unemployment = outlook[outlook['INDICATOR'] == "Unemployment rate"].iloc[:, 36:-4].squeeze()
    unemployment.index = pd.to_numeric(pd.to_datetime(unemployment.index).strftime('%Y'), errors='coerce')
    
    # area plot
    plot = count.plot.area(colormap=colors)
    plot.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.title("Bill Counts by Year")
    plt.xticks(range(2009, 2027, 1), rotation=90, ha='right')
    plt.savefig('final_report/count_by_year/area.png', bbox_inches='tight')
    plt.clf()
    
    # stacked bar plot
    plot = count.plot.bar(stacked=True, colormap=colors)
    plot.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.title("Bill Counts by Year")
    plt.savefig('final_report/count_by_year/bar.png', bbox_inches='tight')
    plt.clf()
    
    # line plot
    plot_lines(
        "year", 
        "count_by_year/line",
        "Number of Bills per year vs Economic Data",
        (count, "Number of Bills"), 
        (consumer_confidence, "Consumer Confidence Index"),
        (gdp, "GDP (billions of dollars)"),
        #(gdp_capita, "GDP per capita (dollars)"),
        (unemployment, "Unemployment Rate")
    )


"""
Generates all plots
"""
def plot_all():
    print("Starting plot generation...")
    os.makedirs('final_report/prop_by_year', exist_ok=True)
    os.makedirs('final_report/prop_and_economy', exist_ok=True)
    os.makedirs('final_report/count_by_year', exist_ok=True)
    
    tasks = [
        ("CCI Index", consumer_confidence_index_plot),
        ("US GDP", united_states_gdp),
        ("Proportions Over Time", proportions_over_time),
        ("Prop and Economy", prop_and_economy),
        ("Slope Graph", slope_prop_graph),
        ("Count Time", count_time)
    ]
    
    for name, func in tasks:
        try:
            print(f"Running {name}...")
            func()
        except Exception as e:
            print(f"Error in {name}:")
            traceback.print_exc()
            
    print("All plots created successfully")

if __name__ == "__main__":
    plot_all()
