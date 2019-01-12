cmake_minimum_required (VERSION 3.10)

project (RTEMS LANGUAGES C)
enable_language(C ASM)

include(${PROJECT_SOURCE_DIR}/cmake/checks/RunRtemsChecks.cmake)



run_rtems_checks()


add_subdirectory(${PROJECT_SOURCE_DIR}/cpukit)
add_subdirectory(${PROJECT_SOURCE_DIR}/bsps/${RTEMS_CPU}/${RTEMS_BSP_DIR_NAME})
