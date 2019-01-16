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
      self.cmFile.write("target_include_directories( {0} PRIVATE\n".format(target.getName()))
      self.cmFile.write("  $<BUILD_INTERFACE:;")

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

  def writeInstallHeadersBlock(self, blockName, headers, baseName):
    self.cmFile.write("set(INSTALL_HEADERS{0} \n".format(blockName))
    for i in range(len(headers)):
      self.cmFile.write("{0}\n".format(headers[i]))
    self.cmFile.write(") \n")
    idxL = headers[0].find(baseName) +len(baseName)
    idxR = headers[0].rfind("/")
    dest = "${CMAKE_INSTALL_PREFIX}/include/" + headers[0][idxL:idxR]
    self.cmFile.write("install(FILES ${{INSTALL_HEADERS{0}}} DESTINATION {1})\n\n".format(blockName,dest))

  def writeInstallHeaders(self, headers, baseName):

    blockHeaders = []
    saveHeaders = []

    searchString = baseName
    baseIdx = headers[0].find(searchString)
    baseIdx = baseIdx + len(searchString)

    for i in range(len(headers)):
      searchString = baseName
      if -1 == headers[i].find('/', baseIdx):
        if len(headers[i]) > baseIdx:
          blockHeaders.append(headers[i])
        else:
          saveHeaders.append(headers[i])
      else:
        saveHeaders.append(headers[i])
    self.writeInstallHeadersBlock(baseName.replace("/", "_") + searchString.replace("/", "_"), blockHeaders,baseName)

    headers = saveHeaders

    # loop over all source files
    while len(headers) > 0:
      saveHeaders = []
      blockHeaders = []
      rIdx = headers[0].rfind("/")
      searchString = headers[0]
      searchString = searchString[baseIdx-1:rIdx]
      for i in range(len(headers)):
        rIdxAct = headers[i].rfind("/")
        if rIdxAct == rIdx:
          idx = headers[i].find(searchString,baseIdx-1)
          if idx == baseIdx-1:
            blockHeaders.append(headers[i])
          else:
            saveHeaders.append(headers[i])
        else:
          saveHeaders.append(headers[i])
      if blockHeaders:
        self.writeInstallHeadersBlock(baseName.replace("/", "_") + searchString.replace("/", "_"), blockHeaders,baseName)
      headers = saveHeaders

  def writeInstallHeadersBsp(self, headers, baseName):
    saveHeaders = []
    for i in range(len(headers)):
      idx = headers[i].find("/bspopts.h")
      if -1 == idx:
        saveHeaders.append(headers[i])

    self.writeInstallHeaders(saveHeaders, baseName)


class KernelCmakeFileWriter(CmakeFileWriter):

  def __init__(self,logger, sourceFolder, topDir):
    super().__init__(logger,sourceFolder,topDir)

  def writeKernelCmakeFileHeader(self):
    self.writeCmakeFileHeader()
    self.cmFile.write("include_directories (\"${PROJECT_SOURCE_DIR}/cpukit/include\")\n")
    self.cmFile.write("add_definitions(-DHAVE_CONFIG_H)\n")
    self.cmFile.write("\n\n")

  def writeKernelTargetsList(self, targets):
    for i in range(len(targets)):
      self.writeLibraryTargetList("RTEMS_LIBS", targets[i])

  def writeKernelCmakeExport(self,targets):

    self.cmFile.write("include(CMakePackageConfigHelpers)\n\n")

    self.cmFile.write("set(CPU_HEADER_DIR ${CPU_HEADER_DIR} CACHE INTERNAL \"CPU_HEADER_DIR\")\n")
    self.cmFile.write("set(RTEMS_LIBS ${RTEMS_LIBS} CACHE INTERNAL \"RTEMS_LIBS\")\n")
    self.cmFile.write("install(TARGETS ${RTEMS_LIBS}\n")
    self.cmFile.write("  EXPORT rtems-kernel-targets\n")
    self.cmFile.write("  ARCHIVE DESTINATION lib\n")
    self.cmFile.write("  PUBLIC_HEADER DESTINATION include\n")
    self.cmFile.write(")\n\n")

    self.cmFile.write("set(INSTALL_CONFIGDIR \"${CMAKE_INSTALL_PREFIX}/cmake\")\n\n")


    self.cmFile.write("install(EXPORT rtems-kernel-targets\n")
    self.cmFile.write("  FILE RtemsTargets.cmake\n")
    self.cmFile.write("  DESTINATION ${INSTALL_CONFIGDIR}\n")
    self.cmFile.write(")\n\n")


    self.cmFile.write("configure_package_config_file(${PROJECT_SOURCE_DIR}/cmake/find/RtemsConfig.cmake.in\n")
    self.cmFile.write("  ${CMAKE_CURRENT_BINARY_DIR}/RtemsConfig.cmake\n")
    self.cmFile.write("  INSTALL_DESTINATION ${INSTALL_CONFIGDIR}\n")
    self.cmFile.write(")\n\n")

    self.cmFile.write("install(FILES\n")
    self.cmFile.write("  ${CMAKE_CURRENT_BINARY_DIR}/RtemsConfig.cmake\n")
    self.cmFile.write("  DESTINATION ${INSTALL_CONFIGDIR}\n")
    self.cmFile.write(")\n\n")

    self.cmFile.write("install(FILES\n")
    self.cmFile.write("  ${CMAKE_TOOLCHAIN_FILE}\n")
    self.cmFile.write("  DESTINATION ${INSTALL_CONFIGDIR}\n")
    self.cmFile.write(")\n\n")


    self.cmFile.write("install(DIRECTORY ${PROJECT_SOURCE_DIR}/cpukit/score/cpu/${RTEMS_CPU}/include/ DESTINATION ${CMAKE_INSTALL_PREFIX}/include)\n\n")



