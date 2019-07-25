#!/usr/bin/env bash

file=$1
path=$(dirname $0)
version=$(./${path}/version.sh|awk '{print $3}')
if [[ ${#version} -gt 35 ]]; then
    version=${version:0:35}
fi

sed -i s,##VERSION##,${version},g ${file}

