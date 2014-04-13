#
# This file is a part of 'framework'.
#
# Description:  Application context class.
#
# Author:       Richard Riman (ret@space4web.org)
#
# $Id: context.py 262 2009-10-01 18:38:09Z mordred $
#

import types, sys, thread

from mod_python.apache      import import_module
from framework.exception    import *

try:
    from dbglog                     import dbg
except:
    import framework.dummy_dbglog   as dbg
#endtry

class Context(object):

    __lockObj = thread.allocate_lock()
    __instance = None

    def __new__(cls, *args, **kwargs):
        return cls.__getInstance()
    #enddef

    # --------------------------------------------------------------------------

    @classmethod
    def __getInstance(cls, *args, **kargs):
        # Critical section start
        cls.__lockObj.acquire()
        try:
            if cls.__instance is None:
                # Initialize **the unique** instance
                cls.__instance = object.__new__(cls, *args, **kargs)
                cls.__initialize()
            #endif
        finally:
            #  Exit from critical section whatever happens
            cls.__lockObj.release()
        #endtry
        # Critical section end

        return cls.__instance
    #enddef

    # --------------------------------------------------------------------------

    def __init__(self):
        pass
    #enddef

    # --------------------------------------------------------------------------

    @classmethod
    def __initialize(cls):
        # default framework configuration values
        cls.config = {
            'logFile': '/var/log/messages',
            'logMask': 'AI3W2E1F1',

            'acceptLanguages': ['en'],
            'defaultLanguage': 'en',

            'templateRoot': 'templates',
            'tengConfigFile': None,
            'tengDictionaryFile': None,

            'useUser': None,

            'allowHeadWhenGet': True,        # This always allow HEAD request where used GET

            'databases': {
                #'default': {                # database identifier
                #    'host': 'localhost',    # database host (optional, default is localhost)
                #    'port': 3306,           # database port (optional, defalut is 3306)
                #    'user': 'root',         # user name (needed)
                #    'pass': '',             # user password (needed)
                #    'name': 'framework'     # database name (needed)
                #}
            },

            'backends': {
                #"default": {                                        # backend identifier
                #    "url"           : "http://localhost:2400/RPC2"  # backend url (needed)
                #    "readTimeout"   : 1000,                         # backend read timeout (optinal, defalut is 1000)
                #    "writeTimeout"  : 1000,                         # backend write timeout (optinal, defalut is 1000)
                #    "connectTimeout": 1000,                         # backend connect timeout (optinal, defalut is 1000)
                #}
            },

            'exceptions': {
                # exception handlers
            },

            'permissions': {
                "user":         0
            }
        }

        cls.request = None
        cls.session = None
        cls.controller = None
        cls.user = None
    #enddef

    # --------------------------------------------------------------------------

    def getDatabase(self, database = 'default'):
        if database in self.config['databases']:
            db = self.config['databases'][database]['_connection']
            if not db: raise DatabaseNotReachable(database)
            return db
        else:
            raise BaseException(500, "Database `%s` isn't known." % database)
    #enddef

    # --------------------------------------------------------------------------

    def getBackend(self, backend = 'default'):
        if backend in self.config['backends']:
            return self.config['backends'][backend]['_proxy']
        else:
            raise BaseException(500, "Backend `%s` isn't known." % backend)
    #enddef

    # --------------------------------------------------------------------------

    def getPresenter(self, presenter = None):

        if self.config['templateRoot'].startswith('/'):
            templateRoot = self.config['templateRoot']
        else:
            templateRoot = self.config['serverPath'] + '/' + self.config['templateRoot']
        #endif

        if 'presenter' in self.config:
            path = self.config['presenter'].split('.')
            className = path[-1]

            presenterMod = self.controller.importModule(self.config['presenter'])

            # pokusime se natahnout custom presenter
            try:
                presenterClass = getattr(presenterMod, className)
                return presenterClass(self, templateRoot)
            except:
                raise BaseException(500, "Can't instantiate `%s` class." % className)
            #endtry
        else:
            presenterMod = self.controller.importModule('framework.presenter')
            presenterObj = getattr(presenterMod, 'Presenter')
            return apply(presenterObj, (self, templateRoot))
        #endif
    #enddef

    # --------------------------------------------------------------------------

    def getPermissionId(self, permission):
        """
            Vrati cislo opravenia z configu
        """
        if 'permissions' in self.config:
            return self.config['permissions'][permission]
        else:
            return False
        #endif
    #enddef

#endclass
