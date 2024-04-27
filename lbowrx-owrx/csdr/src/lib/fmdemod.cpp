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

#include "fmdemod.hpp"

#include <algorithm>

using namespace Csdr;

FmDemod::FmDemod(): AnyLengthModule() {
    temp_dq = (float*) malloc(sizeof(float) * buffer_size);
    temp_di = (float*) malloc(sizeof(float) * buffer_size);
}

FmDemod::~FmDemod() {
    free(temp_dq);
    free(temp_di);
}

void FmDemod::process(complex<float>* input, float* output, size_t work_size) {
    temp_dq[0] = input[0].q() - last_sample.q();
    for (int i = 1; i < work_size; i++) {
        temp_dq[i] = input[i].q() - input[i-1].q();
    }

    temp_di[0] = input[0].i() - last_sample.i();
    for (int i = 1; i < work_size; i++) {
        temp_di[i] = input[i].i() - input[i-1].i();
    }

    for (int i = 0; i < work_size; i++){
        output[i] = (input[i].i() * temp_dq[i] - input[i].q() * temp_di[i]);
    }

    for (int i = 0; i < work_size; i++) {
        temp_dq[i] = input[i].i() * input[i].i() + input[i].q() * input[i].q();
    }

    for (int i = 0; i < work_size; i++) {
        output[i] = temp_dq[i] ? fmdemod_quadri_K * output[i] / temp_dq[i] : 0;
    }

    last_sample = input[work_size - 1];
}