#include "common.h"
#include "gva_crop.hpp"

#ifdef __cplusplus
extern "C"{
#endif

gboolean gva_crop_plugin_init(GstPlugin *plugin)
{
    return gst_element_register(plugin, GVA_CROP_NAME,
                                GST_RANK_NONE, GST_TYPE_GVA_CROP);
}

GST_PLUGIN_EXPORT const GstPluginDesc *gst_plugin_gva_crop_get_desc(void)
{
    static const GstPluginDesc desc = {
        GST_VERSION_MAJOR,
        GST_VERSION_MINOR,
        GVA_CROP_NAME,
        GVA_CROP_DESC,
        gva_crop_plugin_init,
        PLUGIN_VERSION,
        PLUGIN_LICENSE,
        GVA_CROP_NAME,
        PACKAGE_NAME,
        GST_PACKAGE_ORIGIN,
        __GST_PACKAGE_RELEASE_DATETIME,
        GST_PADDING_INIT
    };

    return &desc;
}

#ifdef __cplusplus
}
#endif

