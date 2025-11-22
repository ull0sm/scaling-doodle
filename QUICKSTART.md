# Quick Start Guide 🚀

Get your Company Insight Chat UI running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Supabase account created (free tier works!)
- [ ] n8n instance accessible (cloud or self-hosted)
- [ ] Google OAuth credentials (from Google Cloud Console)

## Step-by-Step Setup

### 1️⃣ Install Dependencies (1 minute)

```bash
# Clone the repository
git clone <your-repo-url>
cd scaling-doodle

# Install Python dependencies
pip install -r requirements.txt
```

### 2️⃣ Set Up Supabase Database (2 minutes)

1. **Create a Supabase project** at [supabase.com](https://supabase.com)
2. **Run the database schema**:
   - Go to SQL Editor in your Supabase dashboard
   - Copy all contents from `supabase_schema.sql`
   - Paste and click "Run"
   - ✅ You should see "Success. No rows returned"

3. **Get your credentials**:
   - Go to Project Settings > API
   - Copy your `URL` (looks like: `https://xxxxx.supabase.co`)
   - Copy your `anon` `public` key (starts with `eyJ...`)

### 3️⃣ Configure Google OAuth (2 minutes)

1. **In Supabase Dashboard**:
   - Go to Authentication > Providers
   - Enable "Google"
   - Note the callback URL shown (you'll need this next)

2. **In Google Cloud Console** ([console.cloud.google.com](https://console.cloud.google.com)):
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Web application"
   - Add Authorized redirect URIs:
     - Your Supabase callback: `https://YOUR-PROJECT.supabase.co/auth/v1/callback`
     - Your local dev: `http://localhost:8501`
   - Copy Client ID and Client Secret

3. **Back in Supabase**:
   - Paste Google Client ID and Secret
   - Save

### 4️⃣ Configure n8n Webhook (30 seconds)

Your n8n workflow has webhook ID: `5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd`

**Find your full webhook URL:**

Option A - If you know your n8n instance URL:
```
https://YOUR-N8N-INSTANCE.com/webhook/5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd
```

Option B - From n8n editor:
1. Open your workflow in n8n
2. Click the "When chat message received" node
3. Copy the Webhook URL shown

**Important**: Make sure your workflow is **activated** (toggle the switch at the top)!

### 5️⃣ Create .env File (30 seconds)

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
nano .env  # or use your favorite editor
```

**Your .env should look like:**
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd
PROFILE_SUMMARY_MESSAGE_THRESHOLD=10
REQUEST_TIMEOUT=30
```

### 6️⃣ Launch the App! (10 seconds)

```bash
streamlit run app.py
```

Your browser should open automatically to `http://localhost:8501`

## First Time Using the App

1. **Sign in with Google** 
   - Click the "Sign in with Google" button
   - Choose your Google account
   - Grant permissions

2. **Create your first chat**
   - Click "➕ New Chat" in the sidebar
   - Type a message like "What companies are hiring?"
   - Click Send or press Enter

3. **Chat with Sam!** 🎉
   - Sam uses your n8n workflow to answer questions
   - Sam can search the web AND your company database
   - Each conversation is automatically saved

## Testing Your Setup

### Test 1: Database Connection
```bash
# Check if Supabase is accessible
curl https://your-project.supabase.co/rest/v1/ \
  -H "apikey: your-anon-key"

# Should return schema information (not an error)
```

### Test 2: n8n Webhook
```bash
# Test your webhook directly
curl -X POST https://your-n8n.com/webhook/5f1c0c82-0ff9-40c7-9e2e-b1a96ffe24cd \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, are you working?"}'

# Should return JSON with a reply field
```

### Test 3: OAuth Flow
1. Go to `http://localhost:8501`
2. Click "Sign in with Google"
3. You should be redirected to Google login
4. After login, you should come back to the app (authenticated)

## Common Issues & Quick Fixes

### ❌ "Missing configuration" error
**Fix**: Check your `.env` file exists and has all required variables

### ❌ "Failed to create user record"
**Fix**: Make sure you ran `supabase_schema.sql` in the SQL Editor

### ❌ OAuth redirect fails
**Fix**: 
1. Verify callback URL in Google Console matches Supabase
2. Add `http://localhost:8501` to authorized redirect URIs

### ❌ n8n timeout
**Fix**: 
1. Check workflow is **activated** in n8n (toggle at top)
2. Increase `REQUEST_TIMEOUT=60` in `.env`

### ❌ "I cannot find this in the available resources"
**Fix**: This is the default fallback. Check:
1. n8n workflow is running
2. Webhook URL is correct
3. Test webhook with curl (see Test 2 above)

## What's Next?

### Customize Your Experience

**Change the message threshold for profile summaries:**
```env
PROFILE_SUMMARY_MESSAGE_THRESHOLD=5  # Update every 5 messages instead of 10
```

**Increase timeout for complex queries:**
```env
REQUEST_TIMEOUT=60  # Wait up to 60 seconds
```

**Modify the dark theme:**
Edit `DARK_THEME_CSS` in `app.py` to change colors

### Add More Features

See `ARCHITECTURE.md` for extension points:
- LLM-based profile summarization
- Session rename/delete in UI
- Trait extraction
- Source citations
- User preferences

## Need More Help?

📖 **Detailed docs**: See `README.md` for complete documentation
🏗️ **Architecture**: See `ARCHITECTURE.md` for system design
🔧 **Troubleshooting**: Check README.md troubleshooting section

## Success Indicators ✅

You're all set when:
- [ ] App loads at `http://localhost:8501`
- [ ] You can sign in with Google
- [ ] Sidebar shows "New Chat" option
- [ ] You can send a message
- [ ] Sam responds with relevant information
- [ ] Your conversation is saved (refresh page, messages persist)

**Congratulations! You're now chatting with Sam! 🎉**
