
include_directories(${GSTREAMER_INCLUDE_DIRS})
include_directories(${GLIB2_INCLUDE_DIRS})
link_directories( ${GSTREAMER_LIBRARY_DIRS} )

#build the "helper" GstElements. Technically, these have nothing to do with the
# 'remoteoffload' capabilities. They are simply custom elements that are used
# for some of the tests/examples to "show off" the capabilities of the
# remote offload framework.
include_directories(bps)

add_library(gstbufferspersecond SHARED
gstbufferspersecond.c
)
target_link_libraries(gstbufferspersecond ${GLIBS} )

set_target_properties(
                      gstbufferspersecond
                      PROPERTIES
                      LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/gstreamer-1.0")

install( TARGETS 
                 gstbufferspersecond
                 DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/gstreamer-1.0")
