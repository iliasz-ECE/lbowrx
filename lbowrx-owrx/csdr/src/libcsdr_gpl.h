/*
This file is part of libcsdr.

	Copyright (c) Andras Retzler, HA7ILM <randras@sdr.hu>
	Copyright (c) Warren Pratt, NR0V <warren@wpratt.com>
    Copyright (c) Jakob Ketterl, DD5JFK <jakob.ketterl@gmx.de>
	Copyright 2006,2010,2012 Free Software Foundation, Inc.

    libcsdr is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    libcsdr is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with libcsdr.  If not, see <http://www.gnu.org/licenses/>.
*/

#pragma once

#ifdef LIBCSDR_GPL

#include "libcsdr.h"
#include <math.h>
#include <stdlib.h>
#include <limits.h>

typedef struct shift_addition_data_s
{
	float sindelta;
	float cosdelta;
	float rate;
} shift_addition_data_t;
shift_addition_data_t shift_addition_init(float rate);
float shift_addition_cc(complexf *input, complexf* output, int input_size, shift_addition_data_t d, float starting_phase);
float shift_addition_fc(float *input, complexf* output, int input_size, shift_addition_data_t d, float starting_phase);
void shift_addition_cc_test(shift_addition_data_t d);

typedef struct {
    float last_gain;
    unsigned long int hang_counter;
    short attack_wait_counter;
    float xk;
    float vk;
} agc_state;

typedef struct {
    float reference;
    float attack_rate;
    float decay_rate;
    float max_gain;
    unsigned long int hang_time;
    short attack_wait_time;
    float gain_filter_alpha;
} agc_params;

agc_state* agc_ff(float* input, float* output, int input_size, agc_params* params, agc_state* state);

agc_state* agc_s16(short* input, short* output, int input_size, agc_params* params, agc_state* state);

typedef struct decimating_shift_addition_status_s
{
	int decimation_remain;
	float starting_phase;
	int output_size;
} decimating_shift_addition_status_t;
decimating_shift_addition_status_t decimating_shift_addition_cc(complexf *input, complexf* output, int input_size, shift_addition_data_t d, int decimation, decimating_shift_addition_status_t s);
shift_addition_data_t decimating_shift_addition_init(float rate, int decimation);

#endif

