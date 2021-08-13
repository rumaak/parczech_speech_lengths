#!/bin/bash

for file in $1/*
do
    bn=$(basename "$file" ".xml")
    mkdir -p $2
    xsltproc scripts/speech_timestamps.xsl "$file" >> "${2}/${bn}.txt"
done

