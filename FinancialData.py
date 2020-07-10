from bs4 import BeautifulSoup
import requests
import pandas as pd

def basicInfo(ticker, type):
    if type != 'df' and type != 'd':
        raise ValueError('Invalid type argument!')

    try:
        is_link = f'https://www.marketwatch.com/investing/stock/{ticker}/financials'
        bs_link = f'https://www.marketwatch.com/investing/stock/{ticker}/financials/balance-sheet'
        cf_link = f'https://www.marketwatch.com/investing/stock/{ticker}/financials/cash-flow'
        # Getting source objects from target website(MarketWatch)
        # Cash flow is not used now. I plan to use it in valuation in the future
        is_src = BeautifulSoup(requests.get(is_link).text, 'lxml')
        bs_src = BeautifulSoup(requests.get(bs_link).text, 'lxml')
        cf_src = BeautifulSoup(requests.get(cf_link).text, 'lxml')

    except:
        raise ValueError('Invalid ticker!')

    #Getting titles of rows in the income statement, including the time scope
    is_titles = is_src.find_all('td', class_='rowTitle')
    scope_src = is_src.find('tr', class_='topRow')
    scope = [th.text for th in scope_src.findChildren(attrs={'scope': 'col'}) if len(th.text) == 4]


    #Iterate through rows of the income statement, getting desired contents
    info = {}
    for title in is_titles:
        if title.text == ' EPS (Basic)':
            info['EPS (Basic)'] = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]
        if 'Net Income' in title.text:
            info['Net Income'] = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]
        if title.text == ' Interest Expense':
            info['Interest Expense'] = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]
        if title.text == ' EBITDA':
            info['EBITDA'] = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]
        if title.text == "EBIT after Unusual Expense":
            info['EBIT(after unusual expense)'] = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]

    #Iterate through the balance sheet
    bs_titles = bs_src.find_all('td', class_='rowTitle')
    for title in bs_titles:
        if title.text == " Total Shareholders' Equity":
            info['Total Shareholders\' Equity'] = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]
        if 'Long-Term Debt' in title.text:
            info['Long-Term Debt'] = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]
        if title.text == ' Total Assets':
            info['Total Assets'] = [td.text for td in title.findNextSiblings(attrs={'class': 'valueCell'}) if td.text]

    #Calculate ROE, taking note that the unit might be in millions for some entries/companies
    info['ROE %'] = []
    for n in range(0, len(info['Interest Expense'])):
        if 'M' in info['Net Income'][n] and 'M' not in info['Total Shareholders\' Equity'][n]:
            info['ROE %'].append(
                (float(info['Net Income'][n].strip('BM'))/1000) /
                float(info['Total Shareholders\' Equity'][n].strip('BM')) * 100)
        elif 'M' in info['Total Shareholders\' Equity'][n] and 'M' not in info['Net Income'][n]:
            info['ROE %'].append(
                float(info['Net Income'][n].strip('BM')) /
                (float(info['Total Shareholders\' Equity'][n].strip('BM'))/1000) * 100)
        else:
            info['ROE %'].append(float(info['Net Income'][n].strip('BM')) / float(info['Total Shareholders\' Equity'][n].strip('BM')) * 100)

    info['ROA %'] = []
    for n in range(0, len(info['Total Assets'])):
        if 'M' in info['Net Income'][n] and 'M' not in info['Total Assets'][n]:
            info['ROA %'].append(
                (float(info['Net Income'][n].strip('BM')) / 1000) /
                float(info['Total Assets'][n].strip('BM')) * 100)
        elif 'M' in info['Total Assets'][n] and 'M' not in info['Net Income'][n]:
            info['ROA %'].append(
                float(info['Net Income'][n].strip('BM')) /
                (float(info['Total Assets'][n].strip('BM')) / 1000) * 100)
        else:
            info['ROA %'].append(float(info['Net Income'][n].strip('BM')) / float(info['Total Assets'][n].strip('BM')) * 100)
    info['Interest Coverage Ratio'] = []

    for n in range(0, len(info['EBIT(after unusual expense)'])):
        #EBIT needs to be recaculated
        if info['EBIT(after unusual expense)'][n] == '-':
            info['Interest Coverage Ratio'].append('Unavailable')
        elif 'M' in info['EBIT(after unusual expense)'][n] and 'M' not in info['Interest Expense'][n]:
            info['Interest Coverage Ratio'].append(
                (float(info['EBIT(after unusual expense)'][n].strip('BM')) / 1000) /
                float(info['Interest Expense'][n].strip('BM')))
        elif 'M' in info['Interest Expense'][n] and 'M' not in info['EBIT(after unusual expense)'][n]:
            info['Interest Coverage Ratio'].append(
                float(info['EBIT(after unusual expense)'][n].strip('BM')) /
                (float(info['Interest Expense'][n].strip('BM')) / 1000))
        else:
            #takes care the case when a negative number is represented in parenthesis, updates will take care of the problem
            try:
                info['Interest Coverage Ratio'].append(float(info['EBIT(after unusual expense)'][n].strip('BM')) / float(info['Interest Expense'][n].strip('BM')))
            except:
                info['Interest Coverage Ratio'].append(None)


    if type == 'df':
        info_df = pd.DataFrame.from_dict(info, orient='index', columns=scope)
        return info_df

    elif type == 'd':
        return info

#Take a dictionary and evaluate key aspects
# Conditions to check:
# 1. EPS
# 2. ROE(Efficiency > 15%)
# 3. ROA(Manipulation > 7%)
# 4. Interest Coverage Ratio (ability to pay interest > 3)
if __name__ == '__main__':
    ticker = input('Enter a ticker: ')
    info = basicInfo(ticker, 'd')
    print(f'From 2015 to 2019, the EPS of the company were '
          f'{info["EPS (Basic)"][0]}, {info["EPS (Basic)"][1]}, {info["EPS (Basic)"][2]}, {info["EPS (Basic)"][3]}, {info["EPS (Basic)"][4]}.\n')
    ROE_counter = 0
    ROA_counter = 0
    IC_counter = 0
    for n in range(0, 5):
        if info['ROE %'][n] < 15:
            print(f'In {n+2015}, '
                  f'the company demonstrated inefficiency. The ROE of that year was {info["ROE %"][n]}')
        else:
            ROE_counter += 1

        if info['ROA %'][n] < 7:
            print(f'In {n + 2015}, '
                  f'the company\'s manipulation of asset fell short. The ROA of that year was {info["ROA %"][n]}')
        else:
            ROA_counter += 1
        try:
            if info['Interest Coverage Ratio'][n] is None or info['Interest Coverage Ratio'][n] < 3:
                print(f'In {n + 2015}, '
                      f'the company\'s ability to pay interest was impaired. The Interest Coverage ratio of that year was {info["Interest Coverage Ratio"][n]}')
            else:
                IC_counter += 1
        except:
            pass
        print('')

    if ROE_counter == 5:
        print('The company had no risk in efficiency')
    if ROA_counter == 5:
        print('The company had no risk in manipulation of asset.')
    if IC_counter == 5:
        print('The company had no problem in paying their interest')


