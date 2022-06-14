import random

def tail(b, x):
    count = 0
    while x > 0 and ((x & 0x1) == (b & 0x1)):
        count += 1
        x >>= 1
    return count

def head(b, x):
    count = 0
    while x > 0:
        if ((x & 0x1) == (b & 0x1)):
            count += 1
        else:
            # reset count so we will only count the leading bits
            count = 0
        x >>= 1
    return count

def evaluateFourPeaks(x, T, N):
    t = tail(0, x)
    h = head(1, x)
    R = 0
    if (t > T and h > T):
        R = N
    return max(t, h) + R


T = 1
N = 6
for i in range(1 << N):
    print "{0}:  {1}".format(bin(i), evaluateFourPeaks(i, T, N))

print

samples = []
for i in range(8):
    value = int(random.random() * 64)
    samples.append([evaluateFourPeaks(value, T, N), value])

samples.sort()

for sample in samples:
    print "f(x)={0}, x={1}".format(sample[0], sample[1])

median = samples[len(samples)/2:]
plist = []
for i in range(N):
    mask = 1 << i
    count = 0
    jcounts = [0 for j in range(i+1, N)]
    for sample in median:
        if sample[1] & mask:
            count += 1
            for j in range(i+1, N):
                jmask = 1 << j
                if sample[1] & jmask:
                    jcounts[j-(i+1)] += 1

    iprob = float(count) / len(median)
    # conditionals p(j|i) = p(j, i) / p(i)
    jconditionals = map(lambda x : x/iprob, jcounts)

    plist.append([float(count) / len(median), jconditionals)

print plist
for p in plist:
    for jconditional in plist[1]:
        mutualInformation = 
