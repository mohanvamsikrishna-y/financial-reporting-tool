# Deployment Guide

## 🚀 Quick Deployment Options

### Option 1: Streamlit Cloud (Recommended - Free)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/financial-reporting-tool.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Add secrets in the secrets section:
     ```
     GEMINI_API_KEY = "your_gemini_api_key_here"
     ```
   - Click "Deploy"

3. **Your app will be live at**: `https://your-app-name.streamlit.app`

### Option 2: Heroku (Professional)

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login and create app**
   ```bash
   heroku login
   heroku create your-financial-app-name
   ```

3. **Add PostgreSQL database**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

4. **Set environment variables**
   ```bash
   heroku config:set GEMINI_API_KEY=your_gemini_api_key_here
   heroku config:set ENVIRONMENT=production
   ```

5. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

6. **Your app will be live at**: `https://your-financial-app-name.herokuapp.com`

## 🔧 Environment Variables

### Required
- `GEMINI_API_KEY`: Your Google Gemini API key

### Optional
- `DATABASE_URL`: Database connection string (auto-generated on Heroku)
- `ENVIRONMENT`: production/development
- `LOG_LEVEL`: INFO/DEBUG/WARNING

## 📱 Features Available After Deployment

- ✅ **Interactive Dashboard** - Real-time financial data visualization
- ✅ **AI Chat Assistant** - Ask questions about your financial data
- ✅ **Report Generation** - Automated P&L, expense, and vendor reports
- ✅ **Data Upload** - CSV/Excel file processing
- ✅ **Real-time Analysis** - AI-powered insights using Gemini

## 🎯 Resume-Ready Features

### Technical Stack
- **Frontend**: Streamlit, Plotly
- **Backend**: Python, SQLAlchemy
- **AI/ML**: Google Gemini API
- **Database**: PostgreSQL, SQLite
- **Deployment**: Heroku, Streamlit Cloud
- **CI/CD**: GitHub Actions

### Key Capabilities
- Multi-source data integration
- Real-time AI-powered analysis
- Interactive web dashboard
- Automated report generation
- Cloud deployment ready

## 🐛 Troubleshooting

### Common Issues

1. **App won't start**
   - Check environment variables are set
   - Verify GEMINI_API_KEY is correct
   - Check logs: `heroku logs --tail`

2. **Database errors**
   - Ensure DATABASE_URL is set
   - Check database connection

3. **AI not working**
   - Verify GEMINI_API_KEY is valid
   - Check API quota limits

## 📊 Monitoring

### Heroku
- View logs: `heroku logs --tail`
- Monitor metrics: Heroku dashboard
- Scale dynos: `heroku ps:scale web=1`

### Streamlit Cloud
- View logs in the Streamlit Cloud dashboard
- Monitor usage and performance

## 🔒 Security

- Environment variables are encrypted
- Database credentials are auto-generated
- HTTPS enabled by default
- No sensitive data in code

## 📈 Scaling

### Heroku
- Upgrade dyno type for more resources
- Add more dynos: `heroku ps:scale web=2`
- Use Heroku Postgres for production

### Streamlit Cloud
- Free tier: 1 app, 1GB RAM
- Pro tier: Multiple apps, more resources

## 🎉 Success!

Your financial reporting platform is now live and ready for your resume!

**Live Demo**: Include the URL in your resume
**GitHub**: Show the code repository
**Features**: Highlight AI integration, real-time analysis, cloud deployment
