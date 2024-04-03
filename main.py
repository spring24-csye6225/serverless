import os
import base64
import json
import pymysql
import requests
import uuid
import logging
from datetime import datetime, timedelta, timezone

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def verify_email(event, context):
    """Triggered by a message on a Cloud Pub/Sub topic.
    Args:
        event (dict): Event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """
    try:
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        message_data = json.loads(pubsub_message)
        user_email = message_data["username"]
        logger.info(f"Received message for user: {user_email}")
    except Exception as e:
        logger.error(f"Error processing Pub/Sub message: {e}")
        return

    # Database Connection
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_name = os.environ.get('DB_NAME')
    db_connection_name = os.environ.get('DB_CONNECTION_NAME')
    db_host = os.environ.get('DB_HOST')
    try:
        db = pymysql.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            database=db_name
        )
        logger.info("Successfully connected to the database")
    except Exception as e:
        logger.error(f'Error connecting to DB: {e}')
        return

    # Generate Token and Expiration
    token = str(uuid.uuid4())
    expiration = datetime.now(timezone.utc) + timedelta(minutes=2)

    # Store in Database
    try:
        with db.cursor() as cursor:
            # Format expiration for SQL
            formatted_expiration = expiration.strftime('%Y-%m-%d %H:%M:%S')
            sql = "INSERT INTO verification_token (token, email, expiration, verified) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (token, user_email, formatted_expiration, 0))
        db.commit()
        logger.info(f"Token stored in database with expiration: {formatted_expiration}")
    except Exception as e:
        logger.error(f"DB Error on token storage: {e}")
        db.rollback()
        return

    # Construct Verification Link
    verification_link = f"https://ns1.csye6225-vakiti.me/verify?token={token}"

    # Send Email using Mailgun
    try:
        mailgun_api_key = os.environ.get('MAILGUN_API_KEY')
        mailgun_domain = os.environ.get('MAILGUN_DOMAIN')
        request_url = f'https://api.mailgun.net/v3/{mailgun_domain}/messages'
        response = requests.post(
            request_url,
            auth=("api", mailgun_api_key),
            data={
                "from": "webapp@csye6225-vakiti.me",
                "to": [user_email],
                "subject": "Verify Your Email",
                "text": f"Click here to verify your email: {verification_link}"
            })

        if response.status_code != 200:
            logger.error(f'Error sending email via Mailgun: {response.text}')
        else:
            logger.info(f'Email sent successfully to {user_email}')
    except Exception as e:
        logger.error(f'Error sending email: {e}')
        return

    # Close Database Connection
    if db:
        db.close()
        logger.info("Database connection closed")
