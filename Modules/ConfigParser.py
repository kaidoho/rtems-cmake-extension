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
    self.headerFiles = []
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
  def findTargetSourceFiles(self, target, makefile, makefileToplevel):
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

        if 0 == idx:
          line = line[len(findsting):]
          pMake = os.path.dirname(os.path.abspath(makefileToplevel))
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

      #check if makefile includes irq-sources.am
      with open(makefile, 'r') as f:
        line = f.readline()
        while line:
          idx = line.find('irq-sources.am')
          if -1 != idx:
            self.findTargetSourceFiles(target, self.getSrcDir()+ "/bsps/shared/irq-sources.am" , makefile)
          line = f.readline()

      #check if makefile includes shared-sources.am
      with open(makefile, 'r') as f:
        line = f.readline()
        while line:
          idx = line.find('shared-sources.am')
          if -1 != idx:
            self.findTargetSourceFiles(target, self.getSrcDir()+ "/bsps/shared/shared-sources.am" , makefile)
          line = f.readline()

  def findTargetHeaderFiles(self, headerPath, destPath):
    headerFile = headerPath + "/headers.am"
    linenumber = 1
    headerFiles = []
    searchString = "_HEADERS += "
    self.logger.info("Headerfile: {0}".format(headerFile))

    with open(headerFile, 'r') as f:
      line = f.readline()
      while line:
        idx = line.find(searchString)
        if -1 != idx:
          line = line[idx + len(searchString):]
          line = line.rstrip()
          idxN = line.rfind("../")
          if - 1 != idxN:
            line = line[idxN +len("../"):]
          headerFiles.append(destPath + line)
        linenumber = linenumber + 1;
        line = f.readline()
    return headerFiles

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
  headerFilesNetworking = []
  headerFilesKernel = []
  def __init__(self, topDir, logger):
    super().__init__(logger)
    self.setSrcDir(topDir)
    self.makeFile = self.getSrcDir() + "/cpukit/Makefile.am"
    self.headerFilesNetworking = []
    self.headerFilesKernel = []
    return

  def parseMakefile(self):
    self.logger.info("Starting to parse Kernel Makefile: {0}".format(self.makeFile))
    self.findTargets("project_lib_LIBRARIES += ")

    self.headerFilesKernel = self.findTargetHeaderFiles(os.path.dirname(os.path.abspath(self.makeFile)), "${PROJECT_SOURCE_DIR}/cpukit/")
    self.headerFilesNetworking = self.findTargetHeaderFiles(os.path.dirname(os.path.abspath(self.makeFile))+"/libnetworking", "${PROJECT_SOURCE_DIR}/cpukit/")

    for i in range(len(self.libraryObjs)):
      self.findTargetDependencies(self.libraryObjs[i], self.makeFile)
      self.findTargetSourceFiles(self.libraryObjs[i], self.makeFile, self.makeFile)
      self.findTargetCompilerFlags(self.libraryObjs[i], self.makeFile)
      self.logger.info("Found lib: {0} contains {1} source files".format(self.libraryObjs[i].getName(),
                                                                         self.libraryObjs[i].getNumberOfSourceFiles()))

    mWriter = KernelCmakeFileWriter(self.logger, os.path.dirname(os.path.abspath(self.makeFile)), self.getSrcDir())
    mWriter.writeKernelCmakeFileHeader()
    mWriter.writeAllTargetSourceFiles(self.libraryObjs)
    mWriter.writeLibraryTargets(self.libraryObjs)
    mWriter.writeKernelTargetsList(self.libraryObjs)

    mWriter.writeInstallHeaders(self.headerFilesKernel,"/include/")
    mWriter.writeInstallHeaders(self.headerFilesNetworking,"/libnetworking/")
    mWriter.writeKernelCmakeExport(self.libraryObjs)


