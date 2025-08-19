import math

class Prime :
    def __init__(self, size):
        self.size = size 

    def run(self):
        arr = [True] * self.size
        arr[0] = False
        arr[1] = False
        for i in range(2, int(math.sqrt(self.size)) + 1):
            if arr[i]:
                for j in range(i * i, self.size, i):
                    arr[j] = False
        primes = [i for i, is_prime in enumerate(arr) if is_prime]
        return primes

if __name__ == "__main__" :
    a = Prime(100000)
    print(a.run())
