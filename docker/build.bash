#!/bin/bash

SCRIPT_DIR=$(cd $(dirname $0); pwd)
docker build -t onnxgraphqt $SCRIPT_DIR