from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.graph import graph

# Initialize FastAPI
app = FastAPI(
    title="FutureSmart AI Support Agent",
    description="A LangGraph Agent capable of checking orders (SQL) and answering policy questions (Vector DB)."
)

# Define the request format
class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default_thread"  # Used for conversation memory

@app.get("/")
def health_check():
    return {"status": "active", "message": "AI Agent is online. Use POST /chat to interact."}

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    """
    Main endpoint to interact with the agent.
    """
    try:
        # 1. Setup config for memory
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # 2. Input format for LangGraph
        inputs = {"messages": [("user", request.message)]}
        
        # 3. Invoke the graph (The Agent Thinks & Acts)
        # graph.invoke() runs the entire flow until it stops
        result = graph.invoke(inputs, config=config)
        
        # 4. Extract the final response
        final_message = result["messages"][-1].content
        
        return {
            "response": final_message,
            "thread_id": request.thread_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))