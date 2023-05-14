from flask import Flask, render_template, request
import finnhub
from chart_studio.tools import set_credentials_file
import plotly.graph_objects as go

import plotly.express as px
import chart_studio.plotly as py
import pandas as pd
from dotenv import load_dotenv
import os
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "http://my-test-site.great-site.net"}})


load_dotenv()

# Set up the Finnhub client
finnhub_client = finnhub.Client(api_key=os.environ.get("FINNHUB_API_KEY"))

# Set up the Plotly client
plotly_username = os.environ.get("PLOTLY_USERNAME")
plot_api_key = os.environ.get("PLOTLY_API_KEY")
print("username, api_key:", plotly_username, plot_api_key)
set_credentials_file(username=plotly_username, api_key=plot_api_key)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stock', methods=['POST'])
def stock():
    ticker = request.form['ticker']
    prices = get_stock_prices(ticker)
    fig = create_plot(prices, ticker)
    fig_html = save_plot_to_cloud(fig, ticker)
    return render_template('stock.html', fig_html=fig_html, ticker=ticker.upper())

def get_stock_prices(ticker):
    now = int(pd.Timestamp.now().timestamp())
    last_month = int((pd.Timestamp.now() - pd.DateOffset(days=30)).timestamp())
    res = finnhub_client.stock_candles(ticker, 'D', last_month, now)
    prices = pd.DataFrame(res)
    prices['t'] = pd.to_datetime(prices['t'], unit='s')
    return prices

def create_plot(prices, ticker):
    fig = px.line(prices, x='t', y='c', title=f'{ticker.upper()} Stock Prices', labels={'t': 'Date', 'c': 'Closing Price'})
    return fig

def save_plot_to_cloud(fig, ticker):
    filename = f"{ticker}_stock_prices"
    py.plot(fig, f"{filename}.png", auto_open=True)
    return py.to_html(fig)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
