
LD_PRELOAD=/usr/lib/libjemalloc.so perf2bolt /data/gcc-graphite/lib/gcc/x86_64-pc-linux-gnu/13.2.1/cc1 \
            -p cc1.data \
            -o cc1.fdata

LD_PRELOAD=/usr/lib/libjemalloc.so llvm-bolt /data/gcc-graphite/lib/gcc/x86_64-pc-linux-gnu/13.2.1/cc1 \
            --data cc1.fdata \
            -o /data/gcc-graphite/lib/gcc/x86_64-pc-linux-gnu/13.2.1/cc1.bolt \
            -reorder-blocks=ext-tsp \
            -reorder-functions=cdsort \
            -split-functions \
            -split-all-cold \
            -split-eh \
            -dyno-stats \
            -icf=1 \
            -use-gnu-stack \
            -plt=hot || (echo "Could not optimize binary for cc1"; exit 1)

LD_PRELOAD=/usr/lib/libjemalloc.so perf2bolt /data/gcc-graphite/lib/gcc/x86_64-pc-linux-gnu/13.2.1/cc1plus \
            -p cc1plus.data \
            -o cc1plus.fdata

LD_PRELOAD=/usr/lib/libjemalloc.so llvm-bolt /data/gcc-graphite/lib/gcc/x86_64-pc-linux-gnu/13.2.1/cc1plus \
            --data cc1plus.fdata \
            -o /data/gcc-graphite/lib/gcc/x86_64-pc-linux-gnu/13.2.1/cc1plus.bolt \
            -reorder-blocks=ext-tsp \
            -reorder-functions=cdsort \
            -split-functions \
            -split-all-cold \
            -split-eh \
            -dyno-stats \
            -icf=1 \
            -use-gnu-stack \
            -plt=hot || (echo "Could not optimize binary for cc1"; exit 1)

cd /data/gcc-graphite/lib/gcc/x86_64-pc-linux-gnu/13.2.1
mv cc1 cc1.orig
mv cc1.bolt cc1
mv cc1plus cc1plus.orig
mv cc1plus.bolt cc1plus