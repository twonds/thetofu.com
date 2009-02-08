# bot.py
#
# Pubsub Client Bot - Listens to PEP notifications for new blog entries.
#
import time
from twisted.internet import defer
from twisted.words.xish import domish
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
        return open(templatedir.template, 'r').read() % vars


    def atom2html(self, orig):
	"""Return a sanitized Atom entry.
	This method should be overridden.
	"""
        content = None

        if orig.content:
            content = orig.content
        elif orig.title:
            content = orig.title


	return orig


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
        p = AvailablePresence()
        p.addElement('priority', None, '-1')
        self.send(p)
        
        self.subscribe(self.service, self.nodeIdentifier, self.getJid().userhostJID())
        

    def rebuild(self):
        """Gather all items and rebuild html.
        """

    def itemsReceived(self, items):
        """Gather items, convert to html and send the files to there proper location.
        """

        for item in items:
            item_id = item.getAttribute('id', str(time.time()))

    def getJid(self):
	"""Return the JID the connection is authenticed as."""

	return self.xmlstream.authenticator.jid


