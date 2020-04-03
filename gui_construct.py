#Gui Helper
import pandas as pd
import numpy as np
from ob_helper import * 
from stochastic_process_helper import *
import time 
from IPython.display import display,HTML

import ipywidgets as widgets 

def main_loop(n):
    """
    gui display
    """
    #initialize book
    book = Book(100)

    #initialize market_orders
    market_orders = market_order_poisson()
    #need to find a way to standardize inputs 
    limit_orders = limit_order_poisson(100,30,0.25,5,book.bid_sched,book.ask_sched)

    time_step = 0 
    index = 0
    while time_step < n +1 :
        m_orders = market_orders[time_step]
        l_orders = limit_orders[time_step]
        msgs = []
        lmts = []
        #Market Orders
        for i in m_orders:
            if i:
                msgs.append(book.order_enter('BUY',5))
            else:
                msgs.append(book.order_enter('SELL',5))
        #Limit Orders        
        for i in l_orders:
            if i[0]:
                lmts.append(book.order_enter('BUY',5,price = i[1],type = 'LMT'))
            else:
                lmts.append(book.order_enter('SELL',5,price = i[1],type = 'LMT'))
                
        time_step += 1
        book_widget = widgets.Output(layout={'border': '1px solid black'})
        with book_widget:
            display('Time step: '+str(time_step))
            display(HTML(book.generate_book().to_html(index = None)))

        msg_widget = widgets.Output(layout={'border': '1px solid black'})
        lmt_widget = widgets.Output(layout={'border': '1px solid black'})
        with msg_widget:
            display(HTML(pd.DataFrame(msgs,columns = ['Orders']).to_html(index = None)))

        with lmt_widget:
            display(HTML(pd.DataFrame(lmts,columns = ['Limits Placements']).to_html(index = None)))
            

        master = widgets.HBox([book_widget,msg_widget,lmt_widget])
        display(master)
        time.sleep(1)
        book_widget.clear_output()
        msg_widget.clear_output()
        lmt_widget.clear_output()