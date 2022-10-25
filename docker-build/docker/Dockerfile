#FROM amr-registry-pre.caas.intel.com/iotg-wlc/iotg-usecases/ubuntu-custom-2204:latest as base-image
FROM amr-registry-pre.caas.intel.com/iotg-wlc/iotg-usecases/ubuntu-custom-2204@sha256:fe0e6c1439217c7c4e90cf4a4c09c4d647114ea6007b66a96f6d4d885c289a35 as base-image

ENV TZ=Asia
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

ENV http_proxy "http://proxy.png.intel.com:911"
ENV https_proxy "http://proxy.png.intel.com:912"
ENV no_proxy "127.0.0.1,localhost,intel.com,.intel.com"

RUN apt-get update

RUN apt-get install -y --no-install-recommends \
    sudo \
    curl \
    gpg-agent \
    software-properties-common

RUN apt-get install -y --no-install-recommends \
    libigdgmm12 \
    libigdgmm-dev \
    intel-media-va-driver-non-free \
    va-driver-all \
    gir1.2-gst-plugins-bad-1.0 \
    gir1.2-gst-rtsp-server-1.0 \
    gstreamer1.0-alsa \
    gstreamer1.0-gl \
    gstreamer1.0-gtk3 \
    gstreamer1.0-opencv \
    gstreamer1.0-plugins-bad-apps \
    gstreamer1.0-plugins-base-apps \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-pulseaudio \
    gstreamer1.0-qt5 \
    gstreamer1.0-rtsp \
    gstreamer1.0-vaapi \
    gstreamer1.0-wpe \
    libgstreamer-gl1.0-0 \
    libgstreamer-opencv1.0-0 \
    libgstreamer-plugins-bad1.0-0 \
    libgstreamer-plugins-bad1.0-dev \
    libgstreamer-plugins-base1.0-0 \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-good1.0-0 \
    libgstreamer-plugins-good1.0-dev \
    libgstreamer1.0-0 \
    libgstreamer1.0-dev \
    libgstrtspserver-1.0-0 \
    libgstrtspserver-1.0-dev \
    libmfx-dev \
    libmfx-tools \
    libmfx1 \
    libmfx-gen-dev \
    libmfx-gen1.2 \
    libva-dev \
    libva-glx2 \
    libvpl-dev \
    libvpl2 \
    vainfo

FROM base-image as builder

RUN apt-get update

RUN apt-get install -y --no-install-recommends \
    unzip \
    git \
    ninja-build \
    wget \
    bison \
    flex \
    cmake \
    pkg-config \
    autoconf \
    build-essential \
    automake \
    libtool \
    libssl-dev \
    libpciaccess-dev \
    cpio \
    libxcb-randr0-dev \
    python3 \
    python3-pip \
    python-gi-dev

RUN pip3 install meson

# Install DPC++
RUN env -u no_proxy curl -fsSL https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | apt-key add - \
    && env -u no_proxy apt-add-repository "deb https://apt.repos.intel.com/oneapi all main"

# install dpc++ compiler
RUN env -u no_proxy apt-get install -y intel-oneapi-compiler-dpcpp-cpp

RUN apt-add-repository -r "deb https://apt.repos.intel.com/oneapi all main"

WORKDIR /root

# build paho-mqtt3a
RUN git clone https://github.com/eclipse/paho.mqtt.c.git
RUN cd paho.mqtt.c \
    && git checkout 556cd568345e47b70da603edc92f11ff94a6161f \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make -j`nproc` \
    && make install

# build opencv
RUN git clone https://github.com/opencv/opencv.git
WORKDIR /root/opencv
RUN git checkout 4.6.0
RUN mkdir -p build
RUN mkdir -p /root/opencv_release
WORKDIR /root/opencv/build
RUN cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/root/opencv_release ..
RUN make -j`nproc`
RUN make install
COPY docker/patches/opencv_setupvars.sh /root/opencv_release/setupvars.sh

WORKDIR /root
# build openvino
RUN git clone -b 2022.1.0 https://github.com/openvinotoolkit/openvino.git
WORKDIR /root/openvino
RUN git submodule update --init --recursive
COPY docker/patches/0001-ubuntu-22.04.patch /root/openvino/0001-ubuntu-22.04.patch
RUN git apply /root/openvino/0001-ubuntu-22.04.patch
RUN chmod +x ./install_build_dependencies.sh
RUN	./install_build_dependencies.sh
RUN pip install -r ./src/bindings/python/src/compatibility/openvino/requirements-dev.txt
RUN mkdir build
WORKDIR /root/openvino/build
ENV OpenCV_DIR=/root/opencv_release
RUN cmake -DCMAKE_BUILD_TYPE=Release \
    -DENABLE_PYTHON=ON \
    -DENABLE_INTEL_CPU=ON \
    -DENABLE_INTEL_GPU=ON \
    -DTREAT_WARNING_AS_ERROR=OFF \
    -DCMAKE_INSTALL_PREFIX=/opt/intel/openvino ..
