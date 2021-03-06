/*
 * RH850 FPU Emulation Helpers for QEMU.
 *
 * Copyright (c) 2016-2017 Sagar Karandikar, sagark@eecs.berkeley.edu
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms and conditions of the GNU General Public License,
 * version 2 or later, as published by the Free Software Foundation.
 *
 * This program is distributed in the hope it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "qemu/osdep.h"
#include <stdlib.h>
#include "cpu.h"
#include "qemu/host-utils.h"
#include "exec/exec-all.h"
#include "exec/helper-proto.h"

target_ulong cpu_rh850_get_fflags(CPURH850State *env)
{
    int soft = get_float_exception_flags(&env->fp_status);
    target_ulong hard = 0;

    hard |= (soft & float_flag_inexact) ? FPEXC_NX : 0;
    hard |= (soft & float_flag_underflow) ? FPEXC_UF : 0;
    hard |= (soft & float_flag_overflow) ? FPEXC_OF : 0;
    hard |= (soft & float_flag_divbyzero) ? FPEXC_DZ : 0;
    hard |= (soft & float_flag_invalid) ? FPEXC_NV : 0;

    return hard;
}

void cpu_rh850_set_fflags(CPURH850State *env, target_ulong hard)
{
    int soft = 0;

    soft |= (hard & FPEXC_NX) ? float_flag_inexact : 0;
    soft |= (hard & FPEXC_UF) ? float_flag_underflow : 0;
    soft |= (hard & FPEXC_OF) ? float_flag_overflow : 0;
    soft |= (hard & FPEXC_DZ) ? float_flag_divbyzero : 0;
    soft |= (hard & FPEXC_NV) ? float_flag_invalid : 0;

    set_float_exception_flags(soft, &env->fp_status);
}

void helper_set_rounding_mode(CPURH850State *env, uint32_t rm)
{
    int softrm;

    if (rm == 7) {
        rm = 0; //env->frm;
    }
    switch (rm) {
    case 0:
        softrm = float_round_nearest_even;
        break;
    case 1:
        softrm = float_round_to_zero;
        break;
    case 2:
        softrm = float_round_down;
        break;
    case 3:
        softrm = float_round_up;
        break;
    case 4:
        softrm = float_round_ties_away;
        break;
    default:
        do_raise_exception_err(env, RH850_EXCP_ILLEGAL_INST, GETPC());
    }

    set_float_rounding_mode(softrm, &env->fp_status);
}

uint64_t helper_fmadd_s(CPURH850State *env, uint64_t frs1, uint64_t frs2,
                        uint64_t frs3)
{
    return float32_muladd(frs1, frs2, frs3, 0, &env->fp_status);
}

uint64_t helper_fmadd_d(CPURH850State *env, uint64_t frs1, uint64_t frs2,
                        uint64_t frs3)
{
    return float64_muladd(frs1, frs2, frs3, 0, &env->fp_status);
}

uint64_t helper_fmsub_s(CPURH850State *env, uint64_t frs1, uint64_t frs2,
                        uint64_t frs3)
{
    return float32_muladd(frs1, frs2, frs3, float_muladd_negate_c,
                          &env->fp_status);
}

uint64_t helper_fmsub_d(CPURH850State *env, uint64_t frs1, uint64_t frs2,
                        uint64_t frs3)
{
    return float64_muladd(frs1, frs2, frs3, float_muladd_negate_c,
                          &env->fp_status);
}

uint64_t helper_fnmsub_s(CPURH850State *env, uint64_t frs1, uint64_t frs2,
                         uint64_t frs3)
{
    return float32_muladd(frs1, frs2, frs3, float_muladd_negate_product,
                          &env->fp_status);
}

uint64_t helper_fnmsub_d(CPURH850State *env, uint64_t frs1, uint64_t frs2,
                         uint64_t frs3)
{
    return float64_muladd(frs1, frs2, frs3, float_muladd_negate_product,
                          &env->fp_status);
}

uint64_t helper_fnmadd_s(CPURH850State *env, uint64_t frs1, uint64_t frs2,
                         uint64_t frs3)
{
    return float32_muladd(frs1, frs2, frs3, float_muladd_negate_c |
                          float_muladd_negate_product, &env->fp_status);
}

uint64_t helper_fnmadd_d(CPURH850State *env, uint64_t frs1, uint64_t frs2,
                         uint64_t frs3)
{
    return float64_muladd(frs1, frs2, frs3, float_muladd_negate_c |
                          float_muladd_negate_product, &env->fp_status);
}

uint64_t helper_fadd_s(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float32_add(frs1, frs2, &env->fp_status);
}

uint64_t helper_fsub_s(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float32_sub(frs1, frs2, &env->fp_status);
}

uint64_t helper_fmul_s(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float32_mul(frs1, frs2, &env->fp_status);
}

uint64_t helper_fdiv_s(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float32_div(frs1, frs2, &env->fp_status);
}

uint64_t helper_fmin_s(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float32_minnum(frs1, frs2, &env->fp_status);
}

uint64_t helper_fmax_s(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float32_maxnum(frs1, frs2, &env->fp_status);
}

uint64_t helper_fsqrt_s(CPURH850State *env, uint64_t frs1)
{
    return float32_sqrt(frs1, &env->fp_status);
}

target_ulong helper_fle_s(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float32_le(frs1, frs2, &env->fp_status);
}

target_ulong helper_flt_s(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float32_lt(frs1, frs2, &env->fp_status);
}

target_ulong helper_feq_s(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float32_eq_quiet(frs1, frs2, &env->fp_status);
}

target_ulong helper_fcvt_w_s(CPURH850State *env, uint64_t frs1)
{
    return float32_to_int32(frs1, &env->fp_status);
}

target_ulong helper_fcvt_wu_s(CPURH850State *env, uint64_t frs1)
{
    return (int32_t)float32_to_uint32(frs1, &env->fp_status);
}

#if defined(TARGET_RH85064)
uint64_t helper_fcvt_l_s(CPURH850State *env, uint64_t frs1)
{
    return float32_to_int64(frs1, &env->fp_status);
}

uint64_t helper_fcvt_lu_s(CPURH850State *env, uint64_t frs1)
{
    return float32_to_uint64(frs1, &env->fp_status);
}
#endif

uint64_t helper_fcvt_s_w(CPURH850State *env, target_ulong rs1)
{
    return int32_to_float32((int32_t)rs1, &env->fp_status);
}

uint64_t helper_fcvt_s_wu(CPURH850State *env, target_ulong rs1)
{
    return uint32_to_float32((uint32_t)rs1, &env->fp_status);
}

#if defined(TARGET_RH85064)
uint64_t helper_fcvt_s_l(CPURH850State *env, uint64_t rs1)
{
    return int64_to_float32(rs1, &env->fp_status);
}

uint64_t helper_fcvt_s_lu(CPURH850State *env, uint64_t rs1)
{
    return uint64_to_float32(rs1, &env->fp_status);
}
#endif

target_ulong helper_fclass_s(uint64_t frs1)
{
    float32 f = frs1;
    bool sign = float32_is_neg(f);

    if (float32_is_infinity(f)) {
        return sign ? 1 << 0 : 1 << 7;
    } else if (float32_is_zero(f)) {
        return sign ? 1 << 3 : 1 << 4;
    } else if (float32_is_zero_or_denormal(f)) {
        return sign ? 1 << 2 : 1 << 5;
    } else if (float32_is_any_nan(f)) {
        float_status s = { }; /* for snan_bit_is_one */
        return float32_is_quiet_nan(f, &s) ? 1 << 9 : 1 << 8;
    } else {
        return sign ? 1 << 1 : 1 << 6;
    }
}

