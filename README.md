# 🤖 AI Research Assistant - LangGraph Multi-Tool Chatbot

A powerful Streamlit-based chatbot that uses LangGraph to orchestrate multiple search tools (ArXiv, Wikipedia, Tavily) for AI research and general queries. **Now with action selection interface!**

## ✨ Features

- 🎯 **Action Selection**: Choose your search type before querying
- 📄 **ArXiv Search**: Query academic papers by ID or topic
- 📖 **Wikipedia Search**: Get information from Wikipedia
- 🔍 **Tavily Search**: Access recent news and web information
- 🤖 **Intelligent Tool Routing**: LangGraph routes to the selected tool
- 💬 **Chat Interface**: Clean, interactive chat UI with history
- ⚡ **Powered by Groq**: Fast inference with qwen-qwq-32b model

## 🎯 How It Works

1. **Select Action**: Choose from Web Search, Research Paper, or Wikipedia
2. **Enter Query**: Type your question or search term
3. **Get Results**: The AI uses the appropriate tool to fetch results
4. **Continue Chat**: Ask follow-up questions within the same session
5. **Change Action**: Switch to a different search type anytime

## 🛠️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file and add your API keys:

```
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

**Get your API keys:**
- **Groq**: https://console.groq.com/
- **Tavily**: https://tavily.com/

### 3. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 💡 Usage Examples

### Web Search (Tavily)
1. Click **"🔍 Search Web"**
2. Enter: `Recent AI news for March 2025`
3. Get latest web results

### Research Papers (ArXiv)
1. Click **"📄 Read Research Paper"**
2. Enter: `1706.03762` or `Attention is all you need`
3. Get paper summaries

### Wikipedia
1. Click **"📖 Search Wikipedia"**
2. Enter: `What is machine learning?`
3. Get encyclopedic information

You can switch between actions anytime using the "↩️ Change" button!

## 🏗️ Architecture

The app uses LangGraph to create an agentic workflow with action-guided tool selection:

```
Action Selection → User Query → Guided Prompt → LLM (with tools) → Tool Execution → Response
```

**User Flow:**
1. User selects action (Web Search / Research Paper / Wikipedia)
2. User enters query with action-specific placeholder
3. App creates guided prompt (e.g., "Search ArXiv for: {query}")
4. LLM intelligently routes to the appropriate tool
5. Tool executes and returns results
6. User can continue conversation or change action

**Graph Structure:**
1. **START** → `tool_calling_llm` node
2. `tool_calling_llm` → Conditional edge:
   - If tool call needed → `tools` node
   - If no tool call → END
3. `tools` → END

## 📦 Project Structure

```
.
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .env               # Your API keys (create this)
└── README.md          # This file
```

## 🔧 Customization

### Change the LLM Model

Edit line 64 in `app.py`:

```python
llm = ChatGroq(model="qwen-qwq-32b")  # Change to other Groq models
```

Available Groq models: `mixtral-8x7b-32768`, `llama2-70b-4096`, etc.

### Adjust Tool Parameters

Modify the tool wrappers (lines 50-56):

```python
# Example: Get more ArXiv results
api_wrapper_arxiv = ArxivAPIWrapper(
    top_k_results=5,  # Change from 2 to 5
    doc_content_chars_max=1000  # Increase content length
)
```

## 🚀 Features Overview

### Action Selection Interface
- **Welcome Screen**: Three large action buttons to choose your search type
- **Guided Experience**: Each action has customized placeholder text
- **Easy Switching**: Change actions anytime without losing chat history

### Chat Interface
- **Message History**: Conversation persists during the session
- **Clear History**: Reset the conversation with one click
- **Responsive Design**: Works on desktop and mobile

### Sidebar
- **About Section**: Quick overview of available tools
- **How to Use**: Step-by-step guide
- **Clear Chat**: Reset conversation history

### Error Handling
- Graceful error messages
- API failure recovery
- User-friendly error display

## 🧪 Testing

Test different action types:

1. **Web Search Action**:
   - Select "🔍 Search Web"
   - Try: `latest developments in AI safety`
   - Try: `AI news for March 2025`

2. **Research Paper Action**:
   - Select "📄 Read Research Paper"
   - Try: `2103.14030` (paper ID)
   - Try: `transformer architecture explained`

3. **Wikipedia Action**:
   - Select "📖 Search Wikipedia"
   - Try: `neural networks`
   - Try: `What is reinforcement learning?`

4. **Action Switching**:
   - Start with one action, ask a question
   - Click "↩️ Change" to switch actions
   - Verify chat history persists

## 📝 Notes

- First run may take a moment to initialize the graph
- The app uses `@st.cache_resource` to cache the chatbot initialization
- Chat history is stored in session state (resets on page refresh)

## 🤝 Contributing

Feel free to customize and extend this app:
- Add more tools (Google Search, DuckDuckGo, etc.)
- Implement conversation memory across sessions
- Add voice input/output
- Create different agent personalities

## 📄 License

This project is open source and available for educational purposes.

## 🆘 Troubleshooting

**Issue**: "Module not found" error
- **Solution**: Run `pip install -r requirements.txt`

**Issue**: "API key not found" error
- **Solution**: Check your `.env` file has the correct keys

**Issue**: Slow responses
- **Solution**: Try a different Groq model or reduce `top_k_results`

**Issue**: Graph visualization doesn't show
- **Solution**: This is expected - the original code's `display(Image(...))` is for Jupyter notebooks

---

Built with ❤️ using LangChain, LangGraph, Groq, and Streamlit
