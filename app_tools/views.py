from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.

import pandas as pd
import pandas_datareader.data as web
import datetime as dt
from datetime import date, datetime, timedelta
import numpy as np

import matplotlib.pyplot as plt
from django.http import HttpResponse
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from django.contrib import messages

class ToolsOverview(TemplateView):
    template_name = 'tools0.html'
class Tool1(TemplateView):
    template_name = 'tools1_optimal_portfolio.html'
class Tool2(TemplateView):
    template_name = 'tools2_leverage_calc.html'
class Tool3(TemplateView):
    template_name = 'tools3_portfolio_perf.html'
class Tool4(TemplateView):
    template_name = 'tools4_benchmark.html'
class Tool5(TemplateView):
    template_name = 'tools5_correlation.html'

#error_handling and essential functions
def str2date(str):
    str_list = str.split(',')
    year = int(str_list[0])
    month = int(str_list[1])
    day = int(str_list[2])

    return(dt.datetime(year,month,day))

def ticker_data(tickers, start, end):
    days = (end-start).days

    index = pd.date_range(start, periods = days, freq='D')
    df = pd.DataFrame(index = index,columns = tickers)

    for ticker in tickers:
        df[ticker] = web.DataReader(ticker, 'yahoo', start, end)['Adj Close']
    df = df.dropna()
    return(df)

def is_int(input):
    try:
        if (int(input))>=0:
            return(True)
        else:
            return('Portfolios to Simulate must be positive whole number')
    except:
        return('Portfolios to Simulate must be positive whole number')
def is_good_ticker(tickers_input):
    start_test = date.today() - timedelta(days = 5)
    end_test = date.today()
    try:
        tickers = tickers_input.replace(' ','').split(',')
        df = ticker_data(tickers, start_test,end_test)
        return(True)
    except:
        return('Please check your Tickers')
def is_good_date(start, end):
    try:
        end_date = str2date(end)
        start_date=str2date(start)
        time_diff = (end_date - start_date).days
        if time_diff>0:
            return(True)
        else:
            return('Please check your start date and/or end date. Dates must be in format YYYY,MM,DD and start date must be before end date')
    except:
        return('Please check your start date and/or end date. Dates must be in format YYYY,MM,DD and start date must be before end date')

def is_good_holdings(port_str):
    holdings={}
    try:
        for item in port_string.split(','):
            holdings[item.split(':')[0]] = float(item.split(':')[1])/100

        if np.sum(list(holdings.values()))!=1:
            return('Check portfolio holdings allocations. Allocations must sum to 100')
        if is_good_ticker(','.join(list(holdings.keys())))!=True:
            return('check portfolio holdings tickers')
        else:
            return(True)
    except:
        return('check porfolio holdings formatting')

def is_good_int(int_rate_input):
    try:
        x = float(int_rate_input)
        return(True)
    except:
        return('interest rate must be a number')

def is_pos(entry, num):
    try:
        x = float(num)
        if x>0:
            return(True)
        else:
            return(entry +' must be a positive number')
    except:
        return(entry +' must be a positive number')
### tool1 optimal portfolio
def calc_portfolio_perf(weights, mean_returns, cov, rf):
    portfolio_return = np.sum(mean_returns * weights) * 252
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov, weights))) * np.sqrt(252)
    sharpe_ratio = (portfolio_return - rf) / portfolio_std
    return portfolio_return, portfolio_std, sharpe_ratio
def simulate_random_portfolios(num_portfolios, mean_returns, cov, rf, tickers):
    results_matrix = np.zeros((len(mean_returns)+3, num_portfolios))
    for i in range(num_portfolios):
        weights = np.random.random(len(mean_returns))
        weights /= np.sum(weights)
        portfolio_return, portfolio_std, sharpe_ratio = calc_portfolio_perf(weights, mean_returns, cov, rf)
        results_matrix[0,i] = portfolio_return
        results_matrix[1,i] = portfolio_std
        results_matrix[2,i] = sharpe_ratio
        #iterate through the weight vector and add data to results array
        for j in range(len(weights)):
            results_matrix[j+3,i] = weights[j]

    results_df = pd.DataFrame(results_matrix.T,columns=['ret','stdev','sharpe'] + [ticker for ticker in tickers])

    return results_df
