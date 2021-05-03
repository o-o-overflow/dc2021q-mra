# DEFCON 2021 Quals mra

## Description

There is a classical stack buffer overflow in the stripped aarch64 binary,
it's is designed for hackers those are new to binary exploitation.

## Fun Facts

It's technically the _easiest_ challenge, but not all solvers have understood the meaning behind it.

1. The stack pionter ($sp) in this program is growing up, unlike any other
program. It's invisible if you solve the challenge by decompiler, fuzzer or tools like pwntools.cyclic.

2. MRA means for reversed ARM, it grants 🦾 which is a _mechanical arm_

3. I add tag `reversing` because of the reversed stack layout. Reversing the stripped aarch64 binary is trivial and it should not be qualified as a real reversing challenge.

4. It's inspired by the brilliant project _[isEvenApi](https://isevenapi.xyz/)_

5. As the flag says, the [Order Of Overflow](https://oooverflow.io/) is odd!
