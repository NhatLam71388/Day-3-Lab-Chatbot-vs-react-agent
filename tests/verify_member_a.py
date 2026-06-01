import sys
import os
import unittest
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.agent import ReActAgent
from src.agent.chatbot import ChatbotBaseline
from src.core.llm_provider import LLMProvider

class TestMemberA(unittest.TestCase):
    def setUp(self):
        self.mock_llm = MagicMock(spec=LLMProvider)
        self.mock_llm.model_name = "gpt-4o"
        
        self.tools = [
            {
                "name": "check_stock",
                "description": "Checks stock",
                "func": lambda item_name: f"{item_name} has 10 units"
            }
        ]

    def test_chatbot_baseline_format(self):
        self.mock_llm.generate.return_value = {
            "content": "Hello! I am a chatbot.",
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            "latency_ms": 100
        }
        
        chatbot = ChatbotBaseline(self.mock_llm)
        result = chatbot.run("Hi")
        
        self.assertIn("answer", result)
        self.assertEqual(result["answer"], "Hello! I am a chatbot.")
        self.assertEqual(len(result["steps"]), 0)
        self.assertIn("metrics", result)
        self.assertIn("cost_usd", result["metrics"])

    def test_react_agent_loop(self):
        # Mock LLM and tools logic
        # First call: Thought + Action
        # Second call: Final Answer
        self.mock_llm.generate.side_effect = [
            {
                "content": "Thought: I need to check stock.\nAction: check_stock(item_name='iPhone 15')",
                "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30}
            },
            {
                "content": "Thought: I have the stock info.\nFinal Answer: iPhone 15 has 10 units.",
                "usage": {"prompt_tokens": 40, "completion_tokens": 5, "total_tokens": 45}
            }
        ]
        
        agent = ReActAgent(self.mock_llm, self.tools)
        result = agent.run("Is iPhone 15 in stock?")
        
        self.assertEqual(result["answer"], "iPhone 15 has 10 units.")
        self.assertEqual(len(result["steps"]), 2)
        self.assertEqual(result["steps"][0]["action"], "check_stock(item_name='iPhone 15')")
        self.assertEqual(result["steps"][0]["observation"], "iPhone 15 has 10 units")
        self.assertIn("metrics", result)
        self.assertGreater(result["metrics"]["total_tokens"], 0)
        self.assertGreater(result["metrics"]["cost_usd"], 0)

if __name__ == "__main__":
    unittest.main()
