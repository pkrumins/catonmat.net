#!/bin/bash
#

set -f
ext="*.py *.html"
for e in $ext; do
    find /home/pkrumins/catonmat/catonmat -name $e | xargs grep -i "TODO"
done

