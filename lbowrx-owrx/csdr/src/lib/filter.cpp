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

#include "filter.hpp"
#include "complex.hpp"

using namespace Csdr;

template<typename T>
SparseView<T> SampleFilter<T>::sparse(T* data) {
    return SparseView<T>(data, this);
}

template <typename T>
size_t SampleFilter<T>::apply(T *input, T *output, size_t size) {
    for (size_t i = 0; i < size; i++) {
        output[i] = processSample(input, i);
    }
    return size;
}

template<typename T>
SparseView<T>::SparseView(T *data, SampleFilter<T> *filter):
    data(data),
    filter(filter)
{}

template<typename T>
T SparseView<T>::operator[](size_t index) {
    return filter->processSample(data, index);
}

template <typename T>
FilterModule<T>::FilterModule(Filter<T> *filter): filter(filter) {}

template <typename T>
FilterModule<T>::~FilterModule() {
    delete filter;
}

template <typename T>
void FilterModule<T>::setFilter(Filter<T>* filter) {
    std::lock_guard<std::mutex> lock(this->processMutex);
    delete this->filter;
    this->filter = filter;
}

template <typename T>
bool FilterModule<T>::canProcess() {
    std::lock_guard<std::mutex> lock(this->processMutex);
    return this->reader->available() > filter->getMinProcessingSize() + filter->getOverhead() && this->writer->writeable() > filter->getMinProcessingSize();
}

template <typename T>
void FilterModule<T>::process() {
    std::lock_guard<std::mutex> lock(this->processMutex);
    size_t available = this->reader->available();
    size_t writeable = this->writer->writeable();
    size_t filterOverhead = filter->getOverhead();

    // sanity check
    // if this condition is not met, the calculation below produces impossible results due to negative numbers
    if (available < filterOverhead) return;

    size_t size = std::min(available - filterOverhead, writeable);

    T* input = this->reader->getReadPointer();
    T* output = this->writer->getWritePointer();
    size = filter->apply(input, output, size);
    this->reader->advance(size);
    this->writer->advance(size);
}

namespace Csdr {
    template class SampleFilter<complex<float>>;
    template class SampleFilter<float>;

    template class SparseView<complex<float>>;
    template class SparseView<float>;

    template class FilterModule<complex<float>>;
    template class FilterModule<float>;
}