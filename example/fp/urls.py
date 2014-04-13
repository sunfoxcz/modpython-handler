from framework.request import REQUEST_GET, REQUEST_POST

urlPatterns = (
    (
        r'^(?P<id>[0-9]+)$',                # regularni vyraz
        'main',                             # modul
        'frontpage'                         # metoda
        REQUEST_GET                         # povoleny typ pozadavku
    ),
)


