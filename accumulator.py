# A simple crypto accumulator. There are a lot of assumptions I made to
# simplify the implementation:
# 1. This only works for interactive scenarios (i.e. we have to ask
# the server to sign something)
# 2. The server has to be trusted
# 3. The server has to have perfect knowledge of the possible universe of
# values. This is what makes it tenable to use a Bloom filter, since we need
# to guarantee no false positives for our scenario.

from rsa import verify, sign
from blind import blind, unblind, blind_sign
from bloom import new_bloom, bloom_insert, bloom_contains

# This is just for example purpose and isn't used in the algorithm.
# Please don't use random for cryptographic purposes.
from random import randint, sample

# For a short overview of the process, here's what needs to happen
# 1. Server builds the accumulator
# 2. Server distributes the accumulator
# 3. Client wants to check membership of an element
# 4. Client prepares element for blind signing
# 5. Server blind-signs the element
# 6. Client recovers signatures and checks to see if they are in the filter
# There are tons of other practical steps we could take but this serves
# well enough.
# Also, as a reminder of who can do what:
# Server: access to raw data, can sign()
# Client: can verify(), blind(), and unblind()

# Step 1: Server side, build the accumulator
# 100 names generated using http://random-name-generator.info

# Perfect knowledge here means that these are all of the possible elements that
# could ever be a member. In other words: if someone not on this list gets
# checked, we can't guarantee no false positives. This is a consequence of my
# simple implementation and not of accumulators in general.
all_people = ["Noah Porter", "Lynn Drake", "Freda Rice", "Lana Carr",
"Lawrence Harmon", "Raymond Sparks", "Hattie Gordon", "Ronald Alvarado",
"Abel Quinn", "Bill Murray", "Daisy Banks", "Kayla Perkins", "Gilberto Hawkins",
"Mildred Luna", "Tabitha Bridges", "Mike Vaughn", "Kirk Myers", "Javier Park",
"Kyle Carson", "Juanita Poole", "Lionel Harrison", "Ricky Mack",
"Melissa Chavez", "Rhonda Johnston", "Victor Knight", "Christopher Cox",
"Al Barnes", "Jerome Wong", "Veronica Townsend", "Armando Owens",
"Jesus Palmer", "Wilson Waters", "Lorraine Lawson", "Ronnie Murphy",
"Rita Hampton", "Jennifer Jones", "Emanuel Mathis", "Kerry Cannon",
"Jessie Bradley", "Stephanie Hodges", "Ken Moss", "Yvonne Pittman", "Ida Lane",
"Brad Bowen", "Patti Blair", "Alberta Fields", "Jeannie Martinez",
"Ernestine Cunningham", "Claudia French", "Russell Reyes", "Allan Garcia",
"Earl Jordan", "Arnold Duncan", "Jon Peterson", "Winifred Lucas",
"Dominick Boyd", "Julius Floyd", "Keith Price", "Jonathan Hopkins",
"Cynthia Hines", "Rene Mullins", "Lucy Sanders", "Lori Black", "Elsa Lindsey",
"Patrick Ryan", "Damon Rodriguez", "Diana Griffin", "Vernon Summers",
"Vanessa Ingram", "Marcus Lewis", "Holly Thompson", "Irving Estrada",
"Joy Hayes", "Dana Walsh", "Gilbert Reed", "Sherri Patterson", "Katherine Nguyen",
"Beatrice Cohen", "Guadalupe Robinson", "Jake Hubbard", "Ginger Haynes",
"Danielle West", "Judith Fleming", "Margie Daniel", "Eddie Collier",
"Lindsay Riley", "Clay Terry", "Tami Willis", "Maxine Harvey", "Monica Robertson",
"Teri Miles", "Amelia Andrews", "Sheryl Parks", "Anthony Cook", "Willis Brock",
"Billie Bass", "Steven Patrick", "Clifford Steele", "Myron Burton",
"Blanca Gill"]

# Split them into members and non members
num_members = randint(35, 65)
members = set(sample(all_people, k=num_members))
non_members = set(all_people) - members

# Number of buckets isn't too important
accumulator = new_bloom(10000)

for member in members:
    bloom_insert(sign(member), accumulator)

# Ensure that we won't get false positives
for non_member in non_members:
    assert not bloom_contains(sign(non_member), accumulator)

# 2. Server distributes accumulator
pass

# 3. Client wants to check membership of an element

# Let's choose 4 people at random
elements = sample(all_people, k=4)

# 4. Client prepares element for blind signing
blinded_elements = [blind(x) for x in elements]

# 5. Server blind-signs the element
blind_signatures = [blind_sign(x) for x in blinded_elements]

# 6. Client recovers signatures and checks to see if they are in the filter
signatures = [unblind(x) for x in blind_signatures]

in_accumulator = [bloom_contains(x, accumulator) for x in signatures]

# Let's verify that things worked!
if __name__ == "__main__":

# First let's see whether our elements are really members or not
    element_status = [(name in members) for name in elements]

# To print nicely
    element_status = [str(x) for x in element_status]
    in_accumulator = [str(x) for x in in_accumulator]

# Now we can print a table to compare
print(f"{'Name':<30}\t{'is_member':<10}\t{'in_accumulator'}")
for name, real_status, accum_status in zip(elements, element_status, in_accumulator):
    print(f"{name:<30}\t{real_status:<10}\t{accum_status}")
# Name                            is_member       in_accumulator
# Myron Burton                    False           False
# Lana Carr                       True            True
# Wilson Waters                   True            True
# Cynthia Hines                   False           False
