# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Nhật Lâm
- **Student ID**: 2A202600851
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

In this lab, my primary role was the **Tools & Test Developer** (working on branch `feat-tools`). I designed and implemented the e-commerce simulation environment, constructed metadata schemas for tool discovery, and wrote a robust suite of unit tests to prevent regression and runtime failures.

### 1. Modules Implemented
- **[stock_tool.py](file:///d:/AI_20K/Day-3-Lab-Chatbot-vs-react-agent/src/tools/stock_tool.py)**: Simulates inventory checking for products like iPhone 15, MacBook M3, etc. Normalizes item names to ensure case and whitespace insensitivity.
- **[discount_tool.py](file:///d:/AI_20K/Day-3-Lab-Chatbot-vs-react-agent/src/tools/discount_tool.py)**: Validates coupon codes and returns discount decimals (e.g. `0.15` for 15% discount for `WINNER`).
- **[shipping_tool.py](file:///d:/AI_20K/Day-3-Lab-Chatbot-vs-react-agent/src/tools/shipping_tool.py)**: Implements shipping rate formulas per city (Hanoi, HCM, and default other locations) with weight-based increments. Supports converting string representation of weights to floats.
- **[__init__.py](file:///d:/AI_20K/Day-3-Lab-Chatbot-vs-react-agent/src/tools/__init__.py)**: Bundles tools and exposes `ALL_TOOLS` with clear, precise text descriptions that LLM models parse to invoke the functions.
- **[test_tools.py](file:///d:/AI_20K/Day-3-Lab-Chatbot-vs-react-agent/tests/test_tools.py)**: Standard unit testing suite mapping all standard use cases, edge cases, and tool exports.

### 2. Code Highlights
Here is the definition of `ALL_TOOLS` in `src/tools/__init__.py`:
```python
ALL_TOOLS = [
    {
        "name": "check_stock",
        "description": "Checks available quantity for an item. Input: item_name (str). Returns: stock count (int).",
        "func": check_stock
    },
    {
        "name": "get_discount",
        "description": "Checks discount percentage for a coupon code. Input: coupon_code (str). Returns: discount percentage (float, e.g., 0.15 for 15%).",
        "func": get_discount
    },
    {
        "name": "calc_shipping",
        "description": "Calculates shipping cost based on weight and destination. Input: weight (float, in kg), destination (str, capitalized city name e.g. 'Hanoi'). Returns: shipping cost (float).",
        "func": calc_shipping
    }
]
```

### 3. How the Tools Interact with the ReAct Loop
- During execution, the LLM reads the description schemas of `ALL_TOOLS` provided in the system prompt.
- Based on the user's inquiry (e.g., *Check if MacBook M3 is available*), the LLM decides to trigger `check_stock(item_name='MacBook M3')`.
- The Agent parser extracts the tool name and arguments, triggers the corresponding python function, and formats the output into an `Observation` string which is fed back into the LLM context.

---

## II. Debugging Case Study (10 Points)

### 1. Problem Description
During testing of the shipping fee tool in integration trials, the LLM frequently generated action calls with weights as strings (e.g., `calc_shipping(weight="2.0", destination="Hanoi")`) instead of raw float numbers, or passed destinations with varying capitalization (e.g. `hanoi`, `tp.hcm`). This resulted in either type errors inside the math formula or routing failures.

### 2. Diagnosis
LLMs represent numbers as text strings and do not strictly guarantee type compliance unless the python-side function dynamically resolves, validates, and casts the inputs. Relying solely on the LLM to format types correctly is fragile.

### 3. Solution
I updated the tool code to handle normalization and casting internally:
1. **Weight parsing**: Used a `try/except` block to convert the `weight` argument to `float` internally, falling back to `0.0` on failure instead of raising a script crash.
2. **String normalization**: Used `" ".join(destination.lower().split())` to parse inputs like `"Ha Noi"`, `"hanoi"`, `"TP.HCM"`, and `"tp hcm"` uniformly.
3. This was validated by writing tests like `test_shipping_tool_invalid_weight` and `test_shipping_tool_others`.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: The `Thought` block acts as the scratchpad/mental map of the agent. A standard Chatbot is a single-shot generator; it tries to calculate the answer inline, which leads to arithmetic errors and hallucinated stock information. The ReAct Agent slows down, breaks the request into sequential steps, fetches state data first, and only then computes the final response.
2. **Reliability**: ReAct Agents can perform *worse* than Chatbots in simple Q&A because of parsing overhead, high token count, and latency. If the query is simple (e.g., "Hello, how are you?"), running a ReAct loop introduces redundant reasoning steps, increases costs, and raises the chance of JSON format errors.
3. **Observation**: Observations ground the agent in reality. Without observations, the agent works entirely on pre-trained memory. When a tool returns `stock count: 0`, the agent receives this observation and immediately changes its next Thought (e.g., "Since the item is out of stock, I should inform the customer instead of calculating shipping fees").

---

## IV. Future Improvements (5 Points)

1. **Scalability**: For a larger e-commerce catalog, we cannot dump hundreds of tool definitions directly into the LLM system prompt due to context limitations and token costs. We should implement a **Semantic Tool Retriever** (using a Vector DB) that selects the top 3-5 relevant tools dynamically based on the user prompt before injecting them into the system prompt.
2. **Safety & Guardrails**: Add input sanitization on arguments (e.g., preventing shell injections or prompt injection attempts through tool arguments) and set strict rate-limiting on API endpoints.
3. **Parallel Tool Execution**: Enable the agent to call multiple independent tools in parallel in a single loop step (e.g., calling `check_stock` for multiple items simultaneously) to decrease total latency.
