from .. import db
from ..models import Portfolio, Holding

import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from dx import *
import os

basedir = os.path.abspath(os.path.dirname(__file__))


# class definition for optimized portfolio
# to hold methods and attributes needed while optimizing
class optimized_portfolio(object):
    """
    Optimized Portfolio Object

    Used for optimizing portfolio in app

    Parameters
    =========
    portfolio : Portfolio model
        input portfolio to be optimized
    start_date : datetime.date
        start of time-span for historical return analysis

    Methods
    =======

    """

    def __init__(self, portfolio, start_date, rf=0.01):
        # initialize input parameters
        self.portfolio = portfolio  # portfolio to optimize
        self.start_date = start_date  # start date for historical returns
        self.rf = rf  # risk-free interest rate

        # add dx parameters needed for portfolio
        self.initialize_parameters()

        # simulate various portfolio weights
        # and optimize portfolio
        self.simulate_optimize()
        # generate efficient frontier
        # and plot all on active plot
        self.gen_eff_plot()
        # try and plot CAPM line
        # may fail with high-return portfolios
        self.plot_capm_opt_save()

        # rebalance optimal portfolio
        self.rebalance_opt_port()

    def initialize_parameters(self):
        # add dx parameters needed for portfolio
        self.ma = market_environment('ma', self.start_date)
        self.ma.add_list('symbols', [holding.symbol for holding in self.portfolio.holdings])
        self.ma.add_constant('source', 'google')
        self.ma.add_constant('final_date', dt.datetime.today())
        # create portfolio object
        self.port = mean_variance_portfolio('optimizing_port', self.ma)

    def simulate_optimize(self):
        # Monte Carlo simulation for portfolio compositions
        self.rets = []
        self.vols = []
        for w in range(500):
            weights = np.random.random(self.portfolio.num_holdings)
            weights /= sum(weights)
            r, v, sr = self.port.test_weights(weights)
            self.rets.append(r)
            self.vols.append(v)
        self.rets = np.array(self.rets)
        self.vols = np.array(self.vols)
        self.port.optimize('Sharpe')

    def gen_eff_plot(self):
        self.evols, self.erets = self.port.get_efficient_frontier(100)
        plt.figure(figsize=(10, 6))
        plt.scatter(self.vols, self.rets, c=self.rets / self.vols, marker='o')
        plt.scatter(self.evols, self.erets, c=self.erets / self.evols, marker='x')
        plt.xlabel(r'$\sigma$')
        plt.ylabel(r'$\mu$')
        plt.colorbar(label='Sharpe Ratio')
        plt.title('Optimal Holding based on MCS (rf ={}%)'.format(self.rf * 100))

    def plot_capm_opt_save(self):
        try:
            cml, optv, optr = self.port.get_capital_market_line(riskless_asset=self.rf)
            plt.plot((0, 0.4), (cml(0), cml(0.4)), lw=2.0, label='CAPM Line')
            plt.plot(optv, optr, 'y*', markersize=20, label='Optimal Portfolio')
        except ValueError:
            plt.plot(self.port.get_volatility(), self.port.get_portfolio_return(), 'y*', markersize=20,
                     label='Optimal Portfolio')
        finally:
            plt.legend(loc=0)
            plt.ylim(0)
            plt.savefig(basedir[:-4] + 'static/optimized_portfolio.png')

    def rebalance_opt_port(self):
        # create optimal portfolio in database
        # if not already in
        self.portfolio.create_optimal_portfolio()
        self.opt_port = Portfolio.query.filter_by(name=self.portfolio.name + '_opt').first()

        # rebalance opt_portfolio to optimal weights
        total_balance = self.portfolio.market_value - self.portfolio.cash
        for i in range(len(self.port.symbols)):
            holding = Holding.query.filter_by(symbol=self.port.symbols[i], portfolio_id=self.opt_port.id).first()
            new_mkval = self.port.weights[i] * total_balance
            holding.shares = int(round(new_mkval / holding.last_price, 0))
            holding.purch_price = holding.last_price
            holding.update()
        self.opt_port.update()

        # adjust cash-holdings based on new invested total
        self.opt_port.cash += (self.portfolio.market_value - self.opt_port.market_value)
        self.opt_port.update()



        #
        #     # initialize variables for calculation
        #     # returns DataFrame object
        #     self.rets = self.gen_returns_dataframe()
        #     # MCS sampling for portfolio returns and volatility
        #     self.prets, self.pvols = self.gen_port_rets_and_vol()
        #     # efficient frontier returns and volatility pairs
        #     self.trets, self.tvols = self.gen_efficient_frontier()
        #     # cleaned efficient frontier
        #     self.erets, self.evols = self.clean_eff_frontier()
        #
        #     # solve for optimized portfolio on efficient frontier (max Sharpe ratio)
        #     self.solve_optimized_port()
        #     # solve for optimal weights
        #     self.solve_optimal_weights()
        #     # plot optimal portfolio and save png to static folder
        #     self.plot_optimal_portfolio()
        #
        #     # create optimal portfolio in database
        #     self.portfolio.create_optimal_portfolio()
        #     self.opt_port = Portfolio.query.filter_by(name=portfolio.name + '_opt').first()
        #     # rebalance optimal portfolio
        #     self.rebalance_opt_port()
        #
        # def gen_returns_dataframe(self):
        #     # function to return DataFrame with daily returns
        #     # of holdings in portfolio
        #     import numpy as np
        #     import pandas as pd
        #     from pandas_datareader import data as web
        #     symbols = []
        #     for holding in self.portfolio.holdings:
        #         symbols.append(holding.symbol)
        #     data = pd.DataFrame()
        #     for sym in symbols:
        #         data[sym] = web.DataReader(sym, data_source='yahoo',
        #                                    start=self.start_date)['Adj Close']
        #     data.columns = symbols
        #     return np.log(data / data.shift(1))
        #
        # def gen_port_rets_and_vol(self, samples=2500):
        #     # function to generate portfolio returns and volatility
        #     # based off returns from start date argument
        #     import numpy as np
        #     prets = []
        #     pvols = []
        #     noa = self.portfolio.num_holdings
        #     for p in range(samples):
        #         weights = np.random.random(noa)
        #         weights /= np.sum(weights)
        #         prets.append(np.sum(self.rets.mean() * weights) * 252)
        #         pvols.append(np.sqrt(np.dot(weights.T,
        #                                     np.dot(self.rets.cov() * 252, weights))))
        #     return np.array(prets), np.array(pvols)
        #
        # def gen_efficient_frontier(self):
        #     # function to generate efficient frontier of portfolio
        #     # returns and volatility based off returns from
        #     # start date argument
        #     import numpy as np
        #     import scipy.optimize as sco
        #     trets = np.linspace(0.0, 0.6, 100)
        #     tvols = []
        #     noa = self.portfolio.num_holdings
        #     bnds = tuple((0, 1) for x in range(noa))
        #     for tret in trets:
        #         cons = ({'type': 'eq', 'fun': lambda x: self.statistics(x)[0] - tret},
        #                 {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        #         res = sco.minimize(self.min_func_port, noa * [1. / noa, ], method='SLSQP',
        #                            bounds=bnds, constraints=cons)
        #         tvols.append(res['fun'])
        #     return trets, np.array(tvols)
        #
        # def clean_eff_frontier(self):
        #     # clean up efficient frontier
        #     # use positive values for volatility
        #     import numpy as np
        #     ind = np.argmin(self.tvols)
        #     evols = self.tvols[ind:]
        #     erets = self.trets[ind:]
        #     evols = evols.round(8)
        #     erets = erets.round(8)
        #     # remove duplicate volatility values for interpolation
        #     lower = None; upper = None
        #     midpt = round(len(evols) / 2)
        #     for i in range(len(evols) - 1):
        #         # iterate through evols list and determine upper and
        #         # lower limites of range that does not have identical
        #         # evol values <-- needed for interpolation
        #         if evols[i] == evols[i + 1]:
        #             if i <= midpt:
        #                 lower = i + 1
        #             else:
        #                 upper = i + 1
        #                 break
        #     return erets[lower:upper], evols[lower:upper]
        #
        # def solve_optimized_port(self):
        #     # solve for optimized portfolio
        #     import scipy.interpolate as sci
        #     import scipy.optimize as sco
        #     if len(self.evols) < 3:
        #         self.tck = sci.splrep(self.evols, self.erets, k=2)
        #     else:
        #         self.tck = sci.splrep(self.evols, self.erets)
        #     # try various initial "guess" values for optimization
        #     # optimization path varies greatly depending on initial parameter
        #     for x in [2, 4, 1, 5, 3]:
        #         # catch runtime error that may otherwise stop program
        #         try:
        #             self.opt = sco.fsolve(self.equations, [self.rf, self.prets.mean() * x, self.pvols.mean()])
        #             break
        #         except RuntimeWarning:
        #             continue
        #
        # def solve_optimal_weights(self):
        #     # find optimal portfolio weights
        #     import scipy.optimize as sco
        #     import numpy as np
        #     noa = len(self.rets.columns)
        #     bnds = tuple((0, 1) for x in self.rets.columns)
        #     cons = ({'type': 'eq', 'fun': lambda x: self.statistics(x)[0] - self.f(self.opt[2])},
        #             {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        #     res = sco.minimize(self.min_func_port, noa * [1. / noa, ], method='SLSQP',
        #                        bounds=bnds, constraints=cons)
        #     self.opt_weights = abs(res['x'].round(4))
        #
        # def plot_optimal_portfolio(self):
        #     # plot and save to static folder
        #     import numpy as np
        #     import matplotlib.pyplot as plt
        #     plt.figure(figsize=(10, 5))
        #     # random portfolio
        #     plt.scatter(self.pvols, self.prets, c=(self.prets - self.rf) / self.pvols, marker='o')
        #     # efficient frontier
        #     plt.plot(self.evols, self.erets, 'g', lw=4.0)
        #     cx = np.linspace(0.0, 0.3)
        #     # CAPM line
        #     plt.plot(cx, self.rf + ((self.f(self.opt[2]) - self.rf) / self.opt[2]) * cx, lw=1.5)
        #     plt.plot(self.opt[2], self.f(self.opt[2]), 'r*', markersize=15.0)
        #     plt.grid(True)
        #     plt.axhline(0, color='k', ls='--', lw=2.0)
        #     plt.axvline(0, color='k', ls='--', lw=2.0)
        #     plt.xlabel(r'$\sigma$')
        #     plt.ylabel(r'$\mu$')
        #     plt.colorbar(label='Sharpe Ratio')
        #     plt.title('Optimal Holding based on MCS (rf ={}%)'.format(self.rf * 100))
        #     plt.savefig(basedir[:-4] + 'static/optimized_portfolio.png')
        #
        # def rebalance_opt_port(self):
        #     # rebalance opt_portfolio to optimal weights
        #     total_balance = self.portfolio.market_value - self.portfolio.cash
        #     for i in range(len(self.rets.columns)):
        #         holding = Holding.query.filter_by(symbol=self.rets.columns[i], portfolio_id=self.opt_port.id).first()
        #         new_mkval = self.opt_weights[i] * total_balance
        #         holding.shares = int(round(new_mkval / holding.last_price, 0))
        #         holding.purch_price = holding.last_price
        #         holding.update()
        #     self.opt_port.update()
        #
        #     # adjust cash-holdings based on new invested total
        #     self.opt_port.cash += (self.portfolio.market_value - self.opt_port.market_value)
        #     self.opt_port.update()
        #
        # def statistics(self, weights):
        #     """ Returns portfolio statitstics.
        #
        #     Parameters
        #     ==========
        #     weights : array
        #         weights for different securities in portfolio
        #
        #     Returns
        #     =======
        #     pret : float
        #         expected portfolio return
        #     pvol : float
        #         expected portfolio volatility
        #     pret / pvol : float
        #         Sharpe ratio for rf = 0
        #     """
        #     import numpy as np
        #     weights = np.array(weights)
        #     pret = np.sum(self.rets.mean() * weights) * 252
        #     pvol = np.sqrt(np.dot(weights.T, np.dot(self.rets.cov() * 252, weights)))
        #     return np.array([pret, pvol, pret / pvol])
        #
        # def min_func_sharpe(self, weights):
        #     return -self.statistics(weights)[2]
        #
        # def min_func_variance(self, weights):
        #     return self.statistics(weights)[1] ** 2
        #
        # def min_func_port(self, weights):
        #     return self.statistics(weights)[1]
        #
        # def f(self, x):
        #     # efficient frontier function (splines approximation)
        #     import scipy.interpolate as sci
        #     return sci.splev(x, self.tck, der=0)
        #
        # def df(self, x):
        #     # efficient frontier function (splines approximation)
        #     import scipy.interpolate as sci
        #     return sci.splev(x, self.tck, der=1)
        #
        # def equations(self, p, rf=0.01):
        #     eq1 = rf - p[0]
        #     eq2 = rf + p[1] * p[2] - self.f(p[2])
        #     eq3 = p[1] - self.df(p[2])
        #     return eq1, eq2, eq3
        #
        # def gen_portfolio_weight_dict(portfolio):
        #     port_dict = {}
        #     for holding in portfolio:
        #         port_dict[holding.symbol] = 0
        #     return port_dict
