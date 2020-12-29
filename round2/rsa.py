import subprocess, re
from fractions import gcd
from Crypto.Util.number import inverse

Em = 71511896681324833458361392885184344933333159830863878600189212073777582178173
E2 = 50154912289039335014669339773308393642658123228965873078737860474494117389068
E3 = 74177167678866806519929337366689313939300015489238864541679630476008627210599
E4 = 34176590322694690833975364940063423615063159848675783675025873390206977645476
E6 = 69732835711852253044075185248502970714729629373386336194927784886349053828079

n = gcd(E2*E2 - E4, E2*E3 - E6)
print(f"n = {n}")

e = 65537
assert pow(2, e, n) == E2

yafu_outp = subprocess.check_output(["./yafu-x64.exe", f"factor({n})"])
p, q = [int(x) for x in re.findall(r'P\d+ = (\d+)', yafu_outp.decode())]

print(f"p = {p}")
print(f"q = {q}")

assert p*q == n

L = (p-1)*(q-1)//gcd(p-1, q-1)
d = inverse(e, L)
print(f"d = {d}")

m = pow(Em, d, n)
print(f"m = {m}")