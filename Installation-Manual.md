# Manual of Installation

Load Balancing OpenWebRX is available for Linux.
To use this software you need to have at least 2 PCs or mini-PCs and a connection between them.
The minimum is the load balancer and an OpenWebRX server running in the first PC and an OpenWebRX server in the second.

--------------------

# Steps:

## 1.  Prerequisites: 

    Python version 3.7+

    Required packages:
    sudo apt-get update &&\
    sudo apt-get install git build-essential cmake libfftw3-dev python3 python3-setuptools rtl-sdr netcat libsndfile-dev librtlsdr-dev automake autoconf libtool pkg-config libsamplerate-dev libpython3-dev

    Also for load balancer:

    pip install requests

## 2.  Download the code
   
    git clone https://github.com/iliasz-ECE/lbowrx.git

    There are 2 parts in the code. The load balancer (lb) and the OpenWebRX server (owrx).

    Decide the role of each PC. Install the corresponding part, depending on the target function of the PC,
    or even both lb and owrx in the same PC.
    You may want to remove the extra part.

## 3.  Build the dependencies of the OpenWebRX server 

    (this step can be skipped for the load balancer)

    Code for csdr, pycsdr, js8py and owrx_connector is included and must be installed for the owrx server.
    These projects are also available at github.com/jketterl repositories.

### 3.1 Install csdr

    cd lbowrx/lbowrx-owrx/csdr
    mkdir build
    cd build
    cmake ..
    make
    sudo make install
    cd ../..
    sudo ldconfig


### 3.2 Install pycsdr
    
    cd pycsdr
    sudo python3 setup.py install install_headers
    cd ..

### 3.3 Install js8py

    cd js8py
    sudo python3 setup.py install
    cd ..

### 3.4 SoapySdr is also needed. 

    Version 0.8 is tested to work.
    
    sudo apt-get install libsoapysdr0.8 libsoapysdr-dev soapysdr-tools
    sudo apt-get install soapysdr-module-all

    Note: if you wish to come back and install SoapySDR at a later point, please make sure you also recompile the owrx_connector.

### 3.5 Install owrx_connector
    
    cd owrx_connector
    mkdir build
    cd build
    cmake ..
    make
    sudo make install
    cd ../..
    sudo ldconfig

Additional software for digital protocols, can be instaled at OpenWebRX server.
See https://github.com/jketterl/openwebrx/wiki/Manual-Package-installation-(including-digital-voice)


## 4.  Create data folders and assign permissions:

    Load Balancing OpenWebRX needs a directory to store dynamic data from the web configuration interface. The default path for this directory is /var/lib/lbowrx/{lb,owrx} but this can be changed in openwebrx.conf if necessary.

    Create the directory and set its permissions.
    Replace [openwebrx-user] with the your user name.
    Make sure to include the period (.) after the username as that will also change the group ownership of the file.
    
    Choose 4a or 4b or 4c, depending on PC role:

### 4a. for load balancer:

    sudo mkdir /var/lib/lbowrx
    sudo chown [openwebrx-user]. /var/lib/lbowrx
    sudo mkdir /var/lib/lbowrx/lb
    sudo chown [openwebrx-user]. /var/lib/lbowrx/lb 

### 4b. for OpenWebRX server:

    sudo mkdir /var/lib/lbowrx
    sudo chown [openwebrx-user]. /var/lib/lbowrx
    sudo mkdir /var/lib/lbowrx/owrx     
    sudo chown [openwebrx-user]. /var/lib/lbowrx/owrx

### 4c. for both load balancer and OpenWebRX server:

    sudo mkdir /var/lib/lbowrx
    sudo chown [openwebrx-user]. /var/lib/lbowrx
    sudo mkdir /var/lib/lbowrx/lb
    sudo chown [openwebrx-user]. /var/lib/lbowrx/lb 
    sudo mkdir /var/lib/lbowrx/owrx     
    sudo chown [openwebrx-user]. /var/lib/lbowrx/owrx

## 5.  Users file
    The following commands initialize an empty users file.
    
### 5a. for load balancer:

    sudo sh -c "echo [] > /var/lib/lbowrx/lb/users.json"
    sudo chown [openwebrx-user]. /var/lib/lbowrx/lb/users.json
    sudo chmod 0600 /var/lib/lbowrx/lb/users.json

### 5b. for OpenWebRX server:

    sudo sh -c "echo [] > /var/lib/lbowrx/owrx/users.json"
    sudo chown [openwebrx-user]. /var/lib/lbowrx/owrx/users.json
    sudo chmod 0600 /var/lib/lbowrx/owrx/users.json

### 5c. for both load balancer and OpenWebRX server:

    combine
    
## 6.  How to run:
 
### 6a. for load balancer:

    lbowrx/lbowrx-lb/loadbalancer.py
    
### 6b. for OpenWebRX server:
    
    lbowrx/lbowrx-owrx/lbowrx_owrx/openwebrx.py

## 7.  Create admin username and password for the web configuration interface. 

    Write your own username in the [].

### 7a. for load balancer:

    lbowrx/lbowrx-lb/loadbalancer.py admin adduser [username]
    
### 7b. for OpenWebRX server:
    
    lbowrx/lbowrx-owrx/lbowrx_owrx/openwebrx.py admin adduser [username]

## 8.  Install lbowrx as a systemd service (Optional)

    You can find the needed files in the systemd folder.
    You will need to write your data at the User, Group, ExecStart and Path, according to your environment. 

    After moving the file into /etc/systemd/system, run: sudo systemctl daemon-reload.
    Start the program with: 
    
    sudo systemctl start lbowrx-lb
    
    or

    sudo systemctl start lbowrx-owrx
    
## 9.  Configure settings at the load balancer and the OpenWebRX servers.

### 9.1 Add SDRs and their profiles (available frequency zones) at the OpenWebRX servers
    
    At the OpenWebRX server PC, run: lbowrx/lbowrx-owrx/lbowrx_owrx/openwebrx.py
    
    After that, type in your browser PC_IP:8073, where PC_IP is the IP address of the specific PC.
    Enter the username and password you created for the OpenWebRX server at step 7.
    Click SDR devices and profiles.
    Add your device(s) and the available profiles.
    
### 9.2 General profiles at the load balancer

    At the load balancer, run: lbowrx/lbowrx-lb/loadbalancer.py
    After that, type in your browser <PC_IP_address>:8080
    Enter the username and password you created for the load balancer at step 7.
    Click General profiles.
    Add all the frequency zones that were entered above, at the OpenWebRX servers.
    Keep in mind to enter smaller or equal bandwidth for profile matching to work.
    Load balancer will match the general profiles to specific profiles of OpenWebRX servers and will direct the user there.
    
### 9.3 Servers at the load balancer

    Continue config of load balancer.
    Go back and click Servers.
    Add your OpenWebRX servers data, for example their IP address.
    Load balancer will communicate with them.
    
### 9.4 General settings at the load balancer

    Go back and click General settings.
    You can add some info about your server and a photo if you want.
    

## You are Ready!

Connect your SDR devices and run again all the OpenWebRX servers.
