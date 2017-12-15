#!/bin/bash
REC_DIR='test'
for groupDirName in *; do
    #echo $groupDirName
    for testDirName in "$groupDirName"/*; do
	recDir="$testDirName"/"$REC_DIR"
	if [ -d "$recDir" ]; then
	    echo $recDir
	    rm -R "$recDir"
	fi
    done
done