import itertools
from collections import defaultdict

class DihedralElement:
	def __init__(self, ac, uc, m):
		assert uc in [0,1]
		self.ac = ac
		self.uc = uc
		self.m = m
		self.M = 2**(m-1)

	def __mul__(self, other):
		"""
		a^i   * a^j   = a^(i+j)
		a^i*u * a^j   = a^(i-j)*u
		a^i   * a^j*u = a^(i+j)*u
		a^i*u * a^j*u = a^(i-j)
		"""
		assert self.m == other.m
		if self.uc == 1:
			return DihedralElement((self.ac - other.ac) % self.M, 1-other.uc, self.m)
		else:
			return DihedralElement((self.ac + other.ac) % self.M, other.uc, self.m)

	def __pow__(self, power):
		assert type(power) == int
		base = self
		res = DihedralElement(0, 0, self.m)
		while power:
			if power % 2 == 1:
				res = res * base
			base *= base
			power //= 2
		return res

	def inv(self):
		if self.uc == 1:
			return DihedralElement(self.ac, 1, self.m)
		else:
			return DihedralElement(-self.ac % self.M, 0, self.m)

	def __repr__(self):
		return f'a^{self.ac}*u^{self.uc}(%{self.m})'

	def __eq__(self, other):
		return self.ac == other.ac and self.uc == other.uc and self.m == other.m

	def __hash__(self):
		return self.ac * 2 + self.uc

def theta(r1, r2, c1, c2, q1, q2, b1, b2):
	def morphism(a):
		assert type(a) == DihedralElement
		if a.uc == 0:
			if a.ac < 2**(a.m-2):
				return DihedralElement(r1*a.ac + c1, 0, a.m)
			else:
				return DihedralElement(r2*a.ac + c2, 1, a.m)
		else:
			if a.ac < 2**(a.m-2):
				return DihedralElement(q1*a.ac + b1, 1, a.m)
			else:
				return DihedralElement(q2*a.ac + b2, 0, a.m)
	return morphism

def is_orthomorphism(theta, m):
	M = 2**(m-1)
	input_set = { DihedralElement(ac, uc, m) for ac in range(M) for uc in [0,1] }
	output_set = { a.inv() * theta(a) for a in input_set }
	return input_set == output_set # Check if it's a permutation

m = 4
a = DihedralElement(1, 0, m)
u = DihedralElement(0, 1, m)

sal = DihedralElement(3, 1, m)

print(a)
print(u)
print(a*u)
print(u*a)
print(a**(2**(m-1)))
print("")
print(sal)
print(sal.inv())
print(sal * sal.inv())
print(sal.inv() * sal)
print("")
print(a**3, a**5, a**3 * a**5)

print("identity theta test")
T = theta(1, 1, 0, 0, 1, 1, 0, 0)
for ac in range(8):
	for uc in [0,1]:
		x = DihedralElement(ac, uc, m)
		y = T(x)
		print(x, y)

assert DihedralElement(1, 0, m) == DihedralElement(1, 0, m)
assert DihedralElement(1, 0, m)**(2**(m-1)) == DihedralElement(0, 0, m)

for m in range(4, 8):
	i = 0
	cate = 0
	values = [defaultdict(int) for _ in range(4)]
	#for r1, r2, q1, q2, c1, c2, b1, b2 in itertools.product(range(2**(m-1)), repeat=8):
	for r, q, c, b in itertools.product(range(2**(m-1)), repeat=4):
		r1 = r2 = r
		q1 = q2 = q
		c1 = c2 = c
		b1 = b2 = b
		i += 1
		if i % 100000 == 0:
			print(i, i / 16**(m-1) * 100)
		theta_i = theta(r1, r2, c1, c2, q1, q2, b1, b2)
		if is_orthomorphism(theta_i, m):
			cate += 1
			#print(r1, r2, c1, c2, q1, q2, b1, b2)
			values[0][r] += 1
			values[1][c] += 1
			values[2][q] += 1
			values[3][b] += 1

	print(f'm = {m}. count = {cate}')

	for i in range(4):
		print('rcqb'[i], end=': ')
		for j in range(2**(m-1)):
			print(values[i][j], end='\t')
		print()



