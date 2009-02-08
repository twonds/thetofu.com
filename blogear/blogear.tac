# blogear.tac
# -*- mode: python -*-

from twisted.application import service
from twisted.words.protocols.jabber import jid

from wokkel.client import XMPPClient

import bot

application = service.Application("blogear")

blog = bot.PubSub2Blog(".")


client = XMPPClient(jid.internJID("tofu@localhost"), "secret")
client.logTraffic = True
client.setServiceParent(application)

listener = bot.Bot(blog, jid.internJID("pubsub.localhost"), "/home/localhost/tofu")
listener.setHandlerParent(client)


