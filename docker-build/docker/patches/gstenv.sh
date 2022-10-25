#!/bin/sh
export YAMI_ROOT_DIR="/root/gstreamer"


export VAAPI_PREFIX="${YAMI_ROOT_DIR}/vaapi"
export LIBYAMI_PREFIX="${YAMI_ROOT_DIR}/libyami"
export GST_PREFIX="${YAMI_ROOT_DIR}/gst"
ADD_PKG_CONFIG_PATH="${VAAPI_PREFIX}/lib/pkgconfig/:${LIBYAMI_PREFIX}/lib/pkgconfig/:${GST_PREFIX}/lib/pkgconfig"
ADD_LD_LIBRARY_PATH="${VAAPI_PREFIX}/lib/:${LIBYAMI_PREFIX}/lib/:${GST_PREFIX}/lib"
ADD_PATH="${VAAPI_PREFIX}/bin/:${GST_PREFIX}/bin/"

export GST_PLUGIN_PATH=${GST_PLUGIN_PATH}:/home/vss/projects/gst-video-wall/plugin
source /opt/intel/oneapi/compiler/2021.2.0/env/vars.sh


PLATFORM_ARCH_64=`uname -a | grep x86_64`
if [ -n "$PKG_CONFIG_PATH" ]; then
export PKG_CONFIG_PATH="${ADD_PKG_CONFIG_PATH}:$PKG_CONFIG_PATH"
elif [ -n "$PLATFORM_ARCH_64" ]; then
export PKG_CONFIG_PATH="${ADD_PKG_CONFIG_PATH}:${GST_PREFIX}/lib/x86_64-linux-gnu/pkgconfig:/usr/lib/pkgconfig/:/usr/lib/x86_64-linux-gnu/pkgconfig/"
else
export PKG_CONFIG_PATH="${ADD_PKG_CONFIG_PATH}:${GST_PREFIX}/lib/i386-linux-gnu/pkgconfig:/usr/lib/pkgconfig/:/usr/lib/i386-linux-gnu/pkgconfig/"
fi



export LD_LIBRARY_PATH="${ADD_LD_LIBRARY_PATH}:${GST_PREFIX}/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}"
export PATH="${ADD_PATH}:$PATH"
export GST_PLUGIN_PATH="${GST_PREFIX}/gstreamer-1.0:${GST_PREFIX}/lib//x86_64-linux-gnu/gstreamer-1.0:${GST_PLUGIN_PATH}"
export LIBVA_DRIVER_NAME="iHD"
export GST_VAAPI_ALL_DRIVERS="1"



echo "*======================current configuration============================="
echo "* VAAPI_PREFIX: $VAAPI_PREFIX"
echo "* GST_PREFIX: $GST_PREFIX"
echo "* LIBYAMI_PREFIX: ${LIBYAMI_PREFIX}"
echo "* LD_LIBRARY_PATH: ${LD_LIBRARY_PATH}"
echo "* PATH: $PATH"
echo "* PKG_CONFIG: $PKG_CONFIG_PATH"
echo "*========================================================================="



echo "* vaapi: git clean -dxf && ./autogen.sh --prefix=\$VAAPI_PREFIX && make -j8 && make install"
echo "* gstreamer: git clean -dxf && ./autogen.sh --prefix=\$GST_PREFIX && make -j8 && make install"
echo "* ffmpeg: ./configure --prefix=\$VAAPI_PREFIX && make -j8 && make install"
echo "* libyami: git clean -dxf && ./autogen.sh --prefix=\$LIBYAMI_PREFIX --enable-tests --enable-tests-gles && make -j8 && make install"
