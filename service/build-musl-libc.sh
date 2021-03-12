#!/bin/sh
# apt-get update && apt-get install -y gcc-8-aarch64-linux-gnu
export musl=musl-1.2.2
if ! [ -d $musl ]
then
    wget https://musl.libc.org/releases/$musl.tar.gz
    tar xf $musl.tar.gz
fi
cd $musl
CC=$PWD/../tools/gcc-mra ./configure
make -j`nproc`
