import streamlit as st
from order_book_fetcher import OrderBookFetcher
from order_book_plotter import OrderBookPlotter

# Initialize the OrderBookFetcher
fetcher = OrderBookFetcher()

# Fetch all available payment methods
payment_methods_json = fetcher.fetch_all_payment_methods()

# Extract labels for display in the dropdown and create a mapping to values
payment_method_labels = [method['label'] for method in payment_methods_json]
payment_method_value_map = {method['label']: method['value'] for method in payment_methods_json}

# Write a title for the app
st.title('Order Book Simulator')

fiat_options = {
    "BOB": "BOB",
    "USD": "USD",
    "EUR": "EUR",
    "GBP": "GBP"
}
# Ensure the order of keys matches the display order in the select box
fiat_keys = list(fiat_options.keys())

# Find the index of "🇺🇸 USD" to set it as the default option
default_fiat_index = fiat_keys.index("USD")
selected_fiat_label = st.selectbox('Choose the Fiat currency:', fiat_keys, index=default_fiat_index)

# Retrieve the corresponding value from fiat_options
selected_fiat = fiat_options[selected_fiat_label]

# Determine default payment methods based on selected fiat currency
default_payment_methods = []
if selected_fiat == "USD":
    # Set default payment methods for USD
    default_payment_methods = ["Zinli", "Wally Tech", "Dukascopy Bank"]
elif selected_fiat == "BOB":
    default_payment_methods = ["Banco Ganadero", "Banco Economico","Banco de Credito","Banco Union","Banco Nacional de Bolivia","Banco Mercantil Santa Cruz","SoliPagos", "Tigo Money", "Bank Transfer"]


# Create a multi-select list box for payment methods with labels, and capture the selected labels
selected_labels = st.multiselect('Choose one or more payment methods:', options=payment_method_labels, default=default_payment_methods)

# Map selected labels back to their corresponding values
selected_values = [payment_method_value_map[label] for label in selected_labels if label in payment_method_value_map]

# Asset selection
asset_options = ["USDT", "BTC", "ETH"]
selected_asset = st.selectbox('Choose an asset:', asset_options)

# Predefined transaction amounts
trans_amount_options = ["100 $", "200 $", "500 $", "1000 $"]
selected_trans_amount = None  # Variable to store the selected transaction amount

# Create columns for each predefined amount (simulate tile selector)
cols = st.columns(len(trans_amount_options))
for i, amount in enumerate(trans_amount_options):
    # Use index to access specific column and place a button
    if cols[i].button(amount):
        selected_trans_amount = int(amount.split(" $")[0])

# Allow for custom transaction amount
if st.button("Other..."):
    selected_trans_amount = "Other"

# Handle custom transaction amount input
if selected_trans_amount == "Other":
    custom_amount = st.text_input("Enter your amount ($):", value="0")
    try:
        trans_amount = int(custom_amount)
        st.write(f"You entered a custom amount: {trans_amount} $")
    except ValueError:
        st.error("Please enter a valid number for the amount.")
elif selected_trans_amount is not None:
    st.write(f"You selected transaction amount: {selected_trans_amount} $")


# Checkbox for "Verified" selection
is_verified = st.checkbox("Verified")

# Set merchant_type based on checkbox status
if is_verified:
    publisher_type = "merchant"
else:
    publisher_type = None


# Button to fetch data
if st.button('Show Results'):
    # Assuming you have logic to determine selected_payment_methods and trans_amount

    # Initialize the OrderBookFetcher with selected parameters
    fetcher = OrderBookFetcher(
        fiat=selected_fiat,
        asset=selected_asset,
        payment_methods=selected_values,
        trans_amount=selected_trans_amount,
        publisher_type=publisher_type
    )

    # Fetch the data
    fetcher.fetch_order_books()
    # Initialize the plotter
    plotter = OrderBookPlotter(fetcher)

    # Assuming you have already fetched or generated all_asks, all_bids, and payment_methods
    # Generate the plot
    fig = plotter.plot_order_book(fetcher.all_asks, fetcher.all_bids, fetcher.payment_methods)

    # Display the plot in Streamlit
    st.pyplot(fig)