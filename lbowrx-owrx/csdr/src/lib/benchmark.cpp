/*
This software is part of libcsdr, a set of simple DSP routines for
Software Defined Radio.

Copyright (c) 2014-2015, Andras Retzler <randras@sdr.hu>
Copyright (c) 2021 Jakob Ketterl <jakob.ketterl@gmx.de>
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

#include "benchmark.hpp"
#include "complex.hpp"
#include "firdecimate.hpp"
#include "window.hpp"
#include "adpcm.hpp"

#include <iostream>
#include <fcntl.h>
#include <unistd.h>

#define T_BUFSIZE (1024 * 1024 / 4)
#define T_N 200
#define T_DECFACT 10

using namespace Csdr;

template <>
complex<float>* Benchmark::getTestData() {
    std::cerr << "Getting " << T_BUFSIZE << " of random samples...\n";
    int urand_fp = open("/dev/urandom", O_RDWR);
    auto buf_u8 = (unsigned char*) malloc(sizeof(unsigned char) * T_BUFSIZE * 2);
    auto buf_c = (complex<float>*) malloc(sizeof(complex<float>) * T_BUFSIZE);
    read(urand_fp, buf_u8, T_BUFSIZE * 2);
    close(urand_fp);

    for (int i = 0; i < T_BUFSIZE; i++) {
        buf_c[i].i(buf_u8[2 * i] / 128.0);
        buf_c[i].q(buf_u8[2 * i + 1] / 128.0);
    }

    free(buf_u8);
    return buf_c;
}

template <>
float* Benchmark::getTestData() {
    std::cerr << "Getting " << T_BUFSIZE << " of random samples...\n";
    int urand_fp = open("/dev/urandom", O_RDWR);
    auto buf_u8 = (unsigned char*) malloc(sizeof(unsigned char) * T_BUFSIZE);
    auto buf_f = (float*) malloc(sizeof(float) * T_BUFSIZE);
    read(urand_fp, buf_u8, T_BUFSIZE);
    close(urand_fp);

    for (int i = 0; i < T_BUFSIZE; i++) {
        buf_f[i] = buf_u8[i] / 128.0f;
    }

    free(buf_u8);
    return buf_f;
}

template <>
short* Benchmark::getTestData() {
    std::cerr << "Getting " << T_BUFSIZE << " of random samples...\n";
    int urand_fp = open("/dev/urandom", O_RDWR);
    auto buf_u8 = (unsigned char*) malloc(sizeof(unsigned char) * T_BUFSIZE);
    auto buf_sh = (short*) malloc(sizeof(short) * T_BUFSIZE);
    read(urand_fp, buf_u8, T_BUFSIZE);
    close(urand_fp);

    for (int i = 0; i < T_BUFSIZE; i++) {
        buf_sh[i] = (((int) (buf_u8[i])) - 127) * 255;
    }

    free(buf_u8);
    return buf_sh;
}

template <typename T, typename U>
void Benchmark::runModule(Module<T, U>* module) {
    T* buf_c = getTestData<T>();
    auto reader = new MemoryReader<T>(buf_c, T_BUFSIZE);
    module->setReader(reader);
    auto writer = new VoidWriter<U>(T_BUFSIZE);
    module->setWriter(writer);

    struct ::timespec start_time, end_time;

    std::cerr << "Starting tests of processing " << T_BUFSIZE * T_N << " samples...\n";

    //fir_decimate_cc
    clock_gettime(CLOCK_MONOTONIC_RAW, &start_time);
    for (int i = 0; i < T_N; i++) {
        while (module->canProcess()) module->process();
        reader->rewind();
    }
    clock_gettime(CLOCK_MONOTONIC_RAW, &end_time);
    std::cerr << "firdecimate done in " << timeTaken(start_time, end_time) << " seconds.\n";

    delete reader;
    delete writer;
    free(buf_c);
}

void Benchmark::run() {
    auto window = new HammingWindow();
    auto module = new FirDecimate(T_DECFACT, 0.00391389432485, window);
    runModule(module);
    delete module;
    delete window;
}

double Benchmark::timeTaken(struct ::timespec start, struct ::timespec end) {
    return (end.tv_sec - start.tv_sec) + (end.tv_nsec-start.tv_nsec) / 1e9;
}
