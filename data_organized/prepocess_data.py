'''
This file is intended to do the following types of work:
    * download data from APIs  
    * screenscrape data from websites  
    * reduce the size of large datasets to something more manageable  
    * clean data: reduce/rename columns, normalize strings, adjust values  
    * generate data through relatively complicated calculations   
''' 

import requests
from bs4 import BeautifulSoup
import spacy

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from urllib.parse import urljoin

from transformers import pipeline
from enum import Enum

import io
import os
import sys
import re

from pathlib import Path

import pandas

# Helps mimic humans when webscraping
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng*/*;q=0.8","Accept-Language": "en-US,en;q=0.9","Upgrade-Insecure-Requests": "1"}

# Shared SeleniumBase session for batch scraping — avoids spinning up Chrome once per bill.
# Set by generate_appropriation_txts before looping; None causes _get_legiscan_html to manage its own session.
_shared_sb_session = None


"""
Helper: Locates Playwright's Chromium binary installed on the system by ms-playwright.
Falls back to None, letting SeleniumBase use its own managed driver if not found.
Returns:
    str | None: absolute path to chrome.exe if found, otherwise None
"""
def _find_chromium_binary() -> str:
    import glob
    local_app_data = os.environ.get('LOCALAPPDATA', '')
    pattern = os.path.join(local_app_data, "ms-playwright", "chromium-*", "chrome-win*", "chrome.exe")
    matches = glob.glob(pattern)
    return matches[0] if matches else None

"""
Helper: Navigates to the Legiscan drafts page for a bill URL, waits for Cloudflare/Turnstile
to clear, and returns the fully rendered page HTML along with the active session's cookies
and user-agent string for downstream requests.

If _shared_sb_session is set (by generate_appropriation_txts), it reuses that existing
browser session to avoid Chrome startup costs between bills. Otherwise it manages its own
full session lifecycle.

Args:
    url (str): the full Legiscan bill URL to navigate to
Returns:
    tuple(str, dict, str): (page_html, cookies_dict, user_agent_string)
"""
def _get_legiscan_html(url: str) -> tuple:
    import time
    from seleniumbase import SB

    # The gaits-textlist table (PDF versions) lives on the /drafts/ page, not /bill/
    drafts_url = url.replace("/bill/", "/drafts/")

    def _navigate_and_extract(sb):
        sb.uc_open_with_reconnect(drafts_url, reconnect_time=6)
        # Attempt to handle explicit Turnstile captchas automatically
        try:
            sb.uc_gui_click_captcha()
        except Exception:
            pass
        # Allow JS table to fully render
        time.sleep(5)
        html = sb.get_page_source()
        cookies = {c['name']: c['value'] for c in sb.driver.get_cookies()}
        user_agent = sb.driver.execute_script("return navigator.userAgent;")
        return html, cookies, user_agent

    # Reuse the shared session if available (set by generate_appropriation_txts)
    if _shared_sb_session is not None:
        return _navigate_and_extract(_shared_sb_session)

    # No shared session — manage our own browser lifecycle for single-call usage
    binary = _find_chromium_binary()
    sb_kwargs = dict(uc=True, headless=True)
    if binary:
        sb_kwargs["binary_location"] = binary

    with SB(**sb_kwargs) as sb:
        return _navigate_and_extract(sb)


"""
Helper: Given a dict of {version_label: pdf_url} scraped from the Legiscan drafts table,
returns the URL of the highest-priority version found.

Priority order: Enrolled > Engrossed > Amended > Introduced > first available fallback

Args:
    versions (dict): mapping of version label strings to their PDF href values
Returns:
    str | None: the selected PDF URL, or None if versions is empty
"""
def _pick_priority_pdf(versions: dict) -> str:
    priorities = ["Enrolled", "Engrossed", "Amended", "Introduced"]
    for priority in priorities:
        if priority in versions:
            return versions[priority]
    # Fallback to first available version if none of the priority labels matched
    return list(versions.values())[0] if versions else None


"""
Reads a PDF from a provided US house bill link. Returns the text content of the bill.
Optionally saves the PDF and/or saves the text to a TXT file.

Note: only works for https://legiscan.com/US/bill... links
Attribution: Claude Haiku 4.5 used to rewrite method due to a complex web scraping error with 
             Beautiful Soup 4 inability to read JS script loaders and only initial HTML.
Args:
    url (str): the url of the bill to download
    make_txt (bool): wether or not to save the file to a txt, defaults to false
    keep_pdf (bool): wether or not to keep the created pdf
    folder (str): the folder to save the PDFs and/or TXTs to
Returns:
    str: the scraped text content of the bill
"""
def get_pdf_from_bill_url(url: str, make_txt: bool = False, keep_pdf: bool = False, folder: str = "") -> str:

    try:
        from curl_cffi import requests as cffi_requests

        # Create unique name based on URL, removes "/" and concatenates for full name
        name = url.split("/")[-2] + url.split("/")[-1]

        # Legiscan uses JS to load tables dynamically; use stealth browser to render the page
        html, cookies, user_agent = _get_legiscan_html(url)
        soup = BeautifulSoup(html, "html.parser")

        # Find the JS loaded table
        table = soup.find('table', {'id': 'gaits-textlist'})
        if not table:
            print(f"Error: Could not find 'gaits-textlist' table on rendered page for {url}")
            return ""

        # Find best PDF link (Enrolled > Engrossed > first available)
        versions = {}
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 4:
                version_type = cells[0].get_text(strip=True)
                link_tag = cells[3].find('a', href=True)
                if link_tag:
                    versions[version_type] = link_tag['href']

        # Gets pdf_url from highest priority version available
        pdf_url = _pick_priority_pdf(versions)

        if not pdf_url:
            print(f"Skipping: No PDF link found in table for {url}")
            return ""

        # Resolve relative Legiscan URLs to absolute
        if pdf_url.startswith('/'):
            pdf_url = "https://legiscan.com" + pdf_url

        pdf_text = ""
        # Paths used for storing data, data is largely unprocessed, so it remains in raw_data folder
        pdf_path = "discovery_raw_data/" + folder + "/bills/pdfs/" + name + ".pdf"
        txt_path = "discovery_raw_data/" + folder + "/bills/txts/" + name + ".txt"

        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        if make_txt:
            os.makedirs(os.path.dirname(txt_path), exist_ok=True)

        # Download PDF using curl_cffi, passing the cleared session cookies to bypass
        # Cloudflare's backend API block with a matching JA3/TLS browser fingerprint
        cffi_headers = {
            "User-Agent": user_agent,
            "Referer": "https://legiscan.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        }
        response = cffi_requests.get(pdf_url, headers=cffi_headers, cookies=cookies, impersonate="chrome110")

        if response.status_code != 200 or len(response.content) < 1000:
            print(f"Skipping: Failed to download PDF from {pdf_url} (status={response.status_code})")
            return ""

        # Download and Parse
        with open(pdf_path, "wb+") as temp_pdf:
            temp_pdf.write(response.content)
            temp_pdf.seek(0)

            manager = PDFResourceManager()
            data = io.StringIO()
            converter = TextConverter(manager, data, laparams=LAParams())
            interpretor = PDFPageInterpreter(manager, converter)

            for page in PDFPage.get_pages(temp_pdf):
                interpretor.process_page(page)

            # Use replace for encoding safety
            pdf_text = data.getvalue().encode('utf-8', errors='replace')

            # If txt file is requested, write and save to the path given
            if make_txt:
                with open(txt_path, "wb+") as bill_txt:
                    bill_txt.write(pdf_text)

        if not keep_pdf:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

        # Return as decoded string for NLP processing
        return pdf_text.decode('utf-8', errors='replace')

    # Error handling to find the error name and get print trace (error log)
    except Exception as e:
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        import traceback
        traceback.print_exc()
        return None
# result = get_pdf_from_bill_url(
#     "https://legiscan.com/US/bill/HB1/2025", 
#     make_txt=True,
#     keep_pdf=False,
#     folder="test"
# )
# print(result[:500] if result else "FAILED - returned empty/None")

"""
Calculates the maximum consecutive NA series or gap for a country
Note: This method is used to be applied across a dataframe. 
Attribution: Gemini 3 Flash used to produce the logic of the method
Args:
    column (Series): Used to calculate the max gaps found in data
Return:
    gap (int): A integer value representing the max gap found in the entire country's dataset column
"""
def get_max_gap(column: pandas.Series) -> int:
    # Returns the size of the largest block of NaNs
    return column.isna().astype(int).groupby(column.notna().cumsum()).sum().max()

"""
Interpolates consumer confidence data to prevent statistical errors with NaNs or zero values.
Args: 
    df (dataframe)
Returns: 
    df (dataframe)
"""
def interpolate_Consumer_Confidence(df: pandas.DataFrame) -> pandas.DataFrame:
    # Calculate how many countries have reported
    reporting_countries = df.notna().sum(axis=1)
    
    total_countries = len(df.columns) - 1
    threshold = 0.8 * total_countries
    
    # Uses threshold to calculate start_date when most countries are listed in data
    start_date = (reporting_countries[reporting_countries >= threshold].index)[0]
    df = df.loc[start_date:]

    # Calculate gap to drop countries with extreme gaps prevent interpolation scewing
    # Gaps of more than 6 months are HUGE, the avg. time(6-12 months) for economic policy effects
    gap_report = df.apply(get_max_gap)
    gaps = (gap_report[gap_report > 6].index).tolist()

    # Drops any countries with major gaps in data
    df = df.drop(columns=gaps, errors="ignore")

    # Interpolation
    df_final = df.interpolate(method='linear', limit=3, limit_area='inside')

    # Testing Gaps
    # gap_report = df_final.apply(get_max_gap)
    # print(gap_report[gap_report > 6].index)
    
    return df_final

"""
Creates a dataset that is merged and interpolated for processing uses.
Returns:
    DataFrame: the merged consumer confidence index that is interpolated and
        converted to use date-time
"""
def original_consumer_confidence() -> pandas.DataFrame:
    # Locations of the two halves
    part_1 = pandas.read_csv("discovery_raw_data/Consumer_Confidence_Index/export-2026-02-09T18_18_53.225Z.csv")
    part_2 = pandas.read_csv("discovery_raw_data/Consumer_Confidence_Index/export-2026-02-09T18_32_51.587Z.csv")

    # Category (year) and Luxembourg are in both datasets
    merged = part_1.merge(part_2, on=["Category", "Luxembourg"])
    consumer_confidence = merged.rename(columns={"Category" : "Date"})

    # Converting date to timeseries for interpolation
    consumer_confidence["Date"] = pandas.to_datetime(consumer_confidence["Date"])
    consumer_confidence = consumer_confidence.set_index("Date")
    consumer_confidence = interpolate_Consumer_Confidence(consumer_confidence)

    # Save merged to csv, when it becomes csv there is no time series
    # Important to have indices as columnn in csv, for usage by other methods
    # consumer_confidence.to_csv("data_organized/Consumer_Confidence_Index.csv")
    return consumer_confidence

# Already Processed consumer_confidence so it is commented.
#original_consumer_confidence()

"""
Joins the two halves of the consumer confidence index data set and reorganizes the data.
Saves two CSVs, one with date as the column and another with date as the row. Also converts
years to TimeSeries values
"""
def preprocess_Consumer_Confidence() -> None:

    consumer_confidence = original_consumer_confidence()
    #dates = consumer_confidence["Date"].to_list()
    consumer_confidence = consumer_confidence.loc[:, "Estonia" : "China"]

    # Switches rows and columns to make dates to columns instead of being countries
    consumer_confidence = consumer_confidence.transpose()

    # The Date was a column in the previous code
    #consumer_confidence.columns = dates 
    consumer_confidence.to_csv("data_organized/transposed_Consumer_Confidence_Index.csv")


"""
Filters World Economic Outlook data to only be for US (country of focus).
Saves output to a new CSV
"""
def preprocess_World_Economic_Outlook() -> None:
    # Interpolation not needed, will use more precise dataset that includes monthly indicators(vital to "short-term" analysis)
    economic_outlook = pandas.read_csv("discovery_raw_data/World_Economic_Outlook.csv")
    united_states = economic_outlook["COUNTRY"] == "United States"
    united_states_outlook = economic_outlook[united_states]
    united_states_outlook.to_csv("data_organized/united_states_outlook.csv", index=False)

# Processed both consumer_confidence/economic outlook
#preprocess_Consumer_Confidence()
#preprocess_World_Economic_Outlook()


""""
Process all passed bills, creating a dataset of Bill ID, name, date, a url to the text, and a description
"""
def process_bills() -> pandas.DataFrame:
    # Get all subfolders (congress sessions) in the folder
    sessions = [ f.path for f in os.scandir("discovery_raw_data/Congress/US/") if f.is_dir() ]

    # Output will have the bill ID, name, date of the last action, and its status
    out = pandas.DataFrame(columns=["Bill ID", "Bill Name", "Date"])

    for session in sessions:
        
        # Get the data for one session
        session = pandas.read_csv(session + "/csv/bills.csv")

        # Only look at passed appropriations bills
        session = session[session['status_desc'] == "Passed"]
        session_important_data = pandas.DataFrame()

        # Gets important infor the transfer over
        # URL and/or description will be converted to keywords
        session_important_data["Bill ID"] = session["bill_number"]
        session_important_data["Bill Name"] = session["title"]
        session_important_data["Date"] = session["status_date"]
        # Note: When reprocessing csv it is important to handle this step for potential missing values for keywords
        session_important_data["url"] = session["url"]
        session_important_data["short_description"] = session["description"]

        # Append important data for all sessions
        out = pandas.concat([out, session_important_data])

    # Index must be false to avoid extra index column
    # out.to_csv("data_organized/bills.csv", index=False) 
    return out


#process_bills()

"""
Saves all passed bills relating to appropriations
"""
def organize_appropriations() -> None:
    # Get all passed bills
    bills = process_bills()
    # Filter for only appropriations bills
    appropriations = bills[bills["Bill Name"].str.contains("Appropriations")]
    appropriations.to_csv("data_organized/appropriations.csv", index=False)

# Processed dataset
#organize_appropriations()

"""
Reads all bills from the list of urls, downloading a TXT file for each url.

Opens a single SeleniumBase browser session shared across all bill requests to avoid
Chrome startup overhead on every call — saving ~4s per bill for large batches.

Args:
    urls (list[str]): the urls to download texts for 
"""
def generate_bills_txts(urls: list[str], folder: str) -> None:
    global _shared_sb_session
    import time
    from seleniumbase import SB

    binary = _find_chromium_binary()
    sb_kwargs = dict(uc=True, headless=True)
    if binary:
        sb_kwargs["binary_location"] = binary

    with SB(**sb_kwargs) as sb:
        _shared_sb_session = sb
        try:
            for url in urls:
                get_pdf_from_bill_url(url, make_txt=True, keep_pdf=False, folder=folder)
        finally:
            # Always clear the shared session, even if an error occurs mid-batch
            _shared_sb_session = None

"""
A class used when picking the classifier mode
"""
class ClassifyMode(Enum):
    VERBOSE = 0
    LONG = 1
    BOTH = 2

    DESCRIPTION = 0
    TEXT = 1


"""
Code for one catagorizaiton by Gemini, slight modifications by me

Classifies how well categories fit a piece of text

Args:
    text_to_classify (str): the text to be classified
    labels (list[str]): a list of categories in the form of strings
    print_output (bool): used for debugging. wether or not to print the scores while running
    key_extension (str): a string appended to the end of the keys, used when catagorize_bills is
        running in BOTH mode
Returns:
    dict{str : float}: a dictionary containing all passed labels and a number representing how well
        the document fits that label. The dictionary is sorted so keys are in alphabetical order
"""
# ── Developer GPU toggle ─────────────────────────────────────────────────────
# None  → auto-detect: uses CUDA GPU if available, otherwise falls back to CPU
# True  → always use GPU (raises an error if CUDA is not available)
# False → always use CPU
USE_GPU = None

def _get_device() -> int:
    """Returns the device index for HuggingFace pipelines (0 = first GPU, -1 = CPU)."""
    import torch
    if USE_GPU is None:
        device = 0 if torch.cuda.is_available() else -1
    else:
        device = 0 if USE_GPU else -1
    
    device_name = f"GPU (CUDA device: {device})" if device >= 0 else "CPU"
    print(f"Classification pipeline using device: {device_name}")
    return device

# Module-level singleton — loaded once on first use, reused for all subsequent calls.
_classifier_pipeline = None

def _get_classifier():
    """Returns the shared zero-shot classification pipeline, initializing it on first call.
    On GPU, runs a small warm-up inference to pre-compile CUDA kernels so the first
    real document doesn't pay the JIT compilation penalty (~3 minutes).
    """
    global _classifier_pipeline
    if _classifier_pipeline is None:
        device = _get_device()
        
        # Smart Model Selection based on Compute Power
        if device >= 0:
            # For GPU: High performance, highly accurate model
            import torch
            model_id = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0"
            pipeline_kwargs = {"dtype": torch.float16}
        else:
            # For CPU: Reliable and familiar model
            model_id = "facebook/bart-large-mnli"
            print(f"CPU detected: Loading standard fallback model for accuracy -> {model_id}")
            # Disable low_cpu_mem_usage to prevent HuggingFace's default two-pass
            # weight loading (skeleton allocation + value fill), which causes the
            # visible "Loading weights" bar to appear twice on CPU.
            pipeline_kwargs = {"model_kwargs": {"low_cpu_mem_usage": False}}

        _classifier_pipeline = pipeline(
            "zero-shot-classification",
            model=model_id,
            device=device,
            **pipeline_kwargs
        )

    return _classifier_pipeline


_embedding_model = None

def _get_embedding_model():
    """Returns the shared sentence-transformer embedding model for lightning-fast CPU classification."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        print(f"Loading lightning-fast embedding model for CPU -> sentence-transformers/all-MiniLM-L6-v2")
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    return _embedding_model

def classify_fast_embeddings(text_to_classify: str, labels: list[str], print_output: bool = False, key_extension: str = '') -> dict[str, float]:
    """Classifies text using Cosine Similarity on embeddings instead of NLI, running in O(N) instead of O(N*M)."""
    from sentence_transformers import util
    
    model = _get_embedding_model()
    chunks = chunk_text(text_to_classify)
    print(f"\n[CPU] Processing {len(chunks)} text chunks for classification...")
    
    # Calculate vector representation of our labels
    label_embeddings = model.encode(labels, convert_to_tensor=True, show_progress_bar=False)
    
    aggregated = {label: 0.0 for label in labels}
    
    if not chunks or not chunks[0]:
        return {label + key_extension: 0.0 for label in labels}
        
    # Calculate vector representations of our text chunks
    chunk_embeddings = model.encode(chunks, convert_to_tensor=True, show_progress_bar=True)
    
    # Calculate cosine similarity matrix (chunks x labels)
    cosine_scores = util.cos_sim(chunk_embeddings, label_embeddings)
    
    # Average the scores across all chunks
    for i in range(len(chunks)):
        for j, label in enumerate(labels):
            # Clamp scores so they act like percentages (0 to 1) instead of cosine (-1 to 1)
            score = float(cosine_scores[i][j])
            score = max(0.0, score) 
            aggregated[label] += score
            
    scores = {label + key_extension: aggregated[label] / len(chunks) for label in labels}

    if print_output:
        for label, score in scores.items():
            print(f"{label}: {score:.4f}")
            
    return dict(sorted(scores.items()))


def chunk_text(text: str, max_words: int = 400) -> list[str]:
    """Splits a string into chunks of max_words to fit within the model's context limit."""
    if not isinstance(text, str) or not text.strip():
        return [""]
    words = text.split()
    return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]


def classify(text_to_classify: str, labels: list[str], print_output: bool = False, key_extension: str = '') -> dict[str, float]:
    if _get_device() < 0:
        return classify_fast_embeddings(text_to_classify, labels, print_output, key_extension)
        
    from tqdm import tqdm
    chunks = chunk_text(text_to_classify)
    print(f"\n[GPU] Processing {len(chunks)} text chunks for classification...")
    
    if len(chunks) <= 1:
        result = _get_classifier()(chunks[0], labels)
        scores = {label + key_extension: score for label, score in zip(result['labels'], result['scores'])}
    else:
        # Feed the entire list of chunks directly to the pipeline. Zero-shot 
        # internally batches this without blocking sequential GPU cycles.
        classifier = _get_classifier()
        results = classifier(chunks, labels, batch_size=8)

        # Aggregate scores across chunks
        aggregated = {label: 0.0 for label in labels}
        for res in results:
            for label, score in zip(res['labels'], res['scores']):
                aggregated[label] += score
                
        # Average the classification scores across all chunks
        scores = {label + key_extension: aggregated[label] / len(chunks) for label in labels}

    # used for debugging
    if print_output:
        for label, score in scores.items():
            print(f"{label}: {score:.4f}")
            
    return dict(sorted(scores.items()))


"""
A test method used to ensure the catagorize_bills method
works correctly, without taking ages actually classifying
the texts. 

Args:
    labels (list[str]): a list of categories in the form of strings
    key_extension (str): a string appended to the end of the keys, used when catagorize_bills is
        running in BOTH mode
Returns:
    dict{str : float}: a dictionary containing all passed labels and a number representing 
        that key's index in the input. The dictionary is sorted so keys are in alphabetical order.
        Ex: ['B', 'C', 'A'] -> {'A':2, 'B':0, 'C':1}  
"""
def test_dict(labels: list[str], key_extension: str = '') -> dict[str: float]:
    d =  {labels[i] + key_extension: i for i in range(len(labels))}
    return dict(sorted(d.items()))


"""
Catagorizes bills into provided catagories and scores how well each bill fits

WARNING: MAY BE VERY SLOW TO RUN - it is advised that for testing new labels, you start with a 
small portion of the full dataset

Please ensure bills_df contains at least 2 rows of data

Args:
    bills_df (DataFrame): the input DataFrame. Requires a column labeled 'short_description' when in 'verbose' mode,
        or a url column when not. 
    labels (list[str]): a list of categories in the form of strings
    test (bool): wether or not the method should run in test mode, replacing actual scores with test values generated
        with the test_dict method
    mode (int) the mode to run in. it is recomended to use the enum values from ClassifyMode class for clarity. Verbose uses just bill description from the dataset,
        Long uses scraped bill text, and Both uses both of those methods
    debug (bool): wether or not the method should print at key points for debugging purposes
Returns:
    DataFrame: returns bills_df modified to contain columns for each label, with each bills fit score for those labels.
    Saves the returned DataFrame to 'data_organized/catagorized_bills.csv'
"""
def catagorize_bills(bills_df: pandas.DataFrame, labels: list[str], test: bool = False, mode: int = ClassifyMode.VERBOSE, debug: bool = False) -> pandas.DataFrame:

    # alphabetize labels
    l = list(sorted(labels))

    # when catagorizing with both, create two columns per label
    if mode == ClassifyMode.BOTH:
        l = [str(label) + "_description" for label in labels]
        l.extend([str(label) + "_full text" for label in labels])
    
    if debug:
        print("Labels: " + str(l))

    # TODO: update to handle single row bills_df?

    # run with test values in test mode, otherwise actually classify the bills
    # if running in verbose or both, use short_desctription column
    # if running in long or both, use webscraped txts
    from tqdm import tqdm
    if test:
        if mode == ClassifyMode.VERBOSE:
            scores = [test_dict(labels) for ignore in bills_df["short_description"]]
        elif mode == ClassifyMode.LONG:
            scores = [test_dict(labels) for ignore in bills_df["url"]]
        elif mode == ClassifyMode.BOTH:
            scores_description = [test_dict(labels, "_description") for ignore in bills_df["short_description"]]
            scores_text = [test_dict(labels, "_full text") for ignore in bills_df["url"]]
            scores = [{**score_description, **score_text} for score_description, score_text in zip(scores_description, scores_text)]
    else:
        if mode == ClassifyMode.VERBOSE:
            scores = [classify(description, labels, debug) for description in tqdm(bills_df["short_description"], desc="Classifying Descriptions")]
        elif mode == ClassifyMode.LONG:
            # Derive file paths from the DataFrame's url column using the same naming
            # logic as get_pdf_from_bill_url, so only the correct files are read in
            # DataFrame row order. classify() handles chunking internally so the full
            # text of each bill is evaluated correctly regardless of its length.
            txt_dir = Path("discovery_raw_data/appropriations/bills/txts")
            scores = []
            for url in tqdm(bills_df["url"], desc="Classifying Bills"):
                name = url.split("/")[-2] + url.split("/")[-1]
                txt_path = txt_dir / (name + ".txt")
                with open(txt_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                scores.append(classify(text, labels, debug))
        elif mode == ClassifyMode.BOTH:
            scores_description = [classify(description, labels, debug, "_description") for description in tqdm(bills_df["short_description"], desc="Classifying Descriptions")]
            scores_text = [classify(get_pdf_from_bill_url(url), labels, debug, "_full text") for url in tqdm(bills_df["url"], desc="Classifying Bills")]
            scores = [{**score_description, **score_text} for score_description, score_text in zip(scores_description, scores_text)]


    if debug:
        print("Scores: " + str(scores))

    # adds a new column for each label
    for label in l:
        bills_df[label] = [score[label] for score in scores]

    
    if debug:
        print("Output: " + str(bills_df))
    
    # save and return dataframe
    bills_df.to_csv("data_organized/appropriations_catagorized.csv")
    return bills_df
    

"""
Runs all preprocess methods

catagorize_bills not run here due to time requirements. 
Run catagorize_bills after this method if needed
"""
def main() -> None:
    organize_appropriations()
    preprocess_World_Economic_Outlook()
    preprocess_Consumer_Confidence()
    # Takes long time to run(approx. 30 min) (run the tests below to figure out how long it takes)
    # Web Scraped texts and are processed to text, put into raw data due to their unprocessed state
    # appropriations = pandas.read_csv("data_organized/appropriations.csv")
    # url_links = appropriations["url"].to_list()
    # generate_bills_txts(url_links, "appropriations")


"""----------------------------------------------------------------------------------"""
"""CODE IN THIS BLOCK SHOULD BE RUN TO PROCESS DATA"""

main()

labels = ["Education", "Military", "Infrastructure", "Science", "Domestic Aid", "Foreign Aid"]

# test method
#catagorize_bills(pandas.read_csv("data_organized/appropriations.csv").loc[0:1, :], labels, mode=ClassifyMode.LONG, debug=True)

# uncomment to run catagorization. WARNING: RUNTIME IS LONG
#catagorize_bills(pandas.read_csv("data_organized/appropriations.csv"), labels, debug=True, mode=ClassifyMode.LONG)

"""----------------------------------------------------------------------------------"""

#import time

# # # ── Test 1: single standalone call (non-shared session) ──────────────────────
# print("\n=== TEST 1: Single bill (standalone session) ===")
# t0 = time.time()
# result = get_pdf_from_bill_url(
#     "https://legiscan.com/US/bill/HB1/2025",
#     make_txt=True, keep_pdf=False, folder="test_single"
# )
# t1 = time.time()
# print(f"Time: {t1 - t0:.1f}s")
# print(result[:200] if result else "FAILED")

# ── Test 2: 3-bill batch (shared session) ────────────────────────────────────
# print("\n=== TEST 2: 3 bills (shared session) ===")
# test_urls = [
#     "https://legiscan.com/US/bill/HB1/2025",
#     "https://legiscan.com/US/bill/HB30/2009",  
#     "https://legiscan.com/US/bill/HB24/2009",
# ]
# t2 = time.time()
# generate_txts(test_urls, "test_batch")
# t3 = time.time()
# print(f"Total time for 3 bills: {t3 - t2:.1f}s")
# print(f"Avg per bill: {(t3 - t2) / 3:.1f}s")
