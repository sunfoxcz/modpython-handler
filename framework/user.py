#
# This file is a part of 'framework'.
#
# Description:  Class for hold user data.
#
# Author:       Richard Riman <richard.riman@sunfox.cz>
#
# $Id: user.py 218 2009-03-08 20:45:41Z ret $
#

from copy       import deepcopy

from framework.context      import Context
import framework.exception

try:
    from dbglog                     import dbg
except:
    import framework.dummy_dbglog   as dbg
#endtry

# --- SECURITY DECORATORs ------------------------------------------------------

context = Context()

# USAGE @secure
class secure(object):

    def __init__(self, function):
        self.fnc = function
    #enddef

    def __call__(self, *args):
        if not context.user.isAuthenticated():
            raise framework.exception.UnauthorizedUserException()
        #endif

        return self.fnc(*args)
    #enddef

#endclass

# USAGE @permissions( [ permission1, permission2, ...] )
class permissions(object):

    def __init__(self, permissions):
        from types import ListType, StringType, IntType

        if type(permissions) is ListType:
            self.permissions = permissions
        elif type(permissions) is StringType or type(permissions) is IntType:
            self.permissions = [ permissions ]
        else:
            self.permissions = []
        #endif
    #enddef

    def __call__(self, function):
        def checked(*args):
            allowed = False
            for permission in self.permissions:
                if context.user.hasPermission(permission):
                    allowed = True
                #endif
            #endfor
            if not allowed:
                raise framework.exception.UnaccessibleUserException()
            #endif

            return function(*args)
        #enddef

        return checked
    #enddef

#endclass

# ------------------------------------------------------------------------------

