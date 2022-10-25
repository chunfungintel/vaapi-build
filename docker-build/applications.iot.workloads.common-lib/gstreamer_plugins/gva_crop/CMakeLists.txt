# ==============================================================================
# Copyright (C) 2018-2022 Intel Corporation
# ==============================================================================
cmake_minimum_required (VERSION 3.1)

project(gva_crop)

if(NOT(UNIX))
    message(FATAL_ERROR "Only UNIX supported")
endif()

if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
    message(STATUS "CMAKE_BUILD_TYPE is undefined. Set default build type ${CMAKE_BUILD_TYPE}.")
endif()

option(TREAT_WARNING_AS_ERROR "Treat build warnings as errors" OFF)

set(VERSION_MAJOR 1)
set(VERSION_MINOR 0)
set(VERSION_PATCH 0)
set(PLUGIN_VERSION ${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH})

# Propagate version to plugins
add_definitions(-DPLUGIN_VERSION="${PLUGIN_VERSION}")
add_definitions(-DPACKAGE="gst crop")
add_definitions(-DPACKAGE_NAME="gst crop plugin")
add_definitions(-DGST_PACKAGE_ORIGIN="Unknown package origin")
add_definitions(-DPLUGIN_LICENSE="MIT/X11")

macro(set_target_lib_version TARGET)
    set_target_properties(
        ${TARGET}
        PROPERTIES
        SOVERSION ${VERSION_MAJOR}
        VERSION ${PLUGIN_VERSION}
    )
endmacro(set_target_lib_version)

if (NOT(BIN_FOLDER))
    if("${CMAKE_SIZEOF_VOID_P}" EQUAL "8")
        set (ARCH intel64)
    else()
        set (ARCH ia32)
    endif()
    set (BIN_FOLDER ${ARCH})
endif()

set (CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${BIN_FOLDER}/${CMAKE_BUILD_TYPE}/lib)
set (CMAKE_PLUGIN_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${BIN_FOLDER}/${CMAKE_BUILD_TYPE}/lib/gstreamer-1.0)
set (CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${BIN_FOLDER}/${CMAKE_BUILD_TYPE}/lib)
set (CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/${BIN_FOLDER}/${CMAKE_BUILD_TYPE}/bin)

find_package(Threads REQUIRED)

# Common compilation flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wuninitialized -Winit-self -Wmaybe-uninitialized -Warray-bounds -fstack-protector-strong -Wno-deprecated-declarations  -fno-strict-overflow -fno-delete-null-pointer-checks -fwrapv")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wuninitialized -Warray-bounds -fstack-protector-strong -Wno-deprecated-declarations -fno-strict-overflow -fno-delete-null-pointer-checks -fwrapv")

if(TREAT_WARNING_AS_ERROR)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Werror")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Werror")
endif()

set(C_FLAGS -Wall -Wextra)
set(CXX_FLAGS -Wall -Wextra)
set(CMAKE_CXX_FLAGS_RELEASE "-O2")

## to use C/C++11
set (CMAKE_C_STANDARD 11)
set (CMAKE_CXX_STANDARD 11)
set (CMAKE_POSITION_INDEPENDENT_CODE ON)

include_directories(${CMAKE_CURRENT_BINARY_DIR}/configs)

add_subdirectory(gva_crop)
