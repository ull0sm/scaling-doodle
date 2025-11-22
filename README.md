# Company Insight Chat UI 💼

A minimal dark-mode Streamlit frontend for an n8n LangChain-based company insight & career guidance chatbot named "Sam". This application provides authentication via Supabase, persistent chat sessions, and seamless integration with your existing n8n workflow.

> **🚀 New here?** Check out [QUICKSTART.md](QUICKSTART.md) for a 5-minute setup guide!

## 🎯 Features

- **Dark Theme UI**: Clean, professional dark interface inspired by modern chat applications
- **Supabase Authentication**: Built-in Google OAuth (no manual Authlib configuration)
- **Persistent Sessions**: Multiple chat sessions per user, stored in Supabase
- **n8n Integration**: Sends user messages to your existing n8n webhook and receives AI responses
- **Profile Summarization**: Automatically generates user profile summaries to personalize responses
- **Reliable Error Handling**: Graceful fallbacks for failed API calls and malformed responses

## 📋 Prerequisites

- Python 3.8 or higher
- Supabase account and project
- n8n instance with the chatbot workflow deployed
- Google OAuth credentials (configured in Supabase)

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd scaling-doodle
pip install -r requirements.txt
```

### 2. Set Up Supabase Database

1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Copy and paste the contents of `supabase_schema.sql`
4. Run the SQL script to create all necessary tables and policies

This will create:
- `users` table (stores user profiles and summaries)
- `sessions` table (stores chat sessions)
- `messages` table (stores all chat messages)
- `user_traits` table (for future trait extraction features)
- Row Level Security policies to ensure data privacy

### 3. Configure Google OAuth in Supabase

1. In Supabase dashboard, go to **Authentication > Providers**
2. Enable the **Google** provider
3. Add your Google OAuth credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create OAuth 2.0 credentials
   - Add authorized redirect URI: `https://<your-project>.supabase.co/auth/v1/callback`
4. Copy your Google Client ID and Secret into Supabase
5. Add your app URL to authorized redirect URLs (e.g., `http://localhost:8501`)

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key-here

# n8n Webhook Configuration
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd

# Application Settings
PROFILE_SUMMARY_MESSAGE_THRESHOLD=10
REQUEST_TIMEOUT=30
```

**Where to find these values:**

- **SUPABASE_URL**: Supabase Project Settings > API > Project URL
- **SUPABASE_KEY**: Supabase Project Settings > API > Project API keys > `anon` `public` key
- **N8N_WEBHOOK_URL**: See the n8n webhook configuration section below

### 5. Verify Your Setup (Optional but Recommended)

Run the diagnostic tool to check your configuration:

```bash
python3 diagnose.py
```

This will verify:
- ✓ Python version and dependencies
- ✓ All required files present
- ✓ Environment variables configured
- ✓ Supabase connection working
- ✓ n8n webhook responding

### 6. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🔗 n8n Webhook Configuration

### Understanding the n8n Workflow

Your n8n workflow uses a **Chat Trigger** node which creates a webhook endpoint. This is the entry point where the Streamlit app sends user messages.

#### Current Workflow Structure:
```
When chat message received (Chat Trigger)
    ↓
AI Agent (with system message)
    ├─ Vector Store Tool (Pinecone + Gemini embeddings)
    ├─ Search Tool (SearchApi)
    ├─ Memory (Window Buffer)
    └─ Language Model (Google Gemini)
```

### How to Find Your Webhook URL

#### Option 1: From n8n Webhook ID (Current Setup)
Your workflow's Chat Trigger has webhook ID: `5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd`

The webhook URL format is:
```
https://<your-n8n-instance>/webhook/<webhook-id>
```

For example:
- Self-hosted: `https://n8n.yourcompany.com/webhook/5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd`
- n8n cloud: `https://your-instance.app.n8n.cloud/webhook/5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd`

#### Option 2: Get URL from n8n Editor
1. Open your workflow in n8n editor
2. Click on the **"When chat message received"** node (the Chat Trigger)
3. Look for the **Webhook URL** field in the node parameters
4. Copy this URL and paste it into your `.env` file as `N8N_WEBHOOK_URL`

### Modifying the Webhook Response Format

The Streamlit app expects the n8n workflow to return JSON with a `reply` field:

```json
{
  "reply": "The assistant's response text here"
}
```

#### If Your Current Workflow Doesn't Return This Format:

The **Chat Trigger** node in n8n automatically handles the response format when used with an **AI Agent** node. However, if you need to customize it:

