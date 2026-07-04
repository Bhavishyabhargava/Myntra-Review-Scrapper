# Myntra Review Scrapper - Deployment Guide

This guide provides step-by-step instructions for deploying the Streamlit app.

## Prerequisites

- Python 3.8+
- Git
- MongoDB account (for data storage)
- Streamlit Account (optional, for Streamlit Cloud)

## Local Testing

Before deploying, test the app locally:

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

The app will be available at `http://localhost:8501`

---

## Deployment Options

### Option 1: Streamlit Cloud (Recommended - Free & Easy)

**Advantages:** Free, automatic deployments from GitHub, built for Streamlit

**Steps:**

1. **Push code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Streamlit Cloud:**
   - Go to [streamlit.io/cloud](https://streamlit.io/cloud)
   - Click "New app"
   - Select your repository, branch, and `streamlit_app.py`
   - Click "Deploy"

3. **Configure Secrets:**
   - In Streamlit Cloud dashboard, go to Settings > Secrets
   - Add your MongoDB URL:
     ```
     MONGO_DB_URL = "mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
     ```

4. **Environment Variables:**
   - Create a `.streamlit/secrets.toml` file locally (add to `.gitignore`):
     ```toml
     MONGO_DB_URL = "your_mongodb_url"
     ```

---

### Option 2: Heroku

**Advantages:** More control, suitable for production

**Steps:**

1. **Install Heroku CLI** from https://devcenter.heroku.com/articles/heroku-cli

2. **Login to Heroku:**
   ```bash
   heroku login
   ```

3. **Create a Heroku app:**
   ```bash
   heroku create myntra-review-scrapper
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set MONGO_DB_URL="your_mongodb_url"
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   ```

6. **View logs:**
   ```bash
   heroku logs --tail
   ```

---

### Option 3: Docker (AWS, GCP, Any Cloud)

**Advantages:** Works anywhere, full control

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Create .dockerignore:**
   ```
   __pycache__
   .venv
   .git
   .env
   *.pyc
   ```

3. **Build and push to Docker Hub:**
   ```bash
   docker build -t myntra-scrapper .
   docker tag myntra-scrapper yourusername/myntra-scrapper
   docker push yourusername/myntra-scrapper
   ```

4. **Deploy on AWS ECS, GCP Cloud Run, etc.**

---

### Option 4: AWS Lambda + API Gateway

1. Use `serverless` framework for deployment
2. Requires modifications for serverless environment

---

## Important Notes

### For Streamlit Cloud:

- Free tier has limitations (1GB RAM, limited CPU)
- Selenium web scraping might timeout on free tier
- Consider using Browserless or similar services

### Selenium Headless Mode:

For cloud deployment, ensure Selenium runs in headless mode. Update `scrape.py`:

```python
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
self.driver = webdriver.Chrome(options=options)
```

### MongoDB:

- Use MongoDB Atlas for cloud MongoDB
- Ensure IP whitelist includes your deployment server
- Connection string format: `mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure all dependencies in `requirements.txt` |
| MongoDB connection timeout | Add server IP to MongoDB Atlas IP whitelist |
| Selenium timeout | Increase timeout or use headless mode |
| Streamlit Cloud slow | Use caching: `@st.cache_data` for expensive operations |

---

## After Deployment

- Monitor logs for errors
- Set up error alerts
- Test the app regularly
- Backup MongoDB data periodically

---

## Support

For issues:
1. Check Streamlit docs: https://docs.streamlit.io/
2. Check deployment platform's documentation
3. Review logs for specific errors

