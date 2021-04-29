#!/usr/bin/env bash

# script Mike uses to start interactive drpy container

docker run -v $(pwd)/drpy:/media/drpy -it drpydev /bin/bash
