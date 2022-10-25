#include <new>
#include <unistd.h>
#include <gst/allocators/gstdmabuf.h>
#include <gst/gstbuffer.h>
#include "gva_crop.hpp"

#define DEF_MAX_ITER    (6)
#define DEF_OUT_WIDTH   (224)
#define DEF_OUT_HEIGHT  (224)
#define DEF_OUT_SPP     (4)
#define DEF_OUT_SIZE    (DEF_OUT_WIDTH * DEF_OUT_HEIGHT * DEF_OUT_SPP)

using namespace cv;

GType c_gva_crop::s_type = g_type_register_static_simple(
        GST_TYPE_ELEMENT,
        GVA_CROP_NAME,
        sizeof(GstElementClass),
        c_gva_crop::s_class_init,
        sizeof(c_gva_crop),
        c_gva_crop::s_inst_init,
        (GTypeFlags)0);

GstStaticPadTemplate c_gva_crop::s_sink_factory =
    GST_STATIC_PAD_TEMPLATE("gva_crop_sink",
                             GST_PAD_SINK,
                             GST_PAD_REQUEST,
                             GST_STATIC_CAPS("video/x-raw,format=BGRx"));

GstStaticPadTemplate c_gva_crop::s_src_factory =
    GST_STATIC_PAD_TEMPLATE("gva_crop_src",
                            GST_PAD_SRC,
                            GST_PAD_ALWAYS,
                            GST_STATIC_CAPS("video/x-raw,format=BGRx"));

gpointer c_gva_crop::s_parent_class = nullptr;

c_gva_crop::c_gva_crop(void) :
    m_width(0),
    m_height(0),
    m_fps(0),
    m_frame(0),
    m_detect(DEF_MAX_ITER),
    m_idx(0),
    m_out_width(DEF_OUT_WIDTH),
    m_out_height(DEF_OUT_HEIGHT),
    m_out_type(CV_8UC4),
    m_buf_size(DEF_OUT_SIZE),
    m_n_buf(DEF_MAX_ITER),
    m_buf_info(nullptr),
    m_buf_bmp((1 << m_n_buf) - 1)
{
    g_mutex_init(&m_buf_lock);
    g_cond_init(&m_buf_event);
}

BufInfo *c_gva_crop::alloc_buf(void)
{
    g_mutex_lock(&m_buf_lock);
    while (0 == m_buf_bmp) {
        g_cond_wait(&m_buf_event, &m_buf_lock);
    }

    /* ffs starts from 1 */
    uint32_t idx = ffs(m_buf_bmp) - 1;
    m_buf_bmp &= ~(1 << idx);
    g_mutex_unlock(&m_buf_lock);

    return &m_buf_info[idx];
}

void c_gva_crop::free_buf(BufInfo *buf_info)
{
    buf_info->buf = gst_buffer_new_wrapped_full(GST_MEMORY_FLAG_PHYSICALLY_CONTIGUOUS,
                                                buf_info->data,
                                                m_buf_size,
                                                0,
                                                m_buf_size,
                                                buf_info,
                                                s_free_buf);

    g_mutex_lock(&m_buf_lock);
    m_buf_bmp |= 1 << buf_info->idx;
    g_mutex_unlock(&m_buf_lock);
    g_cond_broadcast(&m_buf_event);
}

void c_gva_crop::s_free_buf(void *pdata)
{
    BufInfo *buf_info = (BufInfo *)pdata;
    buf_info->inst->free_buf(buf_info);
}

/*****************************************
 * Help functions
 *****************************************/
static UNUSED void print_image_size(const char *name, Mat &img)
{
    uint32_t size = img.rows * img.cols * img.elemSize();
    printf("[%s] rows=%d cols=%d elemSize=%ld size=%d\n",
           name, img.rows, img.cols, img.elemSize(), size);
}

static UNUSED gboolean print_field(GQuark field,
                            const GValue *val,
                            gpointer ptr UNUSED)
{
    gchar *str = gst_value_serialize(val);
    printf("%15s: %s\n", g_quark_to_string(field), str);
    g_free(str);
    return TRUE;
}

