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


import argparse
from Modules.ConfigParser import *



def get_rtems_src_dir(rDir):
    if os.path.isabs(rDir):
        rtemsDir = rDir
    else:
        rtemsDir = os.getcwd()
        rtemsDir = rtemsDir + "/" + rDir

    if not os.path.exists(rtemsDir + "/cpukit"):
        logger.error("Directory {0} does not contain RTEMS".format(rtemsDir))
        sys.exit()
    return rtemsDir

def clean_rtems_src_dir(rdir):
    logger.info("Remove old CMake additions")

    if os.path.exists(rdir + "/cmake"):
        logger.info("\tDelete folder: {0}".format(rdir + "/cmake"))
        shutil.rmtree(rdir + "/cmake", ignore_errors=True)
    return

def copy_in_cmake_rtems_src_dir(rdir):
    logger.info("Add CMake extensions")

    cmScriptInDir = os.getcwd() + "/cmake/RTEMS"
    cmakeScriptOutDir = rdir

    filesToCopy = []
    for filename in glob.iglob(cmScriptInDir + "/**/*.*", recursive=True):
        filesToCopy.append(os.path.relpath(filename, cmScriptInDir))

    for i in range(len(filesToCopy)):
        tmpPath = os.path.dirname(os.path.abspath(cmakeScriptOutDir + "/" + filesToCopy[i]))
        if not os.path.exists(tmpPath):
            logger.info("\tCreate folder: {0}".format(tmpPath))
            os.makedirs(tmpPath, exist_ok=True)
        logger.info("\tCopy file: {0}".format(filesToCopy[i]))
        shutil.copy2(cmScriptInDir + "/" + filesToCopy[i], cmakeScriptOutDir + "/" + filesToCopy[i])



    return


if __name__ == '__main__':
    argParser = argparse.ArgumentParser(description='Add CMake support to RTEMS Core')
    optArgs = argParser._action_groups.pop()
    optArgs.add_argument('-rtems-src', '--rtems-source-directory',
                         help="set the path to directory in which you've checked out RTEMS"
                         "(default=../../SystemOS/rtems/rtems)",
                         default="../../SystemOS/rtems/rtems")
    argParser._action_groups.append(optArgs)
    args = argParser.parse_args()
    currentWorkDir = os.getcwd()

    rtemsFolder = get_rtems_src_dir(args.rtems_source_directory)
    clean_rtems_src_dir(rtemsFolder)
    copy_in_cmake_rtems_src_dir(rtemsFolder)

    logger.info("Bootstrap RTEMS")
    logger.info("Current work directory: {0}".format(currentWorkDir))
    logger.info("RTEMS directory: {0}".format(rtemsFolder))

    CpukitParser = CpukitParser(rtemsFolder, logger)
    CpukitParser.parseMakefile()

    searchPath = rtemsFolder + "/c/src/lib/libbsp/**/Makefile.am"
    BspParsers = []

    bspCount = 0
    for filename in glob.iglob(searchPath, recursive=True):
        bspName = filename[filename.find("libbsp") + 7:]
        bspName = bspName[:bspName.find("Makefile.am")]
        bspName = bspName[:-1]
        projSourceDir = rtemsFolder + "/bsps/" + bspName
        projSourceDir = projSourceDir.replace("\\", "/")

        bspName = bspName.replace("\\", "-")
        bspName = bspName.replace("/", "-")
        idx = bspName.find("qemu_fakerom")
        idxx = bspName.find("bootloader")
        if -1 == idx:
            if -1 == idxx:
                idx = bspName.find("-")
                makefileLocation = os.path.dirname(os.path.abspath(filename))
                if -1 != idx:
                    bspCount = bspCount + 1
                    makefileLocation = makefileLocation.replace("\\", "/")
                    logger.info("Found BSP [{0}] in: {1}".format(bspCount, makefileLocation))
                    BspParsers.append(BspParser(rtemsFolder, makefileLocation, logger))

            else:
                logger.info("Dropped BSP in: {0}".format(bspName))
        else:
            logger.info("Dropped BSP in: {0}".format(bspName))

    for i in range(len(BspParsers)):
        BspParsers[i].parseMakefile()
