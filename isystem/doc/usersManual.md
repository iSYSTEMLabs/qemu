Using QEMU with iSYSTEM tools

Overview
========

[QEMU](https://www.qemu.org/) is a generic and open source machine emulator 
and virtualizer. iSYSTEM tools can connect to QEMU device via GDB interface.
This way winIDEA can be used to debug software, and testIDEA to execute unit
tests. While QEMU is not full replacement for real hardware, it can be used for
development and testing of code, which is not hardware dependent (functions
dealing with hardware can be stubbed). The main advantage of this approach is
speed, because communication with QEMU is much faster than with real device.
Unit tests executed with testIDEA or Python scripts can execute more than 100
times faster.


iSYSTEM distribution of QEMU
============================

Version of QEMU distributed with iSYSTEM tools supports:

- devices based on ARM cores (arm-softmmu, aarch64-softmmu). These devices
  are the same available in the official QEMU release. There is a minor
  update in netduino2, where start address and size of FLASH memory and 
  RAM can be configured with command line.
- V850E3 core (Renesas RH850 family). This device is implemented by 
  iSYSTEM, and contains only core, no hardware is emulated. 

Changes/improvements

These features were added by iSYSTEM:

1. Flash, RAM, and flash alias addresses and sizes for STM32F205 SoC are
configurable in command line:
- Flash option: `-flash start0=<flash start addr>,size0=<flash size>,start1=<flash alias address>`,
  for example: `-flash start0=0,size0=1M,start1=8M`
- RAM option: `-ram start0=<RAM start addr>,size0=<RAM size>', for example:
  -ram start0=0xfebc0000,size0=256k

winIDEA Configuration
=====================

To use QEMU, only winIDEA has to be configured. testIDEA 


