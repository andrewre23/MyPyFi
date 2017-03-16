from .. import db
from ..models import Portfolio, Holding

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
    gen_returns_dataframe:
        generate DataFrame object with daily returns for portfolio holdings
    gen_port_rets_and_vol:
        generate portfolio returns based on individual return/variance
    gen_efficient_frontier:
        generate efficient frontier of minimum risk per level of return
    clean_eff_frontier:
        clean values for optimization and interpolation
    solve_optimized_port:
        determine optimized portfolio on efficient frontier
    solve_optimal_weights:
        determine equivalent weights for optimized portfolio
    plot_optimal_portfolio:
        plot portfolio into static folder
    """

    def __init__(self, portfolio, start_date, rf=0.01):
        # initialize input parameters
        self.portfolio = portfolio  # portfolio to optimize
        self.start_date = start_date  # start date for historical returns
        self.rf = rf  # risk-free interest rate

        # initialize variables for calculation
        # returns DataFrame object
        self.rets = self.gen_returns_dataframe()
        # MCS sampling for portfolio returns and volatility
        self.prets, self.pvols = self.gen_port_rets_and_vol()
        # efficient frontier returns and volatility pairs
        self.trets, self.tvols = self.gen_efficient_frontier()
        # cleaned efficient frontier
        self.erets, self.evols = self.clean_eff_frontier()

        # solve for optimized portfolio on efficient frontier (max Sharpe ratio)
        self.solve_optimized_port()
        # solve for optimal weights
        self.solve_optimal_weights()
        # plot optimal portfolio and save png to static folder
        self.plot_optimal_portfolio()

        # create optimal portfolio in database
        self.portfolio.create_optimal_portfolio()
        self.opt_port = Portfolio.query.filter_by(name=portfolio.name + '_opt').first()
        # rebalance optimal portfolio
        self.rebalance_opt_port()

    def gen_returns_dataframe(self):
        # function to return DataFrame with daily returns
        # of holdings in portfolio
        import numpy as np
        import pandas as pd
        from pandas_datareader import data as web
        symbols = []
        for holding in self.portfolio.holdings:
            symbols.append(holding.symbol)
        data = pd.DataFrame()
        for sym in symbols:
            data[sym] = web.DataReader(sym, data_source='yahoo',
                                       start=self.start_date)['Adj Close']
        data.columns = symbols
        return np.log(data / data.shift(1))

    def gen_port_rets_and_vol(self, samples=2500):
        # function to generate portfolio returns and volatility
        # based off returns from start date argument
        import numpy as np
        prets = []
        pvols = []
        noa = self.portfolio.num_holdings
        for p in range(samples):
            weights = np.random.random(noa)
            weights /= np.sum(weights)
            prets.append(np.sum(self.rets.mean() * weights) * 252)
            pvols.append(np.sqrt(np.dot(weights.T,
                                        np.dot(self.rets.cov() * 252, weights))))
        return np.array(prets), np.array(pvols)

    def gen_efficient_frontier(self):
        # function to generate efficient frontier of portfolio
        # returns and volatility based off returns from
        # start date argument
        import numpy as np
        import scipy.optimize as sco
        trets = np.linspace(0.0, 0.5, 100)
        tvols = []
        noa = self.portfolio.num_holdings
        bnds = tuple((0, 1) for x in range(noa))
        for tret in trets:
            cons = ({'type': 'eq', 'fun': lambda x: self.statistics(x)[0] - tret},
                    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            res = sco.minimize(self.min_func_port, noa * [1. / noa, ], method='SLSQP',
                               bounds=bnds, constraints=cons)
            tvols.append(res['fun'])
        return trets, np.array(tvols)

    def clean_eff_frontier(self):
        # clean up efficient frontier
        # use positive values for volatility
        import numpy as np
        ind = np.argmin(self.tvols)
        evols = self.tvols[ind:]
        erets = self.trets[ind:]
        lastval = None
        evols = evols.round(8)
        erets = erets.round(8)
        # remove duplicate volatility values for interpolation
        for i in range(len(evols) - 1):
            if evols[i] == evols[i + 1]:
                lastval = i + 1
                break
        return erets[:lastval], evols[:lastval]

    def solve_optimized_port(self):
        # solve for optimized portfolio
        import scipy.interpolate as sci
        import scipy.optimize as sco
        if len(self.evols) < 3:
            self.tck = sci.splrep(self.evols, self.erets, k=2)
        else:
            self.tck = sci.splrep(self.evols, self.erets)
        # try various initial "guess" values for optimization
        # optimization path varies greatly depending on initial parameter
        for x in [2, 4, 1, 5, 3]:
            # catch runtime error that may otherwise stop program
            try:
                self.opt = sco.fsolve(self.equations, [self.rf, self.prets.mean() * x, self.pvols.mean()])
                break
            except RuntimeWarning:
                continue

    def solve_optimal_weights(self):
        # find optimal portfolio weights
        import scipy.optimize as sco
        import numpy as np
        noa = len(self.rets.columns)
        bnds = tuple((0, 1) for x in self.rets.columns)
        cons = ({'type': 'eq', 'fun': lambda x: self.statistics(x)[0] - self.f(self.opt[2])},
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        res = sco.minimize(self.min_func_port, noa * [1. / noa, ], method='SLSQP',
                           bounds=bnds, constraints=cons)
        self.opt_weights = abs(res['x'].round(4))

    def plot_optimal_portfolio(self):
        # plot and save to static folder
        import numpy as np
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 5))
        # random portfolio
        plt.scatter(self.pvols, self.prets, c=(self.prets - self.rf) / self.pvols, marker='o')
        # efficient frontier
        plt.plot(self.evols, self.erets, 'g', lw=4.0)
        cx = np.linspace(0.0, 0.3)
        # CAPM line
        plt.plot(cx, self.rf + ((self.f(self.opt[2]) - self.rf) / self.opt[2]) * cx, lw=1.5)
        plt.plot(self.opt[2], self.f(self.opt[2]), 'r*', markersize=15.0)
        plt.grid(True)
        plt.axhline(0, color='k', ls='--', lw=2.0)
        plt.axvline(0, color='k', ls='--', lw=2.0)
        plt.xlabel(r'$\sigma$')
        plt.ylabel(r'$\mu$')
        plt.colorbar(label='Sharpe Ratio')
        plt.title('Optimal Holding based on MCS (rf ={}%)'.format(self.rf * 100))
        plt.savefig(basedir[:-4] + 'static/optimized_portfolio.png')

    def rebalance_opt_port(self):
        # rebalance opt_portfolio to optimal weights
        total_balance = self.portfolio.market_value - self.portfolio.cash
        for i in range(len(self.rets.columns)):
            holding = Holding.query.filter_by(symbol=self.rets.columns[i], portfolio_id=self.opt_port.id).first()
            new_mkval = self.opt_weights[i] * total_balance
            holding.shares = int(round(new_mkval / holding.last_price, 0))
            holding.purch_price = holding.last_price
            holding.update()
        self.opt_port.update()

        # adjust cash-holdings based on new invested total
        self.opt_port.cash += (self.portfolio.market_value - self.opt_port.market_value)
        self.opt_port.update()

    def statistics(self, weights):
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
        pret = np.sum(self.rets.mean() * weights) * 252
        pvol = np.sqrt(np.dot(weights.T, np.dot(self.rets.cov() * 252, weights)))
        return np.array([pret, pvol, pret / pvol])

    def min_func_sharpe(self, weights):
        return -self.statistics(weights)[2]

    def min_func_variance(self, weights):
        return self.statistics(weights)[1] ** 2

    def min_func_port(self, weights):
        return self.statistics(weights)[1]

    def f(self, x):
        # efficient frontier function (splines approximation)
        import scipy.interpolate as sci
        return sci.splev(x, self.tck, der=0)

    def df(self, x):
        # efficient frontier function (splines approximation)
        import scipy.interpolate as sci
        return sci.splev(x, self.tck, der=1)

    def equations(self, p, rf=0.01):
        eq1 = rf - p[0]
        eq2 = rf + p[1] * p[2] - self.f(p[2])
        eq3 = p[1] - self.df(p[2])
        return eq1, eq2, eq3

    def gen_portfolio_weight_dict(portfolio):
        port_dict = {}
        for holding in portfolio:
            port_dict[holding.symbol] = 0
        return port_dict
