# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (C) 2018, M. B. Moessner
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


function( run_rtems_checks )

include(CheckIncludeFiles)
include(CheckCSourceCompiles)

#set (CMAKE_EXTRA_INCLUDE_FILES ${CMAKE_EXTRA_INCLUDE_FILES} "${RTEMS_TC_ROOT}/${RTEMS_CC_PREFIX}/include/pthread.h")

include(${PROJECT_SOURCE_DIR}/cmake/checks/CheckRtemsCpuSupported.cmake)
include(${PROJECT_SOURCE_DIR}/cmake/checks/CheckRtemsPosixApi.cmake)
include(${PROJECT_SOURCE_DIR}/cmake/checks/CheckRtemsNetworking.cmake)
include(${PROJECT_SOURCE_DIR}/cmake/checks/CheckRtemsNewlib.cmake)
include(${PROJECT_SOURCE_DIR}/cmake/checks/CheckRtemsTypeExists.cmake)
include(${PROJECT_SOURCE_DIR}/cmake/checks/CheckRtemsFunctionExists.cmake)
include(${PROJECT_SOURCE_DIR}/cmake/checks/CheckRtemsGccSanity.cmake)
include(${PROJECT_SOURCE_DIR}/cmake/checks/CheckRtemsTypeSize.cmake)
include(${PROJECT_SOURCE_DIR}/cmake/checks/CheckRtemsSmp.cmake)


message(STATUS "")
message(STATUS "Running RTEMS Configuration and Pre - Tests")
message(STATUS "===========================================")
message(STATUS "")

#check if we build out of source
if ( ${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR} )
  message( FATAL_ERROR "\
Attempt to build inside the source tree.\
Please use a separate build directory, instead.\
Remove all generated files in this folder." )
endif()

#TODO RTEMS_ENABLE_MULTIPROCESSING
#is only enabled if provided by the bsp (introduce generic target?)

check_rtems_cpu_supported()

#check if target supports possix api
check_rtems_posix_api()

#TODO RTEMS_ENABLE_NETWORKING
check_rtems_networking()
# ephaniy x86_64 ? fail or silently walk over it?
# include path will be added in other cmakelists
#RTEMS_CPPFLAGS="${RTEMS_CPPFLAGS} -I${RTEMS_SOURCE_ROOT}/cpukit/libnetworking"],

if(${RTEMS_ENABLE_RTEMS_DEBUG})
  message(STATUS "RTEMS debug is enabled")
  add_definitions(-DRTEMS_DEBUG)
else()
  message(STATUS "RTEMS debug is disabled")
endif()

#TODO check the specs files
#RTEMS_PROG_CC_FOR_TARGET

check_rtems_newlib()

# Newlib proprietary
check_rtems_type_exits("((struct _Thread_queue_Queue*)0)->_name" HAVE_THREAD_QUEUE_QUEUE_NAME)
if(NOT HAVE_THREAD_QUEUE_QUEUE_NAME)
  message(FATAL_ERROR "Newlib struct _Thread_queue_Queue has no member called _name")
endif()

# pthread-functions not declared in some versions of newlib.
check_rtems_function_exist("pthread_attr_getguardsize" "pthread.h" HAVE_DECL_PTHREAD_ATTR_GETGUARDSIZE)
check_rtems_function_exist("pthread_attr_setguardsize" "pthread.h" HAVE_DECL_PTHREAD_ATTR_SETGUARDSIZE)
check_rtems_function_exist("pthread_attr_setstack" "pthread.h" HAVE_DECL_PTHREAD_ATTR_SETSTACK)
check_rtems_function_exist("pthread_attr_getstack" "pthread.h" HAVE_DECL_PTHREAD_ATTR_GETSTACK)

# These are SMP related and were added to newlib by RTEMS.
check_rtems_function_exist("pthread_attr_setaffinity_np" "pthread.h" HAVE_DECL_PTHREAD_ATTR_SETAFFINITY_NP)
check_rtems_function_exist("pthread_attr_getaffinity_np" "pthread.h" HAVE_DECL_PTHREAD_ATTR_GETAFFINITY_NP)
check_rtems_function_exist("pthread_setaffinity_np" "pthread.h" HAVE_DECL_PTHREAD_SETAFFINITY_NP)
check_rtems_function_exist("pthread_getaffinity_np" "pthread.h" HAVE_DECL_PTHREAD_GETAFFINITY_NP)
check_rtems_function_exist("pthread_getattr_np" "pthread.h" HAVE_DECL_PTHREAD_GETATTR_NP)


