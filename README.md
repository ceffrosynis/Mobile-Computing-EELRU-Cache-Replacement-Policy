# Mobile-Computing-EELRU-Cache-Replacement-Policy
## Early Eviction - LRU Cache Policy

Cache replacement policy plays a vital role to improve the performance in a cached mobile environment, since the amount of data stored in a client cache is small.

The idea behind this algorithm is to improve the performance of the LRU cache replacement policy.

## Technical Overview
In the case of LRU fails in packets it recently expelled, EELRU recognizes it and instead of expelling the LRU packet, does an "early eviction", by expelling a packet that we recently referenced from the LRU, in the hope that by keeping the older packets, they will be referenced again soon.
