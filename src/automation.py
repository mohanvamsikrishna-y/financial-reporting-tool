"""
Automation and scheduling module for the Financial Reporting Tool.
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

from config.settings import *
from src.pipeline import FinancialReportingPipeline

logger = logging.getLogger(__name__)

class AutomationManager:
    """Manages automated reporting and scheduling"""
    
    def __init__(self, pipeline: FinancialReportingPipeline):
        self.pipeline = pipeline
        self.is_running = False
        self.scheduler_thread = None
        self.email_enabled = EMAIL_ENABLED
        
        if self.email_enabled:
            self._setup_email()
    
    def _setup_email(self):
        """Setup email configuration"""
        try:
            self.smtp_server = SMTP_SERVER
            self.smtp_port = SMTP_PORT
            self.email_username = EMAIL_USERNAME
            self.email_password = EMAIL_PASSWORD
            self.notification_emails = [email.strip() for email in NOTIFICATION_EMAILS if email.strip()]
            
            logger.info("Email configuration setup successfully")
        except Exception as e:
            logger.error(f"Error setting up email: {str(e)}")
            self.email_enabled = False
    
    def start_scheduler(self):
        """Start the automated scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Schedule daily refresh
            if REFRESH_SCHEDULE == 'daily':
                schedule.every().day.at(REFRESH_TIME).do(self._run_daily_refresh)
                logger.info(f"Daily refresh scheduled for {REFRESH_TIME}")
            
            # Schedule weekly refresh
            elif REFRESH_SCHEDULE == 'weekly':
                schedule.every().monday.at(REFRESH_TIME).do(self._run_weekly_refresh)
                logger.info(f"Weekly refresh scheduled for Monday at {REFRESH_TIME}")
            
            # Schedule monthly refresh
            elif REFRESH_SCHEDULE == 'monthly':
                schedule.every().month.do(self._run_monthly_refresh)
                logger.info("Monthly refresh scheduled")
            
            # Start scheduler in background thread
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            logger.info("Automation scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")
            raise
    
    def stop_scheduler(self):
        """Stop the automated scheduler"""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            self.is_running = False
            schedule.clear()
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            logger.info("Automation scheduler stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {str(e)}")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(60)
    
    def _run_daily_refresh(self):
        """Run daily data refresh and report generation"""
        logger.info("Starting daily refresh")
        
        try:
            # Run pipeline for current month
            current_period = datetime.now().strftime("%Y-%m")
            results = self.pipeline.run_full_pipeline(period=current_period)
            
            if results['status'] == 'success':
                logger.info("Daily refresh completed successfully")
                self._send_notification("Daily Refresh Completed", 
                                      "Financial reports have been generated successfully.", 
                                      results)
            else:
                logger.error("Daily refresh failed")
                self._send_notification("Daily Refresh Failed", 
                                      f"Error: {results.get('error', 'Unknown error')}", 
                                      results)
                
        except Exception as e:
            logger.error(f"Error in daily refresh: {str(e)}")
            self._send_notification("Daily Refresh Error", 
                                  f"Error: {str(e)}", 
                                  {})
    
    def _run_weekly_refresh(self):
        """Run weekly data refresh and report generation"""
        logger.info("Starting weekly refresh")
        
        try:
            # Run pipeline for current month
            current_period = datetime.now().strftime("%Y-%m")
            results = self.pipeline.run_full_pipeline(period=current_period)
            
            if results['status'] == 'success':
                logger.info("Weekly refresh completed successfully")
                self._send_notification("Weekly Refresh Completed", 
                                      "Financial reports have been generated successfully.", 
                                      results)
            else:
                logger.error("Weekly refresh failed")
                self._send_notification("Weekly Refresh Failed", 
                                      f"Error: {results.get('error', 'Unknown error')}", 
                                      results)
                
        except Exception as e:
            logger.error(f"Error in weekly refresh: {str(e)}")
            self._send_notification("Weekly Refresh Error", 
                                  f"Error: {str(e)}", 
                                  {})
    
    def _run_monthly_refresh(self):
        """Run monthly data refresh and report generation"""
        logger.info("Starting monthly refresh")
        
        try:
            # Run pipeline for previous month
            last_month = datetime.now().replace(day=1) - timedelta(days=1)
            period = last_month.strftime("%Y-%m")
            results = self.pipeline.run_full_pipeline(period=period)
            
            if results['status'] == 'success':
                logger.info("Monthly refresh completed successfully")
                self._send_notification("Monthly Refresh Completed", 
                                      f"Financial reports for {period} have been generated successfully.", 
                                      results)
            else:
                logger.error("Monthly refresh failed")
                self._send_notification("Monthly Refresh Failed", 
                                      f"Error: {results.get('error', 'Unknown error')}", 
                                      results)
                
        except Exception as e:
            logger.error(f"Error in monthly refresh: {str(e)}")
            self._send_notification("Monthly Refresh Error", 
                                  f"Error: {str(e)}", 
                                  {})
    
    def run_manual_refresh(self, period: Optional[str] = None) -> Dict[str, Any]:
        """Run manual refresh for specified period"""
        logger.info(f"Starting manual refresh for period: {period or 'current'}")
        
        try:
            results = self.pipeline.run_full_pipeline(period=period)
            
            if results['status'] == 'success':
                logger.info("Manual refresh completed successfully")
                self._send_notification("Manual Refresh Completed", 
                                      f"Financial reports for {period or 'current period'} have been generated successfully.", 
                                      results)
            else:
                logger.error("Manual refresh failed")
                self._send_notification("Manual Refresh Failed", 
                                      f"Error: {results.get('error', 'Unknown error')}", 
                                      results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in manual refresh: {str(e)}")
            self._send_notification("Manual Refresh Error", 
                                  f"Error: {str(e)}", 
                                  {})
            return {'status': 'error', 'error': str(e)}
    
    def _send_notification(self, subject: str, message: str, results: Dict[str, Any]):
        """Send email notification"""
        if not self.email_enabled or not self.notification_emails:
            logger.info("Email notifications disabled or no recipients configured")
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = ', '.join(self.notification_emails)
            msg['Subject'] = f"Financial Reporting Tool - {subject}"
            
            # Add body
            body = f"""
            {message}
            
            Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Results Summary:
            - Status: {results.get('status', 'Unknown')}
            - Reports Generated: {len(results.get('report_results', {}).get('excel_reports', []))} Excel, {len(results.get('report_results', {}).get('pdf_reports', []))} PDF
            - AI Summaries: {len(results.get('ai_summary_results', {}).get('summary_files', []))}
            
            Please check the outputs/reports directory for generated files.
            
            ---
            Financial Reporting Tool v1.0
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_username, self.notification_emails, text)
            server.quit()
            
            logger.info(f"Notification sent to {len(self.notification_emails)} recipients")
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status"""
        return {
            'is_running': self.is_running,
            'schedule_type': REFRESH_SCHEDULE,
            'schedule_time': REFRESH_TIME,
            'email_enabled': self.email_enabled,
            'notification_recipients': len(self.notification_emails) if self.email_enabled else 0,
            'next_run': self._get_next_run_time()
        }
    
    def _get_next_run_time(self) -> Optional[str]:
        """Get next scheduled run time"""
        try:
            jobs = schedule.get_jobs()
            if jobs:
                next_run = min(job.next_run for job in jobs)
                return next_run.strftime('%Y-%m-%d %H:%M:%S')
            return None
        except Exception as e:
            logger.error(f"Error getting next run time: {str(e)}")
            return None
    
    def add_custom_schedule(self, schedule_type: str, time_str: str, function):
        """Add custom schedule"""
        try:
            if schedule_type == 'daily':
                schedule.every().day.at(time_str).do(function)
            elif schedule_type == 'weekly':
                schedule.every().monday.at(time_str).do(function)
            elif schedule_type == 'monthly':
                schedule.every().month.do(function)
            else:
                raise ValueError(f"Unsupported schedule type: {schedule_type}")
            
            logger.info(f"Custom schedule added: {schedule_type} at {time_str}")
            
        except Exception as e:
            logger.error(f"Error adding custom schedule: {str(e)}")
            raise
    
    def remove_all_schedules(self):
        """Remove all scheduled jobs"""
        try:
            schedule.clear()
            logger.info("All schedules removed")
        except Exception as e:
            logger.error(f"Error removing schedules: {str(e)}")
            raise
