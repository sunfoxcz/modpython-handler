
import os
from mod_python import apache

class Presenter(object):

    def __init__(self, context, templateRoot):
        self.context = context
        self.templateRoot = templateRoot
    #enddef

    def renderPage(self, data, template = '', contentType = 'text/html'):
        if os.path.exists(self.templateRoot + '/' + template):
            self.context.request.getMPRequest().content_type = contentType
            import cStringIO, pprint
            ppbuf = cStringIO.StringIO()
            pp = pprint.PrettyPrinter(indent = 4, stream = ppbuf)
            pp.pprint(data)
            return "<pre>" + ppbuf.getvalue() + "</pre>"
        else:
            raise "Template file `%s` doesn't exists." % template
        #endif
    #enddef

#endclass
