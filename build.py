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



import sys
import os
import argparse
import json
import shutil
import logging
import glob

from Modules.Utils import *



def run_cmake(tcRoot, tcDef, rtemsFolder, installFolder, cmakeBin, ninjaBin, 
              workDir, rtemsCpu, bspName, enable_networking, enable_posix, 
              enable_multiprocessing, enable_smp , enable_rtems_debug, 
              enable_cxx, enable_tests, enable_paravirt, enable_drvmgr):

  cmd = []
  cmd.append(cmakeBin)
  #cmd.append("--debug-trycompile")

  tcRoot = tcRoot.replace("\\", "/")
  installFolder = installFolder.replace("\\", "/")

  #searchPath = rtemsFolder + "/**/"+bspName+".cfg"
  #logger.info("Search Path {0}".format(searchPath))

  #for filename in glob.iglob( searchPath, recursive=True):
  #  bspFolder = filename
  #  break

  
  #if not os.path.isfile(bspFolder):
   # logger.error("BSP {0} not found in {1}.".format(bspName,rtemsFolder))
   # sys.exit()
  #bspFolder = os.path.dirname(bspFolder)
  #bspFolder = os.path.abspath(bspFolder + "/../")
  #bspFolder = os.path.basename(bspFolder)


  cmd.append("-GEclipse CDT4 - Ninja")
  cmd.append("-DCMAKE_MAKE_PROGRAM={0}".format(ninjaBin))
  cmd.append("-DPREBUILD_LIB_DIR={0}".format(workDir +"/precompile/lib"))
  cmd.append("-DPREBUILD_LINKER_DIR={0}".format(workDir +"/precompile/linker"))
  #cmd.append("-DRTEMS_CPU={0}".format(rtemsCpu))
  #cmd.append("-DRTEMS_BSP={0}".format(bspName))
  cmd.append("-DRTEMS_TC_ROOT={0}".format(tcRoot))
  cmd.append("-DCMAKE_INSTALL_PREFIX={0}".format(installFolder))
  cmd.append("-DCMAKE_TOOLCHAIN_FILE={0}".format(tcDef))
  cmd.append("-DCMAKE_VERBOSE_MAKEFILE=ON")
  #cmd.append("-DRTEMS_BSP_DIR_NAME={0}".format(bspFolder))
  cmd.append("-DRTEMS_NETWORKING={0}".format(str(int(enable_networking))))
  cmd.append("-DRTEMS_POSIX_API={0}".format(str(int(enable_posix))))
  cmd.append("-DRTEMS_MULTIPROCESSING={0}".format(str(int(enable_multiprocessing))))
  cmd.append("-DRTEMS_SMP={0}".format(str(int(enable_smp))))
  cmd.append("-DRTEMS_ENABLE_RTEMS_DEBUG={0}".format(str(int(enable_rtems_debug))))
  cmd.append("-DRTEMS_CXX={0}".format(str(int(enable_cxx))))
  cmd.append("-DRTEMS_TESTS={0}".format(str(int(enable_tests))))
  cmd.append("-DRTEMS_PARAVIRT={0}".format(str(int(enable_paravirt))))
  cmd.append("-DRTEMS_DRVMGR={0}".format(str(int(enable_drvmgr))))

  cmd.append( rtemsFolder )
  #print(cmd)
  run_cmd(cmd, workDir)




def find_cpu_of_bsp(rtemsFolder, bspName):
  logger.info("Search for BSP")
  bspFolder = ""
  searchPath = rtemsFolder + "/**/"+bspName+".cfg"
  logger.info("Search Path {0}".format(searchPath))

  for filename in glob.iglob( searchPath, recursive=True):
    bspFolder = filename
    break

  if not os.path.isfile(bspFolder):
    logger.error("BSP {0} not found in {1}.".format(bspName,rtemsFolder))
    sys.exit()
  bspFolder = os.path.dirname(bspFolder)
  bspFolder = os.path.abspath(bspFolder + "/../../")
  cpu = os.path.basename(bspFolder)
  logger.info("BSP {} found uses CPU {}".format(bspName,cpu))
  return cpu


