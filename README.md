fabric
======

My fabfile Library. This uses fabric an open source project you can read about here: fabfile.org.

Instalation
======

To use this you must install fabric. Please read: http://docs.fabfile.org/en/1.8/installation.html for in depth install instructions. If you are on ubuntu(lucid or later)/debian (jessie or later) you can install it via apt command: "apt-get install fabric". 

After Installing the package you can can: git clone https://github.com/majormoses/fabric.git or download a zip via: https://github.com/majormoses/fabric/archive/master.zip

Usage
======
When running interactively and in directory you cloned/downloaded to you can run fab -l (el not 1). If you are not in the same directory you will need to specify the location of the fabfile via fab -f PATH/TO/FABFILE.py -l (el not 1).

This should output should contain the list of functions you can run via fabric and will look similar to:

fab -l
Available commands:

    addLocalAdmin         creates a new local admin,
    all_internal_servers  array of all internal servers
    backUpAllVMs          will backup VM's returned by getListofVMs()
    backUpVM              backs up a single VM with uuid=/UUID/OF/VM and xs_name=/NAME/OF/VM
    configEthX            reconfigs ethX(any interface number) from dynamic to static.
    config_host           This is a string with your management server
    createBackUpDirs      creates backup dirs on xen SR with the tag backup-sr
    delLocalAdmin         deletes the local_admin specified on command line
    getListOfVMs          gets a list of all VM's in a xen pool
    ldapClientConfig      installs/configures ldap clients based on template
    nameMyServer          rename the server based on user input,
    pingHost              pings a host let you know results
    rotateBackUps         rotates and deletes backups with retention policy:
    syncRootKeys          syncs all of roots ssh
    syncUserKeys          syncs the user supplied SSH keys from config_host
    xen_servers           list of all xen servers (ip/dns),

The output is multi line and truncated... to see more useful info try something like:

fab -d backUpVM
Displaying detailed information for task 'backUpVM':

    backs up a single VM with uuid=/UUID/OF/VM and xs_name=/NAME/OF/VM
    using the follwoing methodology:
    	1) checks and ejects dvd from vm if neccessary
    	2) takes snapshot of VM
    	3) removes any longering copies
    	4) backup vm from snapshot
    	5) fixes permissions
    	6) deletes snapshot we created...we are not slobs
    
    Arguments: uuid, xs_name



To run a function with options try something like: 
fab -H HOSTNAME/IP/HOST-DEFINED(defined in fabfile)  function:option='WHAT/YOUR/VARIABLE/SHOULD/EQUAL'

