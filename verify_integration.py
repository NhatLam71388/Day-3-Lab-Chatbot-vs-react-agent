import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.agent.agent import ReActAgent
from src.agent.chatbot import ChatbotBaseline
from src.tools import ALL_TOOLS
from unittest.mock import MagicMock

def test_run_simulated():
    print("--- Testing Member A Implementation ---\n")
    
    # 1. Mock LLM Provider
    mock_llm = MagicMock()
    mock_llm.model_name = "gemini-1.5-flash"
    
    # Simulated conversation for a stock check
    mock_llm.generate.side_effect = [
        {
            "content": "Thought: The user wants to check the stock for iPhone 15. I should use the check_stock tool.\nAction: check_stock(item_name='iPhone 15')",
            "usage": {"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80}
        },
        {
            "content": "Thought: I have the stock information now. There are 10 units.\nFinal Answer: Yes, we have 10 units of iPhone 15 in stock.",
            "usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120}
        }
    ]

    # 2. Initialize Agent with REAL tools from src/tools
    agent = ReActAgent(llm=mock_llm, tools=ALL_TOOLS)
    
    print("Running ReAct Agent with simulated 'iPhone 15' query...")
    result = agent.run("Is iPhone 15 in stock?")
    
    print("\n[AGENT OUTPUT]")
    print(f"Answer: {result['answer']}")
    print(f"Steps taken: {len(result['steps'])}")
    for step in result['steps']:
        print(f"  Step {step['step']}: {step['thought']}")
        print(f"    Action: {step['action']}")
        print(f"    Observation: {step['observation']}")
    
    print("\n[METRICS]")
    print(f"Total Tokens: {result['metrics']['total_tokens']}")
    print(f"Estimated Cost: ${result['metrics']['cost_usd']}")
    print(f"Latency: {result['metrics']['latency_ms']}ms")

    # 3. Test Chatbot Baseline
    print("\n" + "="*30 + "\n")
    print("Running Chatbot Baseline...")
    mock_llm.generate.side_effect = None
    mock_llm.generate.return_value = {
        "content": "We have various items in stock including iPhone 15 and MacBook M3.",
        "usage": {"prompt_tokens": 30, "completion_tokens": 15, "total_tokens": 45}
    }
    
    chatbot = ChatbotBaseline(llm=mock_llm)
    chat_result = chatbot.run("What do you have in stock?")
    print(f"Baseline Answer: {chat_result['answer']}")
    print(f"Baseline Cost: ${chat_result['metrics']['cost_usd']}")

if __name__ == "__main__":
    try:
        test_run_simulated()
        print("\n✅ Internal logic and tool integration check PASSED!")
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
