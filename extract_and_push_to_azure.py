import requests
import pandas as pd
import dateutil.parser as dt
import os

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

conn_str = os.environ['strong_conn_str']
url = os.environ['rapid_api_url']
api_key = os.environ['rapid_api_key']
api_host = os.environ['rapid_api_host']
container_name = os.environ['strg_container']


def get_time_series_stocks_data(symbol, period, url, api_key, api_host):

    querystring = {"symbol": symbol, "period": period, "language": "en"}

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_host
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json().get('data', []).get('time_series', [])

        if data:
            cols = ['symbol', 'date', 'price', 'change']
            df = pd.DataFrame(columns=cols)

            for entry in data:
                df = df._append({
                    'symbol': symbol,
                    'date': dt.parse(entry),
                    'price': data[entry]['price'],
                    'change': data[entry]['change']
                }, ignore_index=True)

            path = './data/'
            df.to_csv(os.path.join(
                path, f'{symbol}-{period}.csv'), mode='w+', index=False)

            print(f"Data fetched successfully and written")
        else:
            print("No data available from the API.")

    else:
        print("Failed to fetch data:", response.status_code)


symbols = ['AAPL', 'MSFT', 'TSLA', 'AMZN',
           'GOOGL', 'META', 'GS', 'DJIA', 'SPX', 'COMP']

for symbol in symbols:
    get_time_series_stocks_data(symbol, "1M", url, api_key, api_host)

blob_service_client = BlobServiceClient.from_connection_string(conn_str)

for filename in os.listdir("./data"):
    blob_obj = blob_service_client.get_blob_client(
        container=container_name, blob=filename)
    with open(os.path.join("./data", filename), mode='rb') as file:
        blob_obj.upload_blob(file)
