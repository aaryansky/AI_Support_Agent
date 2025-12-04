import sqlite3
import os
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings # <--- Updated import

# Define paths relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "orders.db")
CHROMA_PATH = os.path.join(BASE_DIR, "data", "chroma_db")

@tool
def check_order_status(order_id: str):
    """Query the SQL database to find the status of an order given an Order ID (e.g., ORD-123)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT status, item FROM orders WHERE order_id=?", (order_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return f"Order {order_id} containing '{result[1]}' is currently: {result[0]}"
        return f"Order ID {order_id} not found."
    except Exception as e:
        return f"Error querying database: {str(e)}"

@tool
def get_refund_policy(query: str):
    """Search the policy documents for refund, shipping, or return information."""
    try:
        # <--- Updated to use Hugging Face (Free)
        hf_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        vector_store = Chroma(
            persist_directory=CHROMA_PATH, 
            embedding_function=hf_embeddings
        )
        # Search for the most relevant document
        retriever = vector_store.as_retriever(search_kwargs={"k": 1})
        docs = retriever.invoke(query)
        
        if not docs:
            return "No relevant policy information found."
            
        return "\n".join([d.page_content for d in docs])
    except Exception as e:
        return f"Error searching policy documents: {str(e)}"