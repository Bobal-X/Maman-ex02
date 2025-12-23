import unittest
import Solution as Solution
from Business.Order import Order
from Utility.ReturnValue import ReturnValue
from Tests.AbstractTest import AbstractTest
from Business.Customer import Customer
from Business.Dish import Dish
from datetime import datetime


class TestGetPotentialDishRecommendations(AbstractTest):
    
    def setUp(self) -> None:
        super().setUp()
        # Create some customers and dishes for testing
        Solution.add_customer(Customer(1, 'Alice', 25, "0123456789"))
        Solution.add_customer(Customer(2, 'Bob', 30, "1234567890"))
        Solution.add_customer(Customer(3, 'Charlie', 28, "2345678901"))
        Solution.add_customer(Customer(4, 'David', 35, "3456789012"))
        Solution.add_customer(Customer(5, 'Eve', 22, "4567890123"))
        
        Solution.add_dish(Dish(1, "Pizza", 50.0, True))
        Solution.add_dish(Dish(2, "Burger", 30.0, True))
        Solution.add_dish(Dish(3, "Salad", 20.0, True))
        Solution.add_dish(Dish(4, "Pasta", 40.0, True))
        Solution.add_dish(Dish(5, "Sushi", 60.0, True))
        Solution.add_dish(Dish(6, "Soup", 15.0, True))
        Solution.add_dish(Dish(7, "Steak", 80.0, True))
        Solution.add_dish(Dish(8, "Fish", 45.0, True))
    
    def test_empty_result_no_ratings(self):
        """Test: Customer with no ratings should return empty list"""
        result = Solution.get_potential_dish_recommendations(1)
        self.assertEqual([], result, "Customer with no ratings should return empty list")
    
    def test_nonexistent_customer(self):
        """Test: Non-existent customer should return empty list"""
        result = Solution.get_potential_dish_recommendations(999)
        self.assertEqual([], result, "Non-existent customer should return empty list")
    
    def test_empty_result_no_similar_customers(self):
        """Test: Customer with ratings but no similar customers should return empty list"""
        # Customer 1 orders and rates dish 1
        Solution.add_order(Order(1, datetime.now(), 10, "Address1"))
        Solution.customer_placed_order(1, 1)
        Solution.order_contains_dish(1, 1, 1)
        Solution.customer_rated_dish(1, 1, 4)
        
        # Customer 2 rates dish 1 with 3 (below threshold, not similar)
        Solution.customer_rated_dish(2, 1, 3)
        
        result = Solution.get_potential_dish_recommendations(1)
        self.assertEqual([], result, "No similar customers should return empty list")
    
    def test_basic_direct_similarity(self):
        """Test: Basic case with direct similarity - one similar customer"""
        # Customer 1 orders and rates dish 1
        Solution.add_order(Order(1, datetime.now(), 10, "Address1"))
        Solution.customer_placed_order(1, 1)
        Solution.order_contains_dish(1, 1, 1)
        Solution.customer_rated_dish(1, 1, 5)  # Alice rates Pizza 5
        
        # Customer 2 rates dish 1 highly (similar to customer 1)
        Solution.customer_rated_dish(2, 1, 4)  # Bob rates Pizza 4
        
        # Customer 2 also rates other dishes
        Solution.customer_rated_dish(2, 2, 5)  # Bob rates Burger 5
        Solution.customer_rated_dish(2, 3, 4)  # Bob rates Salad 4
        
        result = Solution.get_potential_dish_recommendations(1)
        # Alice should get recommendations: Burger (2) and Salad (3) from Bob
        # Should NOT include dish 1 (already ordered)
        self.assertIn(2, result, "Should recommend Burger")
        self.assertIn(3, result, "Should recommend Salad")
        self.assertNotIn(1, result, "Should not recommend Pizza (already ordered)")
    
    def test_exclude_already_ordered_dishes(self):
        """Test: Should exclude dishes the customer already ordered"""
        # Customer 1 orders dishes 1 and 2
        Solution.add_order(Order(1, datetime.now(), 10, "Address1"))
        Solution.customer_placed_order(1, 1)
        Solution.order_contains_dish(1, 1, 1)
        Solution.order_contains_dish(1, 2, 1)
        Solution.customer_rated_dish(1, 1, 5)
        Solution.customer_rated_dish(1, 2, 3)
        
        # Customer 2 is similar (both rate dish 1 >= 4)
        Solution.customer_rated_dish(2, 1, 4)
        Solution.customer_rated_dish(2, 2, 5)
        Solution.customer_rated_dish(2, 3, 5)
        
        result = Solution.get_potential_dish_recommendations(1)
        # Should recommend dish 3, but NOT dish 1 or 2 (already ordered)
        self.assertIn(3, result, "Should recommend Salad")
        self.assertNotIn(1, result, "Should not recommend Pizza (already ordered)")
        self.assertNotIn(2, result, "Should not recommend Burger (already ordered)")
    
    def test_recursive_similarity(self):
        """Test: Recursive similarity - A similar to B, B similar to C, so C's dishes recommended to A"""
        # Customer 1 orders and rates dish 1
        Solution.add_order(Order(1, datetime.now(), 10, "Address1"))
        Solution.customer_placed_order(1, 1)
        Solution.order_contains_dish(1, 1, 1)
        Solution.customer_rated_dish(1, 1, 5)
        
        # Customer 2 rates dish 1 (direct similarity with customer 1)
        Solution.customer_rated_dish(2, 1, 4)
        
        # Customer 2 orders and rates dish 2
        Solution.add_order(Order(2, datetime.now(), 10, "Address2"))
        Solution.customer_placed_order(2, 2)
        Solution.order_contains_dish(2, 2, 1)
        Solution.customer_rated_dish(2, 2, 5)
        
        # Customer 3 rates dish 2 (direct similarity with customer 2)
        Solution.customer_rated_dish(3, 2, 4)
        
        # Customer 3 rates dish 3
        Solution.customer_rated_dish(3, 3, 5)
        
        result = Solution.get_potential_dish_recommendations(1)
        # Customer 1 should get recommendations from both customer 2 and 3
        # From customer 2: dish 2 (but customer 1 didn't order it, so it should be included)
        # From customer 3: dish 3
        self.assertIn(2, result, "Should recommend dish 2 from customer 2")
        self.assertIn(3, result, "Should recommend dish 3 from customer 3 (recursive)")
        self.assertNotIn(1, result, "Should not recommend dish 1 (already ordered)")
    
    def test_multiple_similar_customers_same_dish(self):
        """Test: Multiple similar customers recommend same dish - should appear once"""
        # Customer 1 orders and rates dish 1
        Solution.add_order(Order(1, datetime.now(), 10, "Address1"))
        Solution.customer_placed_order(1, 1)
        Solution.order_contains_dish(1, 1, 1)
        Solution.customer_rated_dish(1, 1, 5)
        
        # Both customer 2 and 3 rate dish 1 highly (both similar to customer 1)
        Solution.customer_rated_dish(2, 1, 4)
        Solution.customer_rated_dish(3, 1, 5)
        
        # Both customer 2 and 3 rate dish 2
        Solution.customer_rated_dish(2, 2, 5)
        Solution.customer_rated_dish(3, 2, 4)
        
        result = Solution.get_potential_dish_recommendations(1)
        # Dish 2 should appear only once in results
        self.assertEqual(1, result.count(2), "Dish 2 should appear only once")
        self.assertIn(2, result, "Should recommend dish 2")
        self.assertNotIn(1, result, "Should not recommend dish 1 (already ordered)")
    
    def test_rating_threshold(self):
        """Test: Only ratings >= 4 create similarity"""
        # Customer 1 orders and rates dish 1
        Solution.add_order(Order(1, datetime.now(), 10, "Address1"))
        Solution.customer_placed_order(1, 1)
        Solution.order_contains_dish(1, 1, 1)
        Solution.customer_rated_dish(1, 1, 5)
        
        # Customer 2 rates dish 1 with 3 (below threshold, not similar)
        Solution.customer_rated_dish(2, 1, 3)
        
        # Customer 2 rates dish 2
        Solution.customer_rated_dish(2, 2, 5)
        
        result = Solution.get_potential_dish_recommendations(1)
        # Customer 2 is NOT similar (rating 3 < 4), so dish 2 should not be recommended
        self.assertNotIn(2, result, "Should not recommend from non-similar customer")
    
    def test_customer_ordered_all_dishes(self):
        """Test: If customer ordered all dishes from similar customers, return empty list"""
        # Customer 1 orders dishes 1 and 2
        Solution.add_order(Order(1, datetime.now(), 10, "Address1"))
        Solution.customer_placed_order(1, 1)
        Solution.order_contains_dish(1, 1, 1)
        Solution.order_contains_dish(1, 2, 1)
        Solution.customer_rated_dish(1, 1, 5)
        Solution.customer_rated_dish(1, 2, 4)
        
        # Customer 2 is similar (both rate dish 1 >= 4)
        Solution.customer_rated_dish(2, 1, 4)
        Solution.customer_rated_dish(2, 2, 5)  # Customer 2 rates dish 2
        
        result = Solution.get_potential_dish_recommendations(1)
        # Should return empty since customer 1 ordered all dishes customer 2 rated
        self.assertEqual([], result, "Should return empty if customer ordered all dishes")
    
    def test_complex_scenario(self):
        """Test: Complex scenario with multiple customers and dishes"""
        # Customer 1 orders dishes 1, 2, 3
        Solution.add_order(Order(1, datetime.now(), 10, "Address1"))
        Solution.customer_placed_order(1, 1)
        Solution.order_contains_dish(1, 1, 1)
        Solution.order_contains_dish(1, 2, 1)
        Solution.order_contains_dish(1, 3, 1)
        Solution.customer_rated_dish(1, 1, 5)
        Solution.customer_rated_dish(1, 2, 4)
        Solution.customer_rated_dish(1, 3, 5)
        
        # Customer 2 is similar to customer 1 (both rate dish 1 >= 4)
        Solution.customer_rated_dish(2, 1, 4)
        Solution.customer_rated_dish(2, 4, 5)  # Customer 2 rates dish 4
        Solution.customer_rated_dish(2, 5, 4)  # Customer 2 rates dish 5
        
        # Customer 3 is similar to customer 2 (both rate dish 4 >= 4)
        Solution.customer_rated_dish(3, 4, 5)
        Solution.customer_rated_dish(3, 6, 5)  # Customer 3 rates dish 6
        
        # Customer 4 is similar to customer 1 (both rate dish 2 >= 4)
        Solution.customer_rated_dish(4, 2, 5)
        Solution.customer_rated_dish(4, 7, 4)  # Customer 4 rates dish 7
        
        result = Solution.get_potential_dish_recommendations(1)
        # Should get recommendations: 4, 5 (from customer 2), 6 (from customer 3), 7 (from customer 4)
        # Should NOT include: 1, 2, 3 (already ordered by customer 1)
        # Result should be sorted by dish_id ascending
        expected_dishes = [4, 5, 6, 7]
        self.assertEqual(expected_dishes, result, "Should get correct recommendations in sorted order")
        self.assertNotIn(1, result, "Should not recommend dish 1 (already ordered)")
        self.assertNotIn(2, result, "Should not recommend dish 2 (already ordered)")
        self.assertNotIn(3, result, "Should not recommend dish 3 (already ordered)")
    
    def test_self_exclusion(self):
        """Test: Should not include the customer itself in similar customers"""
        # Customer 1 orders dishes 1 and 2
        Solution.add_order(Order(1, datetime.now(), 10, "Address1"))
        Solution.customer_placed_order(1, 1)
        Solution.order_contains_dish(1, 1, 1)
        Solution.order_contains_dish(1, 2, 1)
        Solution.customer_rated_dish(1, 1, 5)
        Solution.customer_rated_dish(1, 2, 4)
        
        # Customer 2 is similar to customer 1
        Solution.customer_rated_dish(2, 1, 4)
        Solution.customer_rated_dish(2, 3, 5)
        
        result = Solution.get_potential_dish_recommendations(1)
        # Should only get dish 3 from customer 2, not dish 1 or 2 (already ordered)
        self.assertIn(3, result, "Should recommend dish 3")
        self.assertNotIn(1, result, "Should not recommend dish 1 (already ordered)")
        self.assertNotIn(2, result, "Should not recommend dish 2 (already ordered)")
    
    def test_no_duplicates_in_result(self):
        """Test: Result should not contain duplicate dish_ids"""
        # Customer 1 orders dish 1
        Solution.add_order(Order(1, datetime.now(), 10, "Address1"))
        Solution.customer_placed_order(1, 1)
        Solution.order_contains_dish(1, 1, 1)
        Solution.customer_rated_dish(1, 1, 5)
        
        # Multiple customers similar to customer 1, all rate dish 2
        Solution.customer_rated_dish(2, 1, 4)
        Solution.customer_rated_dish(2, 2, 5)
        
        Solution.customer_rated_dish(3, 1, 5)
        Solution.customer_rated_dish(3, 2, 4)
        
        Solution.customer_rated_dish(4, 1, 4)
        Solution.customer_rated_dish(4, 2, 5)
        
        result = Solution.get_potential_dish_recommendations(1)
        # Dish 2 should appear only once despite being recommended by multiple customers
        self.assertEqual(1, result.count(2), "Dish 2 should appear only once")
        self.assertEqual(len(result), len(set(result)), "Result should not contain duplicates")
        self.assertNotIn(1, result, "Should not recommend dish 1 (already ordered)")
    
    def test_rating_exactly_4(self):
        """Test: Rating of exactly 4 should create similarity"""
        # Customer 1 orders dish 1
        Solution.add_order(Order(1, datetime.now(), 10, "Address1"))
        Solution.customer_placed_order(1, 1)
        Solution.order_contains_dish(1, 1, 1)
        Solution.customer_rated_dish(1, 1, 5)
        
        # Customer 2 rates dish 1 with exactly 4 (should create similarity)
        Solution.customer_rated_dish(2, 1, 4)
        Solution.customer_rated_dish(2, 2, 5)
        
        result = Solution.get_potential_dish_recommendations(1)
        self.assertIn(2, result, "Rating of 4 should create similarity")
        self.assertNotIn(1, result, "Should not recommend dish 1 (already ordered)")
    
    def test_rating_3_no_similarity(self):
        """Test: Rating of 3 should NOT create similarity"""
        # Customer 1 orders dish 1
        Solution.add_order(Order(1, datetime.now(), 10, "Address1"))
        Solution.customer_placed_order(1, 1)
        Solution.order_contains_dish(1, 1, 1)
        Solution.customer_rated_dish(1, 1, 5)
        
        # Customer 2 rates dish 1 with 3 (should NOT create similarity)
        Solution.customer_rated_dish(2, 1, 3)
        Solution.customer_rated_dish(2, 2, 5)
        
        result = Solution.get_potential_dish_recommendations(1)
        self.assertNotIn(2, result, "Rating of 3 should NOT create similarity")

    def test_result_sorted_by_dish_id(self):
        """Test: Result should be sorted by dish_id ascending"""
        # Customer 1 orders dish 1
        Solution.add_order(Order(1, datetime.now(), 10, "Address1"))
        Solution.customer_placed_order(1, 1)
        Solution.order_contains_dish(1, 1, 1)
        Solution.customer_rated_dish(1, 1, 5)
        
        # Customer 2 is similar and rates dishes 7, 2, 5, 4 (out of order)
        Solution.customer_rated_dish(2, 1, 4)
        Solution.customer_rated_dish(2, 7, 5)
        Solution.customer_rated_dish(2, 2, 4)
        Solution.customer_rated_dish(2, 5, 5)
        Solution.customer_rated_dish(2, 4, 4)
        
        result = Solution.get_potential_dish_recommendations(1)
        # Result should be sorted: [2, 4, 5, 7]
        self.assertEqual([2, 4, 5, 7], result, "Result should be sorted by dish_id ascending")
        self.assertEqual(result, sorted(result), "Result should be in ascending order")
    
    def test_scenario_from_HW(self):
        """Test: Scenario from homework example"""
        Solution.add_order(Order(1, datetime.now(), 3, "Haifa"))
        Solution.customer_placed_order(1, 1)
        Solution.order_contains_dish(1, 1, 1)
        Solution.order_contains_dish(1, 2, 1)
        Solution.order_contains_dish(1, 3, 1)

        Solution.customer_rated_dish(1, 1, 5)
        Solution.customer_rated_dish(1, 2, 4)
        Solution.customer_rated_dish(1, 3, 5)

        Solution.customer_rated_dish(2, 1, 4)
        Solution.customer_rated_dish(2, 4, 5)

        Solution.customer_rated_dish(3, 4, 5)
        Solution.customer_rated_dish(3, 5, 4)
        Solution.customer_rated_dish(3, 7, 5)

        Solution.customer_rated_dish(4, 6, 4)

        result = Solution.get_potential_dish_recommendations(1)
        self.assertEqual([4, 5, 7], result, "Customer 1 should be recommended dishes 4,5,7")


    def test_scenario_from_HW_original(self):
        Solution.add_order(Order(1,datetime.now(),3,"Haifa"))
        Solution.customer_placed_order(1,1)
        Solution.order_contains_dish(1,1,1)
        Solution.order_contains_dish(1,2,1)
        Solution.order_contains_dish(1,3,1)

        Solution.customer_rated_dish(1, 1, 5)
        Solution.customer_rated_dish(1, 2, 4)
        Solution.customer_rated_dish(1, 3, 5)

        Solution.customer_rated_dish(2, 1, 4)
        Solution.customer_rated_dish(2, 4, 5)

        Solution.customer_rated_dish(3, 4, 5)
        Solution.customer_rated_dish(3, 5, 4)
        Solution.customer_rated_dish(3, 7, 5)

        Solution.customer_rated_dish(4, 6, 4)

        result = Solution.get_potential_dish_recommendations(1)
        self.assertEqual([4,5,7], result, "Customer 1 should be recommended dishes 4,5,7")
# *** DO NOT RUN EACH TEST MANUALLY ***
if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)

