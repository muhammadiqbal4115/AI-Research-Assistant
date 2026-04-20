import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.tools import ArxivQueryRun
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_tavily import TavilySearch
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .tool-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 1rem;
        background-color: #667eea;
        color: white;
        font-size: 0.85rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .action-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .action-card h3 {
        color: #667eea;
        margin-top: 0;
    }
</style>
""", unsafe_allow_html=True)

# State Schema
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Initialize tools and LLM (cached to avoid re-initialization)
@st.cache_resource
def initialize_chatbot():
    """Initialize the LangGraph chatbot with tools"""
    
    # Set environment variables
    os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    
    # Initialize tools
    api_wrapper_arxiv = ArxivAPIWrapper(top_k_results=2, doc_content_chars_max=500)
    arxiv = ArxivQueryRun(api_wrapper=api_wrapper_arxiv)
    
    wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    
    tavily = TavilySearch()
    tavily_tool = tavily.as_tool()
    
    tools = [arxiv, wiki, tavily_tool]
    
    # Initialize LLM
    llm = ChatGroq(model="openai/gpt-oss-120b")
    llm_with_tools = llm.bind_tools(tools, strict=True)
    
    # Node definition
    def tool_calling_llm(state: State):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}
    
    # Build graph
    builder = StateGraph(State)
    builder.add_node("tool_calling_llm", tool_calling_llm)
    builder.add_node("tools", ToolNode(tools, handle_tool_errors=True))
    builder.add_edge(START, "tool_calling_llm")
    builder.add_conditional_edges(
        "tool_calling_llm",
        tools_condition,
    )
    # After tools execute, go back to LLM to generate final response
    builder.add_edge("tools", "tool_calling_llm")
    
    graph = builder.compile()
    
    return graph

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_action" not in st.session_state:
    st.session_state.selected_action = None

if "graph" not in st.session_state:
    with st.spinner("🔧 Initializing AI Research Assistant..."):
        st.session_state.graph = initialize_chatbot()

# Header
st.markdown('<h1 class="main-header">🤖 AI Research Assistant</h1>', unsafe_allow_html=True)

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This assistant helps you:
    - 📄 Search research papers (ArXiv)
    - 📖 Get info from Wikipedia
    - 🔍 Search the web for recent news
    """)
    
    st.markdown("---")
    st.subheader("🎯 How to Use")
    st.markdown("""
    1. **Select an action** from the main screen
    2. **Enter your query**
    3. **Get AI-powered results**
    """)
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.selected_action = None
        st.rerun()
    
    st.markdown("---")
    st.caption("Powered by LangGraph + Groq")

# Main area - Action selection
if not st.session_state.selected_action:
    st.markdown("### 👋 Welcome! What would you like to do?")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Search Web\n\nFind recent news & information", 
                     use_container_width=True, 
                     key="web_search"):
            st.session_state.selected_action = "web_search"
            st.rerun()
    
    with col2:
        if st.button("📄 Read Research Paper\n\nSearch ArXiv papers", 
                     use_container_width=True,
                     key="research_paper"):
            st.session_state.selected_action = "research_paper"
            st.rerun()
    
    with col3:
        if st.button("📖 Search Wikipedia\n\nGet encyclopedic info", 
                     use_container_width=True,
                     key="wikipedia"):
            st.session_state.selected_action = "wikipedia"
            st.rerun()
    
    st.markdown("---")
    st.markdown("#### 💡 Example Queries")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🔍 Web Search**")
        st.code("Recent AI news for March 2025", language=None)
    with col2:
        st.markdown("**📄 Research**")
        st.code("1706.03762\n(or)\nAttention is all you need", language=None)
    with col3:
        st.markdown("**📖 Wikipedia**")
        st.code("What is machine learning?", language=None)

else:
    # Show selected action
    action_icons = {
        "web_search": "🔍 Web Search",
        "research_paper": "📄 Research Paper",
        "wikipedia": "📖 Wikipedia"
    }
    
    action_prompts = {
        "web_search": "Search the web for recent news and information...",
        "research_paper": "Enter paper ID (e.g., 1706.03762) or topic...",
        "wikipedia": "Ask about any topic..."
    }
    
    # Action header with change button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### {action_icons[st.session_state.selected_action]}")
    with col2:
        if st.button("↩️ Change", use_container_width=True):
            st.session_state.selected_action = None
            st.rerun()

    
    st.markdown("---")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input(action_prompts[st.session_state.selected_action]):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking and searching..."):
                try:
                    # Create a modified prompt based on action to guide tool selection
                    if st.session_state.selected_action == "web_search":
                        guided_prompt = f"Use web search to find: {prompt}"
                    elif st.session_state.selected_action == "research_paper":
                        guided_prompt = f"Search ArXiv for: {prompt}"
                    elif st.session_state.selected_action == "wikipedia":
                        guided_prompt = f"Search Wikipedia for: {prompt}"
                    else:
                        guided_prompt = prompt
                    
                    # Invoke the graph
                    result = st.session_state.graph.invoke({
                        "messages": [HumanMessage(content=guided_prompt)]
                    })
                    
                    # Get the last AI message (which should be the final response after tool use)
                    final_response = None
                    for msg in reversed(result["messages"]):
                        if isinstance(msg, AIMessage) and msg.content:
                            final_response = msg.content
                            break
                    
                    if final_response:
                        # Display the response
                        st.markdown(final_response)
                        
                        # Add to chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": final_response
                        })
                    else:
                        error_msg = "I couldn't generate a response. Please try again."
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
                        
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    # Also show the full error for debugging
                    with st.expander("Debug Info"):
                        st.code(str(e))
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Built with LangChain, LangGraph, and Streamlit | "
    "Powered by Groq (qwen-qwq-32b)"
    "</div>",
    unsafe_allow_html=True
)
