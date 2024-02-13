import json

import paho.mqtt.client as mqtt
import requests
import docker

broker_address = "192.168.153.32"
broker_port = 1883
shared_url = {"url": 'http://192.168.153.237:8000/calculator'}

def is_container_running(container_name):
    # Connect to Docker
    dockerClient = docker.from_env()

    # List all containers
    all_containers = dockerClient.containers.list(all=True)

    # Check if the specified container is running
    for container in all_containers:
        if container.name == container_name:
            if container.status == 'running':
                return True
            break
    return False

def on_connect(client,userdata,flags,rc):
    print("Connected to the broker with result code " + str(rc))

    client.subscribe([("MLSysOps/Data/DISTANCE", 0), ("MLSysOps/Data/XY", 0)])


def on_message(client, userdata, msg):
    print("asd")
    receivedMsg = json.loads(msg.payload)
    print(receivedMsg)

    if is_container_running("calculatorservice"):
        print("run")
        shared_url["url"] = 'http://192.168.153.237:8000/calculator'
    else:
        print("notrun")
        shared_url["url"] = 'http://192.168.153.237:8001/visualizer'

    print("test")
    print(shared_url["url"])

    res = requests.post(shared_url["url"],
                        headers={
                            'Content-type': 'application/json'
                        },
                        json=receivedMsg

                        )


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message
print ("Here")
client.connect(broker_address, broker_port,60)


client.loop_forever()

