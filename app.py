from flask import Flask, render_template, request
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import os

app = Flask(__name__)

def abbreviate_number(num):
    """
    Abbreviate a number using 'k', 'M', 'B', etc.
    """
    if num < 1000:
        return str(num)
    for unit in ['k', 'M', 'B', 'T']:
        num /= 1000
        if num < 1000:
            return f"{num:.1f}{unit}"

def fetch_data_and_plot(payment_methods):
    # URL and base parameters from your notebook
    url = 'https://2txjwiew8a.execute-api.us-east-1.amazonaws.com/pre/latest/order-book'
    params_base = {
        'fiat': 'USD',
        'asset': 'USDT',
        'trans_amount': 500,
        'payment_methods': payment_methods
    }

    # Sending the GET request
    response = requests.get(url, params=params_base)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Create DataFrames for 'asks' and 'bids'
        df_asks = pd.DataFrame(data['aks'])
        df_bids = pd.DataFrame(data['bids'])

        # Add payment method column
        df_asks['payment_method'] = payment_methods
        df_bids['payment_method'] = payment_methods

    if df_asks is not None and df_bids is not None:
        # Your plotting code, adjusted for a single payment method
        sns.set_theme()
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot asks and bids
        ax.barh(df_asks['price'], df_asks['available'], color='green', label='Asks')
        ax.barh(df_bids['price'], df_bids['available'], color='red', label='Bids', alpha=0.7)

        # Other plot settings (titles, labels, etc.)
        # ...

        # Save the plot to a file
        image_path = f'static/{payment_methods}_plot.png'
        fig.savefig(image_path)

        plt.close(fig)  # Close the plot to free memory

        return df_asks, df_bids, image_path

    else:
        return None, None, None
@app.route('/')
def index():
    return render_template('index.html')  # The form for user input

@app.route('/data', methods=['POST'])
def data():
    fiat = request.form['fiat']
    asset = request.form['asset']
    trans_amount = request.form['trans_amount']
    payment_methods = request.form.getlist('payment_methods')  # For multiple selections
    df_asks, df_bids, image_path = fetch_data_and_plot(payment_methods)

    if df_asks is not None and df_bids is not None:
        asks_html = df_asks.to_html(classes='data')
        bids_html = df_bids.to_html(classes='data')

        return render_template('data.html', 
                               asks_table=asks_html, 
                               bids_table=bids_html, 
                               payment_method=payment_methods, 
                               image_path=image_path)
    else:
        return render_template('error.html', message="Data fetching failed.")

if __name__ == '__main__':
    app.run(debug=True)
