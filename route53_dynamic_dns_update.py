#
# Chris Keller <chris@umbrellalabs.net>
# 
# Route 53 dynamic DNS updater will attempt to find a systems public IP by polling a URL that outputs REMOTE_ADDR only. 
# Once discovered, the public IP is validated for syntax and the applicable DNS entry is updated w/ boto.
#
# URL that outputs REMOTE_ADDR consists of the following PHP code:
# <?php echo $_SERvER['REMOTE_ADDR']; ?>

import sys
import pycurl
import boto

from boto.route53.record import ResourceRecordSets
from IPy import IP

# Validate address by instantiating IP and making sure we are working w/ IPv4
def is_valid_ip(address):
    try:
        ip = IP(address)
    except:
        return False
        
    if ip._ipversion == 4:
        return True
    
    return False

# This URL should point to a service that will return nothing more than REMOTE_ADDR
reflector_url = "https://wtfismyip.com/text"

# Update the A record you want to change and the hosted zone it is under
route53_dns = "home-server.mylabs.net."
route53_hosted_zone = "mylabs.net."

# Retrieve IP address from reflector_url using cURL
from StringIO import StringIO

curl_buffer = StringIO()
c = pycurl.Curl()

c.setopt(c.URL, reflector_url)
c.setopt(c.WRITEFUNCTION, curl_buffer.write)
c.perform()
c.close()

reflector_ip = curl_buffer.getvalue().strip()

if not is_valid_ip(reflector_ip):
    print "Data returned from reflector is not valid!"
    print "Data: \"" + reflector_ip + "\""
    
    sys.exit()

# Credentials are stored in ~/.boto
route53 = boto.connect_route53()    
zone = route53.get_zone(route53_hosted_zone)
change_set = ResourceRecordSets(route53, zone.id)

change = change_set.add_change("UPSERT", route53_dns, type="A", ttl=300)
change.add_value(reflector_ip)

try:
    change_set.commit()
except Exception as e:
    print e
    sys.exit()
    
print "Updating DNS entry %s with value %s worked!" % (route53_dns, reflector_ip)
