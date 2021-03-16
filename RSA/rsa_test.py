import os
from rsa import RSA
from BitVector import *

# Initial
messege_file = "/home/mc/Documents/ECE404/RSA/resources/message.txt"

test_encrypted_file = "/home/mc/Documents/ECE404/RSA/resources/encrypted.txt"
test_q_file = "/home/mc/Documents/ECE404/RSA/resources/q.txt"
test_p_file = "/home/mc/Documents/ECE404/RSA/resources/p.txt"

my_d_file = "/home/mc/Documents/ECE404/RSA/resources/myd.txt"
my_e_file = "/home/mc/Documents/ECE404/RSA/resources/mye.txt"
my_p_file = "/home/mc/Documents/ECE404/RSA/resources/myp.txt"
my_q_file = "/home/mc/Documents/ECE404/RSA/resources/myq.txt"

break_encrypted1_file = "/home/mc/Documents/ECE404/RSA/resources/encrypted_1.txt"
break_encrypted2_file = "/home/mc/Documents/ECE404/RSA/resources/encrypted_2.txt"
break_encrypted3_file = "/home/mc/Documents/ECE404/RSA/resources/encrypted_3.txt"

## create objects
# rsa4e = RSA('e',p=test_p_file,q=test_q_file,out=my_e_file)  # created for Encryption
# rsa4d = RSA('d',p=test_p_file,q=test_q_file,out=my_d_file)  # created for Decryption

# AES.py file I/O Tests
def test_encryption():
    # rsa4e.encrypt(plaintext=messege_file)
    stream1 = os.popen("python rsa.py -e " + messege_file + " " + test_p_file  + " " + test_q_file  + " " + my_e_file)
    stream2 = os.popen("diff " + my_e_file + test_encrypted_file)
    assert stream2.read() == ""


# def test_fileIO_correctArguments():
#   stream = os.popen("python AES.py -e message.txt key.txt encrypted.txt")
#   assert stream.read() == "[6;30;42mSuccess -> [0m[6;30;42mOpen encrypted.txt to see your output[0m\n"


# def test_fileIO_tooManyArguments():
#     stream = os.popen("python AES.py -e message.txt key.txt encrypted.txt decrypted.txt")
#     assert stream.read() == "No arguments supplied. Please add the to the arugments list.\n"
