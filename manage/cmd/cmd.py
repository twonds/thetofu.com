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
from wokkel import client

from blogger import Blogger

VERSION=0.1

@defer.inlineCallbacks
def createSearcher(domain, service, node, username, password, blog, debug=False):
    
    factory = client.DeferredClientFactory(jid.internJID(username), password)
    factory.streamManager.logTraffic = debug

    blogger = Blogger(jid.internJID(service), node)
    blogger.blog = blog
    blogger.setHandlerParent(factory.streamManager)

    yield client.clientCreator(factory)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options] username password blog_file', version=VERSION)


    parser.add_option('-s', '--server', action='store', dest='server',
                      help='XMPP Server we will connect to.')

    parser.add_option('-p', '--pubsub', action='store', dest='pubsub',
                      help='XMPP PubSub Search Service')

    parser.add_option('-n', '--node', action='store', dest='node',
                      help='Node to publish to')

    parser.add_option('-d', '--debug', action='store', dest='debug',
                      help='Show debug information.')


    parser.set_defaults(server="localhost")
    parser.set_defaults(pubsub="pubsub.localhost")
    parser.set_defaults(node="blog")
    parser.set_defaults(debug=False)

    
    options, args = parser.parse_args()

    if len(args) != 3:
        print parser.get_usage()
    else:
        log.startLogging(sys.stdout)

        reactor.callWhenRunning(createSearcher,
                                options.server,
                                options.pubsub,
                                options.node,
                                args[0],
                                args[1],
                                args[2],
                                options.debug)
        reactor.run()
