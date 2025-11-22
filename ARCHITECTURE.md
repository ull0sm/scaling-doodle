# Architecture & Data Flow

## System Overview

```
┌─────────────────┐
│  Streamlit UI   │ (Dark Theme)
│   (app.py)      │
└────────┬────────┘
         │
         ├──────────────┐
         │              │
         ▼              ▼
┌─────────────┐  ┌──────────────┐
│  Supabase   │  │   n8n API    │
│  (Auth/DB)  │  │  (Webhook)   │
└─────────────┘  └──────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │  AI Agent     │
                │  (LangChain)  │
                └───────┬───────┘
                        │
           ┌────────────┼────────────┐
           │            │            │
           ▼            ▼            ▼
    ┌──────────┐  ┌─────────┐  ┌────────┐
    │ Pinecone │  │ Gemini  │  │ Search │
    │   RAG    │  │   LLM   │  │  API   │
    └──────────┘  └─────────┘  └────────┘
```

## User Flow

1. **Authentication** (Unauthenticated users)
   ```
   User → Google Sign-in → Supabase OAuth → User Record Created
   ```

2. **Session Management**
   ```
   User → Create/Select Session → Load Messages from DB
   ```

3. **Message Flow** (Main interaction)
   ```
   User Types Message
       ↓
   Store in Supabase (messages table)
       ↓
   Fetch Profile Summary (if exists)
       ↓
   POST to n8n Webhook
       {
         user_id: "uuid",
         session_id: "uuid", 
         message: "text",
         profile_summary: "optional"
       }
       ↓
   n8n AI Agent Processes
       - Checks Vector DB (Pinecone)
       - Uses Web Search (SearchApi) 
       - Generates response with Gemini
       ↓
   Receive Response
       {
         reply: "assistant's answer"
       }
       ↓
   Store Assistant Reply in Supabase
       ↓
   Check if Summary Update Needed
       (every N messages)
       ↓
   Update Profile Summary (if threshold met)
       ↓
   Refresh UI with new messages
   ```

## Database Schema

### Tables

**users**
- id (PK)
- email (unique)
- name
- avatar_url
- profile_summary
- preferences (JSONB)
- timestamps

**sessions**
- id (PK)
- user_id (FK → users)
- title
- timestamps

**messages**
- id (PK)
- session_id (FK → sessions)
- role (user|assistant|system)
- content
- created_at

**user_traits** (Future use)
- id (PK)
- user_id (FK → users)
- key
- value
- confidence
- updated_at

### Row Level Security

All tables have RLS policies ensuring:
- Users can only access their own data
- Policies check `auth.jwt() ->> 'email'` against user records
- Cascading deletes maintain referential integrity

## Module Breakdown

### auth.py
- Supabase client initialization
- Google OAuth integration
- User session management
- User record creation

### database.py
- CRUD operations for all tables
- Session management functions
- Message storage and retrieval
- Profile summary updates

### n8n_client.py
- Webhook POST requests
- Error handling (timeouts, connection errors)
- Response parsing and validation
- Fallback replies

### summarizer.py
- Frequency-based word extraction
- Message threshold checking
- Recent message filtering
- Future LLM summarization hook

### app.py
- Streamlit UI components
- Dark theme CSS
- Session state management
- Message rendering
- Sidebar with session list
- Chat input and send logic

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| SUPABASE_URL | Your Supabase project URL | https://xyz.supabase.co |
| SUPABASE_KEY | Anon public key | eyJhbG... |
| N8N_WEBHOOK_URL | Full webhook URL | https://n8n.com/webhook/abc123 |
| PROFILE_SUMMARY_MESSAGE_THRESHOLD | Messages before summary update | 10 |
| REQUEST_TIMEOUT | Webhook timeout (seconds) | 30 |

## Security Considerations

1. **Never commit .env** - Contains sensitive credentials
2. **Use anon key only** - Never expose service role key in frontend
3. **RLS is mandatory** - All database tables have RLS enabled
4. **JWT-based auth** - Supabase handles authentication tokens
5. **HTTPS required** - All API calls should use secure connections

## Extension Points

### Profile Summarization
Current: Simple frequency-based
```python
# summarizer.py
def generate_simple_summary(messages):
    # Word frequency analysis
    return "User often discusses: word1, word2..."
```

Future: LLM-based via n8n
```python
# summarizer.py  
def generate_llm_summary(webhook_url, messages):
    # Call dedicated n8n summarization workflow
    response = requests.post(webhook_url, json={"messages": messages})
    return response.json()["summary"]
```

### Trait Extraction
Table ready: `user_traits`

Future workflow:
1. n8n analyzes conversation
2. Extracts traits (interests, skills, goals)
3. POSTs back to Streamlit endpoint
4. Stored in user_traits table

### Source Citations
Current: Not implemented
Future: n8n returns sources array
```json
{
  "reply": "...",
  "sources": [
    {"title": "Company X", "url": "...", "type": "rag"},
    {"title": "News Article", "url": "...", "type": "web"}
  ]
}
```

### Session Features
Ready but not exposed in UI:
- Rename session: `update_session_title()`
- Delete session: `delete_session()`

Can add UI buttons in sidebar for these operations.

## Performance Considerations

1. **Database Queries**
   - Indexed on user_id, session_id, created_at
   - Queries are scoped to current user only
   - Messages fetched once per session load

2. **API Calls**
   - Single round-trip per user message
   - Configurable timeout
   - Error handling prevents UI blocking

3. **Profile Summary**
   - Updated only every N messages (configurable)
   - Processes last 12 messages only
   - Lightweight frequency analysis

4. **Streamlit State**
   - Session state for current session
   - Minimal data in memory
   - Rerun only when necessary

## Troubleshooting Common Issues

### "Missing configuration"
→ Check `.env` file exists and contains all required variables

### Authentication fails
→ Verify Google OAuth is configured in Supabase dashboard
→ Check redirect URLs are properly set

### n8n timeout
→ Increase `REQUEST_TIMEOUT` in `.env`
→ Check n8n workflow is activated

### Database errors
→ Verify `supabase_schema.sql` was executed
→ Check RLS policies are active
→ Ensure JWT token is valid

### Messages not loading
→ Check session_id is set in state
→ Verify user has permission to access session
→ Check messages table has data

## Development Tips

1. **Testing without real credentials**
   - Mock Supabase client for unit tests
   - Use requests-mock for n8n webhook tests
   - Test summarizer independently (no external deps)

2. **Local development**
   - Use Supabase local development environment
   - Set up n8n locally with docker
   - Use ngrok for webhook testing

3. **Debugging**
   - Check Streamlit console for print statements
   - Monitor Supabase logs for query errors
   - Test n8n webhook with curl directly

4. **Code modifications**
   - Keep modules independent
   - Update README when adding features
   - Test error paths explicitly
