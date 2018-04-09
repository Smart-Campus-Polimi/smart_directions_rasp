import paho.mqtt.client as mqtt
import time

##########
def on_message(client, userdata, message):
	print "message received " ,str(message.payload.decode("utf-8"))
	print "message topic=",message.topic 
	print "message qos=",message.qos
	print "message retain flag=",message.retain

########
broker_address = "192.168.1.74" 
topic_name = "topic/rasp4/directions"
#############
print "creating new instance"
client = mqtt.Client("P1")
print "connecting to broker"
client.connect(broker_address)
client.on_message = on_message #attach function to callback

#client.loop_start() #start the loop
print "Subscribing to topic"+topic_name
client.subscribe(topic_name)
#client.publish(topic_name, "sucazz")
client.loop_forever()
time.sleep(4) # wait
print "ciao allora?"
#client.loop_stop() #stop the loop