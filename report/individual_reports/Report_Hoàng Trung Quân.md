# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Hoàng Trung Quân  
- **Student ID**: 2A202600720
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

In this lab, I served as the **Core Backend Developer** (working on branch `feat-agent-core`). I was responsible for building the primary reasoning logic of the system, including the ReAct loop, the baseline chatbot, and the telemetry metrics for cost estimation.

### 1. Modules Implemented
- **[agent.py](file:///d:/2%20Code/3%20Test/LAB_3/src/agent/agent.py)**: Developed the `ReActAgent` class which orchestrates the `Thought -> Action -> Observation` loop. I implemented a regex-based parser to extract tool calls and parameters from the LLM's conversational output.
- **[chatbot.py](file:///d:/2%20Code/3%20Test/LAB_3/src/agent/chatbot.py)**: Created the `ChatbotBaseline` class to provide a direct LLM response benchmark. This is essential for comparing the grounding capabilities of the ReAct agent against a standard model.
- **[metrics.py](file:///d:/2%20Code/3%20Test/LAB_3/src/telemetry/metrics.py)**: Updated the `PerformanceTracker` to include real-world pricing for GPT-4o and Gemini 1.5 models, ensuring that the dashboard shows actual USD costs instead of placeholders.

### 2. Code Highlights
One of the most critical parts I worked on was the ReAct logic and telemetry aggregation:
```python
# Cumulative metrics tracking across multiple steps in agent.py
while step_count < self.max_steps:
    response = self.llm.generate(current_history, system_prompt=self.get_system_prompt())
    
    # Aggregating tokens and costs from each step
    metrics["prompt_tokens"] += response["usage"].get("prompt_tokens", 0)
    metrics["completion_tokens"] += response["usage"].get("completion_tokens", 0)
    metrics["cost_usd"] += tracker._calculate_cost(self.llm.model_name, response["usage"])
    
    # Regex parsing for tool execution
    action_match = re.search(r"Action:\s*(\w+\(.*\))", content)
    if action_match:
        tool_name, args = self._parse_action_str(action_match.group(1))
        # ... execute and loop ...
```

### 3. How the Code Interacts with the ReAct Loop
- The **System Prompt** I designed forces the LLM to structure its output into distinct blocks.
- The **Parser** intercepts the `Action` line, halts the conversation generation, triggers a Python tool, and injects the `Observation` back into the context.
- This continues until the LLM generates a `Final Answer` block, at which point the loop terminates and returns the aggregate data.

---

## II. Debugging Case Study (10 Points)

### 1. Problem Description
During initial trials, the Agent often failed to terminate. Instead of providing a `Final Answer`, it would get stuck in a loop repeating the same `Action` or it would fail to parse the `Observation` correctly because it included Markdown code blocks (backticks like ` ```Action: ... ``` `).

### 2. Diagnosis
I checked the telemetry logs and found that the LLM was assuming it should format the "Action" as a code snippet for readability. Since my initial regex didn't account for backticks, the `_parse_action_str` returned `None`, and the agent didn't know what to do next, often repeating its previous thought.

### 3. Solution
I solved this by:
1.  **Refining the Regex**: Updated the pattern to be more flexible, specifically ignoring surrounding whitespace and potentially tricky characters.
2.  **Prompt Engineering**: Added a strict rule in the system prompt: *"Do NOT use Markdown backticks. Every response must be plain text in the specified format."*
3.  **Fallback Logic**: If no Action or Final Answer is detected after parsing, I now inject a reminder observation into the loop: *"Observation: Please provide an Action or Final Answer in the correct format."* This "self-corrects" the agent in the next step.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1.  **Reasoning**: The `Thought` block is like a "chain of thought" that forces the model to verbalize its plan. Without it, the model often makes "leaps of logic" that result in calling tools with the wrong arguments. Verbalizing the plan makes the transitions between steps much more reliable.
2.  **Reliability**: The ReAct agent is significantly more reliable for data-driven tasks (like checking stock or calculating shipping) because it is grounded in real environment feedback. However, a Chatbot is much faster for simple greetings or generic advice where tools aren't needed.
3.  **Observation**: Environment feedback is the "tether to reality." I observed that if a tool returns an error message, a well-prompted ReAct agent can actually *read* that error and try a different approach in the next step, which is something a static chatbot cannot do.

---

## IV. Future Improvements (5 Points)

1.  **Context Window Management**: As the loop progresses, the history grows significantly. For production, we should implement a "sliding window" or "summarization" mechanism to keep the context size manageable without losing the initial user intent.
2.  **Retry logic**: If a tool call fails due to a temporary network blip, the agent should have a mechanism to retry the action once before reporting a failure.
3.  **Streaming Mind Inspector**: Currently, the UI waits for the full `run()` to finish. Implementing a streaming architecture where the UI updates live at every `Thought` and `Observation` would greatly improve the user experience (UX).
