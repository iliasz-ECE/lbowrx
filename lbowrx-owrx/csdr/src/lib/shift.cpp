/*
This software is part of libcsdr, a set of simple DSP routines for
Software Defined Radio.

Copyright (c) 2014, Andras Retzler <randras@sdr.hu>
Copyright (c) 2019-2021 Jakob Ketterl <jakob.ketterl@gmx.de>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the copyright holder nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL ANDRAS RETZLER BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include "shift.hpp"
#include "fmv.h"

#include <cmath>

using namespace Csdr;

Shift::Shift(float rate): rate(rate) {}

void Shift::setRate(float rate) {
    this->rate = rate;
}

ShiftAddfast::ShiftAddfast(float rate): Shift(rate) {
    ShiftAddfast::setRate(rate);
}

void ShiftAddfast::setRate(float rate) {
    Shift::setRate(rate);
    phase_increment = 2.0f * rate * M_PI;
    for (int i = 0; i < 4; i++) {
        dsin[i] = sin(phase_increment * (i + 1));
        dcos[i] = cos(phase_increment * (i + 1));
    }
}

#define SADF_L1(j) cos_vals_ ## j = cos_start * dcos_ ## j - sin_start * dsin_ ## j; \
    sin_vals_ ## j = sin_start * dcos_ ## j + cos_start * dsin_ ## j;
#define SADF_L2(j) output[4 * i + j].i((cos_vals_ ## j) * input[4 * i + j].i() - (sin_vals_ ## j) * input[4 * i + j].q()); \
    output[4 * i + j].q((sin_vals_ ## j) * input[4 * i + j].i() + (cos_vals_ ## j) * input[4 * i + j].q());

void ShiftAddfast::process(complex<float>* input, complex<float>* output) {
    // indirection since FMV on virtual functions does not work...
    process_fmv(input, output, 1024);
}

CSDR_TARGET_CLONES
void ShiftAddfast::process_fmv(complex<float>* input, complex<float>* output, size_t size) {
    //input_size should be multiple of 4
    float cos_start = cos(starting_phase);
    float sin_start = sin(starting_phase);
    float register cos_vals_0, cos_vals_1, cos_vals_2, cos_vals_3,
        sin_vals_0, sin_vals_1, sin_vals_2, sin_vals_3,
        dsin_0 = dsin[0], dsin_1 = dsin[1], dsin_2 = dsin[2], dsin_3 = dsin[3],
        dcos_0 = dcos[0], dcos_1 = dcos[1], dcos_2 = dcos[2], dcos_3 = dcos[3];

    for (int i = 0; i < size / 4; i++) {
        SADF_L1(0)
        SADF_L1(1)
        SADF_L1(2)
        SADF_L1(3)
        SADF_L2(0)
        SADF_L2(1)
        SADF_L2(2)
        SADF_L2(3)
        cos_start = cos_vals_3;
        sin_start = sin_vals_3;
    }
    starting_phase += size * phase_increment;
    while (starting_phase > M_PI) starting_phase -= 2 * M_PI;
    while (starting_phase < -M_PI) starting_phase += 2 * M_PI;
}

ShiftMath::ShiftMath(float rate): Shift(rate) {
    ShiftMath::setRate(rate);
}

void ShiftMath::setRate(float rate) {
    Shift::setRate(rate);
    phase_increment = 2.0f * rate * M_PI;
}

void ShiftMath::process(complex<float> *input, complex<float> *output, size_t size) {
    process_fmv(input, output, size);
}

CSDR_TARGET_CLONES
void ShiftMath::process_fmv(complex<float>* input, complex<float>* output, size_t size) {
    //rate *= 2;
    //Shifts the complex spectrum. Basically a complex mixer. This version uses cmath.
    float cosval, sinval;
    for (int i = 0; i < size; i++) {
        float phaseval = phase_increment * i + phase;
        sincosf(phaseval, &sinval, &cosval);
        output[i] = input[i] * complex<float>(cosval, sinval);
    }

    phase = phase_increment * size + phase;
    while (phase > 2 * M_PI) phase -= 2 * M_PI;
    while (phase < 0) phase += 2 * M_PI;

}
