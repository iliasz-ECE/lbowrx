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

#include "gain.hpp"

using namespace Csdr;


template<typename T>
Gain<T>::Gain(float gain): gain(gain) {}

template<typename T>
void Gain<T>::process(T *input, T *output, size_t size) {
    for (size_t i = 0; i < size; i++) {
        output[i] = static_cast<T>(input[i] * gain);
    }
}

namespace Csdr {
    template class Gain<float>;
    template class Gain<complex<float>>;
}