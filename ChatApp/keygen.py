import random
import pickle
import os
import hashlib
primes = [2]

def nth_prime(n):
    global primes
    if "primes.pickle" in os.listdir("."):
        with open("primes.pickle", 'rb') as f:
            primes = pickle.load(f)

    i = primes[-1] + 1
    changed = False

    while(len(primes)<=n):
        if isprime(i):
            primes.append(i)
            changed = True
        i+=1

    if changed:
        with open("primes.pickle", "wb") as f:
            pickle.dump(primes, f) 

    return primes[n-1]

def isprime(n):
    global primes
    for p in primes:
        if n%p==0:
            return False
    return True

def modexp_lr_k_ary(a, b, n, k=5):
    """ Compute a ** b (mod n)

        K-ary LR method, with a customizable 'k'.
    """
    base = int(2 << (k - 1))

    # Precompute the table of exponents
    table = [1] * base
    for i in range(1, base):
        table[i] = table[i - 1] * int(a % n)

    # Just like the binary LR method, just with a
    # different base
    #
    r = 1
    for digit in reversed(_digits_of_n(b, base)):
        for i in range(k):
            r = r * r % n
        if digit:
            r = r * table[digit] % n

    return r

def _digits_of_n(n, b):
    """ Return the list of the digits in the base 'b'
        representation of n, from LSB to MSB
    """
    digits = []

    while n:
        digits.append(n % b)
        n = int(n/b)

    return digits    

def keygen(passwd):
    global primes
    hex_val = hashlib.sha1(passwd.encode()).hexdigest()[:8]
    x = int("0x" + hex_val, 0)
    p = nth_prime(random.randint(1000, 10000))
    print(x)
    A = random.randint(1, 1000)
    B = modexp_lr_k_ary(A, x, p)
    return {"x":x, "A":A, "B":B, "p":p}

# print(keygen("rohith"))
