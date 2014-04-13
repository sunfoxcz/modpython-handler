#
# This file is a part of 'framework'.
#
# Description:  Mod_python handler.
#
# Author:       Richard Riman (ret@space4web.org)
#
# $Id: handler.py 262 2009-10-01 18:38:09Z mordred $
#

from framework.controller   import Controller
from mod_python             import apache
from time                   import time
import sys

try:
    from dbglog                     import dbg
except:
    import framework.dummy_dbglog   as dbg
#endtry

# ------------------------------------------------------------------------------

def __importHandler(context, handler, extraModules):
    """
        Import handler.
    """

    # check for callable itself
    if callable(handler):
        return handler
    #endif

    # find last dot in handler
    dot = handler.rfind('.')
    if dot < 0:
        context.request.getMPRequest().log_error(
                "Can't find dot in handler name `%s`." % (handler,),
                apache.APLOG_ERROR)
        raise apache.SERVER_RETURN, apache.HTTP_INTERNAL_SERVER_ERROR
    #endif

    # import module
    module = context.controller.importModule(handler[:dot])

    # TODO
    # import extra modules for this module
    #if extraModules:
    #    __importModules(debug, autoreload, serverPath, module, extraModules)
    #endif

    # return module's method
    return getattr(module, handler[dot + 1:])
#enddef

# ------------------------------------------------------------------------------

def handler(request):
    try:
        __t = time()
        __controller = Controller()
        __controller.executionStartTime = __t
        return __controller.dispatch(request)
    except apache.SERVER_RETURN, e:
        # re-raise exception
        dbg.log("Re-raise SERVER_RETURN exceptio.", ERR = 4)
        raise e
    except:
        try:
            exc_info = sys.exc_info()

            config = __controller.context.config

            if isinstance(exc_info[1], exc_info[0]):
                if (config["exceptions"].get(exc_info[0]) or None) is None:
                    # ok, check for handleRequest member and is it callable
                    excHandler = getattr(exc_info[1], "handleRequest", None)
                    if callable(excHandler):
                        # call handler
                        res = excHandler(__controller.context, exc_info)
                        del config
                        return res
                    #endif
                #endif
            #endif

            # try to get handler
            dbg.log("Trying to get an exception handler..", DBG = 3)
            excHandler = config["exceptions"].get(exc_info[0]) or config["exceptions"].get(None)

            del config

            if not excHandler:
                # pass unknown exception, re-raise
                dbg.log("Re-aise unknown exception. (%s)" % (str(exc_info)), ERR = 4)
                raise
            #endif

            # import handler (gets rid of exc_info)
            eh = __importHandler(__controller.context, excHandler[0], excHandler[1])
            if type(eh) == type(Exception) and issubclass(eh, Exception):
                if callable(getattr(eh, "handleRequest", None)):
                    # call handler
                    res = eh.handleRequest(eh(), __controller.context, exc_info)
                    exc_info = None
                    return res
                else:
                    raise
                #endif
            else:
                res = eh(__controller.context, exc_info)
                exc_info = None
                return res
            #endif
        finally:
            del exc_info
        #endtry
    #endtry
#enddef
