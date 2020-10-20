def initialize(context):
    context.stock = symbol('AAPL')  
    #context.obv = None  
    #context.running_obv = None 
 
def handle_data(context, data):
    stock = context.stock   
    stock_data = data[stock]
 
    mavg_short = stock_data.mavg(5)
    mavg_long = stock_data.mavg(30)
    current_price = stock_data.price
 
    cash = context.portfolio.cash
   
    if mavg_short > mavg_long and cash > current_price:
        number_of_shares = int(cash/current_price)
        order(stock, number_of_shares)
    
    elif mavg_short < mavg_long:
        number_of_shares = context.portfolio.positions[stock.sid].amount
        order(stock, -number_of_shares) # When selling we need to pass a negative number of shares
