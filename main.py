from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.tools import FunctionTool
from llama_index.memory.mem0 import Mem0Memory  
from llama_index.core.agent import ReActAgent
from llama_index.core.llms import ChatMessage
from typing import Optional, Dict, Any
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import tool_descriptions
import streamlit as st
import nest_asyncio
import config
import os

# Initialize environment
class SessionManager:
    @staticmethod
    # Initialize session state for chat history and memory
    def initialize_session_state():
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "chat_memory" not in st.session_state:
            st.session_state.chat_memory = ChatMemoryBuffer.from_defaults(token_limit=40000)


# Initialize the memory manager
class MemoryManager:
    def __init__(self):
        self.memory = self.create_memory()

    # Function to create memory
    @staticmethod
    def create_memory():
        return Mem0Memory.from_config(context=config.context, config=config.memory_config, search_msg_limit=5)
    
    # Function to add, update, delete memory. '.add()' method decides if it is an update, delete or add
    def handle_memory(self, content: str, user_id: str = "default_user"):
        try:
            memory_id = self.memory.add(messages=[{"role": "user", "content": content}], user_id=user_id)
            st.write(f"Memory ID: {memory_id}")
            return f"Memory added successfully with ID: {memory_id}" if memory_id.get("results") else "This is not a valid memory entry."
        except Exception as e:
            return f"An error occurred while adding to memory: {e}"
    
    # Function to delete memory
    def delete_memory(self):
        try:
            client = QdrantClient(url="http://qdrant:6333")
            client.delete_collection(collection_name="long_term_memory")
            self.memory = self.create_memory()
            st.write("Memory deleted successfully.")
            return "Memory deleted successfully."
        except Exception as e:
            return f"An error occurred while deleting memory: {e}"

# Initialize the agent manager
class AgentManager:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "") or st.sidebar.text_input("Enter your Gemini API Key", type="password")
        if self.api_key:
            os.environ["GEMINI_API_KEY"] = self.api_key
        
        # Initialize the LLM
        self.llm = GoogleGenAI(model="gemini-2.0-flash", api_key=self.api_key)
        # Initialize the memory manager
        self.memory_manager = MemoryManager()

        # Initialize the agent with tools
        memory_tool = FunctionTool.from_defaults(fn=self.memory_manager.handle_memory, description=tool_descriptions.memory_tool_description)
        clear_memory_tool = FunctionTool.from_defaults(fn=self.memory_manager.delete_memory, description=tool_descriptions.clear_memory_tool_description)
        
        # Initialize the agent with memory and specify the tools
        self.agent = ReActAgent.from_tools(tools=[memory_tool, clear_memory_tool], llm=self.llm, memory=self.memory_manager.memory, verbose=True)

# Initialize the chat UI
class ChatUI:
    @staticmethod
    def display_chat_ui():
        st.title("AI Chat Assistant")
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Function to process user input
    @staticmethod
    def process_user_input():
        user_input = st.chat_input("Type your message here...")
        if user_input:
            with st.chat_message("user"):
                st.write(user_input)

            # Append user input to chat history and memory
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_memory.put(ChatMessage(role="user", content=user_input))
            
            # Generate a response from the agent
            with st.spinner("Thinking..."):
                response = st.session_state.agent.chat(user_input, chat_history=st.session_state.chat_memory.get_all())
            
            # Display the response
            with st.chat_message("assistant"):
                st.write(response.response)
            
            # Append the assistant's response to chat history and memory
            st.session_state.chat_history.append({"role": "assistant", "content": response.response})
            st.session_state.chat_memory.put(ChatMessage(role="assistant", content=response.response))
            
            # Update the session state
            st.rerun()

# Main function to run the AI Chat Assistant
class AIChatAssistant:
    def __init__(self):
        load_dotenv()
        nest_asyncio.apply()
        st.set_page_config(page_title="AI Chat Assistant", layout="wide")
        SessionManager.initialize_session_state()
        self.agent_manager = AgentManager()
        st.session_state.agent = self.agent_manager.agent
        ChatUI.display_chat_ui()
        ChatUI.process_user_input()

# Run the AI Chat Assistant
if __name__ == "__main__":
    AIChatAssistant()
