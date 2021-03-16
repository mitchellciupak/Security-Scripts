#!/usr/bin/env perl

##  ECC.pl
##  Author: Avi Kak
##  February 28, 2016

use strict;                
use warnings;              
use Math::BigInt;

require "FactorizeWithBigInt.pl";         # From Lecture 12, Section 12.9
require "PrimeGenerator.pl";              # From Lecture 12, Section 12.13                                   

###############################  class ECC  ######################################
package ECC;

sub new {                                                                    #(A1)
    my ($class, %args) = @_;                                                 #(A2)
    bless {                                                                  #(A3)
        mod  =>  $args{mod},                                                 #(A4)
        a    =>  $args{a},                                                   #(A5)
        b    =>  $args{b},                                                   #(A6)
    }, $class;                                                               #(A7)
}

# class method:
sub choose_curve_params {                                                    #(B1)
    my ($mod, $num_of_bits) = @_;                                            #(B2)
    my ($param1,$param2) = (undef, undef);                                   #(B3)
    while (1) {                                                              #(B4)
        my @arr = map {my $x = rand(1); $x > 0.5 ? 1 : 0 } 0 .. $num_of_bits-1;
                                                                             #(B5)
        my $bstr = join '', split /\s/, "@arr";                              #(B6)
        $param1 = oct("0b".$bstr);                                           #(B7)
        $param1 = Math::BigInt->new("$param1");                              #(B8)
        @arr = map {my $x = rand(1); $x > 0.5 ? 1 : 0 } 0 .. $num_of_bits-1; #(B9)
        $bstr = join '', split /\s/, "@arr";                                 #(B10)
        $param2 = oct("0b".$bstr);                                           #(B11)
        $param2 = Math::BigInt->new("$param2");                              #(B12)
        last unless $param1->copy()->bpow(Math::BigInt->new("3"))
         ->bmul(Math::BigInt->new("4"))->badd($param2->copy()
          ->bmul($param2)->bmul(Math::BigInt->new("27")))
            ->bmod($mod)->bzero();                                           #(B13)
    }
    return ($param1, $param2);                                               #(B14)
}

sub mycmp3 {                                                                 #(C1)
    my $self = shift;                                                        #(C2)
    my ($p1, $p2) = ($a, $b);                                                #(C3)
    if ($p1->[0]->bcmp($p2->[0]) == 0) {                                     #(C4)
        if ($p1->[1]->bcmp($p2->[1]) > 0) {                                  #(C5)
            return 1;                                                        #(C6)
        } elsif ( $p1->[1]->bcmp($p2->[1]) < 0) {                            #(C7)
            return -1;                                                       #(C8)
        } else {                                                             #(C9)
            return 0;                                                        #(C10)
        }                                     
    } elsif ($p1->[0]->bcmp($p2->[0]) > 0) {                                 #(C11)
        return 1;                                                            #(C12)
    } else {                                                                 #(C13)
        return -1;                                                           #(C14)
    }
}

sub display {                                                                #(D1)
    my $self = shift;                                                        #(D2)
    my @all_points = @{$_[0]};                                               #(D3)
    my @numeric_points = grep {$_ !~ /point_at_infinity/} @all_points;       #(D4)
    my @sorted  = sort   mycmp3   @numeric_points;                           #(D5)
    push @sorted, "point_at_infinity";                                       #(D6)
    my @output = map { $_ !~ /point_at_infinity/ ? 
                   "($_->[0],$_->[1])" : "point_at_infinity" } @sorted;      #(D7)
    print "@output\n";                                                       #(D8)
}

##  This function returns the multiplicative inverse (MI) of $num modulo $mod
sub MI {                                                                     #(E1)
    my $self = shift;                                                        #(E2)
    my ($num, $mod) = @_;                                                    #(E3)
    my ($NUM, $MOD) = ($num, $mod);                                          #(E4)
    my ($x, $x_old) = (Math::BigInt->bzero(), Math::BigInt->bone());         #(E5)
    my ($y, $y_old) = (Math::BigInt->bone(), Math::BigInt->bzero());         #(E6)
    while ($mod->is_pos()) {                                                 #(E7)
        my $q = $num->copy()->bdiv($mod);                                    #(E8)
        ($num, $mod) = ($mod, $num->copy()->bmod($mod));                     #(E9)
        ($x, $x_old) = ($x_old->bsub( $q->bmul($x) ), $x);                   #(E10)
        ($y, $y_old) = ($y_old->bsub( $q->bmul($y)), $y);                    #(E11)
    }                            
    if ( ! $num->is_one() ) {                                                #(E12)
        return undef;                                                        #(E13)
    } else {                                                                 #(E14)
        my $MI = $x_old->badd( $MOD )->bmod( $MOD );                         #(E15)
        return $MI;                                                          #(E16)
    }
}

