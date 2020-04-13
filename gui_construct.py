#Gui Helper
import pandas as pd
import numpy as np
from ob_helper import * 
from stochastic_process_helper import *
import time as t
from IPython.display import display,HTML
from IPython.display import clear_output
import ipywidgets as widgets 

# default = {'time':30 ,'num_market':50, 'lambda_market': 2, 'vol_mkt': 10, 'num_limit': 50, 'lambda_limit':5,  'vol_lmt' :10}
default = {'time':30 ,'lambda_market': 2, 'vol_mkt': 10, 'lambda_limit':5,  'vol_lmt' :10}

# class Q_Book():
#     default = {'time':30 ,'num_market':50, 'lambda_market': 0.25, 'vol_mkt': 10, 'num_limit': 50, 'lambda_limit':0.25,  'vol_lmt' :10}
def main_loop(time , lambda_market, vol_mkt,  lambda_limit, vol_lmt):
    """
    gui display
    """
    #initialize book
    book = Book(100)

    dict_book = defaultdict(pd.DataFrame)
    dict_lm = {}
    dict_om = {}
    dict_cnl = {}

    #initialize market_orders
    market_orders = market_order_poisson(time, lambda_market,vol_mkt)

    #need to find a way to standardize inputs 
    limit_orders = limit_order_poisson(time,lambda_limit,vol_lmt,book)
    
    #cancellations
    

   
    msgs = []
    lmts = []
    cncls = []

    time_step = 0
    dict_book[time_step] =  book.generate_book()
    dict_om[time_step] =  pd.DataFrame(msgs,columns = [' Market Orders'])
    dict_lm[time_step] = pd.DataFrame(lmts,columns = ['Limit Orders'])
    dict_cnl[time_step] = pd.DataFrame(cncls,columns = ['Cancels'])
    
    for t in range(1,time+1,1) :
        time_step = int(t)
        m_orders = market_orders[time_step]
        l_orders = limit_orders[time_step]
        cancels = cancel_order_poisson(1, lambda_limit, book)
        c_orders = cancels[time_step]
        msgs = []
        lmts = []
        cnl = []

        #Market Orders
        for i in m_orders:
            if i:
                msgs.append(book.order_enter('BUY',vol_mkt))
            else:
                msgs.append(book.order_enter('SELL',vol_mkt))
        #Limit Orders        
        for i in l_orders:
            if i[0]:
                lmts.append(book.order_enter('BUY',vol_lmt,price = i[1],type = 'LMT'))
            else:
                lmts.append(book.order_enter('SELL',vol_lmt,price = i[1],type = 'LMT'))
        
        for i in c_orders:
            cnl.append(book.cancel_order(i[0],i[1],i[2]))




        dict_book[time_step] = book.generate_book()
        dict_om[time_step] =  pd.DataFrame(msgs,columns = [' Market Orders'])
        dict_lm[time_step] = pd.DataFrame(lmts,columns = ['Limit Orders'])
        dict_cnl[time_step] = pd.DataFrame(cnl,columns = ['Cancels'])

    return dict_book,dict_lm,dict_om, dict_cnl 

        
    

def GUI_construct(**kwargs):
    book_dict,lmt_dict,om_dict,dict_cnl = main_loop(**kwargs)
    def view_book_time(time_step=0):
        return HTML(book_dict[time_step])

    def view_msg_time(time_step=0):
        return HTML(om_dict[time_step].to_html(index = None))
    
    def view_lmt_time(time_step=0):
        return HTML(lmt_dict[time_step].to_html(index = None))
    
    def view_cnl_time(time_step = 0):
        return HTML(dict_cnl[time_step].to_html(index = None))
        
        
    def master(time_step = 0):
        book = view_book_time(time_step)
        msg = view_msg_time(time_step)
        lmt = view_lmt_time(time_step)
        cnl = view_cnl_time(time_step)
        
        book_out = widgets.Output()
        msg_out = widgets.Output()
        lmt_out = widgets.Output()
        cnl_out = widgets.Output()
        with book_out:
            display(book)
        with msg_out:
            display(msg)
        with lmt_out:
            display(lmt)
        with cnl_out:
            display(cnl)
        message_box = widgets.HBox([msg_out,lmt_out,cnl_out])
        
        return display(widgets.VBox([book_out, message_box]))    

    time = kwargs['time']
    w = widgets.IntSlider(min = 0, max = time,step =1,description='Time Step:')
    master_widget = widgets.interactive(master,time_step=w)
    return master_widget


def setting_panels():
    time_setting = widgets.IntText(value=7,description='Time:', disabled=False)
    lambda_market_setting = widgets.IntText(value=7,description='Lambda:', disabled=False)
    market_volume_setting = widgets.IntText(value=7,description='Vol per Order:', disabled=False)
    lambda_limit_setting = widgets.IntText(value=7,description='Lambda:', disabled=False)
    limit_volume_setting = widgets.IntText(value=7,description='Vol per Order:', disabled=False)
    
    gen_button = widgets.Button(description = "Generate Q Book", disabled = False)
    
    def generate_q_book(b):
        settings = {'time':time_setting.value ,'lambda_market': lambda_market_setting.value, \
                    'vol_mkt': market_volume_setting.value,'lambda_limit':lambda_limit_setting.value,  'vol_lmt' :limit_volume_setting.value}
        clear_output()
        display(gen_button)
        return display(GUI_construct(**settings))
    
    gen_button.on_click(generate_q_book)
    time_gen = widgets.Box([time_setting])
    mkt_set = widgets.VBox(([lambda_market_setting,market_volume_setting]))
    lmt_set = widgets.VBox(([lambda_limit_setting,limit_volume_setting]))
    
    out_left = widgets.Output()
    out_middle = widgets.Output()
    out_right = widgets.Output()
    
    bottom = widgets.Output()
    with bottom:
        display(gen_button)
    
    with out_left:
        display(HTML('<b>Generate<b/>'))
        display(time_gen)
    
    with out_middle:
        display(HTML('<b>Market Settings</b>'))
        display(mkt_set)
    
    with out_right:
        display(HTML('<b>Limit Settings</b>'))
        display(lmt_set)
    
    master_top = widgets.HBox([out_left,out_middle,out_right])
    master = widgets.VBox([master_top,bottom])
    
    return master
