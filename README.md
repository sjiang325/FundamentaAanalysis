# FundamentaAanalysis
**Requirement**: flair, PyTorch, beautifulsoup4, and twitterscraper, with modification needed(explained below)

**FinancialData.py**:
Enter a ticker. The program will evaluate the efficiency and manipulation of a given company. 
You can also choose to view the dataframe or to see the completed report. A sentiment analysis could be done in the end.

**Sentiment_Analysis.py**:

*analyze(tweet)* 
- kind of self-explanatory: it takes a tweet object and determines the positive/negative connotation of the tweet, returns a label object.

*get_tweets(ticker, start, today)* 
- the function that FinancialData.py calls to perform a sentiment analysis on the given company. At the current stage, it calculates the average "label" of all tweets being processed and prints an average. The original design is for this function to write .csv files so that tweets processed and corresponding scores could be saved locally. Those codes are commented out for now, as they produce a Win32 Access Denial error. 
- By default, the function queries three kinds of hashtags/contents: company value, forecast of company, and company performance(where "company" is substituted with the "ticker" passed in FinancialData.py. The default number of tweets processed is 25 per hashtag/content. This can be changed by modifying the limit variable in line 34. One caveat: the more you process, the longer it takes. When limit=100, it takes 23 minutes to analyze all tweets. 

**Modifications needed**: 
- Besure to run as an administrator! 

- twitterscraper/query.py: Twitter banned front-page queries in late August, please refer to the following link for necessary modifications: https://github.com/taspinar/twitterscraper/pull/337/commits/2233682b3c04840531a94ba8ee3c3325d7bf6b4a

- flair/models/text_classification_model.py: transformers 3.1 would corrupt the trained model used in text-classification; a new model needs to be loaded by fixing some lines:
https://github.com/flairNLP/flair/commit/0a6e8161d99a1ef0962f885ff9a860ebfa79b975

**QuantRisk Modules**:
- After picking the "right" stocks, the QuantRisk notebook could calculate portfolio, benchmark, and active risks, with each risk breaking into systematic and unsystematic parts. 

- All data are from Yahoo finance and Ken French's website. 

- Use the PortfolioHoldings sheet to enter holdings and weights.
