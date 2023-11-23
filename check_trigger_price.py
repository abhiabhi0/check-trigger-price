import requests

url = "https://kite.zerodha.com/oms/gtt/triggers"

# Adding the new authorization token in the headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Authorization": 
}

try:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Creating a map to store tradingsymbol as key, trigger_values and type as value if status is active
        symbol_triggers = {}

        for item in data.get("data", []):
            status = item.get("status")
            symbol = item.get("condition", {}).get("tradingsymbol")
            trigger_values = item.get("condition", {}).get("trigger_values")
            gtt_type = item.get("type")

            if status == "active" and symbol and trigger_values:
                symbol_triggers[symbol] = {
                    "trigger_values": trigger_values,
                    "type": gtt_type
                }

        # # Printing the map containing symbol, trigger_values and type for active triggers
        # for symbol, info in symbol_triggers.items():
        #     print(f"Symbol: {symbol}, Trigger Values: {info['trigger_values']}, Type: {info['type']}")

    else:
        print("Failed to fetch data from the API.")

except requests.RequestException as e:
    print(f"Error fetching data: {e}")



url = "https://kite.zerodha.com/oms/portfolio/holdings"

# Adding the new authorization token in the headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Authorization": 
}

try:
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Creating a map to store symbol as key and last_price and average_price as values
        symbol_prices = {}

        for item in data.get("data", []):
            symbol = item.get("tradingsymbol")
            last_price = item.get("last_price")
            average_price = item.get("average_price")

            symbol_prices[symbol] = {"last_price": last_price, "average_price": average_price}

        # Printing the map containing symbol, last_price, and average_price
        for symbol, prices in symbol_prices.items():
            if symbol in symbol_triggers:
                gtt = symbol_triggers[symbol]
                if gtt['type'] == "two-leg":
                    last_price = prices['last_price']
                    average_price = prices['average_price']

                    new_sell_price_trigger = last_price - (last_price * 0.05)

                    if new_sell_price_trigger > average_price and new_sell_price_trigger > gtt['trigger_values'][0]:
                        print(f"Symbol: {symbol},\tAverage Price: {average_price},\tLast Sell Price Trigger: {gtt['trigger_values'][0]},\tNew Sell Price Trigger: {new_sell_price_trigger}")


    else:
        print("Failed to fetch data from the API.")

except requests.RequestException as e:
    print(f"Error fetching data: {e}")
