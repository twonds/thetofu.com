from twisted.python import log
from twisted.internet import defer
from twisted.words.xish import domish

from wokkel.subprotocols import XMPPHandler
from wokkel import xmppim, pubsub, data_form

NS_ATOM = 'http://www.w3.org/2005/Atom'

class Blogger(pubsub.PubSubClient):

    author_name = None
    author_nick = None

    def __init__(self, service, node):
        self.service = service
        self.node = node

    def get_jid(self):
        return self.xmlstream.factory.authenticator.jid

    def getBlogEntry(self):
        bf = open(self.blog)
        blog_entry = bf.read()
        bf.close()
        return blog_entry.split('\n',1)

    @defer.inlineCallbacks
    def getAuthorName(self):
        iq = xmppim.IQ(self.xmlstream, 'get')
        iq.addElement('vCard','vcard-temp')
        r = yield iq.send(self.get_jid().full())

        vcard = getattr(r, 'vCard', None)
        if vcard:
            fn = getattr(vcard, 'FN', None)
            if fn:
                self.author_name = str(fn)
            nick = getattr(vcard, 'NICKNAME', None)
            if nick:
                self.author_nick = str(nick)
        
    @defer.inlineCallbacks
    def connectionInitialized(self):
        self.send(xmppim.AvailablePresence())
        
        # open file to blog and publish it
        if self.blog:
            # grab author information
            yield self.getAuthorName()

            subject, body = self.getBlogEntry()

            # build atom message and then publish
            atom = domish.Element((NS_ATOM,'entry'))
            author = atom.addElement('author')
            
            author.addElement('jid',None, self.get_jid().userhost())
            if self.author_name:
                author.addElement('name', None, self.author_name)
            if self.author_nick:
                author.addElement('nickname', None, self.author_nick)
            atom.addElement('generator', None, 'Twisted PubSuBlog')
            atom.addElement('title', None, subject)
            atom.addElement('content', None, body)
            atom.addElement('id', None, self.node+':'+self.blog)
            
            r = yield self.publish(self.service, self.node, [pubsub.Item(payload=atom)])

        
