#
# This file is a part of 'framework'.
#
# Description:  Controller class.
#
# Author:       Richard Riman (ret@space4web.org)
#
# $Id: controller.py 264 2009-11-11 09:43:44Z mordred $
#

import                      sys, os, re, types
import                      framework.exception

from mod_python             import apache
from mod_python.apache      import import_module
from mod_python.Session     import Session
from mod_python.util        import redirect
from framework.context      import Context
from framework.request      import Request, REQUEST_GET, REQUEST_POST, REQUEST_HEAD
from framework.util         import _fixURI
from types                  import DictType

try:
    from dbglog                     import dbg
except:
    import framework.dummy_dbglog   as dbg
#endtry

# ------------------------------------------------------------------------------

class Controller(object):

    def __init__(self):
        self.context            = None
        self.actualModule       = None
        self.actualModuleScript = None
        self.actualAction       = None
    #enddef

    # --------------------------------------------------------------------------

    def dispatch(self, request):
        request.content_type = "text/html"

        self.initialize(request)

        if request.method == "GET":
            self.context.request.method = REQUEST_GET
        elif request.method == "POST":
            self.context.request.method = REQUEST_POST
        elif request.method == "HEAD":
            self.context.request.method = REQUEST_HEAD
        #endif

        # get top-level url pattern
        uri = _fixURI(request.uri)

        #lng = re.search(r'^([a-z]{2,2})/', uri)
        #if lng:
        #    if lng.group(1) in self.context.config["acceptLanguages"]:
        #        self.context.request.acceptLanguage = lng.group(1)
        #    else:
        #        self.context.request.acceptLanguage = self.context.config["defaultLanguage"]
        #    #endif
        #
        #    self.context.session["acceptLanguage"] = self.context.request.acceptLanguage
        #
        #    uri = "/".join(uri.split("/")[1:])
        #    if not uri:
        #        uri = "/"
        #    #endif
        ##endif

        # get module with top-level urls
        urls = self.importModule("urls")

        if len(urls.urlPatterns) == 1 and "/" in urls.urlPatterns:
            dbg.log("One module mode, only pattern `/` is defined.", INFO = 4)
            pattern = "/"
            residueURI = uri
        else:
            # zistime ci je v urls pattern odpovedajuci URI
            l = 0
            pattern = None
            for pat, value in urls.urlPatterns.iteritems():
                # pattern "/" musi sedet presne, je-li definovan vice nez jeden pattern
                if pat == "/" and uri != "/" and len(urls.urlPatterns) > 1: continue

                pl = len(pat)
                if request.uri.startswith(pat) and pl > l:
                    pattern = pat
                    l = pl
                #endif
            else:
                if pattern is None:
                    dbg.log("HTTP 404: Not found (`%s`)", uri, ERR = 3)
                    raise framework.exception.HttpNotFound(uri)
                #endif
                residueURI = uri[l:]
            #endfor
        #endif

        # nazev subUrls modulu
        urlsModuleName = ".".join((urls.urlPatterns[pattern][0], "urls"))

        # loads url's target module
        targetURLModule = self.importModule(urlsModuleName)

        backref = None
        for pInfo in targetURLModule.urlPatterns:
            m = re.search(pInfo[0], residueURI)
            if m is None:
                continue
            else:
                module = pInfo[1]
                method = pInfo[2]
                allowedMethod = pInfo[3]
                if allowedMethod & REQUEST_GET and self.context.config['allowHeadWhenGet']:
                    allowedMethod |= REQUEST_HEAD
                #endif
                if len(pInfo) == 5 and type(pInfo[4]) == DictType:
                    fakeArguments = pInfo[4]
                else:
                    fakeArguments = {}
                #endif
                backref = m.groupdict()
                actualSubUrl = pInfo[:]
                break
            #endif
        else:
            if backref is None:
                dbg.log("HTTP 404: Not found (`%s`)", uri, ERR = 3)
                raise framework.exception.HttpNotFound(uri)
            #endif
        #endfor

        # test ci bola stranka poslana spravnou metodou
        if not allowedMethod & self.context.request.method:
            dbg.log("HTTP 405: Method not allowed (`%s`)", request.method, ERR = 3)
            raise framework.exception.HttpMethodNotAllowed(request.method)
        #endif

        self.actualModule = urls.urlPatterns[pattern][0]
        self.actualModuleScript = ".".join((urls.urlPatterns[pattern][0],
                                            actualSubUrl[1]))
        self.actualAction = actualSubUrl[2]

        if len(urls.urlPatterns[pattern]) == 3:
            self.context.request.update(urls.urlPatterns[pattern][2])
        #endif

        # pridame do requestu hodnoty vyparsovane z urls
        self.context.request.update(backref)

        # pridame do requestu fake z urls
        self.context.request.update(fakeArguments)

        actionMod = self.importModule(self.actualModuleScript)
        setattr(actionMod, "context", self.context)

        self._importModules(actionMod, urls.urlPatterns[pattern][1])

        try:
            actionFunction = getattr(actionMod, self.actualAction)
        except:
            dbg.log("In module `%s` isn't defined action `%s`.",
                    (self.actualModuleScript, self.actualAction),
                    ERR = 4)
            raise
        #endtry

        result = apply(actionFunction)

        self.context.session.save()

        request.write(str(result))

        self.cleanup()

        return apache.OK
    #enddef

    # --------------------------------------------------------------------------

    def initialize(self, request):
        self.context = Context()

        # get settings
        config = request.get_config()

        self.context.config["debug"] = int(config.get("PythonDebug", 0))
        self.context.config["autoreload"] = int(config.get("PythonAutoReload", 1))

        os.environ.update(request.subprocess_env)

        try:
            self.context.config["serverPath"] = os.environ["ServerPath"]
        except KeyError:
            raise EnvironmentError, "Environment variable `ServerPath` is undefined."
        #endtry

        if not self.context.config["serverPath"] in sys.path:
            sys.path.insert(0, self.context.config["serverPath"])
        #endif

        self.context.controller = self
        self.context.request = Request(request)
        self.context.session = Session(request)

        if "__ns__" not in self.context.session:
            self.context.session["__ns__"] = {}
        #endif

        configMod = self.importModule("config")

        if not isinstance(configMod, types.ModuleType):
            raise
        #endif

        # override default configuration values with config
        for k, v in configMod.__dict__.iteritems():
            if not k.startswith("_"):
                self.context.config[k] = v
            #endif
        #endfor

        # initialize logging
        appDir = self.context.config["serverPath"]
        if self.context.config["logFile"].startswith("/"):
            dbg.logFile(self.context.config["logFile"])
        else:
            dbg.logFile("/".join((appDir, self.context.config["logFile"])))
        #endif
        dbg.logMask(self.context.config["logMask"])

        if self.context.config["useUser"]:
            uMod = self.importModule("framework.user")
            self.context.user = uMod.User()
            dbg.log("Initializing User handler.", INFO = 2)
        #endif

        # languages support
        dbg.log("Inicializuji podporu i18n..", DBG = 3)
        if "language" not in self.context.session:
            dbg.log("V session zatim neni jazyk nastaven..", DBG = 3)
            if "Accept-Language" in request.headers_in:
                # set language from browser setting
                dbg.log("Z prohlizece mame jazykovou hlavicku `%s`",
                        request.headers_in["Accept-Language"],
                        DBG = 3)
                for lng in request.headers_in["Accept-Language"].split(","):
                    l = lng.split(";")[0]
                    if l in self.context.config["acceptLanguages"]:
                        self.context.session["language"] = l
                        dbg.log("Nalezen akceptovatelny jazyk `%s`.", l, DBG = 3)
                        break
                    #endif
                else:
                    dbg.log("Nenalezen akceptovatelny jazyk, volim default.", DBG = 3)
                    self.context.session["language"] = self.context.config["defaultLanguage"]
                #endfor
            else:
                dbg.log("Prohlizec neposila jazykovou hlavicku, volim default.", DBG = 3)
                self.context.session["language"] = self.context.config["defaultLanguage"]
            #endif
        #endif
        dbg.log("Zvoleny jazky: `%s`.", self.context.session["language"], DBG = 3)

        # databases?
        if self.context.config["databases"]:
            SQLMod = self.importModule("MySQLdb")
            SQLExceptions = self.importModule("_mysql_exceptions")
            for k, v in self.context.config["databases"].iteritems():

                if "host" not in v:
                    v["host"] = "localhost"
                #endif
                if "port" not in v:
                    v["port"] = 3306
                #endif
                if "charset" not in v:
                    v["charset"] = "utf8"
                #endif
                if "timeout" not in v:
                    v["timeout"] = 1
                #endif

                try:
                    self.context.config["databases"][k]["_connection"] = \
                            SQLMod.connect(host             = v["host"],
                                           port             = v["port"],
                                           user             = v["user"],
                                           passwd           = v["pass"],
                                           db               = v["name"],
                                           charset          = v["charset"],
                                           connect_timeout  = v["timeout"])
                except SQLExceptions.OperationalError, e:
                    if e[0] == 2003:
                        dbg.log("Can't connect to database server `%s`" % (k), WARN = 3)
                    else:
                        dbg.log(e[1], ERR = 3)
                        # re-raise
                        raise
                    #endif
                    self.context.config['databases'][k]['_connection'] = None
                #endtry
            #endfor
        #endif

        # backends?
        if self.context.config["backends"]:
            frpc = self.importModule("fastrpc")
            for k, v in self.context.config["backends"].iteritems():
                if "url" not in v:
                    raise Exception("Backend url for `%s` is unconfigured.", 500)
                #endif
                if "readTimeout" not in v:
                    v["readTimeout"] = 1000
                #endif
                if "writeTimeout" not in v:
                    v["writeTimeout"] = 1000
                #endif
                if "connectTimeout" not in v:
                    v["connectTimeout"] = 1000
                #endif

                self.context.config["backends"][k]["_proxy"] = \
                        frpc.ServerProxy(v["url"],
                                         readTimeout = v["readTimeout"],
                                         writeTimeout = v["writeTimeout"],
                                         connectTimeout = v["connectTimeout"],
                                         useBinary = frpc.ON_SUPPORT_ON_KEEP_ALIVE)
                if "checkMethod" in v:
                    try:
                        proxy = self.context.config["backends"][k]["_proxy"]
                        checkMethod = getattr(proxy, v["checkMethod"], None)
                        res = checkMethod()
                        self.context.config["backends"][k]["_status"] = res["status"]
                        if "diagnostics" in res:
                            self.context.config["backends"][k]["_diagnostics"] = res["diagnostics"]
                        #endif
                    except:
                        dbg.log("Backend `%s`: check method `%s` doesn't exists.",
                                (k, v["checkMethod"]), ERR = 4)
                    #endtry
                else:
                    dbg.log("Backend `%s` can't be checked, checkMethod not defined.", k, WARN = 3)
                #endif
            #endfor
        #endif

    #enddef

    # --------------------------------------------------------------------------

    def importModule(self, module):
        try:
            config = self.context.config
            mod = import_module(module,
                                autoreload  = config["autoreload"],
                                log         = config["debug"])
            dbg.log("Module `%s` successfully imported.", module, INFO = 2)
            mod.context = self.context
            return mod
        except ImportError, e:
            msg = "Module `%s` import failed." % module
            dbg.log(msg, FATAL = 3)
            raise
        except OSError, e:
            msg = "Module `%s` import failed, module not exists." % module
            dbg.log(msg, FATAL = 3)
            raise
        except:
            msg = "Module `%s` isn't imported, higher level error occurred." % module
            dbg.log(msg, FATAL = 4)
            raise
        #endtry
    #enddef

    # --------------------------------------------------------------------------

    def redirect(self, uri):
        """
        Redirect application to specified URI.
        """
        self.context.session.save()

        redirect(self.context.request.getMPRequest(), uri)
    #enddef

    # --------------------------------------------------------------------------

    def cleanup(self):
        """
        Close connections after process request, because it
        creates too much connections to DB server
        """

        dbg.log("Closing connections to database.", INFO = 2)
        for database in self.context.config['databases']:
            db = self.context.config['databases'][database]['_connection']
            if db:
                db.close()
            #endif
        #endfor
    #enddef

    # --------------------------------------------------------------------------

    def _importModules(self, actionModule, modules):
        imported = []
        for module in modules:
            try:
                imod = self.importModule(module)
            except:
                dbg.log("Module `%s` not found.", module, FATAL = 3)
                raise
            #endtry
            setattr(imod, "context", self.context)
            imported.append((module.replace(".", "_"), imod))
        #endfor

        # remember each module in the actionModule and the other modules
        for name, module in imported:
            setattr(actionModule, name, module)
            for otherName, otherModule in imported:
                # check for self-reference
                if module != otherModule:
                    dbg.log("Pridavam modul %s do modulu %s", (otherName, module), DBG = 3)
                    setattr(module, otherName, otherModule)
                #endif
            #endfor
        #endfor
    #enddef

#endclass
