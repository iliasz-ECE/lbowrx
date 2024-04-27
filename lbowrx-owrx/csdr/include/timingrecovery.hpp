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

#pragma once

#include "module.hpp"
#include "complex.hpp"

namespace Csdr {

    class TimingRecovery: public Module<complex<float>, complex<float>> {
        public:
            explicit TimingRecovery(unsigned int decimation, float loop_gain = 0.5f, float max_error = 2.0f, bool use_q = false);
            void process() override;
            bool canProcess() override;
        protected:
            virtual float getError() = 0;
            virtual int getErrorSign() = 0;
            float calculateError(int el_point_right_index, int el_point_left_index, int el_point_mid_index);
            unsigned int decimation;
            int correction_offset = 0;
        private:
            float loop_gain;
            float max_error;
            bool use_q;
    };

    class GardnerTimingRecovery: public TimingRecovery {
        public:
            using TimingRecovery::TimingRecovery;
        protected:
            float getError() override;
            int getErrorSign() override { return -1; }
    };

    class EarlyLateTimingRecovery: public TimingRecovery {
        public:
            using TimingRecovery::TimingRecovery;
        protected:
            float getError() override;
            int getErrorSign() override { return 1; }
        private:
            float earlylate_ratio = 0.25f;
    };

}