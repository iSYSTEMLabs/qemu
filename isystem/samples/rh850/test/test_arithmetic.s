.include "RH850G3M_insts.s"
.include "gpr_init.s"
	
	#test add reg1,reg2

	#simple tests

	mov 0x5,r20
	mov 0x10,r21
	add r2,r1
	mov -20,r1
	add r1,r2
	#testing add and add with negative number
	
	#harder tests
	mov 0x0,r1
	mov 0x0,r2
	add r1,r2
	#testing for Z flag

	mov 0xffffffff,r4
	mov 0xffffffff,r5
	add r4,r5
	#overflow

	mov 0x7fffffff,r1
	mov 0x1,r2
	add r1,r2
	#carry flag
	
	mov -0x80000000,r1
	mov 0x7fffffff,r2
	add r1,r2
	add r2,r1
	
	#test add imm(5),reg2
	#simple testst
	add 0x4,r1
	add -5,r2
	
	#harder tests
	mov 0x0,r1
	add 0x0,r1
	#Z flag test

	mov 0xffffffff,r7
	add 0x1,r7
	#Z flag
	
	mov 0x7fffffff,r6
	add 0x5,r6
	#carry flag

	mov -0x80000000,r1
	add 0x5,r1

	mov 0xffffffff,r9
	add 0x1,r9
	#owerflow test

	add 0x0f,r10
	add 0x0f,r11
	add -16,r12


	#test addi imm(16),reg1,reg2
	
	#simple tests
		
	mov 0x5,r7
	addi 0x10,r7,r5
	addi -15,r5,r6
	mov -1,r1
	addi 0x10,r1,r5
	addi -15,r1,r6

	#harder tests
	
	mov 0x0,r1
	addi 0x0,r1,r2
	#Z flag


	mov 0xffffffff,r4
	addi 0x1,r4,r5
	#overflow

	mov 0x7fffffff,r1
	addi 0x1, r1,r2
	#carry flag
	
	mov 0x7fffffff,r2
	mov 0x7fffffff,r1
	addi -0xfff,r1,r2
	addi -0xfff, r2,r1
	
	
	#tests for CMP reg1,reg2
	
	#simple tests
	mov 0x5,r1
	mov 0x4,r2
	cmp r1,r2

	mov -0x1,r5
	mov -0x1,r6
	cmp r5,r6
	cmp r6,r5
	
	#harder test for cmp
	mov 0x0,r1
	mov 0x0,r2
	cmp r1,r2
	#testing Z flag

	mov 0xffffffff,r1
	mov -0x1,r2
	cmp r1,r2
	#testing owerflow flag
	
	mov -0x8000000,r1
	mov -0x2,r2
	cmp r1,r2
	#testing cy flag

	mov 0x7fffffff,r11
	mov -0x1,r10
	cmp r11,r10

	mov 0xffffffff,r1
	mov -0x1,r2
	cmp r2,r1
	#testing owerflow flag
	
	mov -0x8000000,r1
	mov -0x2,r2
	cmp r2,r1
	#testing cy flag

	mov 0x7fffffff,r11
	mov -0x1,r10
	cmp r10,r11

	#tests for CMP imm5,reg2
	#simple tests 
	mov 0x5,r1
	cmp 0x6,r1
	
	mov -0xf,r2
	cmp -0x1,r2

	#harder test for  CMP imm5,reg2
	mov 0x0,r1
	cmp 0x0,r1
	#Z flag test

	mov -0x80000000,r7
	cmp 0x1,r7
	cmp -0x1,r7
	#testing ov flag

	mov 0x7fffffff,r12
	cmp -0x5,r12
	cmp 0x5,r12
	#testing cy flag

	mov +0x7fffffff,r15
	cmp -0xf,r15
	
	#test for mov

	mov 0x1,r1
	mov 0x5,r2
	mov r1,r2
	mov r2,r1
	mov -0x8000000,r1
	mov r1,r2

	#tests for movea imm16,r1,r2

	#simple test 
	mov 0x5,r1
	movea 0x10,r1,r2
	movea -0xf,r2,r3
	movea +0x1,r3,r4

	#harder tests for movea imm16,reg1,reg2
	
	mov 0xffffffff,r1
        movea 0x1,r1,r2
	#overflow test

	mov 0x0,r1
	movea 0x0,r1,r2

	mov 0x7fffffff,r1
        movea 0x1,r1,r2

	mov +0x7fffffff,r1
        movea 0x1,r1,r2
	
	mov -0x80000000,r1
        movea 0x1,r1,r2
	
	mov -0x80000000,r1
        movea -0x12,r1,r2
	
	#test for movhi imm16,reg1,reg2

	

	mov 0x10,r1
	movhi 0x5,r1,r10
	movhi -0x5,r10,r12
	movhi 0xff,r12,r11
	#harder test for movhi
	mov -0x80000000,r1
	movhi 0x1,r1,r2
	movhi -0x1,r1,r8
	
	mov 0x7fffffff,r2
	movhi 0x8,r2,r9
	movhi -0xf,r9,r12
	#test for sub
	#simple tests for sub
	mov 0x1,r12
	mov 0x5,r14
	sub r12,r14
		
	mov 0x6,r29
	mov 0x6,r30
	sub r29,r30
	sub r30,r29
	#harder testf for sub
	mov 0xfff,r16
	mov 0x333,r11
	sub r16,r11
	mov 0x80000000,r8
	mov 0xfff,r6
	sub r8,r6
	
	mov 0x80000000,r8
	mov 0xfff,r6
	sub r6,r8
	sub r8,r6
	mov 0x7fffffff,r12
	mov 0xffffffff,r13
	sub r13,r12
	
	mov 0x7fffffff,r16
	mov 0x80000001,r17
	sub r17,r16
	
	mov 0x1,r1
	mov 0x80000000,r2
	sub r2,r1
	#test for subr
	#simple tests
	
	mov 0x5,r5
	mov 0x4,r6
	subr r5,r6
	subr r6,r5
	mov 0x5,r2
	mov 0x5,r3
	subr r2,r3
	
	mov 0xfff,r16
	mov 0x333,r11
	subr r11,r16
	mov 0x80000000,r8
	mov 0xfff,r6
	subr r6,r8
	
	mov 0x80000000,r8
	mov 0xfff,r6
	subr r8,r6
	subr r6,r8
	mov 0x7fffffff,r12
	mov 0xffffffff,r13
	subr r12,r13
	
	mov 0x7fffffff,r16
	mov 0x80000001,r17
	subr r16,r17
	
	mov 0x1,r1
	mov 0x80000000,r2
	subr r1,r2

	Lbl: br Lbl
	
