#pragma once

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "module.hpp"

struct Squelch: Module {
    Writer* powerWriter;
    unsigned int reportInterval;
    int reportCounter;
};

extern PyType_Spec SquelchSpec;