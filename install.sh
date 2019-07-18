#!/usr/bin/env bash

if [[ -z "$1" ]]; then
    echo "Try again using $0 /some/path"
    exit 1
fi

BUILD_DIR=$1

if [[ ! -d ${BUILD_DIR} ]]; then
    mkdir -p ${BUILD_DIR}
else
    rm -rf ${BUILD_DIR}
    mkdir -p ${BUILD_DIR}
fi

pip=$(which pip)

if [[ -z ${pip} ]]; then
    echo "Unable to locate pip"
    exit 1
fi
version=$(grep version setup.py |sed -E 's/(.*)=(.*)/\2/'|sed -E s,[\',],,g)
python setup.py sdist
cd dist
echo `pwd`
ls -l
if [[ -f drpy-${version}.tar.gz ]]; then
    tar xzvf drpy-${version}.tar.gz
else
    echo "Missing drpy tar ball."
    ls
    exit 1
fi

cd drpy-${version}
${pip} install . -t ${BUILD_DIR}
cd ${BUILD_DIR}/bin
mv agent ${BUILD_DIR}