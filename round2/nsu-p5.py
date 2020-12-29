"""
This approach is immensly non-general, but if the Kolmogorov complexity is
irrelevant, it is optimal. I will build an algorithm which uses the same concept
as in [Minimal perfect hash functions], by identifying each unique matrix with a
number from 0 to 85036. This is not a practical algorithm because most of the
information is stored in the algorithm itself, and any matrix not in the input
set cannot be encoded.

Furthermore, we can treat those indices, or the matrices themselves, as
arbitrary symbols and use Huffman coding on the multiset of *entire matrices* to
obtain an optimal encoding.

Yet again, if the input set was changed, we would need to recompute the set of
unique matrices and the huffman codes, but this algorithm fits the requirements:
 - the sum of the lengths of the encoded matrices is minimal, by the very nature
   of huffman coding

 - each matrix can be mapped to a seuqence of bits, and this is reversible

[Minimal perfect hash functions]: https://en.wikipedia.org/wiki/Perfect_hash_function#Minimal_perfect_hash_function
"""

from functools import reduce
from collections import Counter
import math

BIAS = 127
def Matrix(s):
	return bytes([int(q)+BIAS for q in s.strip().split(' ')])

class HuffmanNode:
	def __init__(self, a, b):
		if type(a) == bytes and type(b) == int:
			self.leaf = True
			self.value = a
			self.count = b
			self.depth = 1
		elif type(a) == HuffmanNode and type(b) == HuffmanNode:
			self.leaf = False
			self.value = (a.value, b.value)
			self.count = a.count + b.count
			self.depth = max(a.depth, b.depth) + 1
		else:
			raise TypeError

	def __lt__(self, other):
		return self.count < other.count

	def __repr__(self):
		return f"<HuffmanNode depth={self.depth}>"

matrices = []

hamming_sum = [0]*64
value_sum = [0]*64
bit_sum = [0]*64
nonzero_sum = [0]*64

element_frequencies = [Counter() for _ in range(64)]

def hamming_weight(x):
	n = 0
	while x:
		n += x&1
		x>>=1
	return n

def bit_count(x):
	n = 0
	while x:
		n += 1
		x>>=1
	return n

print("Reading matrices from file")
with open("jpeg-matrices.txt") as f:
	for line in f:
		m = Matrix(line)
		matrices.append(m)

		for i in range(64):
			x = m[i] - 127
			hamming_sum[i] += hamming_weight(abs(x))
			value_sum[i] += x
			bit_sum[i] += bit_count(abs(x))
			if x != 0:
				nonzero_sum[i] += 1
			element_frequencies[i][x] += 1

def print_tbl(tbl, bias=0):
	tbl = [[tbl[i*8+j]-bias for j in range(8)] for i in range(8)]
	row_widths = [max([len(str(tbl[i][j])) for i in range(8)]) for j in range(8)]
	for i in range(8):
		for j in range(8):
			print(str(tbl[i][j]).rjust(row_widths[j]), end=' ')
		print()

print("Hamming sum:")
print_tbl(hamming_sum)
print("Value sum:")
print_tbl(value_sum)
print("Bit sum:")
print_tbl(bit_sum)
print("Nonzero sum:")
print_tbl(nonzero_sum)

from heapq import heappush, heappop, heapify
from collections import Counter

print("Building huffman code")
huffman = []
heapify(huffman)

ctr = Counter(matrices)

for mat in ctr:
	heappush(huffman, HuffmanNode(mat, ctr[mat]))

while len(huffman) > 1:
	a = heappop(huffman)
	b = heappop(huffman)
	heappush(huffman, HuffmanNode(a, b))

huffman = heappop(huffman)

print("Building compression table")
compress_table = {}
uncompress_table = {}
shortest = '1'*100
longest = '1'
def bfs(subtree, bits=''):
	global shortest, longest
	#print(subtree)
	if type(subtree) == bytes:
		compress_table[subtree] = bits
		uncompress_table[int('1'+bits, 2)] = subtree
		if len(bits) < len(shortest):
			shortest = bits
		if len(bits) > len(longest):
			longest = bits
	else:
		bfs(subtree[0], bits+'0')
		bfs(subtree[1], bits+'1')

