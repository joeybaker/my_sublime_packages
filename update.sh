#!/bin/bash

source ./.subtrees

for remote in `git remote | grep -v origin | tr "\\n" " "`; do
  git subtree pull --prefix Packages/$remote $remote ${!remote} --squash
done;

