"""
Dragomir Ioan - trupples
NSU Crypto 2020 first round, problem 4 "RGB"

I initially tried solving it algebraically by considering each query as a
matrix multiplication mod 324:

R = ( 1   18 )
    ( 18  -1 )

G = ( 17  6  )
    ( -6  17 )

B = ( -10 -15 )
    ( 15  -10 )

With the goal of getting from (20,20) to (0,0) mod 324.

A very nice property was that B*G = G*B, so they commute, so you can rearrange
any sequence of consecutive B and G queries to something like B^b * G^g, b,g
natural numbers.

Unfortunately, R does not have this property. If it had had it, it would have
been possible to rearrange the entire sequence of moves to this form:

R^r * G^g * B^b * (20,20)  , with r,g,b natural numbers

Oh well, i was probably on the right track, but I figured I could just make a
directed graph which describes how each element in Z_324^2 can be transformed
by the 3 matrices, and then show there is no path from (20,20) to (0,0).

I am not storing the graph structure, as from each (a,b) node we can easily
compute its 3 direct successors. I am using a basic BFS to get a set of all
possible (a,b) values.

"""

def R(a,b): return (a+18*b) % 324, (18*a-b) % 324
def G(a,b): return (17*a+6*b) % 324, (-6*a+17*b) % 324
def B(a,b): return (-10*a-15*b) % 324, (15*a-10*b) % 324

visited = set()
to_visit = [(20,20)]

def we_can_get_to(ab):
	if ab not in visited:
		to_visit.append(ab)
		visited.add(ab)

while to_visit:
	a, b = to_visit.pop(0)

	we_can_get_to(R(a, b))
	we_can_get_to(G(a, b))
	we_can_get_to(B(a, b))

assert (0,0) not in visited, "(0,0) should not be accessible."
assert (20,20) in visited, "Even though we didn't add it at the start, we should eventually loop back to (20,20)."

print(visited)