bfs(huffman.value)

def optimal_compress(matrix):
	return compress_table[matrix]

def optimal_uncompress(bits):
	b = 1
	while b not in uncompress_table:
		b = b * 2 + int(bits[0])
		bits = bits[1:]
	return uncompress_table[b], bits

def conventional_zigzag():
	for d in range(15):
		if d % 2 == 0:
			if d < 7:
				i = d
				j = 0
			else:
				i = 7
				j = d-7
			di = -1
			dj = +1
		else:
			if d < 8:
				i = 0
				j = d
			else:
				i = d-7
				j = 7
			di = +1
			dj = -1
		while 0 <= i < 8 and 0 <= j < 8:
			yield (i,j)
			i += di
			j += dj

def my_zigzag():
	return iter([(0, 0), (1, 0), (0, 1), (0, 2), (1, 1), (2, 0), (3, 0), (2, 1), (1, 2), (0, 3), (2, 2), (3, 1), (4, 0), (1, 3), (3, 2), (4, 1), (5, 0), (2, 3), (0, 4), (1, 4), (3, 3), (4, 2), (5, 1), (2, 4), (0, 5), (6, 0), (3, 4), (4, 3), (1, 5), (5, 2), (0, 6), (2, 5), (6, 1), (1, 6), (5, 3), (1, 7), (4, 4), (7, 0), (2, 7), (0, 7), (2, 6), (6, 2), (3, 5), (5, 4), (4, 7), (7, 1), (3, 6), (6, 3), (3, 7), (7, 2), (4, 5), (6, 4), (7, 3), (5, 5), (4, 6), (5, 7), (7, 4), (6, 5), (7, 5), (5, 6), (6, 6), (6, 7), (7, 6), (7, 7)])

def expgolomb_compress(m):
	zz = [m[i*8+j]-127 for i,j in my_zigzag()]
	nnz = 0
	bits = ""
	zeros = ""
	assert nnz <= 64
	for x in zz:
		if x == 0:
			zeros += "0"
			continue
		bits += zeros
		zeros = ""
		if x < 0:
			sgn_bit = "0"
			x = -x
		else:
			sgn_bit = "1"
		assert bin(x).startswith("0b1"), x
		bits += "1" * (len(bin(x))-2) + "0"
		bits += sgn_bit
		bits += bin(x)[3:]
		nnz += 1

	bits = bin(0b1000000 + nnz)[-6:] + bits
	return bits

def expgolomb_uncompress(bits):
	try:
		nnz = int(bits[:6], 2); bits = bits[6:]
		m = bytearray(b"\x7f"*64)
		for i,j in my_zigzag():
			if nnz == 0 or bits == "":
				break
			if bits[0] == "0":
				m[i*8+j] = 0+BIAS
				bits = bits[1:]
				continue
			length = bits.index("0"); bits = bits[length+1:]
			sgn_bit = bits[0]; bits = bits[1:]
			x = int("1" + bits[:length-1], 2); bits = bits[length-1:]
			if sgn_bit == "0":
				x = -x
			m[i*8+j] = x+BIAS
			nnz -= 1
		return m, bits
	except:
		print(f"buba. {bits}, {m}")

def benchmark_algorithm(name, compress_fn, uncompress_fn):
	global beep
	print(f"Benchmarking {name}")
	compressed = ""
	longest_matrix = None
	longest_encoding = ""
	shortest_matrix = None
	shortest_encoding = "1"*1000
	for m in matrices:
		enc = compress_fn(m)
		compressed += enc

		if len(enc) > len(longest_encoding):
			longest_encoding = enc
			longest_matrix = m
		if len(enc) < len(shortest_encoding):
			shortest_encoding = enc
			shortest_matrix = m
	print(f"Total output size: {len(compressed)} bits ~ {len(compressed)/8192}kb")
	print(f"Average of {len(compressed) / len(matrices)} bits/matrix")
	#print(f"Longest encoding ({longest_encoding}) for matrix (count: {matrices.count(longest_matrix)}):")
	#print_tbl(longest_matrix, BIAS)
	#print(f"Shortest encoding ({shortest_encoding}) for matrix (count: {matrices.count(shortest_matrix)}):")
	#print_tbl(shortest_matrix, BIAS)

	cs = compress_fn(shortest_matrix)
	ucs = uncompress_fn(cs)
	#print(cs, ucs)
	assert(ucs == (shortest_matrix, ""))

	cl = compress_fn(longest_matrix)
	ucl = uncompress_fn(cl)	
	#print(cl, ucl)
	assert(ucl == (longest_matrix, ""))

