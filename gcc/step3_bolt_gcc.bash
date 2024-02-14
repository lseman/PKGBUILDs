TOPLEV=$(pwd)

# download linux
#wget -c https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.7.3.tar.xz -O linux.tar.xz
#tar -xf linux.tar.xz

cd linux-6.7.3
make distclean
yes "" | make oldconfig

perf record -o ${TOPLEV}/cc1.data --max-size=4G -F 1700 -e cycles:u -j any,u -- make -j$(nproc)

_confflags=(
    --prefix=/usr
    --libdir=/usr/lib
    --libexecdir=/usr/lib
    --mandir=/usr/share/man
    --infodir=/usr/share/info
    --with-build-config=bootstrap-O3
    --with-linker-hash-style=gnu
    --with-system-zlib
    --enable-__cxa_atexit
    --enable-cet=auto
    --enable-checking=release
    --enable-clocale=gnu
    --enable-default-pie
    --enable-default-ssp
    --enable-gnu-indirect-function
    --enable-gnu-unique-object
    --enable-libstdcxx-backtrace
    --enable-link-serialization=1
    --enable-linker-build-id
    --enable-lto
    --disable-multilib
    --enable-plugin
    --enable-shared
    --enable-threads=posix
    --disable-libssp
    --enable-libstdcxx-pch
    --disable-werror
    --with-cloog 
    --with-isl
    --with-tune=native
    --with-arch=native
    --disable-vtable-verify
    --enable-linux-futex
    # define gcc to use mold
    #--with-ld=/usr/bin/mold
)

cd "${TOPLEV}"

mkdir -p "${TOPLEV}/gcc-bolt"
cd "${TOPLEV}/gcc-bolt"
make distclean
"${TOPLEV}/src/gcc/configure" \
    --enable-languages=c,c++,lto \
    --enable-bootstrap \
    "${_confflags[@]:?_confflags unset}"

perf record -o ${TOPLEV}/cc1plus.data --max-size=4G -F 1700 -e cycles:u -j any,u -- make -j$(nproc) all-gcc
