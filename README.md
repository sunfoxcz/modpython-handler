## Instalace

Slozka framework se prolinkuje nebo zkopiruje primo do pythoni slozky site-packages.

Samotna aplikace se instaluje do FTP prostoru prisluneho webhostingu a je potreba spravne
nastavit <VirtualHost> na webhostingu.

```
<VirtualHost *:80>

    ServerName example.lan
    DocumentRoot /www/example

    <Directory />
        Sethandler python-program
        PythonHandler framework.handler
        PythonAutoReload On
        PythonDebug On
        SetEnv ServerPath /www/example
    </Directory>

    AliasMatch ^/(css|img|js)/(.*) /www/example/webpub/$1/$2
    <Directory /www/example/webpub>
        Sethandler None
    </Directory>
</VirtualHost>
```