#benchmark_algorithm("Optimal", optimal_compress, optimal_uncompress)
#benchmark_algorithm("Exp-Golomb", expgolomb_compress, expgolomb_uncompress)

#print_tbl(expgolomb_uncompress("0000011111111011111111")[0], 127)

fc = Counter()

for i, j in my_zigzag():
	if i == j == 0: continue
	fc.update(element_frequencies[i*8+j])
	
class Huffman2():
	def __init__(self, val, freq):
		self.val = val
		self.freq = freq
		self.leaf = True

	def __lt__(self, other):
		return self.freq < other.freq

	def __add__(self, other):
		c = Huffman2((self.val, other.val), self.freq+other.freq)
		c.leaf = False
		return c

	def __repr__(self):
		return f"<Huffman2 freq={self.freq}" + (f" {self.val}" if self.leaf else "") + ">"

for i in range(-127, 129):
	if i not in fc:
		fc[i] += 1

fch = [Huffman2(b,a) for b, a in fc.most_common(256)]
heapify(fch)

while len(fch) > 1:
	b = heappop(fch)
	a = heappop(fch)
	heappush(fch, a+b)

assert len(fch) == 1
fch = heappop(fch)

a_enc = {}
a_dec = {}

totalbits = 0
def bbfs(n, bs='', i=1):
	global totalbits
	if type(n) == int:
		#print(str(n+BIAS).rjust(3, '0'), bs)
		totalbits += element_frequencies[0][n] * len(bs)
		a_enc[n] = bs
		a_dec[bs] = n
	else:
		bbfs(n[0], bs+'0', i*2)
		bbfs(n[1], bs+'1', i*2+1)

bbfs(fch.val)

def encode_element(x):
	return a_enc[x]

def decode_element(bits):
	for k in range(len(bits)):
		B = bits[:k+1]
		if B in a_dec:
			return a_dec[B], bits[k+1:]

def a1_compress(m):
	zz = [m[i*8+j]-BIAS for i,j in my_zigzag()]
	nnz = sum(q != 0 for q in zz[1:])
	bits = bin(0b1000000 + nnz)[-6:] + bin(0b100000000 + zz[0])[-8:]
	assert nnz <= 63
	for x in zz[1:]:
		if nnz == 0: break
		bits += encode_element(x)
		if x != 0: nnz -= 1
	return bits

def a1_uncompress(bits):
	try:
		nnz = int(bits[:6], 2); bits = bits[6:]
		m = bytearray(b"\x7f"*64)
		tl = int(bits[:8], 2); bits = bits[8:]
		if tl >= 0x80: tl -= 0x100
		m[0] = tl+BIAS
		for i,j in my_zigzag():
			if i == j == 0: continue
			if nnz == 0 or bits == "":
				break

			x, bits = decode_element(bits)
			m[i*8+j] = x + BIAS 
			if x != 0:
				nnz -= 1 
		#print("a1_uncompress:")
		#print_tbl(m, BIAS)
		#print(bits)
		return m, bits
	except Exception as e:
		print(f"buba. {e}, {bits}, {m}")

#benchmark_algorithm("a1", a1_compress, a1_uncompress)


def a2_compress(m):
	bits = a1_compress(m)
	num = int(bits[:6], 2) + 1
	B = bin(num)[2:]
	enc = "0" * len(B) + B
	return enc + bits[6:]

def a2_uncompress(bits):
	L = bits.index("1")
	num = int(bits[L:2*L], 2)
	bits = bits[2*L:]
	bits = bin(0b1000000 + num)[-6:] + bits
	return a1_uncompress(bits)

