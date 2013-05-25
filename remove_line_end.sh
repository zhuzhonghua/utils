#!/bin/sh

FILES=`find . -type f`

for f in $FILES
do
	sed 's/\r//g' $f > temp.$$
	mv temp.$$ $f
done