static UNUSED void __print_caps(GstCaps *caps)
{
    if (gst_caps_is_any(caps)) {
        printf("ANY\n");
        return;
    }

    if (gst_caps_is_empty(caps)) {
        printf("EMPTY\n");
        return;
    }

    for (guint i = 0; i < gst_caps_get_size(caps); ++i) {
        GstStructure *s = gst_caps_get_structure(caps, i);
        printf("%s\n", gst_structure_get_name(s));
        gst_structure_foreach(s, print_field, NULL);
    }
}

/* Non-static function to avoid compile warning */
static void UNUSED print_caps(GstCaps *caps, const char *msg)
{
    printf("===== Start printing caps for: %s\n", msg);
    __print_caps(caps);
    printf("===== Stop printing caps for: %s\n", msg);
}

static UNUSED void __dump_meta(GstBuffer *buffer)
{
    gpointer state = NULL;
    GstMeta *meta;

    while ((meta = gst_buffer_iterate_meta(buffer, &state))) {
        printf("%s, %d, %s\n", __func__, __LINE__,
               g_type_name(meta->info->type));
    }
}
/*****************************************
 * End of help functions
 *****************************************/


void c_gva_crop::do_crop(Mat &image, GstStructure *s)
{
    double d_x_min = -1;
    double d_x_max = -1;
    double d_y_min = -1;
    double d_y_max = -1;

    gst_structure_get_double(s, "x_min", &d_x_min);
    gst_structure_get_double(s, "x_max", &d_x_max);
    gst_structure_get_double(s, "y_min", &d_y_min);
    gst_structure_get_double(s, "y_max", &d_y_max);

    uint32_t x_min = (uint32_t)(m_width * d_x_min);
    uint32_t x_max = (uint32_t)(m_width * d_x_max);
    uint32_t y_min = (uint32_t)(m_height * d_y_min);
    uint32_t y_max = (uint32_t)(m_height * d_y_max);
    Rect rect(x_min, y_min, x_max - x_min, y_max - y_min);
    auto cropped_img = image(rect);

    BufInfo *buf_info = alloc_buf();
    Mat resized_img = Mat(Size(m_out_width, m_out_height), m_out_type, buf_info->data, Mat::AUTO_STEP);
    resize(cropped_img, resized_img, Size(m_out_width, m_out_height));

    auto ret = gst_pad_push(m_srcpad, buf_info->buf);
    if (GST_FLOW_OK != ret) {
        printf("Fail to process crop buf: ret=%d\n", ret);
        gst_buffer_unref(buf_info->buf);
    }
}

/* Process the buffer from on of the sink pad */
GstFlowReturn c_gva_crop::chain(GstBuffer *buf)
{
    /* For debugging purpose only */
#if 0
    GstMapInfo map;
    if (!gst_buffer_map(buf, &map, GST_MAP_READ)) {
        return GST_FLOW_ERROR;
    }

    Mat image = Mat(Size(m_width, m_height), m_out_type, map.data, Mat::AUTO_STEP);
    Rect rect(300, 100, m_out_width, m_out_height);
    auto cropped_img = image(rect);

    BufInfo *buf_info = alloc_buf();
    Mat resized_img = Mat(Size(m_out_width, m_out_height), m_out_type, buf_info->data, Mat::AUTO_STEP);
    cropped_img.copyTo(resized_img);
    //resize(cropped_img, resized_img, Size(m_out_width, m_out_height));

    auto ret = gst_pad_push(m_srcpad, buf_info->buf);
    if (GST_FLOW_OK != ret) {
        printf("Fail to process crop buf. ret=%d\n", ret);
        gst_buffer_unref(buf_info->buf);
    }

    //printf("res=%d\n", gst_pad_push(m_srcpad, buf));
    gst_buffer_unref(buf);
    return GST_FLOW_OK;
#else

    /* Only process the first frame for each second */
    if (m_frame > 0) {
        m_frame -= 1;
        if (0 == m_detect) {
            gst_buffer_unref(buf);
            return GST_FLOW_OK;
        }
    } else {
        m_frame = m_fps;
        m_detect = DEF_MAX_ITER;
    }

    GstMeta *meta = NULL;
    gpointer state = NULL;

    GstMapInfo map;
    if (!gst_buffer_map(buf, &map, GST_MAP_READ)) {
        return GST_FLOW_ERROR;
    }

    Mat image = Mat(Size(m_width, m_height), m_out_type, map.data, Mat::AUTO_STEP);

    while (NULL != (meta = gst_buffer_iterate_meta_filtered(buf, &state, GST_VIDEO_REGION_OF_INTEREST_META_API_TYPE))) {
        auto _meta = (GstVideoRegionOfInterestMeta *)meta;

        for (GList *l = _meta->params; l; l = g_list_next(l)) {
            GstStructure *s = GST_STRUCTURE(l->data);
            if (not gst_structure_has_name(s, "object_id")) {
                do_crop(image, s);
                if (0 == --m_detect) {
                    gst_buffer_unref(buf);
                    return GST_FLOW_OK;
                }
            }
        }
    }

    gst_buffer_unref(buf);
    return GST_FLOW_OK;
#endif
}