#benchmark_algorithm("a2", a2_compress, a2_uncompress)

nonzero_sum_by_my_zigzag = [ nonzero_sum[i*8+j] for i,j in my_zigzag() ]

print(nonzero_sum_by_my_zigzag)

def zero_count(left, right):
	N = len(matrices)
	return sum(N-nonzero_sum_by_my_zigzag[i] for i in range(left, right))

def find_approx_halfway_point(left, right):
	#return (left+right)//2
	if left == right-1: return left
	best_diff = 99999999999999
	best_i = None
	for i in range(left, right):
		zl = zero_count(left, i)
		zr = zero_count(i+1, right)
		if abs(zl-zr) < best_diff:
			best_diff = abs(zl-zr)
			best_i = i
	return best_i

q = [None] * 1024
def D(i, left, right):
	q[i] = find_approx_halfway_point(left, right)
	print(i, left, right, q[i])
	if left >= right: return
	D(i*2, left, q[i])
	D(i*2+1, q[i]+1, right)

D(1, 1, 64)

#print(q)
#q = [None, 36, 22, 51, 14, 30, 44, 58, 9, 19, 27, 34, 41, 48, 55, 62, 6, 12, 17, 21, 25, 29, 33, 35, 39, 43, 47, 50, 54, 57, 61, 63, 4, 8, 11, 13, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 35, 36, 38, 40, 42, 44, 46, 48, 49, 51, 53, 55, 56, 58, 60, 62, 63, 64, 3, 5, 7, 9, 10, 12, 13, 14, 15, 17, 18, 19, 20, 21, None, None, 23, 25, 26, 27, 28, 29, None, None, 31, 33, None, None, None, None, None, None, 37, 39, 40, 41, 42, 43, None, None, 45, 47, None, None, 49, 50, None, None, 52, 54, None, None, 56, 57, None, None, 59, 61, None, None, None, None, None, None, 2, 4, 5, 6, 7, 8, None, None, 10, 11, None, None, None, None, None, None, 15, 16, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 23, 24, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 31, 32, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 37, 38, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 45, 46, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 52, 53, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 59, 60, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 1, 3]
LEAST_DIVISION = 1
def a4_compress_recurse(data, i, left, right):
	if all(q == 0 for q in data[left:right]): return "0"
	if right-left <= LEAST_DIVISION:
		return ''.join(encode_element(data[i]) for i in range(left, right))
	return "1" + a4_compress_recurse(data, i*2, left, q[i]) + a4_compress_recurse(data, i*2+1, q[i], right)

def a4_compress(m):
	zz = [m[i*8+j]-BIAS for i,j in my_zigzag()]
	return bin(0b100000000 + zz[0])[-8:] + a4_compress_recurse(zz, 1, 1, 64)

def a4_uncompress_recurse(bits, i, left, right):
	#print(f"a4_uncompress_recurse({bits[:20]}, {i}, {left}, {right})")
	if bits[0] == "0": return [0]*(right-left), bits[1:]
	if right-left <= LEAST_DIVISION:
		elems = []
		for i in range(left, right):
			x, bits = decode_element(bits)
			elems.append(x)
		return elems, bits
	if left == right: raise ValueError(f'left={left} right={right}')
	bits = bits[1:]
	leftdata, bits = a4_uncompress_recurse(bits, i*2, left, q[i])
	rightdata, bits = a4_uncompress_recurse(bits, i*2+1, q[i], right)
	return leftdata+rightdata, bits

def a4_uncompress(bits):
	topleft = int(bits[:8], 2); bits = bits[8:]
	zz, bits = a4_uncompress_recurse(bits, 1, 1, 64)
	zz = [topleft] + zz
	m = bytearray(64)
	for i, j in my_zigzag():
		m[i*8+j] = zz.pop(0) + BIAS
	return m, bits

for i in range(1, 64):
	LEAST_DIVISION = i
	try:
		benchmark_algorithm(f"Partitions {i}", a4_compress, a4_uncompress)
	except:
		print("FAIL")
		pass
