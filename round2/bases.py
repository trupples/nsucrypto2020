import sys, math, itertools

def comb(n, k):
	return math.factorial(n) // (math.factorial(k) * math.factorial(n-k))

assert len(sys.argv) == 3, f"Usage: {sys.argv[0]} s d"

s = int(sys.argv[1])
d = int(sys.argv[2])

assert s >= d > 1

r = sum( comb(s, i) for i in range(d+1) )

print(f"s = {s} generating vectors")
print(f"d = {d} AND inputs")
print(f"r = {r} bits")

Fr = list(range(1, 2**r-1))
lfr = len(Fr)

def fmt(x):
	elems = [f"({bin(2**r + q)[-r:]})" for q in sorted(x)]
	return "{" + ", ".join(elems) + "}"

def is_basis(F, r):
	visited = {0}
	for x in F:
		newvis = set()
		for b in visited:
			bb = b ^ x
			if bb in visited or bb in newvis: return False
			newvis.add(bb)
		visited.update(newvis)
	return True

def orderless(F):
	return tuple(sorted( tuple( (f>>i)&1 for f in F ) for i in range(r) ))

equivalence_classes = set()

for F in itertools.combinations(Fr, s):
	fo = orderless(F)
	if fo in equivalence_classes: continue
	equivalence_classes.add(fo)

	B = []
	for i in range(0, d+1):
		for bois in itertools.combinations(F, i):
			b = 2**r-1
			for boi in bois:
				b &= boi
			B.append(b)
			if b == 0:
				break
		if B[-1] == 0:
			break
	else:
		if is_basis(B, r):
			print(f'F = {fmt(F)}  =>  B = {fmt(B)}')
