import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException

async def send_email(to: str, subject: str, template_vars: dict):
    """
    Send an email using SMTP with template
    """
    # Get email settings from environment variables
    email_host = os.getenv("EMAIL_HOST")
    email_port = int(os.getenv("EMAIL_PORT", "587"))
    email_username = os.getenv("EMAIL_USERNAME")
    email_password = os.getenv("EMAIL_PASSWORD")
    email_from = os.getenv("EMAIL_FROM")
    email_use_tls = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "t")
    
    # Check if all required settings are available
    if not all([email_host, email_username, email_password, email_from]):
        raise HTTPException(status_code=500, detail="Email configuration missing. Please check server settings.")
    
    # Load the HTML template
    html_content = get_email_template()

    # Ensure required template variables are present
    main_message = template_vars.get("main_message", "")

    # Replace template variables in the template
    html_content = html_content.replace("{{main_message}}", str(main_message))

    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = email_from
    message["To"] = to
    message["Subject"] = subject

    # Add message body
    message.attach(MIMEText(html_content, "html"))

    try:
        # Create SMTP session
        with smtplib.SMTP(email_host, email_port) as server:
            if email_use_tls:
                server.starttls()

            # Login to server
            server.login(email_username, email_password)

            # Send email
            server.sendmail(email_from, [to], message.as_string())

        return {
            "success": True,
            "message": "Email sent successfully",
            "to": to,
            "subject": subject
        }

    except Exception as e:
        print(f"Error sending email: {str(e)}, {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

def get_email_template():
    """Return the HTML template for emails"""
    # You could load this from a file or store it as a string
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SaaS API Notification</title>
    <style type="text/css">
        /* Base styles for email clients */
        body, html {
            margin: 0;
            padding: 0;
            font-family: Arial, Helvetica, sans-serif;
            line-height: 1.5;
            color: #333333;
        }
        .email-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
        }
        .email-header {
            padding: 20px 0;
            text-align: center;
            border-bottom: 1px solid #eeeeee;
        }
        .email-logo {
            width: 120px;
            height: auto;
        }
        .email-title {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin: 20px 0 10px;
        }
        .email-content {
            padding: 20px 0;
        }
        .email-button {
            display: inline-block;
            padding: 12px 24px;
            background-color: #3498db;
            color: #ffffff;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            margin: 20px 0;
        }
        .email-footer {
            padding: 20px 0;
            border-top: 1px solid #eeeeee;
            font-size: 12px;
            color: #999999;
            text-align: center;
        }
        @media screen and (max-width: 480px) {
            .email-container {
                padding: 10px;
            }
            .email-title {
                font-size: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="email-header">
            <!-- Replace with your actual logo URL -->
            <img src="https://via.placeholder.com/120x60?text=SaaS+API" alt="" class="email-logo">
            <h1 class="email-title">Free Micro Service</h1>
        </div>
        
        <div class="email-content">
            <!-- Main content goes here -->
            <p>{{main_message}}</p>
        </div>
        
        <div class="email-footer">
            <p>The email should not be involved in real money requests/transactions</p>
            <p>If the email is suspicious, please ignore it.</p>
            <p>This is an automated message, please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>"""