uint64_t helper_fadd_d(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float64_add(frs1, frs2, &env->fp_status);
}

uint64_t helper_fsub_d(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float64_sub(frs1, frs2, &env->fp_status);
}

uint64_t helper_fmul_d(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float64_mul(frs1, frs2, &env->fp_status);
}

uint64_t helper_fdiv_d(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float64_div(frs1, frs2, &env->fp_status);
}

uint64_t helper_fmin_d(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float64_minnum(frs1, frs2, &env->fp_status);
}

uint64_t helper_fmax_d(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float64_maxnum(frs1, frs2, &env->fp_status);
}

uint64_t helper_fcvt_s_d(CPURH850State *env, uint64_t rs1)
{
    return float64_to_float32(rs1, &env->fp_status);
}

uint64_t helper_fcvt_d_s(CPURH850State *env, uint64_t rs1)
{
    return float32_to_float64(rs1, &env->fp_status);
}

uint64_t helper_fsqrt_d(CPURH850State *env, uint64_t frs1)
{
    return float64_sqrt(frs1, &env->fp_status);
}

target_ulong helper_fle_d(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float64_le(frs1, frs2, &env->fp_status);
}

target_ulong helper_flt_d(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float64_lt(frs1, frs2, &env->fp_status);
}

target_ulong helper_feq_d(CPURH850State *env, uint64_t frs1, uint64_t frs2)
{
    return float64_eq_quiet(frs1, frs2, &env->fp_status);
}

target_ulong helper_fcvt_w_d(CPURH850State *env, uint64_t frs1)
{
    return float64_to_int32(frs1, &env->fp_status);
}

target_ulong helper_fcvt_wu_d(CPURH850State *env, uint64_t frs1)
{
    return (int32_t)float64_to_uint32(frs1, &env->fp_status);
}

#if defined(TARGET_RH85064)
uint64_t helper_fcvt_l_d(CPURH850State *env, uint64_t frs1)
{
    return float64_to_int64(frs1, &env->fp_status);
}

uint64_t helper_fcvt_lu_d(CPURH850State *env, uint64_t frs1)
{
    return float64_to_uint64(frs1, &env->fp_status);
}
#endif

uint64_t helper_fcvt_d_w(CPURH850State *env, target_ulong rs1)
{
    return int32_to_float64((int32_t)rs1, &env->fp_status);
}

uint64_t helper_fcvt_d_wu(CPURH850State *env, target_ulong rs1)
{
    return uint32_to_float64((uint32_t)rs1, &env->fp_status);
}

#if defined(TARGET_RH85064)
uint64_t helper_fcvt_d_l(CPURH850State *env, uint64_t rs1)
{
    return int64_to_float64(rs1, &env->fp_status);
}

uint64_t helper_fcvt_d_lu(CPURH850State *env, uint64_t rs1)
{
    return uint64_to_float64(rs1, &env->fp_status);
}
#endif

target_ulong helper_fclass_d(uint64_t frs1)
{
    float64 f = frs1;
    bool sign = float64_is_neg(f);

    if (float64_is_infinity(f)) {
        return sign ? 1 << 0 : 1 << 7;
    } else if (float64_is_zero(f)) {
        return sign ? 1 << 3 : 1 << 4;
    } else if (float64_is_zero_or_denormal(f)) {
        return sign ? 1 << 2 : 1 << 5;
    } else if (float64_is_any_nan(f)) {
        float_status s = { }; /* for snan_bit_is_one */
        return float64_is_quiet_nan(f, &s) ? 1 << 9 : 1 << 8;
    } else {
        return sign ? 1 << 1 : 1 << 6;
    }
}
