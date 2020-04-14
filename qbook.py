# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 00:31:33 2020

@author: kevin
"""

#Gui Helper
import pandas as pd
import numpy as np
from ob_helper import * 
from stochastic_process_helper import *
import time as t
from IPython.display import display,HTML
from IPython.display import clear_output
import ipywidgets as widgets 
import matplotlib.pyplot as plt

# default = {'time':30 ,'num_market':50, 'lambda_market': 2, 'vol_mkt': 10, 'num_limit': 50, 'lambda_limit':5,  'vol_lmt' :10}
default = {'time':30 ,'lambda_market': 2, 'vol_mkt': 10, 'lambda_limit':5,  'vol_lmt' :10, 'lambda_cancel':3}

# class Q_Book():
#     default = {'time':30 ,'num_market':50, 'lambda_market': 0.25, 'vol_mkt': 10, 'num_limit': 50, 'lambda_limit':0.25,  'vol_lmt' :10}
def poisson_book(time , lambda_market, vol_mkt,  lambda_limit, vol_lmt, lambda_cancel):
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
    cancel_arrivals = poisson_arrival(time, lambda_cancel)

   
    msgs = []
    lmts = []
    cncls = []
    mids = [100]

    time_step = 0
    dict_book[time_step] =  book.generate_book()
    dict_om[time_step] =  pd.DataFrame(msgs,columns = [' Market Orders'])
    dict_lm[time_step] = pd.DataFrame(lmts,columns = ['Limit Orders'])
    dict_cnl[time_step] = pd.DataFrame(cncls,columns = ['Cancels'])

    
    for t in range(1,time+1,1) :
        time_step = int(t)
        m_orders = market_orders[time_step]
        l_orders = limit_orders[time_step]
        c_orders = cancel_arrivals[time_step]


        msgs = []
        lmts = []
        cnl = []
        

        #Market Orders
        for i in m_orders:
            if i:
                msgs.append(book.order_enter('BUY',vol_mkt))
            else:
                msgs.append(book.order_enter('SELL',vol_mkt))
            
            #cancel order

        #Limit Orders        
        for i in l_orders:
            if i[0]:
                lmts.append(book.order_enter('BUY',vol_lmt,price = i[1],type = 'LMT'))
            else:
                lmts.append(book.order_enter('SELL',vol_lmt,price = i[1],type = 'LMT'))
        
        
        for i in range(c_orders): #number of cancellations in this time step
            canc_deets = cancel_order_rand(book)
            cnl.append(book.cancel_order(*canc_deets))


        mids.append(book.book_mid())

        dict_book[time_step] = book.generate_book()
        dict_om[time_step] =  pd.DataFrame(msgs,columns = [' Market Orders'])
        dict_lm[time_step] = pd.DataFrame(lmts,columns = ['Limit Orders'])
        dict_cnl[time_step] = pd.DataFrame(cnl,columns = ['Cancels'])

    return dict_book,dict_lm,dict_om, dict_cnl, mids

        
    

def GUI_construct(**kwargs):
    book_dict,lmt_dict,om_dict,dict_cnl, mids= poisson_book(**kwargs)
    def view_book_time(time_step=0):
        return HTML(book_dict[time_step].to_html(index = None))

    def view_msg_time(time_step=0):
        return HTML(om_dict[time_step].to_html(index = None))
    
    def view_lmt_time(time_step=0):
        return HTML(lmt_dict[time_step].to_html(index = None))
    
    def view_cnl_time(time_step = 0):
        return HTML(dict_cnl[time_step].to_html(index = None))
    
    def view_mid_time(time_step = 0):
        return mids[time_step]
    
    def view_mid_graph(time_step = 0):
        mid_select = mids[:time_step]
        return mid_select

        
    def book_display(time_step = 0):
        book = view_book_time(time_step)
        book_out = widgets.Output()
        with book_out:
            display(HTML("<b> Q-BOOK </b>"))
            display(book)
        return display(book_out)
        
    def messages_display(time_step = 0):
        msg = view_msg_time(time_step)
        lmt = view_lmt_time(time_step)
        cnl = view_cnl_time(time_step)
        msg_out = widgets.Output()
        lmt_out = widgets.Output()
        cnl_out = widgets.Output()

        with msg_out:
            display(msg)
        with lmt_out:
            display(lmt)
        with cnl_out:
            display(cnl)
            
        message_box = widgets.HBox([msg_out,lmt_out,cnl_out])

        return display(message_box)
    
    def mid_graph(time_step = 0):
        mids = view_mid_time(time_step)
        mid_select = view_mid_graph(time_step)
        

        mid_out = widgets.Output()
        mid_graph = widgets.Output()
        
        with mid_out:
            display(HTML('MID'))
            display(mids)
            
        with mid_graph:
            x= np.arange(1,len(mid_select)+1,1)
            plt.plot(x,mid_select)
            _= plt.xlabel('Time Step')
            _= plt.ylabel('Mid Price')
            _= plt.title('Mid Price Time Series')
            _= plt.xticks(x)
            plt.show()
            

        mid_box = widgets.VBox([mid_out,mid_graph])
        
        return display(mid_box)

    time = kwargs['time']
    w = widgets.IntSlider(min = 0, max = time,step =1,description='Time Step:')
    book_widget = widgets.interactive(book_display,time_step=w)
    msg_widget = widgets.interactive(messages_display,time_step=w)
    mid_widget = widgets.interactive(mid_graph,time_step=w)
    return w,book_widget,msg_widget,mid_widget


def setting_panels():
    time_setting = widgets.IntText(value=30,description='Time:', disabled=False,layout=widgets.Layout(width='85%'))
    lambda_market_setting = widgets.IntText(value=5,description='Lambda:', disabled=False,layout=widgets.Layout(width='85%'))
    market_volume_setting = widgets.IntText(value=10,description='Vol per Order:', disabled=False,layout=widgets.Layout(width='85%'))
    lambda_limit_setting = widgets.IntText(value=2,description='Lambda:', disabled=False,layout=widgets.Layout(width='85%'))
    limit_volume_setting = widgets.IntText(value=25,description='Vol per Order:', disabled=False,layout=widgets.Layout(width='85%'))
    lambda_cancel_setting = widgets.IntText(value=2,description='Lambda:', disabled=False,layout=widgets.Layout(width='85%'))
    gen_button = widgets.Button(description = "Generate Q Book", disabled = False)
    
    def generate_q_book(b):
        settings = {'time':time_setting.value ,'lambda_market': lambda_market_setting.value, \
                    'vol_mkt': market_volume_setting.value,'lambda_limit':lambda_limit_setting.value,\
                        'vol_lmt' :limit_volume_setting.value, 'lambda_cancel': lambda_cancel_setting.value}
        clear_output()
        display(gen_button)
        return display(QBook(**settings))
    
    gen_button.on_click(generate_q_book)
    time_gen = widgets.Box([time_setting])
    mkt_set = widgets.VBox(([lambda_market_setting,market_volume_setting]))
    lmt_set = widgets.VBox(([lambda_limit_setting,limit_volume_setting]))
    cnl_set = widgets.Box([lambda_cancel_setting])
    
    out_left = widgets.Output()
    out_middle = widgets.Output()
    out_right = widgets.Output()
    out_far = widgets.Output()
    
    
    
    with out_left:
        display(HTML('<b>Time Steps<b/>'))
        display(time_gen)

    
    with out_middle:
        display(HTML('<b>Market Settings</b>'))
        display(mkt_set)
    
    with out_right:
        display(HTML('<b>Limit Settings</b>'))
        display(lmt_set)
    
    with out_far:
        display(HTML('<b>Cancel Settings</b>'))
        display(cnl_set)
    
    master_settings = widgets.HBox([out_left,out_middle,out_right, out_far])

    
    return master_settings,gen_button

def_settings = {'time':30 ,'lambda_market': 2, 'vol_mkt': 10,'lambda_limit':2,'vol_lmt' :20, 'lambda_cancel': 2}
def QBook(**settings):
    """
    1. Generate Q_book with time_step linkage
    2. Generate Tabs: Settings, Messages, Price Movement
    """
    slider, book_w,messages_w, mid_w = GUI_construct(**settings)
    settings,gen_button = setting_panels()
    top = widgets.Box([book_w])
    tab_master = widgets.Tab(titles = ['Settings','Message Log','Mid Price Graph'])
    children = [settings,messages_w,mid_w]
    tab_master.children = children
    labels = ['Settings','Message Log','Mid Price Graph']
    for i,l in enumerate(labels):
        tab_master.set_title(i, l)
    full = widgets.VBox([top,tab_master])
    return full

def QBook_GUI():
    settings,gen_button = setting_panels()
    display(gen_button)
    return display(QBook(**def_settings))