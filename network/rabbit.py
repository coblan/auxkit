import pika

class AutoConnectBlockingPika(object):
    "会自动重连，自动判断channel"
    def __init__(self, host,port=5672,user='',password='', **kwargs):
        self.host = host
        self.port=port
        self.user=user
        self.password = password
        self.connection = None
        self.channel = None
    
    def getChannel(self):
        if not self.connection or self.connection.is_closed:
            credentials = pika.PlainCredentials(self.user,self.password)
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host,port=self.port,credentials=credentials))
            #self.createConnect()
            self.channel = self.connection.channel()
        elif self.channel.is_closed:
            self.channel = self.connection.channel()
        return self.channel
    
    #def createConnect(self):
        #temped = 0
        #while True:
            #try:
                #credentials = pika.PlainCredentials(self.user,self.password)
                #self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host,port=self.port,credentials=credentials))
                #break
            #except Exception as e:
                #print('第%s次重新连接rabbitmq'%temped)
                #temped +=1
                #if temped >3:
                    #raise e


class Consumer(AutoConnectBlockingPika):
    def start_consuming(self):
        while True:
            try:
                self.getChannel()
                self.bind()
                self.channel.start_consuming()
            except Exception as e:
                print(e)

    def bind(self):
        print('need overwrite bind methods')
    
    

#import pika
#import sys

#connection = pika.BlockingConnection(
    #pika.ConnectionParameters(host='localhost'))
#channel = connection.channel()

#channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

#result = channel.queue_declare('', exclusive=True)
#queue_name = result.method.queue

#binding_keys = sys.argv[1:]
#if not binding_keys:
    #sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
    #sys.exit(1)

#for binding_key in binding_keys:
    #channel.queue_bind(
        #exchange='topic_logs', queue=queue_name, routing_key=binding_key)

#print(' [*] Waiting for logs. To exit press CTRL+C')


#def callback(ch, method, properties, body):
    #print(" [x] %r:%r" % (method.routing_key, body))


#channel.basic_consume(
    #queue=queue_name, on_message_callback=callback, auto_ack=True)

#channel.start_consuming()