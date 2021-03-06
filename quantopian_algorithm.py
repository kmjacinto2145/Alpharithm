'''
Created by: Sandeep Das, Jim Ng, Michael Jacinto, Ashish Matthew
'''

from sklearn.ensemble import RandomForestClassifier
from collections import deque
import talib  
import numpy as np

def initialize(context):
    set_long_only()
    set_max_order_count(1)
    context.spy = sid(8554)
    


    # # # ML INIT
    context.security = sid(19920) # QQQ
    context.window_length = 10 # Amount of prior bars to study, originally 10

    context.classifier = RandomForestClassifier() # Use a random forest classifier
    # deques are lists with a maximum length where old entries are shifted out
    context.recent_prices = deque(maxlen=context.window_length+2) # Stores recent prices
    context.X = deque(maxlen=500) # Independent, or input variables
    context.Y = deque(maxlen=500) # Dependent, or output variable
    context.prediction = 0 # Stores most recent prediction
    # # # ML INIT

    
    schedule_function(handle_data, date_rules.every_day(), time_rules.market_open())        
    context.longed = False
    

def vwap(prices, volumes):
    return (prices * volumes).sum() / volumes.sum()

def vwap_std(prices, volumes, bar_count):
    deviation_sum = 0
    
    for day in prices.index:
        deviation_sum += (prices[day] - vwap(prices, volumes)) ** 2
        
    return (1/(bar_count - 1) * deviation_sum) ** (1/2)


def handle_data(context, data):  
    spy = context.spy    
    bar_count = 30
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # Michael's Stuff
    p_history = data.history(context.spy, fields="close", bar_count = bar_count, frequency="1d")
    v_history = data.history(context.spy, fields="volume", bar_count = bar_count, frequency="1d")
    
    price_d1 = np.diff(p_history)
    obv_d1 = np.diff(talib.OBV(p_history, v_history))
    
    price_d1_norm = (price_d1[-1] - np.mean(price_d1)) / np.std(price_d1)
    #obv_d1_norm = (obv_d1[-1] - np.mean(obv_d1)) / np.std(obv_d1)
    obv_d1_norm = obv_d1[-1] / np.std(obv_d1)
    
    std_30 = np.std(p_history)
    
    vwap1 = vwap(p_history, v_history)
    
    vwap_norm = (p_history[-1] - vwap1) / vwap_std(p_history, v_history, bar_count)
    
    print(vwap_norm)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    
    # # # # # # # # # # # # # # # # # # # # # # # # 
    # ML STUFF
    context.recent_prices.append(data.current(context.security, 'price')) # Update the recent prices
    if len(context.recent_prices) == context.window_length+2: # If there's enough recent price data
    # Make a list of 1's and 0's, 1 when the price increased from the prior bar
        changes = np.diff(context.recent_prices) > 0
        
        context.X.append(changes[:-1]) # Add independent variables, the prior changes
        context.Y.append(changes[-1]) # Add dependent variable, the final change
        if len(context.Y) >= 100: # There needs to be enough data points to make a good model
            context.classifier.fit(context.X, context.Y) # Generate the model
            context.prediction = context.classifier.predict(changes[1:]) # Predict
            log.debug(context.security)
            # If prediction = 1, buy all shares affordable, if 0 sell all shares
            context.security = sid(8554) #change back to SPY
            # order_target_percent(context.security, int(context.prediction))

    # # # # # # # # # # # # # # # # # # # # # # # # 
    # Michael's Stuff
            if std_30 > 0:
        
                if obv_d1_norm + vwap_norm > 0.5 and context.longed is False:
                    try:
                        order_target_percent(spy, 0.25*int(context.prediction) + 0.75)
                        context.longed = True
                    except:
                        pass
                elif obv_d1_norm + vwap_norm < -0.5 and context.longed is True:
                    try:
                        order_target_percent(spy, 0.25*int(context.prediction))   
                        context.longed = False
                    except:
                        pass

            context.security = sid(19920) #track QQQ again ## ML
    # # # # # # # # # # # # # # # # # # # # # # # # 

    
    record(vwap_norm = vwap_norm)
    record(obv_d1_norm = obv_d1_norm)
