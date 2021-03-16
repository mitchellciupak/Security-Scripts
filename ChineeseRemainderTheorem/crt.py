# Credit: https://github.com/humak/ChineseRemainder-InverseEulerTotient/blob/master/lab4.py
# Also See: https://github.com/rainmayecho/phi/blob/master/eulerphi.py
import math

def findMinX(num, rem, k):
    x = 1
    while(True):
        j = 0
        while(j < k):
            if (x % num[j] != rem[j]):
                break
            j += 1
        if (j == k):
            return x
        x += 1

def gcd(m,n):
    if(n != 0):
        return gcd(n, m%n)
    return m

def isPrime(n):
    if (n <= 1) :
        return False
    if (n <= 3) :
        return True
    if (n % 2 == 0 or n % 3 == 0) :
        return False
    i = 5
    while(i * i <= n) :
        if (n % i == 0 or n % (i + 2) == 0) :
            return False
        i = i + 6
    return True


def inverseOfEulersTotient(z):
    n = 1
    mcount = 0
    nlist = []
    while (1):
        for m in range (1,n):
            if(gcd(m,n)==1):
                mcount += 1
        if(mcount == z):
            nlist.append(n)
        mcount = 0
        n +=1
        if(n > 1000): #guessing an integer for upper bound
            print(nlist)
            break

def eulersTotient(n):
    z = 1
    for i in range(2, n):
        if (gcd(i, n) == 1):
            z+=1
    return z

def main():
    num = [19, 18, 17]
    rem = [10, 12, 14]
    k = len(num)
    print("x is", findMinX(num, rem, k))  #ANSWER: x = 48

    inverseOfEulersTotient(100)

    for n in range (1,1000):
        if(eulersTotient(n) == eulersTotient(n+1)):
            print(n, " - ", n+1)

if __name__== "__main__":
  main()