def tools1_result(request):
    try:
        num_port_input = request.GET['num_port']
        tickers_input = request.GET['tickers']
        start_input= request.GET['start']
        end_input = request.GET['end']

        start_date = str2date(start_input)
        end_date = str2date(end_input)
        tickers= tickers_input.replace(' ','').split(',')
        df = ticker_data(tickers, start_date, end_date)

        mean_returns = df.pct_change().mean()
        cov = df.pct_change().cov()
        num_portfolios = int(num_port_input)
        rf = 0.0
        results_frame = simulate_random_portfolios(num_portfolios, mean_returns, cov, rf, tickers)
        max_sharpe = results_frame['sharpe'].max()
        best_port = results_frame[results_frame['sharpe']==max_sharpe]
        best_port_html = best_port.to_html()
        return render(request, 'tools1_result.html', {'tools1_result': best_port_html})
    except:
        int_check = is_int(num_port_input)
        ticker_check = is_good_ticker(tickers_input)
        date_check= is_good_date(start_input, end_input)
        if int_check!=True:
            messages.add_message(request, messages.ERROR, int_check)
        if ticker_check!=True:
            messages.add_message(request, messages.ERROR, ticker_check)
        if date_check!=True:
            messages.add_message(request, messages.ERROR, date_check)

        return render(request, 'tools1_optimal_portfolio.html')

### tool 2 leverage calculator
def simulate_single_portfolio(portfolio, mean_returns, cov, rf):
    tickers = list(portfolio.keys())
    results_matrix = np.zeros((len(mean_returns)+3, 1))
    weights = np.array(list(portfolio.values()))
    portfolio_return, portfolio_std, sharpe_ratio = calc_portfolio_perf(weights, mean_returns, cov, rf)
    results_matrix[0,0] = portfolio_return
    results_matrix[1,0] = portfolio_std
    results_matrix[2,0] = sharpe_ratio
    #iterate through the weight vector and add data to results array
    for j in range(len(weights)):
        results_matrix[j+3,0] = weights[j]

    results_df = pd.DataFrame(results_matrix.T,columns=['ret','stdev','sharpe'] + [ticker for ticker in tickers])

    return results_df
def target_return(portfolio_data_df, tgt_rtn, int_rate, rf):
    leverage = (tgt_rtn - int_rate)/(float(portfolio_data_df['ret']-int_rate))
    portfolio_data_df['leverage'] = leverage
    portfolio_data_df['levered ret'] = tgt_rtn
    portfolio_data_df['levered stdev'] = portfolio_data_df['stdev']*leverage
    portfolio_data_df['levered sharpe'] = (portfolio_data_df['levered ret'] - rf)/ portfolio_data_df['levered stdev']
    return(portfolio_data_df)
def target_risk(portfolio_data_df, tgt_risk, int_rate, rf):
    leverage = float(tgt_risk / portfolio_data_df['stdev'])
    portfolio_data_df['leverage'] = leverage
    portfolio_data_df['levered ret'] = portfolio_data_df['ret']*leverage-(leverage-1)*int_rate
    portfolio_data_df['levered stdev'] = tgt_risk
    portfolio_data_df['levered sharpe'] = (portfolio_data_df['levered ret'] - rf)/ portfolio_data_df['levered stdev']
    return(portfolio_data_df)
