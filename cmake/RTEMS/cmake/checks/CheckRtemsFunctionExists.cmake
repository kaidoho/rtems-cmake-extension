include(CheckSymbolExists)
include(CMakePushCheckState)

function(check_rtems_function_exist FUNC HFILE VARNAME)

  unset(LRES CACHE)
  cmake_push_check_state(RESET)
  set(CMAKE_REQUIRED_DEFINITIONS -D_GNU_SOURCE)
  check_symbol_exists(rtems_stub_${FUNC} ${HFILE} LRES)
  cmake_pop_check_state()

  if(${LRES})
    set(${VARNAME} "${LRES}" PARENT_SCOPE)
  else()
    unset(LRES CACHE)
    cmake_push_check_state(RESET)
    set(CMAKE_REQUIRED_DEFINITIONS -D_GNU_SOURCE)
    check_symbol_exists(${FUNC} ${HFILE} LRES)
    cmake_pop_check_state()
    if(${LRES})
      set(${VARNAME} "${LRES}" PARENT_SCOPE)
     else()
      set(${VARNAME} "0" PARENT_SCOPE)
    endif()
  endif()

endfunction()
