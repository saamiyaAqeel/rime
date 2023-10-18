# Running under Windows

At the moment, to work on RIME under Windows, you'll probably want to use the Windows Subsystem for Linux (WSL). 
This gives you a Linux environment within your Windows world, which is closer to the environment RIME was developed in.

If you don't already have WSL installed, you can follow the instructions here:
https://learn.microsoft.com/en-us/windows/wsl/install

This will give you an Ubuntu Linux environment, and you can get a terminal by searching for "Ubuntu" in the Windows command prompt.

Within the Linux world, you'll need to install various tools to get started, so you'll want to run something like the following:

    sudo apt update
    sudo apt install python3 python3-pip python3-dev git-lfs curl 

You'll also need a recent version of node.js, and there are instructions here:
https://learn.microsoft.com/en-us/windows/dev-environment/javascript/nodejs-on-wsl

Essentially, it involves getting the node version manage `nvm` and then using that to install the latest version of node. e.g.

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | bash
nvm install 18

If you want to get to your normal Windows home directory, you can find it under `/mnt/c/Users/<your username>`.

Within that directory, you can clone the RIME repository:

    git clone https://github.com/horizon-institute/rime

And within that 'rime' directory you can probably then use the 'run_dev.sh' script as described in the main README.md file.

