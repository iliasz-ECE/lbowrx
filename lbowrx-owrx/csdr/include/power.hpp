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

#include <functional>
#include "module.hpp"
#include "complex.hpp"

namespace Csdr {

    class Power: public Module<complex<float>, complex<float>> {
        public:
            Power(unsigned int decimation, std::function<void(float)> callback);
            size_t getLength();
            bool canProcess() override;
            void process() override;
        protected:
            // to bo overridden by the squelch implementation
            virtual void forwardData(complex<float>* input, float power);
        private:
            unsigned int decimation;
            std::function<void(float)> callback;
    };

    class Squelch: public Power {
        public:
            Squelch(unsigned int decimation, std::function<void(float)> callback): Power(decimation, callback) {}
            void setSquelch(float squelchLevel);
        protected:
            void forwardData(complex<float>* input, float power) override;
        private:
            float squelchLevel = 0.0f;
            unsigned char flushCounter = 0;
    };

}