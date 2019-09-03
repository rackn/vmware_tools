#!/usr/bin/env bash


git checkout -- firewall/stage/descriptor.xml
git checkout -- drpy/stage/descriptor.xml

export TRAVIS_BUILD_DIR=`pwd`
cd drpy
./build.sh $TRAVIS_BUILD_DIR/drpy/stage/payloads/drpy/opt/rackn/drpy
cd $TRAVIS_BUILD_DIR
./build_tools/set_version.sh drpy/stage/descriptor.xml
./build_tools/set_version.sh firewall/stage/descriptor.xml
docker pull lamw/vibauthor
docker run -d --name=vibauthor -v $TRAVIS_BUILD_DIR/drpy/stage:/root/drpy/stage -v $TRAVIS_BUILD_DIR/firewall:/root/firewall lamw/vibauthor tail -f /dev/null
docker exec -it vibauthor /bin/bash -c "cd drpy/ && vibauthor -C -t stage -f"
mkdir -p $TRAVIS_BUILD_DIR/grd/vibs
cp $TRAVIS_BUILD_DIR/drpy/stage/*.vib $TRAVIS_BUILD_DIR/grd/vibs
docker exec -it vibauthor /bin/bash -c "cd firewall/ && vibauthor -C -t stage -f"
cp $TRAVIS_BUILD_DIR/firewall/stage/*.vib $TRAVIS_BUILD_DIR/grd/vibs

