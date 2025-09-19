# Google Gemini AI Integration Setup

## 🎯 Overview
Your Financial Reporting Tool now supports Google Gemini AI for free AI-powered summaries and analysis!

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install google-generativeai
```

### 2. Get Your Free Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" 
4. Create a new API key
5. Copy the API key

### 3. Add API Key to Environment
Add your Gemini API key to the `.env` file:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Test the Integration
```bash
python test_gemini.py
```

## 💡 Usage

### Using Gemini (Free)
```python
from src.ai_summary.ai_summarizer import AISummarizer

# Initialize with Gemini
ai_summarizer = AISummarizer(provider='gemini')

# Generate executive summary
result = ai_summarizer.generate_executive_summary(
    pnl_data, expense_data, vendor_data, "2024-01"
)
```

### Using OpenAI (Paid - Fallback)
```python
# Initialize with OpenAI
ai_summarizer = AISummarizer(provider='openai')
```

## 📊 Free Tier Limits
- **Requests per day**: 250
- **Requests per minute**: 10
- **Tokens per minute**: 250,000

## 🔧 Configuration Options

### Available Models
- `gemini-1.5-flash` (default) - Fast and efficient
- `gemini-1.5-pro` - More capable but slower

### Custom Configuration
```python
ai_summarizer = AISummarizer(
    provider='gemini',
    model='gemini-1.5-pro',
    api_key='your_custom_key'
)
```

## 🧪 Testing

Run the test script to verify everything works:
```bash
python test_gemini.py
```

Expected output:
```
🧪 Testing Gemini AI Integration
========================================
✅ Gemini API key found
🔧 Initializing Gemini AI summarizer...
✅ Gemini AI summarizer initialized successfully
📊 Creating test financial data...
✅ Test data created
🤖 Testing executive summary generation...
✅ Executive summary generated successfully!
```

## 🚨 Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not found"**
   - Make sure you added the key to `.env` file
   - Check the key is correct (no extra spaces)

2. **"google-generativeai package not installed"**
   - Run: `pip install google-generativeai`

3. **"API key invalid"**
   - Verify your API key is correct
   - Check if you have access to Gemini API

4. **Rate limit exceeded**
   - Wait a few minutes before trying again
   - Consider upgrading to paid tier for higher limits

## 📈 Benefits

- ✅ **Free AI summaries** for your financial reports
- ✅ **No subscription required** - just a Google account
- ✅ **Same interface** as your existing code
- ✅ **Fallback to OpenAI** if needed
- ✅ **Professional quality** financial analysis

## 🔄 Migration from OpenAI

If you were using OpenAI before, simply change:
```python
# Old way
ai_summarizer = AISummarizer()

# New way (with Gemini)
ai_summarizer = AISummarizer(provider='gemini')
```

That's it! Your existing pipeline will now use Gemini for AI summaries.
