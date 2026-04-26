# Feedback Form Setup with Formspree

The Munger Screener now includes a feedback form in the sidebar. It uses Formspree to handle email delivery.

## Setup (5 minutes)

1. **Go to https://formspree.io and sign up** (free)

2. **Create a new form:**
   - Click "New Form"
   - Set email to: `robinsongm321@gmail.com`
   - Click "Create"

3. **Copy your form endpoint:**
   - Formspree will show you an endpoint like: `https://formspree.io/f/xyzabc123`
   - Copy this URL

4. **Update `.streamlit/secrets.toml`:**
   ```toml
   FORMSPREE_ENDPOINT = "https://formspree.io/f/YOUR_FORM_ID"
   ```
   Replace `YOUR_FORM_ID` with your actual form ID from Formspree

5. **Test locally:**
   - Run `streamlit run streamlit_app.py`
   - Go to the sidebar and fill in the feedback form
   - Click "Send Feedback"
   - Check your email to confirm it works

## Streamlit Cloud Deployment

1. **Go to your Streamlit Cloud app dashboard**
2. **Click the three dots** → **Settings**
3. **Go to the Secrets tab**
4. **Add the same secret:**
   ```toml
   FORMSPREE_ENDPOINT = "https://formspree.io/f/YOUR_FORM_ID"
   ```
5. **Save** — your app will automatically redeploy

## Why Formspree?

- ✅ No backend required
- ✅ No credentials to manage
- ✅ Free tier covers 50 submissions/month
- ✅ Emails go directly to your inbox
- ✅ No setup complexity
