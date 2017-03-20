from .. import db
from ..models import Portfolio, Holding

import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from dx import *
import os

basedir = os.path.abspath(os.path.dirname(__file__))


# class definition for portfolio plot
# to hold methods and attributes needed while plotting
class PortfolioPlot(object):
    """
    Portfolio Plot Object

    -Plots portfolio on portfolio page as pie chart

    Parameters
    =========
    portfolio : Portfolio model
        input portfolio to be plotted

    Methods
    =======
    plot_portfolio:
        plot portfolio pie chart into static folder
    """

    def __init__(self, portfolio):
        # initialize input parameters
        self.portfolio = portfolio  # portfolio to plot

        # plot portfolio into static folder
        self.plot_portfolio()

    def plot_portfolio(self):
        # get sorted list of holdings and portfolio percentages
        labels = [holding.symbol for holding in self.portfolio.holdings]
        values = [holding.portfolio_percent for holding in self.portfolio.holdings]
        labels.append('Cash')
        values.append(self.portfolio.cash / self.portfolio.market_value)
        tups = [(values[i], labels[i]) for i in range(len(labels))]
        tups = sorted(tups, key=lambda val: val[0], reverse=True)
        values = [tup[0] for tup in tups]
        labels = [tup[1] for tup in tups]

        # prep parameters for plotting and
        # plot portfolio pie chart into static folder
        explode = [0.05 for value in values]
        plt.close()
        plt.title('Portfolio: ' + self.portfolio.name, fontsize=30)
        plt.pie(values, autopct="%1.1f%%", startangle=90, pctdistance=0.65,
                counterclock=False, labeldistance=1.03, explode=explode)
        plt.axis('equal')
        plt.legend(labels)
        plt.savefig(basedir[:-4] + 'static/portfolio_plot.png')


# class definition for optimized portfolio
# to hold methods and attributes needed while optimizing
class OptimizedPortfolio(object):
    """
    Optimized Portfolio Object

    -Used for optimizing portfolio in app
    -Simulates various holding weights
    -Determines optimal portfolio (MPT methodology)
    -Creates new Portfolio in db with optimal holdings
    -Plots optimal portfolio on page with simulated returns

    Parameters
    =========
    portfolio : Portfolio model
        input portfolio to be optimized
    start_date : datetime.date
        start of time-span for historical return analysis

    Methods
    =======
    initialize_parameters:
        initialize input parameters and portfolio market env. data
    simulate_optimize:
        use MCS to simulate portfolio weights and optimize Sharpe's ratio
    gen_eff_plot:
        generate efficient frontier and begin to plot on MPL plot
    plot_capm_opt_save:
        plot CAPM line (if works), plot optimal portfolio, save to static folder
    rebalance_opt_port:
        create optimal portfolio and add optimal holdings to it
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
        # create efficient frontier
        self.evols, self.erets = self.port.get_efficient_frontier(100)
        plt.figure(figsize=(10, 6))
        # plot simulation and efficient frontier
        plt.scatter(self.vols, self.rets, c=self.rets / self.vols, marker='o')
        plt.scatter(self.evols, self.erets, c=self.erets / self.evols, marker='x')
        plt.grid(True)
        # add lines at axis = 0
        plt.axhline(0, color='k', ls='--', lw=2.0)
        plt.axvline(0, color='k', ls='--', lw=2.0)
        # rescale axis
        plt.xlim(xmin=-0.05)
        plt.ylim(ymin=-0.1)
        # add labels and title
        plt.xlabel(r'$\sigma$', fontsize=20)
        plt.ylabel(r'$\mu$', fontsize=20)
        plt.colorbar(label='Sharpe Ratio')
        plt.title('Optimal Holding based on MCS (rf ={}%)'.format(self.rf * 100))

    def plot_capm_opt_save(self):
        try:
            # gen CAPM line and optimal vol and ret
            cml, optv, optr = self.port.get_capital_market_line(riskless_asset=self.rf)
            plt.plot((0, 0.4), (cml(0), cml(0.4)), lw=2.0, label='CAPM Line')
        except ValueError:
            # calculate optimal vol and ret - no CAPM line
            optv = self.port.get_volatility();
            optr = self.port.get_portfolio_return()
        finally:
            plt.plot(optv, optr, 'y*', markersize=20, label='Optimal Portfolio')
            # plot lines from opt portfolio
            plt.plot((optv, optv), (0, optr), 'g-', lw=1.0)
            plt.plot((0, optv), (optr, optr), 'g-', lw=1.0)
            xlocs, xlabels = plt.xticks()
            ylocs, ylabels = plt.yticks()
            xlabels = ["{0:.0f}%".format(100 * xloc) for xloc in xlocs]
            ylabels = ["{0:.0f}%".format(100 * yloc) for yloc in ylocs]
            plt.xticks(xlocs, xlabels)
            plt.yticks(ylocs, ylabels)
            plt.legend(loc=0)
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
