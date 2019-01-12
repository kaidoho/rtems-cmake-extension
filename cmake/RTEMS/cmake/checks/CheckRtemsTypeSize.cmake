include(CheckTypeSize)

function(check_rtems_type_size TYPENAME VARNAME)
  set (SAVE_FLAGS ${CMAKE_EXE_LINKER_FLAGS} ) 
  string(FIND ${CMAKE_EXE_LINKER_FLAGS} "-Wl,--gc-sections" p1)
  string(SUBSTRING ${CMAKE_EXE_LINKER_FLAGS} 0 ${p1} TMP_LFLAGS_L)
  math(EXPR p1 "${p1}+17")
  string(SUBSTRING ${CMAKE_EXE_LINKER_FLAGS} ${p1} -1 TMP_LFLAGS_R)
  string(CONCAT CMAKE_EXE_LINKER_FLAGS ${TMP_LFLAGS_L} ${TMP_LFLAGS_R})
  string(FIND ${CMAKE_EXE_LINKER_FLAGS} "-nodefaultlibs" p1)
  string(SUBSTRING ${CMAKE_EXE_LINKER_FLAGS} 0 ${p1} TMP_LFLAGS_L)
  math(EXPR p1 "${p1}+14")
  string(SUBSTRING ${CMAKE_EXE_LINKER_FLAGS} ${p1} -1 TMP_LFLAGS_R)
  string(CONCAT CMAKE_EXE_LINKER_FLAGS ${TMP_LFLAGS_L} ${TMP_LFLAGS_R})
  
  unset(LRES CACHE)
  unset(HAVE_LRES CACHE)
  
  check_type_size(${TYPENAME} LRES)

  if(${HAVE_LRES})

    set(${VARNAME} ${LRES} PARENT_SCOPE)
    set(HAVE_${VARNAME} ${HAVE_LRES} PARENT_SCOPE)
  endif()
  
  set (CMAKE_EXE_LINKER_FLAGS ${SAVE_FLAGS} )
endfunction()
