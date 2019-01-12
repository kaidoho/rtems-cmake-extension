function( check_rtems_posix_api )

if(${RTEMS_POSIX_API})
  if(${RTEMS_CPU} MATCHES "no_cpu")
    message(FATAL_ERROR "cpu ${RTEMS_CPU} does not provide posix api. Please remove --enable-posix switch")
  endif()
  message(STATUS "RTEMS posix api is enabled")
  message(STATUS "Checking if cpu ${RTEMS_CPU} provides posix api... yes")
else()
  message(STATUS "RTEMS posix api is disabled")
endif()
  
endfunction()