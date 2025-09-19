"""
AI-powered financial analysis and reporting.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)

class AISummarizer:
    """AI-powered financial analysis and reporting."""
    
    def __init__(self, provider: str = 'gemini', api_key: Optional[str] = None, model: Optional[str] = None):
        self.provider = provider.lower()
        self.max_tokens = 500
        self.temperature = 0.7
        
        # Initialize based on provider
        if self.provider == 'gemini':
            self._init_gemini(api_key, model)
        elif self.provider == 'openai':
            self._init_openai(api_key, model)
        else:
            logger.warning(f"Unknown provider: {provider}. Supported: gemini, openai")
            self.api_key = None
    
    def _init_gemini(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize Google Gemini API"""
        try:
            import google.generativeai as genai
            
            self.api_key = api_key or os.getenv('GEMINI_API_KEY')
            self.model_name = model or 'gemini-1.5-flash'
            
            if not self.api_key:
                logger.warning("Gemini API key not provided. AI summaries will not be available.")
                return
            
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Google Gemini API initialized successfully with model: {self.model_name}")
            
        except ImportError:
            logger.error("google-generativeai package not installed. Install with: pip install google-generativeai")
            self.api_key = None
        except Exception as e:
            logger.error(f"Error initializing Gemini API: {str(e)}")
            self.api_key = None
    
    def _init_openai(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize OpenAI API"""
        try:
            import openai
            
            self.api_key = api_key or os.getenv('OPENAI_API_KEY')
            self.model_name = model or 'gpt-3.5-turbo'
            
            if not self.api_key:
                logger.warning("OpenAI API key not provided. AI summaries will not be available.")
                return
            
            openai.api_key = self.api_key
            logger.info(f"OpenAI API initialized successfully with model: {self.model_name}")
            
        except ImportError:
            logger.error("openai package not installed. Install with: pip install openai")
            self.api_key = None
        except Exception as e:
            logger.error(f"Error initializing OpenAI API: {str(e)}")
            self.api_key = None
    
    def generate_executive_summary(self, 
                                 pnl_data: pd.DataFrame,
                                 expense_data: pd.DataFrame,
                                 vendor_data: pd.DataFrame,
                                 period: str) -> Dict[str, Any]:
        """Generate executive summary for financial reports"""
        
        if not self.api_key:
            return {
                'summary': f"AI summary not available - {self.provider.title()} API key not configured.",
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Prepare data summary
            data_summary = self._prepare_data_summary(pnl_data, expense_data, vendor_data, period)
            
            # Generate prompt
            prompt = self._create_summary_prompt(data_summary, period)
            
            # Call appropriate AI provider
            if self.provider == 'gemini':
                summary_text = self._call_gemini(prompt)
            elif self.provider == 'openai':
                summary_text = self._call_openai(prompt)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            result = {
                'summary': summary_text,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'provider': self.provider,
                'model_used': getattr(self, 'model_name', 'unknown'),
                'data_points': len(data_summary)
            }
            
            logger.info(f"Executive summary generated successfully using {self.provider} for period {period}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {str(e)}")
            return {
                'summary': f"Error generating summary: {str(e)}",
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'provider': self.provider
            }
    
    def generate_risk_analysis(self, 
                             pnl_data: pd.DataFrame,
                             expense_data: pd.DataFrame,
                             vendor_data: pd.DataFrame,
                             period: str) -> Dict[str, Any]:
        """Generate risk analysis summary"""
        
        if not self.api_key:
            return {
                'analysis': f"Risk analysis not available - {self.provider.title()} API key not configured.",
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Prepare risk data
            risk_data = self._prepare_risk_data(pnl_data, expense_data, vendor_data, period)
            
            # Generate prompt
            prompt = self._create_risk_prompt(risk_data, period)
            
            # Call appropriate AI provider
            if self.provider == 'gemini':
                analysis_text = self._call_gemini(prompt)
            elif self.provider == 'openai':
                analysis_text = self._call_openai(prompt)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            result = {
                'analysis': analysis_text,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'provider': self.provider,
                'model_used': getattr(self, 'model_name', 'unknown')
            }
            
            logger.info(f"Risk analysis generated successfully using {self.provider} for period {period}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating risk analysis: {str(e)}")
            return {
                'analysis': f"Error generating risk analysis: {str(e)}",
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'provider': self.provider
            }
    
    def generate_trend_analysis(self, 
                              monthly_data: pd.DataFrame,
                              period: str) -> Dict[str, Any]:
        """Generate trend analysis summary"""
        
        if not self.api_key:
            return {
                'analysis': f"Trend analysis not available - {self.provider.title()} API key not configured.",
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Prepare trend data
            trend_data = self._prepare_trend_data(monthly_data, period)
            
            # Generate prompt
            prompt = self._create_trend_prompt(trend_data, period)
            
            # Call appropriate AI provider
            if self.provider == 'gemini':
                analysis_text = self._call_gemini(prompt)
            elif self.provider == 'openai':
                analysis_text = self._call_openai(prompt)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
            
            result = {
                'analysis': analysis_text,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'provider': self.provider,
                'model_used': getattr(self, 'model_name', 'unknown')
            }
            
            logger.info(f"Trend analysis generated successfully using {self.provider} for period {period}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating trend analysis: {str(e)}")
            return {
                'analysis': f"Error generating trend analysis: {str(e)}",
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'provider': self.provider
            }
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API"""
        import google.generativeai as genai
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=self.max_tokens,
                temperature=self.temperature
            )
        )
        return response.text.strip()
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        import openai
        
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a financial analyst providing executive summaries for financial reports. Focus on key insights, trends, and actionable recommendations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        return response.choices[0].message.content.strip()
    
    def _prepare_data_summary(self, pnl_data: pd.DataFrame, 
                            expense_data: pd.DataFrame, 
                            vendor_data: pd.DataFrame, 
                            period: str) -> Dict[str, Any]:
        """Prepare data summary for AI analysis"""
        
        # P&L summary
        revenue_data = pnl_data[pnl_data['account_type'] == 'Revenue']
        expense_data_pnl = pnl_data[pnl_data['account_type'] == 'Expense']
        
        revenue_total = revenue_data['net_amount'].sum()
        expense_total = expense_data_pnl['net_amount'].sum()
        net_income = revenue_total - expense_total
        
        # Expense breakdown
        total_expenses = expense_data['total_amount'].sum()
        expense_categories = expense_data['category'].tolist()
        top_expense_category = expense_data.iloc[0]['category'] if not expense_data.empty else "N/A"
        top_expense_amount = expense_data.iloc[0]['total_amount'] if not expense_data.empty else 0
        
        # Vendor analysis
        total_vendors = len(vendor_data)
        total_vendor_spending = vendor_data['total_amount'].sum()
        top_vendor = vendor_data.iloc[0]['vendor_name'] if not vendor_data.empty else "N/A"
        top_vendor_amount = vendor_data.iloc[0]['total_amount'] if not vendor_data.empty else 0
        
        return {
            'period': period,
            'revenue_total': revenue_total,
            'expense_total': expense_total,
            'net_income': net_income,
            'total_expenses': total_expenses,
            'expense_categories': expense_categories,
            'top_expense_category': top_expense_category,
            'top_expense_amount': top_expense_amount,
            'total_vendors': total_vendors,
            'total_vendor_spending': total_vendor_spending,
            'top_vendor': top_vendor,
            'top_vendor_amount': top_vendor_amount
        }
    
    def _prepare_risk_data(self, pnl_data: pd.DataFrame, 
                          expense_data: pd.DataFrame, 
                          vendor_data: pd.DataFrame, 
                          period: str) -> Dict[str, Any]:
        """Prepare risk analysis data"""
        
        data_summary = self._prepare_data_summary(pnl_data, expense_data, vendor_data, period)
        
        # Calculate risk indicators
        expense_concentration = 0
        if not expense_data.empty:
            top_3_expenses = expense_data.head(3)['total_amount'].sum()
            total_expenses = expense_data['total_amount'].sum()
            expense_concentration = (top_3_expenses / total_expenses) * 100 if total_expenses > 0 else 0
        
        vendor_concentration = 0
        if not vendor_data.empty:
            top_3_vendors = vendor_data.head(3)['total_amount'].sum()
            total_vendor_spending = vendor_data['total_amount'].sum()
            vendor_concentration = (top_3_vendors / total_vendor_spending) * 100 if total_vendor_spending > 0 else 0
        
        return {
            **data_summary,
            'expense_concentration': expense_concentration,
            'vendor_concentration': vendor_concentration,
            'is_profitable': data_summary['net_income'] > 0
        }
    
    def _prepare_trend_data(self, monthly_data: pd.DataFrame, period: str) -> Dict[str, Any]:
        """Prepare trend analysis data"""
        
        if monthly_data.empty:
            return {'period': period, 'trends': []}
        
        trends = []
        for account_type in monthly_data['account_type'].unique():
            type_data = monthly_data[monthly_data['account_type'] == account_type].sort_values('month')
            if len(type_data) > 1:
                first_amount = type_data.iloc[0]['net_amount']
                last_amount = type_data.iloc[-1]['net_amount']
                change_percent = ((last_amount - first_amount) / abs(first_amount)) * 100 if first_amount != 0 else 0
                
                trends.append({
                    'account_type': account_type,
                    'first_amount': first_amount,
                    'last_amount': last_amount,
                    'change_percent': change_percent,
                    'trend_direction': 'increasing' if change_percent > 0 else 'decreasing'
                })
        
        return {
            'period': period,
            'trends': trends,
            'total_months': len(monthly_data['month'].unique())
        }
    
    def _create_summary_prompt(self, data_summary: Dict[str, Any], period: str) -> str:
        """Create prompt for executive summary generation"""
        
        prompt = f"""
        Please provide a concise executive summary for the financial report covering {period}. 
        
        Key Financial Metrics:
        - Total Revenue: ${data_summary['revenue_total']:,.2f}
        - Total Expenses: ${data_summary['expense_total']:,.2f}
        - Net Income: ${data_summary['net_income']:,.2f}
        - Top Expense Category: {data_summary['top_expense_category']} (${data_summary['top_expense_amount']:,.2f})
        - Total Vendors: {data_summary['total_vendors']}
        - Top Vendor: {data_summary['top_vendor']} (${data_summary['top_vendor_amount']:,.2f})
        
        Please provide a 5-8 sentence summary that:
        1. Highlights the key financial performance
        2. Identifies the most significant expense categories
        3. Notes any notable vendor relationships
        4. Provides a brief assessment of financial health
        5. Suggests any immediate areas of attention
        
        Write in a professional, executive-friendly tone suitable for board presentations.
        """
        
        return prompt
    
    def _create_risk_prompt(self, risk_data: Dict[str, Any], period: str) -> str:
        """Create prompt for risk analysis generation"""
        
        prompt = f"""
        Please provide a risk analysis for the financial period {period}.
        
        Financial Metrics:
        - Net Income: ${risk_data['net_income']:,.2f} (Profitable: {risk_data['is_profitable']})
        - Expense Concentration (Top 3 categories): {risk_data['expense_concentration']:.1f}%
        - Vendor Concentration (Top 3 vendors): {risk_data['vendor_concentration']:.1f}%
        - Top Expense Category: {risk_data['top_expense_category']} (${risk_data['top_expense_amount']:,.2f})
        - Top Vendor: {risk_data['top_vendor']} (${risk_data['top_vendor_amount']:,.2f})
        
        Please identify:
        1. Key financial risks and their potential impact
        2. Concentration risks in expenses or vendors
        3. Profitability concerns
        4. Recommended mitigation strategies
        5. Areas requiring immediate attention
        
        Provide a concise 4-6 sentence analysis suitable for risk management discussions.
        """
        
        return prompt
    
    def _create_trend_prompt(self, trend_data: Dict[str, Any], period: str) -> str:
        """Create prompt for trend analysis generation"""
        
        trends_text = ""
        for trend in trend_data['trends']:
            trends_text += f"- {trend['account_type']}: {trend['trend_direction']} by {abs(trend['change_percent']):.1f}% (${trend['first_amount']:,.2f} to ${trend['last_amount']:,.2f})\n"
        
        prompt = f"""
        Please analyze the financial trends for the period {period}.
        
        Trend Data (covering {trend_data['total_months']} months):
        {trends_text}
        
        Please provide:
        1. Overall trend assessment
        2. Key patterns and changes
        3. Potential implications for future performance
        4. Areas of concern or opportunity
        5. Recommended actions based on trends
        
        Provide a concise 4-6 sentence analysis suitable for strategic planning discussions.
        """
        
        return prompt
    
    def save_summary_to_file(self, summary_data: Dict[str, Any], 
                           output_dir: str = 'outputs/reports',
                           filename: Optional[str] = None) -> str:
        """Save AI summary to text file"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            provider = summary_data.get('provider', 'unknown')
            filename = f"AI_Summary_{provider}_{timestamp}.txt"
        
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("AI-GENERATED EXECUTIVE SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {summary_data['timestamp']}\n")
            f.write(f"Provider: {summary_data.get('provider', 'unknown')}\n")
            f.write(f"Model: {summary_data.get('model_used', 'N/A')}\n")
            f.write(f"Status: {summary_data['status']}\n\n")
            
            if summary_data['status'] == 'success':
                f.write("SUMMARY:\n")
                f.write("-" * 20 + "\n")
                f.write(summary_data['summary'])
            else:
                f.write("ERROR:\n")
                f.write("-" * 20 + "\n")
                f.write(summary_data['summary'])
        
        logger.info(f"AI summary saved to: {file_path}")
        return file_path