class BspParser(CfgParser):
  headerFilesBsp = []

  def __init__(self, topDir, makefileDir, logger):
    super().__init__(logger)
    self.setSrcDir(topDir)
    self.makeFile = makefileDir + "/Makefile.am"
    self.headerFilesBsp = []
    return

  def parseMakefile(self):
    self.logger.info("Starting to parse BSP Makefile: {0}".format(self.makeFile))
    self.findTargets("project_lib_LIBRARIES = ")

    for i in range(len(self.libraryObjs)):
      self.findTargetDependencies(self.libraryObjs[i], self.makeFile)
      self.findTargetSourceFiles(self.libraryObjs[i], self.makeFile, self.makeFile)
      self.findTargetCompilerFlags(self.libraryObjs[i], self.makeFile)
      self.logger.info("Found lib: {0} contains {1} source files".format(self.libraryObjs[i].getName(),
                                                                         self.libraryObjs[i].getNumberOfSourceFiles()))

    # write bspopts.h.in file
    cfgFile = os.path.dirname(os.path.abspath(self.makeFile))
    cfgFile = cfgFile + "/configure.ac"
    bspOptsFile = os.path.dirname(os.path.abspath(self.makeFile))
    bspOptsFile = bspOptsFile + "/bspopts.h.in"
    bspOptsFile = open(bspOptsFile, 'w')
    if 1 == self.createCfgInBspOpts(cfgFile, bspOptsFile):
      cfgFile = self.getSrcDir() + "/c/src/aclocal/bsp-bspcleanup-options.m4"
      self.appendCfgInBspOpts(cfgFile, bspOptsFile)
    self.writeCfgInBspOptsEnd(bspOptsFile)

    bspName = os.path.dirname(self.makeFile)
    bspName = os.path.basename(bspName)
    cpuName = os.path.dirname(os.path.dirname(self.makeFile))
    cpuName = os.path.basename(cpuName)

    sourceFolder = os.path.abspath(self.getSrcDir() + "/bsps/" + cpuName + "/" + bspName)


    self.headerFilesBsp = self.findTargetHeaderFiles(sourceFolder,
                                           "${PROJECT_SOURCE_DIR}"+ "/")


    mWriter = BspCmakeFileWriter(self.logger, sourceFolder, self.getSrcDir())
    mWriter.writeBspCmakeFileHeader()

    bspOptsFile = os.path.dirname(os.path.abspath(self.makeFile))
    cfgFile = bspOptsFile + "/configure.ac"
    if 1 == mWriter.writeBspOptsFile(cfgFile):
      cfgFile = self.getSrcDir() + "/c/src/aclocal/bsp-bspcleanup-options.m4"
    mWriter.writeBspOptsFile(cfgFile)

    mWriter.writeAllTargetSourceFiles(self.libraryObjs)
    mWriter.writeLibraryTargets(self.libraryObjs)
    mWriter.writeInstallHeadersBsp(self.headerFilesBsp, "/include/")
    mWriter.writeBspCmakeExport(self.libraryObjs)

  def appendCfgInBspOpts(self, cfgFile, outFile):
    names = []

    with open(cfgFile, 'r') as f:
      line = f.readline()

      while line:
        line = line.rstrip()
        searchString = "RTEMS_BSPOPTS_SET("

        idx = line.find(searchString)
        if -1 != idx:
          line = line[len(searchString) + 1:]
          names.append(line[:line.find("]")])
        line = f.readline()

    names = list(set(names))

    for i in range(len(names)):
      self.writeCfgInBspOptsSwitch(cfgFile, outFile, names[i])

  def writeCfgInBspOptsHeader(self, outFile):
    outFile.write("/* BSP dependent options file */\n")
    outFile.write("/* automatically generated -- DO NOT EDIT!! */\n\n")
    outFile.write("#ifndef __BSP_OPTIONS_H\n")
    outFile.write("#define __BSP_OPTIONS_H\n\n")

    outFile.write("// The RTEMS BSP name\n")
    outFile.write("#cmakedefine RTEMS_BSP @RTEMS_BSP@\n\n")

    outFile.write("// If defined, then the BSP Framework will put a non - zero pattern into \n")
    outFile.write("// the RTEMS Workspace and C program heap.This should assist in finding \n")
    outFile.write("// code that assumes memory starts set to zero \n")

    outFile.write("#cmakedefine01 BSP_DIRTY_MEMORY @BSP_DIRTY_MEMORY@\n\n")


  def writeCfgInBspOptsEnd(self, outFile):
    outFile.write("\n#endif // __BSP_OPTIONS_H\n")

  def writeCfgInBspOptsSwitch(self, cfgFile, outFile, name):

    found = 0
    with open(cfgFile, 'r') as f:
      line = f.readline()

      while line:
        line = line.rstrip()
        searchString = "RTEMS_BSPOPTS_HELP("

        idx = line.find(searchString)
        if -1 != idx:
          line = line[len(searchString) + 1:]
          idx = line.find(name)
          if -1 != idx:
            line = line[len(name) + 3:]
            line = line[:line.find("]")]
            outFile.write("//{0} {1}\n".format(name, line))
            outFile.write("#cmakedefine {0} @{1}@\n\n".format(name, name))
            found = 1

        line = f.readline()

    if 0 == found:
      outFile.write("// {0} - not in BSP CONFIG\n".format(name))
      outFile.write("#cmakedefine {0} @{1}@\n\n".format(name, name))

  def createCfgInBspOpts(self, cfgFile, outFile):

    self.writeCfgInBspOptsHeader(outFile)
    self.appendCfgInBspOpts(cfgFile, outFile)

    with open(cfgFile, 'r') as f:
      line = f.readline()

      while line:
        searchString = "RTEMS_BSP_CLEANUP_OPTIONS"

        idx = line.find(searchString)
        if -1 != idx:
          return 1

        line = f.readline()

    return 0
