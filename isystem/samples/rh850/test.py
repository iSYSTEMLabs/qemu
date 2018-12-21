# This script is used for testing implementation of microcontroller RH850 in
# qemu.  Script launches all files with .s extension in folder rh850/test in
# qemu and on real microcontroller RH850 using iSYSTEM BlueBox and then
# compares the results.
#
# Module checkRegisters is used for formatting a readable output of QEMU log file.
#
# Module checkRegistersBlueBox is used to read registers from real
# microcontroller RH850.

# Usage:
# Run this script in qemu/isystem/samples/rh850/
# Example: python3 test.py

# Optional
# Check flags.
# Default usage doesnt check flags, run script with --flag to check them also.

import os
import sys
import time
import argparse
import subprocess
import glob
import checkRegistersBlueBox as crbb

NUM_OF_REGISTERS = 31
NUM_OF_PRINTED_REGISTERS = 35;
NUM_OF_REGS_TO_NOT_CHECK = NUM_OF_REGISTERS * NUM_OF_PRINTED_REGISTERS
NUM_OF_LINES_WITH_GPR_VALUES = 12

# files provifing common functionality to test files
NOT_TEST_FILES = ['gpr_init.s', 'RH850G3M_insts.s']
QEMU_LOG_FILE = "../../../../rh850.log"

RESULT_PASSED = "PASSED"
RESULT_FAILED = "FAILED"


def buildElf(fileName):
    cmd = ['./build.sh ' + fileName + ' > build_' + fileName + '.log']
    subprocess.check_call(cmd, shell=True, executable='/bin/bash')


def runQemu(fileName, logFile):
    subprocess.check_call("../../../../rh850-softmmu/qemu-system-rh850 -M rh850mini -s -singlestep -d"
                          " nochain,exec,in_asm,cpu -D " + logFile + " -kernel bin/" + fileName + ".elf &", shell=True)

    # TODO replace with GDB control and exiting nicely
    time.sleep(3)
    subprocess.check_call('kill $(pgrep qemu-system)', shell=True, executable='/bin/bash')


def extract_registers(qemuLogFileName, num_of_ints_to_print, asmFileStem):
    """
    This function extracts instruction and registers from QEMU log file. It 
    prints out PC, instruction, status register PSW, and 32 general purpose 
    registers.
    """
    with open('log_qemu_' + asmFileStem + '.log', 'w') as qemuRegsFile:

        with open(qemuLogFileName, "r") as qemuLogFile:

            instNumber = 0
            counter = 0
            out = ['','']

            for line in qemuLogFile:

                if line.startswith("0x"):
                    instNumber += 1
                    readLogLine = True
                    counter = 0
                    raw_line = line.split()

                    if len(raw_line) == 4:
                        print('->->-', raw_line[0], raw_line[1], raw_line[2], raw_line[3], file=qemuRegsFile)

                elif line.startswith(" "):
                    raw_line = line.split()
                    if readLogLine:
                        val = 0
                        for i in raw_line:
                            if val % 2 == 0:
                                out[0] = i + ":"
                            else:
                                out[1] = i
                                print(f">>>- {out[0]:>5} {out[1]}", file=qemuRegsFile)
                            val += 1

                counter += 1
                if counter > NUM_OF_LINES_WITH_GPR_VALUES:
                    readLogLine = False
                if instNumber > num_of_ints_to_print:
                    break


# not used, seems to be redundant, if files are different sizes compare will fail anyway
def _check_file_sizes(asmFileStem):
    with open('log_qemu_' + asmFileStem + '.log', 'r') as log_qemu: 
        with open('log_bluebox_' + asmFileStem + '.log', 'r') as log_blubox: 

            num_lines_qemu = sum(1 for line in log_qemu)
            print('num_lines_qem =', unum_lines_qemu)
            num_lines_bluebox = sum(1 for line in log_blubox)
            print('num_lines_bluebox =', num_lines_bluebox)
            if num_lines_bluebox-(NUM_OF_PRINTED_REGISTERS*2) > num_lines_qemu:
                return RESULT_FAILED
                print("files are different size")
        
    return RESULT_PASSED


