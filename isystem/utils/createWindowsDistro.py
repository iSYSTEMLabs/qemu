#!/usr/bin/python3
# This script builds quemu and creates distributables. See help for more info.

import sys
import os
import re
import glob
import subprocess
import time
import shutil
import argparse
import shutil
import pathlib 

g_isVerbose = False
BIN_DIR = 'build'
DOCKER_DIR_GLOB = 'docker-src*'
DIST_DIR = 'dist'
ZIP_FILE_NAME = 'qemu-isystem'
ZIP_FILE_EXT = 'zip'
NETWORK_DIST_DIR = '/media/sf_qemu' # this dir must be shared in VM

def log(msg: str):
    if g_isVerbose:
        print('\033[1;32;40m ' + msg + '\033[0;37;40m')


def remove_docker_dirs():
    host_dirs = glob.glob(DOCKER_DIR_GLOB)
    for host_dir in host_dirs:
        shutil.rmtree(host_dir)


def get_latest_host_dir():
    dockerDirs = glob.glob(DOCKER_DIR_GLOB)

    if not dockerDirs:
        raise Exception("No dir with docker output exists! Run build first.")

    if len(dockerDirs) == 1:
        return dockerDirs[0]

    return dockerDirs.sort()[-1]


def create_host_dir():
    """
    Runs script for docker build with invalid target. This way the script creates
    qemu/docker.src-<timestamp>/qemu.tar
    """

    dockerDirs = glob.glob(DOCKER_DIR_GLOB)

    cmd = ['make', 'docker-test-mingw@fedora', 'J=4', 'TARGET_LIST=intentionallyInvalidToCreateDirOnly']
    if g_isVerbose:  # Option: V=1 for verbose build
        cmd += ['V=1']
    log('Start docker to create mounted dir: ' + ' '.join(cmd))

    p = subprocess.call(cmd)  # do not check for error, should fail anyway

    dockerDirsAfterCall = glob.glob(DOCKER_DIR_GLOB)
    newDockerDir = set(dockerDirsAfterCall) - set(dockerDirs)
    if len(newDockerDir) != 1:
        raise Exception("Internal error - only one directory exepcted, "
                        "use debugger to find cause!" + str(newDockerDir))

    return list(newDockerDir)[0]


def _docker_build(docker_host_dir, targets):

    isVerbose = 0
    if g_isVerbose:  # Option: V=1 for verbose build
        isVerbose = 1

    homeDir = pathlib.Path.home()
    curDir = os.getcwd()
    targetsStr = ','.join(targets).replace(',', '-softmmu,') + '-softmmu'

    cmd = 'sudo -n docker run --label com.qemu.instance.uuid=isystemBuild -u 1000 --security-opt seccomp=unconfined --rm --net=none ' + \
         f'-e TARGET_LIST={targetsStr} -e EXTRA_CONFIGURE_OPTS= -e V={isVerbose} -e J=12 -e DEBUG= -e SHOW_ENV= -e CCACHE_DIR=/var/tmp/ccache ' + \
         f'-v {homeDir}/.cache/qemu-docker-ccache:/var/tmp/ccache:z -v {curDir}/{docker_host_dir}:/var/tmp/qemu ' + \
          ' qemu:fedora /var/tmp/qemu/run ../../isystem/dockerBuild.sh'

    log('Start docker for build and copy: ' + cmd)

    p = subprocess.check_call(cmd, shell=True)

#    while True:
#        time.sleep(1)
#        id = str(os.popen("sudo docker ps --filter ancestor=qemu:fedora -q").readlines())
#        if len(id) > 4:
#            id = id[2:]
#            id = id[:-4]
#            log(f'Started docker with id: {id}')
#            break
#
#    return id


