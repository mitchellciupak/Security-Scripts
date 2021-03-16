#!/usr/bin/env python3

# Homework Number: 5
# Name: Mitchell Ciupak
# ECN Login: ciupak
# Due Date: 202010302

"""NOTICE: This script was created with the influence and awareness of Prof. Avi Kak's './Lecture8Code and 'Lecture8.pdf' and functions were directly implemented after testing"""

import sys
from BitVector import *

ROUND_COUNT = 14
BLOCK_SIZE = 128
KEY_SIZE = 256

ROWS = 4
COLS = 4

key_words = []

# Arguments:
## v0: 128-bit BitVector object containing the seed value
## dt: 128-bit BitVector object symbolizing the date and time
## key_file: String of file name containing the encryption key (in ASCII) for AES
## totalNum: integer indicating the total number of random numbers to generate
# Function Description:
## Uses the arguments with the X9.31 algorithm to generate totalNum random numbers as BitVector objects
# Returns:
## a list of BitVector objects, with each BitVector object representing a random number generated from X9.31
def x931(v0, dt, totalNum, key_file):
    out = []

    #Create AES Object
    a = AES(key_file)

    for i in range(0,totalNum):
        dt = a.encrypt(dt)
        v = v0 ^ dt

        output_val = a.encrypt(v)
        v = dt ^ output_val
        v0 = a.encrypt(v)

        out.append(output_val.deep_copy())

    return out

