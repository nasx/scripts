# Chris Keller <chris@umbrellalabs.net>
# Enumerate IP addresses from a Linux system by manipulating output from ip command
#

from re import sub
from subprocess import check_output

# Leverage for debugging, not currently used
from subprocess import CalledProcessError

import sys

def enumerate_ip_addresses():
    list_of_ips = []
    
    # Run the command `ip -4 -o addr` and convert the output to a list of lines
    try:
        lines = check_output(["ip", "-4", "-o", "addr"]).splitlines()
    except CalledProcessError as e:
        return []
    
    # Grab 4th element from each line, remove subnet mask and append to list
    for line in lines:
        list_of_ips.append(sub("\/.*$", "", line.split()[3].strip()))    
    
    return list_of_ips

# Example usage
host_ips = enumerate_ip_addresses()

sys.stdout.write("Found ")

for ip in host_ips:
    sys.stdout.write("%s, " % ip)
    
sys.stdout.write("total of %d found!" % len(host_ips))
