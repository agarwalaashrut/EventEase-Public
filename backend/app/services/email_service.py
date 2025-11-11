"""
Email service for sending notifications
Handles invitation emails and event update notifications
"""
from flask_mail import Mail, Message
import os

mail = Mail()


def init_mail(app):
    """Initialize Flask-Mail with app configuration"""
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@eventease.com')
    
    # IMPORTANT: Disable Flask-Mail's test mode suppression
    app.config['MAIL_SUPPRESS_SEND'] = False
    
    mail.init_app(app)

def send_invitation_email(recipient_email, event_title, organizer, event_id):
    """
    Send an invitation email to a user
    
    Args:
        recipient_email (str): Email address of the recipient
        event_title (str): Title of the event
        organizer (str): Name of the event organizer
        event_id (str): ID of the event for generating links
    """
    try:
        msg = Message(
            subject=f"You're invited to {event_title}",
            recipients=[recipient_email]
        )
        
        msg.body = f"""
Hello!

You have been invited to the following event:

Event: {event_title}
Organized by: {organizer}

To view event details and respond to this invitation, please log in to EventEase.

Event ID: {event_id}

Best regards,
The EventEase Team
"""
        
        msg.html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
        .event-details {{ background-color: white; padding: 15px; margin: 20px 0; border-left: 4px solid #007bff; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        .cta-button {{ display: inline-block; padding: 12px 24px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>You're Invited!</h1>
        </div>
        <div class="content">
            <p>Hello!</p>
            <p>You have been invited to join an event on EventEase.</p>
            
            <div class="event-details">
                <h2 style="margin-top: 0; color: #007bff;">{event_title}</h2>
                <p><strong>Organized by:</strong> {organizer}</p>
            </div>
            
            <p>To view full event details and respond to this invitation, please log in to EventEase.</p>
            
            <p style="text-align: center;">
                <a href="#" class="cta-button">View Event Details</a>
            </p>
            
            <p style="font-size: 12px; color: #666;">Event ID: {event_id}</p>
        </div>
        <div class="footer">
            <p>This is an automated message from EventEase. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending invitation email to {recipient_email}: {str(e)}")
        return False


def send_response_notification(organizer_email, user_name, user_email, event_title, response):
    """
    Notify event organizer when someone responds to an invitation
    
    Args:
        organizer_email (str): Email address of the event organizer
        user_name (str): Name of the user who responded
        user_email (str): Email of the user who responded
        event_title (str): Title of the event
        response (str): "accepted" or "declined"
    """
    try:
        response_text = "accepted" if response == "accepted" else "declined"
        response_color = "#28a745" if response == "accepted" else "#dc3545"
        
        msg = Message(
            subject=f"Response to {event_title}: {user_name} has {response_text}",
            recipients=[organizer_email]
        )
        
        msg.body = f"""
Hello,

{user_name} ({user_email}) has {response_text} your invitation to "{event_title}".

Best regards,
The EventEase Team
"""
        
        msg.html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
        .response-badge {{ display: inline-block; padding: 8px 16px; background-color: {response_color}; color: white; border-radius: 20px; font-weight: bold; margin: 10px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Invitation Response</h1>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p><strong>{user_name}</strong> ({user_email}) has responded to your event invitation:</p>
            
            <p style="text-align: center;">
                <span class="response-badge">{response_text.upper()}</span>
            </p>
            
            <p><strong>Event:</strong> {event_title}</p>
            
            <p>You can view all event details and attendee responses in EventEase.</p>
        </div>
        <div class="footer">
            <p>This is an automated message from EventEase. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending response notification to {organizer_email}: {str(e)}")
        return False