def precompile_start_file(tcroot, cpu,startFile,cflags):
  cmd = []
  cmd.append(tcroot +"/"+ cpu+"-rtems5-gcc" )
  cmd.append(cflags)
  cmd.append("-c " + startFile)

  print(cmd)
  run_cmd(cmd, os.path.dirname(startFile))

  return

def prepare_build(tcroot, rtemsFolder, bspName,buildfolder,cpu):
  bspFolder = ""
  cfgFile = ""

  precompileFolder = buildfolder + "/precompile"

  logger.info("Create pre-compile folder: {0}".format(precompileFolder))
  if os.path.exists(precompileFolder):
    shutil.rmtree(precompileFolder, ignore_errors=True)
  os.makedirs(precompileFolder, exist_ok=True)

  linkFolder = precompileFolder  + "/linker"
  libFolder = precompileFolder  + "/lib"

  os.makedirs(linkFolder, exist_ok=True)
  os.makedirs(libFolder, exist_ok=True)

  searchPath = rtemsFolder +"/bsps/"+cpu+ "/shared/start/**/linkcmds.*"

  for filename in glob.iglob( searchPath, recursive=True):
    logger.info("Copy file: {0}".format(filename))
    shutil.copy2(filename, linkFolder )

  searchPath = rtemsFolder + "/**/"+bspName+".cfg"
  logger.info("Search Path {0}".format(searchPath))

  for filename in glob.iglob( searchPath, recursive=True):
    bspFolder = os.path.dirname(filename)
    cfgFile = filename
    break

    linkcmdsFile = bspFolder + "/../start/linkcmds." + bspName

    if  os.path.isfile(linkcmdsFile):
      shutil.copy2(filename, linkFolder + "/linkcmds" )
    else:
      logger.info("No file linkcmds.{} found!".format(bspName))
      logger.info("Pre-Compile will fail!")
      logger.info("Perhaps .in file or linkcmds without extension is used")

    startFile = libFolder + "/start.S"

    f = open(startFile, "w")
    f.write(".globl	_start\n")
    f.write(".globl	bsp_start_vector_table_begin\n")
    f.write(".globl	bsp_start_vector_table_end\n")
    f.write(".globl	bsp_start_vector_table_size\n")
    f.write(".globl	bsp_vector_table_size\n")
    f.write(".section	\".bsp_start_text\", \"ax\"\n")
    f.write("_start:\n")
    f.write("\tbl  main\n\n")
    f.close()

    cflags = ""

    with open(cfgFile, "r") as f:
      line = f.readline()
      searchString = "CPU_CFLAGS = "

      while line:
        idx = line.find(searchString)
        if -1 != idx:
          # get the library name and remove preceeding "lib"
          cflags = line[len(searchString):]
        line = f.readline()

    logger.info("CFLAGS {0}".format(cflags))


    #precompile_start_file(tcroot, cpu,startFile,cflags.rstrip())