def compare_qemu_and_blue_box_regs(asmFileStem):

    # TODO - review algorithm

    # EXAMPLE OF LOG FILE
    # QEMU              BLUEBOX     index

    # INSTRUCTION       --------    0
    # PC                PC          1
    # PSW               PSW         2
    # R0                R0          3
    # R1                R1
    # R2                R2
    # ...               ...
    
    log_qemu = open('log_qemu_' + asmFileStem + '.log', 'r')
    log_blubox = open('log_bluebox_' + asmFileStem + '.log', 'r')

    index = 0
    start = 0;
    isOkay = True
    result_for_file = RESULT_PASSED

    print("----------")
    for line1, line2 in zip(log_qemu, log_blubox):
        if start >= NUM_OF_REGS_TO_NOT_CHECK:
            if(index == 0):
                #NAME OF INSTRUCTION
                print("-----------------")
                print('@@@> ', line1[:-1])
            elif(index == 2):
                #PSW
                if True:
                    #print("CHECKING FLAGS ALSO");
                    if line1[-2:] != line2[-2:]:
                        # CHECKING JUST LAST 4 BITS OF PSW REG
                        print("ERROR"  +  line1[:-1]  + " " +  line2[:-1])
                        isOkay = False
                    elif ((int(line1[-3]) % 2) != (int(line2[-3]) % 2)):
                        #CHECKING SAT FLAG
                        print("ERROR" + line1[:-1]  + " " +  line2[:-1])
                        isOkay = False
            else:
                #PC AND OTHER GPR
                print('l1 l2\n  ', line1, '\n  ', line2)
                if line1.split(': ')[1] != line2.split('x')[1]:
                    print("ERROR" + line1[:-1]  + " " +  line2[:-1])
                    isOkay = False

            index = index + 1

            if(index == NUM_OF_PRINTED_REGISTERS):
                if isOkay:
                    print("OK")
                    print("-----------------")
                else:
                    print("FAILED")
                    result_for_file = RESULT_FAILED
                    print("-----------------")
                index = 0
                isOkay = True

        start = start + 1

    log_qemu.close()
    log_blubox.close()
    return result_for_file


def _parseArgs():

    usage = """
Usage: %prog [asmFilesToTest]

If no asm file is specified, all .s files in dir 'test' are tested. 
Use shell globbing to specify groups of files to be tested, for 
example:

$ %prog test/mov*.s
"""
    parser = argparse.ArgumentParser(description=usage)

    parser.add_argument('files', metavar='files', type=str, nargs='*',
                        help='list of asm files to test')

    args = parser.parse_args()

    return args


def main():

    args = _parseArgs()
    asmFiles = args.files
    if not asmFiles:   # no files specified in cmd line
        asmFiles = glob.glob("*.s")

    print(f"Testing {len(asmFiles)} files:")
    print(asmFiles)

    tested_files = []
    results = []

    blueBox = crbb.BlueBox()
    blueBox.openConnection()

    for asmFile in asmFiles:

        asmFile = os.path.basename(asmFile) # strip away path from files 
                           # specified in cmdLine. Only dir 'test' is allowed.

        if asmFile in NOT_TEST_FILES:
            continue

        tested_files.append(asmFile)
        print("Testing:", asmFile)
        asmFileStem = asmFile[:-2]  # remove the .s extension

        buildElf(asmFileStem)
        runQemu(asmFileStem, QEMU_LOG_FILE)

        num_of_all_inst =  blueBox.check_registers_blue_box(asmFileStem)
        extract_registers(QEMU_LOG_FILE, num_of_all_inst, asmFileStem)

        #_check_file_sizes(asmFileStem)
        fileRes = compare_qemu_and_blue_box_regs(asmFileStem)
        results.append(fileRes)

    final_results = zip(tested_files, results)
    print("---------------------FINAL RESULTS-------------------------")
    for x in final_results:
        print(x)


if __name__ == '__main__':
    os.chdir("test")
    main()
    os.chdir('..')