class AES():
    def __init__(self, keyfile):
        self.key_fptr = open(keyfile, 'r')
        self.key = self.key_fptr.read()
        self.key_bv = BitVector(textstring=self.key)

        self.s_table = None
        self.round_const = None
        self.AES_modulus = BitVector(bitstring='100011011')

    def __del__(self):
        self.key_fptr.close()

    def outputBVtoFILE(self, bv):
        if (self.out_fptr):
            bv.write_to_file(self.out_fptr)
            return
        print('\x1b[6;30;43m' + 'Failure to Output to Outfile!' + '\x1b[0m')

    def prep_s_table_forEncryption(self):
        self.s_table = []
        c = BitVector(bitstring='01100011')

        for i in range(0, 256):
            # For the encryption SBox
            a = BitVector(intVal=i, size=8).gf_MI(
                self.AES_modulus, 8) if i != 0 else BitVector(intVal=0)
            # For bit scrambling for the encryption SBox entries:
            a1, a2, a3, a4 = [a.deep_copy() for x in range(4)]
            a ^= (a1 >> 4) ^ (a2 >> 5) ^ (a3 >> 6) ^ (a4 >> 7) ^ c
            self.s_table.append(int(a))

        return self.s_table

    def prep_s_table_forDecryption(self):
        self.s_table = []

        d = BitVector(bitstring='00000101')

        for i in range(0, 256):
            # For the decryption Sbox:
            b = BitVector(intVal=i, size=8)
            # For bit scrambling for the decryption SBox entries:
            b1, b2, b3 = [b.deep_copy() for x in range(3)]
            b = (b1 >> 2) ^ (b2 >> 5) ^ (b3 >> 7) ^ d
            check = b.gf_MI(self.AES_modulus, 8)
            b = check if isinstance(check, BitVector) else 0
            self.s_table.append(int(b))

        return self.s_table

    def gee(self,keyword, round_constant, byte_sub_table):  # Figure 4, Lecture 8
        rotated_word = keyword.deep_copy()
        rotated_word << 8
        newword = BitVector(size=0)
        for i in range(4):
            newword += BitVector(intVal=byte_sub_table[rotated_word[8 * i:8 * i + 8].intValue()], size=8)
        newword[:8] ^= round_constant
        round_constant = round_constant.gf_multiply_modular(BitVector(intVal=0x02), self.AES_modulus, 8)
        return newword, round_constant


    def prep_key_words(self):

        self.key_words = [None for i in range(60)]
        round_constant = BitVector(intVal=0x01, size=8)
        for i in range(8):
            self.key_words[i] = self.key_bv[i * 32:i * 32 + 32]
        for i in range(8, 60):
            if i % 8 == 0:
                kwd, round_constant = self.gee(self.key_words[i - 1], round_constant, self.s_table)
                self.key_words[i] = self.key_words[i - 8] ^ kwd
            elif (i - (i // 8) * 8) < 4:
                self.key_words[i] = self.key_words[i - 8] ^ self.key_words[i - 1]
            elif (i - (i // 8) * 8) == 4:
                self.key_words[i] = BitVector(size=0)
                for j in range(4):
                    self.key_words[i] += BitVector(intVal=self.s_table[self.key_words[i - 1][8 * j:8 * j + 8].intValue()], size=8)
                self.key_words[i] ^= self.key_words[i - 8]
            elif ((i - (i // 8) * 8) > 4) and ((i - (i // 8) * 8) < 8):
                self.key_words[i] = self.key_words[i - 8] ^ self.key_words[i - 1]
            else:
                sys.exit("error in key scheduling algo for i = %d" % i)
        return self.key_words

    def prep_key_schedule(self):
        if self.s_table is None:
            self.prep_s_table_forEncryption()

        self.key_schedule = []
        self.key_words = self.prep_key_words()

        for word_index, word in enumerate(self.key_words):
            keyword_in_ints = []
            for i in range(4):
                keyword_in_ints.append(word[i * 8:i * 8 + 8].intValue())
            self.key_schedule.append(keyword_in_ints)

        return self.key_words

    def SubBytes(self,block):
        if self.s_table is None or self.s_table[0] != 99:
            self.prep_s_table_forEncryption()

        blockAsString = list(block.get_bitvector_in_ascii())
        newBlockAsString = ""
        for i in blockAsString:
            newBlockAsString += chr(self.s_table[ord(i)])

        return BitVector(textstring=newBlockAsString)

    def ShiftRows(self,block):

        blockAsString = list(block.get_bitvector_in_ascii())

        blockAsString[1],blockAsString[5],blockAsString[9],blockAsString[13] = blockAsString[5],blockAsString[9],blockAsString[13],blockAsString[1]
        blockAsString[2],blockAsString[6],blockAsString[10],blockAsString[14] = blockAsString[10],blockAsString[14],blockAsString[2],blockAsString[6]
        blockAsString[3],blockAsString[7],blockAsString[11],blockAsString[15] = blockAsString[15],blockAsString[3],blockAsString[7],blockAsString[11]

        blockAsString = "".join(blockAsString)
        return BitVector(textstring=blockAsString)

    def MixCol(self,block):
        newBlock = BitVector(size = 0)

        dos = BitVector(intVal=2,size=8)
        tres = BitVector(intVal=3,size=8)

        bCharList = list(block.get_bitvector_in_ascii()) #blockAsCharArray
        for col in range(0,COLS):
            for row in range(0,ROWS):
                if row == 0: newBlock +=  BitVector(textstring=bCharList[col*4+0]).gf_multiply_modular(dos,self.AES_modulus,8) ^ BitVector(textstring=bCharList[col*4+1]).gf_multiply_modular(tres,self.AES_modulus,8) ^ BitVector(textstring=bCharList[col*4+2]) ^ BitVector(textstring=bCharList[col*4+3])
                if row == 1: newBlock +=  BitVector(textstring=bCharList[col*4+1]).gf_multiply_modular(dos,self.AES_modulus,8) ^ BitVector(textstring=bCharList[col*4+2]).gf_multiply_modular(tres,self.AES_modulus,8) ^ BitVector(textstring=bCharList[col*4+0]) ^ BitVector(textstring=bCharList[col*4+3])
                if row == 2: newBlock +=  BitVector(textstring=bCharList[col*4+2]).gf_multiply_modular(dos,self.AES_modulus,8) ^ BitVector(textstring=bCharList[col*4+3]).gf_multiply_modular(tres,self.AES_modulus,8) ^ BitVector(textstring=bCharList[col*4+0]) ^ BitVector(textstring=bCharList[col*4+1])
                if row == 3: newBlock +=  BitVector(textstring=bCharList[col*4+3]).gf_multiply_modular(dos,self.AES_modulus,8) ^ BitVector(textstring=bCharList[col*4+0]).gf_multiply_modular(tres,self.AES_modulus,8) ^ BitVector(textstring=bCharList[col*4+1]) ^ BitVector(textstring=bCharList[col*4+2])

        return newBlock

    def AddRoundKey(self,block,i):
        w = ""
        w += self.key_schedule[i*4+0].get_bitvector_in_ascii()
        w += self.key_schedule[i*4+1].get_bitvector_in_ascii()
        w += self.key_schedule[i*4+2].get_bitvector_in_ascii()
        w += self.key_schedule[i*4+3].get_bitvector_in_ascii()
        bv = BitVector(textstring=w)
        return block ^ bv

    ########### Primary Functions ###########

    def encrypt(self, in_bv):
        self.in_bv = in_bv #128
        self.out_bv = BitVector(size=0)

        self.prep_s_table_forEncryption()
        self.key_schedule = self.prep_key_schedule()

        block = self.in_bv

        if (block.length() != BLOCK_SIZE):
            block.pad_from_right(BLOCK_SIZE - block.length())

        block = self.AddRoundKey(block,0)

        for round in range(0, ROUND_COUNT): # Round 0-13 aka 1-14
            block = self.SubBytes(block)
            block = self.ShiftRows(block)

            if round != (ROUND_COUNT - 1): #Skip for last round
                block = self.MixCol(block)

            block = self.AddRoundKey(block,round+1)


        self.out_bv = block.deep_copy()

        return self.out_bv

if __name__ == "__main__":
    v0 = BitVector(textstring="computersecurity")
    dt = BitVector(intVal = 501, size=128)
    listX931 = x931(v0,dt,3,"resources/keyX931.txt")
    print("{}\n{}\n{}".format(int(listX931[0]),int(listX931[1]),int(listX931[2])))