#!/usr/bin/env python

##  ECC.py
##  Author: Avi Kak
##  February 26, 2012
##  Modified: February 28, 2016

import random, sys, functools
from PrimeGenerator import *          # From Homework Problem 15 of Lecture 12
from Factorize import factorize       # From Section 12.6 of Lecture 12


def MI(num, mod):            # This method is from Section 5.7 of Lecture 5    #(A1)
    '''
    The function returns the multiplicative inverse (MI)
    of num modulo mod
    '''
    NUM = num; MOD = mod                                                       #(A2)
    x, x_old = 0, 1                                                            #(A3)
    y, y_old = 1, 0                                                            #(A4)
    while mod:                                                                 #(A5)
        q = num // mod                                                         #(A6)
        num, mod = mod, num % mod                                              #(A7)
        x, x_old = x_old - q * x, x                                            #(A8)
        y, y_old = y_old - q * y, y                                            #(A9)
    if num != 1:                                                               #(A10)
        return "NO MI. However, the GCD of %d and %d is %u" % (NUM, MOD, num)  #(A11)
    else:                                                                      #(A12)
        MI = (x_old + MOD) % MOD                                               #(A13)
        return MI                                                              #(A14)

def add(curve, point1, point2, mod):                                           #(B1)
    '''
    If `point1 + point2 = result_point', this method returns the
    result_point, where `+' means the group law for the set of points
    E_p(a,b) on the elliptic curve y^2 = x^3 + ax + b defined over the
    prime finite field Z_p for some prime p.
    Parameters:
          curve    =  (a,b)       represents the curve y^2 = x^3 + ax + b
          point1   =  (x1,y1)     the first point on the curve
          point2   =  (x2,y2)     the second point on the curve
          mod      =  a prime p for Z_p elliptic curve
    The args for the parameters point1 and point2 may also be the string
    "point at infinity" when one or both of these points is meant to be the
    identity element of the group E_p(a,b).
    '''
    if isinstance(point1, str) and isinstance(point2, str):                    #(B2)
        return "point at infinity"                                             #(B3)
    elif isinstance(point1, str):                                              #(B4)
        return point2                                                          #(B5)
    elif isinstance(point2, str):                                              #(B6)
        return point1                                                          #(B7)
    elif (point1[0] == point2[0]) and (point1[1] == point2[1]):                #(B8)
        alpha_numerator = 3 * point1[0]**2 + curve[0]                          #(B9)
        alpha_denominator =  2 * point1[1]                                    #(B10)
    elif point1[0] == point2[0]:                                              #(B11)
        return "point at infinity"                                            #(B12)
    else:                                                                     #(B13)
        alpha_numerator = point2[1] - point1[1]                               #(B14)
        alpha_denominator = point2[0] - point1[0]                             #(B15)
    alpha_denominator_MI = MI( alpha_denominator, mod )                       #(B16)
    alpha = (alpha_numerator * alpha_denominator_MI) % mod                    #(B17)
    result = [None] * 2                                                       #(B18)
    result[0] = (alpha**2 - point1[0] - point2[0]) % mod                      #(B19)
    result[1] = (alpha * (point1[0] - result[0]) - point1[1]) % mod           #(B20)
    return result                                                             #(B21)

def k_times_point(curve, point, k, mod):                                       #(C1)
    '''
    This method returns a k-fold application of the group law to the same
    point.  That is, if `point + point + .... + point = result_point',
    where we have k occurrences of `point' on the left, then this method
    returns result of such `summation'.  For notational convenience, we may
    refer to such a sum as `k times the point'.
    Parameters:
          curve    =  (a,b)       represents the curve y^2 = x^3 + ax + b
          point    =  (x,y)       a point on the curve
          k        =  positive integer
          mod      =  a prime p for Z_p elliptic curve
    '''
    if k <= 0: sys.exit("k_times_point called with illegal value for k")       #(C2)
    if isinstance(point, str): return "point at infinity"                      #(C3)
    elif k == 1: return point                                                  #(C4)
    elif k == 2: return add(curve, point, point, mod)                          #(C5)
    elif k % 2 == 1:                                                           #(C6)
        return add(curve, point, k_times_point(curve, point, k-1, mod), mod)   #(C7)
    else:                                                                      #(C8)
        return k_times_point(curve, add(curve, point, point, mod), k/2, mod)   #(C9)

def on_curve(curve, point, mod):                                               #(C10)
    '''
    Checks if a point is on an elliptic curve.
    Parameters:
          curve    =  (a,b)       represents the curve y^2 = x^3 + ax + b
          point    =  (x,y)       a candidate point 
          mod      =  a prime p for Z_p elliptic curve
    '''
    lhs = point[1]**2                                                          #(C11)
    rhs = point[0]**3 + curve[0]*point[0] + curve[1]                           #(C12)
    return lhs % mod == rhs % mod                                              #(C13)

