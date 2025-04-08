# Copyright (c) 2025 Materials Modelling Lab, The University of Tokyo
# SPDX-License-Identifier: Apache-2.0

find_package(douka 0.0.0 REQUIRED)
find_package(libtensor REQUIRED)
find_package(nlohmann_json REQUIRED)
find_package(phase_field REQUIRED)
if(CMAKE_CXX_COMPILER_ID STREQUAL "FujitsuClang")
  add_library(OpenMP::OpenMP_CXX INTERFACE IMPORTED)
  set_property(
    TARGET OpenMP::OpenMP_CXX PROPERTY
    INTERFACE_LINK_LIBRARIES -fopenmp)
else()
  find_package(OpenMP REQUIRED)
endif()
