#Creating an orderbook!

import pandas as pd
import numpy as np
from collections import defaultdict, OrderedDict
from IPython.display import display,HTML

import ipywidgets as widgets 

class Book:
    """
    Iniatlize and alter book using mkt and limit orders
    Should display as a dataframe
    """
    def __init__(self,mid):
        self.mid = mid
        self.bid_side_gen() #think of these as queues 
        self.ask_side_gen()
        self.book = self.generate_book()
    
    def bid_side_gen(self):
        """
        Initialize Bid side of Book
        Add in more functionality to have imbalance
        """
        
        self.bid_sched = [self.mid-0.01*i for i in range(1,11,1)] #10 levels deep
        self.bid_vol_sched = [int(100 - 10*i) for i in range(10)] #exponentially decreasing vol sched
        self.bid_vol_dict = [{i*1000:self.bid_vol_sched[i-1]} for i in range(1,len(self.bid_vol_sched)+1,1)]
        # return defaultdict(list,(zip(self.bid_sched,self.bid_vol_sched)))
        self.bid_side =  defaultdict(dict,(zip(self.bid_sched,self.bid_vol_dict)))      

    def ask_side_gen(self):
        """
        Initialize Bid side of Book
        Add in more functionality to have imbalance
        """
        self.ask_sched = [self.mid+0.01*i for i in range(1,11,1)] #10 levels deep
        self.ask_vol_sched = [int(100 - 10*i) for i in range(10)] #exponentially decreasing vol sched
        self.ask_vol_dict = [{-i*1000:self.ask_vol_sched[i-1]} for i in range(1,len(self.ask_vol_sched)+1,1)]
        self.ask_side =  defaultdict(dict,(zip(self.ask_sched,self.ask_vol_dict)))

    def generate_book(self):
        """
        Always show the top 10 - if none then it should be 0
        """

        ask_side = self.ask_side.copy()
        bid_side = self.bid_side.copy()

        #remove empty portions
        ask_side = {i:{t:v for t,v in ask_side[i].items() if v != 0} for i in ask_side.keys()}
        bid_side = {i:{t:v for t,v in bid_side[i].items() if v != 0} for i in bid_side.keys()}

        #Initialize numpy arrays
     

        book_gen = pd.DataFrame()
        bids = list(bid_side.keys())
        bids.sort(reverse = True)
        bid_vols = pd.Series([bid_side[k] for k in bids ])
        bids = pd.Series(bids)
        bid_total = pd.Series([sum(bid_side[k].values()) for k in bid_side.keys()])


        asks = list(ask_side.keys())
        asks.sort()
        ask_vols = pd.Series([ask_side[k] for k in asks ])
        asks = pd.Series(asks)
        ask_total = pd.Series([sum(ask_side[k].values()) for k in ask_side.keys()])

        levels = max(len(bids),len(asks))
        book_gen['Level'] = np.arange(1,levels+1,1)

        book_gen['Bids'] = bids
        book_gen['Bid_Vol'] = bid_vols
        book_gen['Bid Total'] = bid_total
        book_gen['Asks'] = asks
        book_gen['Ask_Vols'] = ask_vols
        book_gen['Ask Total'] = ask_total
        book_gen = book_gen[['Level','Bid_Vol','Bid Total','Bids','Asks','Ask Total','Ask_Vols']]
        self.book = book_gen
        return book_gen.to_html(index = None)
        
    def display_book(self):
        self.book = self.generate_book()
        return HTML(self.book.to_html(index = False))

    def order_enter(self,action,amount, price=0,type='MKT'):
        total_amount = amount

        if action == "BUY":
            if type == 'MKT':
                avg_price = 0
                
                for k in self.ask_side.keys(): 
                    v = self.ask_side[k]
                    for q in v.keys(): #so now v is a dict
                        new_amount = max(0,amount-v[q]) #make as key
                
                        if new_amount == 0:
                            avg_price += amount*k
                        
                            self.ask_side[k][q] = v[q] - amount #works
                            msg = "ACTION: BUY, AMOUNT : " + str(amount) + ", PRICE: " + str(round(avg_price/total_amount,2))
                            return msg
                        else:
                            avg_price += k*v[q]
                            amount = new_amount
                            self.ask_side[k][q] = 0                   
                
            elif type =='LMT':
                # self.bid_side[price].append(amount)
                # SECTION FOR DICTIONARY RETURN 
                id = list(self.bid_side[price].keys())[-1] 
                if id == 'MM': #Market Making Algo ID
                    id = list(self.bid_side[price].keys)[-2]
                
                id += 1
                self.bid_side[price][id] = amount
                
                
                msg = "ORDER ID: " + str(id) + ", ACTION: BUY,  AMOUNT: " + str(amount) + ", PRICE: " + str(price)
                return msg
            
            else:
                print("Please enter value type: either 'MKT' or 'LMT'")
                return None
        
        elif action == "SELL":
            if type == 'MKT':
                
                avg_price = 0
                
                for k in self.bid_side.keys(): 
                    v = self.bid_side[k]
                    for q in v.keys(): #v is a qqueue
                        new_amount = max(0,amount-v[q])
                
                        if new_amount == 0:
                            avg_price += amount*k
                        
                            self.bid_side[k][q] = v[q] - amount
                            msg = "ACTION: SELL, AMOUNT : " + str(amount) + ", PRICE: " + str(round(avg_price/total_amount,2))
                            return msg
                        else:
                            avg_price += k*v[q]
                            amount = new_amount
                            self.bid_side[k][q] = 0                       
                   
                
            elif type =='LMT':
                id = list(self.ask_side[price].keys())[-1] 
                if id == 'MM': #Market Making Algo ID
                    id = list(self.ask_side[price].keys)[-2]
                
                id -= 1
                self.ask_side[price][id] = amount
                
                
                msg = "ORDER ID: " + str(id) + ", TYPE: SELL,  AMOUNT: " + str(amount) + ", PRICE: " + str(price)
                return msg

            
            else:
                print("Please enter value type: either 'MKT' or 'LMT'")
                return None
                
        else:
            print("Please enter a valid Action: either 'BUY' or 'SELL'")
            return None

    def cancel_order(self,dir_,level,id_):
        if dir_:
            self.bid_side[level][id_] = 0
            msg = 'ORDER ID: ' + str(id_) + ", TYPE: CANCEL, SIDE: BID"
            return msg
        else:
            self.ask_side[level][id_] = 0
            msg = 'ORDER ID: ' + str(id_) + ", TYPE: CANCEL, SIDE: ASK"
            return msg

def generate_book(book):
    """
    Always show the top 10 - if none then it should be 0
    """

    ask_side = book.ask_side
    bid_side = book.bid_side

    #remove empty portions
    # ask_side = {k:v for k,v in ask_side.items() if np.sum(v) != 0}
    # bid_side = {k:v for k,v in bid_side.items() if np.sum(v) != 0}

    #Initialize numpy arrays
 

    book = pd.DataFrame()
    bids = list(bid_side.keys())
    bids.sort(reverse = True)
    bid_vols = pd.Series([bid_side[k] for k in bids ])
    bids = pd.Series(bids)


    asks = list(ask_side.keys())
    asks.sort()
    ask_vols = pd.Series([ask_side[k] for k in asks ])
    asks = pd.Series(asks)

    levels = max(len(bids),len(asks))
    book['Level'] = np.arange(1,levels,1)

    book['Bids'] = bids
    book['Bid_Vol'] = bid_vols
    book['Asks'] = asks
    book['Ask_Vols'] = ask_vols
    
    return book





