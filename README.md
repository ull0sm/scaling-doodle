# Simple Chatbot with n8n Integration

A minimal Streamlit-based chatbot application that integrates with n8n workflow for AI-powered responses.

## Features

- 💬 ChatGPT-like user interface
- 🤖 Integration with n8n AI Agent workflow
- 🎨 Clean and modern dark theme
- 📝 Chat history within session
- ⚡ Simple and lightweight

## Prerequisites

- Python 3.8 or higher
- n8n instance with the AI Agent workflow deployed
- n8n webhook URL

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and set your n8n webhook URL:

```env
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/c69d3aba-2057-4ad6-a853-5fdff3bd8eb0
```

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

Navigate to the chat page at `http://localhost:8501/app/chat`

## n8n Workflow Integration

### Expected Webhook Response Format

Your n8n workflow should return JSON with a `reply` field:

```json
{
  "reply": "The AI assistant's response text here"
}
```

### Request Payload

The app sends the following JSON to your webhook:

```json
{
  "message": "User's question text",
  "session_id": "unique-session-id"
}
```

### n8n Workflow Setup

The provided n8n workflow includes:
- **AI Agent** with system message defining Sam's role
- **Vector Store Tool** for RAG (Pinecone + Google Gemini embeddings)
- **Web Search Tool** for real-time information
- **Window Buffer Memory** for conversation context
- **Google Gemini Chat Model** for responses

Make sure your workflow is activated in n8n and the webhook URL is accessible.

## Project Structure

```
.
├── app.py              # Main Streamlit application
├── pages/
│   └── chat.py         # Chat page at /app/chat
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Usage

1. Start the application with `streamlit run app.py`
2. Navigate to the chat page (automatically redirects)
3. Type your message in the input box
4. Press Send or hit Enter to get a response from Sam

## Customization

### Change Assistant Name

Edit `pages/chat.py` and replace "Sam" with your preferred name.

### Modify Theme

Edit the CSS in `pages/chat.py` under the `<style>` tag to customize colors and styling.

### Adjust Timeout

Edit `REQUEST_TIMEOUT` in `.env` (default: 30 seconds) if your n8n workflow needs more time.

## Future Enhancements

This is a foundation for:
- 🔐 User authentication and login
- 💾 Persistent chat sessions across visits
- 👥 Multi-user support
- 📊 Chat history management
- 🔄 Session switching and management

## Troubleshooting

### "Missing N8N_WEBHOOK_URL" error
- Ensure `.env` file exists in the project root
- Verify `N8N_WEBHOOK_URL` is set correctly

### Connection errors
- Check that your n8n workflow is activated
- Verify the webhook URL is accessible
- Test the webhook directly with curl

### Timeout errors
- Increase `REQUEST_TIMEOUT` in `.env`
- Check n8n workflow performance

## License

This project is provided as-is for your use.
