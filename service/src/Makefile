OBJPATH := musl-1.2.2/lib
AS := as
LD := ld
CFLAGS := -fno-stack-protector -fPIC -fomit-frame-pointer -O0
# LDFLAGS := $(OBJPATH)/crt1.o $(OBJPATH)/libc.a /usr/lib/gcc-cross/aarch64-linux-gnu/8/libgcc.a
LDFLAGS := $(OBJPATH)/crt1.o $(OBJPATH)/libc.a libgcc.a
CROSS_COMPILE := aarch64-linux-gnu-
CC := ../tools/gcc-mra
.PHONY: all clean

all: mra

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

service: service.o
	$(CROSS_COMPILE)$(LD) -o $@ $^ $(LDFLAGS)

mra: service
	cp $< $@
	$(CROSS_COMPILE)strip $@

clean:
	rm -rf *.o *.s
