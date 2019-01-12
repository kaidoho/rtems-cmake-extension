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


from Modules.ConfigWriter import *

class CfgParser():
  logger = ""
  __sourceDir = ""
  makeFile = ""
  libraryObjs = []



  def __init__(self, logger):
    super().__init__()
    self.logger = logger
    self.makeFile = ""
    self.__sourceDir = ""
    self.libraryObjs = []
    return

  def setSrcDir(self, dir):
    self.__sourceDir = dir
  def getSrcDir(self):
    return self.__sourceDir

  # Go through the Makefile an find all
  # libraries build within it
  def findTargets(self, searchString):
    libraryObjs = []
    mpath = os.path.dirname(os.path.abspath(self.makeFile))

    with open(self.makeFile, 'r') as f:
      line = f.readline()
      cnt = 1
      while line:
        idx = line.find(searchString)
        if -1 != idx:
          # get the library name and remove preceeding "lib"
          libName = line[idx + len(searchString) + 3:]
          libName = libName[:libName.find(".a")]
          sb = LibraryTarget(self.logger, libName, self.__sourceDir)
          self.libraryObjs.append(sb)

        line = f.readline()
        cnt += 1
    return

  # Check if this target is only build if a certain build switch is present (e.g. --enable-networking)
  # Additionally, get the depth of the "if" blocks in which this lib is contained.
  def findTargetDependencies(self, target, makefile):
    target.findLibraryDependencies(makefile)

  # Find all source files which belong to this target. Some source may only be added if a certain build switch
  # (e.g. --enable-networking) was given. Additionally, get the depth of the "if" blocks in which this lib is
  # contained.
  def findTargetSourceFiles(self, target, makefile):
    linenumber = 1
    nFiles = 0
    with open(makefile, 'r') as f:
      line = f.readline()

      dependencyDepth = 0;
      dependencyNames = ['empty']

      while line:
        line = line.rstrip()
        idx = line.find("if ")
        if 0 == idx:
          dependencyDepth = dependencyDepth + 1;
          dependencyNames.append(line[3:])

        idx = line.find('endif')
        if 0 == idx:
          dependencyDepth = dependencyDepth - 1;
          del dependencyNames[-1]

        findsting = "lib" + target.getName() + "_a_SOURCES += "
        idx = line.find(findsting)

        if -1 != idx:
          line = line[len(findsting):]
          pMake = os.path.dirname(os.path.abspath(makefile))
          line = pMake + "/" + line
          sfile = SourceFile(self.logger, os.path.abspath(line))
          sfile.setDependencyDepth(dependencyDepth)
          sfile.setDependencyNames(dependencyNames[:])
          target.addSourceFile(sfile)
          nFiles = nFiles + 1
        if dependencyDepth < 0:
          self.logger.error("ERROR: this should not happen at line " + str(linenumber))
          sys.exit()
        linenumber = linenumber + 1;
        line = f.readline()

  def findTargetCompilerFlags(self, target, makefile):
    linenumber = 1
    nFiles = 0
    c_flags = []
    cpp_flags = []

    with open(makefile, 'r') as f:
      line = f.readline()

      findsting_c = "lib" + target.getName() + "_a_CFLAGS += "

      while line:
        line = line.rstrip()
        idx = line.find(findsting_c)
        if -1 != idx:
          line = line[len(findsting_c):]
          c_flags.append(line)
        else:
          findsting_cpp = "lib" + target.getName() + "_a_CPPFLAGS += "
          idx = line.find(findsting_cpp)
          if -1 != idx:
            line = line[len(findsting_cpp):]
            cpp_flags.append(line)
        linenumber = linenumber + 1;
        line = f.readline()

    target.setCompilerFlags(c_flags, cpp_flags)

class CpukitParser(CfgParser):

  def __init__(self, topDir, logger):
    super().__init__(logger)
    self.setSrcDir(topDir)
    self.makeFile=self.getSrcDir() + "/cpukit/Makefile.am"
    return

  def parseMakefile(self):
    self.logger.info("Starting to parse Kernel Makefile: {0}".format(self.makeFile))
    self.findTargets("project_lib_LIBRARIES += ")

    for i in range(len(self.libraryObjs)):
      self.findTargetDependencies(self.libraryObjs[i], self.makeFile)
      self.findTargetSourceFiles(self.libraryObjs[i], self.makeFile)
      self.findTargetCompilerFlags(self.libraryObjs[i], self.makeFile)
      self.logger.info("Found lib: {0} contains {1} source files".format(self.libraryObjs[i].getName(),
                                                                         self.libraryObjs[i].getNumberOfSourceFiles()))


    mWriter = KernelCmakeFileWriter(self.logger, os.path.dirname(os.path.abspath(self.makeFile)), self.getSrcDir() )
    mWriter.writeKernelCmakeFileHeader()
    mWriter.writeAllTargetSourceFiles(self.libraryObjs)
    mWriter.writeLibraryTargets(self.libraryObjs)
    mWriter.writeKernelTargetsList(self.libraryObjs)
    mWriter.writeKernelCmakeExport(self.libraryObjs)