##  The args for the parameters point1 and point2 may also be the string
##  "point at infinity" when one or both of these points is meant to be the
##  identity element of the group E_p(a,b).
sub add {                                                                    #(F1)
    my $self = shift;                                                        #(F2)
    my ($point1, $point2) = @_;                                              #(F3)
    my ($alpha_numerator, $alpha_denominator);                               #(F4)
    if (($point1 =~ /point_at_infinity/) 
                          && ($point2 =~ /point_at_infinity/)) {             #(F5)
        return "point_at_infinity";                                          #(F6)
    } elsif ($point1 =~ /point_at_infinity/) {                               #(F7)
        return $point2;                                                      #(F8)
    } elsif ($point2 =~ /point_at_infinity/) {                               #(F9)
        return $point1;                                                      #(F10)
    } elsif (($point1->[0]->bcmp( $point2->[0] ) == 0) 
                    && ($point1->[1]->bcmp( $point2->[1] ) == 0 )) {         #(F11)
        $alpha_numerator = $point1->[0]->copy()->bmul($point1->[0])
                    ->bmul(Math::BigInt->new("3"))->badd($self->{a});        #(F12)
        $alpha_denominator =  $point1->[1]->copy()->badd($point1->[1]);      #(F13)        
    } elsif ($point1->[0]->bcmp( $point2->[0] ) == 0 ) {                     #(F14)
        return "point_at_infinity";                                          #(F15)
    } else {
        $alpha_numerator = $point2->[1]->copy()->bsub( $point1->[1] );       #(F16)
        $alpha_denominator = $point2->[0]->copy()->bsub( $point1->[0] );     #(F17)
    }
    my $alpha_denominator_MI = 
                  $self->MI( $alpha_denominator->copy(), $self->{mod} );     #(F18)
    my $alpha = 
      $alpha_numerator->bmul( $alpha_denominator_MI )->bmod( $self->{mod} ); #(F19)
    my @result = (undef, undef);                                             #(F20)
    $result[0] = $alpha->copy()->bmul($alpha)
        ->bsub( $point1->[0] )->bsub( $point2->[0] )->bmod( $self->{mod} );  #(F21)
    $result[1] = $alpha->copy()
            ->bmul( $point1->[0]->copy()->bsub($result[0]) )
                   ->bsub( $point1->[1] )->bmod( $self->{mod} );             #(F22)
    return \@result;                                                         #(F22)
}

##  Returns a point (x,y) on a given elliptic curve.
sub get_point_on_curve {                                                     #(G1)
    my $self = shift;                                                        #(G2)
    my $randgen = Math::BigInt::Random::OO->new( max => $self->{mod} - 1 );  #(G3)
    my $x = Math::BigInt->new();                                             #(G4)
    unless ($x->is_pos()) {                                                  #(G5)
        $x =  $randgen->generate(1);                                         #(G6)
    }
    my $y;                                                                   #(G7)
    my $trial = Math::BigInt->bzero();                                       #(G8)
    while (1) {                                                              #(G9)
        last if $trial->binc()->bcmp( 
                      $self->{mod}->copy()->badd($self->{mod}) ) >= 0;       #(G10)
        my $rhs = $x->copy()->bpow(Math::BigInt->new("3"))
                     ->badd($x->copy()->bmul($self->{a}->copy()))
                           ->badd($self->{b}->copy())->bmod( $self->{mod} ); #(G11)
        if ($rhs->is_one()) {                                                #(G12)
            $y = Math::BigInt->bone();                                       #(G13)
            last;                                                            #(G14)
        }
        my @factors = @{FactorizeWithBigInt->new($rhs)->factorize()};        #(G15)
        if ((@factors == 2) && ($factors[0] == $factors[1])) {               #(G16)
            $y = $factors[0];                                                #(G17)
            last;                                                            #(G18)
        }
        $x = Math::BigInt->new();                                            #(G19)
        unless ($x->is_pos()) {                                              #(G20)
            $x =  $randgen->generate(1);                                     #(G21)
        }
    }
    if (! defined $y) {                                                      #(G22)
        die "Point on curve not found.  Try again --- if you have time";     #(G23)
    } else {                                                                 #(G24)
        my @point = ($x, $y);                                                #(G25)
        return \@point;                                                      #(G26)
    }
}

