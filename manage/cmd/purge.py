import sys

try:
    from twisted.internet import epollreactor
    epollreactor.install()
except:
    pass
from twisted.internet import reactor

from zope.interface import implements
from twisted.python import log
from twisted.internet import defer
from twisted.words.protocols.jabber import jid
from wokkel import client, pubsub

from blogger import Blogger

VERSION=0.1

class Purger(pubsub.PubSubClient):
    """
    """

    def __init__(self, service, node):
        self.service = service
        self.node = node

    def get_jid(self):
        return self.xmlstream.factory.authenticator.jid

    @defer.inlineCallbacks
    def connectionInitialized(self):
                
        # gather items and remove them
        ret_items = yield self.items(self.service, self.node)

        for item in ret_items:
            r = yield self.retract(self.service, self.node, item['id'])
            

    def retract(self, service, nodeIdentifier, item_id, method='set'):
        request = pubsub._PubSubRequest(self.xmlstream, 
                                        'retract', 
                                        pubsub.NS_PUBSUB_OWNER, 
                                        method=method)
        request.command['node'] = nodeIdentifier
        item = request.command.addElement('item')
        item['id'] = item_id
        
        return request.send(service)


@defer.inlineCallbacks
def createPurger(domain, service, node, username, password, debug=False):
    
    factory = client.DeferredClientFactory(jid.internJID(username), password)
    factory.streamManager.logTraffic = debug

    purger = Purger(jid.internJID(service), node)
    purger.setHandlerParent(factory.streamManager)

    yield client.clientCreator(factory)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options] username password node', version=VERSION)


    parser.add_option('-s', '--server', action='store', dest='server',
                      help='XMPP Server we will connect to.')

    parser.add_option('-p', '--pubsub', action='store', dest='pubsub',
                      help='XMPP PubSub Search Service')


    parser.add_option('-a', '--author', action='store', dest='author',
                      help='Author Name')

    parser.add_option('-d', '--debug', action='store', dest='debug',
                      help='Show debug information.')


    parser.set_defaults(server="localhost")
    parser.set_defaults(pubsub="pubsub.localhost")

    parser.set_defaults(author=None)
    parser.set_defaults(debug=False)

    
    options, args = parser.parse_args()

    if len(args) != 3:
        print parser.get_usage()
    else:
        log.startLogging(sys.stdout)

        reactor.callWhenRunning(createPurger,
                                options.server,
                                options.pubsub,
                                args[2],
                                args[0],
                                args[1],
                                options.debug)
        reactor.run()
