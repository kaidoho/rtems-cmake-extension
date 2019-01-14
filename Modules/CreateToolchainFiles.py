# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (C) 2018, M.B.Moessner
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

from Modules.Utils import *

class BspSourceFolder():
  logger = ""
  __sourceFolder = ""
  __cpu = ""

  def __init__(self, logger, sourceFolder, cpu):
    self.logger = logger
    self.__sourceFolder = sourceFolder
    self.__cpu = cpu

  def getSourceFolder(self):
    return self.__sourceFolder

  def getCpu(self):
    return self.__cpu



def get_flags(searchString, cfgFile):
  flags = []
  searchStringA = searchString + " ="
  searchStringB = searchString + " +="
  with open(cfgFile, 'r') as f:
    line = f.readline()
    while line:
      line = line.rstrip()

      idx = line.find(searchStringA)
      if -1 != idx:
        flags.append(line[idx+len(searchStringA):])
      idx = line.find(searchStringB)
      if -1 != idx:
        flags.append(line[idx+len(searchStringB):])

      line = f.readline()

  return ''.join(str(s) for s in flags)


def write_toolchain_file(tcDefFolder, cfgFile, bspName, cpu):

  tcOutFile = tcDefFolder + "/" + bspName +".cmake"
  f = open(tcOutFile, "w")

  f.write("set(CMAKE_SYSTEM_NAME  Generic)\n")
  f.write("SET(CMAKE_SYSTEM_PROCESSOR {0})\n".format(cpu))
  f.write("SET(CMAKE_CROSSCOMPILING  1)\n\n")

  f.write("set(RTEMS_CPU  \"{0}\")\n".format(cpu))
  f.write("set(RTEMS_CC_PREFIX  \"{0}-rtems5\")\n\n".format(cpu))

  f.write("IF(WIN32)\n")
  f.write("  set(EXE_SUFFIX  \".exe\")\n")
  f.write("ELSE()\n")
  f.write("  set(EXE_SUFFIX  \"\")\n")
  f.write("ENDIF()\n\n")

  f.write("set(CMAKE_C_COMPILER  ${RTEMS_TC_ROOT}/bin/${RTEMS_CC_PREFIX}-gcc${EXE_SUFFIX} "
          "CACHE INTERNAL \"C Compiler\")\n")
  f.write("set(CMAKE_CXX_COMPILER  ${RTEMS_TC_ROOT}/bin/${RTEMS_CC_PREFIX}-g++${EXE_SUFFIX} "
          "CACHE INTERNAL \"C++ Compiler\")\n")
  f.write("set(CMAKE_OBJCOPY  ${RTEMS_TC_ROOT}/bin/${RTEMS_CC_PREFIX}-objcopy${EXE_SUFFIX} "
          "CACHE INTERNAL \"Objcopy\")\n")
  f.write("set(CMAKE_SIZE_UTIL  ${RTEMS_TC_ROOT}/bin/${RTEMS_CC_PREFIX}-size${EXE_SUFFIX} "
          "CACHE INTERNAL \"Size\")\n")
  f.write("set(CMAKE_AR  ${RTEMS_TC_ROOT}/bin/${RTEMS_CC_PREFIX}-ar${EXE_SUFFIX} "
          "CACHE INTERNAL \"Archiver\")\n")
  f.write("set(CMAKE_RANLIB  ${RTEMS_TC_ROOT}/bin/${RTEMS_CC_PREFIX}-ranlib${EXE_SUFFIX} "
          "CACHE INTERNAL \"Ranlib\")\n")
  f.write("set(CMAKE_LINKER  ${RTEMS_TC_ROOT}/bin/${RTEMS_CC_PREFIX}-ld${EXE_SUFFIX} "
          "CACHE INTERNAL \"Linker\")\n\n")


  cpu_flags = get_flags("CPU_CFLAGS",cfgFile)
  opt_flags = get_flags("CFLAGS_OPTIMIZE_V", cfgFile)
  ld_flags = get_flags("LDFLAGS", cfgFile)
  logger.info(cpu_flags)

  f.write("set(CPU_FLAGS \"{0}\")\n".format(cpu_flags))
  f.write("set(OPT_FLAGS \"-ffunction-sections -fdata-sections {0}\")\n".format(opt_flags))
  f.write("set(AUX_FLAGS \"\")\n")
  f.write("set(RTEMS_FLAGS \"-Wall -Wmissing-prototypes -Wimplicit-function-declaration -Wstrict-prototypes " 
          " -Wnested-externs\")\n")
  f.write("set(RTEMS_LINK_FLAGS \"-B${BSP_SPEC_FOLDER} -qrtems --specs bsp_specs -Wl,--wrap=printf" 
          " -Wl,--wrap=puts -Wl,--wrap=putchar\")\n\n")
  f.write("set(CMAKE_C_FLAGS \"${CPU_FLAGS} ${AUX_FLAGS} ${OPT_FLAGS} ${RTEMS_FLAGS} -std=gnu99\" "
          " CACHE INTERNAL \"C Flags\")\n")
  f.write("set(CMAKE_ASM_FLAGS \"${CPU_FLAGS} -x assembler-with-cpp\")\n")
  f.write("set(CMAKE_EXE_LINKER_FLAGS \"-Wl,--gc-sections -Wl,-print-memory-usage -Wl,-Map=out.map\")\n")
  f.close()

  return


def get_inner_cfg_file(cfgFile,bspName):
  with open(cfgFile, 'r') as f:
    line = f.readline()
    while line:
      line = line.rstrip()
      searchString = ".inc"
      idx = line.find(searchString)
      if -1 != idx:
        idxx = line.rfind("/")
        cfgFile = os.path.dirname(cfgFile) + line[idxx:idx + 4]
        get_inner_cfg_file(cfgFile, bspName)
        break
      line = f.readline()

  return cfgFile

def parse_config_file(tcDefFolder, cfgFile,bspName,cpu):
  cfgFile = get_inner_cfg_file(cfgFile,bspName)
  logger.info("{0} {1}".format(bspName,cfgFile))

  write_toolchain_file(tcDefFolder, cfgFile, bspName,cpu)


def check_toolchain_files(rtemsFolder, tcDefFolder):
  bspToolchains = []
  searchPath = rtemsFolder + "/c/src/lib/libbsp/**/Makefile.am"
  tcDefFolderTmp = tcDefFolder +"/_tmp"
  if os.path.exists(tcDefFolderTmp):
    shutil.rmtree(tcDefFolderTmp, ignore_errors=True)
  os.makedirs(tcDefFolderTmp, exist_ok=True)

  for filename in glob.iglob(searchPath, recursive=True):
    bspName = filename[filename.find("libbsp") + 7:]
    bspName = bspName[:bspName.find("Makefile.am")]
    bspName = bspName[:-1]
    bspName = bspName.replace("\\", "/")
    idx = bspName.find("/")
    idxx = bspName.rfind("/")
    if -1 != idx:
      if idxx == idx:
        cpu = bspName[:idx]
        bspToolchains.append(BspSourceFolder(logger, rtemsFolder + "/bsps/" + bspName, cpu))

  for i in range(len(bspToolchains)):
    sourceFolder = bspToolchains[i].getSourceFolder() + "/config/*.cfg"
    for filename in glob.iglob(sourceFolder, recursive=True):
      idx = filename.find("testsuite")
      if -1 == idx:
        bspName= os.path.basename(filename).replace(".cfg", "")

        parse_config_file(tcDefFolderTmp, filename,bspName,bspToolchains[i].getCpu() )










