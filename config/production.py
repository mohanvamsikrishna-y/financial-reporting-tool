import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class DatabaseConfig:
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600

@dataclass
class AIConfig:
    provider: str = "gemini"
    api_key: Optional[str] = None
    model: str = "gemini-1.5-flash"
    max_tokens: int = 500
    temperature: float = 0.7
    rate_limit: int = 250

@dataclass
class APIConfig:
    exchange_rate_key: str = "free"
    timeout: int = 30
    retry_attempts: int = 3

@dataclass
class LoggingConfig:
    level: str = "INFO"
    file_path: str = "logs/financial_reporting.log"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5

@dataclass
class SecurityConfig:
    secret_key: str = os.urandom(32).hex()
    session_timeout: int = 3600
    max_login_attempts: int = 5
    password_min_length: int = 8

class ProductionConfig:
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self._load_config()
    
    def _load_config(self):
        """Load configuration based on environment"""
        if self.environment == Environment.PRODUCTION:
            self._load_production_config()
        elif self.environment == Environment.STAGING:
            self._load_staging_config()
        else:
            self._load_development_config()
    
    def _load_development_config(self):
        """Development configuration"""
        self.database = DatabaseConfig(
            url=os.getenv('DATABASE_URL', 'sqlite:///financial_data.db')
        )
        
        self.ai = AIConfig(
            provider=os.getenv('AI_PROVIDER', 'gemini'),
            api_key=os.getenv('GEMINI_API_KEY'),
            model=os.getenv('AI_MODEL', 'gemini-1.5-flash')
        )
        
        self.api = APIConfig(
            exchange_rate_key=os.getenv('EXCHANGE_RATE_API_KEY', 'free')
        )
        
        self.logging = LoggingConfig(
            level=os.getenv('LOG_LEVEL', 'DEBUG'),
            file_path='logs/financial_reporting.log'
        )
        
        self.security = SecurityConfig()
        
        self.reports_dir = 'outputs/reports'
        self.sample_data_dir = 'sample_data'
        self.upload_dir = 'uploads'
        
    def _load_staging_config(self):
        """Staging configuration"""
        self.database = DatabaseConfig(
            url=os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost:5432/financial_staging'),
            pool_size=20,
            max_overflow=30
        )
        
        self.ai = AIConfig(
            provider=os.getenv('AI_PROVIDER', 'gemini'),
            api_key=os.getenv('GEMINI_API_KEY'),
            model=os.getenv('AI_MODEL', 'gemini-1.5-flash'),
            rate_limit=500
        )
        
        self.api = APIConfig(
            exchange_rate_key=os.getenv('EXCHANGE_RATE_API_KEY'),
            timeout=60
        )
        
        self.logging = LoggingConfig(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            file_path='/var/log/financial_reporting.log'
        )
        
        self.security = SecurityConfig(
            secret_key=os.getenv('SECRET_KEY', os.urandom(32).hex())
        )
        
        self.reports_dir = '/var/reports'
        self.sample_data_dir = '/var/sample_data'
        self.upload_dir = '/var/uploads'
        
    def _load_production_config(self):
        """Production configuration"""
        self.database = DatabaseConfig(
            url=os.getenv('DATABASE_URL'),
            pool_size=50,
            max_overflow=100,
            pool_timeout=60,
            pool_recycle=1800
        )
        
        self.ai = AIConfig(
            provider=os.getenv('AI_PROVIDER', 'gemini'),
            api_key=os.getenv('GEMINI_API_KEY'),
            model=os.getenv('AI_MODEL', 'gemini-1.5-pro'),
            max_tokens=1000,
            rate_limit=1000
        )
        
        self.api = APIConfig(
            exchange_rate_key=os.getenv('EXCHANGE_RATE_API_KEY'),
            timeout=120,
            retry_attempts=5
        )
        
        self.logging = LoggingConfig(
            level=os.getenv('LOG_LEVEL', 'WARNING'),
            file_path='/var/log/financial_reporting.log',
            max_file_size=52428800,  # 50MB
            backup_count=10
        )
        
        self.security = SecurityConfig(
            secret_key=os.getenv('SECRET_KEY'),
            session_timeout=7200,
            max_login_attempts=3,
            password_min_length=12
        )
        
        self.reports_dir = os.getenv('REPORTS_DIR', '/var/reports')
        self.sample_data_dir = os.getenv('SAMPLE_DATA_DIR', '/var/sample_data')
        self.upload_dir = os.getenv('UPLOAD_DIR', '/var/uploads')
        
        # Production-specific settings
        self.debug = False
        self.testing = False
        self.ssl_required = True
        self.cors_origins = os.getenv('CORS_ORIGINS', '').split(',')
        
    def get_database_url(self) -> str:
        """Get database URL"""
        return self.database.url
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration"""
        return {
            'provider': self.ai.provider,
            'api_key': self.ai.api_key,
            'model': self.ai.model,
            'max_tokens': self.ai.max_tokens,
            'temperature': self.ai.temperature,
            'rate_limit': self.ai.rate_limit
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            'level': self.logging.level,
            'file_path': self.logging.file_path,
            'max_file_size': self.logging.max_file_size,
            'backup_count': self.logging.backup_count
        }
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == Environment.DEVELOPMENT

# Global configuration instance
config = ProductionConfig(
    environment=Environment(os.getenv('ENVIRONMENT', 'development'))
)
