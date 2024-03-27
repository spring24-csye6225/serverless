# User Verification Cloud Function

This Cloud Function is designed to handle user verification processes in your application. When a new user is created, a message is published to a Google Cloud Pub/Sub topic, triggering this function. The function then generates a verification token, stores it in the database, and sends a verification email to the user.

## Prerequisites

Before deploying and using this Cloud Function, ensure that you have:

- Google Cloud SDK installed and configured.
- Access to a Google Cloud project with billing enabled.
- Required Google Cloud services enabled (e.g., Cloud Functions, Cloud Pub/Sub, Cloud SQL).
- Terraform installed, if using Terraform for deployment.

## Configuration

Variables to be set in the Terraform script or environment:

- `DB_USER`: Username for the database access.
- `DB_PASSWORD`: Password for the database access.
- `DB_NAME`: Name of the database.
- `DB_HOST`: Host address of the Cloud SQL instance.
- `MAILGUN_API_KEY`: API key for Mailgun to send emails.
- `MAILGUN_DOMAIN`: Domain configured in Mailgun for sending emails.
- `DB_CONNECTION_NAME`: Connection name of the Cloud SQL instance.

## Deployment

To deploy the function with Terraform, navigate to the directory containing your Terraform scripts and run:

```bash
terraform init
terraform apply
```

## Function Logic

1. The function is triggered by a message on the Google Cloud Pub/Sub topic.
2. It decodes the message, which contains the new user's email.
3. It connects to the Cloud SQL database and inserts a new verification token.
4. Generates a verification link and sends an email to the user through Mailgun.

## Testing

After deployment, test the function by publishing a message to the associated Pub/Sub topic. Ensure the message format aligns with the expected schema.

## Logs

Logs for the function execution can be viewed in the Google Cloud Console under Cloud Functions logs.

## Troubleshooting

For any errors or issues:
- Check the logs for detailed error messages.
- Verify all environment variables and dependencies are correctly configured.
- Ensure the Cloud Function has appropriate permissions and roles.

