# Mobile-Computing-EELRU-Cache-Replacement-Policy
## Early Eviction - LRU Cache Policy

Cache replacement policy plays a vital role to improve the performance in a cached mobile environment, since the amount of data stored in a client cache is small.

The idea behind this algorithm is to improve the performance of the LRU cache replacement policy.

## Technical Overview
In the case of LRU fails in packets it recently expelled, EELRU recognizes it and instead of expelling the LRU packet, does an "early eviction", by expelling a packet that we recently referenced from the LRU, in the hope that by keeping the older packets, they will be referenced again soon.

## Experiment
| Number of Packets | Cache Size |
|       :---:        |    :---:    |
|        512        |     64     |
|        768        |     168    |
|        1024       |     256    |

<table>
<tr><th>Table 1 Heading 1 </th><th>Table 1 Heading 2</th></tr>
<tr><td>

|Table 1| Middle | Table 2|
|--|--|--|
|a| not b|and c |

</td><td>

|b|1|2|3| 
|--|--|--|--|
|a|s|d|f|

</td></tr> </table>