class User(object):
    """
        Zajistuje manipulaci s uzivatelskymi promennymi, jmennymi prostory
        pro tyto promenne a taky zajistuje uzivatelska zabezpeceni
        (stav prihlaseni a uzivatelska opravneni).
    """

    def __init__(self):
        self._attributeNamespace    = 'user/attributes'
        self._authNamespace         = 'user/authenticated'
        self._permissionNamespace   = 'user/permissions'
        self.context                = context

        if self._authNamespace not in self.context.session:
            self.context.session[self._attributeNamespace] = {'default': {}}
            self.context.session[self._authNamespace] = {'authenticated': False}
            self.context.session[self._permissionNamespace] = {'permissions': []}
        #endif
    #enddef

    # --------------------------------------------------------------------------

    def addPermission(self, permission):
        """
            Prida uzivateli zadane opravneni (permission).
        """
        from types import StringType, IntType, LongType

        userNamespace = self.context.session[self._permissionNamespace]

        if (type(permission) is IntType) or (type(permission) is LongType):
            if permission not in userNamespace['permissions']:
                userNamespace['permissions'].append(permission)
            #endif
        elif type(permission) is StringType:
            permission = self.context.getPermissionId(permission)
            if permission not in userNamespace['permissions']:
                userNamespace['permissions'].append(permission)
            #endif
        else:
            return False
        #endif
    #enddef

    # --------------------------------------------------------------------------

    def clearPermissions(self):
        """
            Zrusi uzivateli vsechna opravneni pro aktualni session.
        """
        self.context.session[self._permissionNamespace]['permissions'] = []
    #enddef

    # --------------------------------------------------------------------------

    def getAttribute(self, name, namespace = 'default'):
        """
            Vrati hodnotu zadaneho atributu z prislusneho namespace.
        """
        #assert type(name) is str
        #assert type(namespace) is str

        attributes = self.context.session[self._attributeNamespace]
        if attributes.has_key(namespace) and attributes[namespace].has_key(name):
            return attributes[namespace][name]
        else:
            return None
        #endif
    #enddef

    # --------------------------------------------------------------------------

    def getAttributeNames(self, namespace = 'default'):
        """
            Vrati seznam atributu v prislusnem namespace.
        """
        #assert type(namespace) is str

        if self.context.session[self._attributeNamespace].has_key(namespace):
            return self.context.session[self._attributeNamespace][namespace].keys()
        #endif

        return None
    #enddef

    # --------------------------------------------------------------------------

    def getAttributeNamespace(self, namespace = 'default'):
        """
            Vrati uvedeny namespace, pokud existuje, jinak vrati None.
        """
        #assert type(namespace) is str

        session = self.context.session

        if session[self._attributeNamespace].has_key(namespace):
            return session[self._attributeNamespace][namespace]
        #enddef

        return None
    #enddef

    # --------------------------------------------------------------------------

    def getAttributeNamespaces(self):
        """
            Vrati korenovy namespace, tedy vcetne vsech vnorenych.
        """
        return self.context.session[self._attributeNamespace]
    #enddef

    # --------------------------------------------------------------------------

    def hasAttribute(self, name, namespace = 'default'):
        """
            Vrati True, pokud dany namespace obsahuje uvedeny atribut, jinak False.
        """
        #assert type(name) is str
        #assert type(namespace) is str

        userNamespace = self.context.session[self._attributeNamespace]

        if userNamespace.has_key(namespace):
            return userNamespace[namespace].has_key(name)
        #enddef

        return False
    #enddef

    # --------------------------------------------------------------------------

    def hasAttributeNamespace(self, namespace):
        """
            Vrati true, pokud existuje uvedeny namespace, jinak False.
        """
        #assert type(namespace) is str

        return self.context.session[self._attributeNamespace].has_key(namespace)
    #enddef

    # --------------------------------------------------------------------------

    def hasPermission(self, permission):
        """
            Overi, zda uzivatel disponuje prislusnym opravnenim, je-li na vstupu
            retezec. Pokud vstoupi list, ma se za to, ze uzivatel disponuje
            potrebnym opravnenim, shoduje-li se alespon jeden permission.
        """
        from types import StringType, IntType, ListType

        userNamespace = self.context.session[self._permissionNamespace]

        if type(permission) is IntType:
            return permission in userNamespace['permissions']
        elif type(permission) is StringType:
            permission = self.context.getPermissionId(permission)
            return permission in userNamespace['permissions']
        elif type(permission) is ListType:
            hasIt = False
            for permis in permission:
                if type(permis) is IntType and permis in userNamespace['permissions']:
                    hasIt = True
                elif type(permis) is StringType:
                    permis = self.context.getPermissionId(permis)
                    if permis in userNamespace['permissions']:
                        hasIt = True
                    #endif
                #endif
            #endfor
            return hasIt
        else:
            return False
        #endif
    #enddef

    # --------------------------------------------------------------------------

    def isAuthenticated(self):
        """
            Vrati True, pokud je uzivatel prihlasen, jinak False.
        """
        return self.context.session[self._authNamespace]['authenticated']
    #enddef

    # --------------------------------------------------------------------------

    def removeAttribute(self, name, namespace = 'default'):
        """
            Odstrani zadany atribut z prislusneho namespace. Odstranena
            hodnota je vracena jako vysledek, pokud existovala. V opacnem
            pripade vrati None.
        """
        #assert type(name) is str
        #assert type(namespace) is str

        userNamespace = self.context.session[self._attributeNamespace]
        retVal = None

        if userNamespace.has_key(namespace) and userNamespace[namespace].has_key(name):
            retVal = deepcopy(userNamespace[namespace][name])
            del userNamespace[namespace][name]
        #endif

        return retVal
    #enddef

    # --------------------------------------------------------------------------

    def removeAttributeNamespace(self, namespace):
        """
            Odstrani zadany namespace.
        """
        #assert type(namespace) is str

        self.context.session[self._attributeNamespace].discard(namespace)
    #enddef

    # --------------------------------------------------------------------------

    def removePermission(self, permission):
        """
            Odstrani uzivateli pro danou relaci prislusny permission.
        """
        from types import StringType, IntType

        userNamespace = self.context.session[self._permissionNamespace]

        if type(permission) is IntType:
            if permission in userNamespace['permissions']:
                userNamespace['permissions'].remove(permission)
            #endif
        elif type(permission) is StringType:
            permission = self.context.getPermissionId(permission)
            if permission in userNamespace['permissions']:
                userNamespace['permissions'].remove(permission)
            #endif
        else:
            return False
        #endif
    #enddef

    # --------------------------------------------------------------------------

    def setAttribute(self, name, value, namespace = 'default'):
        """
            Nastavi zadany atribut v prislusnem namespace. Pokud zadany namespace
            neexistuje, vytvori jej.
        """
        #assert type(name) is str
        #assert type(namespace) is str

        session = self.context.session

        if not session[self._attributeNamespace].has_key(namespace):
            session[self._attributeNamespace][namespace] = {}
        #endif

        session[self._attributeNamespace][namespace][name] = value
    #enddef

    # --------------------------------------------------------------------------

    def setAttributes(self, attributes, namespace = 'default'):
        """
            Do prislusneho namespace sloucenim prida zadane atributy. Hodnoty
            shodnych klicu jsou nahrazeny, nove jsou pridany a puvodni
            jsou zachovany bez zmeny.
        """
        #assert type(attributes) is dict

        # TODO
    #enddef

    # --------------------------------------------------------------------------

    def setAuthenticated(self, authenticated):
        """
            Nastavi prislusny stav prihlaseni uzivatele. Pri odhlaseni odstrani
            vsechny permissiony uzivatele.
        """
        #assert type(authenticated) is bool

        session = self.context.session

        if authenticated:
            session[self._authNamespace] = {'authenticated': True}
        else:
            session[self._authNamespace] = {'authenticated': False}
            session[self._permissionNamespace] = {'permissions': []}
        #endif
    #enddef

#endclass