RUN make --jobs=$(nproc --all)
RUN make install
WORKDIR /root/openvino
RUN cp -r /root/opencv_release /opt/intel/openvino/opencv
ENV OpenCV_DIR=/opt/intel/openvino/opencv
RUN sed -i 's/MAX_SUPPORTED_PYTHON_VERSION_MINOR="9"/MAX_SUPPORTED_PYTHON_VERSION_MINOR="10"/g' /opt/intel/openvino/setupvars.sh

WORKDIR /root

RUN mkdir -p root/neo
WORKDIR /root/neo

# Intel(R) Graphics Compute Runtime for oneAPI Level Zero and OpenCL(TM) Driver
# https://github.com/intel/compute-runtime/releases 22.31.23852
RUN wget https://github.com/intel/intel-graphics-compiler/releases/download/igc-1.0.11485/intel-igc-core_1.0.11485_amd64.deb
RUN wget https://github.com/intel/intel-graphics-compiler/releases/download/igc-1.0.11485/intel-igc-opencl_1.0.11485_amd64.deb
RUN wget https://github.com/intel/compute-runtime/releases/download/22.31.23852/intel-level-zero-gpu-dbgsym_1.3.23852_amd64.ddeb
RUN wget https://github.com/intel/compute-runtime/releases/download/22.31.23852/intel-level-zero-gpu_1.3.23852_amd64.deb
RUN wget https://github.com/intel/compute-runtime/releases/download/22.31.23852/intel-opencl-icd-dbgsym_22.31.23852_amd64.ddeb
RUN wget https://github.com/intel/compute-runtime/releases/download/22.31.23852/intel-opencl-icd_22.31.23852_amd64.deb


# oneAPI Level Zero Loader v1.8.5
RUN wget https://github.com/oneapi-src/level-zero/releases/download/v1.8.5/level-zero-devel_1.8.5+u18.04_amd64.deb
RUN wget https://github.com/oneapi-src/level-zero/releases/download/v1.8.5/level-zero_1.8.5+u18.04_amd64.deb

RUN dpkg -i *.deb



WORKDIR /root
# Build Dlstreamer
RUN apt install -y python3-virtualenv
RUN python3 -m pip install virtualenv
RUN git clone -b v1.6 https://github.com/dlstreamer/dlstreamer.git
COPY docker/patches/0001-perf-count-for-v1.6.patch /root/dlstreamer/0001-perf-count-for-v1.6.patch
COPY docker/patches/0002-fix-python-videoinfo.patch /root/dlstreamer/0002-fix-python-videoinfo.patch
COPY docker/patches/0001-VAMemory.patch /root/dlstreamer/0001-VAMemory.patch
WORKDIR /root/dlstreamer
RUN git apply 0001-perf-count-for-v1.6.patch
RUN git apply 0002-fix-python-videoinfo.patch
#RUN git apply 0001-VAMemory.patch
#RUN sed -i 's/VA_PROGRESSIVE/0/g' src/vaapi/video_preproc_vaapi/video_preproc_vaapi.cpp
RUN mkdir -p build
WORKDIR /root/dlstreamer/build
RUN virtualenv -p /usr/bin/python3 .env3 --system-site-packages \
    && source .env3/bin/activate \
    && source /opt/intel/oneapi/compiler/latest/env/vars.sh \
    && source /opt/intel/openvino/setupvars.sh \
    && cmake -DCMAKE_INSTALL_PREFIX=/opt/intel/dlstreamer -DTREAT_WARNING_AS_ERROR=OFF -DENABLE_VAAPI=ON -DENABLE_PERF_CAL=ON .. \
    && env -u no_proxy make -j`nproc` \
    && make install
COPY docker/patches/dlstreamer_setupvars.sh /opt/intel/dlstreamer/setupvars.sh

WORKDIR /root

# build bps
RUN --mount=type=secret,id=mynetrc,dst=/root/.netrc git clone -b nvr https://github.com/intel-innersource/applications.iot.workloads.common-lib
RUN cd applications.iot.workloads.common-lib/bps \
   && rm -rf build \
   && mkdir build \
   && cd build \
   && cmake .. \
   && make

# build crypto
RUN git clone --branch release-1.0 https://github.com/RidgeRun/gst-crypto.git
RUN cd ./gst-crypto \
    && ./autogen.sh \
    && ./configure \
    && make -j`nproc`

