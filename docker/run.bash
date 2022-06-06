xhost +
XAUTH=/tmp/.docker.xauth
if [ ! -f $XAUTH ]
then
    xauth_list=$(xauth nlist :0 | sed -e 's/^..../ffff/')
    if [ ! -z "$xauth_list" ]
    then
        echo $xauth_list | xauth -f $XAUTH nmerge -
    else
        touch $XAUTH
    fi
    chmod a+r $XAUTH
fi

docker run --rm -it \
        -v=/tmp/.X11-unix:/tmp/.X11-unix:rw \
        -v=${XAUTH}:${XAUTH}:rw \
        -e="XAUTHORITY=${XAUTH}" \
        -e="DISPLAY=${DISPLAY}" \
        -e=TERM=xterm-256color \
        -e=QT_X11_NO_MITSHM=1 \
        onnxgraphqt:latest bash