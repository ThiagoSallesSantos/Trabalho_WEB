#!/usr/bin/env python
import pika

user = "guest"
password = "guest"
host = "localhost"
queue = "sorvete_delicia"

credentials = pika.PlainCredentials(user, password)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue=queue, durable=True)

print(' [*] Esperando mensagens. Pressione CTRL+C para sair')

def callback(ch, method, properties, body):
    print(
        f"""
        Mensagem recebida foi:
        {body.decode()}
        --------------------------
        """
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue, on_message_callback=callback)

channel.start_consuming()