class BspCmakeFileWriter(CmakeFileWriter):

  def __init__(self, logger, sourceFolder, topDir):
    super().__init__(logger, sourceFolder, topDir)

  def writeBspCmakeFileHeader(self):
    self.writeCmakeFileHeader()

    folder = os.path.basename(os.path.normpath(self.sourceFolder))

    self.cmFile.write("include_directories (\"${PROJECT_SOURCE_DIR}/cpukit/include\")\n")
    self.cmFile.write("include_directories (\"${PROJECT_SOURCE_DIR}/cpukit/score/cpu/${RTEMS_CPU}/include\")\n")
    self.cmFile.write("include_directories (\"${PROJECT_SOURCE_DIR}/bsps/include\")\n")
    self.cmFile.write("include_directories (\"${PROJECT_SOURCE_DIR}/bsps/${RTEMS_CPU}/include\")\n")
    self.cmFile.write("include_directories (\"${{PROJECT_SOURCE_DIR}}/bsps/${{RTEMS_CPU}}/{0}/include\")"
                      "\n".format(folder))
    self.cmFile.write("include_directories (\"${CMAKE_CURRENT_BINARY_DIR}/_generated/bsp\")\n\n")

  def getBspSwitch(self, line):
    sIdx = line.find("[")
    eIdx = line.find("]")

    name = line[sIdx + 1:eIdx]

    line = line[eIdx + 1:]
    sIdx = line.find("[")
    eIdx = line.find("]")

    clause = line[sIdx + 1:eIdx]

    line = line[eIdx + 1:]
    sIdx = line.find("[")
    eIdx = line.find("]")

    value = line[sIdx + 1:eIdx]
    BspSwitch(name, clause, value)
    return BspSwitch(name, clause, value)

  def writeBspOptsFile(self, cfgFile):

    switches = []
    bspSwitches = []

    with open(cfgFile, 'r') as f:
      line = f.readline()

      while line:
        line = line.rstrip()
        searchString = "RTEMS_BSPOPTS_SET("

        idx = line.find(searchString)
        if -1 != idx:
          line = line[len(searchString) + 1:]
          switches.append(line[:line.find("]")])

        line = f.readline()

    switches = list(set(switches))

    for i in range(len(switches)):
      bspSwitches.append(BspSwitch(switches[i]))

    for i in range(len(bspSwitches)):
      with open(cfgFile, 'r') as f:
        line = f.readline()

        while line:
          line = line.rstrip()
          searchString = "RTEMS_BSPOPTS_SET("
          idx = line.find(searchString)
          if -1 != idx:
            idx = line.find(bspSwitches[i].getName())
            if -1 != idx:
              line = line[idx + 2 + len(bspSwitches[i].getName()):]
              sIdx = line.find("[")
              eIdx = line.find("]")

              clause = line[sIdx + 1:eIdx]

              line = line[eIdx + 1:]
              sIdx = line.find("[")
              eIdx = line.find("]")

              value = line[sIdx + 1:eIdx]
              bspSwitches[i].addClause(clause, value)
          line = f.readline()

    for i in range(len(bspSwitches)):
      self.parseBspSwitch(bspSwitches[i])

    with open(cfgFile, 'r') as f:
      line = f.readline()

      while line:
        searchString = "RTEMS_BSP_CLEANUP_OPTIONS"

        idx = line.find(searchString)
        if -1 != idx:
          return 1

        line = f.readline()

    return 0

  def parseBspSwitch(self, switch):
    ifIsOpen = 0
    clauses = switch.getClauses()


    tn = switch.getName()
    idx = tn.find("STM32F4_ENABLE_I2C1")
    if -1 != idx:
      self.logger.info("Switch: {0}".format(switch.getName()))


    if 1 == len(clauses):

      if "" != clauses[0].getValue():
        if "*" == clauses[0].getClause():
          self.writeSwitch(switch.getName(), clauses[0].getValue())
          self.cmFile.write("\n")
        else:
          self.writeSwitchStart("if", clauses[0].getClause())
          self.writeSwitch(switch.getName(), clauses[0].getValue())
          self.cmFile.write("endif() # {0}\n\n".format(switch.getName()))
    else:
      for i in range(len(clauses)):

        if ifIsOpen == 0:
          self.writeSwitchStart("if", clauses[i].getClause())
          ifIsOpen = 1
        else:
          if "*" == clauses[i].getClause():
            self.writeSwitchStart("else", clauses[i].getClause())
          else:
            self.writeSwitchStart("elseif", clauses[i].getClause())

        self.writeSwitch(switch.getName(), clauses[i].getValue())
      self.cmFile.write("endif() # {0}\n\n".format(switch.getName()))

  def writeSwitchStart(self, pfx, clause):

    clause = clause.replace("*", "")

    if pfx == "else":
      self.cmFile.write("else()\n")

    else:
      self.cmFile.write("{0}(${{RTEMS_BSP}} MATCHES \"{1}\")\n".format(pfx, clause))

  def writeSwitch(self, name, value):
    if value:
      self.cmFile.write("set({0} {1} CACHE INTERNAL \"{2}\")\n".format(name, value, name))
    else:
      self.cmFile.write("message(\"\") #dummy\n")
  def writeBspCmakeExport(self,targets):

    self.cmFile.write("install(DIRECTORY ${PROJECT_SOURCE_DIR}/bsps/include/ DESTINATION ${CMAKE_INSTALL_PREFIX}/include)\n")
    self.cmFile.write("install(DIRECTORY ${PROJECT_SOURCE_DIR}/bsps/${RTEMS_CPU}/include/ DESTINATION ${CMAKE_INSTALL_PREFIX}/include)\n\n")

    self.cmFile.write("install(TARGETS rtemsbsp\n")
    self.cmFile.write("  EXPORT rtems-bsp-targets\n")
    self.cmFile.write("  ARCHIVE DESTINATION lib\n")
    self.cmFile.write("  PUBLIC_HEADER DESTINATION include\n")
    self.cmFile.write(")\n\n")

    self.cmFile.write("set(INSTALL_CONFIGDIR \"${CMAKE_INSTALL_PREFIX}/cmake\")\n\n")

    self.cmFile.write("install(EXPORT rtems-bsp-targets\n")
    self.cmFile.write("  FILE BspTargets.cmake\n")
    self.cmFile.write("  DESTINATION ${INSTALL_CONFIGDIR}\n")
    self.cmFile.write(")\n\n")

    self.cmFile.write("file(GLOB CPU_LINKER_FILES \"${PROJECT_SOURCE_DIR}/bsps/${RTEMS_CPU}/shared/start/linkcmds.*\")\n")
    self.cmFile.write("install(FILES ${CPU_LINKER_FILES} DESTINATION ${CMAKE_INSTALL_PREFIX}/linker)\n\n")
    self.cmFile.write("install(FILES ${PROJECT_SOURCE_DIR}/bsps/${RTEMS_CPU}/${RTEMS_BSP_DIR_NAME}/start/bsp_specs DESTINATION ${CMAKE_INSTALL_PREFIX}/linker)\n\n")

    self.cmFile.write("if(EXISTS \"${PROJECT_SOURCE_DIR}/bsps/${RTEMS_CPU}/${RTEMS_BSP_DIR_NAME}/start/linkcmds.${RTEMS_BSP}\")\n")
    self.cmFile.write("install(FILES \n")
    self.cmFile.write("  ${PROJECT_SOURCE_DIR}/bsps/${RTEMS_CPU}/${RTEMS_BSP_DIR_NAME}/start/linkcmds.${RTEMS_BSP}\n")
    self.cmFile.write("  DESTINATION ${CMAKE_INSTALL_PREFIX}/linker\n")
    self.cmFile.write("  RENAME linkcmds)\n")
    self.cmFile.write("endif()\n\n")
    
    self.cmFile.write("if(EXISTS \"${PROJECT_SOURCE_DIR}/bsps/${RTEMS_CPU}/shared/start/start.S\")\n")
    self.cmFile.write("  add_library(start OBJECT ${PROJECT_SOURCE_DIR}/bsps/${RTEMS_CPU}/shared/start/start.S )\n")
    self.cmFile.write("  add_dependencies(rtemsbsp start)\n")
    self.cmFile.write("  add_custom_command(TARGET rtemsbsp POST_BUILD\n")
    self.cmFile.write("    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_OBJECTS:start> ${CMAKE_INSTALL_PREFIX}/lib/start.o\n")
    self.cmFile.write("  )\n")
    self.cmFile.write("endif()\n\n")


