# Deployment Guide

Step-by-step guide to deploy the Gmail Outreach Automation System to production.

## Overview

| Service | Platform | Purpose |
|---------|----------|--------|
| Backend | Render | FastAPI server + worker |
| Frontend | Vercel | Next.js dashboard |
| Database | Supabase | PostgreSQL storage |

## Step 1: Supabase Setup

### 1.1 Create Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Choose your organization
4. Set project name (e.g., `gmail-outreach`)
5. Select region closest to you
6. Set a strong database password
7. Copy the password (you'll need it)
8. Wait for project to provision (~2 minutes)

### 1.2 Get Credentials

From project Settings > API:
- **Project URL**: `https://xxxxx.supabase.co`
- **anon/public key**: `eyJhbGc...` (public key)
- **service_role key**: `eyJhbGc...` (keep secret!)

### 1.3 Run Database Schema

1. Go to **SQL Editor** in Supabase dashboard
2. Copy and paste the contents of `backend/database/schema.sql`
3. Click **Run**
4. Verify tables created in **Table Editor**

## Step 2: Google Cloud Setup

### 2.1 Create Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click "Select a project" > "New Project"
3. Name it `gmail-outreach`
4. Enable billing (required)
5. Wait for project creation

### 2.2 Enable APIs

1. Go to **APIs & Services** > **Library**
2. Enable these APIs:
   - Gmail API
   - Google Sheets API

### 2.3 Create OAuth2 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click "Create Credentials" > **OAuth client ID**
3. Application type: **Web application**
4. Name: `Gmail Outreach`
5. Add authorized redirect URI:
   ```
   http://localhost:8000/auth/callback
   ```
6. Click **Create**
7. Copy your **Client ID** and **Client Secret**

### 2.4 Get Gmail OAuth Tokens

For each Gmail account you want to use:

1. Open: `https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code&scope=https://www.googleapis.com/auth/gmail.send`

2. Sign in with the Gmail account

3. Grant permissions

4. Get the **authorization code** from the redirect URL

5. Exchange for tokens:

```bash
curl -X POST https://oauth2.googleapis.com/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&code=AUTH_CODE&redirect_uri=YOUR_REDIRECT_URI&grant_type=authorization_code"
```

6. Save the `access_token` and `refresh_token`

## Step 3: OpenAI Setup

### 3.1 Get API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Go to **API Keys**
3. Click "Create new secret key"
4. Name it `gmail-outreach`
5. Copy the key (starts with `sk-`)
6. Set up billing if not already (pay-as-you-go)

## Step 4: Backend Deployment (Render)

### 4.1 Connect Repository

1. Go to [render.com](https://render.com)
2. Sign up / Log in
3. Click "New +" > **Blueprint** (or Web Service)
4. Connect your GitHub repository
5. Select `Gmail-Outreach`

### 4.2 Configure Service

For **Web Service**:
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Plan**: Free tier works for testing

### 4.3 Add Environment Variables

In Render dashboard, add these environment variables:

| Variable | Value |
|----------|-------|
| `SUPABASE_URL` | From Supabase |
| `SUPABASE_KEY` | Service role key from Supabase |
| `OPENAI_API_KEY` | `sk-...` from OpenAI |
| `GOOGLE_CLIENT_ID` | From Google Cloud |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud |
| `GOOGLE_REDIRECT_URI` | `http://localhost:8000/auth/callback` |
| `EST_TIMEZONE` | `America/New_York` |
| `SEND_WINDOW_START` | `9` |
| `SEND_WINDOW_END` | `17` |
| `SKIP_WEEKENDS` | `true` |
| `MAX_EMAILS_PER_DAY` | `12` |
| `MAX_EMAILS_PER_HOUR` | `3` |

### 4.4 Deploy

1. Click "Create Web Service"
2. Wait for build (~3 minutes)
3. Note your deployed URL: `https://xxx.onrender.com`

## Step 5: Frontend Deployment (Vercel)

### 5.1 Connect Repository

1. Go to [vercel.com](https://vercel.com)
2. Sign up / Log in
3. Click "Add New..." > **Project**
4. Import `Gmail-Outreach` from GitHub
5. Framework: **Next.js** (auto-detected)

### 5.2 Configure Project

- **Root Directory**: `frontend`
- **Build Command**: `npm run build` (auto-filled)
- **Output Directory**: `/.next` (auto-filled)

### 5.3 Add Environment Variable

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_BASE_URL` | Your Render backend URL (e.g., `https://xxx.onrender.com`) |

### 5.4 Deploy

1. Click "Deploy"
2. Wait for deployment (~2 minutes)
3. Your dashboard URL: `https://gmail-outreach.vercel.app`

## Step 6: Configure Leads (Google Sheets)

### 6.1 Create Spreadsheet

1. Create a new Google Sheet
2. Name it "Outreach Leads"

### 6.2 Set Up Columns

In row 1:
```
A: No | B: name | C: email | D: github_url | E: status | F: last_contacted_at | G: followup_stage
```

### 6.3 Share Spreadsheet

1. Click "Share"
2. Add your service account email
3. Give "Viewer" access
4. Copy the Spreadsheet ID from URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```

### 6.4 Add Leads

Add leads in rows starting from row 2:
- Column A: Number (1, 2, 3...)
- Column B: Lead name
- Column C: Lead email
- Column D: GitHub URL (optional)
- Column E: `pending`
- Column F: (empty)
- Column G: `none`

## Step 7: Add Gmail Accounts

### 7.1 Via API

```bash
curl -X POST https://xxx.onrender.com/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@gmail.com",
    "access_token": "ya29...",
    "refresh_token": "1//..."
  }'
```

### 7.2 Via Dashboard

1. Go to your Vercel dashboard URL
2. Click "Accounts"
3. Click "Add Account"
4. Enter email and OAuth tokens

## Step 8: Start Campaign

### 8.1 Configure Spreadsheet

1. Go to dashboard
2. Go to Settings or Leads page
3. Enter your Google Sheets Spreadsheet ID
4. Click "Sync"

### 8.2 Start Campaign

```bash
curl -X POST https://xxx.onrender.com/campaign/start \
  -H "Content-Type: application/json" \
  -d '{"spreadsheet_id": "YOUR_SPREADSHEET_ID"}'
```

Or via dashboard:
1. Go to Overview page
2. Enter Spreadsheet ID
3. Click "Start Campaign"

## Verification

### Check Status

```bash
curl https://xxx.onrender.com/campaign/status
```

### View Logs

```bash
curl https://xxx.onrender.com/logs/recent?hours=24
```

### Check Dashboard

1. Visit `https://your-frontend.vercel.app`
2. See campaign status
3. See email logs
4. See account stats

## Troubleshooting

### Backend Won't Start

1. Check Render logs
2. Verify environment variables
3. Check Supabase connection

### Emails Not Sending

1. Verify EST time (9AM-5PM)
2. Check account limits haven't exceeded
3. Verify Gmail tokens valid
4. Check email logs for errors

### Google Sheets Sync Failed

1. Verify spreadsheet ID correct
2. Check column names match exactly
3. Verify sharing permissions

### OpenAI Errors

1. Verify API key valid
2. Check billing set up
3. Check rate limits

## Production Checklist

- [ ] All environment variables set
- [ ] Database schema applied
- [ ] At least one Gmail account added
- [ ] Google Sheets configured
- [ ] Campaign starts successfully
- [ ] Dashboard accessible
- [ ] Email sends successfully
- [ ] Logs showing activity

## Scaling Tips

1. **Multiple accounts**: Add more Gmail accounts for higher volume
2. **Different time zones**: All accounts share same EST window
3. **Weekly reset**: Daily counts reset at midnight EST automatically
4. **Pause anytime**: Use dashboard to pause immediately

## Security Reminders

- Never commit `.env` files
- Use Render environment variables
- Keep Supabase service role key secret
- Rotate Gmail refresh tokens periodically