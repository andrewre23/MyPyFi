from pandas_datareader import data as web
from .. import db
from ..models import Portfolio, Holding

import os


basedir = os.path.abspath(os.path.dirname(__file__))


def gen_returns_dataframe(portfolio, start_date):
    # function to return DataFrame with daily returns
    # of holdings in portfolio
    import numpy as np
    import pandas as pd
    from pandas_datareader import data as web
    symbols = []
    for holding in portfolio.holdings:
        symbols.append(holding.symbol)
    data = pd.DataFrame()
    for sym in symbols:
        data[sym] = web.DataReader(sym,data_source='yahoo',
                                   start=start_date)['Adj Close']
    data.columns = symbols
    return np.log(data/data.shift(1))


def gen_port_rets_and_vol(portfolio, start_date, samples=2500):
    # function to generate portfolio returns and volatility
    # based off returns from start date argument
    import numpy as np
    prets = []
    pvols = []
    noa = portfolio.num_holdings
    for p in range(samples):
        weights = np.random.random(noa)
        weights /= np.sum(weights)
        prets.append(np.sum(rets.mean()*weights)*252)
        pvols.append(np.sqrt(np.dot(weights.T,
                    np.dot(rets.cov()*252,weights))))
    return np.array(prets), np.array(pvols)


def statistics(weights):
    """ Returns portfolio statitstics.

    Parameters
    ==========
    weights : array
        weights for different securities in portfolio

    Returns
    =======
    pret : float
        expected portfolio return
    pvol : float
        expected portfolio volatility
    pret / pvol : float
        Sharpe ratio for rf = 0
    """
    import numpy as np
    weights = np.array(weights)
    pret = np.sum(rets.mean()*weights)*252
    pvol = np.sqrt(np.dot(weights.T,np.dot(rets.cov()*252,weights)))
    return np.array([pret,pvol,pret/pvol])

def min_func_sharpe(weights):
    return -statistics(weights)[2]


def min_func_variance(weights):
    return statistics(weights)[1]**2


def min_func_port(weights):
    return statistics(weights)[1]


def gen_efficient_frontier(portfolio, start_date):
    # function to generate efficient frontier of portfolio
    # returns and volatility based off returns from
    # start date argument
    import numpy as np
    import scipy.optimize as sco
    trets = np.linspace(0.0,0.5,100)
    tvols = []
    noa = portfolio.num_holdings
    bnds = tuple((0,1) for x in range(noa))
    for tret in trets:
        cons = ({'type':'eq','fun': lambda x: statistics(x)[0] - tret},
                {'type':'eq','fun':lambda x:np.sum(x)-1})
        res = sco.minimize(min_func_port,noa*[1./noa,],method='SLSQP',
                           bounds=bnds,constraints=cons)
        tvols.append(res['fun'])
    return trets, np.array(tvols)


def f(x):
    # efficient frontier function (splines approximation)
    import scipy.interpolate as sci
    return sci.splev(x,tck,der=0)

def df(x):
    # efficient frontier function (splines approximation)
    import scipy.interpolate as sci
    return sci.splev(x,tck,der=1)


def equations(p,rf=0.01):
    eq1 = rf - p[0]
    eq2 = rf + p[1] * p[2] - f(p[2])
    eq3 = p[1] - df(p[2])
    return eq1, eq2, eq3



def optimal_portfolio(portfolio,start_date, rf=0.01):
    # function to return optimal portfolio based on
    # input portfolio and input start date for returns
    import numpy as np
    import scipy.interpolate as sci
    import scipy.optimize as sco
    import matplotlib.pyplot as plt

    # generate return DataFrame, and simulated portfolio
    # returns and efficient frontier -> minimized volatility
    global rets
    rets = gen_returns_dataframe(portfolio,start_date)
    prets,pvols = gen_port_rets_and_vol(portfolio,start_date)
    trets,tvols = gen_efficient_frontier(portfolio,start_date)

    # use positives of efficient frontier for CAPM line
    ind = np.argmin(tvols)
    evols = tvols[ind:]
    erets = trets[ind:]
    lastval = None
    evols = evols.round(6)
    erets = erets.round(6)
    # remove duplicate volatility values for interpolation
    for i in range(len(evols) - 1):
        if evols[i] == evols[i + 1]:
            lastval = i + 1
            break
    evols = evols[:lastval]
    erets = erets[:lastval]

    # solve for optimized portfolio
    global tck
    tck = sci.splrep(evols,erets)
    opt = sco.fsolve(equations,[rf,prets.mean(),pvols.mean()])

    # plot and save to static folder
    plt.figure(figsize=(10,5))
    plt.scatter(pvols,prets,c=(prets-rf)/pvols,marker='o')
    plt.plot(evols,erets,'g',lw=4.0)
    cx = np.linspace(0.0,opt[2]*1.5)
    plt.plot(cx,opt[0] + opt[1] * cx, lw=1.5)
    plt.plot(opt[2],f(opt[2]),'r*',markersize=15.0)
    plt.grid(True)
    plt.axhline(0,color='k',ls='-',lw=2.0)
    plt.axvline(0,color='k',ls='-',lw=2.0)
    plt.xlabel(r'$\sigma$')
    plt.ylabel(r'$\mu$')
    plt.colorbar(label='Sharpe Ratio')
    plt.title('Optimal Holding based on MCS (rf ={}%)'.format(rf*100))
    plt.savefig(basedir[:-4]+ 'static/optimized_portfolio.png')




# def last_price(symbol):
#     data = web.DataReader(symbol,'yahoo')['Adj Close']
#     return data.iloc[-1]
#
# def update_last_price(holding_id):
#     holding = Holding.query.filter_by(id=holding_id).first()
#     holding.last_price = round(last_price(holding.symbol),2)
#     db.session.add(holding)
#     db.session.commit()
#
# def update_mkt_val(portfolio_id):
#     portfolio = Portfolio.query.filter_by(id=portfolio_id).first()
#     portfolio.market_value = portfolio.cash
#     for hold in Holding.query.filter_by(portfolio_id=portfolio.id).all():
#         portfolio.market_value += hold.shares * hold.last_price
#     db.session.add(portfolio)
#     db.session.commit()
#
# def update_all_market_vals():
#     for port in Portfolio.query.all() or []:
#         for hold in Holding.query.filter_by(portfolio_id=port.id).all() or []:
#             update_last_price(hold.id)
#         update_mkt_val(port.id)
#
# def add_hold_to_port(holding, port_name):
#     holding.portfolio_id = Portfolio.query.filter_by(name=port_name).first().id
#     db.session.add(holding)
#     db.session.commit()
#     update_mkt_val(holding.portfolio_id)
#
#
#
# def edit_portfolio():
#     pass