#ifdef USE_FFTW

#include "fft_fftw.h"
#include <stdlib.h>

fft_plan_t* make_fft_c2c(int size, complexf* input, complexf* output, int forward, int benchmark)
{
	fft_plan_t* plan=(fft_plan_t*)malloc(sizeof(fft_plan_t));
	plan->plan = fftwf_plan_dft_1d(size, (fftwf_complex*)input, (fftwf_complex*)output, (forward)?FFTW_FORWARD:FFTW_BACKWARD, (benchmark)?CSDR_FFTW_MEASURE:FFTW_ESTIMATE);
	plan->size=size;
	plan->input=(void*)input;
	plan->output=(void*)output;
	return plan;
}

fft_plan_t* make_fft_r2c(int size, float* input, complexf* output, int benchmark) //always forward DFT
{
	fft_plan_t* plan=(fft_plan_t*)malloc(sizeof(fft_plan_t));
	plan->plan = fftwf_plan_dft_r2c_1d(size, input, (fftwf_complex*)output, (benchmark)?CSDR_FFTW_MEASURE:FFTW_ESTIMATE);
	plan->size=size;
	plan->input=(void*)input;
	plan->output=(void*)output;
	return plan;
}

fft_plan_t* make_fft_c2r(int size, complexf* input, float* output, int benchmark) //always backward DFT
{
	fft_plan_t* plan=(fft_plan_t*)malloc(sizeof(fft_plan_t));
	plan->plan = fftwf_plan_dft_c2r_1d(size, (fftwf_complex*)input, output, (benchmark)?CSDR_FFTW_MEASURE:FFTW_ESTIMATE);
	plan->size=size;
	plan->input=(void*)input;
	plan->output=(void*)output;
	return plan;
}

void fft_execute(fft_plan_t* plan)
{
	fftwf_execute(plan->plan);
}

void fft_destroy(fft_plan_t* plan)
{
	fftwf_destroy_plan(plan->plan);
	free(plan);
}

#endif
