#
# This file is a part of 'framework'.
#
# Description:  Common framework utils.
#
# Author:       Richard Riman (ret@space4web.org)
#
# $Id: util.py 87 2008-04-26 10:46:42Z phonkee $
#

def singleton(cls):
    """
    singleton decorator
    """
    instances = {}
    def getInstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    #enddef
    return getInstance
#enddef

def _fixURI(uri):
    if uri != '/' and uri[-1:] == '/': uri = uri[:-1]
    return uri
#enddef

