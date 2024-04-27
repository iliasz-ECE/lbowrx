# Load Balancing OpenWebRX

Load Balancing OpenWebRX is a web-based app for SDR.
It is an expansion of the OpenWebRX program. (https://github.com/jketterl/openwebrx)
It adds a load balancer in front of a pool of OpenWebRX servers.
This way, it scales the number of supported clients and the potential number of connected SDR devices.
It also enhances the coexistence of multiple users and handles SDR device failures.

You need at least 2 PCs or mini-PCs to make use of this software. Two OpenWebRX servers and one of them acting as a load balancer as well. You can also have 3 PCs with a separate load balancer.
You can add as many servers as you want, depending on the desired number of supported clients and number of available sdr devices.
There is no limit.

There is a load balancer (lb) part of the code and the OpenWebRX server (owrx) part.
Use each one depending on the target function of the PC, or even use both in the same PC.
The software is available for Linux.
There is a detailed installation manual in the wiki page.

This is open source software, a GNU AGPL licence is included.
