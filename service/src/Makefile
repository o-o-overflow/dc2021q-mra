OBJPATH := musl-1.2.2/lib
AS := as
LD := ld
CFLAGS := -fno-stack-protector -fPIC
LDFLAGS := $(OBJPATH)/crt1.o $(OBJPATH)/libc.a /usr/lib/gcc-cross/aarch64-linux-gnu/8/libgcc.a
CROSS_COMPILE := aarch64-linux-gnu-
CC := ../tools/gcc-mra
.PHONY: all clean

all: service

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

service: service.o
	$(CROSS_COMPILE)$(LD) -o $@ $^ $(LDFLAGS)

clean:
	rm -rf *.o *.s