check_c_source_compiles("
#include <sys/mman.h>
int mprotect(const void *, size_t, int);
int main()
{
  return 0;
}" HAVE_MPROTECT_CONST)

check_c_source_compiles("
#include <pthread.h>
int pthread_mutex_getprioceiling(const pthread_mutex_t *__restrict, int *);
int main()
{
  return 0;
}" HAVE_PTHREAD_MUTEX_GETCEILING_CONST)

check_c_source_compiles("
#include <pthread.h>
int pthread_setschedparam(pthread_t, int, const struct sched_param *);
int main()
{
  return 0;
}" HAVE_PTHREAD_SETSCHEDPARAM_CONST)

# Some toolchain sanity checks and diagnostics
check_gcc_sanity()

# These are conditionally defined by the toolchain
# FIXME: we should either conditionally compile those parts in
# RTEMS depending on them, or abort - For now, simply check
check_include_files("pthread.h" HEADER_PRESENT)
if(${HEADER_PRESENT})
  check_rtems_type_exits("pthread_rwlock_t" HAVE_PTHREAD_RWLOCK_T)
  check_rtems_type_exits("pthread_barrier_t" HAVE_PTHREAD_BARRIER_T)
  check_rtems_type_exits("pthread_spinlock_t" HAVE_PTHREAD_SPINLOCK_T)
  check_rtems_type_exits("struct _pthread_cleanup_context" HAVE_STRUCT__PTHREAD_CLEANUP_CONTEXT)
  check_rtems_type_exits("struct _Priority_Node" HAVE_STRUCT__PRIORITY_NODE)
endif()

if(NOT ${HAVE_STRUCT__PTHREAD_CLEANUP_CONTEXT})
  message(FATAL_ERROR "struct _pthread_cleanup_context not found")
endif()

if(NOT ${HAVE_STRUCT__PRIORITY_NODE})
  message(FATAL_ERROR "struct _Priority_Node not found")
endif()

#RTEMS_CHECK_MULTIPROCESSING
#RTEMS_CHECK_POSIX_API
#RTEMS_CHECK_NETWORKING


check_rtems_smp()

check_include_files("string.h" HAVE_STRING_H)
check_include_files("strings.h" HAVE_STRINGS_H)
check_include_files("stdlib.h" HAVE_STDLIB_H)
check_include_files("stdatomic.h" HAVE_STDATOMIC_H)
check_include_files("sys/stat.h" HAVE_SYS_STAT_H)
check_include_files("unistd.h" HAVE_UNISTD_H)
check_include_files("inttypes.h" HAVE_INTTYPES_H)
check_include_files("memory.h" HAVE_MEMORY_H)
check_include_files("stddef.h" HAVE_STDDEF_H)
check_include_files("stdio.h" HAVE_STDIO_H)
check_include_files("sys/types.h" HAVE_SYS_TYPES_H)
check_include_files("stdint.h" HAVE_STDINT_H)

#very simply check for STDC_HEADERS but i guess good enough for now
if( ${HAVE_STDDEF_H} AND ${HAVE_STDIO_H} AND ${HAVE_STDLIB_H} AND ${HAVE_STRING_H} AND
    ${HAVE_SYS_TYPES_H} AND ${HAVE_SYS_STAT_H} AND ${HAVE_STRINGS_H} AND ${HAVE_INTTYPES_H} AND
    ${HAVE_STDINT_H} AND ${HAVE_UNISTD_H} AND ${HAVE_STRINGS_H} AND ${HAVE_INTTYPES_H})
set (STDC_HEADERS "1")
endif()


check_rtems_function_exist("rcmd" "unistd.h" HAVE_DECL_RCMD)
check_rtems_function_exist("_Timecounter_Time_second" "sys/time.h" HAVE_DECL__TIMECOUNTER_TIME_SECOND)
check_rtems_type_size("mode_t" SIZEOF_MODE_T)
check_rtems_type_size("off_t" SIZEOF_OFF_T)
check_rtems_type_size("time_t" SIZEOF_TIME_T)
check_rtems_type_size("size_t" SIZEOF_SIZE_T)
check_rtems_type_size("blksize_t" SIZEOF_BLKSIZE_T)
check_rtems_type_size("blkcnt_t" SIZEOF_BLKCNT_T)

set(RTEMS_VERSION ${CMAKE_PROJECT_VERSION})
set(__RTEMS_MAJOR__ ${CMAKE_PROJECT_VERSION_MAJOR})
set(__RTEMS_MINOR__ ${CMAKE_PROJECT_VERSION_MINOR})
set(__RTEMS_REVISION__ ${CMAKE_PROJECT_VERSION_PATCH})
set(__RTEMS_SIZEOF_MODE_T__ ${SIZEOF_MODE_T})
set(__RTEMS_SIZEOF_OFF_T__ ${SIZEOF_OFF_T})
set(__RTEMS_SIZEOF_TIME_T__ ${SIZEOF_TIME_T})
set(__RTEMS_SIZEOF_BLKSIZE_T__ ${SIZEOF_BLKSIZE_T})
set(__RTEMS_SIZEOF_BLKCNT_T__ ${SIZEOF_BLKCNT_T})


configure_file(${PROJECT_SOURCE_DIR}/cmake/config/config.h.in ${CMAKE_CURRENT_BINARY_DIR}/_generated/config.h)
configure_file(${PROJECT_SOURCE_DIR}/cmake/config/version-vc-key.h.in ${CMAKE_CURRENT_BINARY_DIR}/_generated/version-vc-key.h)
configure_file(${PROJECT_SOURCE_DIR}/cmake/config/cpuopts.h.in ${CMAKE_CURRENT_BINARY_DIR}/_generated/rtems/score/cpuopts.h)
configure_file(${PROJECT_SOURCE_DIR}/c/src/lib/libbsp/${RTEMS_CPU}/${RTEMS_BSP_DIR_NAME}/bspopts.h.in ${CMAKE_CURRENT_BINARY_DIR}/_generated/bsp/bspopts.h)
include_directories(${CMAKE_CURRENT_BINARY_DIR}/_generated)
include_directories(${CMAKE_CURRENT_BINARY_DIR}/_generated/bsp)

#install(FILES ${CMAKE_CURRENT_BINARY_DIR}/_generated/config.h DESTINATION ${CMAKE_INSTALL_PREFIX}/include)
#install(FILES ${CMAKE_CURRENT_BINARY_DIR}/_generated/version-vc-key.h DESTINATION ${CMAKE_INSTALL_PREFIX}/include)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/_generated/rtems/score/cpuopts.h DESTINATION ${CMAKE_INSTALL_PREFIX}/include/rtems/score)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/_generated/bsp/bspopts.h DESTINATION ${CMAKE_INSTALL_PREFIX}/include)

endfunction()
