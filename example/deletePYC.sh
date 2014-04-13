#!/bin/bash

for file in `find .|grep -v svn|grep "\.pyc$"`; do
    if [ -f $file ]; then
	rm -rf $file
    fi
done
