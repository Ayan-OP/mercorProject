import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.config import settings

async def send_invitation_email(to_email: str, token: str):
    """
    Sends an invitation email to the new employee with their activation token.
    """
    # This is the URL for your frontend application's activation page
    activation_url = f"http://localhost:3000/activate-account?token={token}"

    message = MIMEMultipart("alternative")
    message["Subject"] = "You're Invited to Join T3 Tracker"
    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email

    # Create the plain-text and HTML version of your message
    text = f"""
    Hi,
    You have been invited to join the T3 Time Tracker.
    Please activate your account by visiting the following link:
    {activation_url}
    """
    html = f"""
    <html>
      <body>
        <h2>Welcome!</h2>
        <p>You have been invited to join the T3 Time Tracker.</p>
        <p>Please click the button below to activate your account and set your password.</p>
        <a href="{activation_url}" style="background-color: #4CAF50; color: white; padding: 14px 25px; text-align: center; text-decoration: none; display: inline-block; border-radius: 8px;">Activate Your Account</a>
        <p>If you cannot click the button, copy and paste this link into your browser:</p>
        <p>{activation_url}</p>
      </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    message.attach(part1)
    message.attach(part2)

    # Send the email
    try:
        # NOTE: This is a synchronous operation. For high-volume sending,
        # you would use a background task queue (e.g., Celery, ARQ).
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, to_email, message.as_string())
        print(f"Invitation email successfully sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")
        # In a real app, you might want to handle this failure more gracefully
        # (e.g., retry, log to a monitoring service).