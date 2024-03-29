# Mobile-Computing-EELRU-Cache-Replacement-Policy
## Early Eviction - LRU Cache Replacement Policy

Cache replacement policy plays a vital role to improve the performance in a cached mobile environment, since the amount of data stored in a client cache is small.

The idea behind this algorithm is to improve the performance of the LRU cache replacement policy.

## Technical Overview
In the case of LRU fails in packets it recently expelled, EELRU recognizes it and instead of expelling the LRU packet, does an "early eviction", by expelling a packet that we recently referenced from the LRU, in the hope that by keeping the older packets, they will be referenced again soon.

## Experiment
We have two independent variables in our experiment. The possible values of these two variables are shown in the table below.

| Number of Packets | Cache Size |
|       :---:        |    :---:    |
|        512        |     64     |
|        768        |     168    |
|        1024       |     256    |

## Experiment Results

| Cache Size | 512 packets | 768 packets |  1024 packets |
|    ---     | ---         | ---         | ---           |
| `64`       | 56.98       | 52.08       | 47.94         |
| `128`      | 68.32       | 62.72       | 58.16         |
| `256`      | 74.14       | 69.4        | 66.8          |

![alt text](https://github.com/ceffrosynis/Mobile-Computing-EELRU-Cache-Replacement-Policy/blob/main/hitRate.png)
