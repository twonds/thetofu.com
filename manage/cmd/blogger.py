import os
from twisted.python import log
from twisted.internet import defer, reactor
from twisted.words.xish import domish, xpath

from wokkel.subprotocols import XMPPHandler
from wokkel import xmppim, pubsub, data_form

NS_ATOM = 'http://www.w3.org/2005/Atom'

class Blogger(pubsub.PubSubClient):

    author_name = None
    author_nick = None

    options = [
        data_form.Field(var='pubsub#presence_based_delivery',value='1'),
        data_form.Field(var='pubsub#persist_items',value='1'),
        data_form.Field(var='pubsub#max_items',value='10'), #change this value later
        ]
    


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
        
        # gather and create blog
        request = self._buildConfigureRequest('get')

        node_configure = yield request.send(self.service).addErrback(lambda _: None)
        
        
        do_create = True
        if node_configure and node_configure.getAttribute('type') == 'result':
            do_create = False
            # check the configuration
            node_persistence = xpath.queryForNodes(
                "/x/field[@var='pubsub#persist_items']/value", 
                node_configure.pubsub.configure.x)
            if len(node_persistence)>0 and str(node_persistence[0]) == '0':
                request = self._buildConfigureRequest(options=self.options)
                
                r = yield request.send(self.service)

                
        if do_create:
            yield self.create()


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
            # clean up blog path
            blog_id, prefix = os.path.basename(self.blog).split(".",1)
            
            atom.addElement('id', None, self.node+':'+blog_id)
            
            r = yield self.publish(self.service, self.node, [pubsub.Item(payload=atom)])

            self.send(xmppim.UnavailablePresence())
            
            reactor.stop()
            

    def _buildConfigureRequest(self, method='set', nodeIdentifier=None, options=[]):
        if nodeIdentifier is None:
            nodeIdentifier = self.node
        request = pubsub._PubSubRequest(self.xmlstream, 
                                 'configure', 
                                 pubsub.NS_PUBSUB_OWNER, 
                                 method=method)
        request.command['node'] = nodeIdentifier
        if options:
            configure = data_form.Form('submit', 
                                       fields=options,
                                       formNamespace=pubsub.NS_PUBSUB+'#node_config')
            
            request.command.addChild(configure.toElement())
            
        return request

    @defer.inlineCallbacks
    def create(self, nodeIdentifier=None):
        """
        create the publish subscribe node 
        
        NOTE: wokkel needs better configuration support 
        """
        if nodeIdentifier is None:
            nodeIdentifier = self.node
        result = yield self.createNode(self.service, nodeIdentifier, nodeType='flat')

        
        
    def createNode(self, service, nodeIdentifier=None, nodeType=None):
        """
        Create a publish subscribe node.
        
        @param service: The publish subscribe service to create the node at.
        @type service: L{JID}
        @param nodeIdentifier: Optional suggestion for the id of the node.
        @type nodeIdentifier: C{unicode}
        """
        

        request = pubsub._PubSubRequest(self.xmlstream, 'create')
        if nodeIdentifier:
            request.command['node'] = nodeIdentifier
        if nodeType:
            request.command['type'] = nodeType
        request.pubsub.addElement('configure')
        configure = data_form.Form('submit', 
                                   fields=self.options,
                                   formNamespace=pubsub.NS_PUBSUB+'#node_config')
        
        request.pubsub.configure.addChild(configure.toElement())

        
        def cb(iq):
            try:
                new_node = iq.pubsub.create["node"]
            except AttributeError:
                # the suggested node identifier was accepted
                new_node = nodeIdentifier
            return new_node

        return request.send(service).addCallback(cb)


