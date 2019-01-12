include(CheckTypeSize)

function(check_rtems_type_exits TYPENAME VARNAME)

  unset(LRES CACHE)
  unset(HAVE_LRES CACHE)

  check_type_size(${TYPENAME} LRES)
  
  if(${HAVE_LRES})

    set(${VARNAME} "1" PARENT_SCOPE)

  endif()
  
  
endfunction()