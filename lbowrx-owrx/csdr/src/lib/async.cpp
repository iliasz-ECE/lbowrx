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

#include "async.hpp"
#include "ringbuffer.hpp"

using namespace Csdr;

AsyncRunner::AsyncRunner(UntypedModule* module):
    module(module),
    thread([this] { loop(); })
{}

AsyncRunner::~AsyncRunner() {
    stop();
}

void AsyncRunner::stop() {
    {
        std::lock_guard<std::mutex> lock(stateMutex);
        if (run) {
            run = false;
            module->unblock();
        }
    }
    try {
        thread.join();
    } catch (std::system_error&) {
        // NOOP - thread is not joinable
    }
}

bool AsyncRunner::isRunning() const {
    return run;
}

void AsyncRunner::loop() {
    // can't use run as a loop condition due to the locking system
    while (true) {

        // the lock must be obtained before checking the condition, but it must be released before looping to be able to stop
        std::unique_lock<std::mutex> lock(stateMutex);

        if (!run) return;

        try {
            if (module->canProcess()) {
                // don't hold the lock during the actual processing since that may cause deadlocks
                // we should be safe during this period as far as state is concerned
                lock.unlock();
                module->process();
            } else {
                // lock will be released and re-locked during blocking operation by the wait() method
                module->wait(lock);
            }
        } catch (const BufferError&) {
            run = false;
            break;
        }
    }
}