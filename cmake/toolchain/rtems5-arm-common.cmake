


set(RTEMS_TOP_ARCH  arm)



list(APPEND RTEMS_CPU_FLAGS -mthumb)
list(APPEND RTEMS_CPU_FLAGS -mtune=${RTEMS_TARGET_CPU} )

if(DEFINED RTEMS_FPU_ABI)
    list(APPEND RTEMS_CPU_FLAGS -mfloat-abi=${RTEMS_FPU_ABI})
endif()

if(DEFINED RTEMS_FPU_TYPE)
    list(APPEND RTEMS_CPU_FLAGS -mfpu=${RTEMS_FPU_TYPE})
endif()



if( "${RTEMS_TARGET_CPU}" MATCHES "cortex-m7")
    list(APPEND RTEMS_CPU_FLAGS -march=armv7e-m)
else()
    message(FATAL_ERROR "Unknown CPU ${RTEMS_TARGET_CPU}")
endif()


include(${CMAKE_CURRENT_LIST_DIR}/rtems5-common.cmake)