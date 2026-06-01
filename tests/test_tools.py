import unittest
import sys
import os

# Add src directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.stock_tool import check_stock
from src.tools.discount_tool import get_discount
from src.tools.shipping_tool import calc_shipping
from src.tools import ALL_TOOLS

class TestEcommerceTools(unittest.TestCase):
    
    def test_stock_tool_existing_items(self):
        """Test stock_tool returning correct stock for existing items (case-insensitive)."""
        self.assertEqual(check_stock("iPhone 15"), 10)
        self.assertEqual(check_stock("iphone 15"), 10)
        self.assertEqual(check_stock("MacBook M3"), 5)
        self.assertEqual(check_stock("macbook m3"), 5)
        self.assertEqual(check_stock("  iPad Air  "), 8)
        self.assertEqual(check_stock("AirPods Pro"), 15)

    def test_stock_tool_non_existent_item(self):
        """Test stock_tool returning 0 for items not in the inventory database."""
        self.assertEqual(check_stock("Samsung Galaxy S24"), 0)
        self.assertEqual(check_stock(""), 0)
        self.assertEqual(check_stock(None), 0)

    def test_discount_tool_valid_coupons(self):
        """Test discount_tool returning correct percentages for active coupons."""
        self.assertEqual(get_discount("WINNER"), 0.15)
        self.assertEqual(get_discount("winner"), 0.15)  # Case insensitive
        self.assertEqual(get_discount("  Winner  "), 0.15)  # Spaces
        self.assertEqual(get_discount("WELCOME"), 0.10)
        self.assertEqual(get_discount("welcome"), 0.10)

    def test_discount_tool_invalid_coupons(self):
        """Test discount_tool returning 0.0 for invalid coupon codes."""
        self.assertEqual(get_discount("LOSER"), 0.0)
        self.assertEqual(get_discount(""), 0.0)
        self.assertEqual(get_discount(None), 0.0)

    def test_shipping_tool_hanoi(self):
        """Test shipping_tool pricing calculations for Hanoi destination."""
        # Hanoi rate: base 30000.0 + 5000.0 * weight
        self.assertAlmostEqual(calc_shipping(0.0, "Hanoi"), 30000.0)
        self.assertAlmostEqual(calc_shipping(2.5, "Ha Noi"), 42500.0)
        self.assertAlmostEqual(calc_shipping("1.5", "hanoi"), 37500.0)

    def test_shipping_tool_hcm(self):
        """Test shipping_tool pricing calculations for Ho Chi Minh destination."""
        # HCM rate: base 50000.0 + 10000.0 * weight
        self.assertAlmostEqual(calc_shipping(0.0, "Ho Chi Minh"), 50000.0)
        self.assertAlmostEqual(calc_shipping(3.0, "TP.HCM"), 80000.0)
        self.assertAlmostEqual(calc_shipping("1.2", "HCM"), 62000.0)
        self.assertAlmostEqual(calc_shipping(2.0, "tp hcm"), 70000.0)

    def test_shipping_tool_others(self):
        """Test shipping_tool pricing calculations for other destinations."""
        # Other rate: base 80000.0 + 15000.0 * weight
        self.assertAlmostEqual(calc_shipping(2.0, "Da Nang"), 110000.0)
        self.assertAlmostEqual(calc_shipping("1.0", "Can Tho"), 95000.0)
        self.assertAlmostEqual(calc_shipping(0.0, ""), 0.0)
        self.assertAlmostEqual(calc_shipping(5.0, None), 0.0)

    def test_shipping_tool_invalid_weight(self):
        """Test shipping_tool fallback weight value when weight is not float convertible."""
        # If invalid weight, should treat as 0.0 kg -> base cost only
        self.assertAlmostEqual(calc_shipping("heavy_box", "Hanoi"), 30000.0)
        self.assertAlmostEqual(calc_shipping(None, "Ho Chi Minh"), 50000.0)

    def test_all_tools_structure(self):
        """Test that ALL_TOOLS exports the correct structure needed for the Agent."""
        self.assertEqual(len(ALL_TOOLS), 3)
        tool_names = [tool["name"] for tool in ALL_TOOLS]
        self.assertIn("check_stock", tool_names)
        self.assertIn("get_discount", tool_names)
        self.assertIn("calc_shipping", tool_names)
        
        for tool in ALL_TOOLS:
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("func", tool)
            self.assertTrue(callable(tool["func"]))

    def test_agent_parsing_robustness(self):
        """Test ReActAgent._parse_action_str with various formats of action calls."""
        from src.agent.agent import ReActAgent
        agent = ReActAgent(llm=None, tools=ALL_TOOLS)
        
        # Test Case 1: Standard keyword arguments
        name, args = agent._parse_action_str("calc_shipping(weight=1.5, destination='Hanoi')")
        self.assertEqual(name, "calc_shipping")
        self.assertEqual(args.get("weight"), 1.5)
        self.assertEqual(args.get("destination"), "Hanoi")
        
        # Test Case 2: Standard positional arguments
        name, args = agent._parse_action_str("calc_shipping(2.5, 'Ho Chi Minh')")
        self.assertEqual(name, "calc_shipping")
        self.assertEqual(args.get("weight"), 2.5)
        self.assertEqual(args.get("destination"), "Ho Chi Minh")
        
        # Test Case 3: Mixed positional & keyword arguments
        name, args = agent._parse_action_str("calc_shipping(3.0, destination='Da Nang')")
        self.assertEqual(name, "calc_shipping")
        self.assertEqual(args.get("weight"), 3.0)
        self.assertEqual(args.get("destination"), "Da Nang")

        # Test Case 4: Missing destination parameter (optional fallback)
        name, args = agent._parse_action_str("calc_shipping(weight=1.2)")
        self.assertEqual(name, "calc_shipping")
        self.assertEqual(args.get("weight"), 1.2)
        self.assertNotIn("destination", args)
        
        # Verify call with missing destination executes successfully and returns 0.0
        result = calc_shipping(**args)
        self.assertEqual(result, 0.0)

        # Test Case 5: Unquoted keyword argument values (often generated by smaller LLMs)
        name, args = agent._parse_action_str("calc_shipping(weight=1.5, destination=Hanoi)")
        self.assertEqual(name, "calc_shipping")
        self.assertEqual(args.get("weight"), 1.5)
        self.assertEqual(args.get("destination"), "Hanoi")


if __name__ == "__main__":
    unittest.main()
