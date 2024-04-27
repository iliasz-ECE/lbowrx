/*
Copyright (c) 2020-2022 Jakob Ketterl <jakob.ketterl@gmx.de>

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

#ifndef FMV_H

#ifdef CSDR_FMV
#if defined(__has_attribute)
#if __has_attribute(target_clones)
#if defined(__x86_64)
#define CSDR_TARGET_CLONES __attribute__((target_clones("avx","sse4.2","sse3","sse2","default")))
#endif
#endif
#endif
#endif

#ifndef CSDR_TARGET_CLONES
#define CSDR_TARGET_CLONES
#endif

#endif