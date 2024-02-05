import requests

authorizationToken = "enctoken"

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Authorization": authorizationToken
    }

# Creating a map to store tradingsymbol as key, trigger_values and type as value if status is active
symbol_triggers = {}

# Creating a map to store symbol as key and last_price and average_price as values
symbol_prices = {}

def updateTriggerMap():
    url = "https://kite.zerodha.com/oms/gtt/triggers"
        # Adding the new authorization token in the headers
    
    try:
        response = requests.get(url, headers=headers)
        print(response.json)

        if response.status_code == 200:
            data = response.json()

            for item in data.get("data", []):
                id = item.get("id")
                status = item.get("status")
                expires_at = item.get("expires_at")
                exchange = item.get("condition", {}).get("exchange")
                symbol = item.get("condition", {}).get("tradingsymbol")
                trigger_values = item.get("condition", {}).get("trigger_values")
                gtt_type = item.get("type")

                orders = item["orders"]
                order_1 = orders[0]
                #order_2 = orders[1]

                transaction_type = order_1["transaction_type"]
                quantity = order_1["quantity"]
                order_type = order_1["order_type"]
                product = order_1["product"]
                quantity = order_1["quantity"]

                #print(id, status, expires_at, exchange, symbol, trigger_values, gtt_type, quantity, order_type, product)

                symbol_triggers[symbol] = {
                    "id": id,
                    "status": status,
                    "expires_at": expires_at,
                    "exchange": exchange,
                    "trigger_values": trigger_values,
                    "type": gtt_type,
                    "transaction_type": transaction_type,
                    "quantity": quantity,
                    "order_type": order_type,
                    "product": product,
                    "quantity": quantity
                }

            # # Printing the map containing symbol, trigger_values and type for active triggers
            # for symbol, info in symbol_triggers.items():
            #     print(f"Symbol: {symbol}, Trigger Values: {info['trigger_values']}, Type: {info['type']}")

        else:
            print("Failed to fetch data from the API.")

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")

def printTriggerValues(transactionType):
    url = "https://kite.zerodha.com/oms/portfolio/holdings"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            for item in data.get("data", []):
                symbol = item.get("tradingsymbol")
                last_price = item.get("last_price")
                average_price = item.get("average_price")
                quantity = item.get("quantity")

                symbol_prices[symbol] = {"last_price": last_price, "average_price": average_price, "quantity": quantity}
                

            # Printing the map containing symbol, last_price, and average_price
            for symbol, prices in symbol_prices.items():
                if symbol in symbol_triggers:
                    gtt = symbol_triggers[symbol]
                    trigger_qty = gtt['quantity']
                    total_qty = prices['quantity']
                    if gtt['type'] == "two-leg" and transactionType == "SELL":
                        last_price = prices['last_price']
                        average_price = prices['average_price']

                        percentage_change = (last_price - average_price)/average_price * 100

                        if percentage_change > 10.00:
                            percentage_change = 10.00

                        trigger_percentage = percentage_change/200

                        new_sell_price_trigger = last_price - (last_price * trigger_percentage)
                        new_sell_price_trigger = round(new_sell_price_trigger, 1)
                    
                        if new_sell_price_trigger > average_price and new_sell_price_trigger >  gtt['trigger_values'][0] and trigger_percentage >= 0.01:
                            old_trigger_values = "[" + str(gtt['trigger_values'][0]) + ", " + str(gtt['trigger_values'][1]) + "]"

                            new_trigger_values = "[" + str(new_sell_price_trigger) + ", " + str(new_sell_price_trigger + new_sell_price_trigger) + "]"
                            print("{:<20} {:20} {:20} {:>20}".format(symbol, str(trigger_qty)+"/"+str(total_qty), old_trigger_values, new_trigger_values))
                    elif gtt['type'] == "single" and transactionType == "BUY":
                        last_price = prices['last_price']
                        average_price = prices['average_price']

                        new_buy_price_trigger = last_price + (last_price * 0.05)
                        rounded_trigger = round(new_buy_price_trigger / 0.05) * 0.05  # rounding to nearest multiple of 0.05
                        rounded_trigger = round(rounded_trigger, 2)  # ensuring two decimal places
                        new_buy_price_trigger = rounded_trigger
                        print(f"{symbol}: \t\t avg buy price: {average_price}, last_price: {last_price:<10.2f} \t\t old trigger values:{gtt['trigger_values']} \t\t new trigger values: {new_buy_price_trigger}")
        else:
            print("Failed to fetch data from the API.")

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")

def modifyTrigger(url, payload):
    print("url is ", url)
    print("payload is ", payload)
    try:
        response = requests.put(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            trigger_id = data.get("data", {}).get("trigger_id")

            print(f"Status: {status}, Trigger ID: {trigger_id}")
        else:
            print("Failed to perform the PUT request.")

    except requests.RequestException as e:
        print(f"Error during the PUT request: {e}")

updateTriggerMap()
print("SELL TRIGGERS")
printTriggerValues("SELL")
print()
print()

# print("BUY TRIGGERS")
# printTriggerValues("BUY")
# print()
# print()

print("Add trigger for these: ")
for symbol, prices in symbol_prices.items():
    pOrL = "LOSS"
    new_sell_price_trigger = 0.0
    if symbol not in symbol_triggers:
        last_price = symbol_prices[symbol]['last_price']
        average_price = symbol_prices[symbol]['average_price']

        if last_price - average_price > 0:
            
            percentage_change = (last_price - average_price)/average_price * 100

            if percentage_change > 10.00:
                percentage_change = 10.00

            trigger_percentage = percentage_change/200

            new_sell_price_trigger = last_price - (last_price * trigger_percentage)
            new_sell_price_trigger = round(new_sell_price_trigger, 1)
            pOrL = "PROFIT"
            
        if new_sell_price_trigger > average_price:
            new_trigger_values = "[" + str(new_sell_price_trigger) + ", " + str(new_sell_price_trigger + new_sell_price_trigger) + "]"
            print("{:<20} {:20} {:>20}".format(symbol, pOrL, new_trigger_values))
            # print(f"Symbol: {symbol},\t Status: {pOrL} \t new trigger values: [{new_sell_price_trigger}, {new_sell_price_trigger+new_sell_price_trigger}]")
        else:
            new_sell_price_trigger = 0.0
