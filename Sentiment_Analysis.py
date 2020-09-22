from flair.models import TextClassifier
from flair.data import Sentence
from twitterscraper import query_tweets
import datetime as dt
import pandas as pd
import csv

def analyze(tweet):
    if type(tweet) != str:
        raise ValueError('The argument passed is not a string! ')
    else:
        tagger = TextClassifier.load('sentiment')
        sentence = Sentence(tweet)
        tagger.predict(sentence)
        return sentence.labels

def get_tweets(ticker, start, today):
    if type(ticker) != str:
        raise ValueError('The argument passed is not a string! ')
    else:
        start = start.split('/')
        s_month = int(start[0])
        s_date = int(start[1])
        s_year = int(start[2])
        begin_date = dt.date(s_year, s_month, s_date)

        today = today.split('/')
        month = int(today[0])
        date = int(today[1])
        year = int(today[2])
        end_date = dt.date(year, month, date)

        limit = 100
        lang = 'english'

        scope1 = ticker + ' value'
        tweets1 = query_tweets(scope1, begindate=begin_date, enddate=end_date, limit=limit, lang=lang)
        scope2 = 'forecasts on ' + ticker
        tweets2 = query_tweets(scope2, begindate=begin_date, enddate=end_date, limit=limit, lang=lang)
        scope3 = ticker + ' performance'
        tweets3 = query_tweets(scope3, begindate=begin_date, enddate=end_date, limit=limit, lang=lang)

        df1 = pd.DataFrame(t.__dict__ for t in tweets1)
        df2 = pd.DataFrame(t.__dict__ for t in tweets2)
        df3 = pd.DataFrame(t.__dict__ for t in tweets3)

        df1_results = {}
        df2_results = {}
        df3_results = {}

        for t in df1['text']:
            score = analyze(t)
            df1_results[t] = str(score[0])
        for t in df2['text']:
            score = analyze(t)
            df2_results[t] = str(score[0])
        for t in df3['text']:
            score = analyze(t)
            df3_results[t] = str(score[0])

#Figure out the overall number of +s and -s in the dfs.
        ns = [0, 0, 0]
        ps = [0, 0, 0]
        for s in df1_results:
            if 'NEGATIVE' in df1_results[s]:
                ns[0] += 1
            elif 'POSITIVE' in df1_results[s]:
                ps[0] += 1

        for s in df2_results:
            if 'NEGATIVE' in df2_results[s]:
                ns[1] += 1
            elif 'POSITIVE' in df2_results[s]:
                ps[1] += 1

        for s in df3_results:
            if 'NEGATIVE' in df3_results[s]:
                ns[2] += 1
            elif 'POSITIVE' in df3_results[s]:
                ps[2] += 1
#calculate the overall positive and negative rates
        nt1 = (ns[0]/len(df1_results))*100
        nt2 = (ns[1]/len(df2_results))*100
        nt3 = (ns[2]/len(df3_results))*100

        pt1 = (ps[0]/len(df1_results))*100
        pt2 = (ps[1]/len(df2_results))*100
        pt3 = (ps[2]/len(df3_results))*100

        print("For the twitter search '", scope1, "':\n", str(nt1)+'% had a negative connotation; ', str(pt1)+'% had a positive connotation.')
        print("For the twitter search '", scope2, "':\n", str(nt2) + '% had a negative connotation; ',
              str(pt2) + '% had a positive connotation.')
        print("For the twitter search '", scope3, "':\n", str(nt3) + '% had a negative connotation; ',
              str(pt3) + '% had a positive connotation.')

        # csv_columns = ['Tweet', 'Score']
        # csv_file = ticker + "Scope1.csv"
        # try:
        #     with open(csv_file, 'w') as csvfile:
        #         writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        #         writer.writeheader()
        #         for data in df1_results:
        #             writer.writerow(data)
        # except IOError:
        #     print("I/O error")
        #
        # csv_file = ticker + "Scope2.csv"
        # try:
        #     with open(csv_file, 'w') as csvfile:
        #         writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        #         writer.writeheader()
        #         for data in df2_results:
        #             writer.writerow(data)
        # except IOError:
        #     print("I/O error")
        #
        # csv_file = ticker + "Scope3.csv"
        # try:
        #     with open(csv_file, 'w') as csvfile:
        #         writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        #         writer.writeheader()
        #         for data in df3_results:
        #             writer.writerow(data)
        # except IOError:
        #     print("I/O error")
        #
        # print('The individual tweets and scores are saved to CSV files. ')



