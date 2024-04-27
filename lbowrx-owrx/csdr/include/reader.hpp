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

#include "complex.hpp"

#include <cstdlib>

namespace Csdr {

    // container class for template-agnostic storage
    class UntypedReader {
        public:
            virtual ~UntypedReader() = default;
            virtual size_t available() = 0;
            virtual void advance(size_t how_much) = 0;
            virtual void wait() = 0;
            virtual void unblock() = 0;
    };

    template <typename T>
    class Reader: public UntypedReader {
        public:
            virtual T* getReadPointer() = 0;
    };

    template <typename T>
    class MemoryReader: public Reader<T> {
        public:
            MemoryReader(T* data, size_t size);
            size_t available() override;
            T* getReadPointer() override;
            void advance(size_t how_much) override;
            void wait() override;
            void unblock() override {}
            void rewind();
        private:
            T* data;
            size_t size;
            size_t read_pos = 0;
    };

}