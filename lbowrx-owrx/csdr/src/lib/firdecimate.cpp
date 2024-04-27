/*
Copyright (c) 2021 Jakob Ketterl <jakob.ketterl@gmx.de>

This file is part of libcsdr.

libcsdr is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

libcsdr is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with libcsdr.  If not, see <https://www.gnu.org/licenses/>.
*/

#include "firdecimate.hpp"

using namespace Csdr;

FirDecimate::FirDecimate(unsigned int decimation, float transitionBandwidth, Window* window, float cutoff):
    decimation(decimation),
    lowpass(new LowPassFilter<complex<float>>(cutoff / (float) decimation, transitionBandwidth, window))
{}

FirDecimate::FirDecimate(unsigned int decimation, float transitionBandwidth, Window* window):
    FirDecimate(decimation, transitionBandwidth, window, 0.5f)
{}

FirDecimate::~FirDecimate() {
    delete lowpass;
}

void FirDecimate::process() {
    std::lock_guard<std::mutex> lock(processMutex);
    size_t available = reader->available();
    size_t writeable = writer->writeable();
    size_t lpLen = lowpass->getOverhead();

    // sanity check
    // if this condition is not met, the calculation below produces impossible results due to negative numbers
    if (available < lpLen) return;

    size_t samples = std::min((available - lpLen) / decimation, writeable);

    complex<float>* output = writer->getWritePointer();
    SparseView<complex<float>> sparseView = lowpass->sparse(reader->getReadPointer());
    for (size_t i = 0; i < samples; i++) {
        output[i] = sparseView[i * decimation];
    }
    reader->advance(samples * decimation);
    writer->advance(samples);
}

bool FirDecimate::canProcess() {
    std::lock_guard<std::mutex> lock(processMutex);
    size_t available = reader->available();
    size_t writeable = writer->writeable();
    size_t lpLen = lowpass->getOverhead();
    return available > lpLen && (available - lpLen) / decimation > 0 && writeable > 0;
}
