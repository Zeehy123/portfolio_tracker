from django.db import models
from django.contrib.auth import get_user_model
import yfinance as yf

User = get_user_model()
class Stock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link stocks directly to a user
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    ticker = models.CharField(max_length=10, unique=True)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.ticker} - {self.name}"

    def get_current_price(self):
        try:
            stock_data = yf.Ticker(self.ticker)
            stock_info = stock_data.history(period="1d")
            if stock_info.empty:
                return None  # Return None if no data is found
            return stock_info['Close'].iloc[0]  # Get the latest closing price
        except Exception as e:
            print(f"Error fetching data for {self.ticker}: {e}")
            return None  # Return None in case of error

    @property
    def value(self):
        return self.quantity * self.buy_price

    @property
    def performance_percentage(self):
        current_price = self.get_current_price()
        if current_price is None or self.buy_price == 0:
            return None  # Avoid division by zero or invalid current price
        return ((current_price - float(self.buy_price)) / float(self.buy_price)) * 100
    def price_change(self):
        current_price = self.get_current_price()
        if current_price is None:
            return None  # Return None if there's no current price
        return current_price - float(self.buy_price)


    def get_previous_close_price(self):
        try:
            stock_data = yf.Ticker(self.ticker)
            stock_info = stock_data.history(period="2d")
            if len(stock_info) < 2:
                return None  # Not enough data for previous close
            return stock_info['Close'].iloc[-2]  # Get the previous day's closing price
        except Exception as e:
            print(f"Error fetching data for {self.ticker}: {e}")
            return None

    def daily_gain_loss(self):
        current_price = self.get_current_price()
        previous_close_price = self.get_previous_close_price()
    
        if current_price is None or previous_close_price is None:
            return None  # Return None if prices cannot be determined

        return current_price - previous_close_price  # Calculate daily change
