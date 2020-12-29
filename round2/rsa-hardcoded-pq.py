
# pow(2, e, n) == 50154912289039335014669339773308393642658123228965873078737860474494117389068
# pow(3, e, n) == 74177167678866806519929337366689313939300015489238864541679630476008627210599
# pow(4, e, n) == 34176590322694690833975364940063423615063159848675783675025873390206977645476
# pow(6, e, n) == 69732835711852253044075185248502970714729629373386336194927784886349053828079
# pow(9, e, n) == 51250457553422544471678089837959016263959958280836142992507348470497811391846


n = 76200708443433250012501342992033571586971760218934756930058661627867825188509

def gcd(a, b):
	while b != 0:
		a, b = b, a % b
	return a

assert gcd(10, 20) == 10
assert gcd(15, 4) == 1
assert gcd(15, 35) == 5

e = 65537
p=232086664036792751646261018215123451301
q=328328681700354546732404725320581286809
y=71511896681324833458361392885184344933333159830863878600189212073777582178173

phi = (p-1)*(q-1)//gcd(p-1, q-1)

def extended_gcd(aa, bb):
    lastremainder, remainder = abs(aa), abs(bb)
    x, lastx, y, lasty = 0, 1, 1, 0
    while remainder:
        lastremainder, (quotient, remainder) = remainder, divmod(lastremainder, remainder)
        x, lastx = lastx - quotient*x, x
        y, lasty = lasty - quotient*y, y
    return lastremainder, lastx * (-1 if aa < 0 else 1), lasty * (-1 if bb < 0 else 1)
 
def modinv(a, m):
	g, x, y = extended_gcd(a, m)
	if g != 1:
		raise ValueError
	return x % m

d = modinv(e, phi)

print(pow(y, d, n))