"""

def theta(a):
	if a.uc == 0:
		if a.ac < 2**(a.m-2):
			return DihedralElement((a.ac*(r1-1) + c1) % a.M, 0, a.m)
		else:
			return DihedralElement((a.ac*(r2-1) + c2) % a.M, 1, a.m)
	else:
		if a.ac < 2**(a.m-2):
			return DihedralElement((a.ac*(1-q1) - b1) % a.M, 0, a.m)
		else:
			return DihedralElement((a.ac*(1-q2) - b2) % a.M, 1, a.m)

r1 != 1
r2 != 1
q1 != 1
q2 != 1


r1-1 = 2, c1 par => primul return da doar chestii pare
1-q1 = 2 => al treilea return TREBUIE sa dea doar chestii impare

cand r1-1 = 2,
1-q1 = 2 sau -2

0 1 2 3 4 5 6 7
X Y X Y X Y X Y

vrem sa evitam r1-1, r2-1, 1-q1, 1-q2 divizibile cu 2,
insa e ok daca sunt exact -2 sau 2, pentru ca putem seta
b, c de paritati diferite, astfel incat r*x+c si q*x+b sa
se completeze una pe cealalta.

Impartim problema in 2, (r1,c1,q1,b1) si (r2,c2,q2,b2), ca sunt independente.
Au aceeasi cardinalitate, deci numarul de solutii finale e numarul de solutii a uneia la patrat.


r,c,q,b ca sa fie mai scurt


r,q nu sunt de forma 4k+1


grupu: 0 1 2 3 4 5 6 7 N=8
jum1:  1   2   3   4
jum2:    1   2   3   4

gcd(r, 2**(m-2)) = 1
gcd(q, 2**(m-2)) = 1

r, q pot fi pare, dar nu multiplu de 4, deci 4k+2

0 1 2 3 4 5 6 7 8 9 a b c d e f
r1  r2  r3  r4  r5  r6  r7  r8
  q1  q5  q2  q6  q3  q7  q4  q8       

(2**(m-3))**2 perechi (r,q) de forma (4k+2,4l+2)
(2**(m-1)) valori pentru b (orice valoare)
(2**(m-2)) valori pentru c (paritate inversa lui b, deci doar jumate)

nr cazuri pt 4k+2 = 2**(4*m-9)

--------------------------------------

r = 2k + 1
r genereaza tot grupu
q = 2l + 1
q genereaza tot grupu
alegem b, c astfel incat "unde termina r cu generatul, acolo porneste q"


cand r, q impare, trebuie sa fie si egale in modul.

ex:
r = 3
q = r; Q = -r
0 1 2 3 4 5 6 7 8 9 a b c d e f
r1  r7r2  r8r3    r4    r5    r6
  q4    q5    q6q1  q7q2  q8q3
  Q5    Q4    Q3Q8  Q2Q7  Q1Q6

Pentru orice r impar (2**(m-2)), avem doua posibilitati pentru q (r, -r).
Putem permuta fiecare din alea circular, deci inmultim cu
2**(m-1).

2**(m-2) * 2 * 2**(m-1) = 2**(2*m-2)

nr cazuri pentru 2l+1 = 2**(2*m-2)

--------------------------------------

nr cazuri pt 4k+2 = 2**(4*m-9)
nr cazuri pentru 2l+1 = 2**(2*m-2)
nr cazuri totale = 2**(4*m-9) + 2**(2*m-2)
                 = 2**(2*m-2) * (2**(2*m-7) + 1)


ASTA E PENTRU FIECARE JUMATATE DIN PROBLEMA (r1,c1,q1,b1), (r2,c2,q2,b2)

Numarul de ortomorfisme = aia la patrat
                        = (2**(2*m-2) * (2**(2*m-7) + 1)) ** 2
                        = 2**(4*m-4) * (2**(4*m-14) + 2**(2*m-6) + 1)
                        = 16**(m-1) * (4**(2*m-7) + 4**(m-3) + 1)

"""