#Gui Helper
import pandas as pd
import numpy as np
from ob_helper import * 
from stochastic_process_helper import *
import time as t
from IPython.display import display,HTML
from IPython.display import clear_output
import ipywidgets as widgets 

def main_loop(time,num_market = 100, num_limit = 100,display_live = True ):
    """
    gui display
    """
    #initialize book
    book = Book(100)
    dict_book = {}
    dict_lm = {}
    dict_om = {}

    #initialize market_orders
    market_orders = market_order_poisson(num_market,time)
    #need to find a way to standardize inputs 
    limit_orders = limit_order_poisson(num_limit,time,0.25,5,book.bid_sched,book.ask_sched)

    time_step = 0 
    index = 0
    

    while time_step < time +1 :
        m_orders = market_orders[time_step]
        l_orders = limit_orders[time_step]
        msgs = []
        lmts = []
        
        book_widget = widgets.Output(layout={'border': '1px solid black'})
        msg_widget = widgets.Output(layout={'border': '1px solid black'})
        lmt_widget = widgets.Output(layout={'border': '1px solid black'})
    
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
        
        with book_widget:
            display('Time step: '+str(time_step))
            book_i = book.generate_book()
            display(HTML(book_i.to_html(index = None)))
            dict_book[time_step-1] = book_i
            


        with msg_widget:
            om = pd.DataFrame(msgs,columns = ['Orders'])
            display(HTML(om.to_html(index = None)))
            dict_om[time_step-1]=  om
                        

        with lmt_widget:
            lm = pd.DataFrame(lmts,columns = ['Limits Placements'])
            display(HTML(lm.to_html(index = None)))
            dict_lm[time_step-1] = lm
        
        if display_live:
            display(widgets.HBox([book_widget,msg_widget,lmt_widget]))
            t.sleep(1)
            clear_output(wait = True)

            book_widget.clear_output()
            msg_widget.clear_output()
            lmt_widget.clear_output()
        
    return dict_book,dict_lm,dict_om

def GUI_construct(time,display_live = False):
    a,b,c = main_loop(time)
    def view_book_time(time_step=3):
        return HTML(a[time_step].to_html(index = None))

    def view_msg_time(time_step=3):
        return HTML(c[time_step].to_html(index = None))
    
    def view_lmt_time(time_step=3):
        return HTML(b[time_step].to_html(index = None))
        
        
    def master(time_step = 3):
        book = view_book_time(time_step)
        msg = view_msg_time(time_step)
        lmt = view_lmt_time(time_step)
        book_out = widgets.Output()
        msg_out = widgets.Output()
        lmt_out = widgets.Output()
        with book_out:
            display(book)
        with msg_out:
            display(msg)
        with lmt_out:
            display(lmt)
        return display(widgets.HBox([book_out,msg_out,lmt_out]))    

    
    w = widgets.IntSlider(min = 0, max = time,step =1)
    master_widget = widgets.interactive(master,time_step=w)
    return display(master_widget)