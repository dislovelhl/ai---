"""
Email Service for sending transactional emails.

Supports:
- Password reset emails
- Welcome emails
- Notification emails

Uses SMTP with SSL/TLS for secure email delivery.
Optimized for Chinese email providers (QQ Mail, 163, etc.)

Security:
- All user-provided content is HTML-escaped to prevent XSS
"""

import smtplib
import ssl
import html
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import Optional, List
import logging
from urllib.parse import quote
from .config import settings

logger = logging.getLogger(__name__)


def escape_html(text: str) -> str:
    """Escape HTML special characters to prevent XSS."""
    return html.escape(str(text), quote=True)


def escape_url_param(text: str) -> str:
    """URL-encode a parameter for safe inclusion in URLs."""
    return quote(str(text), safe='')


class EmailService:
    """Email service for sending transactional emails."""

    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        self.from_name = settings.SMTP_FROM_NAME
        self.use_ssl = settings.SMTP_USE_SSL
        self.use_tls = settings.SMTP_USE_TLS

    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(self.user and self.password and self.from_email)

    def _create_smtp_connection(self):
        """Create SMTP connection with proper SSL/TLS settings."""
        if self.use_ssl:
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(self.host, self.port, context=context)
        else:
            server = smtplib.SMTP(self.host, self.port)
            if self.use_tls:
                server.starttls()

        if self.user and self.password:
            server.login(self.user, self.password)

        return server

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> bool:
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional, for fallback)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)

        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.warning("Email service not configured. Skipping email send.")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = formataddr((self.from_name, self.from_email))
            msg["To"] = to_email

            if cc:
                msg["Cc"] = ", ".join(cc)

            # Add plain text version if provided
            if text_content:
                part1 = MIMEText(text_content, "plain", "utf-8")
                msg.attach(part1)

            # Add HTML version
            part2 = MIMEText(html_content, "html", "utf-8")
            msg.attach(part2)

            # Build recipient list
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)

            # Send email
            with self._create_smtp_connection() as server:
                server.sendmail(self.from_email, recipients, msg.as_string())

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """
        Send password reset email.

        Args:
            to_email: User's email address
            reset_token: Password reset token

        Returns:
            True if email was sent successfully
        """
        # URL-encode the token for safe inclusion in URL
        safe_token = escape_url_param(reset_token)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={safe_token}"
        # HTML-escape the URL for display in email
        safe_reset_url = escape_html(reset_url)

        subject = "重置您的密码 - AI导航"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    text-align: center;
                    padding: 20px 0;
                    border-bottom: 1px solid #eee;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #6366f1;
                }}
                .content {{
                    padding: 30px 0;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 28px;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                    color: white !important;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
                .button:hover {{
                    opacity: 0.9;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px 0;
                    border-top: 1px solid #eee;
                    color: #666;
                    font-size: 12px;
                }}
                .note {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    font-size: 14px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">AI导航</div>
            </div>
            <div class="content">
                <h2>重置您的密码</h2>
                <p>您好，</p>
                <p>我们收到了您的密码重置请求。点击下面的按钮来重置您的密码：</p>
                <p style="text-align: center;">
                    <a href="{safe_reset_url}" class="button">重置密码</a>
                </p>
                <div class="note">
                    <p><strong>注意：</strong></p>
                    <ul>
                        <li>此链接将在 1 小时后过期</li>
                        <li>如果您没有请求重置密码，请忽略此邮件</li>
                        <li>如果按钮无法点击，请复制以下链接到浏览器：<br>
                            <code style="word-break: break-all;">{safe_reset_url}</code>
                        </li>
                    </ul>
                </div>
            </div>
            <div class="footer">
                <p>&copy; 2025 AI导航. 保留所有权利.</p>
                <p>如有任何问题，请联系我们的支持团队。</p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        重置您的密码 - AI导航

        您好，

        我们收到了您的密码重置请求。请访问以下链接来重置您的密码：

        {reset_url}

        注意：
        - 此链接将在 1 小时后过期
        - 如果您没有请求重置密码，请忽略此邮件

        AI导航团队
        """

        return self.send_email(to_email, subject, html_content, text_content)

    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """
        Send welcome email to new users.

        Args:
            to_email: User's email address
            username: User's username

        Returns:
            True if email was sent successfully
        """
        # HTML-escape the username to prevent XSS
        safe_username = escape_html(username)
        safe_dashboard_url = escape_html(f"{settings.FRONTEND_URL}/dashboard")

        subject = "欢迎加入 AI导航!"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    text-align: center;
                    padding: 20px 0;
                    border-bottom: 1px solid #eee;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #6366f1;
                }}
                .content {{
                    padding: 30px 0;
                }}
                .feature {{
                    display: flex;
                    align-items: flex-start;
                    margin: 15px 0;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 8px;
                }}
                .feature-icon {{
                    font-size: 24px;
                    margin-right: 15px;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 28px;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                    color: white !important;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px 0;
                    border-top: 1px solid #eee;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="logo">AI导航</div>
            </div>
            <div class="content">
                <h2>欢迎加入 AI导航, {safe_username}!</h2>
                <p>感谢您注册 AI导航 - 您的一站式AI工具发现平台。</p>

                <h3>您可以：</h3>
                <div class="feature">
                    <span class="feature-icon">🔍</span>
                    <div>
                        <strong>发现 AI 工具</strong><br>
                        浏览数百款精选 AI 工具，找到最适合您的解决方案
                    </div>
                </div>
                <div class="feature">
                    <span class="feature-icon">🤖</span>
                    <div>
                        <strong>创建智能体工作流</strong><br>
                        在 Studio 中构建您自己的 AI 自动化工作流
                    </div>
                </div>
                <div class="feature">
                    <span class="feature-icon">📚</span>
                    <div>
                        <strong>学习 AI 技能</strong><br>
                        通过我们的学习路线图，系统性地提升 AI 技能
                    </div>
                </div>

                <p style="text-align: center;">
                    <a href="{safe_dashboard_url}" class="button">开始探索</a>
                </p>
            </div>
            <div class="footer">
                <p>&copy; 2025 AI导航. 保留所有权利.</p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        欢迎加入 AI导航, {username}!

        感谢您注册 AI导航 - 您的一站式AI工具发现平台。

        您可以：
        - 发现 AI 工具：浏览数百款精选 AI 工具
        - 创建智能体工作流：在 Studio 中构建 AI 自动化
        - 学习 AI 技能：通过学习路线图提升技能

        访问您的控制台：{settings.FRONTEND_URL}/dashboard

        AI导航团队
        """

        return self.send_email(to_email, subject, html_content, text_content)


# Singleton instance
email_service = EmailService()
