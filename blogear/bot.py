# bot.py
#
# Pubsub Client Bot - Listens to pubsub events for new blog entries.
#
import time
import datetime
import os
from twisted.python import log
from twisted.internet import defer, task, reactor
from twisted.words.xish import domish, xpath
from wokkel.pubsub import PubSubClient, Item
from wokkel import disco
from twisted.words.protocols.jabber.jid import internJID

from wokkel.xmppim import AvailablePresence
# use cheetah for templating
from Cheetah.Template import Template


class PubSub2Blog(object):
    """ Handles PubSub event items and turns them to formated static files.

    The templates are extremly simple for now and can be changed later.
    """
    queue_interval = 2.0

    def __init__(self, path):
        self.path = path
        self.www_path = path+'/www'
        self.template_path = path+'/templates'
         
        self.atom_queue  = []
        self.index_queue = []

        self.processing_atom  = False
        self.processing_index = False

        ## tasks to process queues
        self.task = task.LoopingCall(self._processQueues)
        self.task.start(self.queue_interval) # run every N seconds


    def _processQueue(self, queue_name, ext='.html'):
        """ Process a queue with the given name. 
        """
        queue = getattr(self, queue_name+'_queue')
        queue_status = getattr(self, 'processing_'+queue_name, False)
        
        if not queue_status and len(queue)>0:
            setattr(self, 'processing_'+queue_name, True)
            id, entry_file_name, entries = queue.pop()
            args = {
                'id': id,
                'entries': entries,
                'updated':str(datetime.datetime.utcnow()),
                    }
            
            html = self.template(queue_name+ext, args)
            file_name = self.www_path+'/' + queue_name + ext
            self._writeFile(file_name, html)

            reactor.callLater(1.0, setattr, self, 'processing_'+queue_name, True)

    def _processQueues(self):
        self._processQueue('atom', '.xml')
        self._processQueue('index')
            

    def template(self, file, vars):
        """ Process a template 
        """
        template = open(self.template_path+'/'+file, 'r').read()
        return str(Template(template, searchList=[vars]))


    def atom2hash(self, elem):
        """ Convert an atom domish element to a dictionary for template processing.
        """
        args = {}
        args['id'] = str(elem.id)
        id, args['idname'] = str(elem.id).split(":",1)
        args['categories'] = []
        cats = domish.generateElementsNamed(elem.children, 'category')
        for cat in cats:
            args['categories'].append(cat['term'])
            
        if elem.content:
            args['content'] = str(elem.content)
        elif elem.title:
            args['content'] = str(elem.title)
            
        if elem.title:
            args['title'] = str(elem.title)
        elif elem.id:
            args['title'] = str(elem.id)
        else:
            args['title'] = 'No Title'
            
        return args


    def _writeFile(self, file_name, html):
        # open up file
        ef = open(file_name, 'w')
        ef.write(html)
        ef.close()
        os.chmod(file_name, 0644)

    def updateEntry(self, blog_id, args):
        """update the entry on disk.
        
        """
        html = self.template('entry.html', args)
        id, file_name = blog_id.split(":", 1)
        file_name = self.www_path+'/archive/' + file_name + ".html"
        self._writeFile(file_name, html)
        

    def updateAtom(self, blog_id, entries):
        """
        """
        id, file_name = blog_id.split(":", 1)
        # push on queue
        self.atom_queue.append((id, file_name, entries))
        

    def updateIndex(self, blog_id, entries):
        """
        """
        id, file_name = blog_id.split(":", 1)
        # push on queue
        self.index_queue.append((id, file_name, entries))
        


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


    @defer.inlineCallbacks
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

            # create entry
            args = self.blog.atom2hash(item.entry)
            self.blog.updateEntry(blog_id, args)
            # grab last 10 items
            ret_items = yield self.items(self.service, self.nodeIdentifier, 10)
            last_items = []
            last_ids   = []
            for ri in ret_items:
                rargs = self.blog.atom2hash(ri.entry)
                
                if rargs['id'] not in last_ids:
                    last_items.append(rargs)
                    last_ids.append(rargs['id'])
            # update index
            self.blog.updateIndex(blog_id, last_items)
            # update atom
            self.blog.updateAtom(blog_id, last_items)


    def getJid(self):
	"""Return the JID the connection is authenticed as."""

	return self.xmlstream.authenticator.jid



