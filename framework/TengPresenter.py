
import                      os, sys
import                      framework.exception

from time                   import time
from teng                   import Teng

#from framework.exception    import HttpException

try:
    from dbglog                     import dbg
except:
    import framework.dummy_dbglog   as dbg
#endtry

# ------------------------------------------------------------------------------

class TengPresenter(object):
    """
        Presenter class for rendering pages/templates by teng engine.
    """

    def __init__(self, context, templateRoot):
        self.context        = context
        self.templateRoot   = templateRoot
        self.template       = None
        self.tengDataRoot   = None
        self.tengEngine     = Teng(root = self.templateRoot)
    #enddef

    # --------------------------------------------------------------------------

    def preRenderCheck(self):
        config = "/".join((self.templateRoot, self.context.config["tengConfigFile"]))
        dictionary = self.context.config["tengDictionaryFile"].rsplit(".", 2)
        dictionary.insert(1, self.context.session["language"])
        dictionary = ".".join(dictionary)
        dictionary = "/".join((self.templateRoot, dictionary))
        template = "/".join((self.templateRoot, self.template))

        if not os.path.exists(config):
            msg = "Missing config/dictionary file `%s`." % config
            dbg.log(msg, ERR = 4)
            raise Exception(msg, 500)
        elif not os.path.exists(dictionary):
            msg = "Missing dictionary file `%s`." % dictionary
            dbg.log(msg, ERR = 4)
            raise Exception(msg, 500)
        elif not os.path.exists(template):
            msg = "Missing template file `%s`." % template
            dbg.log(msg, ERR = 4)
            raise Exception(msg, 500)
        #endif
    #enddef

    # --------------------------------------------------------------------------

    def renderPage(self, data, template, contentType = "text/html"):
        """
            Render page using specified template.
        """
        self.template = template

        self.preRenderCheck()

        if context.config["debug"]:
            __timeLen = time() - self.context.controller.executionStartTime
            data.update({
                "debug": {
                    "executionTime": "%.10f" % __timeLen
                }
            })
        #endif

        self.context.request.getMPRequest().content_type = contentType

        result = self.tengEngine.generatePage(templateFilename = template,
                                              dictionaryFilename = self.context.config["tengDictionaryFile"],
                                              language = self.context.session["language"],
                                              configFilename = self.context.config["tengConfigFile"],
                                              contentType = contentType,
                                              data = data,
                                              encoding = "utf-8")

        # zalogujeme teng chyby (ak nejake su)
        if result["status"]:
            msg = []
            msg.append("Teng Warning: Status: %d" % result["status"])
            for k, v in enumerate(result["errorLog"]):
                msg.append("""%d. Level: %d, Filename: `%s`, Line: %d, Column: %d, Message: `%s`"""
                           % (k + 1, v["level"], v["filename"], v["line"], v["column"], v["message"]))
            #endfor
            dbg.log("\n".join(msg), WARN = 2)
            del msg
        #endif

        return result["output"]
    #enddef

    # --------------------------------------------------------------------------

    def dictLookup(self, key):
        """
            Translate dictionary key to real phrase.
        """
        return self.tengEngine.dictionaryLookup(self.context.config["tengDictionaryFile"],
                                                self.context.session["language"], key)
    #enddef

#endclass
