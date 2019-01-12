function( check_rtems_networking )

if(${RTEMS_NETWORKING})
  message(STATUS "RTEMS networking is enabled")
  
  if(${RTEMS_CPU} MATCHES "epiphany" OR ${RTEMS_CPU} MATCHES "x86_64" )
    message(WARNING "cpu ${RTEMS_CPU} does not provide standard networking. Please remove --enable-networking switch")
  else()
    message(STATUS "Checking if cpu ${RTEMS_CPU} provides networking... yes")
  endif()
else()
  message(STATUS "RTEMS networking is disabled")
endif()
  
endfunction()