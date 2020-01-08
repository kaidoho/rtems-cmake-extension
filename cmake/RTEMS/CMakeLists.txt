cmake_minimum_required (VERSION 3.10)

project (RTEMS LANGUAGES C)
enable_language(C ASM)

include(${PROJECT_SOURCE_DIR}/cmake/checks/RunRtemsChecks.cmake)



run_rtems_checks()


add_subdirectory(${PROJECT_SOURCE_DIR}/cpukit)
#add_subdirectory(${PROJECT_SOURCE_DIR}/bsps/${RTEMS_CPU}/${RTEMS_BSP_DIR_NAME})

#configure_file(${PROJECT_SOURCE_DIR}/c/src/lib/libbsp/${RTEMS_CPU}/${RTEMS_BSP_DIR_NAME}/bspopts.h.in ${CMAKE_CURRENT_BINARY_DIR}/_generated/bsp/bspopts.h)
