#ifndef __COMMON_H__
#define __COMMON_H__

#include <stdio.h>
#include <stdint.h>
#include <array>

#include <gst/gst.h>
#include <gst/video/video.h>
#include <gst/allocators/allocators.h>

/* We assume:
 * max resolution 4K: 3840 * 2160
 * max sink: 5 * 5
 */
#define MAX_SINK (25)
#define ARR_SIZE (2160 * 5)

//these have been moved to CMakeList.txt
//#define RGBA
//#define NV12
//NOT OPEN THIS! CRTC NOT SUPPORT! #define YV12

#define UNUSED __attribute__((unused))

#define GVA_CROP_NAME "gva_crop"

#define GVA_CROP_KLASS "gva_Crop"
#define GVA_CROP_DESC "GVA crop input video streams according to the meta data"
#define GVA_CROP_AUTHOR "Guo Xiang <xiang.guo@intel.com>"

#define GVA_CROP_SINK_PAD_NAME "gva_crop_sink_pad"
#define GVA_CROP_BUF_POOL_NAME "gva_crop_buf_pool"

#define FORMATSINK GST_VIDEO_CAPS_MAKE("{ BGRA }") "; "
#define FORMATSRC GST_VIDEO_CAPS_MAKE("{ BGRA }") "; "

enum {
  PROP_0,
  PROP_BUF_NUM,
  PROP_XPOS,
  PROP_YPOS,
  PROP_N
};

#endif /* __COMMON_H__ */

