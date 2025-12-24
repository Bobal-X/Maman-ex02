import unittest
import Solution as Solution
from Utility.ReturnValue import ReturnValue
from Tests.AbstractTest import AbstractTest
from Business.Customer import Customer
from Business.Dish import Dish
from Business.Order import Order
from datetime import datetime


class TestGetCumulativeProfitPerMonth(AbstractTest):
    
    def setUp(self) -> None:
        super().setUp()
        # Create some customers and dishes for testing
        Solution.add_customer(Customer(1, 'Alice', 25, "0123456789"))
        Solution.add_customer(Customer(2, 'Bob', 30, "1234567890"))
        Solution.add_customer(Customer(3, 'Charlie', 28, "2345678901"))
        
        Solution.add_dish(Dish(1, "Pizza", 50.0, True))
        Solution.add_dish(Dish(2, "Burger", 30.0, True))
        Solution.add_dish(Dish(3, "Salad", 20.0, True))
        Solution.add_dish(Dish(4, "Pasta", 40.0, True))
        Solution.add_dish(Dish(5, "Sushi", 60.0, True))
    
    def test_empty_year_no_orders(self):
        """Test: Year with no orders should return all 12 months with 0.0 profit"""
        result = Solution.get_cumulative_profit_per_month(2023)
        expected = [(12, 0.0), (11, 0.0), (10, 0.0), (9, 0.0), (8, 0.0), (7, 0.0), 
                    (6, 0.0), (5, 0.0), (4, 0.0), (3, 0.0), (2, 0.0), (1, 0.0)]
        self.assertEqual(expected, result, "Year with no orders should return all 12 months with 0.0 profit")
    
    def test_single_month_single_order(self):
        """Test: Single order in one month"""
        # Order in January 2023
        Solution.add_order(Order(1, datetime(2023, 1, 15, 12, 0, 0), 10.0, "Address1"))
        Solution.order_contains_dish(1, 1, 2)  # 2 pizzas at 50.0 each = 100.0
        # Total: 100.0 + 10.0 delivery = 110.0
        
        result = Solution.get_cumulative_profit_per_month(2023)
        # Should return all 12 months, all showing cumulative profit of 110.0 (from January)
        expected = [(12, 110.0), (11, 110.0), (10, 110.0), (9, 110.0), (8, 110.0), (7, 110.0), 
                    (6, 110.0), (5, 110.0), (4, 110.0), (3, 110.0), (2, 110.0), (1, 110.0)]
        self.assertEqual(12, len(result), "Should return all 12 months")
        self.assertEqual(expected, result, "All months should have cumulative profit of 110.0 (from January)")
    
    def test_single_month_multiple_orders(self):
        """Test: Multiple orders in one month"""
        # Order 1 in January
        Solution.add_order(Order(1, datetime(2023, 1, 10, 12, 0, 0), 10.0, "Address1"))
        Solution.order_contains_dish(1, 1, 1)  # 1 pizza = 50.0
        # Order 1 total: 50.0 + 10.0 = 60.0
        
        # Order 2 in January
        Solution.add_order(Order(2, datetime(2023, 1, 20, 12, 0, 0), 15.0, "Address2"))
        Solution.order_contains_dish(2, 2, 2)  # 2 burgers = 60.0
        # Order 2 total: 60.0 + 15.0 = 75.0
        
        # Cumulative for January: 60.0 + 75.0 = 135.0
        result = Solution.get_cumulative_profit_per_month(2023)
        # All months should show cumulative profit of 135.0 (from January)
        expected = [(12, 135.0), (11, 135.0), (10, 135.0), (9, 135.0), (8, 135.0), (7, 135.0), 
                    (6, 135.0), (5, 135.0), (4, 135.0), (3, 135.0), (2, 135.0), (1, 135.0)]
        self.assertEqual(12, len(result), "Should return all 12 months")
        self.assertEqual(expected, result, "All months should have cumulative profit of 135.0 (from January)")
    
    def test_multiple_months_cumulative(self):
        """Test: Multiple months with cumulative calculation"""
        # January: Order 1
        Solution.add_order(Order(1, datetime(2023, 1, 15, 12, 0, 0), 10.0, "Address1"))
        Solution.order_contains_dish(1, 1, 1)  # 1 pizza = 50.0
        # January total: 50.0 + 10.0 = 60.0
        
        # February: Order 2
        Solution.add_order(Order(2, datetime(2023, 2, 10, 12, 0, 0), 15.0, "Address2"))
        Solution.order_contains_dish(2, 2, 2)  # 2 burgers = 60.0
        # February total: 60.0 + 15.0 = 75.0
        # February cumulative: 60.0 (Jan) + 75.0 (Feb) = 135.0
        
        # March: Order 3
        Solution.add_order(Order(3, datetime(2023, 3, 5, 12, 0, 0), 20.0, "Address3"))
        Solution.order_contains_dish(3, 3, 1)  # 1 salad = 20.0
        # March total: 20.0 + 20.0 = 40.0
        # March cumulative: 60.0 (Jan) + 75.0 (Feb) + 40.0 (Mar) = 175.0
        
        result = Solution.get_cumulative_profit_per_month(2023)
        # Should be sorted by month descending with all 12 months
        expected = [(12, 175.0), (11, 175.0), (10, 175.0), (9, 175.0), (8, 175.0), (7, 175.0), 
                    (6, 175.0), (5, 175.0), (4, 175.0), (3, 175.0), (2, 135.0), (1, 60.0)]
        self.assertEqual(12, len(result), "Should return all 12 months")
        self.assertEqual(expected, result, "Should have cumulative profits for Jan-Mar, others carry forward")
    
    def test_order_with_multiple_dishes(self):
        """Test: Order with multiple dishes"""
        Solution.add_order(Order(1, datetime(2023, 1, 15, 12, 0, 0), 10.0, "Address1"))
        Solution.order_contains_dish(1, 1, 2)  # 2 pizzas = 100.0
        Solution.order_contains_dish(1, 2, 1)  # 1 burger = 30.0
        Solution.order_contains_dish(1, 3, 3)  # 3 salads = 60.0
        # Total: 100.0 + 30.0 + 60.0 + 10.0 delivery = 200.0
        
        result = Solution.get_cumulative_profit_per_month(2023)
        expected = [(12, 200.0), (11, 200.0), (10, 200.0), (9, 200.0), (8, 200.0), (7, 200.0), 
                    (6, 200.0), (5, 200.0), (4, 200.0), (3, 200.0), (2, 200.0), (1, 200.0)]
        self.assertEqual(expected, result, "Should calculate total with multiple dishes, all months show cumulative")
    
    def test_order_with_only_delivery_fee(self):
        """Test: Order with no dishes (only delivery fee)"""
        Solution.add_order(Order(1, datetime(2023, 1, 15, 12, 0, 0), 25.0, "Address1"))
        # No dishes, only delivery fee = 25.0
        
        result = Solution.get_cumulative_profit_per_month(2023)
        expected = [(12, 25.0), (11, 25.0), (10, 25.0), (9, 25.0), (8, 25.0), (7, 25.0), 
                    (6, 25.0), (5, 25.0), (4, 25.0), (3, 25.0), (2, 25.0), (1, 25.0)]
        self.assertEqual(expected, result, "Order with only delivery fee should return delivery fee for all months")
    
    def test_sorting_descending(self):
        """Test: Results should be sorted by month in descending order"""
        # Create orders in different months
        Solution.add_order(Order(1, datetime(2023, 1, 15, 12, 0, 0), 10.0, "Address1"))
        Solution.order_contains_dish(1, 1, 1)  # 50.0 + 10.0 = 60.0
        
        Solution.add_order(Order(2, datetime(2023, 3, 10, 12, 0, 0), 15.0, "Address2"))
        Solution.order_contains_dish(2, 2, 1)  # 30.0 + 15.0 = 45.0
        
        Solution.add_order(Order(3, datetime(2023, 2, 5, 12, 0, 0), 20.0, "Address3"))
        Solution.order_contains_dish(3, 3, 1)  # 20.0 + 20.0 = 40.0
        
        # January: 60.0
        # February: 60.0 + 40.0 = 100.0
        # March: 100.0 + 45.0 = 145.0
        # Months 4-12: 145.0 (carry forward)
        
        result = Solution.get_cumulative_profit_per_month(2023)
        expected = [(12, 145.0), (11, 145.0), (10, 145.0), (9, 145.0), (8, 145.0), (7, 145.0), 
                    (6, 145.0), (5, 145.0), (4, 145.0), (3, 145.0), (2, 100.0), (1, 60.0)]
        self.assertEqual(12, len(result), "Should return all 12 months")
        self.assertEqual(expected, result, "Months should be in descending order with cumulative profits")
        # Verify descending order
        months = [r[0] for r in result]
        self.assertEqual(months, sorted(months, reverse=True), "Months should be in descending order")
    
    def test_different_years(self):
        """Test: Orders in different years should be separated"""
        # Order in 2023
        Solution.add_order(Order(1, datetime(2023, 1, 15, 12, 0, 0), 10.0, "Address1"))
        Solution.order_contains_dish(1, 1, 1)  # 50.0 + 10.0 = 60.0
        
        # Order in 2024
        Solution.add_order(Order(2, datetime(2024, 1, 15, 12, 0, 0), 15.0, "Address2"))
        Solution.order_contains_dish(2, 2, 1)  # 30.0 + 15.0 = 45.0
        
        result_2023 = Solution.get_cumulative_profit_per_month(2023)
        result_2024 = Solution.get_cumulative_profit_per_month(2024)
        
        expected_2023 = [(12, 60.0), (11, 60.0), (10, 60.0), (9, 60.0), (8, 60.0), (7, 60.0), 
                         (6, 60.0), (5, 60.0), (4, 60.0), (3, 60.0), (2, 60.0), (1, 60.0)]
        expected_2024 = [(12, 45.0), (11, 45.0), (10, 45.0), (9, 45.0), (8, 45.0), (7, 45.0), 
                         (6, 45.0), (5, 45.0), (4, 45.0), (3, 45.0), (2, 45.0), (1, 45.0)]
        self.assertEqual(expected_2023, result_2023, "2023 should have 60.0 for all months")
        self.assertEqual(expected_2024, result_2024, "2024 should have 45.0 for all months")
    
    def test_multiple_orders_same_month(self):
        """Test: Multiple orders in the same month should be summed"""
        # Three orders in January
        Solution.add_order(Order(1, datetime(2023, 1, 5, 12, 0, 0), 10.0, "Address1"))
        Solution.order_contains_dish(1, 1, 1)  # 50.0 + 10.0 = 60.0
        
        Solution.add_order(Order(2, datetime(2023, 1, 15, 12, 0, 0), 15.0, "Address2"))
        Solution.order_contains_dish(2, 2, 1)  # 30.0 + 15.0 = 45.0
        
        Solution.add_order(Order(3, datetime(2023, 1, 25, 12, 0, 0), 20.0, "Address3"))
        Solution.order_contains_dish(3, 3, 1)  # 20.0 + 20.0 = 40.0
        
        # January cumulative: 60.0 + 45.0 + 40.0 = 145.0
        result = Solution.get_cumulative_profit_per_month(2023)
        expected = [(12, 145.0), (11, 145.0), (10, 145.0), (9, 145.0), (8, 145.0), (7, 145.0), 
                    (6, 145.0), (5, 145.0), (4, 145.0), (3, 145.0), (2, 145.0), (1, 145.0)]
        self.assertEqual(expected, result, "January should sum all orders, all months show cumulative")
    
    def test_cumulative_across_months(self):
        """Test: Cumulative profit accumulates from beginning of year"""
        # January: 2 pizzas (100.0) + delivery (10.0) = 110.0
        Solution.add_order(Order(1, datetime(2023, 1, 15, 12, 0, 0), 10.0, "Address1"))
        Solution.order_contains_dish(1, 1, 2)  # 100.0 + 10.0 = 110.0
        
        # February: 1 burger (30.0) + delivery (10.0) = 40.0
        # February cumulative: 110.0 (Jan) + 40.0 (Feb) = 150.0
        Solution.add_order(Order(2, datetime(2023, 2, 10, 12, 0, 0), 10.0, "Address2"))
        Solution.order_contains_dish(2, 2, 1)  # 30.0 + 10.0 = 40.0
        
        # March: 1 burger (30.0) + delivery (10.0) = 40.0
        # March cumulative: 110.0 (Jan) + 40.0 (Feb) + 40.0 (Mar) = 190.0
        Solution.add_order(Order(3, datetime(2023, 3, 5, 12, 0, 0), 10.0, "Address3"))
        Solution.order_contains_dish(3, 2, 1)  # 30.0 + 10.0 = 40.0
        
        result = Solution.get_cumulative_profit_per_month(2023)
        expected = [(12, 190.0), (11, 190.0), (10, 190.0), (9, 190.0), (8, 190.0), (7, 190.0), 
                    (6, 190.0), (5, 190.0), (4, 190.0), (3, 190.0), (2, 150.0), (1, 110.0)]
        self.assertEqual(expected, result, "Cumulative profit should accumulate from beginning of year")
    
    def test_result_type_float(self):
        """Test: Results should be float type"""
        Solution.add_order(Order(1, datetime(2023, 1, 15, 12, 0, 0), 10.0, "Address1"))
        Solution.order_contains_dish(1, 1, 1)  # 50.0 + 10.0 = 60.0
        
        result = Solution.get_cumulative_profit_per_month(2023)
        self.assertEqual(12, len(result), "Should return all 12 months")
        for month, profit in result:
            self.assertIsInstance(profit, float, f"Profit for month {month} should be float type")
    
    def test_large_amounts(self):
        """Test: Orders with large amounts"""
        Solution.add_order(Order(1, datetime(2023, 1, 15, 12, 0, 0), 100.0, "Address1"))
        Solution.order_contains_dish(1, 1, 10)  # 10 pizzas = 500.0
        # Total: 500.0 + 100.0 = 600.0
        
        result = Solution.get_cumulative_profit_per_month(2023)
        expected = [(12, 600.0), (11, 600.0), (10, 600.0), (9, 600.0), (8, 600.0), (7, 600.0), 
                    (6, 600.0), (5, 600.0), (4, 600.0), (3, 600.0), (2, 600.0), (1, 600.0)]
        self.assertEqual(expected, result, "Should handle large amounts correctly, all months show cumulative")
    
    def test_all_months_year(self):
        """Test: Orders spread across all 12 months"""
        # Create orders for each month
        cumulative = 0.0
        for month in range(1, 13):
            order_id = month
            profit = month * 10.0  # Each month has different profit
            Solution.add_order(Order(order_id, datetime(2023, month, 15, 12, 0, 0), 10.0, f"Address{month}"))
            # Create dish order to get the desired profit
            # We'll use dish 1 (50.0) and adjust amount
            dish_amount = int((profit - 10.0) / 50.0)  # Calculate amount needed
            if dish_amount > 0:
                Solution.order_contains_dish(order_id, 1, dish_amount)
            # If profit is exactly 10.0, no dishes needed
            cumulative += profit
        
        result = Solution.get_cumulative_profit_per_month(2023)
        self.assertEqual(12, len(result), "Should return all 12 months")
        # Verify descending order
        months = [r[0] for r in result]
        self.assertEqual(list(range(12, 0, -1)), months, "Months should be 12 down to 1")
        # Verify cumulative values increase as months decrease (since descending order)
        # Month 12 should have cumulative of all months, month 1 should have only month 1
        profits = [r[1] for r in result]
        # Profits should be in descending order (month 12 has highest cumulative)
        self.assertGreater(profits[0], profits[-1], "Month 12 should have higher cumulative than month 1")
    
    def test_year_with_no_matching_orders(self):
        """Test: Year with orders but none in that specific year"""
        # Order in 2022
        Solution.add_order(Order(1, datetime(2022, 1, 15, 12, 0, 0), 10.0, "Address1"))
        Solution.order_contains_dish(1, 1, 1)
        
        # Query 2023
        result = Solution.get_cumulative_profit_per_month(2023)
        expected = [(12, 0.0), (11, 0.0), (10, 0.0), (9, 0.0), (8, 0.0), (7, 0.0), 
                    (6, 0.0), (5, 0.0), (4, 0.0), (3, 0.0), (2, 0.0), (1, 0.0)]
        self.assertEqual(expected, result, "Year with no matching orders should return all 12 months with 0.0 profit")
    
    def test_order_with_price_changes(self):
        """Test: Order uses current_price at time of order, not current dish price"""
        # Create order when dish price is 50.0
        Solution.add_order(Order(1, datetime(2023, 1, 15, 12, 0, 0), 10.0, "Address1"))
        Solution.order_contains_dish(1, 1, 2)  # 2 pizzas at 50.0 = 100.0
        # Total: 100.0 + 10.0 = 110.0
        
        # Change dish price (should not affect existing order)
        Solution.update_dish_price(1, 60.0)
        
        result = Solution.get_cumulative_profit_per_month(2023)
        expected = [(12, 110.0), (11, 110.0), (10, 110.0), (9, 110.0), (8, 110.0), (7, 110.0), 
                    (6, 110.0), (5, 110.0), (4, 110.0), (3, 110.0), (2, 110.0), (1, 110.0)]
        # Should still use the price at time of order (50.0)
        self.assertEqual(expected, result, "Should use price at time of order, all months show cumulative")


# *** DO NOT RUN EACH TEST MANUALLY ***
if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)

