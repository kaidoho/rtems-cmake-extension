set(CMAKE_SYSTEM_NAME Generic)
SET(CMAKE_SYSTEM_PROCESSOR arm)
SET(CMAKE_CROSSCOMPILING 1)


set(RTEMS_CC_PREFIX "arm-rtems5")

IF (WIN32)
  set(EXE_SUFFIX ".exe")
ELSE()
  set(EXE_SUFFIX "")
ENDIF()


set(CMAKE_C_COMPILER    ${RTEMS_TC_ROOT}/bin/${RTEMS_CC_PREFIX}-gcc${EXE_SUFFIX}      CACHE INTERNAL "C Compiler")
set(CMAKE_CXX_COMPILER  ${RTEMS_TC_ROOT}/bin/${RTEMS_CC_PREFIX}-g++${EXE_SUFFIX}      CACHE INTERNAL "C++ Compiler")
set(CMAKE_OBJCOPY       ${RTEMS_TC_ROOT}/bin/${RTEMS_CC_PREFIX}-objcopy${EXE_SUFFIX}  CACHE INTERNAL "Objcopy")
set(CMAKE_SIZE_UTIL     ${RTEMS_TC_ROOT}/bin/${RTEMS_CC_PREFIX}-size${EXE_SUFFIX}     CACHE INTERNAL "Size")
set(CMAKE_AR            ${RTEMS_TC_ROOT}/bin/${RTEMS_CC_PREFIX}-ar${EXE_SUFFIX}       CACHE INTERNAL "AR")
set(CMAKE_RANLIB        ${RTEMS_TC_ROOT}/bin/${RTEMS_CC_PREFIX}-ranlib${EXE_SUFFIX}   CACHE INTERNAL "Ranlib")
set(CMAKE_LINKER        ${RTEMS_TC_ROOT}/bin/${RTEMS_CC_PREFIX}-ld${EXE_SUFFIX}       CACHE INTERNAL "Linker")

#arm-rtems5-gcc --pipe -DHAVE_CONFIG_H   -I. -I/home/blofeld/projects/rtems-cmake-wrapper/_build_os/arm-rtems5/c/nucleo-stm32f746zg/include 
#-I/home/blofeld/projects/rtems-cmake-wrapper/src/RTEMS/cpukit/include -I/home/blofeld/projects/rtems-cmake-wrapper/src/RTEMS/cpukit/score/cpu/arm/include 
#-I/home/blofeld/projects/rtems-cmake-wrapper/src/RTEMS/cpukit/libnetworking   
#-mcpu=cortex-m7 -mthumb -mfloat-abi=hard -mfpu=fpv5-d16 
#-DSTM32F746xx -O0 -g -ffunction-sections -fdata-sections  -MT libcsupport/src/cfgetospeed.o -MD -MP -MF $depbase.Tpo 
#-c -o libcsupport/src/cfgetospeed.o /home/blofeld/projects/rtems-cmake-wrapper/src/RTEMS/c/src/../../cpukit/libcsupport/src/cfgetospeed.c &&\

set(CPU_FLAGS   "-mcpu=cortex-m7 -march=armv7e-m -mfloat-abi=hard -mfpu=fpv5-d16 -ffunction-sections -fdata-sections -mthumb -mthumb-interwork")
set(OPT_FLAGS   "-ffunction-sections -fdata-sections")
set(RTEMS_FLAGS "-qrtems  -Wall -Wmissing-prototypes -Wimplicit-function-declaration -Wstrict-prototypes -Wnested-externs")

set(CMAKE_C_FLAGS    "${CPU_FLAGS} ${OPT_FLAGS}  ${RTEMS_FLAGS}  -std=gnu99" CACHE INTERNAL "C Flags")
#-qrtems -B${exec_prefix}/lib/ -B${libdir}/ --specs bsp_specs ${CFLAGS}


set(CMAKE_EXE_LINKER_FLAGS_INIT "${CPU_FLAGS} -nodefaultlibs -Wl,--gc-sections -Wl,-print-memory-usage -Wl,-Map=out.map")
set(CMAKE_EXE_LINKER_FLAGS      "${CPU_FLAGS} -nodefaultlibs -Wl,--gc-sections -Wl,-print-memory-usage -Wl,-Map=out.map")

set(CMAKE_EXECUTABLE_SUFFIX_C ".elf")