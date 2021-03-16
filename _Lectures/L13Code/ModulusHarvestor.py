#!/usr/bin/env python

### ModulusHarvestor.py

### Author:    Avi Kak (kak@purdue.edu)
### Date:      February 24, 2016

##  The script can be used in following two different modes:
##
##    --- With no command-line args.  In this case, the script scans the internet
##        with randomly synthesized IP addresses and, when it finds a site with its
##        port 443 open, it grabs the certificate(s) offered by that site and
##        extracts the various certificate parameters (modulus, public exponent,
##        etc.) from the certificate(s).
##
##    --- With just one command-line arg, which must be an IPv4 address.  In this
##        case, the script will try to connect with that address on its port 443 and
##        download the certificate offered by it.  So as not to waste your time, it
##        is best if you use an IP address that does offer an HTTPS service.  You can
##        check that with a simple port scanner like 'port_scan.pl' we will cover in
##        Lecture 16.

##  The basic purpose of this script is to harvest RSA moduli used for public keys in
##  SSL/TLS certificates.  Recent research has demonstrated that if two different
##  moduli share a common factor, they can both be factored easily, thus compromising
##  the security of both.

##  For harvesting moduli, the script first randomly selects $NHOSTS number of hosts
##  from the space of all possible IP addresses and tries to download their X.509
##  certificates using a GnuTLS client.  It subsequently extracts the modulus and
##  public key used in the certificates using openssl commands.  These are finally
##  dumped into a file called Dumpfile.txt.

import sys
import socket
import subprocess
import random
import re
import os

debug = 1

mark1 = "-----BEGIN CERTIFICATE-----"                                            #(A)
mark2 = "-----END CERTIFICATE-----"                                              #(B)
dumpfile = "Dumpfile.txt"                                                        #(C)
DUMP = open( dumpfile, 'w')                                                      #(D)
ip_addresses_to_scan = []                                                        #(E)

## This subroutine was borrowed from the AbraWorm.py code in Lecture 22.
def get_fresh_ipaddresses(howmany):                                              #(F)
    if howmany == 0: return 0                                                    #(G)
    ipaddresses = []                                                             #(H)
    for i in range(howmany):
        first,second,third,fourth = list(map(lambda x: random.randint(1, x),
                                                        [223] * 4))              #(I)
        ipaddresses.append( "%s.%s.%s.%s" % (first,second,third,fourth) )        #(J)
    return ipaddresses                                                           #(K)


if __name__ == '__main__':      

    if len(sys.argv) == 1:                                                       #(L)
        NHOSTS = 200                                                             #(M)
        ip_addresses_to_scan = get_fresh_ipaddresses(NHOSTS)                     #(N)
    elif len(sys.argv) == 2:
        ip_addresses_to_scan.append(sys.argv[1])                                 #(O)
    else:
        sys.exit("You cannot call %s with more than one command-line argument"
                                                             % sys.argv[0])      #(P)
    for ip_address in ip_addresses_to_scan:                                      #(Q)
        print("\nTrying IP address: %s\n\n\n" % ip_address)                      #(R)
        try:                                                             
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM )            #(S)
            sock.settimeout(0.1)                                                 #(T)
            sock.connect((ip_address, 443))                                      #(U)
        except:                                                                  #(V)
            continue                                                             #(W)
        DUMP.write("%s\n\n" % ip_address)                                        #(X)
        proc = subprocess.Popen(['gnutls-cli --insecure --print-cert ' + \
             ip_address + ' < /dev/null'], stdout=subprocess.PIPE, shell=True)   #(Y)
        (output,err) = proc.communicate()                                        #(Z)
        regex = mark1 + r'(.+?)' + mark2                                         #(a)                                    
        certificates = re.findall( regex, output, re.DOTALL )                    #(b)
        howmany_certs = len(certificates)                                        #(c)
        if debug: print "Found %s certificates\n\n" % howmany_certs              #(d)
        for i in range(1, len(certificates)+1):                                  #(e)
            if debug:                                                           
                print "Certificate %s:\n\n" % i                                  #(f)
                print str(certificates[i-1]) + "\n\n"                            #(g)
            FILE = open("__temp.cert", 'w')                                      #(i)
            FILE.write(mark1 + str(certificates[i-1]) + mark2 + "\n")            #(j)
            FILE.close()                                                         #(k)
            proc2 = subprocess.Popen(['openssl x509 -text < __temp.cert'],
                                     stdout=subprocess.PIPE, shell=True)         #(l)
            (cert_text, err) = proc2.communicate()                               #(m)
            if debug: print cert_text + "\n\n\n"                                 #(n)
            all_lines = filter(None, re.split(r'\s+', cert_text)   )             #(o)
            cert_text = ''.join(all_lines)                                       #(p)
            params = re.findall(r'Modulus:(.+?)Exponent:(\d+)', cert_text,
                                                                    re.DOTALL)   #(q)
            modulus = "0x" + ''.join( re.split(r':', params[0][0] ) )            #(r)
            if debug:                                                      
                print "Modulus:"                                                 #(s)
                print int(modulus, 16)                                           #(t)
                print "\n"                                 
                print "Public exponent: %s\n" % params[0][1]                     #(u)
                print "\n\n\n";
            DUMP.write( "Modulus:\n" )                                           #(v)
            DUMP.write( modulus )                                                #(w)
            DUMP.write("\n\nPublic Exponent: %s\n\n\n" % params[0][1])           #(x)
            os.unlink( "__temp.cert")                                            #(y)
            DUMP.write("\n\n\n")    
