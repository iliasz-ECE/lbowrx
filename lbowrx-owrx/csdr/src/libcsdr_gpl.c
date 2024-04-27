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

#include "libcsdr_gpl.h"

#ifdef LIBCSDR_GPL

float shift_addition_cc(complexf *input, complexf* output, int input_size, shift_addition_data_t d, float starting_phase)
{
	//The original idea was taken from wdsp:
	//http://svn.tapr.org/repos_sdr_hpsdr/trunk/W5WC/PowerSDR_HPSDR_mRX_PS/Source/wdsp/shift.c

	//However, this method introduces noise (from floating point rounding errors), which increases until the end of the buffer.
	//fprintf(stderr, "cosd=%g sind=%g\n", d.cosdelta, d.sindelta);
	float cosphi=cos(starting_phase);
	float sinphi=sin(starting_phase);
	float cosphi_last, sinphi_last;
	for(int i=0;i<input_size;i++) //@shift_addition_cc: work
	{
		iof(output,i)=cosphi*iof(input,i)-sinphi*qof(input,i);
		qof(output,i)=sinphi*iof(input,i)+cosphi*qof(input,i);
		//using the trigonometric addition formulas
		//cos(phi+delta)=cos(phi)cos(delta)-sin(phi)*sin(delta)
		cosphi_last=cosphi;
		sinphi_last=sinphi;
		cosphi=cosphi_last*d.cosdelta-sinphi_last*d.sindelta;
		sinphi=sinphi_last*d.cosdelta+cosphi_last*d.sindelta;
	}
	starting_phase+=d.rate*PI*input_size;
	while(starting_phase>PI) starting_phase-=2*PI; //@shift_addition_cc: normalize starting_phase
	while(starting_phase<-PI) starting_phase+=2*PI;
	return starting_phase;
}

float shift_addition_fc(float *input, complexf* output, int input_size, shift_addition_data_t d, float starting_phase)
{
	//The original idea was taken from wdsp:
	//http://svn.tapr.org/repos_sdr_hpsdr/trunk/W5WC/PowerSDR_HPSDR_mRX_PS/Source/wdsp/shift.c

	//However, this method introduces noise (from floating point rounding errors), which increases until the end of the buffer.
	//fprintf(stderr, "cosd=%g sind=%g\n", d.cosdelta, d.sindelta);
	float cosphi=cos(starting_phase);
	float sinphi=sin(starting_phase);
	float cosphi_last, sinphi_last;
	for(int i=0;i<input_size;i++) //@shift_addition_cc: work
	{
		iof(output,i)=cosphi*input[i];
		qof(output,i)=sinphi*input[i];
		//using the trigonometric addition formulas
		//cos(phi+delta)=cos(phi)cos(delta)-sin(phi)*sin(delta)
		cosphi_last=cosphi;
		sinphi_last=sinphi;
		cosphi=cosphi_last*d.cosdelta-sinphi_last*d.sindelta;
		sinphi=sinphi_last*d.cosdelta+cosphi_last*d.sindelta;
	}
	starting_phase+=d.rate*PI*input_size;
	while(starting_phase>PI) starting_phase-=2*PI; //@shift_addition_cc: normalize starting_phase
	while(starting_phase<-PI) starting_phase+=2*PI;
	return starting_phase;
}

shift_addition_data_t shift_addition_init(float rate)
{
	rate*=2;
	shift_addition_data_t out;
	out.sindelta=sin(rate*PI);
	out.cosdelta=cos(rate*PI);
	out.rate=rate;
	return out;
}

#define SACCTEST_LOOPS 50
#define SACCTEST_STEP 10000

void shift_addition_cc_test(shift_addition_data_t d)
{
	float phi=0;
	float cosphi=cos(phi);
	float sinphi=sin(phi);
	float cosphi_last, sinphi_last;
	int avg_size=(int)(2.0/d.rate+1.0); //average one period of sine
	int avg_counter=0;
	float avg=0;
	printf("error_vector=[");
	for(unsigned i=0;i<SACCTEST_STEP*SACCTEST_LOOPS;i++) //@shift_addition_cc: work
	{
		cosphi_last=cosphi;
		sinphi_last=sinphi;
		cosphi=cosphi_last*d.cosdelta-sinphi_last*d.sindelta;
		sinphi=sinphi_last*d.cosdelta+cosphi_last*d.sindelta;
		phi+=d.rate*PI;
		while(phi>2*PI) phi-=2*PI; //@shift_addition_cc: normalize phase
		if(i%SACCTEST_STEP==0)
		{
			avg_counter=avg_size;
			avg=0;
		}
		if(avg_counter)
		{
			avg+=fabs(cosphi-cos(phi));
			if(!--avg_counter) printf("%g ", avg/avg_size);
		}
	}
	printf("]; error_vector_db=20*log10(error_vector); plot(error_vector_db);\n");
}

