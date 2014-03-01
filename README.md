fabric
======

My fabfile Library. This uses fabric an open source project you can read about here: fabfile.org.

Instalation
======

To use this you must install fabric. Please read: http://docs.fabfile.org/en/1.8/installation.html for in depth install instructions. If you are on ubuntu(lucid or later)/debian (jessie or later) you can install it via terminal command: "apt-get install fabric". 

After Installing the package you can can: git clone git@github.com:majormoses/fabric.git or download a zip via: https://github.com/majormoses/fabric/archive/master.zip

Usage
======
When running interactively and in directory you cloned/downloaded to you can run fab -l (el not 1). If you are not in the same directory you will need to specify the location of the fabfile via faf -f PATH/TO/FABFILE.py -l (el not 1).

This should output should contain the list of functions you can run via fabric and will look simialr to:

Available commands:

    addLocalAdmin
    all_internal_servers
    auth_host
    backUpAllVMs
    backUpVM
    configEth0
    createBackUpDirs
    delLocalAdmin
    getListOfVMs
    ldapClientConfig
    nameMyServer
    pingHost
    rotateBackUps
    syncOpsKeys
    syncRootKeys
    syncUserKeys
    xen_servers


To run a function with options try something like: 
fab -H HOSTNAME/IP/HOST-DEFINED(defined in fabfile)  function:option='WHAT/YOUR/VARIABLE/SHOULD/EQUAL'

In order to get a better description you can run fab -d FUNCTION/NAME

This will show something like this:
fab -d pingHost
Displaying detailed information for task 'pingHost':

    This will ping a host
    Arguments: ip

