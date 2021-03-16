#!/usr/bin/env perl

### ModulusHarvestor.pl

### Author:    Avi Kak (kak@purdue.edu)
### Date:      April 22, 2014
### Modified:  February 23, 2016

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

use IO::Socket;                                                                  #(A1)
use Math::BigInt;                                                                #(A2)
use strict;                
use warnings;              

our $debug = 1;                                                                  #(A3)

our $mark1 = "-----BEGIN CERTIFICATE-----";                                      #(A4)
our $mark2 = "-----END CERTIFICATE-----";                                        #(A5)
our $dumpfile = "Dumpfile.txt";                                                  #(A6)
open DUMP, ">> $dumpfile";                                                       #(A7)
our @ip_addresses_to_scan;                                                       #(A8)

unless (@ARGV) {                                                                 #(B1)
    our $NHOSTS = 200;                                                           #(B2)
    @ip_addresses_to_scan = @{get_fresh_ipaddresses($NHOSTS)};                   #(B3)
} elsif (@ARGV == 1) {                                                           #(B4)
    @ip_addresses_to_scan = ($ARGV[0]);                                          #(B5)
} else {                                                                         #(B6)
    die "You cannot call $0 with more than one command-line argument\n";         #(B7)
}

foreach my $ip_address (@ip_addresses_to_scan) {                                 #(C1)
    print "\nTrying IP address: $ip_address\n\n\n";                              #(C2)
    my $sock = IO::Socket::INET->new(PeerAddr => $ip_address,                    #(C3)
                                     PeerPort => 443,                            #(C4)
                                     Timeout  => "0.1",                          #(C5)
                                     Proto => 'tcp');                            #(C6)
    if ($sock) {                                                                 #(C7)
        print DUMP "$ip_address\n\n";                                            #(C8)
        # The --print-cert option outputs the certificate in PEM format.
        # The --insecure option says not to insist on validating the certificate
        my $output = `gnutls-cli --insecure --print-cert $ip_address < /dev/null`;
                                                                                 #(C9)
        my @certificates = $output =~ /$mark1(.+?)$mark2/gs;                     #(C10)
        my $howmany_certs = @certificates;                                       #(C11)
        print "Found $howmany_certs certificates\n\n" if $debug;                 #(C12)
        foreach my $i (1..@certificates) {                                       #(C13)
            print "Certificate $i:\n\n" if $debug;                               #(C14)
            print "$certificates[$i-1]\n\n" if $debug;                           #(C15)
            open FILE, ">__temp.cert";                                           #(C16)
            print FILE "$mark1$certificates[$i-1]$mark2\n";                      #(C17)
            my $cert_text = `openssl x509 -text < __temp.cert`;                  #(C18)
            print "$cert_text\n\n\n" if $debug;                                  #(C19)
            my @all_lines = split /\s+/, $cert_text;                             #(C20)
            $cert_text = join '', grep $_, @all_lines;                           #(C21)
            my @params = $cert_text =~ /Modulus:(.+?)Exponent:(\d+)/gs;          #(C22)
            my $modulus ="0x" . join '', split /:/, $params[0];                  #(C23)
            if ($debug) {                                                        #(C24)
                print "Modulus: \n";                                             #(C25)
                print Math::BigInt->new($modulus)->as_int();                     #(C26)
                print "\n\n";                                                    #(C27)
                print "Public exponent: $params[1]\n";                           #(C28)
                print "\n\n\n";
            }
            print DUMP "Modulus:\n";                                             #(C29)
            print DUMP Math::BigInt->new($modulus)->as_int();                    #(C30)
            print DUMP "\n\nPublic Exponent: $params[1]\n\n\n";                  #(C31)
            unlink "__temp.cert";                                                #(C32)
        }                   
        print DUMP "\n\n\n";                                                     #(C33)
    }
}

## This subroutine was borrowed from the AbraWorm.pl code in Lecture 22.
sub get_fresh_ipaddresses {                                                      #(D1)
    my $howmany = shift || 0;                                                    #(D2)
    return 0 unless $howmany;                                                    #(D3)
    my @ipaddresses;                                                             #(D4)
    foreach my $i (0..$howmany-1) {                                              #(D5)
        my ($first,$second,$third,$fourth) =                               
                               map {1 + int(rand($_))} (223,223,223,223);        #(D6)
        push @ipaddresses, "$first\.$second\.$third\.$fourth";                   #(D7)
    }
    return \@ipaddresses;                                                        #(D8)
}
