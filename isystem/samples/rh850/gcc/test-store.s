.data
var1:   .byte   0
var2:   .byte   0
var3:   .byte   0
var4:   .byte   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
var5:   .byte   0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0

start = 0xfee00000

.text
        mov start, r1

#----------------------------------st.b(1)--disp16---OK
/*
		mov 12, r3
        movea var1 - .data, r1, r2
        st.b r3, 0[r2]
        ld.bu 0[r2], r4

        mov 0x85, r3
        movea var2 - .data, r1, r2
        st.b r3, 0[r2]
        ld.bu 0[r2], r5

        mov -11, r3
        movea var3 - .data, r1, r2
        st.b r3, 0[r2]
        ld.bu 0[r2], r6

        mov 120, r3
        movea var4 - .data, r1, r2
        st.b r3, 0[r2]
        ld.bu 0[r2], r7
*/
#----------------------------------st.h(1)--disp16---OK
/*
        mov 12, r3
        movea var1 - .data, r1, r2
        st.h r3, 0[r2]
        ld.hu 0[r2], r4

        mov 0x4bcd, r3
        movea var2 - .data, r1, r2
        st.h r3, 0[r2]
        ld.hu 0[r2], r5

        mov -11, r3
        movea var3 - .data, r1, r2
        st.h r3, 0[r2]
        ld.hu 0[r2], r6

        mov 2047, r3
        movea var4 - .data, r1, r2
        st.h r3, 0[r2]
        ld.hu 0[r2], r7
*/
#----------------------------------st.w(1)--disp16---OK
/*
        mov 12, r3
        movea var1 - .data, r1, r2
        st.w r3, 0[r2]
        ld.w 0[r2], r4

        mov 0x4321abcd, r3
        movea var2 - .data, r1, r2
        st.w r3, 0[r2]
        ld.w 0[r2], r5

        mov -11, r3
        movea var3 - .data, r1, r2
        st.w r3, 0[r2]
        ld.w 0[r2], r6

        mov 2047, r3
        movea var4 - .data, r1, r2
        st.w r3, 0[r2]
        ld.w 0[r2], r7
*/
#----------------------------------st.dw(1)--disp16--- Seems that v850 doesn't have st.dw

