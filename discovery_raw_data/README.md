

# **Assessing the Effectiveness of <br> Legislative Bills in Improving <br> Economic Health**

**Student Name 1:** **Jack Trepp**  
**Student Name 2:** **Abhinav Bonagiri**  
**Date:** **02/08/2026**  
**Course:** **Intermediate Data Programming**

---

# **Summary of research questions**

## **Focus: How do economic policies affect the economic health of a country?** 

### **1\. How often are each type of policy used, and is there any relationship we can find in their usage?**

Identifying trends in the implementation of different policy types to help understand the impact of those policies. Which can be done by understanding what typically occurs before a certain type of policy is implemented.

### **2\. What are the influential factors that determine the impact the policy has on the “economic health”1 of the country?**

Policies are usually implemented in a systematic manner, and we can identify these patterns by identifying similar attributes across different policies. By breaking policies down into these attributes, we can determine which parts of an economic policy have the largest impact, as well as trends and relationships between these parts, such as one part only being effective when combined with another.

### **3\. How does the impact of economic policies vary by the size of a country?**

Certain policies may be more effective for smaller countries or only viable for larger countries to implement. By looking at correlations between the number of people in a country and the effectiveness of certain policies, we can better find which policies work at which scales.

### **4\. How does the “political climate”2 of a country affect its economic health?**

The political climate of a country determines what policies it will take for the benefit of the public, economy, or companies. Depending on what the country prioritizes, it will be shown in the impact on the long-term data.

### **5\. How long does it take for a policy to take effect, if not at all?**

Some policies may not result in an immediate impact on the economy, such as being delayed or never occur, which may hurt the economy instead of helping it. By looking for trends in the implementation of a policy and the delayed impact on the economy, we can identify how much the policy lags behind the current health of the economy.

*1 \- Economic Health* \- Refers to a combination of GDP per capita, inflation, unemployment, consumer confidence, and other economic indicators.

*2 \- Political Climate* \- Refers to how separated the economy is from politics and the effect of being one or the other socioeconomic system(social democratic, etc) or political alignment.

---

# **Motivation**

The economic health of a country has a major impact on the quality of life of those living there. A country with ‘poor economic health’ might have mass poverty, dramatic wealth inequality, hyperinflation, or other such economic issues. While legislation is not the only contributor to a country’s economy, it will have an impact through aspects such as tariffs, interest rates,  budgets, taxes, and many other factors. It is also easier for citizens to influence compared to other factors, such as job markets, trade, and natural disasters, as in most countries across the world, citizens are able to either directly vote on these policies or elect representatives to do so for them.

By being able to predict the impact of proposed legislation, we can better understand how our votes will impact our country’s economy. We can also notice trends in types of legislation in order to better understand what policies could be proposed to alleviate ongoing issues. This impact is especially relevant to us as we are new or soon-to-be voters in a time where brand-new technology requires new legislation.

---

# **Task List**

