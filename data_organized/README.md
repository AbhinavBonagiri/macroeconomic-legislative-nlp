# Instructions

## Recommended: Create a virtual environment
Revert back Python 3.12 for spacy package and transformers
```Command Prompt
python3.12 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

## Install Dependecies
Install pdfminer, bs4, requests, enum, and transformers. To install these, run the following lines in command prompt
```Command Prompt
pip install pdfminer
pip install bs4
pip install requests
pip install spacy
pip install enum
pip install transformers
pip install torch
pip install pandas
```

# How to run?
To organize data, run the function 'main'. This function is run by default in 'preprocess.py'. This method has functions calls built in for convenience which will output files in `data_organized/`
```Command Prompt
python preprocess.py
```

## Uncomment NLP categorization method
```python
#catagorize_bills(pandas.read_csv("data_organized/appropriations.csv"), labels, debug=True)
```
    
To generate the the catagorization scores for each appropriation bill, you will need to run 'catagorize_bills' on the organized appropriations.csv with a list of your catagories. This method will not run by default and the call is commented out, as said method reuiqres a long time to run.

This code aims to web scrape congressional bills for NLP analysis, process datasets and interpolate NaN values, and organize datasets that are made in odd ways.

# Important Output & Columns
## All_data_FIW_2013-2025.csv
This is a dataset including all the freedoms each country has allowed to its people. How free a country is can tell a lot about its political climate and priorities for its own citizens.
| Column | Description |
| :--- | :--- |
| Country/Territory | The name of the country that is being analyzed. |
| PR rating | Indicates how well a country’s political rights are for its people |
| CL rating | Indicates how well a country’s civil liberties are for its people. |
| A | The electoral process determines a fair political process.|
| C | A rating for how well a government is functioning. |
| D | A rating that determines the freedom of its citizens. |
| G | Indicates how much the citizens’ rights of a country are granted. |
| Total | Aggregates all the categories into one freedom score. |

## appropriations.csv
The organized and filtered version of bills.csv, containing only bills relating to appropriations. 
| Column | Description |
| :--- | :--- |
| Bill ID | The ID of the bill |
| Bill Name | The name of the bill |
| Date | The date of the last action taken with the bill |
| url | A url link to a site containing the full text of the bill |
| short_description | A 'short' description for the bill provided by the original datasource |

## catagorized_bills.csv
Appropriations.csv with additional columns containing the catagorization scores.
The exact names of the columns will vary with how the method was run.
| Column | Description |
| :--- | :--- |
| *Same as appropriations.csv* | *Same as appropriations.csv* |
| *Category n name* | The fit rating for *Category n* |
| *Category n name_description* | The fit rating for *Category n* when run off the short_description in BOTH mode |
| *Category n name_full text* | The fit rating for *Category n* when run off the full, webscraped text in BOTH mode |

## Consumer_Confidence_Index.csv
This dataset contains the consumer confidence index for each country every month. Note: Data was interpolated to accomodate for better plotting and a complete dataset.
| Column | Description |
| :--- | :--- |
| Date | Represents the month and year for the data in the row |
| \<Countries> | A collection of columns named after countries. |

## new_Consumer_Confidence_Index.csv
A transposed dataset of consumer confidence index, countries is the index while columns are years. This is used to know the statistics for a country in a specific year.
| Column | Description |
| :--- | :--- |
| \<Dates> | Consumer confidence index for that country (rows) in that year |

## united_states_outlook.csv
A sorted economic outlook of indicators containing only data on the US. Indicators are by the year.
| Column | Description |
| :--- | :--- |
| OBS_MEASURE | The type of measured value |
| INDICATOR | The economic indicator being analyzed |
| FREQUENCY | How often data appears |
| SCALE | The units used to scale the number |
| \<Dates> | The years of the collection |


#  Data Cleaning, Reduction, and Preparation
1. Webscraping:
    For the logic of web scraping the method below was used.
    def get_pdf_from_bill_url(url: str, make_txt: bool = False, keep_pdf: bool = False, folder: str = "")
    This method utilizes beautifulsoup4 and pdfminer to extract the contents of the url. The process generally is straightforward, but in this case, beautiful soup does not support JS scripts that load webpages instead depends on html. To solve this problem, a html file that locally makes a table to solve the issue.
    The table involves many links and needs to be prioritized which link can be got, as some tables don't give the links you are looking for. The prioritization is as follows, passed > enrolled > first available. 

2. Extracting Data from Web Scraping:
    After creating a bills.csv of all the passed bills. Boolean masking is further used to filter to "Appropriation" bills that show the budget of the U.S., that is vital to understanding how it impacts economic health of the country through budget itself. The Web Scraping will go through the series of url links from the shortened csv file called appropriations.csv. 

3. Consumer Confidence Index(Time-Series Data): 
    Two separate datasets were joined to make a cohesive dataset. This dataset was then interpolated for the missing NaNs. The process of interpolation is as such, to be done through a threshold to limit the interpolation and drop any countries with excessive gaps in data. After that, the code can be interpolated. 

4. Economic Outlook:
    This is one of the easier datasets to change, mainly because the missing values in years largely don't cause issues with the data. Since, we are focusing on data collection specifically on the United States, boolean masking is used to filter United States.