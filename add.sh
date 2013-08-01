#!/bin/bash

rm -rf Packages/$1
git remote add $1 $2;
git fetch $1
git subtree add --prefix Packages/$1 $1/$3 --squash
