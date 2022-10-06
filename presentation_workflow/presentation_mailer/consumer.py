import json
import pika
from pika.exceptions import AMQPConnectionError
import django
import os
import sys
import time
from django.core.mail import send_mail


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()

# def process_message(ch, method, properties, body):
#     print("  Received %r" % body)

def approval_message(ch, method, properties, body):
    content = json.loads(body)
    presenter_name = content["presenter_name"]
    presentation_title = content["title"]
    presenter_email = content["presenter_email"]
    send_mail(
        "Your presentation has been accepted",
        f"{presenter_name}, we're happy to tell you that your presentation {presentation_title} has been accepted",
        "admin@conference.go",
        [presenter_email],
        fail_silently=False,
    )

def rejection_message(ch, method, properties, body):
    content = json.loads(body)
    presenter_name = content["presenter_name"]
    presentation_title = content["title"]
    presenter_email = content["presenter_email"]
    send_mail(
        "Your presentation has been rejected",
        f"{presenter_name}, we're sorry to inform you that your presentation {presentation_title} has been rejected",
        "admin@conference.go",
        [presenter_email],
        fail_silently=False,
    )

def main():
    parameters = pika.ConnectionParameters(host='rabbitmq')
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='presentation_approvals')
    channel.queue_declare(queue='presentation_rejections')
    channel.basic_consume(
        queue='presentation_approvals',
        on_message_callback=approval_message,
        auto_ack=True,
    )
    channel.basic_consume(
        queue='presentation_rejections',
        on_message_callback=rejection_message,
        auto_ack=True,
    )
    channel.start_consuming()



while True:
    try:
        if __name__ == '__main__':
            try:
                main()
            except KeyboardInterrupt:
                print('Interrupted')
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)
    except AMQPConnectionError:
        print("Could not connect to RabbitMQ")
        time.sleep(2.0)