def _check_dlls(out_dir, arch: str, targets):
    """
    This f. checks, which dlls are really necessary for running quemu
    as simulator for isystem.test.
    """

    os.chdir(os.path.join(out_dir, DIST_DIR))

    REDUNDANT_DIR = '../redundantDlls'
    # shutil.rmtree(REDUNDANT_DIR)
    if not os.path.exists(REDUNDANT_DIR):
        os.mkdir(REDUNDANT_DIR)
    

    for dllFName in glob.glob("*.dll"):
        os.rename(dllFName, dllFName + '_tst')
        try:
            #for target in targets:
            target = 'arm'
            cmd = "wine qemu-system-" + target + "w.exe -M help > /dev/null 2>&1 "
            subprocess.check_call(cmd, shell=True)
            log('Redundant dll: ' + dllFName)
            os.rename(dllFName + '_tst', dllFName)
            shutil.move(dllFName, REDUNDANT_DIR)
        except:
            log('Required dll: ' + dllFName)
            os.rename(dllFName + '_tst', dllFName)

    os.chdir("../..")


def _zip_files(out_dir):
    log("Zipping ...")
    shutil.make_archive(ZIP_FILE_NAME, ZIP_FILE_EXT, os.path.join(out_dir, DIST_DIR))


def copytree(src, dst, ignore_patterns=[]):
    errors = []
    names = os.listdir(src)
    for name in names:
        isSkip = False
        for pattern in ignore_patterns:
            if re.match(pattern, name):
                log(f"Skipping '{name}' because it matches '{pattern}'.")
                isSkip = True

        if isSkip:
            continue

        print('#', end='')
        sys.stdout.flush()
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                os.mkdir(dstname)
                copytree(srcname, dstname)
            else:
                shutil.copy2(srcname, dstname)

        except OSError as ex:
            log(str(ex) + "  Copying: " + srcname + ' --> ' + dstname)
            errors.append((srcname, dstname, str(ex)))

    if errors:
        raise Exception(errors)


def copy_to_G(hostDir, winSharedDir):
    srcDir = os.path.join(hostDir, DIST_DIR)
    excludedFiles = ['qemu-system-armw.exe', 'qemu-system-aarchw.exe']

    # clean dest dir to avoid distributing old files
    files = os.listdir(winSharedDir)
    for fname in files:
        fpath = os.path.join(winSharedDir, fname)
        if os.path.isdir(fpath):
            shutil.rmtree(fpath)
        else:
            os.remove(fpath)

    copytree(srcDir, winSharedDir, ['.*w.exe$', '.*ppc.exe$', '.*ppc64.exe$',
                                    '.*tricore.exe$'])


#def stop_docker():
#    os.chdir('..')
#    log(os.getcwd())
#
#    cmd = ["sudo docker stop " + id]
#    log('Stop docker: ' + ' '.join(cmd))
#    p = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
#
#    p.wait()
#
#    # remove docker
#    cmd = ['sudo rm -rf docker-src*']
#    p = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
#
#    os.chdir('isystem')
#
#
#def _copyFromDockerToSharedDir(id, arch, targets):
#    """
#    :param arch: architecture, should be '32' or '64'
#    :param targets: list of strings for targets, eg. ['arm', 'ppc']
#    """
#
#    for target in targets:
#        cmd = [f"sudo docker cp {id}:tmp/qemu-test/src/{target}-softmmu/qemu-system-{target}.exe"
#                                        f" {BIN_DIR}{arch}"]
#        p = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
#        p.wait()
#
#
#def _dockerBuild(dockerId, arch: str, targets):
#    """
#    :param arch: architecture, should be '32' or '64'
#    :param targets: list of strings for targets, eg. ['arm', 'ppc']
#    """
#
#    xarch = 'x86_64'
#    if arch == '32':
#        xarch = 'i686'
#
#    cmd = [f"sudo docker exec -i {dockerId} sh -c "
#                                f"'cd $QEMU_SRC;echo $QEMU_SRC; pwd; ./configure --cross-prefix={xarch}-w64-mingw32- "
#                                         "--target-list=" + ','.join(targets) + "; make'"]
#
#    log('docker build: ' + ' '.join(cmd))
#    p = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
#    p.wait()
#
#    cmd = [f"sudo docker exec -i {dockerId} sh -c 'mkdir ~/dlls{arch};  cd /usr/{xarch}-w64-mingw32/sys-root/mingw/bin/ ;"
#                                         f" cp *.dll ~/dlls{arch}'"]
#    log('docker cp dlls: ' + ' '.join(cmd))
#    p = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
#    p.wait()
#
#    cmd = [f"sudo docker cp {dockerId}:/root/dlls{arch}/ {BIN_DIR}{arch}"]
#    log('docker cp root dlls: ' + ' '.join(cmd))
#    p = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
#    p.wait()
#
#
#def _buildWinExecutables(arch, targets):
#    """
#    :param arch: architecture, should be '32' or '64'
#    :param targets: list of strings for targets, eg. ['arm', 'ppc']
#    """
#    log("---------Building: " + ','.join(targets) + f" for {arch}-bit Windows---------")
#    if os.path.exists(f"{BIN_DIR}{arch}"):
#        shutil.rmtree(f"{BIN_DIR}{arch}")
#    os.makedirs(f"{BIN_DIR}{arch}")
#
#    # start docker
#    start_docker_and_build(arch, targets)
#    dockerId = get_docker_id()
#
#    _dockerBuild(dockerId, arch, targets)
#    _copyFromDockerToSharedDir(dockerId, arch, targets)
#    check_dlls(arch, targets)
#    zip_files()
#    stop_docker()


