# 🔑 How to Get Embedding API Keys

## Quick Setup Guide

### Option 1: OpenAI (Recommended - Most Reliable) ⭐

1. **Go to**: https://platform.openai.com/api-keys
2. **Sign up/Login** to your OpenAI account
3. **Click** "Create new secret key"
4. **Copy** the key (starts with `sk-`)
5. **Add to code**: Paste in `HARDCODED_OPENAI_API_KEY` in `approve-posting/index.ts`
   - Or add as secret in Supabase: `OPENAI_API_KEY`

**Pricing**: Pay-as-you-go, ~$0.02 per 1M tokens (very cheap for embeddings)
**Model**: `text-embedding-3-small` (supports custom dimensions)

---

### Option 2: Cohere (Free Tier Available) 🆓

1. **Go to**: https://dashboard.cohere.com/api-keys
2. **Sign up/Login** to Cohere
3. **Click** "Create API Key"
4. **Copy** the key
5. **Add to code**: Paste in `HARDCODED_COHERE_API_KEY` in `approve-posting/index.ts`
   - Or add as secret in Supabase: `COHERE_API_KEY`

**Pricing**: Free tier available, then pay-as-you-go
**Model**: `embed-english-v3.0` or `embed-english-light-v3.0`

---

### Option 3: HuggingFace (Free Tier) 🆓

1. **Go to**: https://huggingface.co/settings/tokens
2. **Sign up/Login** to HuggingFace
3. **Click** "New token"
4. **Select** "Read" access
5. **Copy** the token (starts with `hf_`)
6. **Add to code**: Paste in `HARDCODED_HUGGINGFACE_API_KEY` in `approve-posting/index.ts`
   - Or add as secret in Supabase: `HUGGINGFACE_API_KEY`

**Pricing**: Free for most use cases
**Model**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)

---

## 📝 How to Add Keys to Code (For Testing)

1. Open `supabase/functions/approve-posting/index.ts`
2. Find the section at the top that says `TEMPORARY: Hardcoded values`
3. Fill in the keys you want to use:

```typescript
const HARDCODED_OPENAI_API_KEY = 'sk-your-actual-key-here';
const HARDCODED_QDRANT_URL = 'https://your-qdrant-url.com';
const HARDCODED_QDRANT_API_KEY = 'your-qdrant-key';
```

4. **Save** the file
5. **Test** your function

⚠️ **IMPORTANT**: Remove hardcoded keys before pushing to GitHub! Use Supabase Secrets for production.

---

## 🔐 How to Add Keys to Supabase (For Production)

1. Go to **Supabase Dashboard**
2. Navigate to: **Project Settings** → **Edge Functions** → **Secrets**
3. Click **"Add new secret"**
4. Add each key:
   - Name: `OPENAI_API_KEY`, Value: `sk-...`
   - Name: `QDRANT_URL`, Value: `https://...`
   - Name: `QDRANT_API_KEY`, Value: `...`
5. Click **"Save"**

---

## 🎯 Recommended Setup

**For Quick Testing**: Use OpenAI (most reliable)
1. Get OpenAI key from https://platform.openai.com/api-keys
2. Add to `HARDCODED_OPENAI_API_KEY` in the code
3. Test immediately

**For Production**: Use Supabase Secrets
1. Add keys to Supabase Dashboard → Edge Functions → Secrets
2. Remove hardcoded values from code
3. Deploy

---

## ❓ Which One Should I Use?

- **OpenAI**: Best for reliability and dimension control (recommended)
- **Cohere**: Good free tier, easy setup
- **HuggingFace**: Completely free, but may be slower

You only need **ONE** of these - the code will try them in order!

