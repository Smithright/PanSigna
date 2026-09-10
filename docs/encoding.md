# Experimental bit encoding contract

An identifier is a nonempty bit string, starts and ends with `1`, and contains no
`00000000` at **any bit offset**. This is not a byte-aligned exclusion.

- `100000001` is valid (seven internal zero bits).
- `1000000001` is invalid (eight internal zero bits).
- `01 00 01` rendered without spaces has no null substring, but is not a valid
  complete identifier because it starts with zero.

In this reference codec, a sequence joins valid IDs with exactly eight zero bits.
No leading/trailing delimiter is emitted; an empty stream denotes an empty sequence.
Empty notions, nonbinary characters and malformed framing are rejected. This framing
convention and ascending-positive-integer enumeration are implementation proposals;
they are not claims about a ratified global registry. The boundary 1 bits prevent
the delimiter from merging with the interior of an adjacent valid identifier.

The API uses strings of bit characters to make the rules inspectable. It is not a
packed-byte network implementation and makes no line-rate or memory-efficiency claim.
The `bits` model arm consumes individual `0`/`1` tokens; the `ps` arm consumes one
categorical token per experimental ID. These test different inductive biases.

Huffman transport, byte packing/padding, streaming recovery, encryption, glif
rendering and a consortium-managed registry are outside this initial implementation.