[Final Project Task List](https://docs.google.com/spreadsheets/d/1d8SZ-Q937NU6FQnIpNDvuuZURXYM4zOMWoKYDN33mL4/edit?usp=sharing)

| Task | Task ID | Partner | Status | Week \# | Dependency | Details / Description | Notes |
| :---- | ----- | :---- | :---- | ----- | :---- | :---- | :---- |
| **Discovery Document** |  |  | Completed | 6 |  |  |  |
| Finalize Topic | 1 | Both | Completed | 6 |  | Decide on topic to research | Sentiment Analysis chosen |
| Finalize Research Questions | 2 | Both | Completed | 6 | TID: 1 | 3+ Research Questions for topic | Need 1-3 sentences / question |
| Finish Task List for Discovery Document Milestone | 3 | [Abhinav Bonagiri](mailto:2022986@apps.nsd.org) | Completed | 6 |  | Milestones and next few weeks in this sheet |  |
| Challenge Goal Plan | 4 | Both | Completed | 6 |  | Planned Challenge Goal ideas | Review and edit |
| Motivation Paragraph | 5 | Both | Completed | 6 |  | 1-2 paragraphs, why we care about topic, why it matters | Review and edit |
| **Data collection** |  |  | Completed |  |  | Data Collection for the Discovery Document |  |
| Gather Data | 6 | Both | Completed | 7 |  | Gather datasets for our topic | Need more legislation for other countries |
| Summarize Datasets | 7 | Both | Completed | 7 | TID: 6 | Size, source, description for each dataset. Column summary for each dataset |  |
| Dataset Challenges | 8 | [Jack Trepp](mailto:1108608@apps.nsd.org) | Completed | 7 | TID: 6 | Explain the challenges in finding datasets or with using the data |  |
| Mid-Winter Break |  |  | Completed | 8 |  | Have fun\! | Not long enough :( |
| **Data Organization** |  |  | In progress | 9 |  | Organize and reduce datasets, upload to github. Sketches of graphs |  |
| Scrape bills | 9 | TBD | Not started | 9 |  | Utilize bill datasets to scrape bill pdf (and other things?) |  |
| Sentiment analysis | 10 | TBD | Blocked | 9 |  | Perform sentiment analysis on the scraped bills | Blocked until bill pdfs scraped, may need converting to txt |
| Combine Consumer Sentiment Data | 11 | TBD | Not started | 9 |  | Combine the 2 downloads for consumer\_sentiment\_index.csv |  |

---

# **Datasets**

## **Overall Summary**

| Dataset | Source | Size (row x column) | Description |
| :---- | :---- | :---- | :---- |
| Consumer\_Confidence\_Index.csv | [https://www.oecd.org/en/data/indicators/consumer-confidence-index-cci.html](https://www.oecd.org/en/data/indicators/consumer-confidence-index-cci.html) | 43x639 | A collection of consumer confidence index values (reflection of outlook of citizens on a country’s economy) by country and month. |
| World\_Economic\_Outlook.csv | [https://data.imf.org/en/Data-Explorer](https://data.imf.org/en/Data-Explorer) | 58x8170 | Annual data on a variety of economic indicators for a variety of countries. |
| 2009-2010\_111th\_Congress/csv/bills.csv (representative of all congress bill csv files) | [https://legiscan.com/US/datasets](https://legiscan.com/US/datasets) | 14x10996 | An overview of bills passed by the US congress in the 111th congress session (similar data for 112th-119th). |
| Sentiment\_Analysis\_Bills.csv | Scraped from links provided by other data sets | Unknown | We will utilize web scraping and sentiment analysis of bills to create a dataset containing the name of bills, key dates for actions such as introduction and resolution, whether it passed or failed, and keywords connecting it to the economy, created by sentiment analysis.  |
| All\_data\_FIW\_2013-2025.csv | [https://freedomhouse.org/report/freedom-world](https://freedomhouse.org/report/freedom-world)  | 44x2725 | Aggregates numerical data of each country’s freedom and democracy standing across 2013-2025. Splits the freedom and democracy index into 44 subfactors that detail each aspect of a country’s freedom. |

## **Column Summaries**

### **2009-2010\_111th\_Congress/csv/bills.csv (representative of all congress bill csv files)**

This dataset and similar datasets contain information about all the bills passed by that congress session. Especially useful are the links to more indepth information on the bill where we can pull the text of the bill and the dates of actions taken.

| Column Name |  | Description |  |
| :---- | ----- | :---- | ----- |
| bill\_id |  | A unique number identifying the bill |  |
| session\_id |  | The session the bill was in (typically 77, sometimes in another session, likely a more specific group) |  |
| bill\_number |  | The number of the bill used in legal documents |  |
| status / status description / status\_date |  | A number and description representing the status of the bill, as well as the date this status was updated on |  |
| title |  | The title of the bill |  |
| description |  | A more in depth description of the bill |  |
| committee\_id / committee |  | A number that represents the committee that handled the bill and the name of the committee |  |
| last\_action\_date / last\_action |  | The last action that occurred on the bill (such as passing or sending to a sub-committee) and the date of this action |  |
| url |  | A url to data about the bill, including a pdf of its text |  |
| state\_link |  | A url to information on the bill’s state, including a pdf of its text |  |

### **Consumer\_Confidence\_Index.csv**

This dataset contains the consumer confidence index for each country every month. 

Will process to multi-index by time and country, rather than with separate columns for each country.

| Column Name |  | Description |  |
| :---- | ----- | :---- | ----- |
| Category |  | A timeseries value that increments monthly. Represents the month and year for the data in that row |  |
| \<Countries\> |  | A collection of columns named after countries. These columns contain the consumer confidence index for that country by month. |  |

### **World\_Economic\_Outlook.csv**

This dataset contains economic data for each country by year. Examples of data include GDP, unemployment rates, and population among many other variables. 

Will process to make year into a column as part of a multiindex for simplicity. 

| Column Name |  | Description |  |
| :---- | ----- | :---- | ----- |
| DATASET |  | Represents the dataset this data came from. In this case it is always IMF.RES:WEO(9.0.0). This column exists in case the entire dataset is downloaded. |  |
| SERIES\_CODE |  | Likely represents the country with the first 3 letters and the type of data with the rest. |  |
| OBS\_MEASURE |  | Likely represents the type of data contained in the row, in this case always OBS\_VALUE |  |
| COUNTRY |  | The country the data in the row is for. |  |
| INDICATOR |  | What the data in the row is of (ie. GDP, population, unemployment, etc). |  |
| FREQUENCY |  | The frequency that data is updated (In this case, it is always annually) |  |
| SCALE |  | Values in the rows are not the true value, and are instead multiplied by the scale in scale, such as thousands or millions.  |  |
| \<YEAR\> (1980…2030) |  | Represents the year the data is for |  |

### **Sentiment\_Analysis\_Bills.csv**

This dataset will contain key dates and sentiment analysis for bills. Will be created during data processing stage via webscraping and sentiment analysis.  

*This summary is subject to change*

| Column Name |  | Description |  |
| :---- | ----- | :---- | ----- |
| BILL TITLE |  | Represents the official title of the bill / bill number |  |
| BILL NAME |  | Represents the name of the bill |  |
| INTRODUCED |  | The date the bill was introduced |  |
| RESOLUTION |  | Whether the bill was passed, failed to be passed, or is pending |  |
| RESOLUTION DATE |  | The date of the resolution on the bill |  |
| COUNTRY |  | The country the bill is from |  |
| KEYWORDS |  | A list of keywords about the bill’s connection to the economy, generated via sentiment analysis  |  |

### **All\_data\_FIW\_2013-2025.csv**

This is a dataset including all the freedoms each country has allowed to its people. How free a country is can tell a lot about its political climate and priorities for its own citizens.

| Column Name | Description |
| :---- | :---- |
| Country/Territory | The name of the country that is being analyzed. |
| C/T | The country/territory label |
| Status | Defines how free the government is willing their people to be. Important for defining government priority. |
| PR rating  | Indicates how well a country’s political rights are for its people |
| CL rating | Indicates how well a country’s civil liberties are for its people. |
| A | The electoral process determines a fair political process. |
| C | A rating for how well a government is functioning. |
| D | A rating that determines the freedom of its citizens. |
| G | Indicates how much the citizens’ rights of a country are granted. |
| Total | Aggregates all the categories into one freedom score.  |

## 

## **Dataset Challenges**

The Consumer Confidence Index files had to be downloaded in multiple parts in order to prevent the website from freezing. This was only a minor inconvenience as it will be trivial to remerge the files and remove accidental duplicates.

One dataset consists of data about bills passed in the US, but does not actually contain the content of a bill. Thus, in order to access this data we will need to scrape the bills’ PDFs, accessible from the provided URLs. Combining of data will also be necessary as the datasets are split by congress session.

Finding data on bills passed in countries other than the US proved difficult. The few datasets that were found contained only a very small number of bills, preventing them from being adequately useful. Attempting to locate and access these bills will likely make up part of future steps for this project. 

## **Connections to Research**

| Research Question | Dataset & Columns |  | Notes |  |
| :---- | :---- | ----- | :---- | ----- |
| 2,3,5 (potentially 1 as well) | Consumer\_Confidence\_Index.csv  Columns: all |  | This dataset helps us understand the economic health of a country over the years by providing a summary of the residents’ outlook on that country’s economy. <br> All columns in this dataset are of interest to us, as it simply contains dates, countries, and the consumer confidence index for each country by each date. <br>We will use this as one part of judging the economic health of a country. |  |
| 2,3,5 (potentially 1 as well) | World\_Economic\_Outlook.csv Columns: Country, Indicator, Scale, \<Years\> |  | This dataset provides additional economic indicators and data we can use to judge the economic health of a country. The notable columns provide information on the country the data is for, the scale of the data,  the economic indicator the data is for, and the data for each year. We will use this as one part of judging the economic health of a country. |  |
| 1,2,3,5 (potentially 4 as well) (via other scraping with dataset) | 2009-2010\_111th\_Congress/csv/bills.csv (representative of all congress bill csv files) Columns: status\_desc, status\_date, title, last\_action\_date, last\_action, url, state\_link |  | This dataset provides us with links to information about bills in the U.S. Congress.  Notable columns relate to the bill’s status and the date of these actions, which we can use to plot the impact of the bill chronologically. Also of note are the two url columns, which will provide us access to web pages to scrape for further information and the bill’s full text. This allows us to use it to answer questions related to economic policy. |  |
| 1,2,3,5 (potentially 4 as well) | Sentiment\_Analysis\_Bills Columns: RESOLUTION DATE, KEYWORDS, BILL NAME |  | This dataset contains key info about scraped bills, including sentiment analysis. This will allow us to look at specific portions of policies when performing an analysis.  Keywords of each bill can be helpful to figure out factors considered and factors that led to the impact. The name and dates help figure out the impact and can be categorized into multiple policy types. |  |
| 2, 4 | All\_data\_FIW\_2013-2025.csv Columns: All |  | This dataset contains valuable information about politics, which could highlight the factors that these countries aim to achieve or put in their policies based on their political climate.  Mainly, this is useful for looking at the *political factors* of a nation that impact economic policy-making, such as its political freedom, democracy, and functioning of government that determine the voice in these policies. |  |

# **Challenge Goal Proposal**

1. **Sentiment analysis of laws passed** \- Rather than just analyzing readily available economic data, we will focus on the types of policies as our predictor by analyzing laws using sentiment analysis. This lets us focus more on the *policy* part of our research project.  
2. **API Usage and creating generated Data sets** \- We will likely utilize APIs and/or webscraping to access data related to passed laws, such as the contents of the law (which we will perform sentiment analysis on) and the date it was passed. It is unlikely we will be easily able to find laws in a convenient format, so utilizing APIs or webscraping will help us gather this data.  
3. **Use Machine Learning to create economic policy models** \- To further analyze our data, we will create a machine learning model to help us find less obvious patterns in the data, such as the combined influence of multiple policies or a delayed effect of a certain type of policy. This will allow us to have a better, more in-depth understanding of the patterns we uncover.

