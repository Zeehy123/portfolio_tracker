from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import F
from .models import Stock
from .serializers import StockSerializer,StockPerformanceSerializer

from django.shortcuts import get_object_or_404


class StockListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stocks = Stock.objects.filter(user=request.user)
        stock_data = [
            {
                "id": stock.id,
                "name": stock.name,
                "ticker": stock.ticker,
                "quantity": stock.quantity,
                "buy_price": float(stock.buy_price),
                "current_price": stock.get_current_price(),
                "value": stock.value,
            }
            for stock in stocks
        ]
        return Response(stock_data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = StockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            stock = Stock.objects.get(pk=pk, user=request.user)
            stock.delete()
            return Response({"message": "Stock deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Stock.DoesNotExist:
            return Response({"error": "Stock not found."}, status=status.HTTP_404_NOT_FOUND)


class StockDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        stock = get_object_or_404(Stock, id=id, user=request.user)
        serializer = StockSerializer(stock)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        stock = get_object_or_404(Stock, id=id, user=request.user)
        serializer = StockSerializer(stock, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        stock = get_object_or_404(Stock, id=id, user=request.user)
        stock.delete()
        return Response({"message": "Stock deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class PortfolioValueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all stocks for the authenticated user
        stocks = Stock.objects.filter(user=request.user)
        
        # Calculate the total portfolio value by summing up each stock's value
        total_value = sum(stock.value for stock in stocks)
        
        return Response({
            "total_value": total_value
        }, status=status.HTTP_200_OK)
    

class TopPortfolioValueView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from collections import defaultdict

       
        stocks = Stock.objects.filter(user=request.user)

        user_portfolio_values = defaultdict(float)

        
        for stock in stocks:
            current_price = stock.get_current_price()  
            if current_price:  
                stock_value = current_price * stock.quantity
            else:
                stock_value = 0 
            user_portfolio_values[stock.user] += stock_value

        
        top_user, top_value = max(user_portfolio_values.items(), key=lambda x: x[1], default=(None, 0))

        if top_user:
            return Response({
                
                "top_value": top_value
            }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No portfolios found."}, status=status.HTTP_404_NOT_FOUND)
class PortfolioPerformanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all stocks for the authenticated user
        stocks = Stock.objects.filter(user=request.user)
        
        total_buy_value = 0.0  
        total_current_value = 0.0  

        for stock in stocks:
            current_price = stock.get_current_price()
            if current_price:
                total_buy_value += float(stock.buy_price) * stock.quantity 
                total_current_value += float(current_price) * stock.quantity  

        if total_buy_value == 0:
            return Response({"message": "No valid portfolio data available."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate performance percentage
        performance_percentage = ((total_current_value - total_buy_value) / total_buy_value) * 100

     
        performance_status = "Profit" if performance_percentage > 0 else "Loss"
        return Response({
           
            "performance_percentage": round(performance_percentage, 2),
            "status": performance_status
        }, status=status.HTTP_200_OK)


class TopPerformingStocksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
           
            stocks = Stock.objects.filter(user=request.user)

            if not stocks.exists():
                return Response({"message": "No valid stocks found."}, status=status.HTTP_404_NOT_FOUND)

            
            top_stock = max(
                stocks,
                key=lambda stock: stock.performance_percentage if stock.performance_percentage is not None else -float('inf'),
                default=None
            )

            if not top_stock or top_stock.performance_percentage is None:
                return Response({"message": "No valid stocks found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = StockPerformanceSerializer(top_stock)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BarChartDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Filter stocks for the authenticated user
            stocks = Stock.objects.filter(user=request.user)

            if not stocks.exists():
                return Response({"message": "No valid stocks found."}, status=status.HTTP_404_NOT_FOUND)

            # Debugging
            print("Fetched stocks:", stocks)

            # Prepare data for the bar chart
            chart_data = {
                "labels": [stock.name for stock in stocks],
                "data": [{"total_value": stock.value} for stock in stocks],  # Ensure the data is structured properly
            }

            return Response(chart_data, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error:", e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class StockDataView(APIView):
    def get(self, request):
        try:
            # Retrieve all stocks from a particular user
            stocks = Stock.objects.filter(user=request.user)

            # Prepare the data for the response
            stock_data = [
                {
                    "name": stock.name,
                    "ticker": stock.ticker,
                    "priceChange": round(stock.price_change(), 2) if stock.price_change() is not None else 0.00,  # Rounded to 2 decimals
                    "percentageChange": round(stock.performance_percentage, 2) if stock.performance_percentage is not None else 0.00,  # Rounded to 2 decimals
                    "currentPrice": round(stock.get_current_price(), 2) if stock.get_current_price() is not None else 0.00,  # Rounded to 2 decimals
                }
                for stock in stocks
            ]

            return Response(stock_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DailyGainLossView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Retrieve all stocks for the authenticated user
            stocks = Stock.objects.filter(user=request.user)
            daily_gain_loss_data = []

            for stock in stocks:
                gain_loss = stock.daily_gain_loss()
                
               
                if gain_loss is None:
                    status_message = "Data Not Available"
                    daily_gain_loss_data.append({
                        "ticker": stock.ticker,
                        "name": stock.name,
                        "quantity": stock.quantity,
                        "daily_gain_loss": None,
                        "status": status_message,
                    })
                    continue

                # the gain/loss data
                daily_gain_loss_data.append({
                    "ticker": stock.ticker,
                    "name": stock.name,
                    "quantity": stock.quantity,
                    "daily_gain_loss": gain_loss,
                    "status": "Gain" if gain_loss > 0 else "Loss" if gain_loss < 0 else "No Change",
                })

            return Response(daily_gain_loss_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WorstPerformingStockView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Retrieve all stocks for the authenticated user
            stocks = Stock.objects.filter(user=request.user)
            worst_stock = min(
                stocks,
                key=lambda stock: stock.performance_percentage if stock.performance_percentage is not None else float('inf'),
                default=None
            )

            if worst_stock is None or worst_stock.performance_percentage is None:
                return Response({"message": "No valid stock data found."}, status=status.HTTP_404_NOT_FOUND)

            # Prepare the response data
            worst_stock_data = {
                "ticker": worst_stock.ticker,
                "name": worst_stock.name,
                
                "performance_percentage": round(worst_stock.performance_percentage, 2),
                "status": "Loss" if worst_stock.performance_percentage < 0 else "No Change",
            }

            return Response(worst_stock_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class BestPerformingStockView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch all stocks for the authenticated user
            stocks = Stock.objects.filter(user=request.user)

        
            best_stock = max(
                stocks,
                key=lambda stock: stock.performance_percentage if stock.performance_percentage is not None else float('-inf'),
                default=None
            )

            if best_stock is None or best_stock.performance_percentage is None:
                return Response({"message": "No valid stock data found."}, status=status.HTTP_404_NOT_FOUND)

           
            best_stock_data = {
                "ticker": best_stock.ticker,
                "name": best_stock.name,
                "performance_percentage": round(best_stock.performance_percentage, 2),
                "status": "Gain" if best_stock.performance_percentage > 0 else "No Change",
            }

            return Response(best_stock_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TopThreeStocksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            
            stocks = Stock.objects.filter(user=request.user)
            if not stocks.exists():
                return Response({"message": "No stocks found in the portfolio."}, status=status.HTTP_404_NOT_FOUND)

            
            total_portfolio_value = 0
            stock_data = []

            for stock in stocks:
                current_price = stock.get_current_price()
                if current_price is not None:
                    current_value = current_price * stock.quantity
                    total_portfolio_value += current_value
                    stock_data.append({
                        "ticker": stock.ticker,
                        "name": stock.name,
                        "quantity": stock.quantity,
                        "current_value": current_value
                    })

            if total_portfolio_value == 0:
                return Response({"message": "Total portfolio value is zero, no valid stock data found."}, status=status.HTTP_400_BAD_REQUEST)

            for stock in stock_data:
                stock["portfolio_percentage"] = (stock["current_value"] / total_portfolio_value) * 100

           
            top_three_stocks = sorted(stock_data, key=lambda x: x["current_value"], reverse=True)[:3]

          
            total_percentage_top_three = sum(stock["portfolio_percentage"] for stock in top_three_stocks)

            return Response({
               
                "top_three_stocks": [
                    {
                        
                        "name": stock["name"],
                  
                        "portfolio_percentage": round(stock["portfolio_percentage"], 2),
                    }
                    for stock in top_three_stocks
                ],
                "total_percentage_top_three": round(total_percentage_top_three, 2)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