1. **Add a "Set" node** after the AI Agent node:
   - Click the **+** button after AI Agent
   - Select **Data transformation > Set**
   - Configure it to set:
     - **Name**: `reply`
     - **Value**: `{{ $json.output }}` (or whatever field contains the agent's response)

2. **Alternative: Add a "Code" node** for more control:
   ```javascript
   return [{
     json: {
       reply: $input.first().json.output || "I cannot find this in the available resources."
     }
   }];
   ```

### Request Format from Streamlit App

The Streamlit app sends the following JSON payload to your webhook:

```json
{
  "user_id": "uuid-of-the-user",
  "session_id": "uuid-of-the-chat-session",
  "message": "User's question text",
  "profile_summary": "User often discusses: internships, backend, salaries..."
}
```

**Note**: `profile_summary` is optional and only included if the user has enough message history.

### Using the Extra Fields in n8n

Your current workflow only uses the `message` field (automatically extracted by the Chat Trigger). To use `user_id`, `session_id`, or `profile_summary`:

1. **Access them in the AI Agent's system message**:
   ```
   User ID: {{ $json.user_id }}
   Session: {{ $json.session_id }}
   User Context: {{ $json.profile_summary }}
   ```

2. **Use them for personalization** by modifying the system message in the AI Agent node to include:
   ```
   Additional context about the user: {{ $json.profile_summary || "No prior context available" }}
   ```

3. **Store them for analytics** by adding a database write node after the AI Agent

### Testing Your Webhook

You can test your webhook using the diagnostic tool:

```bash
python3 diagnose.py
```

Or test it directly using curl:

```bash
curl -X POST https://your-n8n-instance.com/webhook/5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-id",
    "session_id": "test-session-id",
    "message": "What companies are hiring backend developers?"
  }'
```

Expected response:
```json
{
  "reply": "Based on current data, several companies are hiring backend developers..."
}
```

### Common Issues and Solutions

#### Issue: Webhook returns 404
- **Solution**: Make sure the workflow is **activated** (toggle the Active switch in n8n)
- Check that the webhook ID matches exactly

#### Issue: Timeout errors
- **Solution**: Increase `REQUEST_TIMEOUT` in `.env` to 60 or higher
- The AI Agent may take time to search and retrieve information

#### Issue: "reply" field not found
- **Solution**: The app will fall back to checking `output` or `text` fields
- Alternatively, add a Set/Code node to format the response (see above)

#### Issue: Memory not working across sessions
- **Solution**: The current workflow uses Window Buffer Memory which resets per webhook call
- To persist memory, you'd need to implement session management in n8n (future enhancement)

## 📁 Project Structure

```
scaling-doodle/
├── app.py                  # Main Streamlit application
├── auth.py                 # Authentication with Supabase
├── database.py             # Database CRUD operations
├── n8n_client.py          # n8n webhook integration
├── summarizer.py          # Profile summary generation
├── requirements.txt        # Python dependencies
├── supabase_schema.sql    # Database schema
├── .env.example           # Environment variable template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🔐 Security Notes

- Never commit your `.env` file with actual credentials
- Use the `anon` public key from Supabase (not the service role key)
- Row Level Security (RLS) policies ensure users can only access their own data
- All database operations use authenticated Supabase client with JWT tokens

## 🎨 User Interface

### Dark Theme
- Background: `#121212` (near black)
- Accent: `#10a37f` (teal green)
- User messages: bordered with accent color
- Assistant messages: neutral gray border

### Main Sections
1. **Sidebar**: Session list, new chat button, user profile
2. **Chat Area**: Chronological message display
3. **Input Area**: Text input and send button

## 📊 Profile Summary Feature

The app automatically generates a profile summary after every N messages (default: 10).

**Current Implementation** (Simple frequency-based):
- Analyzes last 12 user messages
- Extracts top 5 meaningful words (4+ characters)
- Filters out common stop words
- Creates summary: "User often discusses: word1, word2, word3..."

**Future Enhancement** (Hook ready):
The `summarizer.py` includes a `generate_llm_summary()` function placeholder for future LLM-based summarization via a dedicated n8n webhook.

## 🔧 Customization

### Change Summary Threshold
Edit `PROFILE_SUMMARY_MESSAGE_THRESHOLD` in `.env` (default: 10 messages)

### Modify Dark Theme Colors
Edit the CSS in `app.py` under `DARK_THEME_CSS`

### Change Assistant Name
Replace "Sam" throughout `app.py` with your preferred name

### Adjust Request Timeout
Edit `REQUEST_TIMEOUT` in `.env` (default: 30 seconds)

## 🐛 Troubleshooting

### "Missing configuration" error
- Ensure all required environment variables are set in `.env`
- Verify `.env` file is in the same directory as `app.py`

### Authentication not working
- Confirm Google OAuth is properly configured in Supabase
- Check that redirect URLs are correctly set
- Try accessing Supabase auth directly via their UI

### Database errors
- Verify `supabase_schema.sql` was executed successfully
- Check RLS policies are enabled
- Ensure user has proper permissions

### n8n connection issues
- Test webhook URL with curl (see Testing section above)
- Verify n8n workflow is activated
- Check firewall/network settings if self-hosted

## 📈 Future Enhancements

Hooks are ready for these features:

1. **LLM-based summarization**: Replace `generate_simple_summary()` with `generate_llm_summary()`
2. **Session rename/delete**: UI buttons exist, backend functions ready
3. **Trait extraction**: `user_traits` table ready for n8n webhook integration
4. **Source citations**: n8n can return sources array, UI can be extended to display
5. **User preferences**: `preferences` JSONB column ready for custom settings
6. **Streaming responses**: Can be added with async Streamlit components

## 📝 License

This project is provided as-is for your use.

## 🤝 Contributing

This is a focused implementation designed to be minimal and maintainable. Extensions should follow the same principles of simplicity and clean separation of concerns.

---

**Need Help?** 

Check the troubleshooting section or review the inline code comments for detailed implementation notes.