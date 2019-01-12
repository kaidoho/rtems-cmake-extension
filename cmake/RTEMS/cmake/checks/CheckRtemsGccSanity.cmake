# Some GCC sanity checks to check for known bugs in the rtems gcc toolchains

function(check_gcc_sanity)

  message(STATUS "Running GCC sanity checks...")
  set(CHECKS  PRIxPTR ; PRIuPTR ; PRIdPTR ; PRINTF_ZU_SIZE_T ; PRINTF_ZD_SSIZE_T ; PRINTF_LD_OFF_T; PRINTF_LD_OFF_T)
  set(TEXTS  "printf(\"%\" PRIxPTR, uintptr_t)" ; "printf(\"%\" PRIuPTR, uintptr_t)" ; "printf(\"%\" PRIdPTR, intptr_t)" ;
             "printf(\"%zu\", size_t)" ; "printf(\"%zd\", ssize_t)" ; "printf(\"%ld\", off_t)" ; "printf(\"%lld\", off_t)")

  list(LENGTH CHECKS count)
  math(EXPR count "${count}-1")
  
  
  foreach(idx RANGE ${count})
    unset(CompileResult)
    unset(log)
    unset(CHECK)
    unset(TEXT)
    list(GET CHECKS ${idx} CHECK)
    list(GET TEXTS ${idx} TEXT)

    try_compile(CompileResult ${CMAKE_BINARY_DIR} ${PROJECT_SOURCE_DIR}/cmake/checks/CheckRtemsGccSanity.c
          #      CMAKE_FLAGS "-Wall -Werror"
                COMPILE_DEFINITIONS "-DTEST_${CHECK}"
                OUTPUT_VARIABLE log)
    if( NOT ${CompileResult})
      message(STATUS "checking if ${TEXT} works... no")
      #message(WARNING "${log}")
    else()
      message(STATUS "checking if ${TEXT} works... yes")
    endif()
  endforeach()
    


endfunction()