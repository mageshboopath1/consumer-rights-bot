import sys
import json
import os

# Add the parent directory to the system path to allow importing queue_manager.py
# This is necessary because the script is in a subdirectory.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

from shared.queue_manager import QueueManager

def send_message(message_text):
    """
    Sends a message with the provided text to the pii_filtering_queue.
    """
    manager = QueueManager(rabbitmq_host='rabbitmq')
    
    # Create the message payload with the provided text
    test_data = {
        "text": message_text
    }
    
    message = json.dumps(test_data)
    
    try:
        manager.send_message(queue_name='pii_filtering_queue', message=message)
        print(f" [✓] Message sent successfully: '{message_text}'")
    finally:
        manager.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # If arguments are provided, use them as the message
        input_text = ' '.join(sys.argv[1:])
        send_message(input_text)
    else:
        # If no arguments, prompt the user for input
        print("Please provide text to send as a command-line argument.")
        print("Example: python interactive_client.py 'Hello my name is John Smith.'")
        sys.exit(1)