def get_point_on_curve(curve, mod):                                            #(D1)
    '''
    WARNING: This is NOT an appropriate function to run for very large
             values of mod (as in the elliptic curves for production work.
             It would be much, much too slow.
    Returns a point (x,y) on a given elliptic curve.
    Parameters:
          curve    =  (a,b)       represents the curve y^2 = x^3 + ax + b
          mod      =  a prime p for Z_p elliptic curve
    '''
    ran = random.Random()                                                      #(D2)
    x = ran.randint(1, mod-1)                                                  #(D3)
    y = None                                                                   #(D4)
    trial = 0                                                                  #(D5)
    while 1:                                                                   #(D6)
        trial += 1                                                             #(D7)
        if trial >= (2*mod): break                                             #(D8)
        rhs = (x**3 + x*curve[0] + curve[1]) % mod                             #(D9)
        if rhs == 1:                                                           #(D10)
            y = 1                                                              #(D11)
            break                                                              #(D12)
        factors = factorize(rhs)                                               #(D13)
        if (len(factors) == 2) and (factors[0] == factors[1]):                 #(D14)
            y = factors[0]                                                     #(D15)
            break                                                              #(D16)
        x = ran.randint(1, mod-1)                                              #(D17)
    if not y:                                                                  #(D18)
        sys.exit("Point on curve not found.  Try again --- if you have time")  #(D19)
    else:                                                                      #(D20)
        return (x,y)                                                           #(D21)

def choose_curve_params(mod, num_of_bits):                                     #(E1)
    a,b = None,None                                                            #(E2)
    while 1:                                                                   #(E3)
        a = random.getrandbits(num_of_bits)                                    #(E4)
        b = random.getrandbits(num_of_bits)                                    #(E5)
        if (4*a**3 + 27*b**2)%mod == 0: continue                               #(E6)
        break                                                                  #(E7)
    return (a,b)                                                               #(E8)

def mycmp(p1, p2):                                                             #(F1)
    if p1[0] == p2[0]:                                                         #(F2)
        if p1[1] > p2[1]: return 1                                             #(F3)
        elif p1[1] < p2[1]: return -1                                          #(F4)
        else: return 0                                                         #(F5)
    elif p1[0] > p2[0]: return 1                                               #(F6)
    else: return -1                                                            #(F7)

def display( all_points ):                                                     #(G1)
    point_at_infy = ["point at infinity" for point in all_points \
                                             if isinstance(point,str)]         #(G2)
    all_points = [[int(str(point[0]).rstrip("L")), \
                   int(str(point[1]).rstrip("L"))] \
                     for point in all_points if not isinstance(point, str)]    #(G3)

    all_points.sort( key = functools.cmp_to_key(mycmp) )
    all_points += point_at_infy                                                #(G5)
    print(str(all_points))                                                     #(G6)


if __name__ == '__main__':

    # Example 1:
    p = 23                                                                     #(M1)
    a,b = 1,4          # y^2 = x^3 + x + 4                                     #(M2)
    point = get_point_on_curve( (a,b), p)                                      #(M3)
    print("Point: %s\n" % str(point))        # (7,3)                           #(M4)
    all_points = list(map( lambda k: k_times_point((a,b), \
                              (point[0],point[1]), k, p), range(1,30)))         #(M5)
    display(all_points)                                                        #(M6)
          # [[0, 2], [0, 21], [1, 11], [1, 12], [4, 7], [4, 16], [7, 3], 
          #  [7, 20], [8, 8], [8, 15], [9, 11], [9, 12], [10, 5], 
          #  [10, 18], [11, 9], [11, 14], [13, 11], [13, 12], [14, 5], 
          #  [14, 18], [15, 6], [15, 17], [17, 9], [17, 14], [18, 9], 
          #  [18, 14], [22, 5], [22, 18], 'point at infinity']

    # Example 2:
    generator = PrimeGenerator( bits = 16 )                                    #(M7)
    p = generator.findPrime()                           # 64951                #(M8)
    print("Prime returned: %d" % p)                                            #(M9)
    a,b = choose_curve_params(p, 16)                                           #(M10)
    print("a and b for the curve: %d %d" % (a, b))      # 62444, 47754         #(M11)
    point = get_point_on_curve( (a,b), p)                                      #(M12)
    print(str(point))                                   # (1697, 89)           #(M13)

    # Example 3:
    ##  Parameters of the DRM2 elliptic curve:
    p = 785963102379428822376694789446897396207498568951                       #(M14)
    a = 317689081251325503476317476413827693272746955927                       #(M15)
    b = 79052896607878758718120572025718535432100651934                        #(M16)
    # A point on the curve:
    Gx = 771507216262649826170648268565579889907769254176                      #(M17)
    Gy = 390157510246556628525279459266514995562533196655                      #(M18)
    
    print(str(list(map( lambda k: k_times_point((a,b), (Gx,Gy), k, p),
                                     range(1,5)))))                            #(M19)
#         [(771507216262649826170648268565579889907769254176L, 
#                      390157510246556628525279459266514995562533196655L), 
#          [131207041319172782403866856907760305385848377513L, 
#                      2139936453045853218229235170381891784525607843L], 
#          [716210695201203540500406352786629938966496775642L, 
#                      251074363473168143346338802961433227920575579388L], 
#          [695225880076209899655288358039795903268427836810L, 
#                      87701351544010607198039768840869029919832813267L]]
