import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        System prompt that instructs the agent to follow the ReAct pattern.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""You are an intelligent e-commerce assistant. You must solve the user's request by following a Thought-Action-Observation loop.

Available Tools:
{tool_descriptions}

Rules:
1. Your response MUST follow this exact format:
Thought: your line of reasoning about what to do next.
Action: tool_name(key1='value1', key2='value2')
Observation: result of the tool call (this will be provided to you).
... (repeat if needed)
Final Answer: your final response to the user.

2. ONLY use the tools listed above.
3. If you have enough information, provide the Final Answer immediately.
4. If you use an Action, you must wait for an Observation. DO NOT hallucinate the Observation.
5. In the Action, use the format: tool_name(parameter_name='value')
"""

    def run(self, user_input: str) -> Dict[str, Any]:
        """
        Implements the ReAct loop logic.
        """
        from src.telemetry.metrics import tracker
        import time

        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        start_overall = time.time()
        steps_list = []
        metrics = {
            "latency_ms": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0
        }
        
        current_history = f"User Question: {user_input}\n"
        step_count = 0
        final_answer = "I'm sorry, I couldn't find an answer within the allowed steps."

        while step_count < self.max_steps:
            step_count += 1
            
            # Generate LLM response
            response = self.llm.generate(current_history, system_prompt=self.get_system_prompt())
            
            # Update metrics
            metrics["prompt_tokens"] += response["usage"].get("prompt_tokens", 0)
            metrics["completion_tokens"] += response["usage"].get("completion_tokens", 0)
            metrics["total_tokens"] += response["usage"].get("total_tokens", 0)
            metrics["cost_usd"] += tracker._calculate_cost(self.llm.model_name, response["usage"])
            
            content = response["content"]
            current_history += content + "\n"
            
            # Parse Thought and Action
            thought_match = re.search(r"Thought:\s*(.*)", content)
            thought = thought_match.group(1) if thought_match else "Thinking..."
            
            # Check for Final Answer
            if "Final Answer:" in content:
                final_answer = content.split("Final Answer:")[-1].strip()
                steps_list.append({
                    "step": step_count,
                    "thought": thought,
                    "action": "None (Final Answer)",
                    "observation": "N/A"
                })
                break
            
            # Check for Action
            action_match = re.search(r"Action:\s*(\w+\(.*\))", content)
            if action_match:
                action_str = action_match.group(1)
                
                # Execute tool
                tool_name, args = self._parse_action_str(action_str)
                observation = self._execute_tool(tool_name, args)
                
                # Update history with observation
                obs_text = f"Observation: {observation}"
                current_history += obs_text + "\n"
                
                steps_list.append({
                    "step": step_count,
                    "thought": thought,
                    "action": action_str,
                    "observation": observation
                })
            else:
                # If no action found and no final answer, something is wrong with formatting
                steps_list.append({
                    "step": step_count,
                    "thought": thought,
                    "action": "Invalid Format",
                    "observation": "I need to follow the Thought/Action format."
                })
                current_history += "Observation: Please provide an Action or a Final Answer in the correct format.\n"

        metrics["latency_ms"] = int((time.time() - start_overall) * 1000)
        
        result = {
            "answer": final_answer,
            "steps": steps_list,
            "metrics": metrics
        }
        
        logger.log_event("AGENT_END", {"steps": step_count, "success": "Final Answer" in content})
        return result

    def _parse_action_str(self, action_str: str):
        """Simple regex to extract tool name and kwargs from Action: tool_name(arg='val')"""
        match = re.search(r"(\w+)\((.*)\)", action_str)
        if not match:
            return None, {}
        
        tool_name = match.group(1)
        args_str = match.group(2)
        
        # Simple extraction of keyword arguments
        args = {}
        if args_str:
            # Matches key='value' or key=value
            arg_pairs = re.findall(r"(\w+)\s*=\s*['\"]?([^'\"]*)['\"]?", args_str)
            for k, v in arg_pairs:
                args[k] = v
        return tool_name, args

    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """
        Executes a tool from the toolset.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                try:
                    # Call the tool function with unpacked arguments
                    result = tool['func'](**args)
                    return str(result)
                except Exception as e:
                    return f"Error executing {tool_name}: {str(e)}"
        
        return f"Tool {tool_name} not found."