# download KPI lib
RUN --mount=type=secret,id=mynetrc,dst=/root/.netrc git clone https://github.com/intel-innersource/frameworks.benchmarking.edge-systems.iotg-wkld-common-lib.git
COPY docker/patches/0001-kpi-commonlib.patch /root/frameworks.benchmarking.edge-systems.iotg-wkld-common-lib/
COPY docker/patches/0001-use-topic-name-from-env.patch /root/frameworks.benchmarking.edge-systems.iotg-wkld-common-lib/
RUN cd frameworks.benchmarking.edge-systems.iotg-wkld-common-lib \
    && git checkout cb5e563e4cf4161662528e4ff6c06abc47016849 \
    && git apply 0001-kpi-commonlib.patch \
    && git apply 0001-use-topic-name-from-env.patch

#get cartwheel patch and build libva
RUN git clone https://github.com/intel-media-ci/cartwheel-gstreamer \
    && cd cartwheel-gstreamer \
    && git checkout 0f2cc60a5453037215c01712a8f6671b74e14cad
RUN git clone --recurse-submodules -j8 https://gitlab.freedesktop.org/gstreamer/gstreamer.git \
    && cd gstreamer \
    && git checkout 6f9ae5d7580763b5d18badb76f2166ff0012886a
COPY docker/patches/gstenv.sh /root/gstreamer/gstenv.sh
COPY docker/patches/0001-kmssink-fd-prop.patch /root/gstreamer/
COPY docker/patches/0002-kmssink-dmabuf-modifier.patch /root/gstreamer/
RUN cd gstreamer \
    && git checkout -b mybranch \
    && source gstenv.sh \
    && meson -Dauto_features=disabled -Dbad=enabled -Dgst-plugins-bad:va=enabled -Dvaapi=enabled -Dgstreamer-vaapi:x11=enabled -Dgstreamer-vaapi:drm=enabled -Dgstreamer-vaapi:encoders=enabled -Dgst-plugins-bad:kms=enabled --prefix=$GST_PREFIX build \
    && git apply ../cartwheel-gstreamer/patches/*.patch \
    && git apply 0001-kmssink-fd-prop.patch \
    && git apply 0002-kmssink-dmabuf-modifier.patch \
    && ninja -C build \
    && meson install -C build

# build libdrmlease.o
RUN git clone https://github.com/kraxel/drminfo.git \
    && cd drminfo \
    && git checkout d45f7c3a2f721e160a9d07a2f5e80daba77775c0
COPY docker/patches/0001-drm-lease-x11.patch /root/drminfo/
RUN cd drminfo \
    && git apply 0001-drm-lease-x11.patch \
    && gcc -shared -o libdrmlease.o -fPIC -DHAVE_XRANDR drm-lease.c drm-lease-x11.c `pkg-config --cflags --libs xcb xcb-randr`

# build media-driver
RUN apt install -y rpm
RUN git clone https://github.com/intel/media-driver.git \
    && cd media-driver \
    && git checkout a825bea1bcdd37bc2e7a773a9c92a52fc6363fae \
    && mkdir -p build \
    && cd build \
    && cmake .. \
    && make -j32 \
    && cpack \
    && cp intel-media-22.5.3-u22.04-.x86_64.deb /root/intel-media-22.5.3-u22.04-.x86_64.deb


COPY docker/gva_crop /root/gva_crop
RUN cd gva_crop \
    && mkdir -p build \
    && cd build \
    && cmake .. \
    && make -j4

RUN mkdir -p gstreamer-libs
RUN cp /root/gst-crypto/src/.libs/libgstcrypto.so /root/gstreamer-libs/
RUN cp /root/applications.iot.workloads.common-lib/bps/build/gstreamer-1.0/libgstbufferspersecond.so  /root/gstreamer-libs/
RUN cp /root/drminfo/libdrmlease.o /root/gstreamer-libs/
RUN cp /root/gva_crop/build/intel64/Release/lib/libgva_crop.so /root/gstreamer-libs/

#########################
# runtime container
#########################
FROM base-image as runner

# Install DPC++
RUN env -u no_proxy curl -fsSL https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | apt-key add - \
    && env -u no_proxy apt-add-repository "deb https://apt.repos.intel.com/oneapi all main"

# install dpc++ compiler
RUN env -u no_proxy apt-get install -y intel-oneapi-compiler-dpcpp-cpp-runtime

RUN apt-add-repository -r "deb https://apt.repos.intel.com/oneapi all main"

WORKDIR /root

RUN apt install -y --no-install-recommends intel-gpu-tools bc psmisc mosquitto-clients libxcb-randr0-dev \
    nodejs \
    npm \
    wget

RUN mkdir -p root/neo
WORKDIR /root/neo

# Intel(R) Graphics Compute Runtime for oneAPI Level Zero and OpenCL(TM) Driver
# https://github.com/intel/compute-runtime/releases 22.31.23852
RUN wget https://github.com/intel/intel-graphics-compiler/releases/download/igc-1.0.11485/intel-igc-core_1.0.11485_amd64.deb
RUN wget https://github.com/intel/intel-graphics-compiler/releases/download/igc-1.0.11485/intel-igc-opencl_1.0.11485_amd64.deb
RUN wget https://github.com/intel/compute-runtime/releases/download/22.31.23852/intel-level-zero-gpu-dbgsym_1.3.23852_amd64.ddeb
RUN wget https://github.com/intel/compute-runtime/releases/download/22.31.23852/intel-level-zero-gpu_1.3.23852_amd64.deb
RUN wget https://github.com/intel/compute-runtime/releases/download/22.31.23852/intel-opencl-icd-dbgsym_22.31.23852_amd64.ddeb
RUN wget https://github.com/intel/compute-runtime/releases/download/22.31.23852/intel-opencl-icd_22.31.23852_amd64.deb


# oneAPI Level Zero Loader v1.8.5
RUN wget https://github.com/oneapi-src/level-zero/releases/download/v1.8.5/level-zero-devel_1.8.5+u18.04_amd64.deb
RUN wget https://github.com/oneapi-src/level-zero/releases/download/v1.8.5/level-zero_1.8.5+u18.04_amd64.deb

RUN dpkg -i *.deb

RUN adduser --disabled-password --gecos '' kpi
RUN adduser kpi sudo
RUN chown -R kpi:kpi /home/kpi

COPY --from=builder /opt/intel/openvino /opt/intel/openvino
COPY --from=builder /opt/intel/dlstreamer /opt/intel/dlstreamer
COPY --from=builder /root/gstreamer-libs /home/kpi/libs
COPY --from=builder /root/frameworks.benchmarking.edge-systems.iotg-wkld-common-lib /home/kpi/libs/kpilib
COPY --from=builder /root/gstreamer/gst /root/gstreamer/gst
COPY --from=builder /root/dlstreamer /root/dlstreamer-build

# For solve vah265dec issue
COPY --from=builder /root/intel-media-22.5.3-u22.04-.x86_64.deb  /root/intel-media-22.5.3-u22.04-.x86_64.deb
RUN dpkg -i --force-all /root/intel-media-22.5.3-u22.04-.x86_64.deb

# For avdec_h264 and gst python plugin
RUN apt-get install -y gstreamer1.0-libav \
    gstreamer1.0-python3-plugin-loader \
    python3-gst-1.0

RUN pip3 install Xlib

# Build KPI lib
RUN pip3 install wheel setuptools twine
RUN mkdir -p /home/kpi/libs/kpilib
RUN cd /home/kpi/libs/kpilib/source-python/WorkloadCommonLib \
    && python3 setup.py bdist_wheel
RUN pip install paho-mqtt==1.6.1
RUN pip install PyYAML==6.0
RUN pip install /home/kpi/libs/kpilib/source-python/WorkloadCommonLib/dist/WorkloadCommonLib-1.1-py3-none-any.whl

ARG vcs_ref=0
ARG image_version=0.1

LABEL "org.opencontainers.image.source"="https://github.com/intel-innersource/applications.iot.workloads.gstreamer.2d-video-ai-nvr/blob/main/docker/Dockerfile"
LABEL "org.opencontainers.image.documentation"="https://github.com/intel-innersource/applications.iot.workloads.gstreamer.2d-video-ai-nvr/blob/main/README.md"
LABEL "org.opencontainers.image.url"="https://github.com/intel-innersource/applications.iot.workloads.gstreamer.2d-video-ai-nvr"
LABEL "org.opencontainers.image.revision"=$vcs_ref
LABEL "org.opencontainers.image.version"=$image_version

#
WORKDIR /home/kpi

COPY datasets /home/kpi/datasets
#COPY docker/cl_cache.zip /home/kpi/cl_cache.zip
#RUN unzip cl_cache.zip
COPY workload   /home/kpi/workload
COPY run.sh     /home/kpi/
COPY config /home/kpi/config
COPY docker/patches/KPI_Err_Monitor.py /home/kpi/libs/
COPY docker/patches/provision.py /home/kpi/libs/
ENV WKLD_CONFIG_PATH="/home/kpi/config"

RUN mkdir -p /home/kpi/output/results

ENV SHOW_FPS=1

WORKDIR /home/kpi/workload
RUN cd pipelineExecutor && npm install
RUN cd pipelineController && npm install

WORKDIR /home/kpi

ENTRYPOINT ["/bin/bash", "./run.sh"]
