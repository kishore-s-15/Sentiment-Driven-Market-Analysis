# CS 5100 Foundations of Artificial Intelligence - Final Project
# Sentiment Driven Market Analysis

## Abstract

The efficient-market hypothesis in financial eco nomics states that asset prices reflect all available information.
With the advent of large language models, it is possible to leverage information sources such as news headlines and
social media feeds to get new metrics like prevailing public sentiment scores. Along with historic market data, this
project aims to use these new metrics to build prescriptive models which will be able to outperform existing stock
investment strategies. Models such as these can be a valuable tool for making informed and proactive investment decisions.

## Project Directory Structure

```
  ├── Sentiment Driven Market Analysis      # Root Folder
    ├── data/                               # Folder contains the datasets used in the project
        ├── fai_project_data.csv                             # Dataset which consists of the historical stock price and the news data combined.
        ├── financial_data.db                                # SQLITE database consisting of the news data for the tech stocks which is used to train the autoregressive model.
        ├── IndianFinancialNews.csv                          # Indian Financial News dataset used for training the sentiment analyzer model.
        ├── merged.csv                                       # Indian Financial News and Sensex historical prices combined dataset.
        ├── Sensex_historical_price.csv                      # Sensex Price dataset for training the sentiment analyzer model.
    ├── src/                                                 # Folder contains the source code of the project
        ├── data-collator.ipynb                              # Jupyter Notebook file which consists of the codes for collating the historical stock prices and the news data.
        ├── eda-and-naive-forecaster.ipynb                   # Jupyter Notebook file consists of the code for performing Exploratory Data Analysis on the stock data and fit a naive forecaster on it.
        ├── multivariate-time-series.ipynb                   # Jupyter Notebook file consists of the training and inference code of the Multivariate timeseries models.
        ├── sentiment-models.ipynb                           # Jupyter Notebook file consists of the code for training a sentiment analyzer.
        ├── webscraper.py                                    # Python script consists of the code for scraping the news data.
    ├── .gitignore                          # Python gitgnore file
    ├── custom_nlp1_std_scaler.bin          # Serialized Scaler of the custom Sentiment Analyzer model.
    ├── custom_nlp1.keras                   # Serialized custom Sentiment Analyzer model.
    ├── requirements.txt                    # Python requirements file which specifies the library dependencies.
    ├── README.md                           # Project README file.
```


## Installation

### TODO: Change Data directory accordingly

1. Clone the repository into a folder and open a terminal of your choice.

2. Create a virtual environment
```
python -m venv .venv (or) python3 -m venv .venv
```

3. Activate the virtual environment

   > On Windows run
   ```
   .venv\Scripts\activate.bat
   ```
   
   > On Linux and MacOs run
   ```
   source .venv/bin/activate
   ```
   
4. Install the dependencies for the project in the virtual environment
```
pip install -r requirements.txt
```
   
5. Then run the following command
```
jupyter notebook
```

## Team Members

[Kishore Sampath](mailto:sampath.ki@northeastern.edu), [Anudeep Ragata](mailto:ragata.s@northeastern.edu), [Kumar Prakhar](mailto:prakhar.k@northeastern.edu), [Deepansh Gandhi](mailto:gandhi.dee@northeastern.edu)