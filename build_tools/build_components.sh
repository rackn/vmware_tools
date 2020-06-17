#!/usr/bin/env bash

# Default settings should not need to be adjusted.
# With the exception of the TARGET_PLATFORM
# and VIB_SIGN_OPTS (example use below commented out)
VIBAUTHOR="/usr/bin/vibauthor"
VIBPUBLISH="/usr/bin/vibpublish"
BUILD_DIR="/root/vibs/build"
BUNDLE_DIR="$BUILD_DIR/component"
TEMP_DIR="$BUILD_DIR/scratch"
VIB_OUT_DIR="$BUILD_DIR/vibs"
#VIB_SIGN_OPTS="--sign --key=/opt/vmware/vibtools/testcerts/vmpartner.key --cert=/opt/vmware/vibtools/testcerts/vmpartner.cert"
VIB_SIGN_OPTS=""
TARGET_PLATFORM="ESXi,7.0.0"
VENDOR="RackN"
VENDOR_CODE="RKN"
################################################
# End Defaults
################################################
VIB_PAYLOAD_VIB_DIR="/root/vibs/firewall/stage"
VMW_VIB_NAME="firewall"
COMPONENT_BASENAME="RackN-DRPY-Firewall"


function show_help {
  cat << EOF

  Usage: ${0##*/} [-h] [ -d VIB_PAYLOAD_VIB_DIR] [-c COMPONENT_BASENAME] [ -v VMW_VIB_NAME]

  VIB_PAYLOAD_VIB_DIR = Path to the staged descriptor.xml
  COMPONENT_BASENAME = Name to give the generated component
  VMW_VIB_NAME = Name to give the outputted vib file

EOF
}

# Start with a clean space.
function clean {
  mkdir -p $VIB_OUT_DIR
  rm -rf $VIB_OUT_DIR/${VMW_VIB_NAME}.vib
  mkdir -p $BUNDLE_DIR
  mkdir -p $TEMP_DIR
  rm -rf $TEMP_DIR/*
  rm -rf $BUNDLE_DIR/*
}

# Build only the vib.
# This is always called, but
# sometimes when building for
# < 7 you only need a vib
function vib_only {
  $VIBAUTHOR -C \
    -t $VIB_PAYLOAD_VIB_DIR \
    -v "$VIB_OUT_DIR/${VMW_VIB_NAME}.vib" $VIB_SIGN_OPTS
}

# Used to build a component for 7.x and newer platforms.
# This can also be used if a customer requests an offline
# bundle/software depot from us.
function build_component {
  $VIBAUTHOR -i -v $VIB_OUT_DIR/${VMW_VIB_NAME}.vib \
                  | egrep -E -w "VIB ID" \
                  | awk '{printf("<vibID>%s</vibID>", $3)}' \
                          > $SCRATCH_DIR/vib-id-list
  if [ -s $SCRATCH_DIR/vib-id-list ]; then
    pat="`cat $SCRATCH_DIR/vib-id-list`";
    sed -i -e "s#<vibID/>#$pat#g" $VIB_BULLETIN_XML;
  fi

  $VIBPUBLISH -f --group=$BUNDLE_DIR/metadata.zip \
              --create-offline-bundle=$BUNDLE_DIR/${COMPONENT_BASENAME}.zip \
              --target=$TARGET_PLATFORM \
              --vendor="$VENDOR" \
              --vendor-code="$VENDOR_CODE" \
              --stage-out-dir=$TEMP_DIR \
              --bulletin=$VIB_BULLETIN_XML \
              --vib-source=$VIB_OUT_DIR/${VMW_VIB_NAME}.vib
}

VIB_ONLY=true

while getopts hv:d:c: opt; do
    case $opt in
        h)
            show_help
            exit 0
            ;;
        v)  VMW_VIB_NAME=$OPTARG
            ;;
        c)  COMPONENT_BASENAME=$OPTARG; VIB_ONLY=false
            ;;
        d)  VIB_PAYLOAD_VIB_DIR=$OPTARG
            ;;
        *)
            show_help >&2
            exit 1
            ;;
    esac
done
if (($# == 0))
then
    echo "No positional arguments specified"
    show_help
    exit;
fi

# Should not need to edit
VIB_BULLETIN_XML="$VIB_PAYLOAD_VIB_DIR/bulletin.xml"

clean
vib_only
if $VIB_ONLY; then
  exit 0;
fi
build_component
exit 0;

