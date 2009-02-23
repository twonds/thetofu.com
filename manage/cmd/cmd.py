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


@defer.inlineCallbacks
def createSearcher(domain, service, node, blog, debug=False):
    
    factory = ClientFactory(jid.internJID(domain), None)
    factory.streamManager.logTraffic = debug

    searcher = Blogger(jid.internJID(service), node)
    searcher.blog = blog
    searcher.setHandlerParent(factory.streamManager)

    yield client.clientCreator(factory)