GstFlowReturn c_gva_crop::s_chain(GstPad *pad UNUSED,
                                  GstObject *parent,
                                  GstBuffer *buf)
{
    return GVA_CROP(parent)->chain(buf);
}

GstStateChangeReturn c_gva_crop::change_state(GstStateChange transition)
{
    auto parent = GST_ELEMENT_CLASS(s_parent_class);
	return parent->change_state(element(), transition);
}

GstStateChangeReturn c_gva_crop::s_change_state(GstElement *element,
                                                GstStateChange transition)
{
    return GVA_CROP(element)->change_state(transition);
}

gboolean c_gva_crop::event_caps(GstEvent *event)
{
    GstCaps *caps;
    gst_event_parse_caps(event, &caps);

    if (!gst_video_info_from_caps(&m_video_info, caps)) {
        printf("Fail to get video info from sink GST_EVENT_CAPS");
        return FALSE;
    }

    const char *name = GST_VIDEO_INFO_NAME(&m_video_info);
    if (0 != strcmp("BGRx", name)) {
        printf("Not support format: %s\n", name);
        return FALSE;
    }

    if (GST_VIDEO_INFO_FORMAT(&m_video_info) == GST_VIDEO_FORMAT_UNKNOWN) {
        printf("Sink set unknown caps\n");
        return FALSE;
    }

    m_width = GST_VIDEO_INFO_WIDTH(&m_video_info);
    m_height = GST_VIDEO_INFO_HEIGHT(&m_video_info);
    m_fps = GST_VIDEO_INFO_FPS_N(&m_video_info) /
            GST_VIDEO_INFO_FPS_D(&m_video_info);

    printf("GST_VIDEO_INFO_FPS_N(&m_video_info): %d\n", GST_VIDEO_INFO_FPS_N(&m_video_info));
    printf("GST_VIDEO_INFO_FPS_D(&m_video_info): %d\n", GST_VIDEO_INFO_FPS_D(&m_video_info));

    GstCaps *new_caps = gst_caps_new_simple("video/x-raw",
				    			            "format", G_TYPE_STRING, "BGRx",
                                            "framerate", GST_TYPE_FRACTION, DEF_MAX_ITER, 1,
                                            "width", G_TYPE_INT, m_out_width,
                                            "height", G_TYPE_INT, m_out_height,
                                            NULL);

    gboolean ret = gst_pad_push_event(m_srcpad, gst_event_new_caps(new_caps));
    gst_caps_unref(new_caps);

    if (!ret) {
        printf("Fail to push the caps to src peer\n");
        return FALSE;
    }

    return TRUE;
}

gboolean c_gva_crop::s_sink_event(GstPad *pad,
                                  GstObject *parent,
                                  GstEvent *event)
{
    switch (GST_EVENT_TYPE(event)) {
    case GST_EVENT_CAPS:
        return GVA_CROP(parent)->event_caps(event);

    default:
        return gst_pad_event_default(pad, parent, event);
    }
}

