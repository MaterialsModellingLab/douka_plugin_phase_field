# Copyright (c) 2025 Materials Modelling Lab, The University of Tokyo
# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.27 FATAL_ERROR)
project(phase_field VERSION 0.0.0 LANGUAGES CXX DESCRIPTION "Data Assimilation Plugin For Phase Field Model")

if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  set(CMAKE_INSTALL_PREFIX "$ENV{HOME}/.local/" CACHE PATH "Default install path" FORCE)
endif()

# Define executable name for different platforms
set(DOUKA_PLUGIN_NAME "${PROJECT_NAME}")

# CMake Local Module Imports
include(${CMAKE_SOURCE_DIR}/cmake/clang_format.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/cppcheck.cmake)
include(${CMAKE_SOURCE_DIR}/cmake/dependencies.cmake)

set(TARGET ${DOUKA_PLUGIN_NAME})
add_library(${TARGET} SHARED)
target_sources(${TARGET}
  PRIVATE
  ${CMAKE_SOURCE_DIR}/src/${PROJECT_NAME}.cc)
target_link_libraries(${TARGET} PRIVATE
  douka::plugin_interface phase_field::phase_field)

douka_plugin_install(${DOUKA_PLUGIN_NAME})
douka_plugin_status(${DOUKA_PLUGIN_NAME})
