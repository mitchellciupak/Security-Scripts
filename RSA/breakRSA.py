#!/usr/bin/env python3

# Homework Number: 6
# Name: Mitchell Ciupak
# ECN Login: ciupak
# Due Date: 20210309

"""NOTICE: This script was created with the influence and awareness of Prof. Avi Kak's './Lecture12Code and 'Lecture8.pdf' and functions were directly implemented after testing"""

import sys
from BitVector import *
from solve_pRoot_BST import solve_pRoot
from PrimeGenerator import PrimeGenerator

KEY_SIZE = 256
BLOCK_SIZE = 256
DATA_BLOCK = 128
e = 3

class RSA2:

    def __init__(self,*args,**kwargs):
        self.flag = args[0]

        if self.flag == 'g':
            self.p_fptr = open(kwargs['p'],'w')
            self.q_fptr = open(kwargs['q'],'w')
            return

        if self.flag == 'e' or self.flag == 'd':
            self.p = BitVector(intVal=kwargs['p'])
            self.q = BitVector(intVal=kwargs['q'])
            self.mod = int(self.p) * int(self.q)
            self.out_fptr = open(kwargs['out'],'w')

    def __del__(self):

        if self.flag != 'NO':
            self.out_fptr.close()

    def gcd(self,a,b):
        while(b):
            # temp_a, temp_b = a,b
            a,b = b, a%b
            # print("The GCD of", temp_a," and",temp_b," is : ", b)

        return a

    def generate_key(self):

        self.p = 0
        self.q = 0

        self.generator = PrimeGenerator( bits = BLOCK_SIZE )
        self.prime = self.generator.findPrime()

        for i in range(self.prime, 100, -1):

            # print(i)
            # Find p
            p = self.generator.findPrime()
            if (self.gcd(p-1,e) and BitVector(intVal=p)[0] and BitVector(intVal=p)[1]) == 1: # (a) & (c)
                self.p = p

            # Find p
            q = self.generator.findPrime()
            if (self.gcd(q-1,e) and BitVector(intVal=q)[0] and BitVector(intVal=q)[1]) == 1: # (a) & (c)
                self.q = q

            if self.p != self.q and self.p != 0 and self.q != 0: # (b)
                if BitVector(intVal=p*q).count_bits() == BLOCK_SIZE:
                    return int(self.p),int(self.q)

    def encryptABlock(self,block):
        mod = self.mod
        e_var = e
        block = int(block)

        newblock = 1
        while e_var > 0:
            if e_var & 1:
                newblock = (newblock*block) % mod
            e_var = e_var >> 1
            block = (block**2) % mod
        return newblock


    def encrypt(self,plaintext):

        in_bv = BitVector(filename=plaintext)
        block = BitVector(size=0)

        while in_bv.more_to_read:
            block = in_bv.read_bits_from_file(DATA_BLOCK)
            if block.length() < DATA_BLOCK:
                block.pad_from_right(DATA_BLOCK - block.length())
            block.pad_from_left(128)


            out = self.encryptABlock(block=block)

            out = format(out,"064x")

            self.out_fptr.write(out)


def output(bv,file):
    fptr = open(file,'a')
    # fptr.write(int(bv))
    fptr.close

'''
# Arguments
* 0: this file pointer
* 1: encrypt/crack flag
## Encrypt Arguments
* 2: message.txt file
* 3: enc1.txt file
* 4: enc2.txt file
* 5: enc3.txt file
* 6: n_1_2_3.txt file
## Crack Arguments
* 2: enc1.txt file
* 3: enc2.txt file
* 4: enc3.txt file
* 5: n_1_2_3.txt file
* 6: output file
'''
if __name__ == "__main__":

    if len(sys.argv) != 7:
        print('Incorrect number of arguments supplied.')
        exit()

    # Check Arguments for flags
    if sys.argv[1] == "-e":
        # print("Encryption")

        #Generate 3 Sets of P and Q
        p1,q1 = RSA2('NO').generate_key()
        p2,q2 = RSA2('NO').generate_key()
        p3,q3 = RSA2('NO').generate_key()

        print("", p1,"\n",p2,"\n",p3)#,"\n",q1,"\n",q2,"\n",q3)

        rsa1 = RSA2('e',p=p1,q=q1,out=sys.argv[3])
        rsa1.encrypt(sys.argv[2])

        rsa2 = RSA2('e',p=p2,q=q2,out=sys.argv[4])
        rsa2.encrypt(sys.argv[2])

        rsa3 = RSA2('e',p=p3,q=q3,out=sys.argv[5])
        rsa3.encrypt(sys.argv[2])

        e_bv = BitVector(intVal=e)
        # output(e_bv.multiplicative_inverse(BitVector(intVal=p1-1 * q1-1)),sys.argv[6])
        # output(e_bv.multiplicative_inverse(BitVector(intVal=p2-1 * q2-1)),sys.argv[6])
        # output(e_bv.multiplicative_inverse(BitVector(intVal=p3-1 * q3-1)),sys.argv[6])

        print('\x1b[6;30;42m' + 'Success -> ' + '\x1b[0m' + '\x1b[6;30;42m' + "Open " + sys.argv[5] + " to see your output" + '\x1b[0m')

    elif sys.argv[1] == "-c":
        pass
    else:
        print('No arguments supplied. Please add the to the arugments list.')