gboolean c_gva_crop::s_sink_query(GstPad *pad,
                                  GstObject *parent,
                                  GstQuery *query)
{
    gboolean ret = TRUE;
    GstCaps *caps;
    GstCaps *filter;
    GstCaps *template_caps;
    gboolean accept;

    switch (GST_QUERY_TYPE(query)) {
    case GST_QUERY_CAPS:
        gst_query_parse_caps(query, &filter);
        caps = gst_pad_get_pad_template_caps(pad);
        gst_query_set_caps_result(query, caps);
        print_caps(caps, "GST_QUERY_CAPS");
        gst_caps_unref(caps);
        break;

    case GST_QUERY_ACCEPT_CAPS:
        gst_query_parse_accept_caps(query, &caps);
        template_caps = gst_pad_get_pad_template_caps(pad);
        accept = gst_caps_is_subset (caps, template_caps);
        gst_caps_unref (template_caps);
        gst_query_set_accept_caps_result(query, accept);
        break;

    default:
        printf("sink %s, %d, query=%s\n", __func__,
               __LINE__, GST_QUERY_TYPE_NAME(query));
        ret = gst_pad_query_default(pad, parent, query);
        break;
    }

    return ret;
}

gboolean c_gva_crop::s_src_query(GstPad *pad,
                                 GstObject *parent UNUSED,
                                 GstQuery *query)
{
    gboolean ret = TRUE;
    GstCaps *caps;

    switch (GST_QUERY_TYPE(query)) {
    case GST_QUERY_CAPS:
        caps = gst_pad_get_pad_template_caps(pad);
        gst_query_set_caps_result(query, caps);
        gst_caps_unref(caps);
        break;

    default:
        ret = FALSE;
        break;
    }

    return ret;
}

gboolean c_gva_crop::s_src_event(GstPad *pad UNUSED,
                                 GstObject *parent,
                                 GstEvent *event)
{
    return gst_pad_push_event(GVA_CROP(parent)->m_sinkpad, event);
}


void c_gva_crop::s_class_init(gpointer klass, gpointer data UNUSED)
{
    GstElementClass *p_class = (GstElementClass *)klass;
    s_parent_class = g_type_class_peek_parent(klass);

    gst_element_class_add_pad_template(p_class, gst_static_pad_template_get(&s_sink_factory));
    gst_element_class_add_pad_template(p_class, gst_static_pad_template_get(&s_src_factory));

    p_class->change_state = c_gva_crop::s_change_state;

    gst_element_class_set_details_simple(p_class,
                                         GVA_CROP_NAME,
                                         GVA_CROP_KLASS,
                                         GVA_CROP_DESC,
                                         GVA_CROP_AUTHOR);
}

void c_gva_crop::init(void)
{
    m_sinkpad = gst_pad_new_from_static_template(&s_sink_factory, "gva_crop_sink");;
    gst_pad_set_event_function(m_sinkpad, GST_DEBUG_FUNCPTR(s_sink_event));
    gst_pad_set_query_function(m_sinkpad, GST_DEBUG_FUNCPTR(s_sink_query));
    gst_pad_set_chain_function(m_sinkpad, GST_DEBUG_FUNCPTR(s_chain));
    GST_PAD_SET_PROXY_CAPS(m_sinkpad);
    gst_element_add_pad(element(), m_sinkpad);

    m_srcpad = gst_pad_new_from_static_template(&s_src_factory, "gva_crop_src");
    GST_PAD_SET_PROXY_CAPS(m_srcpad);
    gst_pad_set_query_function(GST_PAD(m_srcpad), s_src_query);
    gst_pad_set_event_function(GST_PAD(m_srcpad), s_src_event);
    gst_element_add_pad(element(), m_srcpad);

    m_buf_info = new BufInfo[m_n_buf];
    for (uint32_t i = 0; i < m_n_buf; ++i) {
        BufInfo *buf_info = &m_buf_info[i];

        buf_info->idx = i;
        buf_info->inst = this;
        buf_info->data = (gpointer)malloc(m_buf_size);
        buf_info->buf = gst_buffer_new_wrapped_full(GST_MEMORY_FLAG_PHYSICALLY_CONTIGUOUS,
                                                    buf_info->data,
                                                    m_buf_size,
                                                    0,
                                                    m_buf_size,
                                                    buf_info,
                                                    s_free_buf);

        if (NULL == buf_info->data) {
            printf("gva_crop: ERR: Fail to allocate src memory\n");
            abort();
        }
    }
}

void c_gva_crop::s_inst_init(GTypeInstance *inst UNUSED, gpointer klass UNUSED)
{
    c_gva_crop *crop = new (inst) c_gva_crop;

    crop->init();
}

