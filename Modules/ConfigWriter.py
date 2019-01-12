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


from Modules.ParserUtils import *


class CmakeFileWriter():
  logger = ""
  sourceFolder = ""
  cmFile = ""
  topCmFolder = ""

  def __init__(self, logger, sourceFolder, topCmFolder):
    self.logger = logger
    self.sourceFolder = sourceFolder
    self.cmFile = os.path.abspath(self.sourceFolder + "/CMakeLists.txt")
    self.cmFile = open(self.cmFile, 'w')
    self.topCmFolder = topCmFolder

  def writeCmakeFileHeader(self):
    self.cmFile.write("#This is file was generated with bootstrap.py\n\n")

  def writeSourceFiles(self, target):
    sourceFiles = target.getSourceFiles()

    # loop over all source files
    while len(sourceFiles) > 0:
      tmpList = []
      blockOpen = 0
      # get depency depth and names for the first source file
      dependencyDepth = sourceFiles[0].getDependencyDepth()
      dependencyNames = sourceFiles[0].getDependencyNames()

      # now loop over all source files if they match this file
      # if so, add them to the current source block
      for i in range(len(sourceFiles)):
        if sourceFiles[i].getDependencyDepth() == dependencyDepth:
          actDependencyNames = sourceFiles[i].getDependencyNames()

          if compareLists(actDependencyNames, dependencyNames):
            if blockOpen == 0:
              self.__writeBlockHeader(target, dependencyDepth, dependencyNames)
              blockOpen = 1

            self.cmFile.write("  ${PROJECT_SOURCE_DIR}/" + sourceFiles[i].getSourcePath(self.topCmFolder) + "\n")
          else:
            # file does not match so store it for the next pass
            tmpList.append(sourceFiles[i])
        else:
          # file does not match so store it for the next pass
          tmpList.append(sourceFiles[i])

      if blockOpen != 0:
        self.__writeBlockEnd(dependencyDepth, dependencyNames)

      blockOpen = 0
      del sourceFiles
      sourceFiles = tmpList

  def __writeBlockHeader(self, target, dependencyDepth, dependencyNames):
    # if dependencyDepth is 0, there is no dependency,
    # simply add file to source group
    if dependencyDepth == 0:
      self.cmFile.write("set (SRC_{0}\n".format(target.getName().upper()))
    else:
      for i in range(len(dependencyNames) - 1):
        self.cmFile.write("if(${" + dependencyNames[i + 1] + "})\n")

        # special handling for CPU_ blocks
        idx = dependencyNames[i + 1].find("CPU_")
        if -1 != idx:
          cpu = dependencyNames[i + 1]
          searchPath = self.sourceFolder + "/score/cpu/" + cpu[4:].lower()
          self.__addArchitectureIncludePaths(searchPath)

      self.cmFile.write("set (SRC_{0} ${{SRC_{0}}}\n".format(target.getName().upper()))

  def __writeBlockEnd(self, dependencyDepth, dependencyNames):
    self.cmFile.write(")\n")
    self.__writeEndifEnd(dependencyDepth, dependencyNames)

  def __writeEndifEnd(self, dependencyDepth, dependencyNames):
    if dependencyDepth != 0:
      for i in range(len(dependencyNames) - 1):
        self.cmFile.write("endif() # end " + dependencyNames[len(dependencyNames) - 1 - i] + "\n")
    self.cmFile.write("\n")

  def __addArchitectureIncludePaths(self, searchPath):
    headerPath = searchPath
    idx = headerPath.find("cpukit")
    if -1 != idx:
      headerPath = headerPath[idx:]
      headerPath = headerPath.replace("\\", "/")
    self.cmFile.write("set(CPU_HEADER_DIR \"${{PROJECT_SOURCE_DIR}}/{0}\")\n".format(headerPath))
    headerPath = headerPath + "/include"
    self.cmFile.write("include_directories (\"${{PROJECT_SOURCE_DIR}}/{0}\")\n".format(headerPath))

  def writeLibraryTarget(self, target):
    dependencyDepth = target.getDependencyDepth()
    dependencyNames = target.getDependencyNames()

    if dependencyDepth != 0:
      for i in range(len(dependencyNames) - 1):
        self.cmFile.write("if(${{{0}}})\n".format(dependencyNames[i + 1]))

    self.cmFile.write("add_library({0} ${{SRC_{1}}})\n".format(target.getName(), target.getName().upper()))
    self.cmFile.write("target_include_directories({0} PUBLIC $<INSTALL_INTERFACE:include>)\n".format(target.getName()))

    self.__writeTargetCompilerFlags(target)
    self.__writeEndifEnd(dependencyDepth, dependencyNames)

  def __writeTargetCompilerFlags(self, target):
    targetIncludes = []
    outString = ""

    # check for include flags
    cpp_flags = target.getCppFlags()
    for flag in range(len(cpp_flags)):
      idx = cpp_flags[flag].find("-I")
      if 0 == idx:
        flagtxt = cpp_flags[flag][2:]
        flagtxt = flagtxt.replace("$(srcdir)", "${PROJECT_SOURCE_DIR}/cpukit")
        flagtxt = flagtxt.replace("$(RTEMS_SOURCE_ROOT)", "${PROJECT_SOURCE_DIR}")
        flagtxt = flagtxt.replace("\\", "/")
        targetIncludes.append(flagtxt)

    if targetIncludes:
      self.cmFile.write("target_include_directories( {0} PUBLIC\n".format(target.getName()))
      self.cmFile.write("  $<BUILD_INTERFACE:")

    for i in range(len(targetIncludes)):
      outString = outString + targetIncludes[i] + ";"

    if targetIncludes:
      outString = outString[:-1]
      self.cmFile.write("{0}>)\n".format(outString))

    c_flags = target.getCFlags()
    outString = ""
    for flag in range(len(c_flags)):
      idx = c_flags[flag].find("-")
      if 0 == idx:
        self.cmFile.write("target_compile_options({0} PRIVATE {1})\n".format(target.getName(), c_flags[flag]))

  def writeLibraryTargetList(self, listName, target):
    dependencyDepth = target.getDependencyDepth()
    dependencyNames = target.getDependencyNames()

    if dependencyDepth != 0:
      for i in range(len(dependencyNames) - 1):
        self.cmFile.write("if(${{{0}}})\n".format(dependencyNames[i + 1]))

    self.cmFile.write("set({0} ${{{1}}} {2})\n".format(listName, listName, target.getName()))
    self.__writeEndifEnd(dependencyDepth, dependencyNames)

  def writeAllTargetSourceFiles(self, targets):
    for i in range(len(targets)):
      self.writeSourceFiles(targets[i])

  def writeLibraryTargets(self, targets):
    for i in range(len(targets)):
      self.writeLibraryTarget(targets[i])



class KernelCmakeFileWriter(CmakeFileWriter):

  def __init__(self,logger, sourceFolder, topDir):
    super().__init__(logger,sourceFolder,topDir)

  def writeKernelCmakeFileHeader(self):
    self.writeCmakeFileHeader()
    self.cmFile.write("include_directories (\"${PROJECT_SOURCE_DIR}/cpukit/include\")\n")
    self.cmFile.write("add_definitions(-D_BSD_SOURCE) #TODO check this!\n")
    self.cmFile.write("add_definitions(-DHAVE_CONFIG_H)\n")
    self.cmFile.write("\n\n")

  def writeKernelTargetsList(self, targets):
    for i in range(len(targets)):
      self.writeLibraryTargetList("RTEMS_LIBS", targets[i])

  def writeKernelCmakeExport(self,targets):

    self.cmFile.write("set(CPU_HEADER_DIR ${CPU_HEADER_DIR} CACHE INTERNAL \"CPU_HEADER_DIR\")\n")
    self.cmFile.write("set(RTEMS_LIBS ${RTEMS_LIBS} CACHE INTERNAL \"RTEMS_LIBS\")\n")
