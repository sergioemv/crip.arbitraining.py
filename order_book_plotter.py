import matplotlib.pyplot as plt
import seaborn as sns

class OrderBookPlotter:
    def __init__(self, order_book_fetcher):
        """
        Initializes the plotter with an instance of OrderBookFetcher.
        
        :param order_book_fetcher: An instance of OrderBookFetcher containing the data to plot.
        """
        self.order_book_fetcher = order_book_fetcher
        sns.set_theme()

    def abbreviate_number(self, num):
        """
        Abbreviate a number using 'k', 'M', 'B', etc.
        """
        if num < 1000:
            return str(num)
        for unit in ['k', 'M', 'B', 'T']:
            num /= 1000
            if num < 1000:
                return f"{num:.1f}{unit}"
    
    def plot_order_book(self, all_asks, all_bids, payment_methods):
        all_asks = self.order_book_fetcher.all_asks
        all_bids = self.order_book_fetcher.all_bids
        payment_methods = self.order_book_fetcher.payment_methods
        num_methods = len(payment_methods)
        max_prices = max(
            all_asks.groupby('payment_method')['price'].nunique().max(), 
            all_bids.groupby('payment_method')['price'].nunique().max()
        )

        height_per_subplot = max(6, 0.3 * max_prices) * 1.4  # 40% increase
        fig, axes = plt.subplots(1, num_methods, figsize=(5 * num_methods, height_per_subplot))

        if num_methods == 1:
            axes = [axes]

        for ax, method in zip(axes, payment_methods):
            asks_for_method = all_asks[all_asks['payment_method'] == method].sort_values(by='price', ascending=False)
            bids_for_method = all_bids[all_bids['payment_method'] == method].sort_values(by='price', ascending=False)

            asks_bars = ax.barh(asks_for_method['price'], asks_for_method['available'], color='green', label='Asks')
            bids_bars = ax.barh(bids_for_method['price'], bids_for_method['available'], color='red', label='Bids', alpha=0.7)

            for bar in asks_bars + bids_bars:
                width = bar.get_width()
                label = self.abbreviate_number(width)
                ax.text(width, bar.get_y() + bar.get_height() / 2, f' {label}', va='center')

            ax.set_xscale('log')
            ax.set_title(f'{method}')

        fig.legend(['Asks', 'Bids'], loc='upper right')
        plt.tight_layout()
        return fig
