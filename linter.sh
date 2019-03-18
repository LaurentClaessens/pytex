#!/bin/bash

for f in $(git ls-tree -r master --name-only)
do
    echo "------"
    echo $f
    echo ""
    pycodestyle $f
done
