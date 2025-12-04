from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.state import State
from app.tools import check_order_status, get_refund_policy
from dotenv import load_dotenv

load_dotenv()

# --- 1. Initialize the Model (Groq) ---
# We use Llama 3.3 70B because it is excellent at tool calling
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# Bind tools to the model so it knows they exist
tools = [check_order_status, get_refund_policy]
llm_with_tools = llm.bind_tools(tools)

# --- 2. Define System Prompt ---
sys_msg = """You are a helpful customer support assistant for 'FutureSmart AI'.
- You have access to the company's refund policies (Vector DB) and order status database (SQL).
- If a user asks about an order, ALWAYS check the order status tool first.
- If a user asks about policies, use the refund policy tool.
- Be concise and professional.
"""

# --- 3. Define Nodes ---

def chatbot(state: State):
    """The main node where the LLM decides what to do."""
    return {"messages": [llm_with_tools.invoke([("system", sys_msg)] + state["messages"])]}

def route_tools(state: State):
    """Conditional Logic: Check if the LLM wants to use a tool."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# --- 4. Build the Graph ---
graph_builder = StateGraph(State)

# Add Nodes
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))

# Add Edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", route_tools, {"tools": "tools", END: END})
graph_builder.add_edge("tools", "chatbot") # Loop back to chatbot after tool use

# --- 5. Compile with Memory ---
# MemorySaver allows us to pause/resume the conversation (HITL)
memory = MemorySaver()

# interrupt_before=["tools"] checks with a human before running sensitive tools (Optional for this demo)
# For this specific "Vibe Code" demo, we will allow it to run automatically, 
# but you can uncomment 'interrupt_before' to show off HITL features.
graph = graph_builder.compile(checkpointer=memory)