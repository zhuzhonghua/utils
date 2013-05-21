#!/bin/sh

FILES=`find . -name "*.cpp" -o -name "*.h"`

for f in $FILES
do
	sed '/\/\/ c-basic-offset: 8/d' $f | sed '/\/\/ tab-width: 8/d' | sed '/\/\/ indent-tabs-mode: t/d' > temp.$$
	mv temp.$$ $f
done