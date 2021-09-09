import boto3

# Create an SNS client
client = boto3.client(
    "sns"
)

# Send your sms message.
client.publish(
    PhoneNumber="+15128148630",
    Message="Hello World!"
)
