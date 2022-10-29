import yfinance as yf
import pandas as pd
import datetime
import streamlit as st
import matplotlib.pyplot as plt


def getTickerSymbols():
    '''
    Reads a local CSV where all NASDAQ stocks are listed.
    :return: All NASDAQ stock symbols
    '''
    stockData = pd.read_csv(r'path_to_file.csv')
    symbols = stockData['Symbol']
    return symbols


def filterData(allStocks, numStocks=-1):
    '''
    Randomly samples from a dataset of all NASDAQ stock symbols.
    :param numStocks: Number of stock to randomly sample
    :param allStocks: A list of all NASDAQ stock symbols
    :return: Sampled Series of stocks
    '''
    if numStocks != -1:
        stockSample = allStocks.sample(numStocks)
    else:
        stockSample = allStocks
    indexNames = stockSample[stockSample.str.isalpha() == False].index
    stockSample.drop(indexNames, inplace=True)
    return stockSample


def getHistoricalInfo(allStocks):
    df_list = list()
    for ticker in allStocks:
      data = yf.download(ticker, group_by="Ticker", start='2022-03-01', end='2022-09-01', interval='1d')
      data.insert(0, 'ticker', ticker)  # add this column because the dataframe doesn't contain a column with the ticker
      df_list.append(data)
    df = pd.concat(df_list)
    return df


def insert(conn, write_df):
    write_df.to_sql('raw_historical_daily',  # Name of the sql table
                    conn,
                    if_exists='append') # If the table already exists, {‘fail’, ‘replace’, ‘append’}, default ‘fail’

def validateTicker(stockTicker):
    stockData = pd.read_csv(
        r'path_to_file.csv')
    symbols = stockData['Symbol']
    for ticker in symbols:
        if ticker == stockTicker:
            return True
    return False

if __name__ == '__main__':

    st.title('Stock Analysis')
    st.write('This project was inspired by my interest in the stock market. Currently, you can either view the trend'
            'of a specific stock, or you can view a random sample.')

    option = st.selectbox(
        'Please select which analysis you would like to see:',
        ('Single Ticker', 'Random Sample'))

    st.write('You selected:', option)

    if option == 'Single Ticker':
        stockSymbol = st.text_input('Please input ticker here')
        isValid = validateTicker(stockSymbol)
        if isValid == False:
            st.write("Please input a valid ticker.")
        else:
            st.write('Completing analysis of', stockSymbol)
            singleStock = [stockSymbol]
            historicalDF = getHistoricalInfo(singleStock)
            historicalDF.rename(columns={'Open': 'open', 'High': 'high',
                                         'Low': 'low', 'Close': 'close',
                                         'Adj Close': 'adjClose', 'Volume': 'volume'}, inplace=True)
            historicalDF['Date'] = historicalDF.index

            st.write("Here is the raw data that we retrieved from the YFinance API.")
            st.write(historicalDF)

            historicalDF = historicalDF.dropna()
            df2 = pd.DataFrame()
            ticks = historicalDF['ticker'].unique()
            for i in ticks:
                temp = historicalDF.where(historicalDF['ticker'] == i)['open'].dropna()
                df2 = pd.concat([df2, temp.to_frame().set_index(historicalDF['Date'].unique()).T])
                temp = []
            df2 = df2.set_index([historicalDF['ticker'].unique()]).T
            st.write("Here is the transformed data so that we can chart the stocks over time.")
            st.write(df2)
            st.line_chart(df2)


    if option == 'Random Sample':
        allStocks = getTickerSymbols()
        sampleList = filterData(allStocks, 3)

        historicalDF = getHistoricalInfo(sampleList)
        historicalDF.rename(columns={'Open': 'open', 'High': 'high',
                                     'Low': 'low', 'Close': 'close',
                                     'Adj Close': 'adjClose', 'Volume': 'volume'}, inplace=True)
        historicalDF['Date'] = historicalDF.index

        st.write("Here is the raw data that we retrieved from the YFinance API.")
        st.write(historicalDF)

        historicalDF = historicalDF.dropna()
        df2 = pd.DataFrame()
        ticks = historicalDF['ticker'].unique()
        for i in ticks:
            temp = historicalDF.where(historicalDF['ticker'] == i)['open'].dropna()
            df2 = pd.concat([df2, temp.to_frame().set_index(historicalDF['Date'].unique()).T])
            temp = []
        df2 = df2.set_index([historicalDF['ticker'].unique()]).T
        st.write("Here is the transformed data so that we can chart the stocks over time.")
        st.write(df2)
        st.line_chart(df2)
