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

#include "window.hpp"
#include "complex.hpp"
#include <cmath>

using namespace Csdr;

template<> void Window::apply<float>(float* input, float* output, size_t size) {
    for (size_t i = 0; i <size; i++) {
        float rate = (float) i / (size - 1);
        output[i] = input[i] * kernel(2.0 * rate + 1.0);
    }
}

template<> void Window::apply<complex<float>>(complex<float>* input, complex<float>* output, size_t size) {
    for (size_t i = 0; i < size; i++) {
        float rate = (float) i / (size - 1);
        output[i].i(input[i].i() * kernel(2.0 * rate + 1.0));
        output[i].q(input[i].q() * kernel(2.0 * rate + 1.0));
    }
}

PrecalculatedWindow* Window::precalculate(size_t size) {
    float *windowt;
    windowt = (float*) malloc(sizeof(float) * size);
    for (size_t i = 0; i < size; i++) {
        float rate = (float) i / (size-1);
        windowt[i] = kernel(2.0 * rate + 1.0);
    }
    return new PrecalculatedWindow(windowt, size);
}

PrecalculatedWindow::PrecalculatedWindow(float* windowt, size_t size): windowt(windowt), size(size) {}

PrecalculatedWindow::~PrecalculatedWindow() {
    free(windowt);
}

template<> void PrecalculatedWindow::apply<float>(float* input, float* output, size_t size) {
	for (size_t i = 0; i < size; i++) {
		output[i] = input[i] * windowt[i];
	}
}

template<> void PrecalculatedWindow::apply<complex<float>>(complex<float>* input, complex<float>* output, size_t size) {
    for (size_t i = 0; i < size; i++) {
        output[i].i(input[i].i() * windowt[i]);
        output[i].q(input[i].q() * windowt[i]);
    }
}

float BoxcarWindow::kernel(float rate) {
    //"Dummy" window kernel, do not use; an unwindowed FIR filter may have bad frequency response
    return 1.0;
}

float BlackmanWindow::kernel(float rate) {
    //Explanation at Chapter 16 of dspguide.com, page 2
    //Blackman window has better stopband attentuation and passband ripple than Hamming, but it has slower rolloff.
    rate = 0.5 + rate / 2;
    return 0.42 - 0.5 * cos(2 * M_PI * rate) + 0.08 * cos(4 * M_PI * rate);
}

float HammingWindow::kernel(float rate) {
    //Explanation at Chapter 16 of dspguide.com, page 2
    //Hamming window has worse stopband attentuation and passband ripple than Blackman, but it has faster rolloff.
    rate = 0.5 + rate / 2;
    return 0.54 - 0.46 * cos(2 * M_PI * rate);
}
