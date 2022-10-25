# ==============================================================================
# Copyright (C) 2018-2021 Intel Corporation
# ==============================================================================

cmake_minimum_required (VERSION 3.1)

find_package(OpenCV REQUIRED)

set(CMAKE_CXX_COMPILER g++)
set(CMAKE_CXX_STANDARD 17)

set(TARGET_NAME_GVA_CROP "gva_crop")

set (GVA_CROP_LIBRARIES_INSTALL_PATH lib)
set (GVA_CROP_PLUGINS_INSTALL_PATH ${GVA_CROP_LIBRARIES_INSTALL_PATH}/gstreamer-1.0)

find_package(PkgConfig REQUIRED)
pkg_check_modules(GSTREAMER gstreamer-1.0>=1.16 REQUIRED)
pkg_check_modules(GSTALLOC gstreamer-allocators-1.0 REQUIRED)
pkg_check_modules(GSTVIDEO gstreamer-video-1.0>=1.16 REQUIRED)
pkg_check_modules(GLIB2 glib-2.0 REQUIRED)

file (GLOB MAIN_SRC
    main.cpp
    gva_crop.cpp
)

file (GLOB MAIN_HEADERS
)

macro(set_target_build_env TARGET_NAME)
    target_compile_options(${TARGET_NAME} PRIVATE $<$<COMPILE_LANGUAGE:C>:${C_FLAGS}> $<$<COMPILE_LANGUAGE:CXX>:${CXX_FLAGS}> -g -Wno-error=unused-variable -Wno-error=unused-parameter)

    target_include_directories(${TARGET_NAME}
    PRIVATE
        ${GSTREAMER_INCLUDE_DIRS}
        ${GSTVIDEO_INCLUDE_DIRS}
        ${GLIB2_INCLUDE_DIRS}
        ${GSTALLOC_INCLUDE_DIRS}
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${OpenCV_INCLUDE_DIRS}
    )

    target_link_libraries(${TARGET_NAME}
    PRIVATE
        ${GSTREAMER_LDFLAGS}
        ${GSTALLOC_LDFLAGS}
        ${GSTVIDEO_LDFLAGS}
        ${GLIB2_LIBRARIES}
        ${OpenCV_LIBS}
        ze_loader
    )
    #add_subdirectory(gpu/)
    install(TARGETS ${TARGET_NAME} DESTINATION ${GVA_CROP_PLUGINS_INSTALL_PATH})
endmacro()

add_library(${TARGET_NAME_GVA_CROP} SHARED ${MAIN_SRC} ${MAIN_HEADERS})
set_target_lib_version(${TARGET_NAME_GVA_CROP})
set_target_build_env(${TARGET_NAME_GVA_CROP})

