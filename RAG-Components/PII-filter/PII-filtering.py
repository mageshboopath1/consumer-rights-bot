import re
import sys
# This is the new import statement to use the shared QueueManager
from shared.queueManager import QueueManager

# The PII redaction function remains the same
def redact_pii(text: str) -> str:
    """
    Scans a text string for common PII and redacts it.
    """
    name_regex = r"\b(?!Mr\.|Ms\.|Dr\.|Mrs\.|Mr|Ms|Dr|and)\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b"
    email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    phone_regex = r"(\(\d{3}\)\s*\d{3}-\d{4}|\d{3}-\d{3}-\d{4})"

    redacted_text = re.sub(email_regex, "[EMAIL]", text)
    redacted_text = re.sub(phone_regex, "[PHONE]", redacted_text)
    redacted_text = re.sub(name_regex, "[NAME]", redacted_text)

    return redacted_text

# This is the new callback function for RabbitMQ
def pii_redact_callback(ch, method, properties, body):
    """
    Callback function to handle incoming messages from the queue.
    It redacts PII and publishes the result to the next queue.
    """
    try:
        # Decode the message body from bytes to a string
        original_text = body.decode('utf-8')
        print(f" [x] Received from 'pii_redaction_queue': {original_text}")

        # Redact PII
        redacted_text = redact_pii(original_text)
        print(f" [x] Redacted text: {redacted_text}")
        
        # Publish the redacted message to the next queue in the pipeline
        queue_manager.send_message(queue_name='rag_core_queue', message=redacted_text)
        
    except Exception as e:
        print(f"Error processing message: {e}", file=sys.stderr)
    
    # Acknowledge the message (auto_ack=True handles this for us, but this is a good pattern to remember)
    ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    # Initialize the QueueManager
    try:
        queue_manager = QueueManager()
    except Exception as e:
        print(f"Failed to initialize QueueManager: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # Start listening for messages on the 'pii_redaction_queue'
        queue_manager.start_listening(queue_name='pii_redaction_queue', callback=pii_redact_callback)
    except KeyboardInterrupt:
        print('Interrupted. Exiting...')
    finally:
        queue_manager.close()