def tools2_result_return(request):
    start_input= request.GET['start']
    end_input = request.GET['end']
    tgt_rtn_input = request.GET['tgt_rtn']
    int_rate_input = request.GET['int_rate']

    try:
        holdings={}
        port_string = request.GET['holdings']
        for item in port_string.split(','):
            holdings[item.split(':')[0]] = float(item.split(':')[1])/100

        tickers = list(holdings.keys())
        # start_input= request.GET['start']
        # end_input = request.GET['end']
        start_date = str2date(start_input)
        end_date = str2date(end_input)
        df = ticker_data(tickers, start_date, end_date)
        mean_returns = df.pct_change().mean()
        cov = df.pct_change().cov()

        rf=0.0

        input_portfolio = simulate_single_portfolio(holdings, mean_returns, cov, rf)

        # tgt_rtn_input = request.GET['tgt_rtn']
        # int_rate_input = request.GET['int_rate']

        tgt_rtn = float(tgt_rtn_input)
        int_rate = float(int_rate_input)

        lev2rtn_port = target_return(input_portfolio, tgt_rtn, int_rate, rf)
        lev2rtn_port_html = lev2rtn_port.to_html()

        return render(request,'tools2_result_return.html', {'tools2_result_return':lev2rtn_port_html})
    except:
        # tgt_rtn_input = request.GET['tgt_rtn']
        # int_rate_input = request.GET['int_rate']
        holdings_check = is_good_holdings(port_string)
        date_check= is_good_date(start_input, end_input)
        int_rate_check = is_good_int(int_rate_input)
        tgt_rtn_check = is_pos('target returns', tgt_rtn_input)

        if holdings_check!=True:
            messages.add_message(request, messages.ERROR, holdings_check)
        if date_check!=True:
            messages.add_message(request, messages.ERROR, date_check)
        if int_rate_check!=True:
            messages.add_message(request, messages.ERROR, int_rate_check)
        if tgt_rtn_check!=True:
            messages.add_message(request, messages.ERROR, tgt_rtn_check)
        return render(request, 'tools2_leverage_calc.html')

def tools2_result_risk(request):
    port_string = request.GET['holdings2']
    start_input= request.GET['start2']
    end_input = request.GET['end2']

    tgt_risk_input = request.GET['tgt_risk']
    int_rate_input = request.GET['int_rate2']

    try:

        holdings={}
        # port_string = request.GET['holdings2']
        for item in port_string.split(','):
            holdings[item.split(':')[0]] = float(item.split(':')[1])/100

        tickers = list(holdings.keys())
        # start_input= request.GET['start2']
        # end_input = request.GET['end2']
        start_date = str2date(start_input)
        end_date = str2date(end_input)
        df = ticker_data(tickers, start_date, end_date)
        mean_returns = df.pct_change().mean()
        cov = df.pct_change().cov()

        rf=0.0

        input_portfolio = simulate_single_portfolio(holdings, mean_returns, cov, rf)

        # tgt_risk = float(request.GET['tgt_risk'])
        # int_rate = float(request.GET['int_rate2'])
        tgt_risk = float(tgt_risk_input)
        int_rate = float(int_rate_input)


        lev2risk_port = target_risk(input_portfolio, tgt_risk, int_rate, rf)
        lev2risk_port_html = lev2risk_port.to_html()

    except:
        holdings_check = is_good_holdings(port_string)
        date_check= is_good_date(start_input, end_input)
        int_rate_check = is_good_int(int_rate_input)
        tgt_risk_check = is_pos('target risk', tgt_risk_input)

        if holdings_check!=True:
            messages.add_message(request, messages.ERROR, holdings_check)
        if date_check!=True:
            messages.add_message(request, messages.ERROR, date_check)
        if int_rate_check!=True:
            messages.add_message(request, messages.ERROR, int_rate_check)
        if tgt_risk_check!=True:
            messages.add_message(request, messages.ERROR, tgt_risk_check)
        return render(request, 'tools2_leverage_calc.html')

    return render(request,'tools2_result_risk.html', {'tools2_result_risk':lev2risk_port_html})
###

