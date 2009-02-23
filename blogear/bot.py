# bot.py
#
# Pubsub Client Bot - Listens to pubsub events for new blog entries.
#
import time
import datetime
from twisted.python import log
from twisted.internet import defer
from twisted.words.xish import domish, xpath
from wokkel.pubsub import PubSubClient, Item
from wokkel import disco
from twisted.words.protocols.jabber.jid import internJID

from wokkel.xmppim import AvailablePresence


class PubSub2Blog(object):
    """ Handles PubSub event items and turns them to formated static files.

    The templates are extremly simple for now and can be changed later.
    """

    def __init__(self, path):
        self.path = path

    def template(self, file, vars):
        """ Very simple template for writing atom to templates.
        """
        return open(self.path+'/'+file, 'r').read() % vars


    def atom2html(self, orig):
	"""Return a sanitized Atom entry.
	This method should be overridden.
	"""
        args = {}

        if orig.content:
            args['content'] = str(orig.content)
        elif orig.title:
            args['content'] = str(orig.title)
            
        if orig.title:
            args['title'] = str(orig.title)
        elif oriq.id:
            args['title'] = str(orig.id)
        else:
            args['title'] = 'No Title'
        return self.template('entry.html', args)
	


class Bot(PubSubClient):
    """The listener bot to manage the static html representing thetofu.com
    
    In addition to the standard XMPPHandler behavior, it also provides
    getJid() and publish().
    """
    admins = []

    def __init__(self, blog, service=None, node=None):
	PubSubClient.__init__(self)
        self.blog = blog
	self.service = service
	self.nodeIdentifier = node

    def connectionInitialized(self):
        """When connection is establised send presence and subscribe to the node 
        that the bot is listening to. 
        """
        self.send(AvailablePresence())
        
        self.subscribe(self.service, self.nodeIdentifier, self.getJid().userhostJID())
        
        PubSubClient.connectionInitialized(self)


    def itemsReceived(self, item_event):
        """Gather items, convert to html and send the files to there proper location.
        """
        
        for item in item_event.items:
            if item.name != 'item': # TODO - handle retract and other events
                continue
            item_id = item.getAttribute('id', str(time.time()))

            date_pub = xpath.queryForNodes("/item/entry/published", item)
            published = datetime.datetime.now()
            if date_pub:
                published = str(date_pub[0])

            blog_id = None
            blog_ids = xpath.queryForNodes("/item/entry/id", item)
            if blog_ids:
                blog_id = str(blog_ids[0])
                
            log.msg(blog_id)

            # create entry
            html = self.blog.atom2html(item.entry)
            log.msg(html)
            
            # update index

            # update rss



    def getJid(self):
	"""Return the JID the connection is authenticed as."""

	return self.xmlstream.authenticator.jid



