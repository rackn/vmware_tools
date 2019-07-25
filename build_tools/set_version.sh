#!/usr/bin/env bash

file=$1
path=$(dirname $0)
source ${path}/version.sh

if [[ ${#version} -gt 35 ]]; then
    version=${version:0:35}
fi

echo ${version}

#sed -i s,##VERSION##,${version},g ${file}

