# Contents
 * [Introduction](#introduction)
 * [How to use](#how-to-use-this-tour)
 * [Background](#background)
   * [Math](#math)
   * [What can crypto do](#what-can-crypto-do)
   * [Symmetry](#symmetry)
 * [Motivations and Implementations](#motivations-and-implementations)
   * [Prove something is unchanged (hashes)](#prove-something-is-unchanged)
     * [md5 implementation](md5.py)
   * [Prove I was the one who sent it (HMAC, signatures)](#prove-i-was-the-one-who-sent-it)
     * [hmac implementation](hmac.py)
     * [key gen script](gen_key)
     * [annotated private key](parsed_private_key.txt)
     * [rsa signature implementation](rsa.py)
   * [Prove a lot of things are unchanged (Merkle tree)](#prove-a-lot-of-things-are-unchanged)
     * [merkle tree implementation](merkle.py)
   * [Check to see if something is in a set (Bloom filter)](#check-to-see-if-something-is-in-a-set)
     * [bloom filter implementation](bloom.py)
   * [Prove something is unchanged without knowing what it is (blind signatures)](#prove-something-is-unchanged-without-knowing-what-it-is)
     * [blind signature implementation](blind.py)
   * [Putting it together (accumulators)](#putting-it-together)
     * [accumulator implementation](accumulator.py)
 * [Afterword](#afterword)

# Introduction

This is an informal tour of cryptographic constructs up until accumulators,
along with motivations and implementations for each.

I have two main goals. One is to start from (relatively) familiar concepts
like hashes and signatures, and work up to more complex constructions (like
the titular accumulator.)

The second is to try and de-mystify cryptography a bit. Hashes for many (myself
included) seem like magic, and many other crypto functions are hidden behind
very scary and cryptic warnings.  While it still is very much a horrible idea
to implement your own crypto, that doesn't mean that there's anything magic
about it, and you can build up fair amount from scratch to learn the concepts.

Hopefully after reading this, some old concepts should seem more approachable,
and the motivations for creating some of these idea might help one use crypto
tools a bit better. (Or, you just get interested in cryptography, since it's
pretty cool.)

**Mandatory warning:**
Everything discussed here is conceptually correct but practically broken.
Please don't use anything here for any reason other than education.

# How to use this tour

If you want to, you can just read this markdown file and ignore anything else.
That's perfectly fine, and hopefully it will still be interesting. I've also
included implementations of all of the concepts to help make some of the
practical bits more concrete, and to show what's going on behind all of the
scary crypto libraries--other than RSA key generation, it's all plain python.
And really we take all of the information out of the key manually, so it's
basically using openssl as a fancy random number generator.

The files will be mentioned near the end of the relevant sections, but it
should also be pretty clear from the filename and comments in the file what's
going on.

# Background

In order to get started, there are a few concepts that need to be introduced.
If you're the kind of person who just takes what strangers say on the Internet
as truth you can skip the entire section. Otherwise it's hopefully enough to
give a casual introduction and give you the key words to search around and find
sources if you want.

## Math

There's a ton of math in cryptography. I'm going to skip over most of it here.
We'll use some basic probability, but other than that it's mostly knowing what
things are. We need to know what a prime number is and what
logarithms/exponents do.

## What can crypto do

I think the general idea is that cryptography is used to encrypt and decrypt
things, but there are a lot of other uses too. You can use it to prove your
identity, prove that data hasn't been tampered with, and even make agreements
that are impossible to back out of.

Unless otherwise noted, all of the concepts here will only deal with proving
knowledge and not encryption/decryption.

## Symmetry

The final concept we need is a pretty easy one. There are two kinds of crypto:
symmetric and asymmetric.

Symmetric cryptography is where there is one key required to do everything.
Most real world locks work like this: if I want you and I to be the only ones
to be able to open a box, I get a lock with two of the exact same key, give one
key to you, and we're done.

Asymmetric cryptography is where there are two keys, and one "does" the
operation while the other "undoes" it. A useful mental model to me is to
imagine that there is a lock that can be locked with one key but can only be
unlocked with another key.  If I want to give anyone the ability to send me a
package and be sure that no one can mess with it, I can make as many copies of
the "locking" key that I want and leave them everywhere. Anyone can find one,
use it to lock a box, and mail me the box. I have the only copy of the
"unlocking" key, and so everyone can rest assured that I'm the only one who can
open the box.

# Motivations and Implementations

For the meat of this document, the format will be:

1. I present a strawman motivation for why a particular construct might be useful
1. I describe the construct and why it solves the problem
1. A file in this repo will have an annotated implementation

None of the implementations should be used except for learning purposes: I
don't guarantee them to be correct in any edge case. I *do* guarantee that
using them in practice will make it very easy for someone to break whatever
crypto that you're doing.

## Prove something is unchanged

The first thing we'll examine is this: how can I prove that something hasn't
changed since some point? There are several easy examples for why this might
be useful.

I might want to send my friend a message, but because of some network or
processing error it might change before it reaches my friend. It would be
convenient to have an easy way for that friend to check that what they received
was actually what I originally wrote.

Another example would be fair betting. If I wanted to make a bet without
letting anyone know what the bet was, it's difficult to see a way to do that.
It would be convenient if I could write something down *now* that doesn't look
like my choice at all, but *later* could be used to prove what choice I
actually made.

The method that we can actually do this with is called a **hash function**. A
hash function is a function that takes in some piece of information and spits
out a random looking bunch of gibberish called a **hash**, but it spits out the
same hash every time it gets the same input. Since it looks like random data,
you can't look at the output and see what the input was. But, if you have some
data and a hash, you can very easily verify that the hash function will
generate the hash when given the data as input.

For an example, we can use SHA256, a well-known hash function. This sentence

> A hash is a one way function.

hashes to

> c4c3f1368bd5310998ceb9b5a7ec7538928913284dcac01d46d13b51488a2f68

in SHA256. You can verify it: it's easy to find a web page online that will
generate hashes, and you can copy and paste the sentence and watch it spit out
the same hash.

In our example motivations, if the above sentence was the message to my friend,
I could send the message along with the hash at the end. After receiving the
message, my friend could hash it and compare it to the hash I sent. If they're
the same, they can be confident that the message was not changed. Or, if I
wanted to make a bet involving that sentence, I could just write down the hash
before the event.  Afterwards, I could prove what my guess actually was by
revealing my guess and then verifying that it hashes to the hash above.

Actually making a good hash function is difficult. We want it to have several
properties:

 * The same input gives the same output every time
 * It's quick to compute
 * It should be hard to look at the output and guess the input
 * It should be hard to find two different inputs that output the same hash
 * The output should depend on every piece of the input--changing any bit
 of the input should change all bits of the output with ~50% probability

To illustrate this, I picked the MD5 function to look at. It's a bit older and
has been thoroughly broken so should never be used for any cryptographic
purpose, but it's (relatively) simple and it's easy to see what pieces of the
algorithm serve what function.

There is an RFC for MD5 which I used for the implementation:
https://www.ietf.org/rfc/rfc1321.txt

See md5.py for the annotated code. You can use it via the CLI by:
`python3 md5.py <string>` where `<string>` is the data you want to
hash.

## Prove I was the one who sent it

A hash is useful if you want to know if something is unchanged, but there are
some other scenarios where it doesn't work as well. Hashes will help detect
corruption when sending messages, but what if there were someone sitting in the
middle of you and your friend that wanted to change the message on purpose?
They could just change the message, compute the new hash, and pass that along,
and your friend would have no way to tell!

Intuitively we'd like something very close to a hash, except that you and your
friend are the only ones who could create that hash. That's pretty much exactly
what gets used to implement this: an **HMAC**, short for **hashed message
authentication code**. A simple way to imagine how it works is this: let's say
that you and your friend agree on a password to use that only you two know,
perhaps **hunter2**. Whenever you send messages to each other, you don't hash
the message itself, but instead you stick **hunter2** on the end before hashing
it, then send the message. Something like this:

```
message = "Let's eat tacos tonight!"
hmac = md5("Let's eat tacos tonight!hunter2")
send_to_friend(message, hmac)
```

Your friend can verify the same way: they take the message that they received,
stick the password on the end, and hash it. If it matches, then they know not
only that the message hadn't changed, but that you were the one who sent the
message!

In practice, the way you implement this isn't as simple. Depending on what you
do or don't do there are different tricks you can use to change the message
anyways without knowing the key.  [RFC
2104](https://tools.ietf.org/html/rfc2104) defines an implementation to turn
any hash function into an HMAC. In a nutshell, it takes the password, splits it
into two, and hashes twice, with some futzing around in the middle to make it
stronger mathematically. A mental model:

```
message = "Let's eat tacos tonight!"
intermediate_hash = md5("hunter2Let's eat tacos tonight!")
hmac = hash("hunter2" + intermediate_hash)
send_to_friend(message, hmac)
```

See hmac.py for the actual RFC implementation. Use it via the CLI with
`python3 hmac.py <text> <key>` where `<text>` is the data you want to MAC,
and `<key>` is the key you want to use. Here's a quick example:

```
# I want to invite my friend to eat tacos. I also want the message to get there
# safely. We have a buddy password, 'hunter2'. I HMAC my message.

$ python3 hmac.py "Let's eat tacos tonight!" hunter2
3a52ae3c2560d961a6cd743f8c014059

# Now I can message my friend:

$ message_friend "Let's eat tacos tonight!"
$ message_friend 3a52ae3c2560d961a6cd743f8c014059

# My evil nemesis wants to trick my friend into eating brussel sprouts
# instead. They want to change the message and re-hash it, but since they're
# not my buddy, they don't know the buddy password!

$ python3 hmac.py "Let's eat tacos tonight!" hunter3
b0880a97f71f4b288a9c8d9077116663 # not the right hash

$ python3 hmac.py "Let's eat tacos tonight!" hunter1
89ed0012b3f6148c30242f7c92dc2738 # also not the right hash

# My friend receives the messages, and double checks with the password

$ python3 hmac.py "Let's eat tacos tonight!" hunter2
3a52ae3c2560d961a6cd743f8c014059

# Their hash and the one I sent match, so they're confident in their fourthmeal
```

---

HMACs are **symmetric cryptography**. Recall that this means that the key (or
password) used on the sending and receiving side are the same. That means that
you and your friend need to agree on a password before you can use HMACs!

It turns out that we can do something that serves the same purpose as HMACs
with **asymmetric cryptography**.  First, let's take a quick aside and talk
about asymmetric cryptography itself.

 > The first step in asymmetric crypto is to generate what's called a key pair.
 > This pair includes a **public key** and a **private key**. As the name
 > suggests, the public key is meant to be shared publicly, while the private
 > key is meant to be kept secret.  The generation of this key pair and how
 > they work is really complicated in practice and out of scope for this
 > project--you can look up RSA key generation if you want an example.  One of
 > the keys is used to "lock" things, and the other to "unlock". If you keep
 > the key that **unlocks** things, then generally the keys are used for
 > encryption and decryption.  If you keep the key that **locks** things,
 > generally they're used for signing and verifying.

First we generate a signing key pair. One of the keys (which we keep secret) is
called the **signing key**.  Like the name suggests, this key lets us create
signatures, just like we're signing a document except it's impossible to fake.
The other key is the **verification key**, which allows anyone else to check
that whoever wrote the signature really does have the signing key that matches
this verification key.

We could now do something like this. Create a message, hash the message, and
lock the hash with your signing key. (Remember, the signing key is the "lock"
key, so this creates something that anyone with the verification key can
"unlock" and then read.) You can send this message and the signature, and
anyone who has your public key can unlock the signature, hash the message, and
compare the contents. If it matches, then the receiver knows both that it
hasn't been tampered with, and that it actually came from the person who holds
the signing key.

(Signing data with the signing key doesn't destroy any data, so instead of
hashing the message first, you could just lock the entire message. Then the
receiver can just "unlock" it and get the entire message back.  For small
messages that's OK. When the message gets large, then it's way more efficient
just to sign the hash so that anyone who wants to check doesn't have to spend a
long time unlocking a lot of data. Remember, the point here isn't to hide the
contents, it's just to make sure that you can prove that you were the one who
did something.)

The set up for the example here is a bit more complicated. First, the keys need
to be generated. We can use `openssl` to help us, and gen_key is a short bash
script to make a new RSA key and put it in a file called private_key. In order
to get the juicy bits out of the key, we need to parse it--the result of that
is in parsed_private_key.txt. We copy the modulus and exponents, and use them
for the implementation in rsa.py. If you want, you can generate a new key
yourself, extract the numbers with the command in the parsed text file, and use
that instead. Here's a quick example usage:

```
$ python3 rsa.py sign "Noodles are the best no doubt can't deny"
82d0071d0fdcb28336fec3a4d3980f9787ca196bc95aba35ccc6b75744a1042ae5db0a5d4aa6050ab23b117218a7e978502e6d893f574143859205fbb2143320d266904f83b03b049ac90d81fa835a6155e56a9e8426fca2df5186175233e3143fa2afec028ca6c3d9eb98c38d3c18f51a359da5cf0ee2637dd82cf75a91fe5

$ python3 rsa.py verify 82d0071d0fdcb28336fec3a4d3980f9787ca196bc95aba35ccc6b75744a1042ae5db0a5d4aa6050ab23b117218a7e978502e6d893f574143859205fbb2143320d266904f83b03b049ac90d81fa835a6155e56a9e8426fca2df5186175233e3143fa2afec028ca6c3d9eb98c38d3c18f51a359da5cf0ee2637dd82cf75a91fe5
Noodles are the best no doubt can't deny
```

## Prove a lot of things are unchanged

Stepping back from HMACs and signatures for now, let's consider another
problem. We know that we can use hashes to guarantee data integrity, and we saw
some situations where we could use it. When you think about the data we're
working with as messages, hashes are pretty much the only thing we'd need.

But what if instead of sending messages back and forth, we wanted to keep a
record of every message we've ever sent? Well, we could just keep all of the
messages and then the hash of every message, and then every time we wanted to
verify them we could hash everything and compare them. This would also work
although it might take awhile.

Nowadays though, cloud storage is pretty cheap, and local storage is relatively
expensive and also breaks. It would be nice if we could just put all of the
messages into a storage bucket somewhere and not have to worry about it. To be
safe, though it would be nice to have a way to check that they actually have
all of the messages. After all, they use hard drives too, and sometimes they
break.

A naive way might be something like this:

1. Hash all of your messages
1. Send all of your messages to cloud storage
1. Have the cloud provider also hash the messages and send you the hash
1. If the hashes that you receive from cloud storage matches the hash you have
   for the messages, then you can delete the local copy of the message
1. If they don't match, you upload it again and hopefully the error is fixed
   this time

After this, you end up with a list of hashes, which takes up a lot less space.
This is great for you, but there's still a lot of work to do to verify all of
the messages: you have to ask for every one of the hashes, download them all,
and check them one by one. That's potentially a lot of bandwidth and compute
time. It would be more convenient if there were a way to represent the state of
the entire collection with just *one* hash. After all, in general a hash can
take in arbitrary amounts of data, right?

One way you might try to solve this would be to change your approach to
something like this:

1. Hash message 1
1. Put that hash at the end of message 2, then hash that
1. Put *that* hash at the end of message 3, then hash that
1. Repeat until all messages are done
1. Upload all of the messages, and have the cloud provider do the same process
1. When you want to check all of the messages, you compare the final hash with
   the hash generated by cloud storage.

This does solve the problem, but it comes with some other issues. For example,
if the hashes *don't* match, then it's impossible to know which message(s) were
the cause. You still need to go back and check one by one anyways, so you need
to keep the entire list of hashes around. Also, if you notice a typo in message
number 2 of 100,000 and fix it, then you need to re-compute *every* hash after
that in order to come up with the new collection hash.

It turns out that there's a pretty efficient way to solve these (and other)
problems using our old friend from CS class: the tree. Specifically, we can use
a **Merkle tree** (aka **hash tree**), named after Ralph Merkle who patented it
in '79. It works something like this.

1. Hash all of your messages
1. For each **pair** of hashes, concatenate them and then hash that
1. For each pair in the previous step, concatenate them and hash that
1. Continue until there is one hash, which is the root hash
1. Arrange all of the hashes into a tree

We ~double the number of hashes that we need, but we get the following properties:

* We can verify the entire collection with one hash (the root hash)
* If a message has an error, we can find it efficiently! (log(n))
* If we need to update a message, we don't have to re-compute everything! (Only
  log(n) + 1 things)

Now we can save money for us and the cloud provider since there's less work to
do when verifying the data.

Other than our toy message example, these trees are used in a lot of practical
applications that you're probably aware of, including Git/Mercurial, btrfs, and
Bitcoin.

Here, merkle.py uses the hash we made at the beginning for a simple tree.
It walks through a scenario where a client wants to verify file downloads from
a server.

## Check to see if something is in a set

As we approach the goal, we need to step away from crypto for a second and
introduce another cool data structure. The strawman situation will be a bit
more contrived this time, but here we go:

Let's say that you want to start running a lottery. Customers can spend a
dollar and choose six numbers from 1 to 100, and once a week a computer picks 6
random numbers. If someone has chosen those six numbers, they win! You feel
pretty comfortable here, since theres a one-in-a-trillion chance that anyone
chooses the right number. However, you decide that you don't want anyone to be
able to choose the same numbers in any week. It would be a pain to have to deal
with two or more people winning, there would probably be lawsuits, etc. etc.

How could you know when someone comes to purchase a new ticket if that number
had been chosen or not? You'd have to go check all of the previous tickets.
That's a pain too--you don't have a computer handy, so every time you have to
walk into the back room, open the safe, go through all of the tickets, and then
go back and let the customer know whether the number combination they chose was
acceptable.

You don't mind doing it if there's no other way, but here's the problem: while
you're in the back checking, customers are still coming in. You expect that 500
customers come in during the span of time it takes to check one ticket. (It
takes a loooooong time to check!) Since that means you have 500 extra numbers
to check, there's no way to serve any amount of reasonable customers! That's a
lot of dollars you're losing out on!

If you had a computer it would be fine, but due to some extremely unlucky
circumstances you have to do business out in the woods with no electricity, and
the only thing that might be usable is your old cell phone with only 256KB of
free memory. You expect 100,000 customers per week, which means to store all of
the numbers your phone would need around 600KB. Is there anything to be done?

If it weren't obvious from the ridiculous setup, the answer is: yes! The thing
we can use is called a **Bloom filter**, which is what's called a
"probabalistic data structure".  You can use them for a very particular
purpose: given some element and a set, it can tell you that it **absolutely is
not** in the set, or that it's **probably** in the set. What does "probably"
mean here? Well, you get to choose. Do you want a 1% chance of a false
positive? How about a 0.2% chance? Depending on the size of the filter and how
many things you expect, you get to decide that number.

That might not sound too useful, but the lottery example above is a perfect
use! It turns out that a Bloom filter that would hold 100,000 elements with a
1-in-500 chance of a false positive only takes 158KB of space, which is small
enough to fit on your 90's era Nokia cell phone and still have space for a
custom ringtone. (The equations to figure out what these numbers are look
atrocious. You can see them on Wikipedia if you're interested.)

Here's how they work: first, create some array of bits that are all zero. How
long the size of the array should be depends on whatever numbers you worked out
with the equations before.  As part of the filter, you also need a handful of
hash functions. (Recall from earlier that a hash function takes in an element
and outputs some value that looks random.) Using some method (such as a
modulus), you can map the hash output to one spot in the bit array. Adding an
element to the filter follows this process:

1. Using the first hash function, hash the element
1. Go to the corresponding position in the array and set it to 1
1. Repeat for all of the hash functions you have

To check to see whether something is in the filter, it's almost the same
process except that instead of setting the value to a 1, you instead check to
see if it's a 1. If you ever find a zero, you know with 100% certainty that the
item is not in the set. If all of the positions are one, then it's probably in
the set--there are only so many spots available, and the more elements you put
into the filter the more positions are going to have a 1 in them. At some point
you could end up finding 1s in all of the correct spots just by chance, so you
still need some way to go check.

bloom.py makes a Bloom filter with our trusty pal md5, and walks through a few
examples, including one that has a false positive.

It's a bit difficult to follow in words, so check the implementation and maybe
play around with it.  Ultimately the important idea is this: using hashes and
some space, you can check whether some element is in a set or not without
having any information about what's actually in the filter!

The reason this doesn't fit in cryptography is that even without having the
list of elements themselves, there's a ton of information that you can get out
of a Bloom filter. You can approximate how many elements are in the filter, and
if you know what sort of thing the filter holds (e.g. names, social security
numbers, etc.) you can just check any values that you're interested in and see
if they're in there. Later we'll see whether we can make this any better.

## Prove something is unchanged without knowing what it is

Alright, with that detour out of the way let's get back to cryptography, where
we'll remain for the rest of the article. We've seen already how cryptographic
signing can be used to verify that something hasn't changed (and possibly where
it came from). However, it doesn't help in situations where you need to verify
something but you don't want to share the data. For example:

Let's say you're taking an essay test at school. However, the teacher is out
sick, and so there's a substitute teacher giving the exam. In order to prevent
anyone from either bringing in an already written essay or cheating in some
other way, the teacher came up with this scheme:

1. At the beginning of the test, everyone gets a blank sheet of paper
1. Each student writes only their name at the top of the paper
1. The substitute checks that the name matches the student, and writes the time
   and writes their signature
1. When the essay is done, the substitute will sign the bottom of the essay
   right after the last line of written text

The teacher figures that this way they would know at least that the students
turned in their own essays, and that the entire thing was written in the room
during the test. There was one problem though--the topic of the essay was "What
substitute teacher do you dislike the most?" and it turns out the subject of
your essay was today's substitute teacher! How can you get your work signed off
on without giving the substitute a way to see your paper?

In our strawman example, the answer is simple: cover the exam except for the
top and bottom. The substitute can check the top of the paper to make sure it's
yours, and then sign the bottom. That way they never get a chance to see the
content. In cryptography, this is called a **blind signature**.  It does
exactly what it sounds like--anyone with a signing key can sign a piece of data
without being aware of what that data is. The catch is that it only works with
some specially crafted data.  The trick is, of course, how to craft that data.

Recall from the original discussion about signing that the signing key is the
"lock" key, while the verification key is the "unlock" key. We want the holder
of the signing key to be able to sign a message without knowing what it is. We
might try to unintuitively "unlock" the message before it's "locked", and then
have the "lock" key get the original back. It's a clever idea, but not only do
you end up with an unsigned message, the key-holder can see exactly what it is!
We could try to take some random data and mix it with the message to make it
illegible, but then when we get the signature back we have no way to *undo*
that randomness so the thing we have isn't the signature anymore.

What if we did both? First, we take some random data. Then, we "unlock" it, and
combine that unlocked data with the message. Now the message looks like random
data, and we send *that* to get signed. The key-holder signs it with the
signature key and returns the result. What happened during the signing? The
message part of the message got "locked", but the random data that got mixed in
got returned back to the original data! Since we have that original random data
as well, we can now remove it from the result and what's left over is the
signed message that we want.

The process:
```
# Client
msg = "Futonga futonda"
blinded_msg = blind(msg) # looks random

# Server
blind_signature = sign(blinded_msg) # server gets no info

# Client
signature = unblind(blind_signature)
verify(signature) # "Futonga futonda"
```

Hopefully blind.py gives a better look at how this plays out. We leverage some
of the extra information that openssl puts in the private key in order to
efficiently compute some of the required values. (This is starting to get into
the really cool stuff.)

## Putting it together

Now we have all of the pieces for the final step! First, here's our motivation:

Let's imagine we live in a place where buying chocolate isn't allowed unless
you're at least 17 years old. You could of course get some kind of ID to prove
this, but there's a lot of info on the ID card that you'd rather not have to
share just to buy some chocolate. The local government has all of the names of
everyone 17 or older of course, but they can't just publish the list of people
since that's a huge privacy concern! All of the people on the list would be
swamped with requests from children wanting them to buy chocolate on their
behalf. In theory each store could just ask the government every time by giving
the name of the potential purchaser, but then the government knows your
chocolate buying habits. If chocolate ever becomes outlawed and it got out that
you bought some, you might wake up to find the police at your door! How can we
verify that a customer is old enough to buy chocolate?

Spoiler: a **cryptographic accumulator** is what we need! And luckily we can
build it from all of the concepts we've discussed already!

First we have to build the accumulator itself. We want it to look like a bunch
of random data and have no information about what's actually in the
accumulator. We can build something like this using signatures and the Bloom
filter. In our example, the government can **sign** everyone's name who is
older than 17, and insert them into a Bloom filter. (Here we know ahead of time
everyone's name, so we can choose the size and hash functions to guarantee that
there are no false positives, so we don't need to worry about the probability
piece--if a signature hashes to values in the accumulator, it **is** in the
accumulator.)

After that, the government can just send that accumulator out to all of the
stores. The accumulator itself doesn't look like anything, so there's no risk
that any information gets out. When a customer comes into a store and asks to
buy a chocolate bar, the store collects their name and requests that the
government **blind sign** the name. The store gets back a signature without the
government knowing whose name it was. The store can then hash the signature to
see if it's in the accumulator or not. If the signature hashes to a location
with a zero, then the customer gets turned away with no chocolate. Otherwise,
they're allowed to buy as much as they'd like.

In practice there are accumulators with more flexibility--you can add and
remove elements from them without leaking any information, etc. Our examples
are already stretched pretty thin, so we'll deal with the simplified version
here.

# Afterword

I hope the quick look at some interesting crypto pieces was enjoyable! With the
lottery example aside, I think all of the strawman motivations were mostly
plausible, and hopefully the see-saw between motivation and solution helped
show a (kind of) intuitive path from beginning to end.

To re-iterate again, everything here is conceptually correct but flawed
technically. It can (I hope!) be used for educational purposes, but using it
for any actual cryptographic purposes will only lead to a bad end.

# References

Most concepts are from some combination of class and Wikipedia.

The idea for using bloom filters for a crypto accumulator was from:

> Nojima, Ryo, and Youki Kadobayashi. "Cryptographically Secure Bloom-Filters."
> *Trans. Data Priv.* 2.2 (2009): 131-139.

Implementations of md5 and HMAC are from RFC 1321 and 2104 respectively.

> https://tools.ietf.org/html/rfc1321

> https://tools.ietf.org/html/rfc2104
