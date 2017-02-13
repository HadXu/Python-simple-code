import random,sys,os,rabinMiller
from rabinMiller import gcd,findModInverse

def generateKey(keysize=1024):
	#############################
	p = rabinMiller.generateLargePrime(keysize)
	q = rabinMiller.generateLargePrime(keysize)
	n = p*q
	################################
	while True:
		e = random.randrange(2**(keysize-1),2**keysize)
		if gcd(e,(p-1)*(q-1)) == 1:
			break
	################################
	d = findModInverse(e,(p-1)*(q-1))
	################################
	public_key = (n,e)
	private_key = (n,d)
	return (public_key,private_key)

if __name__ == '__main__':
	message = 'hello'
	"""plaintext^e mod n"""
	public_key, private_key = generateKey(keysize=2048)
	n,e = public_key
	n,d = private_key
	encrytext = [pow(ord(x),e,n) for x in message]
	print(encrytext)
	dencrypt = [chr(pow(x,d,n)) for x in encrytext]
	dencrypt = ''.join(dencrypt)
	print(dencrypt)

