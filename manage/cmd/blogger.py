from twisted.words.xish import domish

from wokkel.subprotocols import XMPPHandler
from wokkel import xmppim, pubsub, data_form


class Blogger(pubsub.PubSubClient):


    def __init__(self, service, node):
        self.service = service
        self.node = node

    def get_jid(self):
        return self.xmlstream.factory.authenticator.jid

    def connectionInitialized(self):
        self.send(xmppim.AvailablePresence())
        
        # open file to blog and publish it


        
