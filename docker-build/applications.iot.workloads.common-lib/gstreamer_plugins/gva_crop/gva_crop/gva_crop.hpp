#ifndef __GVA_CROP_HPP__
#define __GVA_CROP_HPP__

#include <opencv2/opencv.hpp>

#include "common.h"

class c_gva_crop;

/* For buffer related struct */
typedef struct {
    uint32_t idx;
    c_gva_crop *inst;
    gpointer data;
    GstBuffer *buf;
} BufInfo;


class c_gva_crop
{
public:
    gboolean push_sink_event(GstEvent *);

    inline GstElement *element(void);

private:
    c_gva_crop(void);

    void init(void);
    BufInfo *alloc_buf(void);
    void free_buf(BufInfo *);

    gboolean init_caps(void);

    gboolean event_caps(GstEvent *);

    void do_crop(cv::Mat &image, GstStructure *s);
    GstFlowReturn chain(GstBuffer *);

    gboolean src_query(GstPad *, GstQuery *);
    gboolean src_event(GstPad *, GstEvent *);

    GstPad *request_new_pad(GstPadTemplate *, const gchar *);
    GstStateChangeReturn change_state(GstStateChange);

    void set_prop(guint, const GValue *, GParamSpec *);
    void get_prop(guint, GValue *, GParamSpec *);

private:
    static void s_free_buf(void *);

    static GstFlowReturn s_chain(GstPad *, GstObject *, GstBuffer *);

    static GstPad *s_request_new_pad(GstElement *, GstPadTemplate *,
                                     const gchar *, const GstCaps *);
    static GstStateChangeReturn s_change_state(GstElement *, GstStateChange);

    static gboolean s_src_event(GstPad *, GstObject *, GstEvent *);
    static gboolean s_src_query(GstPad *, GstObject *, GstQuery *);

    static gboolean s_sink_event(GstPad *, GstObject *, GstEvent *);
    static gboolean s_sink_query(GstPad *, GstObject *, GstQuery *);

    static void s_class_init(gpointer, gpointer);
    static void s_inst_init(GTypeInstance *, gpointer);

private:
    GstElement parent;          /* This is handled by G_parent */

    GstPad *m_sinkpad;
    GstPad *m_srcpad;

    GstVideoInfo m_video_info;

    uint32_t m_width;
    uint32_t m_height;
    uint32_t m_fps;
    uint32_t m_frame;
    uint32_t m_detect;

    uint32_t m_idx;
    uint32_t m_out_width;
    uint32_t m_out_height;
    uint32_t m_out_type;
    uint32_t m_buf_size;
    uint32_t m_n_buf;
    BufInfo *m_buf_info;
    uint32_t m_buf_bmp;

    GMutex m_buf_lock;
    GCond m_buf_event;

private:
    static GstStaticPadTemplate s_sink_factory;
    static GstStaticPadTemplate s_src_factory;
    static gpointer s_parent_class;

public:
    static GType s_type;
};

#define GST_TYPE_GVA_CROP c_gva_crop::s_type

#define GVA_CROP(obj) (G_TYPE_CHECK_INSTANCE_CAST((obj), \
                       GST_TYPE_GVA_CROP, c_gva_crop))

GstElement *c_gva_crop::element(void)
{
    return GST_ELEMENT(this);
}

#endif /* __GVA_CROP_HPP__ */

