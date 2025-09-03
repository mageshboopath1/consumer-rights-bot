import sys
import pika

class QueueManager:
    """
    A reusable class to manage RabbitMQ connections and message handling.
    """
    def __init__(self, rabbitmq_host='rabbitmq'):
        """
        Initializes the QueueManager and establishes a connection to RabbitMQ.
        """
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
            self.channel = self.connection.channel()
            print(" [i] Connected to RabbitMQ.")
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Error: Could not connect to RabbitMQ at '{rabbitmq_host}'. Please ensure the service is running. Details: {e}", file=sys.stderr)
            sys.exit(1)

    def send_message(self, queue_name: str, message: str):
        """
        Sends a message to a specified queue.

        Args:
            queue_name (str): The name of the queue.
            message (str): The message to send.
        """
        self.channel.queue_declare(queue=queue_name)
        self.channel.basic_publish(exchange='',
                                   routing_key=queue_name,
                                   body=message.encode('utf-8'))
        print(f" [x] Sent message to '{queue_name}'")

    def start_listening(self, queue_name: str, callback):
        """
        Starts listening for messages on a queue. This is a blocking call.

        Args:
            queue_name (str): The name of the queue to listen to.
            callback: The function to call when a message is received.
        """
        self.channel.queue_declare(queue=queue_name)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        print(f' [*] Waiting for messages on {queue_name}. To exit press CTRL+C')
        self.channel.start_consuming()

    def close(self):
        """
        Closes the connection to RabbitMQ.
        """
        if self.connection and self.connection.is_open:
            self.connection.close()
            print(" [i] Closed connection to RabbitMQ.")