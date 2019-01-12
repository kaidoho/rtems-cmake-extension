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
from subprocess import *

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s",datefmt='%Y-%m-%d %H:%M:%S')
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)




def run_cmd(cmd, workdir):
  p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, cwd=workdir)
  output, errors = p.communicate()
  p.wait()

  print(output.decode('utf-8'))
  print(errors.decode('utf-8'))




def run_cmake(tcroot,tcdef,makefile,  installfolder,cmakeBinDir,ninjaBinDir,workdir,\
enable_networking , enable_posix , enable_multiprocessing , enable_smp , \
enable_rtems_debug , enable_cxx , enable_tests , enable_paravirt, enable_drvmgr):
  
  cmd = []
  cmd.append(cmakeBinDir)

  cmd.append("-GEclipse CDT4 - Ninja")
  if ninjaBinDir != "":
    cmd.append("-DCMAKE_MAKE_PROGRAM={0}/ninja".format(ninjaBinDir))
  else:
    cmd.append("-DCMAKE_MAKE_PROGRAM=ninja")
 

  tcroot = args.tcroot.replace('\\', '/')
  cmd.append("-DRTEMS_TC_ROOT={0}".format(tcroot))

  installfolder = installfolder.replace('\\', '/')

  cmd.append("-DCMAKE_INSTALL_PREFIX={0}".format(installfolder))
  cmd.append("-DCMAKE_TOOLCHAIN_FILE={0}".format(tcdef))
  cmd.append("-DCMAKE_VERBOSE_MAKEFILE=ON")
#  cmd.append("-DRTEMS_CPU={0}".format(cpu))
  
  cmd.append("-DRTEMS_NETWORKING={0}".format(str(int(enable_networking))))
  cmd.append("-DRTEMS_POSIX_API={0}".format(str(int(enable_posix))))
  cmd.append("-DRTEMS_MULTIPROCESSING={0}".format(str(int(enable_multiprocessing))))
  cmd.append("-DRTEMS_SMP={0}".format(str(int(enable_smp))))
  cmd.append("-DRTEMS_ENABLE_RTEMS_DEBUG={0}".format(str(int(enable_rtems_debug))))
  cmd.append("-DRTEMS_CXX={0}".format(str(int(enable_cxx))))
  cmd.append("-DRTEMS_TESTS={0}".format(str(int(enable_tests))))
  cmd.append("-DRTEMS_PARAVIRT={0}".format(str(int(enable_paravirt))))
  cmd.append("-DRTEMS_DRVMGR={0}".format(str(int(enable_drvmgr))))

  cmd.append( makefile )    
  print(cmd)
  run_cmd(cmd, workdir)

def run_build(ninjaBinDir,workdir):
  if not os.path.exists(workdir):
    logger.error("Error build folder does not exist. Run config")
    sys.exit()

  if not os.path.exists(args.tcroot + "/bin"):
    logger.error("Error toolchain root directory does not contain bin folder")
    sys.exit()
  
  cmd = []
  
  if ninjaBinDir != "":
    cmd.append(ninjaBinDir + "/ninja")
  else:
    cmd.append("ninja")
    
  cmd.append("-v")
  
  run_cmd(cmd, workdir)

  

def run_install(ninjaBinDir,workdir):
  if not os.path.exists(workdir):
    logger.error("Error build folder does not exist. Run config")
    sys.exit()
    
  cmd = []
  
  if ninjaBinDir != "":
    cmd.append(ninjaBinDir + "/ninja")
  else:
    cmd.append("ninja")
    
  cmd.append("install")
  cmd.append("-v")
    
  run_cmd(cmd, workdir)




if __name__ == '__main__':
  logger = logging.getLogger()
  parser = argparse.ArgumentParser(description='Build RTEMS with CMake')
  optional = parser._action_groups.pop()
  required = parser.add_argument_group('required arguments')
  envArgs  = parser.add_argument_group('optional environment arguments')

  
  envArgs.add_argument('-idir','--prefix',   help='set the directory to which RTEMS is installed (default=../../SystemOS/rtems/_install) ', default='../../SystemOS/rtems/_install')
  envArgs.add_argument('-bdir','--builddir', help='set the directory in which CMake will build RTEMS (default=../../SystemOS/rtems/_build) '  , default='../../SystemOS/rtems/_build')

  envArgs.add_argument('-cdir','--cmakebindir', help='path to the directory containing cmake executable'  , default='C:/Program Files/CMake/bin/cmake')
  envArgs.add_argument('-ndir','--ninjabindir', help='path to the directory containing ninja executable'  , default='d:/projects/ninja')

  envArgs.add_argument('-tdef','--toolchaindefinition', help='the toolchain definition is set based on the targetprc setting. '\
                                                  'use this switch to overwrite the settings given in cmake/cfg_targets.json', default='')
  optional.add_argument('-tcroot',   help='must point to the root directory of the toolchain ',default="D:/projects/arm-rtems5-kernel-5-1")
  optional.add_argument('-bsp',   help='enter the BSP',default="nucleo-stm32f7xx")                                                  
                                                  
  optional.add_argument('--enable-multiprocessing', help='enable multiprocessing interface' \
                          'the multiprocessing interface is a communication '\
                          'interface between different RTEMS instances and '\
                          'allows synchronization of objects via message'\
                          'passing', action='store_true')
  optional.add_argument('--enable-smp', help='enable support for symmetric multiprocessing (SMP)', action='store_true')
  optional.add_argument('--enable-posix', help='enable posix interface', action='store_true')
  optional.add_argument('--enable-networking', help='enable TCP/IP stack', action='store_true')
  optional.add_argument('--enable-cxx', help='enable C++ support', action='store_true')
  optional.add_argument('--enable-tests', help='enable tests (default:samples)', action='store_true')
  optional.add_argument('--enable-rtems-debug', help='enable RTEMS_DEBUG', action='store_true')
  optional.add_argument('--enable-paravirt', help='enable support for paravirtualization (default=no)', action='store_true')
  optional.add_argument('--enable-drvmgr', help='enable Driver Manager at Startup', action='store_true')
  optional.add_argument('--print-targets', help='print all available targets and exit', action='store_true')
  optional.add_argument('-rtems-src','--rtems-source-directory', help="set the path to directory in which " 
                          "you've checked out RTEMS (default=../../SystemOS/rtems/rtesm)",
                          default="../../SystemOS/rtems/rtems")
  
  parser._action_groups.append(optional) 
  args = parser.parse_args()

  scriptLocation = os.path.dirname(os.path.abspath(__file__))
  callLocation =  os.getcwd()
  

  buildtasks = ["config","build", "install"]

  buildtasks = ["config"]


   
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
      if not os.path.exists(args.tcroot + "/bin"):
        logger.error("Error toolchain root directory does not contain bin folder")
        sys.exit()
      else:
        tcroot = args.tcroot + "/bin"


      tcDef = rtemsFolder + "/cmake/toolchain/" + args.bsp + ".cmake"


      
      
      run_cmake( tcroot,
        tcDef,
        rtemsFolder,
        installfolder,
        args.cmakebindir,
        args.ninjabindir,
        buildfolder,
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
      run_build(args.ninjabindir, buildfolder)
      
    if buildtasks[task] == "install":
      run_install(args.ninjabindir, buildfolder)

    


  
 
  
  
