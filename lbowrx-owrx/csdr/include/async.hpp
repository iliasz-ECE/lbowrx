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
#include <thread>
#include <mutex>

namespace Csdr {

    class AsyncRunner {
        public:
            explicit AsyncRunner(UntypedModule* module);
            ~AsyncRunner();
            void stop();
            bool isRunning() const;
        private:
            void loop();
            bool run = true;
            UntypedModule*  module;
            std::mutex stateMutex;
            // any members that will be used by the thread must come above the thread itself in the member list here
            // C++ initializes the member variables in this order, so this ensures that members are available as soon
            // as the thread starts working
            std::thread thread;
    };

}