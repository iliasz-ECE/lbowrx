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

namespace Csdr {
    struct varicode_item {
        unsigned long long code;
        int bitcount;
        unsigned char ascii;
    };


    class VaricodeDecoder: public Module<unsigned char, unsigned char> {
        public:
            bool canProcess() override;
            void process() override;
        private:
            unsigned long long status = 0;
            static constexpr varicode_item varicode_items[] = {
                { .code = 0b1010101011, .bitcount=10,   .ascii=0x00 }, //NUL, null
                { .code = 0b1011011011, .bitcount=10,   .ascii=0x01 }, //SOH, start of heading
                { .code = 0b1011101101, .bitcount=10,   .ascii=0x02 }, //STX, start of text
                { .code = 0b1101110111, .bitcount=10,   .ascii=0x03 }, //ETX, end of text
                { .code = 0b1011101011, .bitcount=10,   .ascii=0x04 }, //EOT, end of transmission
                { .code = 0b1101011111, .bitcount=10,   .ascii=0x05 }, //ENQ, enquiry
                { .code = 0b1011101111, .bitcount=10,   .ascii=0x06 }, //ACK, acknowledge
                { .code = 0b1011111101, .bitcount=10,   .ascii=0x07 }, //BEL, bell
                { .code = 0b1011111111, .bitcount=10,   .ascii=0x08 }, //BS, backspace
                { .code = 0b11101111,   .bitcount=8,    .ascii=0x09 }, //TAB, horizontal tab
                { .code = 0b11101,      .bitcount=5,    .ascii=0x0a }, //LF, NL line feed, new line
                { .code = 0b1101101111, .bitcount=10,   .ascii=0x0b }, //VT, vertical tab
                { .code = 0b1011011101, .bitcount=10,   .ascii=0x0c }, //FF, NP form feed, new page
                { .code = 0b11111,      .bitcount=5,    .ascii=0x0d }, //CR, carriage return (overwrite)
                { .code = 0b1101110101, .bitcount=10,   .ascii=0x0e }, //SO, shift out
                { .code = 0b1110101011, .bitcount=10,   .ascii=0x0f }, //SI, shift in
                { .code = 0b1011110111, .bitcount=10,   .ascii=0x10 }, //DLE, data link escape
                { .code = 0b1011110101, .bitcount=10,   .ascii=0x11 }, //DC1, device control 1
                { .code = 0b1110101101, .bitcount=10,   .ascii=0x12 }, //DC2, device control 2
                { .code = 0b1110101111, .bitcount=10,   .ascii=0x13 }, //DC3, device control 3
                { .code = 0b1101011011, .bitcount=10,   .ascii=0x14 }, //DC4, device control 4
                { .code = 0b1101101011, .bitcount=10,   .ascii=0x15 }, //NAK, negative acknowledge
                { .code = 0b1101101101, .bitcount=10,   .ascii=0x16 }, //SYN, synchronous idle
                { .code = 0b1101010111, .bitcount=10,   .ascii=0x17 }, //ETB, end of trans. block
                { .code = 0b1101111011, .bitcount=10,   .ascii=0x18 }, //CAN, cancel
                { .code = 0b1101111101, .bitcount=10,   .ascii=0x19 }, //EM, end of medium
                { .code = 0b1110110111, .bitcount=10,   .ascii=0x1a }, //SUB, substitute
                { .code = 0b1101010101, .bitcount=10,   .ascii=0x1b }, //ESC, escape
                { .code = 0b1101011101, .bitcount=10,   .ascii=0x1c }, //FS, file separator
                { .code = 0b1110111011, .bitcount=10,   .ascii=0x1d }, //GS, group separator
                { .code = 0b1011111011, .bitcount=10,   .ascii=0x1e }, //RS, record separator
                { .code = 0b1101111111, .bitcount=10,   .ascii=0x1f }, //US, unit separator
                { .code = 0b1,          .bitcount=1,    .ascii=0x20 }, //szóköz
                { .code = 0b111111111,  .bitcount=9,    .ascii=0x21 }, //!
                { .code = 0b101011111,  .bitcount=9,    .ascii=0x22 }, //"
                { .code = 0b111110101,  .bitcount=9,    .ascii=0x23 }, //#
                { .code = 0b111011011,  .bitcount=9,    .ascii=0x24 }, //$
                { .code = 0b1011010101, .bitcount=10,   .ascii=0x25 }, //%
                { .code = 0b1010111011, .bitcount=10,   .ascii=0x26 }, //&
                { .code = 0b101111111,  .bitcount=9,    .ascii=0x27 }, //'
                { .code = 0b11111011,   .bitcount=8,    .ascii=0x28 }, //(
                { .code = 0b11110111,   .bitcount=8,    .ascii=0x29 }, //)
                { .code = 0b101101111,  .bitcount=9,    .ascii=0x2a }, //*
                { .code = 0b111011111,  .bitcount=9,    .ascii=0x2b }, //+
                { .code = 0b1110101,    .bitcount=7,    .ascii=0x2c }, //,
                { .code = 0b110101,     .bitcount=6,    .ascii=0x2d }, //-
                { .code = 0b1010111,    .bitcount=7,    .ascii=0x2e }, //.
                { .code = 0b110101111,  .bitcount=9,    .ascii=0x2f }, ///
                { .code = 0b10110111,   .bitcount=8,    .ascii=0x30 }, //0
                { .code = 0b10111101,   .bitcount=8,    .ascii=0x31 }, //1
                { .code = 0b11101101,   .bitcount=8,    .ascii=0x32 }, //2
                { .code = 0b11111111,   .bitcount=8,    .ascii=0x33 }, //3
                { .code = 0b101110111,  .bitcount=9,    .ascii=0x34 }, //4
                { .code = 0b101011011,  .bitcount=9,    .ascii=0x35 }, //5
                { .code = 0b101101011,  .bitcount=9,    .ascii=0x36 }, //6
                { .code = 0b110101101,  .bitcount=9,    .ascii=0x37 }, //7
                { .code = 0b110101011,  .bitcount=9,    .ascii=0x38 }, //8
                { .code = 0b110110111,  .bitcount=9,    .ascii=0x39 }, //9
                { .code = 0b11110101,   .bitcount=8,    .ascii=0x3a }, //:
                { .code = 0b110111101,  .bitcount=9,    .ascii=0x3b }, //;
                { .code = 0b111101101,  .bitcount=9,    .ascii=0x3c }, //<
                { .code = 0b1010101,    .bitcount=7,    .ascii=0x3d }, //=
                { .code = 0b111010111,  .bitcount=9,    .ascii=0x3e }, //>
                { .code = 0b1010101111, .bitcount=10,   .ascii=0x3f }, //?
                { .code = 0b1010111101, .bitcount=10,   .ascii=0x40 }, //@
                { .code = 0b1111101,    .bitcount=7,    .ascii=0x41 }, //A
                { .code = 0b11101011,   .bitcount=8,    .ascii=0x42 }, //B
                { .code = 0b10101101,   .bitcount=8,    .ascii=0x43 }, //C
                { .code = 0b10110101,   .bitcount=8,    .ascii=0x44 }, //D
                { .code = 0b1110111,    .bitcount=7,    .ascii=0x45 }, //E
                { .code = 0b11011011,   .bitcount=8,    .ascii=0x46 }, //F
                { .code = 0b11111101,   .bitcount=8,    .ascii=0x47 }, //G
                { .code = 0b101010101,  .bitcount=9,    .ascii=0x48 }, //H
                { .code = 0b1111111,    .bitcount=7,    .ascii=0x49 }, //I
                { .code = 0b111111101,  .bitcount=9,    .ascii=0x4a }, //J
                { .code = 0b101111101,  .bitcount=9,    .ascii=0x4b }, //K
                { .code = 0b11010111,   .bitcount=8,    .ascii=0x4c }, //L
                { .code = 0b10111011,   .bitcount=8,    .ascii=0x4d }, //M
                { .code = 0b11011101,   .bitcount=8,    .ascii=0x4e }, //N
                { .code = 0b10101011,   .bitcount=8,    .ascii=0x4f }, //O
                { .code = 0b11010101,   .bitcount=8,    .ascii=0x50 }, //P
                { .code = 0b111011101,  .bitcount=9,    .ascii=0x51 }, //Q
                { .code = 0b10101111,   .bitcount=8,    .ascii=0x52 }, //R
                { .code = 0b1101111,    .bitcount=7,    .ascii=0x53 }, //S
                { .code = 0b1101101,    .bitcount=7,    .ascii=0x54 }, //T
                { .code = 0b101010111,  .bitcount=9,    .ascii=0x55 }, //U
                { .code = 0b110110101,  .bitcount=9,    .ascii=0x56 }, //V
                { .code = 0b101011101,  .bitcount=9,    .ascii=0x57 }, //W
                { .code = 0b101110101,  .bitcount=9,    .ascii=0x58 }, //X
                { .code = 0b101111011,  .bitcount=9,    .ascii=0x59 }, //Y
                { .code = 0b1010101101, .bitcount=10,   .ascii=0x5a }, //Z
                { .code = 0b111110111,  .bitcount=9,    .ascii=0x5b }, //[
                { .code = 0b111101111,  .bitcount=9,    .ascii=0x5c }, //backslash
                { .code = 0b111111011,  .bitcount=9,    .ascii=0x5d }, //]
                { .code = 0b1010111111, .bitcount=10,   .ascii=0x5e }, //^
                { .code = 0b101101101,  .bitcount=9,    .ascii=0x5f }, //_
                { .code = 0b1011011111, .bitcount=10,   .ascii=0x60 }, //`
                { .code = 0b1011,       .bitcount=4,    .ascii=0x61 }, //a
                { .code = 0b1011111,    .bitcount=7,    .ascii=0x62 }, //b
                { .code = 0b101111,     .bitcount=6,    .ascii=0x63 }, //c
                { .code = 0b101101,     .bitcount=6,    .ascii=0x64 }, //d
                { .code = 0b11,         .bitcount=2,    .ascii=0x65 }, //e
                { .code = 0b111101,     .bitcount=6,    .ascii=0x66 }, //f
                { .code = 0b1011011,    .bitcount=7,    .ascii=0x67 }, //g
                { .code = 0b101011,     .bitcount=6,    .ascii=0x68 }, //h
                { .code = 0b1101,       .bitcount=4,    .ascii=0x69 }, //i
                { .code = 0b111101011,  .bitcount=9,    .ascii=0x6a }, //j
                { .code = 0b10111111,   .bitcount=8,    .ascii=0x6b }, //k
                { .code = 0b11011,      .bitcount=5,    .ascii=0x6c }, //l
                { .code = 0b111011,     .bitcount=6,    .ascii=0x6d }, //m
                { .code = 0b1111,       .bitcount=4,    .ascii=0x6e }, //n
                { .code = 0b111,        .bitcount=3,    .ascii=0x6f }, //o
                { .code = 0b111111,     .bitcount=6,    .ascii=0x70 }, //p
                { .code = 0b110111111,  .bitcount=9,    .ascii=0x71 }, //q
                { .code = 0b10101,      .bitcount=5,    .ascii=0x72 }, //r
                { .code = 0b10111,      .bitcount=5,    .ascii=0x73 }, //s
                { .code = 0b101,        .bitcount=3,    .ascii=0x74 }, //t
                { .code = 0b110111,     .bitcount=6,    .ascii=0x75 }, //u
                { .code = 0b1111011,    .bitcount=7,    .ascii=0x76 }, //v
                { .code = 0b1101011,    .bitcount=7,    .ascii=0x77 }, //w
                { .code = 0b11011111,   .bitcount=8,    .ascii=0x78 }, //x
                { .code = 0b1011101,    .bitcount=7,    .ascii=0x79 }, //y
                { .code = 0b111010101,  .bitcount=9,    .ascii=0x7a }, //z
                { .code = 0b1010110111, .bitcount=10,   .ascii=0x7b }, //{
                { .code = 0b110111011,  .bitcount=9,    .ascii=0x7c }, //|
                { .code = 0b1010110101, .bitcount=10,   .ascii=0x7d }, //}
                { .code = 0b1011010111, .bitcount=10,   .ascii=0x7e }, //~
                { .code = 0b1110110101, .bitcount=10,   .ascii=0x7f }, //DEL
            };
    };

}