cmake_minimum_required (VERSION 3.10)

project (RTEMS LANGUAGES C)
enable_language(C ASM)

#include(${PROJECT_SOURCE_DIR}/cmake/checks/RunRtemsChecks.cmake)
include(CheckTypeSize)

check_type_size("uint32_t" LRES)
#run_rtems_checks()