shift_addition_data_t decimating_shift_addition_init(float rate, int decimation)
{
	return shift_addition_init(rate*decimation);
}

decimating_shift_addition_status_t decimating_shift_addition_cc(complexf *input, complexf* output, int input_size, shift_addition_data_t d, int decimation, decimating_shift_addition_status_t s)
{
	//The original idea was taken from wdsp:
	//http://svn.tapr.org/repos_sdr_hpsdr/trunk/W5WC/PowerSDR_HPSDR_mRX_PS/Source/wdsp/shift.c
	//However, this method introduces noise (from floating point rounding errors), which increases until the end of the buffer.
	//fprintf(stderr, "cosd=%g sind=%g\n", d.cosdelta, d.sindelta);
	float cosphi=cos(s.starting_phase);
	float sinphi=sin(s.starting_phase);
	float cosphi_last, sinphi_last;
	int i;
	int k=0;
	for(i=s.decimation_remain;i<input_size;i+=decimation) //@shift_addition_cc: work
	{
		iof(output,k)=cosphi*iof(input,i)-sinphi*qof(input,i);
		qof(output,k)=sinphi*iof(input,i)+cosphi*qof(input,i);
		k++;
		//using the trigonometric addition formulas
		//cos(phi+delta)=cos(phi)cos(delta)-sin(phi)*sin(delta)
		cosphi_last=cosphi;
		sinphi_last=sinphi;
		cosphi=cosphi_last*d.cosdelta-sinphi_last*d.sindelta;
		sinphi=sinphi_last*d.cosdelta+cosphi_last*d.sindelta;
	}
	s.decimation_remain=i-input_size;
	s.starting_phase+=d.rate*PI*k;
	s.output_size=k;
	while(s.starting_phase>PI) s.starting_phase-=2*PI; //@shift_addition_cc: normalize starting_phase
	while(s.starting_phase<-PI) s.starting_phase+=2*PI;
	return s;
}


agc_state* agc_ff(float* input, float* output, int input_size, agc_params* params, agc_state* state)
{
	/*
		Notes on parameters (with some default values):
			attack_rate = 0.01
			decay_rate = 0.001
			hang_time = (hang_time_ms / 1000) * sample_rate
				hang_time is given in samples, and should be about 4ms.
				hang_time can be switched off by setting it to zero (not recommended).

			max_gain = pow(2, adc_bits)
				max_gain should be no more than the dynamic range of your A/D converter.
			gain_filter_alpha = 1 / ((fs/(2*PI*fc))+1)

			>>> 1 / ((48000./(2*3.141592654*100))+1)
			0.012920836043344543
			>>> 1 / ((48000./(2*3.141592654*10))+1)
			0.0013072857061786625


		Literature:
			ww.qsl.net/va3iul/Files/Automatic_Gain_Control.pdf
			page 7 of http://www.arrl.org/files/file/Technology/tis/info/pdf/021112qex027.pdf

		Examples:
			http://svn.tapr.org/repos_sdr_hpsdr/trunk/W5WC/PowerSDR_HPSDR_mRX_PS/Source/wdsp/wcpAGC.c
			GNU Radio's agc,agc2,agc3 have quite good ideas about this.
	*/
	float gain = state->last_gain;
	float last_peak = params->reference / state->last_gain; //approx.
	float input_abs;
	float error, dgain;

	float xk, vk, rk;
	float dt = 0.5;
	float beta = 0.005;

	for (int i = 0; i < input_size; i++) {
        //We skip samples containing 0, as the gain would be infinity for those to keep up with the reference.
		if (input[i] != 0) {
            //The error is the difference between the required gain at the actual sample, and the previous gain value.
            //We actually use an envelope detector.
            input_abs = fabs(input[i]);
            error = (input_abs * gain) / params->reference;

			//An AGC is something nonlinear that's easier to implement in software:
			//if the amplitude decreases, we increase the gain by minimizing the gain error by attack_rate.
			//We also have a decay_rate that comes into consideration when the amplitude increases.
			//The higher these rates are, the faster is the response of the AGC to amplitude changes.
			//However, attack_rate should be higher than the decay_rate as we want to avoid clipping signals.
			//that had a sudden increase in their amplitude.
			//It's also important to note that this algorithm has an exponential gain ramp.

			if (error > 1) {
    			//INCREASE IN SIGNAL LEVEL
				if (last_peak < input_abs) {
					state->attack_wait_counter = params->attack_wait_time;
					last_peak = input_abs;
				}

				if (state->attack_wait_counter > 0) {
					state->attack_wait_counter--;
					dgain = 1;
				} else {
					//If the signal level increases, we decrease the gain quite fast.
					dgain = 1 - params->attack_rate;
					//Before starting to increase the gain next time, we will be waiting until hang_time for sure.
					state->hang_counter = params->hang_time;
				}
			} else {
			    //DECREASE IN SIGNAL LEVEL
				if (state->hang_counter > 0) {
					//Before starting to increase the gain, we will be waiting until hang_time.
					state->hang_counter--;
					dgain = 1; //..until then, AGC is inactive and gain doesn't change.
				} else {
				    dgain = 1 + params->decay_rate; //If the signal level decreases, we increase the gain quite slowly.
				}
			}
			gain *= dgain;
		}

        // alpha beta filter
		xk = state->xk + (state->vk * dt);
		vk = state->vk;

		rk = gain - xk;

		xk += params->gain_filter_alpha * rk;
		vk += (beta * rk) / dt;

		state->xk = xk;
		state->vk = vk;

		gain = state->xk;

        // clamp gain to max_gain and 0
		if (gain > params->max_gain) gain = params->max_gain;
		if (gain < 0) gain = 0;

        // actual sample scaling
		output[i] = gain * input[i];
		// limiting
		if (output[i] > 1.0) {
		    output[i] = 1.0;
		} else if (output[i] < -1.0) {
		    output[i] = -1.0;
		}
	}

    state->last_gain=gain;
	return state;
}

