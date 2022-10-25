## Setup the build environment
    source /opt/intel/oneapi/compiler/2021.2.0/env/vars.sh

    if the above path is unavailable, please refer to the section "Insall OpenVINO" in the following wiki
    https://wiki.ith.intel.com/display/Linux4EdgeStack/Walk+Phase+1a%3A+NVR+Use+Case+-+Configuration+and+Setup

## Commands to build
    * inside gva_corp/
    $ mkdir build & cd build
    $ cmake ..
    $ make -j
    
## Output file
    /build/intel64/Release/lib/libgva_crop.so
   
