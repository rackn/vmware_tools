#!/usr/bin/env bash


git checkout -- firewall/stage/descriptor.xml
git checkout -- drpy/stage/descriptor.xml

export TRAVIS_BUILD_DIR=`pwd`
cd drpy
./build.sh $TRAVIS_BUILD_DIR/drpy/stage/payloads/drpy/opt/rackn/drpy
cp -a $TRAVIS_BUILD_DIR/drpy/etc $TRAVIS_BUILD_DIR/drpy/stage/payloads/drpy/
cd $TRAVIS_BUILD_DIR
./build_tools/set_version.sh drpy/stage/descriptor.xml
./build_tools/set_version.sh firewall/stage/descriptor.xml
docker pull lamw/vibauthor
docker run -d --name=vibauthor -v $TRAVIS_BUILD_DIR/drpy/stage:/root/drpy/stage -v $TRAVIS_BUILD_DIR/firewall:/root/firewall lamw/vibauthor tail -f /dev/null
docker exec -it vibauthor /bin/bash -c "cd drpy/ && vibauthor -C -t stage -f -O ./stage/drpy-agent.zip"
mkdir -p $TRAVIS_BUILD_DIR/grd/vibs
mkdir -p $TRAVIS_BUILD_DIR/grd/olb
cp $TRAVIS_BUILD_DIR/drpy/stage/*.vib $TRAVIS_BUILD_DIR/grd/vibs
cp $TRAVIS_BUILD_DIR/drpy/stage/drpy-agent.zip $TRAVIS_BUILD_DIR/grd/olb
docker exec -it vibauthor /bin/bash -c "cd firewall/ && vibauthor -C -t stage -f -O drpy-firewall.zip"
cp $TRAVIS_BUILD_DIR/firewall/stage/*.vib $TRAVIS_BUILD_DIR/grd/vibs
cp $TRAVIS_BUILD_DIR/firewall/*.zip $TRAVIS_BUILD_DIR/grd/olb

# This is too harsh
docker ps -a | awk '{ print $1 }' | xargs docker kill
docker ps -a | awk '{ print $1 }' | xargs docker rm
