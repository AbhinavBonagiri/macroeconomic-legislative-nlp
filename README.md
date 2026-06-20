# IDP Final Project 2025-26

**Authors:** Jack Trepp & Abhinav Bonagiri  
**Course:** Intermediate Data Programming (IDP)  

## Project Overview
This project investigates **how economic policies affect the economic health of a country** by analyzing legislative bills, economic indicators, and sentiment analysis. We combine data from multiple sources, including US Congressional bills, global economic indicators, consumer confidence indices, and political freedom data to identify patterns, correlations, and predictive relationships between policy implementation and economic outcomes.

### Key Focus Areas:
- **Policy Impact Analysis**: Understanding the relationship between legislative actions and economic health
- **Temporal Patterns**: Identifying lag effects and implementation timelines
- **Comparative Analysis**: Examining how policy effectiveness varies by country size and political climate
- **Data Integration**: Combining legislative, economic, and political data for holistic insights

## Research Questions

**1. How often are each type of policy used, and is there any relationship we can find in their usage?**

Identifying trends in the implementation of different policy types to help understand the impact of those policies, which can be done by understanding what typically occurs before a certain type of policy is implemented, such as the state of the economy.

**2. What are the influential factors that determine the impact the policy has on the “economic health” of the country?**

Policies are usually implemented in a systematic manner, and we can identify these patterns by identifying similar attributes across different policies. By breaking policies down into these attributes, we can determine which parts of an economic policy have the largest impact, as well as trends and relationships between these parts, such as one part only being effective when combined with another. We can also determine if certain policies are only effective when the economy is acting or trending a certain way.

**5. How long does it take for a policy to take effect, if not at all?**

Some policies may not result in an immediate impact on the economy, such as being delayed or never occur, which may hurt the economy instead of helping it. By looking for trends in the implementation of a policy and the delayed impact on the economy, we can identify how much the policy lags behind the current health of the economy.

### Extra Questions:

**3. How does the impact of economic policies vary by the size of a country?**

Certain policies may be more effective for smaller countries or only viable for larger countries to implement. By looking at correlations between the number of people in a country and the effectiveness of certain policies, we can better find which policies work at which scales.

**4. How does the “political climate” of a country affect its economic health?**

The political climate of a country determines what policies it will take for the benefit of the public, economy, or companies. Depending on what the country prioritizes, it will be shown in the impact on the long-term data.

## Challenges

**1. Sentiment analysis of laws passed**

Rather than just analyzing readily available economic data, we will focus on the types of policies as our predictor by analyzing laws using sentiment analysis. This lets us focus more on the policy part of our research project.

**2. API Usage and creating generated Data sets**

We will likely utilize APIs and/or webscraping to access data related to passed laws, such as the contents of the law (which we will perform sentiment analysis on) and the date it was passed. It is unlikely we will be easily able to find laws in a convenient format, so utilizing APIs or webscraping will help us gather this data.

**3. Use Machine Learning to create economic policy models**

To further analyze our data, we will create a machine learning model to help us find less obvious patterns in the data, such as the combined influence of multiple policies or a delayed effect of a certain type of policy. This will allow us to have a better, more in-depth understanding of the patterns we uncover.

---

## Quick Start
### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)
- git
  
1. Clone the repository:
   ```bash
   git clone https://github.com/NCHS-CS/idp-final-project-25-26-jackt-abhinavb.git
   cd idp-final-project-25-26-jackt-abhinavb
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required dependencies(also included in other README.md):
   ```bash
   pip install -r requirements.txt
   ```

4. Start exploring:
   - Begin in discovery_raw_data/ to understand the datasets
   - Run python data_organized/preprocess.py to clean and organize data
   - Run python final_report/create_plots.py to generate visualizations

# Project File Structure
```
idp-final-project-25-26-jackt-abhinavb/
├── README.md                     # You are here
├── discovery_raw_data/           # Phase 1: Raw data & research questions
│   ├── README.md
│   ├── discovery.md              # Detailed discovery document
│   └── [raw datasets]            # Original unprocessed data
│
├── data_organized/               # Phase 2: Cleaned & processed data
│   ├── README.md                 # Data preprocessing instructions
│   ├── preprocess.py             # RUN THIS to clean/organize data
│   ├── sketches/                 # Hand-drawn plot sketches
│   │   └── README.md
│   ├── test_data/                # Small test datasets for validation
│   │   └── README.md
│   └── [organized .csv files]    # Output: cleaned datasets
│
└── final_report/                 # Phase 3: Analysis & visualizations
    ├── README.md                 # Plot documentation & findings
    ├── final.md                  # Written research report
    ├── create_plots.py           # RUN THIS to generate all plots
    └── plots/                    # Generated visualization images
```


