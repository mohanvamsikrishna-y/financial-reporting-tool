# Financial Reporting & Analysis Platform

A comprehensive financial reporting platform with AI-powered insights, real-time data processing, and interactive dashboards.

## Features

- **AI-Powered Analysis**: Google Gemini integration for executive summaries, risk analysis, and trend insights
- **Interactive Dashboard**: Real-time financial data visualization with Streamlit
- **Multi-Source Data**: Support for CSV, Excel, databases, and cloud APIs
- **Real-Time Chat**: AI assistant for instant financial queries
- **Automated Reporting**: Scheduled report generation and distribution
- **Data Validation**: Comprehensive data quality checks and transformation
- **Compliance Tracking**: Audit logs and regulatory compliance monitoring

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL (for production)
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/financial-reporting-tool.git
   cd financial-reporting-tool
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   # Development
   python main.py dashboard
   
   # Production
   docker-compose up -d
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///financial_data.db` |
| `ENVIRONMENT` | Environment (development/staging/production) | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Data Sources

The platform supports multiple data sources:

- **CSV Files**: Direct file upload and processing
- **Excel Files**: Multi-sheet Excel file support
- **Databases**: MySQL, PostgreSQL, SQLite
- **Cloud APIs**: QuickBooks, Xero, Salesforce
- **Google Sheets**: Real-time data synchronization

## Usage

### Web Dashboard

Access the interactive dashboard at `http://localhost:8501`:

- **Overview**: Key financial metrics and KPIs
- **Reports**: P&L, expense breakdown, vendor analysis
- **AI Assistant**: Chat interface for financial queries
- **Data Management**: Upload and manage data sources

### Command Line Interface

```bash
# Generate reports
python main.py run

# Start dashboard
python main.py dashboard

# Create sample data
python main.py create-sample-data

# Run automation
python main.py automation
```

### AI Assistant

The AI assistant can answer questions like:

- "What's my profit margin this quarter?"
- "Where am I spending the most money?"
- "Which vendors should I focus on?"
- "What are the financial risks I should be aware of?"

## API Integration

### QuickBooks Online

```python
from src.data_ingestion.real_data_sources import RealDataConnector

connector = RealDataConnector()
connection = connector.connect_quickbooks(
    client_id="your_client_id",
    client_secret="your_client_secret",
    company_id="your_company_id",
    access_token="your_access_token"
)
```

### Xero

```python
connection = connector.connect_xero(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tenant_id="your_tenant_id",
    access_token="your_access_token"
)
```

### Database Connection

```python
# PostgreSQL
connection = connector.connect_postgresql(
    host="localhost",
    port=5432,
    database="financial_db",
    username="user",
    password="password"
)
```

## Deployment

### Docker Deployment

1. **Build and run**
   ```bash
   docker-compose up -d
   ```

2. **Access the application**
   - Web interface: `http://localhost:8501`
   - Database: `localhost:5432`

### Cloud Deployment

#### Heroku

```bash
# Install Heroku CLI
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set GEMINI_API_KEY=your_key
git push heroku main
```

#### AWS

```bash
# Deploy with ECS
aws ecs create-cluster --cluster-name financial-reporting
aws ecs register-task-definition --cli-input-json file://task-definition.json
aws ecs create-service --cluster financial-reporting --service-name web --task-definition financial-reporting
```

#### Google Cloud

```bash
# Deploy with Cloud Run
gcloud run deploy financial-reporting --source . --platform managed --region us-central1
```

## Development

### Project Structure

```
financial-reporting-tool/
├── src/
│   ├── ai_summary/          # AI integration
│   ├── data_ingestion/      # Data source connectors
│   ├── reporting/           # Report generation
│   ├── storage/             # Database management
│   └── validation/          # Data validation
├── config/                  # Configuration files
├── outputs/                 # Generated reports
├── sample_data/            # Sample data files
├── tests/                  # Test suite
└── docker-compose.yml      # Docker configuration
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_pipeline.py
```

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Wiki](https://github.com/yourusername/financial-reporting-tool/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/financial-reporting-tool/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/financial-reporting-tool/discussions)

## Changelog

### v1.0.0
- Initial release
- AI-powered financial analysis
- Multi-source data integration
- Interactive web dashboard
- Real-time chat assistant
- Automated report generation