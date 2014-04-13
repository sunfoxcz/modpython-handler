
from framework.exceptions import BaseException

class HttpNotFound(BaseException):

    def renderException(self, request):
        return "<h3>chyba 404</h3><h4>Pozadovana stranka neexistuje</h4>"

#endclass