### tool 3 portfolio performance / backtest
def sim_port_series(portfolio, ticker_df, initial_value, name, leverage, int_rate):
    portfolio_df = ticker_df.pct_change()
    for ticker in portfolio.keys():
        portfolio_df[ticker + ' Adj Close'] = [0]*len(ticker_df)
        portfolio_df[ticker + ' Adj Close'][0] = initial_value*portfolio[ticker]

        for i in range(1, len(ticker_df)):
            portfolio_df[ticker + ' Adj Close'][i] = (1+portfolio_df[ticker][i])*portfolio_df[ticker + ' Adj Close'][i-1]

    portfolio_df[name + ' Adj Close'] = [0]*len(ticker_df)
    portfolio_df[name + ' Adj Close leveraged'] = [0]*len(ticker_df)
    for i in range(len(ticker_df)):
        for ticker in portfolio.keys():
            portfolio_df[name + ' Adj Close'][i] += portfolio_df[ticker + ' Adj Close'][i]
        portfolio_df[name + ' Adj Close leveraged'][i] = portfolio_df[name + ' Adj Close'][i]*leverage - (leverage*initial_value-initial_value) - (leverage*initial_value-initial_value)*int_rate/252
    return(portfolio_df)

def tools3_result(request):

    # leverage = request.GET['levr']
    # portfolio_df,benchmark_df = tools3_result_data(request)
    # portfolio_df = tools3_result_data(request)[0]

    initial_value_input = request.GET['investment']
    leverage_input = request.GET['levr']
    int_rate_input = request.GET['int_rate']

    start_input= request.GET['start']
    end_input = request.GET['end']
    port_string = request.GET['holdings']
    benchmark_ticker = request.GET['benchmark']

    try:
        initial_value = float(initial_value_input)
        leverage = float(leverage_input)
        int_rate = float(int_rate_input)

        start_input= request.GET['start']
        end_input = request.GET['end']
        start_date = str2date(start_input)
        end_date = str2date(end_input)

        holdings= {}
        port_string = request.GET['holdings']
        for item in port_string.split(','):
            holdings[item.split(':')[0]] = float(item.split(':')[1])/100

        tickers = list(holdings.keys())
        ticker_df = ticker_data(tickers, start_date, end_date)

        name1 = 'portfolio'
        portfolio_df = sim_port_series(holdings, ticker_df, initial_value, name1, leverage, int_rate)
        # portfolio_df_html = portfolio_df.to_html()

        benchmark_holding = {benchmark_ticker:1.0}

        benchmark_ticker_df = ticker_data([benchmark_ticker], start_date, end_date)

        name2 = 'benchmark'
        benchmark_df = sim_port_series(benchmark_holding, benchmark_ticker_df, initial_value, name2, leverage, int_rate)

        x = portfolio_df['portfolio Adj Close leveraged'].index
        y1 = portfolio_df['portfolio Adj Close leveraged']
        y2 = portfolio_df['portfolio Adj Close']
        y3 = benchmark_df['benchmark Adj Close']

        # return render(request,'tools3_result.html', {'tools3_result':y3})

        fig, ax = plt.subplots(figsize=(14,15))
        ax.plot(x, y1, color='red', label = 'levered portfolio')
        ax.plot(x, y2, color='blue', label = 'unlevered portfolio')
        ax.plot(x, y3, color='black', label = 'benchmark')

        ax.legend()

        ax.set(xlabel='time', ylabel='portfolio value',title='backtest')
        ax.grid()

        response = HttpResponse(content_type = 'image/png')
        canvas = FigureCanvasAgg(fig)
        canvas.print_png(response)
        return response
    except:
        holdings_check = is_good_holdings(port_string)
        date_check= is_good_date(start_input, end_input)
        cash_check = is_pos('cash', initial_value_input)
        levr_check = is_pos('leverage', leverage_input )
        int_rate_check = is_good_int(int_rate_input)
        bench_check = is_good_ticker([benchmark_ticker])

        if holdings_check!=True:
            messages.add_message(request, messages.ERROR, holdings_check)
        if date_check!=True:
            messages.add_message(request, messages.ERROR, date_check)
        if cash_check!=True:
            messages.add_message(request, messages.ERROR, cash_check)
        if levr_check!=True:
            messages.add_message(request, messages.ERROR, levr_check)
        if int_rate_check!=True:
            messages.add_message(request, messages.ERROR, int_rate_check)
        if bench_check!=True:
            messages.add_message(request, messages.ERROR, 'check benchmark ticker')

        return render(request,'tools3_portfolio_perf.html')

###

