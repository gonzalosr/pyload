# -*- coding: utf-8 -*-

"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License,
    or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <http://www.gnu.org/licenses/>.
    
    @author: RaNaN, spoob, mkaay
"""

import logging
import re
from os.path import exists
from os.path import join

from time import time
from time import sleep

import sys
from os.path import exists

from os import makedirs


def dec(func):
    def new(*args):
	if args[0].pyfile.abort:
	    raise Abort
	return func(*args)
    return new

class Abort(Exception):
    """ raised when aborted """
    
class Fail(Exception):
    """ raised when failed """
    
class Reconnect(Exception):
    """ raised when reconnected """
    
class Retry(Exception):
    """ raised when start again from beginning """

class Plugin(object):
    __name__ = "Plugin"
    __version__ = "0.4"
    __pattern__ = None
    __type__ = "hoster"
    __description__ = """Base Plugin"""
    __author_name__ = ("RaNaN", "spoob", "mkaay")
    __author_mail__ = ("RaNaN@pyload.org", "spoob@pyload.org", "mkaay@mkaay.de")
    
    def __new__(cls, *args, **kws):
	for f in dir(cls):
	    if not f.startswith("_") and f not in ("checksum"):
		setattr(cls, f, dec(getattr(cls, f)) )
	
        o = super(cls.__class__, cls).__new__(cls)
	#wrap decorator around every method			
	return o
    
    def __init__(self, pyfile):
        self.config = pyfile.m.core.config
        
        self.req = pyfile.m.core.requestFactory.getRequest(self.__name__)
    
        self.wantReconnect = False
        self.multiDL = True
        
        self.waitUntil = 0 # time() + wait in seconds

        self.premium = False
        
        self.ocr = None  # captcha reader instance
        self.account = pyfile.m.core.accountManager.getAccount(self.__name__) # account handler instance
	self.req = pyfile.m.core.requestFactory.getRequest(self.__name__, self.account)
        
        self.log = logging.getLogger("log")
        
        self.pyfile = pyfile
        self.thread = None # holds thread in future
	
    def __call__(self):
	return self.__name__
        
    def preprocessing(self, thread):
        """ handles important things to do before starting """
        self.thread = thread
	
	if not self.account:
	    self.req.clearCookies()
	
        return self.process(self.pyfile)

    #----------------------------------------------------------------------
    def process(self, pyfile):
        """the 'main' method of every plugin"""
        raise NotImplementedError
    
    
    def checksum(self, local_file=None):
        """
        return codes:
        0  - checksum ok
        1  - checksum wrong
        5  - can't get checksum
        10 - not implemented
        20 - unknown error
        """
        #@TODO checksum check hook
        
        return (True, 10)
    

    def setConf(self, option, value):
        """ sets a config value """
        self.config.setPlugin(self.__name__, option, value)

    def removeConf(self, option):
        """ removes a config value """
        raise NotImplementedError

    def getConf(self, option):
        """ gets a config value """
        return self.config.getPlugin(self.__name__, option)
    
    
    def setWait(self, seconds):
        """ set the wait time to specified seconds """
        self.waitUntil = time() + int(seconds)

    def wait():
        """ waits the time previously set """
        pass
    
    def fail(self, reason):
        """ fail and give reason """
        raise Fail(reason)
    
    def offline(self):
	""" fail and indicate file is offline """
	raise Fail("offline")
    
    def retry(self):
        """ begin again from the beginning """
        raise Retry
    
    def askCaptcha(self, url):
        """ loads the catpcha and decrypt it or ask the user for input """
        pass
      
    def waitForCaptcha(self, captchaData, imgType):
        captchaManager = self.parent.core.captchaManager
        task = captchaManager.newTask(self)
        task.setCaptcha(captchaData, imgType)
        task.setWaiting()
        while not task.getStatus() == "done":
            if not self.parent.core.isGUIConnected():
                task.removeTask()
                raise CaptchaError
            sleep(1)
        result = task.getResult()
        task.removeTask()
        return result

    def load(self, url, get={}, post={}, ref=True, cookies=True, just_header=False):
        """ returns the content loaded """
        return self.req.load(url, get, post, ref, cookies, just_header)
        
    def download(self, url, get={}, post={}, ref=True, cookies=True):
        """ downloads the url content to disk """
        download_folder = self.config['general']['download_folder']
	
	location = join(download_folder, self.pyfile.package().folder.decode(sys.getfilesystemencoding()))
	
	if not exists(location): 
	    makedirs(location)
        	        
	newname = self.req.download(url, self.pyfile.name, location, get, post, ref, cookies)
        
        if newname:
	    self.pyfile.name = newname