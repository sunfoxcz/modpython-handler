#
# This file is a part of 'framework'.
#
# Description:  Request wrapper class.
#
# Author:       Richard Riman (ret@space4web.org)
#
# $Id: request.py 262 2009-10-01 18:38:09Z mordred $
#

from mod_python.util    import FieldStorage, Field

# ------------------------------------------------------------------------------

REQUEST_GET  = 1
REQUEST_POST = 2
REQUEST_HEAD = 4

# ------------------------------------------------------------------------------

class Request(FieldStorage):
    """
        class Request
        @param request - mp_request
    """

    def __init__(self, request):
        FieldStorage.__init__(self, request, keep_blank_values = True)

        self._request           = None
        self._request           = request
    #enddef

    # --------------------------------------------------------------------------

    def getMPRequest(self):
        return self._request
    #enddef

    # --------------------------------------------------------------------------

    def noCache(self):
        self._request.headers_out.add("Cache-Control", "no-cache")
        self._request.headers_out.add("Pragma", "no-cache")
        self._request.headers_out.add("Expires", "-1")
    #enddef

    # --------------------------------------------------------------------------

    def sendFile(self, filename):
        self._request.headers_out.add("Content-Disposition", "attachment; filename=" + filename)
        self._request.headers_out.add("Content-Description", "File Transfer")
        self._request.headers_out.add("Content-Type", "application/force-download")
        self._request.headers_out.add("Content-Type", "application/octet-stream")
        self._request.headers_out.add("Content-Type", "application/download")
    #enddef

    # --------------------------------------------------------------------------

    def sendImage(self, image):
        if image == "JPEG":
            self._request.content_type = "image/jpeg"
        #endif
    #enddef

    # --------------------------------------------------------------------------

    def update(self, fields):
        for k,v in fields.iteritems():
            if hasattr(self, "make_field"):
                file = self.make_field()
                file.write(v)

                field = Field(k, file, "text/plain", {}, None, {})
                self.list.append(field)
            else:
                self.add_field(k, v)
            #endif
        #endfor
    #enddef

    # ---------------------------------------------------------------------------

    def write(self, string):
        self._request.write(str(string))
    #enddef

#endclass