##  This method returns a k-fold application of the group law to the same
##  point.  That is, if `point + point + .... + point = result_point',
##  where we have k occurrences of `point' on the left, then this method
##  returns result of such `summation'.  For notational convenience, we may
##  refer to such a sum as `k times the point'.
##  Parameters:
sub k_times_point {                                                          #(H1)
    my $self = shift;                                                        #(H2)
    my ($point, $k) = @_;                                                    #(H3)
    die "k_times_point called with illegal value for k" unless $k > 0;       #(H4)
    if ($point =~ /point_at_infinity/) {                                     #(H5)
        return "point_at_infinity";                                          #(H6)
    } elsif ($k == 1) {                                                      #(H7)
        return $point;                                                       #(H8)
    } elsif ($k == 2) {                                                      #(H9)
        return $self->add($point, $point);                                   #(H10)
    } elsif ($k %2 == 1) {                                                   #(H11)
        return $self->add($point, $self->k_times_point($point, $k-1));       #(H12)        
    } else {                                                                 #(H13)
        return $self->k_times_point($self->add($point, $point), int($k/2));  #(H14)
    }
}

1;

################################  main    ########################################
package main;

#Example 1:
my $p = 23;                                                                  #(M1)
$p = Math::BigInt->new("$p");                                                #(M2)
my ($a, $b) = (1,4);          # y^2 = x^3 + x + 4                            #(M3)
$a = Math::BigInt->new("$a");                                                #(M4)
$b = Math::BigInt->new("$b");                                                #(M5)
my $ecc = ECC->new( mod => $p, a => $a, b => $b );                           #(M6)
my $point = $ecc->get_point_on_curve();                                      #(M7)
print "Point: @{$point}\n";        # Point: (7,3)                            #(M8)
my @all_points = map {my $k = $_; $ecc->k_times_point($point, $k)} 1 .. 31;  #(M9)
$ecc->display(\@all_points);                                                 #(M10)
# (0,2) (0,21) (1,11) (1,12) (4,7) (4,16) (7,3) (7,3) (7,20) (8,8) (8,15) (9,11) 
# (9,12) (10,5) (10,18) (11,9) (11,14) (13,11) (13,12) (14,5) (14,18) (15,6) (15,17) 
# (17,9) (17,14) (18,9) (18,14) (22,5) (22,18) (22,18) point_at_infinity

# Example 2:
my $generator = PrimeGenerator->new(bits => 16);                             #(M11)
$p = $generator->findPrime();           # 64951                              #(M12)
$p = Math::BigInt->new("$p");                                                #(M13)
print "Prime returned: $p\n";           # Prime returned: 56401              #(M14)
($a,$b) = ECC::choose_curve_params($p, 16);                                  #(M15)
print "Parameters a and b for the curve: $a, $b\n";                          #(M16)
                          # Parameters a and b for the curve: 52469, 51053
$ecc = ECC->new( mod => $p, a => $a, b => $b );                              #(M17)
$point = $ecc->get_point_on_curve();                                         #(M18)
print "Point: @{$point}\n";             # Point: 36700 97                    #(M19)

# Example 3:
##  Parameters of the DRM2 elliptic curve:
$p = Math::BigInt->new("785963102379428822376694789446897396207498568951");  #(M20)
$a = Math::BigInt->new("317689081251325503476317476413827693272746955927");  #(M21)
$b = Math::BigInt->new("79052896607878758718120572025718535432100651934");   #(M22)
# A point on the curve:
my $Gx = 
     Math::BigInt->new("771507216262649826170648268565579889907769254176");  #(M23)
my $Gy = 
     Math::BigInt->new("390157510246556628525279459266514995562533196655");  #(M24)
$ecc = ECC->new( mod => $p, a => $a, b => $b );                              #(M25)
@all_points = map {my $k = $_; $ecc->k_times_point([$Gx,$Gy], $k)} 1 .. 5;   #(M26)
$ecc->display(\@all_points);                                                 #(M27)
#  (131207041319172782403866856907760305385848377513,
#                            2139936453045853218229235170381891784525607843)
#  (404132732284922951107528145083106738835171813225,
#                            165281153861339913077400732834828025736032818781)
#  (695225880076209899655288358039795903268427836810,
#                            87701351544010607198039768840869029919832813267)
#  (716210695201203540500406352786629938966496775642,
#                            251074363473168143346338802961433227920575579388)
#  (771507216262649826170648268565579889907769254176,
#                            390157510246556628525279459266514995562533196655)
