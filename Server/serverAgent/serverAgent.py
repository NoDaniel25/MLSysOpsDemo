import spade
from aioxmpp import PresenceShow
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
import docker

import time
import asyncio


class ServerAgent(Agent):
    class SubscBehav(OneShotBehaviour):

        def on_available(self, jid, stanza):
            print("[{}] Agent {} is available.".format(self.agent.name, jid.split("@")[0]))


        def on_subscribed(self, jid):
            print("[{}] Agent {} has accepted the subscription.".format(self.agent.name, jid.split("@")[0]))
            print("[{}] Contacts List: {}".format(self.agent.name, self.agent.presence.get_contacts()))

        def on_subscribe(self, jid):
            print("[{}] Agent {} asked for subscription. Let's aprove it.".format(self.agent.name, jid.split("@")[0]))
            self.presence.approve(jid)

        async def run(self):
            print("Subscription behaviour running")

            self.presence.on_subscribe = self.on_subscribe
            self.presence.on_subscribed = self.on_subscribed
            self.presence.on_available = self.on_available
            self.presence.set_available()
            self.presence.subscribe("cluster_agent@192.168.153.5")

    class RecvBehav(CyclicBehaviour
                    ):

        @staticmethod
        def get_parameters(command):

            comando = command.strip('[]')
            elements = comando.split(',')
            task = elements[0]
            containers = elements[1:]
            return task, containers

        async def run(self):
            print("RecvBehav running")

            msg = await self.receive(timeout=60)  # wait for a message for 10 seconds

            if msg:
                print("Message received with content: {}".format(msg.body))
                docker_client = docker.from_env()

                task, cont = self.get_parameters(msg.body)

                call = Message(to="cluster_agent@192.168.153.5")  # Instantiate the message
                call.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                call.thread = "2032"

                if task == "start":
                    print("Start docker")
                    try:
                        for i in cont:
                            print("starting service " + i)
                            ls = docker_client.containers.get(i)
                            ls.start()

                        print("Service started")
                        call.body = "Service started "
                        await self.send(call)
                    except:
                        print("Service not started ")
                        call.body = "Failure  starting the service"
                        await self.send(call)
                elif task == "stop":
                    try:
                        for i in cont:
                            print("Stopping Service " + i)
                            ls = docker_client.containers.get(i)
                            ls.stop()
                        print("Service stopped")
                        call.body = "Service stopped"
                        await self.send(call)
                    except:
                        print("Service not stopped")
                        call.body = "Failure stopping the service"
                        await self.send(call)
                elif task == "list":
                    print("List command ")
                    # Lista todos los contenedores
                    containers = docker_client.containers.list()

                    print("Send response")
                    print(str(containers))
                    call.body = str(containers)  # Set the message content
                    await self.send(call)
                elif task == "CB":
                    print("Call back recibido ")

                else:
                    print("command not found")


            else:
                print("Did not received any message after 5 seconds")

            # stop agent from behaviour
            # await self.agent.stop()
            # time.sleep(1)
            # await asyncio.sleep(1)

    async def setup(self):
        print("Server agent  set up ...")

        c = self.SubscBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(c, template)

        b = self.RecvBehav()
        template = Template()
        template.set_metadata("performative", "inform")
        self.add_behaviour(b, template)


async def main():
    serveragent = ServerAgent("server_agent@192.168.153.5", "123")
    await serveragent.start(auto_register=True)
    print("Server agent running ...")
    serveragent.web.start(hostname="127.0.0.1", port="10001")
    serveragent.presence.set_available(show=PresenceShow.CHAT)

    await spade.wait_until_finished(serveragent)
    print("Agents finished")


if __name__ == "__main__":
    spade.run(main())