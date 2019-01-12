include(CheckIncludeFiles)

function(check_rtems_smp )

if( ${RTEMS_SMP} )
  message(STATUS "RTEMS SMP is enabled")
  if(RTEMS_CPU MATCHES "arm" OR RTEMS_CPU MATCHES "powerpc" OR RTEMS_CPU MATCHES "riscv" OR RTEMS_CPU MATCHES "sparc" OR RTEMS_CPU MATCHES "i386")

    if(NOT ${HAVE_STDATOMIC_H} )
      message(FATAL_ERROR "SMP requires stdatomic.h")
    endif()
    message(STATUS "Enabled SMP for CPU ${RTEMS_CPU}")
  else()
    message(FATAL_ERROR "CPU ${RTEMS_CPU} does not support SMP, but --enable-smp was set ")
  endif()
else()
  message(STATUS "RTEMS SMP is disabled")
endif()

endfunction()