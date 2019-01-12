include(CheckCSourceCompiles)

function(check_rtems_newlib)

  check_c_source_compiles("
  extern void not_required_by_rtems() ;
  int main() 
  { 
    not_required_by_rtems();
    return 0;
  }" NEWLIB_COMPILE_TEST_1)

  check_c_source_compiles("
  extern void rtems_provides_crt0() ;
  int main() 
  { 
    rtems_provides_crt0();
    return 0;
  }" NEWLIB_COMPILE_TEST_2)

  if( ${NEWLIB_COMPILE_TEST_1} AND ${NEWLIB_COMPILE_TEST_2})
    set(RTEMS_NEWLIB "1" PARENT_SCOPE)
    message(STATUS  "Checking if newlib supports RTEMS... yes" )
  else()
    message(STATUS  "Checking if newlib supports RTEMS... no" )
  endif()

  
endfunction()