###tool 4 benchmark data
def get_benchmark(indices,start, end):

    starter_data = {'benchmark':'0','ret':'0', 'stdev':'0', 'sharpe':'0'}
    df = pd.DataFrame(starter_data, index = starter_data.keys())[0:1].reset_index(drop = True)
    rf = 0
    for index in indices:

        series = web.DataReader(index, 'yahoo', start, end)['Adj Close']
        ret = series.pct_change().mean()*252
        stdev = series.pct_change().std()*np.sqrt(252)
        sharpe = (ret-rf)/stdev
        benchmark_data = {'benchmark':index,'ret':ret, 'stdev':stdev, 'sharpe':sharpe}
        new_row = pd.DataFrame(benchmark_data, index = benchmark_data.keys())[0:1].reset_index(drop = True)
        df = df.append(new_row)
    df = df.reset_index(drop = True).drop(0)
    return(df)

def tools4_result(request):
    tickers_input = request.GET['indices']
    start_input = request.GET['start']
    end_input = request.GET['end']

    try:
        tickers_input = request.GET['indices']
        tickers = tickers_input.replace(' ','').split(',')

        start_input = request.GET['start']
        end_input = request.GET['end']
        start_date = str2date(start_input)
        end_date = str2date(end_input)

        benchmarks = get_benchmark(tickers,start_date, end_date)
        return render(request,'tools4_result.html', {'tools4_result':benchmarks.to_html()})

    except:
        ticker_check = is_good_ticker(tickers_input)
        date_check = is_good_date(start_input, end_input)
        if ticker_check!=True:
            messages.add_message(request, messages.ERROR, ticker_check)
        if date_check!=True:
            messages.add_message(request, messages.ERROR, date_check)
        return render(request, 'tools4_benchmark.html')


###tool 5 correlation
def series_corr(ser1, ser2):
    correlation = ser1.pct_change().corr(ser2.pct_change())
    return(correlation)
def create_corr_matrix(ticker_df):
    data = ticker_df
    stock_dict = ticker_df.to_dict(orient='series')
    corr_matrix = data.corr()

    for stock1 in stock_dict.keys():
        for stock2 in stock_dict.keys():
            corr_matrix[stock1][stock2] = series_corr(stock_dict[stock1], stock_dict[stock2])
    return(corr_matrix)
def tools5_result(request):

    initial_value = 10000
    leverage = 1.5
    int_rate = 0.015
    start_input= request.GET['start']
    end_input = request.GET['end']
    port_string = request.GET['holdings']
    all_tickers_input = request.GET['tickers']

    try:
        start_input= request.GET['start']
        end_input = request.GET['end']
        start_date = str2date(start_input)
        end_date = str2date(end_input)

        holdings= {}
        port_string = request.GET['holdings']
        for item in port_string.split(','):
            holdings[item.split(':')[0]] = float(item.split(':')[1])/100

        tickers = list(holdings.keys())
        ticker_df = ticker_data(tickers, start_date, end_date)

        name = 'portfolio'
        portfolio_df = sim_port_series(holdings, ticker_df, initial_value, name, leverage, int_rate)


        all_tickers_input = request.GET['tickers']
        all_tickers = all_tickers_input.replace(' ','').split(',')
        all_tickers_df = ticker_data(all_tickers, start_date, end_date)
        all_tickers_df['portfolio'] = portfolio_df['portfolio Adj Close']

        # portfolio_df_html = portfolio_df.to_html()

        corr_matrix = create_corr_matrix(all_tickers_df)

        return render(request,'tools5_result.html', {'tools5_result':corr_matrix.to_html()})

    except:
        ticker_check = is_good_ticker(all_tickers_input)
        date_check = is_good_date(start_input, end_input)
        holdings_check = is_good_holdings(port_string)
        if holdings_check!=True:
            messages.add_message(request, messages.ERROR, holdings_check)
        if ticker_check!=True:
            messages.add_message(request, messages.ERROR, ticker_check)
        if date_check!=True:
            messages.add_message(request, messages.ERROR, date_check)

        return render(request, 'tools5_correlation.html')





    #
    #
    #
