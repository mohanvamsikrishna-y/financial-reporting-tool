"""
API data ingestion module for external data sources.
"""

import requests
import pandas as pd
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class APIDataIngestion:
    """Handles data ingestion from external APIs"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Financial-Reporting-Tool/1.0'
        })
    
    def get_exchange_rates(self, base_currency: str = 'USD', target_currencies: Optional[list] = None) -> pd.DataFrame:
        """Fetch exchange rates from external API"""
        try:
            if target_currencies is None:
                target_currencies = ['EUR', 'GBP', 'JPY', 'CAD', 'AUD']
            
            # Use free exchange rate API
            url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DataFrame
            rates_data = []
            for currency, rate in data['rates'].items():
                if currency in target_currencies or not target_currencies:
                    rates_data.append({
                        'currency': currency,
                        'rate_to_usd': 1 / rate if currency != base_currency else 1.0,
                        'rate_date': datetime.now(),
                        'source': 'exchangerate-api.com'
                    })
            
            df = pd.DataFrame(rates_data)
            logger.info(f"Successfully fetched exchange rates for {len(df)} currencies")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching exchange rates: {str(e)}")
            # Return default rates if API fails
            return self._get_default_exchange_rates(target_currencies)
        except Exception as e:
            logger.error(f"Unexpected error fetching exchange rates: {str(e)}")
            return self._get_default_exchange_rates(target_currencies)
    
    def _get_default_exchange_rates(self, currencies: list) -> pd.DataFrame:
        """Return default exchange rates when API is unavailable"""
        default_rates = {
            'EUR': 0.85,
            'GBP': 0.73,
            'JPY': 110.0,
            'CAD': 1.25,
            'AUD': 1.35
        }
        
        rates_data = []
        for currency in currencies:
            rate = default_rates.get(currency, 1.0)
            rates_data.append({
                'currency': currency,
                'rate_to_usd': rate,
                'rate_date': datetime.now(),
                'source': 'default'
            })
        
        logger.warning("Using default exchange rates due to API unavailability")
        return pd.DataFrame(rates_data)
    
    def get_economic_indicators(self, country: str = 'US') -> pd.DataFrame:
        """Fetch economic indicators (placeholder for future implementation)"""
        # This is a placeholder for future economic data integration
        # Could integrate with APIs like FRED, World Bank, etc.
        logger.info(f"Economic indicators for {country} not implemented yet")
        return pd.DataFrame()
    
    def get_market_data(self, symbols: list) -> pd.DataFrame:
        """Fetch market data (placeholder for future implementation)"""
        # This is a placeholder for future market data integration
        # Could integrate with APIs like Alpha Vantage, Yahoo Finance, etc.
        logger.info(f"Market data for {symbols} not implemented yet")
        return pd.DataFrame()
    
    def test_api_connectivity(self) -> Dict[str, Any]:
        """Test API connectivity and return status"""
        test_results = {
            'exchange_rate_api': False,
            'response_time': None,
            'error_message': None
        }
        
        try:
            start_time = time.time()
            response = self.session.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                test_results['exchange_rate_api'] = True
                test_results['response_time'] = round(end_time - start_time, 2)
            else:
                test_results['error_message'] = f"HTTP {response.status_code}"
                
        except Exception as e:
            test_results['error_message'] = str(e)
        
        return test_results
