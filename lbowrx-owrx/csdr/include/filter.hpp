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

#pragma once

#include "module.hpp"

#include <cstdlib>

namespace Csdr {

    template <typename T>
    class Filter {
        public:
            virtual ~Filter() = default;
            virtual size_t apply(T* input, T* output, size_t size) = 0;
            virtual size_t getMinProcessingSize() { return 0; }
            virtual size_t getOverhead() { return 0; };
    };

    template <typename T>
    class SparseView;

    template <typename T>
    class SampleFilter: public Filter<T> {
        public:
            SparseView<T> sparse(T* data);
            virtual T processSample(T* data, size_t index) = 0;
            size_t apply(T* input, T* output, size_t size) override;
    };

    template <typename T>
    class SparseView {
        public:
            SparseView<T>(T* data, SampleFilter<T>* filter);
            T operator[](size_t index);
        private:
            T* data;
            SampleFilter<T>* filter;
    };

    template <typename T>
    class FilterModule: public Module<T, T> {
        public:
            explicit FilterModule(Filter<T>* filter);
            ~FilterModule() override;
            bool canProcess() override;
            void process() override;
            void setFilter(Filter<T>* filter);
        private:
            Filter<T>* filter;
    };
}