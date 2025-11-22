# n8n Webhook Integration Guide

## Understanding the Chat Trigger Webhook

Your n8n workflow uses a **Chat Trigger** node with webhook ID: `5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd`

### What Happens When You Send a Message

```
┌─────────────────────────────────────────────────────────────┐
│                      USER SENDS MESSAGE                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              STREAMLIT APP (app.py)                          │
│  1. Stores user message in Supabase                          │
│  2. Fetches profile summary (if available)                   │
│  3. Prepares JSON payload                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ POST REQUEST
                         │ 
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         n8n WEBHOOK (Chat Trigger Node)                      │
│  URL: https://your-n8n.com/webhook/5f1c0c82-...             │
│                                                              │
│  Receives:                                                   │
│  {                                                           │
│    "user_id": "uuid-123",                                    │
│    "session_id": "uuid-456",                                 │
│    "message": "What companies are hiring?",                  │
│    "profile_summary": "User often discusses: ..."            │
│  }                                                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI AGENT NODE                              │
│  System Message: "You are Sam, a Career Assistant..."        │
│                                                              │
│  Available Tools:                                            │
│  ├─ Vector Store (Pinecone + Gemini embeddings)             │
│  │  └─ For: Company FAQs, Interview guides, Tech stacks     │
│  │                                                           │
│  ├─ Web Search (SearchApi)                                  │
│  │  └─ For: Current jobs, Recent news, Live data            │
│  │                                                           │
│  └─ Window Buffer Memory                                    │
│     └─ Maintains conversation context                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ AI processes and generates response
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  RESPONSE GENERATED                          │
│  {                                                           │
│    "reply": "Several companies are hiring backend..."       │
│  }                                                           │
│                                                              │
│  OR alternative formats supported:                           │
│  {"output": "..."} or {"text": "..."}                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ RESPONSE SENT BACK
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              STREAMLIT APP (app.py)                          │
│  1. Receives response from n8n                               │
│  2. Extracts reply text                                      │
│  3. Stores assistant message in Supabase                     │
│  4. Updates profile summary (if threshold reached)           │
│  5. Refreshes UI to show new messages                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  USER SEES RESPONSE                          │
└─────────────────────────────────────────────────────────────┘
```

## How to Change the Webhook

### Option 1: Keep Current Webhook ID

Your existing webhook ID `5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd` is already configured in the workflow. Just need the full URL:

**Format:**
```
https://[YOUR-N8N-DOMAIN]/webhook/5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd
```

**Examples:**
- Self-hosted: `https://n8n.mycompany.com/webhook/5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd`
- n8n Cloud: `https://myorg.app.n8n.cloud/webhook/5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd`

**Update .env:**
```bash
N8N_WEBHOOK_URL=https://your-n8n-domain/webhook/5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd
```

### Option 2: Get URL from n8n Editor

1. Open workflow in n8n
2. Click "When chat message received" node
3. Look for "Webhook URLs" section
4. Copy the Production URL (not Test URL)
5. Paste into `.env` as `N8N_WEBHOOK_URL`

### Option 3: Create New Webhook

If you want to create a fresh webhook:

1. **In n8n workflow:**
   - Delete existing "When chat message received" node
   - Add new "Chat Trigger" node
   - Connect it to AI Agent node
   - Save workflow
   - Note the new webhook ID

2. **In your .env:**
   - Update `N8N_WEBHOOK_URL` with new webhook URL

## Verifying the Webhook

### Method 1: Use Diagnostic Tool
```bash
python3 diagnose.py
```

This will test:
- ✓ Can connect to webhook
- ✓ Webhook responds with valid format
- ✓ Response contains expected fields

### Method 2: Manual Test with curl
```bash
curl -X POST "https://your-n8n.com/webhook/5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "session_id": "test-session",
    "message": "Hello, are you working?"
  }'
```

**Expected response:**
```json
{
  "reply": "Hello! Yes, I'm working. How can I help you with company insights or career guidance?"
}
```

## Customizing the Response Format

### Current Flow (Default)

Chat Trigger → AI Agent → (automatic response)

The AI Agent automatically returns the response in the correct format.

### If You Need Custom Format

Add a **Function** or **Set** node between AI Agent and the output:

```
Chat Trigger → AI Agent → Function Node → Output
```

**Function Node Example:**
```javascript
// Customize the response format
const agentOutput = $input.first().json.output;

return {
  json: {
    reply: agentOutput,
    sources: [], // Add if you track sources
    timestamp: new Date().toISOString()
  }
};
```

The Streamlit app will extract the `reply` field automatically.

## Using Profile Summary in n8n

The Streamlit app sends `profile_summary` in the request. To use it:

### Method 1: In System Message

Edit the AI Agent's system message:

```
You are Sam, a Company Insights & Career Guidance Assistant.

User Context: {{ $json.profile_summary || "No prior context available" }}

[Rest of your system message...]
```

### Method 2: In a Function Node (Before AI Agent)

```javascript
// Enhance the message with profile context
const message = $json.message;
const profile = $json.profile_summary || "";

let enhancedMessage = message;
if (profile) {
  enhancedMessage = `User Background: ${profile}\n\nQuestion: ${message}`;
}

return {
  json: {
    message: enhancedMessage,
    user_id: $json.user_id,
    session_id: $json.session_id
  }
};
```

## Common Webhook Issues

### Issue: "Connection refused"
**Cause:** n8n is not running or URL is wrong
**Fix:** 
1. Check n8n is accessible
2. Verify URL format
3. Test with curl

### Issue: "404 Not Found"
**Cause:** Webhook ID doesn't exist or workflow not activated
**Fix:**
1. Activate workflow (toggle switch)
2. Verify webhook ID matches
3. Check webhook wasn't deleted

### Issue: "Timeout"
**Cause:** AI Agent taking too long (>30s default)
**Fix:**
1. Increase timeout in `.env`: `REQUEST_TIMEOUT=60`
2. Optimize n8n workflow
3. Check if vector DB is slow

### Issue: "Invalid response format"
**Cause:** Response missing `reply`, `output`, or `text` field
**Fix:**
1. Add Function/Set node to format response
2. Check AI Agent is connected properly
3. Verify no error in workflow execution

## Security Considerations

### ✅ Do:
- Use HTTPS for webhook URL
- Keep webhook URL private (in .env)
- Enable n8n authentication if public
- Use rate limiting if needed

### ❌ Don't:
- Expose webhook URL in frontend code
- Commit webhook URL to git
- Use HTTP in production
- Share webhook URL publicly

## Testing Checklist

Before going live, verify:

- [ ] Workflow is activated in n8n
- [ ] Webhook URL is correct in .env
- [ ] Diagnostic tool passes webhook test
- [ ] Can send test message via curl
- [ ] Response format is correct
- [ ] Timeout is appropriate for your use case
- [ ] Profile summary is used (if desired)
- [ ] Error responses are handled gracefully

## Need Help?

1. Run diagnostic: `python3 diagnose.py`
2. Check n8n execution logs
3. Test with curl command above
4. Review error messages in Streamlit console
5. Verify all n8n credentials are configured

---

**Remember:** The webhook is the bridge between Streamlit and n8n. Once configured correctly, it enables seamless communication between your chat UI and the AI agent! 🎉
