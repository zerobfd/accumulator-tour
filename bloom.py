# Bloom filters are pretty simple to implement, even though it's a bit hard to
# wrap your head around.

from md5 import md5

# We need some more hash functions, so let's get creative

def repeat_hash(num, val):
    output = val
    for i in range(num):
        output = md5(output)
    return output

def md15(val):
    return repeat_hash(15, val)

def md007(val):
    return repeat_hash(7, val)

def mdlidge(val):
    return repeat_hash(54, val)

hs = [md5, md15, md007, mdlidge]

# We want to turn the hash into an int mod some number, so
# hti = Hash To Index
def hti(h, modulus):
    return int(h, 16) % modulus

# Alright, now we need some buckets. Let's start with 10000.

def new_bloom(num_buckets):
    return [0 for _ in range(num_buckets)] 

buckets = new_bloom(10000)

# Inserting into the filter is hashing the value and setting the bits to one

def bloom_insert(val, bloom):
    for h in hs:
        index = hti(h(val), len(bloom))
        bloom[index] = 1

# Checking whether the filter contains the value of hashing the value and
# seeing if the bits are already set to 1

def bloom_contains(val, bloom):
    for h in hs:
        index = hti(h(val), len(bloom))
        if bloom[index] == 0:
            return False
    return True

# Let's stick some data in there!

if __name__ == "__main__":
    homer_iliad = """ARMA virumque cano, Troiae qui primus ab oris
    Italiam, fato profugus, Laviniaque venit
    litora, multum ille et terris iactatus et alto
    vi superum saevae memorem Iunonis ob iram;
    multa quoque et bello passus, dum conderet urbem,
    inferretque deos Latio, genus unde Latinum,
    Albanique patres, atque altae moenia Romae.
    Musa, mihi causas memora, quo numine laeso,
    quidve dolens, regina deum tot volvere casus
    insignem pietate virum, tot adire labores
    impulerit. Tantaene animis caelestibus irae?"""

    for word in homer_iliad.split():
        bloom_insert(word, buckets)

# So let's see if we can find the items we put in there, or some that we didn't

    print(f"With 10000 buckets")
    for word in "ARMA animis meatball potato Tantaene singing".split():
        if bloom_contains(word, buckets):
            print(f"Found {word}!")
        else:
            print(f"Didn't find {word}!")

    print()
    print()

# Cool, that seemed to work out fine! What if we had less buckets?

    buckets = new_bloom(90)

    c_s_lewis = """One, two! One, two! And through and through
    The vorpal blade went snicker-snack!
    He left it dead, and with its head
    He went galumphing back."""

    print(f"With 90 buckets")
    for word in c_s_lewis.split():
        bloom_insert(word, buckets)

    for word in "One, vorpal blade of menacing barrows".split():
        if bloom_contains(word, buckets):
            print(f"Found {word}!")
        else:
            print(f"Didn't find {word}!")

    print()
    print()

# Still no errors. That's 153 characters worth of data in 90 bits, which is
# pretty good. However, if we try once more with 80:

    buckets = new_bloom(80)

    print(f"With 80 buckets")
    for word in c_s_lewis.split():
        bloom_insert(word, buckets)

    for word in "One, vorpal blade of menacing barrows".split():
        if bloom_contains(word, buckets):
            print(f"Found {word}!")
        else:
            print(f"Didn't find {word}!")

    print()
    print()

    # Ok, we definitely didn't put "menacing" in there, so what gives?

    print("menacing", sorted([hti(f("menacing"), 80) for f in hs]))
    print("two!", sorted([hti(f("two!"), 80) for f in hs]))
    print("it", sorted([hti(f("it"), 80) for f in hs]))
    print("went", sorted([hti(f("went"), 80) for f in hs]))

    # We can see that mod 80 these words hash to:
    # menacing [5, 40, 45, 78]
    # two! [5, 6, 37, 78]
    # it [5, 16, 40, 55]
    # went [21, 38, 40, 45]
    # which means the combination of "two!", "it", and "went" happen to hit all of
    # the bits that "menacing" also hits. This is why Bloom filters sometimes give
    # false positives, and we have to adjust the number of buckets/hash functions.
