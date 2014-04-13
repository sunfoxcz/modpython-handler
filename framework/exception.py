
from mod_python import apache
#import sys
#import traceback

# ------------------------------------------------------------------------------

# special non-raiseable type used as fallback catcher
UNKNOWN_EXCEPTION = None

# ------------------------------------------------------------------------------

class HttpException(Exception):
    """
        Default base exception for HTTP exceptions.
    """

    def __init__(self, status, message):
        self._status = status
        self._message = message
    #enddef

    def handleRequest(self, context, exc_info):
        req = context.request.getMPRequest()
        req.status = self._status
        req.content_type = "text/plain"
        req.write("%d: %s" % (self._status, self._message))
        return apache.DONE
    #enddef

#endclass

# ------------------------------------------------------------------------------

class HttpNotFound(HttpException):
    """
        Error "404: Not found" default exception handler.
    """

    def __init__(self, uri):
        HttpException.__init__(self, 404, "Not found\n\n'%s'" % uri)
    #enddef

#endclass

# ------------------------------------------------------------------------------

class HttpMethodNotAllowed(HttpException):
    """
        Error "405: Method not allowed" default exception handler.
    """

    def __init__(self, method):
        HttpException.__init__(self, 405, "Method not allowed\n\n'%s'" % method)
    #enddef

#endclass

# ------------------------------------------------------------------------------

class UnauthorizedUserException(HttpException):
    """
        Error "401: Authorization Required" default exception handler
    """
    def __init__(self):
        HttpException.__init__(self, 401, "Authorization Required")
    #enddef

#endclass

# ------------------------------------------------------------------------------

class UnaccessibleUserException(HttpException):
    """
        Error "403: Forbidden" default exception handler
    """

    def __init__(self):
        HttpException.__init__(self, 403, "Forbidden")
    #enddef

#endclass

# ------------------------------------------------------------------------------

class DatabaseNotReachable(HttpException):
    """
        Error "503: Database service not available" default exception handler
    """
    def __init__(self, name):
        HttpException.__init__(self, 503, "Database service ('%s') not available!" % name)
    #enddef
#endclass

# ------------------------------------------------------------------------------

class BackendNotReachable(HttpException):
    """
        Error "503: Backend service not available" default exception handler
    """
    def __init__(self, name):
        HttpException.__init__(self, 503, "Backend service ('%s') not available!" % name)
    #enddef
#endclass

# ------------------------------------------------------------------------------
#class BaseException(Exception):
#    """
#        Base exception class.
#    """
#
#    __errNo     = 500
#    __errMsg    = "Internal server error"
#    __excInfo  = None
#
#    # --------------------------------------------------------------------------
#
#    def __init__(self, errNo = 500, errMsg = "Internal server error", excInfo = None):
#        self.__errNo    = errNo
#        self.__errMsg   = errMsg
#        self.__excInfo = excInfo
#    #enddef
#
#    # --------------------------------------------------------------------------
#
#    def __repr__(self):
#        return self.__str__()
#    #enddef
#
#    # --------------------------------------------------------------------------
#
#    def setRequestStatus(self, context):
#        """
#            Sets status to apache response.
#        """
#        MPRequest = context.request.getMPRequest()
#
#        if self.__errNo == 301:
#            MPRequest.status = apache.HTTP_MOVED_PERMANENTLY
#        elif self.__errNo == 302:
#            MPRequest.status = apache.HTTP_MOVED_TEMPORARILY
#        elif self.__errNo == 401:
#            MPRequest.status = apache.HTTP_UNAUTHORIZED
#        elif self.__errNo == 403:
#            MPRequest.status = apache.HTTP_FORBIDDEN
#        elif self.__errNo == 404:
#            MPRequest.status = apache.HTTP_NOT_FOUND
#        elif self.__errNo == 405:
#            MPRequest.status = apache.HTTP_METHOD_NOT_ALLOWED
#        elif self.__errNo == 500:
#            MPRequest.status = apache.HTTP_INTERNAL_SERVER_ERROR
#        else:
#            MPRequest.status = apache.HTTP_OK
#        #endif
#    #enddef
#
#    # --------------------------------------------------------------------------
#
#    def renderException(self, context):
#        """
#            Renderuje vyjimku. Na vystupu je ocekavana pozadovana finalni
#            reprezentace, typicky HTML.
#        """
#        html = "<html>\n<head>\n<title>%i - %s</title>\n" % (self.__errNo, self.__errMsg)
#        html += "<style>body { cursor: default; font: 10pt sans-serif; }</style></head><body>\n"
#
#        html += "<h3>Error %d</3>\n" % self.__errNo
#        html += "<h4>%s</h4>" % self.__errMsg
#
#        if context.config['debug'] and self.__excInfo is not None:
#            e1, e2, e3 = self.__excInfo
#            html += "<hr /><xmp>Traceback (most recent call last):\n\n"
#            html += "\n".join(traceback.format_stack(e3.tb_frame.f_back)) + "\n"
#            html += "\n".join(traceback.format_tb(e3)) + "\n"
#            html += "\n".join(traceback.format_exception_only(e1, e2))
#            html += "</xmp>"
#        #endif
#
#        html += "</body>\n</html>"
#        return html
#    #enddef
#
##endclass
