
urlPatterns = {
    "/"         : (
        'frontpage' ,   # modul kde sa nachadza urls.py
        ( "lib.exceptions", "libs.layouts" )
    ) ,

    "/admin"    : (
        'admin' ,
        ("lib.exceptions", )
    )
}




