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

#include "reader.hpp"
#include "complex.hpp"

using namespace Csdr;

template <typename T>
MemoryReader<T>::MemoryReader(T *data, size_t size): data(data), size(size) {}

template <typename T>
size_t MemoryReader<T>::available() {
    return size - read_pos;
}

template <typename T>
T* MemoryReader<T>::getReadPointer() {
    return data + read_pos;
}

template <typename T>
void MemoryReader<T>::advance(size_t how_much) {
    read_pos += how_much;
}

template <typename T>
void MemoryReader<T>::wait() {
    // not implemented. the data should be in memory already.
}

template <typename T>
void MemoryReader<T>::rewind() {
    read_pos = 0;
}

namespace Csdr {
    template class MemoryReader<complex<float>>;
    template class MemoryReader<float>;
    template class MemoryReader<short>;
}