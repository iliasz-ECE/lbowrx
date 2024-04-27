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

#include "fir.hpp"
#include "complex.hpp"
#include "fmv.h"

#include <cmath>
#include <cstring>
#include <fftw3.h>

#include <iostream>

using namespace Csdr;

template <typename T, typename U>
FirFilter<T, U>::FirFilter(size_t length) {
    allocateTaps(length);
}

template <typename T, typename U>
FirFilter<T, U>::FirFilter(U* taps, size_t length): FirFilter(length) {
    // better to copy the taps to our memory since that is aligned
    std::memcpy(this->taps, taps, sizeof(U) * length);
}

template <typename T, typename U>
FirFilter<T, U>::~FirFilter() {
    free(taps);
}

template <typename T, typename U>
T FirFilter<T, U>::processSample(T *data, size_t index) {
    return processSample_fmv(data, index);
}

template <typename T, typename U>
CSDR_TARGET_CLONES
T FirFilter<T, U>::processSample_fmv(T *data, size_t index) {
    T acc = 0;
    for (size_t ti = 0; ti < taps_length; ti++) {
        acc += data[index + ti] * taps[ti];
    }
    return acc;
}

template <typename T, typename U>
size_t FirFilter<T, U>::filterLength(float transition) {
    size_t result = 4.0 / transition;
    if (result % 2 == 0) result++; //number of symmetric FIR filter taps should be odd
    return result;
}

template <typename T, typename U>
size_t FirFilter<T, U>::getOverhead() {
    return taps_length;
}

template<typename T, typename U>
void FirFilter<T, U>::allocateTaps(size_t length) {
    taps = (U*) malloc(length * sizeof(U));
    taps_length = length;
}

template<typename T>
TapGenerator<T>::TapGenerator(Window *window): window(window) {}

template <>
complex<float>* TapGenerator<complex<float>>::generateFftTaps(size_t length, size_t fftSize) {
    complex<float>* taps = generateTaps(length);
    for (size_t i = 0; i < length; i++) {
        // reverse the taps - in FFT, things are upside down
        taps[i] = { taps[i].q(), taps[i].i() };
    }
    taps = (complex<float>*) realloc(taps, sizeof(complex<float>) * fftSize);
    for (size_t i = length; i < fftSize; i++) taps[i] = 0.0f;
    fftwf_complex* output_buffer = fftwf_alloc_complex(fftSize);
    fftwf_plan plan = fftwf_plan_dft_1d(fftSize, (fftwf_complex*) taps, output_buffer, FFTW_FORWARD, FFTW_ESTIMATE);
    fftwf_execute(plan);
    fftwf_destroy_plan(plan);
    free(taps);
    return (complex<float>*) output_buffer;
}

template <>
complex<float>* TapGenerator<float>::generateFftTaps(size_t length, size_t fftSize) {
    float* taps = generateTaps(length);
    taps = (float*) realloc(taps, sizeof(float) * fftSize);
    for (size_t i = length; i < fftSize; i++) taps[i] = 0.0f;
    fftwf_complex* output_buffer = fftwf_alloc_complex(fftSize);
    fftwf_plan plan = fftwf_plan_dft_r2c_1d(fftSize, taps, output_buffer, FFTW_ESTIMATE);
    fftwf_execute(plan);
    fftwf_destroy_plan(plan);
    free(taps);
    return (complex<float>*) output_buffer;
}

template<>
void TapGenerator<float>::normalize(float* taps, size_t length) {
    //Normalize filter kernel
    float sum = 0;
    for (int i = 0; i < length; i++) sum += taps[i];
    for (int i = 0; i < length; i++) taps[i] = taps[i] / sum;
}

template<>
void TapGenerator<complex<float>>::normalize(complex<float>* taps, size_t length) {
    //Normalize filter kernel
    float sum = 0;
    for (int i = 0; i < length; i++) sum += std::abs(taps[i]);
    for (int i = 0; i < length; i++) taps[i] = taps[i] / sum;
}

LowPassTapGenerator::LowPassTapGenerator(float cutoff, Window *window):
    TapGenerator<float>(window),
    cutoff(cutoff)
{}

float* LowPassTapGenerator::generateTaps(size_t length) {
    //Generates symmetric windowed sinc FIR filter real taps
    //  cutoff_rate is (cutoff frequency/sampling frequency)
    //Explanation at Chapter 16 of dspguide.com
    int middle = length / 2;
    auto taps = (float*) malloc(sizeof(float) * length);
    taps[middle] = 2 * M_PI * cutoff * window->kernel(0);
    for (int i = 1; i <= middle; i++)  {
        // by definition: assigning a scalar to a complex assigns the real part (our i) only,
        // with the imaginary part (our q) set to zero
        taps[middle - i] = taps[middle + i] =
                (sinf(2 * M_PI * cutoff * i) / i) * window->kernel((float) i / middle);
    }
    this->normalize(taps, length);
    return taps;
}

template <typename T>
LowPassFilter<T>::LowPassFilter(float cutoff, float transition, Window *window):
    FirFilter<T, float>(LowPassFilter<T>::filterLength(transition))
{
    auto generator = new LowPassTapGenerator(cutoff, window);
    float* taps = generator->generateTaps(this->taps_length);
    memcpy(this->taps, taps, sizeof(float) * this->taps_length);
    free(taps);
    delete generator;
}

BandPassTapGenerator::BandPassTapGenerator(float lowcut, float highcut, Window *window):
    TapGenerator<complex<float>>(window),
    lowcut(lowcut),
    highcut(highcut)
{}

complex<float> * BandPassTapGenerator::generateTaps(size_t length) {
    //To generate a complex filter:
    //  1. we generate a real lowpass filter with a bandwidth of highcut-lowcut
    //  2. we shift the filter taps spectrally by multiplying with e^(j*w), so we get complex taps
    //(tnx HA5FT)

    auto lowpassGenerator = new LowPassTapGenerator((highcut - lowcut) / 2, window);
    float* realTaps = lowpassGenerator->generateTaps(length);
    delete lowpassGenerator;

    auto taps = (complex<float>*) malloc(sizeof(complex<float>) * length);
    float filter_center = (highcut + lowcut) / 2;
    float phase = 0, sinval, cosval;

    for(int i = 0; i < length; i++) {
        sincosf(phase, &sinval, &cosval);
        phase += 2.0f * M_PI * filter_center;
        while (phase > 2 * M_PI) phase -= 2 * M_PI;
        while (phase < 0) phase += 2 * M_PI;
        taps[i] = realTaps[i] * complex<float>(sinval, cosval);
    }

    free(realTaps);
    return taps;
}

template<typename T>
BandPassFilter<T>::BandPassFilter(float lowcut, float highcut, float transition, Window *window):
    FirFilter<T, complex<float>>(BandPassFilter<T>::filterLength(transition))
{
    auto generator = new BandPassTapGenerator(lowcut, highcut, window);
    complex<float>* taps = generator->generateTaps(this->taps_length);
    memcpy(this->taps, taps, sizeof(complex<float>) * this->taps_length);
    delete generator;
    free(taps);
}

namespace Csdr {
    template class FirFilter<complex<float>, complex<float>>;
    template class FirFilter<complex<float>, float>;
    template class FirFilter<float, float>;

    template class LowPassFilter<complex<float>>;
    template class LowPassFilter<float>;

    template class BandPassFilter<complex<float>>;
}