# 🆓 Free API Key Setup Guide

## Option 1: HuggingFace (100% FREE) ⭐ Recommended for Testing

### Steps:
1. Go to: https://huggingface.co/join
2. Sign up (it's free!)
3. Go to: https://huggingface.co/settings/tokens
4. Click "New token"
5. Name it: "talent-scout-embeddings"
6. Select "Read" access
7. Click "Generate token"
8. **Copy the token** (starts with `hf_`)

### Add to Code:
In `supabase/functions/approve-posting/index.ts`, line 20:
```typescript
const HARDCODED_HUGGINGFACE_API_KEY = 'hf_your-token-here';
```

**Cost**: FREE forever! 🎉

---

## Option 2: Cohere (Free Tier)

### Steps:
1. Go to: https://dashboard.cohere.com/signup
2. Sign up (free tier available)
3. Go to: https://dashboard.cohere.com/api-keys
4. Click "Create API Key"
5. **Copy the key**

### Add to Code:
In `supabase/functions/approve-posting/index.ts`, line 19:
```typescript
const HARDCODED_COHERE_API_KEY = 'your-cohere-key-here';
```

**Cost**: Free tier includes 100 requests/minute, then pay-as-you-go

---

## Option 3: OpenAI (Very Cheap, Not Free)

### Cost Breakdown:
- **Embeddings**: $0.02 per 1 million tokens
- **Example**: 1,000 job postings ≈ $0.20 (20 cents!)
- **Very affordable** for production use

### If you want to use OpenAI:
1. Go to: https://platform.openai.com/api-keys
2. Sign up (requires credit card, but you get $5 free credit)
3. Create API key
4. Add to code: `HARDCODED_OPENAI_API_KEY`

**Note**: You get $5 free credit when you sign up, which is enough for thousands of embeddings!

---

## 🎯 My Recommendation:

**For Testing**: Use **HuggingFace** (completely free, no credit card needed)
**For Production**: Use **OpenAI** (very cheap, most reliable)

---

## Quick Setup (HuggingFace - Free):

1. Sign up: https://huggingface.co/join
2. Get token: https://huggingface.co/settings/tokens
3. Copy token (starts with `hf_`)
4. Paste in code at line 20:
   ```typescript
   const HARDCODED_HUGGINGFACE_API_KEY = 'hf_paste-your-token-here';
   ```
5. Save and test!

That's it! No credit card needed! 🎉

