"""
Dragomir Ioan - trupples
NSU Crypto 2020 first round, problem 7 "Collisions"

n = number of bits
N = 2^n

actual_f = the f function used to calculate the "real" hash to verify
known_f = the subset of f with n*10 elements

"""

import random
import hashlib

def f(x):
	return int.from_bytes(hashlib.sha512(x.to_bytes(64, 'big')).digest(), 'big')

n = 512
N = 1<<n

#actual_f = list(range(N))
#random.shuffle(actual_f)

known_f = {}
for _ in range(n*10):
	x = random.randrange(0, N)
	known_f[x] = f(x)

def H(blocks):
	h = 0
	for b in blocks:
		h ^= b
		h = f(h)
		h ^= b
	return h

"""
O(n^2) solution (which will be later easily simplified to O(nlogn))

The idea is to start with a message whose hash we can compute using the known
points, then append two blocks, the first changing the hash and then the second
restoring it to the initial value. All lookups into f MUST only use the known
points, therefore we will iterate through those and extract the message block
from there, so instead of calculating
  unk_f_index = known_block ^ known_prev_hash,
we calculate
  unk_block = known_f_index ^ known_prev_hash.
(This will be clearer later, I think I explained it very roughly)

Let h0 be the hash of the initial message, which can be arbitrary, but we'll 
compute it by using one of the known points:
"""

m0 = random.choice(list(known_f.keys())) # a known x value
h0 = m0 ^ known_f[m0]

"""
Now we will append 2 blocks m1, m2:

h1 = m1 ^ f[m1 ^ h0]
h2 = m2 ^ f[m2 ^ h1]

It is imperative that m1^h0 and m2^h1 are within the known points, so we will
use the trick explained at the beginning:
"""

for m1_xor_h0 in known_f:
	m1 = m1_xor_h0 ^ h0
	h1 = m1 ^ known_f[m1_xor_h0]

	"""
	Now that we have a seemingly random hash after appending one more block,
	find a nice value for the next block to get back to the initial hash:
	"""
	for m2_hox_h1 in known_f:
		m2 = m2_hox_h1 ^ h1
		h2 = m2 ^ known_f[m2_hox_h1]

		if h2 == h0:
			print("(1) Collision! ", [m0], [m0,m1,m2])
			assert H([m0]) == H([m0,m1,m2])

"""
This algorithm is quadratic in the number of known points = the number of bits.
We can optimise the second loop by playing around with the final condition:

                  h2 == h0
m2 ^      f[m2 ^ h1] == h0
m2 ^ h1 ^ f[m2 ^ h1] == h0 ^ h1

let q = m2^h1

q ^ f[q] = h0 ^ h1

We can create a lookup table to quickly resolve problems of the form x^f[x]=y:
"""

xfx = { x^known_f[x] : x for x in known_f } 

"""
And change the two nested for loops to a single loop (n) and a lookup (logn):
"""

for m1_xor_h0 in known_f:
	m1 = m1_xor_h0 ^ h0
	h1 = m1 ^ known_f[m1_xor_h0]

	try:
		m2_xor_h1 = xfx[h0 ^ h1]
		m2 = m2_xor_h1 ^ h1
		print("(2) Collision! ", [m0], [m0,m1,m2])
		assert H([m0]) == H([m0,m1,m2])
	except KeyError as ke: pass # Not all h0^h1 values will be in the xfx table

"""
Thus achieving a final time complexity of O(nlogn) where n is the number of
bits of the function.
"""