def parseArgs():

    usage = f"""
This script is used for building and deploying of ARM, RH850, POWERPC and 
TRICORE qemu for Windows. Script downloads and launches docker, configures 
it and starts building. Target '.exe' files and dll files are copied to 
{BIN_DIR}32 or {BIN_DIR}64. The script also filters DLLs and copies required 
DLLs to dir `filtered_dlls`.

You should have docker, python3 and wine installed.

Usage:

sudo python3 createWindowsDistro.py

Examples:
   To build RH850 and ARM for Windows x64:

   python3 createWindowsDistro.py -t rh850,arm -a 64
"""
    parser = argparse.ArgumentParser(description=usage)

    parser.add_argument("-v", '--verbose', dest="isVerbose", action='store_true', default=False,
                        help="Writes more info during execution.")

    parser.add_argument("-r", '--rmhostdirs', dest="isRmHostDirs", action='store_true', default=False,
                        help=f"Removes dirs starting with '{DOCKER_DIR_GLOB}' "
                              "from previous docker runs. Recommended with build command.")

    parser.add_argument("-b", '--build', dest="isBuild", action='store_true', default=False,
                        help=f"Runs build action. Results are in dir qemu/docker-src<timestamp>.")

    parser.add_argument("-d", '--deploy', dest="isDeploy", action='store_true', default=False,
                        help=f"Copies qemu executables and DLLs for Windows to shared dir {NETWORK_DIST_DIR}.")

    targets = ['arm', 'aarch64', 'ppc', 'ppc64', 'tricore', 'rh850']

    parser.add_argument("-a", "--arch", nargs='+', default=['64'], choices=['32', '64'],
                        help="Not used, currently only 64 bit is always built.")

    parser.add_argument('-t', '--targets', type=str, nargs='+',
                        choices=targets,
                        default=targets,
                        help='list of targets to build')
                        

    return parser.parse_args()


def main():
    global g_isVerbose

    args = parseArgs() 
   
    g_isVerbose = args.isVerbose

    if not os.path.exists('isystem'):
        raise Exception("\033[1;31;40m ERROR: This script should be run in top directory of 'qemu'!")

    if args.isRmHostDirs:
        remove_docker_dirs()

    hostDir = ''
    if args.isBuild:
        for arch in args.arch:
            hostDir = create_host_dir()
            log('Host dir successfully created: ' + hostDir)
            _docker_build(hostDir, args.targets)
            # hostDir = 'docker-src.2019-09-11-15.06.09.6052'
            _check_dlls(hostDir, '', [])
            shutil.copytree('isystem/window-icons/share', os.path.join(hostDir, DIST_DIR, 'share'))
            # _zip_files(hostDir)
            # shutil.copy2(f'{ZIP_FILE_NAME}.{ZIP_FILE_EXT}', '/media/sf_kubuntu1704/')

    if args.isDeploy:
        if not hostDir:
            hostDir = get_latest_host_dir()
        print(f'Copying files to {NETWORK_DIST_DIR} ...')
        copy_to_G(hostDir, NETWORK_DIST_DIR)


if __name__ == '__main__':
    main()
    log("------------FINISHED------------")

