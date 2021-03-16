#!/usr/bin/env python3

# Homework Number: 6
# Name: Mitchell Ciupak
# ECN Login: ciupak
# Due Date: 20210309

"""NOTICE: This script was created with the influence and awareness of Prof. Avi Kak's './Lecture12Code and 'Lecture8.pdf' and functions were directly implemented after testing"""

import sys
from BitVector import *
from PrimeGenerator import PrimeGenerator

KEY_SIZE = 256
BLOCK_SIZE = 256
DATA_BLOCK = 128
e = 65537

class RSA:

    def __init__(self,*args,**kwargs):
        self.flag = args[0]

        if self.flag == 'g':
            self.p_fptr = open(kwargs['p'],'w')
            self.q_fptr = open(kwargs['q'],'w')

            self.generator = PrimeGenerator( bits = BLOCK_SIZE )
            self.prime = self.generator.findPrime()
            return

        # Else E or D
        self.p_fptr = open(kwargs['p'],'r')
        self.q_fptr = open(kwargs['q'],'r')
        self.p = BitVector(intVal=int(self.p_fptr.read()))
        self.q = BitVector(intVal=int(self.q_fptr.read()))

        self.mod = int(self.p) * int(self.q)

        self.out_fptr = open(kwargs['out'],'w')

    def __del__(self):

        self.p_fptr.close()
        self.q_fptr.close()

        if self.flag == 'g':
            return

        # Else E or D
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

        for i in range(self.prime, 100, -1):

            # Find p
            p = self.generator.findPrime()
            if (self.gcd(p-1,e) and BitVector(intVal=p)[0] and BitVector(intVal=p)[1]) == 1: # (a) & (c)
                self.p = p

            # Find p
            q = self.generator.findPrime()
            if (self.gcd(q-1,e) and BitVector(intVal=q)[0] and BitVector(intVal=q)[1]) == 1: # (a) & (c)
                self.q = q

            if self.p != self.q and self.p != 0 and self.q != 0: # (b)
                if BitVector(intVal=q).count_bits() + BitVector(intVal=p).count_bits() == 256:
                    return int(self.p),int(self.q)

    def output(self,var,fptr):
        fptr.write(str(var))

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

        return BitVector(intVal=newblock,size=256)


    def encrypt(self,plaintext):

        in_bv = BitVector(filename=plaintext)
        block = BitVector(size=0)

        while in_bv.more_to_read:
            block = in_bv.read_bits_from_file(DATA_BLOCK)
            if block.length() < DATA_BLOCK:
                block.pad_from_right(DATA_BLOCK - block.length())
            block.pad_from_left(128)

            # block = BitVector(intVal=pow(int(block),e,self.mod))
            block = self.encryptABlock(block=block)

            self.out_fptr.write(block.get_bitvector_in_hex())

    def decrypt(self,plaintext):

        in_fptr = open(plaintext,'r')
        in_bv = BitVector(hexstring=in_fptr.read())
        block = BitVector(size=0)

        self.tot = BitVector(intVal=(int(self.p)-1)*(int(self.q)-1))
        self.e = BitVector(intVal=e, size=DATA_BLOCK)
        self.d = self.e.multiplicative_inverse(self.tot)

        for i in range(0,int(in_bv.length() / BLOCK_SIZE)):

            block = in_bv[i*BLOCK_SIZE:(i+1)*BLOCK_SIZE]

            block = block.int_val()
            block = pow(block,int(self.d),int(self.mod))
            block = BitVector(intVal=block,size=128)

            if block.length() < DATA_BLOCK:
                block = block.pad_from_right(DATA_BLOCK - block.length())

            self.out_fptr.write(block.get_bitvector_in_ascii())

        in_fptr.close()

'''
# Arguments
* 0: this file pointer
* 1: generation/encrypt/decrypt flag
## Generation Arguments
* 2: p.txt file
* 3: q.txt file
## Encrypt/Decryption Arguments
* 2: input file
* 3: p.txt file
* 4: q.txt file
* 4: output file
'''
if __name__ == "__main__":


    # Check Arguments for flags
    if sys.argv[1] == "-g":
        # print("Key Generation")

        if len(sys.argv) != 4:
            print('Incorrect number of arguments supplied.')
            exit()

        rsa = RSA('g',p=sys.argv[2],q=sys.argv[3])
        print(rsa.generate_key())
        rsa.output(rsa.p,rsa.p_fptr)
        rsa.output(rsa.q,rsa.q_fptr)

        print('\x1b[6;30;42m' + 'Success' + '\x1b[0m')
    elif sys.argv[1] == "-e":
        # print("Encryption")

        if len(sys.argv) != 6:
            print('Incorrect number of arguments supplied.')
            exit()

        rsa = RSA('e',p=sys.argv[3],q=sys.argv[4],out=sys.argv[5])
        rsa.encrypt(sys.argv[2])

        print('\x1b[6;30;42m' + 'Success -> ' + '\x1b[0m' + '\x1b[6;30;42m' + "Open " + sys.argv[5] + " to see your output" + '\x1b[0m')
    elif sys.argv[1] == "-d":
        # print("Decryption")

        if len(sys.argv) != 6:
            print('Incorrect number of arguments supplied.')
            exit()

        rsa = RSA('d',p=sys.argv[3],q=sys.argv[4],out=sys.argv[5])
        rsa.decrypt(sys.argv[2])

        print('\x1b[6;30;42m' + 'Success -> ' + '\x1b[0m' + '\x1b[6;30;42m' + "Open " + sys.argv[5] + " to see your output" + '\x1b[0m')
    else:
        print('No arguments supplied. Please add the to the arugments list.')