agc_state* agc_s16(short* input, short* output, int input_size, agc_params* params, agc_state* state)
{
	short reference = params->reference * 32767;
	float gain = state->last_gain;
	float last_peak = reference / state->last_gain; //approx.
	short input_abs;
	float error, dgain;

	float xk, vk, rk;
	float dt = 0.5;
	float beta = 0.005;

	for (int i = 0; i < input_size; i++) {
    //We skip samples containing 0, as the gain would be infinity for those to keep up with the reference.
		if (input[i] != 0) {
            //The error is the difference between the required gain at the actual sample, and the previous gain value.
            //We actually use an envelope detector.
            input_abs = abs(input[i]);
            error = (input_abs * gain) / reference;

			//An AGC is something nonlinear that's easier to implement in software:
			//if the amplitude decreases, we increase the gain by minimizing the gain error by attack_rate.
			//We also have a decay_rate that comes into consideration when the amplitude increases.
			//The higher these rates are, the faster is the response of the AGC to amplitude changes.
			//However, attack_rate should be higher than the decay_rate as we want to avoid clipping signals.
			//that had a sudden increase in their amplitude.
			//It's also important to note that this algorithm has an exponential gain ramp.

			if (error > 1) {
    			//INCREASE IN SIGNAL LEVEL
				if (last_peak < input_abs) {
					state->attack_wait_counter = params->attack_wait_time;
					last_peak = input_abs;
				}

				if (state->attack_wait_counter > 0) {
					state->attack_wait_counter--;
					dgain = 1;
				} else {
					//If the signal level increases, we decrease the gain quite fast.
					dgain = 1 - params->attack_rate;
					//Before starting to increase the gain next time, we will be waiting until hang_time for sure.
					state->hang_counter = params->hang_time;
				}
			} else {
			    //DECREASE IN SIGNAL LEVEL
				if (state->hang_counter > 0) {
					//Before starting to increase the gain, we will be waiting until hang_time.
					state->hang_counter--;
					dgain = 1; //..until then, AGC is inactive and gain doesn't change.
				} else {
				    dgain = 1 + params->decay_rate; //If the signal level decreases, we increase the gain quite slowly.
				}
			}
			gain *= dgain;
		}

        // alpha beta filter
		xk = state->xk + (state->vk * dt);
		vk = state->vk;

		rk = gain - xk;

		xk += params->gain_filter_alpha * rk;
		vk += (beta * rk) / dt;

		state->xk = xk;
		state->vk = vk;

		gain = state->xk;

        // clamp gain to max_gain and 0
		if (gain > params->max_gain) gain = params->max_gain;
		if (gain < 0) gain = 0;

        // actual sample scaling
        // limiting
        if (gain * input[i] > SHRT_MAX) {
            output[i] = SHRT_MAX;
        } else if (gain * input[i] < SHRT_MIN) {
            output[i] = SHRT_MIN;
        } else {
    		output[i] = gain * input[i];
        }
	}

    state->last_gain=gain;
	return state;
}

#endif
