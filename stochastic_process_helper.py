### Stochastic Processes! 

import numpy as np
import pandas as pd

import statsmodels as sm
import random
import math
from collections import defaultdict
from scipy.stats import bernoulli

#----we want to simulate a poisson process

def expo_inv(u,lambda_):
    return -np.log(1-u)/lambda_

def poisson_sim(lambda_,n): 
    """
    Using the inverse CDF sampling method we arrival times of a poisson process with arrival rate lambda
    n-number of samples
    """

    #Step 1: sample n uniform
    unif_sample = [random.uniform(0,1) for i in range(n)]

    #Step 2: get exponential sample using inverse cdf transform
    #Recall that times between poisson proceess arrivals follow exponential dist
    expo_sample = [expo_inv(i,lambda_) for i in unif_sample]

    #Step 3: Cumulative Sum gives us arrival time of posson process
    poisson_arrival = np.cumsum(expo_sample)

    return poisson_arrival

#to do
#random market entry
#design gui - see if dynamic updating 


def market_dir(n):
    """
    Simulate Market Direction
    """
    return bernoulli.rvs(0.5,size = n)



######SIMPLY ORDER ENTRY - MODEL 1 
def market_order_poisson(num_orders,time,lambda_ = 0.25,q = 5):
    """
    time - max length of time for trading
    q - standardized amount per market order (default to 5)
    lambda_ - acverage mkt orders per second
    """

    #step1: generate poisson arrival times, standardize by time
    arrival_time = poisson_sim(0.25,num_orders) #make 100 a parameter 
    arrival_time = list(map(math.ceil,arrival_time/max(arrival_time)*time))

    order_dir = market_dir(len(arrival_time))


    capture = list(zip(arrival_time,order_dir)) 
    m_orders = defaultdict(list)
    for k,v in capture:
        m_orders[k].append(v)
    return m_orders

def limit_order_poisson(num_orders,time,lambda_,q,bid_sched,ask_sched):
    """
    Poisson process of submitting limit orders-independent
    limit order submission at any level at equal probability

    same params as in market order with addition of :
    - bid_sched: initial bid price schedule
    - ask_sched: initial ask price schedule
    """
    arrival_time = poisson_sim(0.1,num_orders)
    arrival_time = list(map(math.ceil,arrival_time/max(arrival_time)*time))

    #price needs to be selected around mid 
    order_dir = market_dir(len(arrival_time))
    level = []
    for i in order_dir:
        if i:
            level.append(np.random.choice(bid_sched)) #bid level
        else:
            level.append(np.random.choice(ask_sched))


    limit_order = list(zip(order_dir,level))
    capture = list(zip(arrival_time,limit_order))
    m_orders = defaultdict(list)
    for k,v in capture:
        m_orders[k].append(v)
    return m_orders

#limit orders 
#cancellations
#split into Queues 
#create functions for statistics on it

#idea - make the poisson time for market orders doubles so that it occurs every other second
#get data for maximum likelihood estimation