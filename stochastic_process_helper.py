### Stochastic Processes! 

import numpy as np
import pandas as pd

import statsmodels as sm
import random
import math
from collections import defaultdict, Counter
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
def market_order_poisson(time,lambda_ = 0.25,q = 5):
    """
    time - max length of time for trading
    q - standardized amount per market order (default to 5)
    lambda_ - acverage mkt orders per second
    """
    num_orders = time*lambda_
    #step1: generate poisson arrival times, standardize by time
    arrival_time = poisson_sim(0.25,num_orders) #make 100 a parameter 
    arrival_time = list(map(math.ceil,arrival_time/max(arrival_time)*time))

    order_dir = market_dir(len(arrival_time))


    capture = list(zip(arrival_time,order_dir)) 
    m_orders = defaultdict(list)
    for k,v in capture:
        m_orders[k].append(v)
    return m_orders

def limit_order_poisson(time,lambda_,q,book):
    """
    Poisson process of submitting limit orders-independent
    limit order submission at any level at equal probability

    same params as in market order with addition of :
    - bid_sched: initial bid price schedule
    - ask_sched: initial ask price schedule
    """
    bid_sched = book.bid_sched
    ask_sched = book.ask_sched
    num_orders = time*lambda_
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

def poisson_arrival(time,lambda_):
    """
    Poisson Arrival
    """
    num_orders = time*int(lambda_)
    arrival_time = poisson_sim(0.1,num_orders)
    arrival_time = list(map(math.ceil,arrival_time/max(arrival_time)*time))
    return Counter(arrival_time)

def cancel_order_rand(book):
    """
    random selection of direction, level, and id for cancellation
    """
    bid_side = book.bid_side.copy()
    ask_side = book.ask_side.copy()


    #get level
    #get side
    #get id 
    
    #level
    
    order_dir = bernoulli.rvs(0.5,size = 1)
    if order_dir:
        while True:
            random_level  = np.random.choice(list(bid_side.keys())) #level
            if len(bid_side[random_level]) != 0:
                break
                    
        id_choice = np.random.choice(list(bid_side[random_level].keys())) #id keys

    else:
        while True:
            random_level  = np.random.choice(list(ask_side.keys()))
            if len(ask_side[random_level]) != 0:
                break
        id_choice = np.random.choice(list(ask_side[random_level].keys()))



    return [order_dir,random_level,id_choice]


#limit orders 
#cancellations
#split into Queues 
#create functions for statistics on it

#idea - make the poisson time for market orders doubles so that it occurs every other second
#get data for maximum likelihood estimation