"""
Dragomir Ioan - trupples
NSU Crypto 2020 second round, problem 7 "CPA game". Solution is identical to the first round.

We can solve this with a 100% success rate in 3 queries:

query 1:
	victor sends (z1, z2) (implementation: I send the same valid plaintext twice, z1=z2)
	victor receives next_iv = enc(z1^iv) or enc(z2^iv)

query 2:
	victor sends (next_iv, next_iv)
	victor receives enc(0)

query 3:
	victor sends (enc(0), z3), z3 != enc(0). (implementation: I generate a valid plaintext different to enc(0))
	victor either receives enc(0) again, case in which b=0, or not, case in which b=1
"""

import random, os
from Crypto.Cipher import AES

class NumericalAlice:
	def __init__(self):
		self.N = 65536
		self.b = random.randint(0, 1)
		self.iv = random.randint(0, self.N)
		self.enc_table = list(range(self.N)) # simulating a completely unknown encryption function with a shuffled lookup table
		random.shuffle(self.enc_table)

	def enc(self, x):
		x ^= self.iv
		x = self.enc_table[x]
		self.iv = x
		return x

	def query(self, m0, m1):
		return self.enc([m0,m1][self.b])

	def check_correct(self, predicted_b):
		return self.b == predicted_b

	def random_valid_plaintext(self):
		return random.randint(0, self.N-1)

class AESAlice:
	def __init__(self):
		self.b = random.randint(0, 1)
		self.crypt = AES.new(mode=AES.MODE_CBC, iv=os.urandom(16), key=os.urandom(16))

	def enc(self, x):
		assert len(x) == 16
		return self.crypt.encrypt(x)

	def query(self, m0, m1):
		return self.enc([m0,m1][self.b])

	def check_correct(self, predicted_b):
		return self.b == predicted_b

	def random_valid_plaintext(self):
		return os.urandom(16)

def victor(alice):
	z1 = alice.random_valid_plaintext()
	while True:
		z2 = alice.random_valid_plaintext()
		if z2 != z1:
			break
	next_iv = alice.query(z1, z2)
	enc0 = alice.query(next_iv, next_iv)

	while True:
		z3 = alice.random_valid_plaintext()
		if z3 != enc0:
			break

	r = alice.query(enc0, z3)
	predicted_b = 0 if r == enc0 else 1
	return predicted_b, alice.check_correct(predicted_b)

print("Running 100 times with my dumb number cryptosystem")
for attempt in range(100):
	print(attempt, *victor(NumericalAlice()))

print("Running 100 times with AES")
for attempt in range(100):
	print(attempt, *victor(AESAlice()))