if __name__ == "__main__":
  
  parser = argparse.ArgumentParser(description="Build RTEMS with CMake")
  optArgs = parser._action_groups.pop()
  required = parser.add_argument_group("required arguments")
  envArgs  = parser.add_argument_group("optional environment arguments")


  envArgs.add_argument("-idir","--prefix",   help="set the directory to which RTEMS is installed" 
                        " (default=build/_install)", default="build/rtems/_install")
  envArgs.add_argument("-bdir","--builddir", help="set the directory in which CMake will build RTEMS" 
                        "(default=build/_build) "  , default="build/_build")
  if sys.platform == "linux" or sys.platform == "linux2":

    envArgs.add_argument("-cdir","--cmakeBin", help="path to the directory containing cmake executable",
                         default="cmake")
    envArgs.add_argument("-ndir","--ninjaBin", help="path to the directory containing ninja executable",
                         default="ninja")
    optArgs.add_argument("-tcRoot",   help="must point to the root directory of the toolchain ",
                         default="/home/blofeld/RTEMS-Toolchains")
  else:
    envArgs.add_argument("-cdir","--cmakeBin", help="path to the directory containing cmake executable",
                         default="C:/Program Files/CMake/bin/cmake.exe")
    envArgs.add_argument("-ndir","--ninjaBin", help="path to the directory containing ninja executable",
                         default="D:/projects/ninja/ninja.exe")
    optArgs.add_argument("-tcRoot",   help="must point to the root directory of the toolchain ",
                         default="D:/home/scrapmetal/tools/rtems")

  optArgs.add_argument("-bsp",   help="enter the BSP",default="rtems5-stm32f7x7")#"nucleo-stm32f746zg") #"stm32f4")#

  optArgs.add_argument("--enable-multiprocessing", help="enable multiprocessing interface" \
                          "the multiprocessing interface is a communication "\
                          "interface between different RTEMS instances and "\
                          "allows synchronization of objects via message"\
                          "passing", action="store_true")
  optArgs.add_argument("--enable-smp", help="enable support for symmetric multiprocessing (SMP)", action="store_true")
  optArgs.add_argument("--enable-posix", help="enable posix interface", action="store_true")
  optArgs.add_argument("--enable-networking", help="enable TCP/IP stack", action="store_true")
  optArgs.add_argument("--enable-cxx", help="enable C++ support", action="store_true")
  optArgs.add_argument("--enable-tests", help="enable tests (default:samples)", action="store_true")
  optArgs.add_argument("--enable-rtems-debug", help="enable RTEMS_DEBUG", action="store_true")
  optArgs.add_argument("--enable-paravirt", help="enable support for paravirtualization (default=no)", action="store_true")
  optArgs.add_argument("--enable-drvmgr", help="enable Driver Manager at Startup", action="store_true")
  optArgs.add_argument("--print-targets", help="print all available targets and exit", action="store_true")
  optArgs.add_argument("-rtems-src","--rtems-source-directory", help="set the path to directory in which "
                          "you have checked out RTEMS (default=../rtems)",
                          default="../rtems")

  parser._action_groups.append(optArgs)
  args = parser.parse_args()

  scriptLocation = os.path.dirname(os.path.abspath(__file__))
  callLocation =  os.getcwd()


  buildtasks = ["config","build", "install"]

 # buildtasks = ["config","build"]



  if os.path.isabs(args.builddir):
    buildfolder = args.builddir
  else:
    buildfolder = callLocation
    buildfolder = buildfolder  + "/" + args.builddir + "/"+ args.bsp

  if os.path.isabs(args.prefix):
    installfolder = args.prefix
  else:
    installfolder = callLocation
    installfolder = installfolder + "/" + args.prefix + "/" +  args.bsp

  if os.path.isabs(args.rtems_source_directory):
    rtemsFolder = args.rtems_source_directory
  else:
    rtemsFolder = os.getcwd()
    rtemsFolder = rtemsFolder + "/" + args.rtems_source_directory

  rtemsFolder = rtemsFolder.replace("\\", "/")

  #rtemsCpu = find_cpu_of_bsp(rtemsFolder, args.bsp)
  rtemsCpu="x"
  for task in range(len(buildtasks)):

    if buildtasks[task] == "config":
      #create a build folder, remove build folder if it exists
      if os.path.exists(buildfolder):
          shutil.rmtree(buildfolder, ignore_errors=True)
      os.makedirs(buildfolder, exist_ok=True)
      #create a install folder, remove install folder if it exists
      if os.path.exists(installfolder):
          shutil.rmtree(installfolder, ignore_errors=True)
      os.makedirs(installfolder, exist_ok=True)


      #check if the toolchain exists
      if not os.path.exists(args.tcRoot + "/bin"):
        logger.error("Error toolchain root directory does not contain bin folder")
        sys.exit()
      else:
        tcRoot = args.tcRoot


      tcDef = rtemsFolder + "/cmake/toolchain/" + args.bsp + ".cmake"

      #prepare_build(tcRoot, rtemsFolder, args.bsp, buildfolder,rtemsCpu)



      run_cmake(tcRoot,
                tcDef,
                rtemsFolder,
                installfolder,
                args.cmakeBin,
                args.ninjaBin,
                buildfolder,
                rtemsCpu,
                args.bsp,
                args.enable_networking,
                args.enable_posix,
                args.enable_multiprocessing,
                args.enable_smp,
                args.enable_rtems_debug,
                args.enable_cxx,
                args.enable_tests,
                args.enable_paravirt,
                args.enable_drvmgr)

    if buildtasks[task] == "build":
      run_build(args.ninjaBin, buildfolder)

    if buildtasks[task] == "install":
      run_install(args.ninjaBin, buildfolder)
