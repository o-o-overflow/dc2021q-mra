from ubuntu:20.04

# example:
run apt-get -qq update && apt-get install -qq --no-install-recommends xinetd qemu-user
# python3-pip, etc.

# Note: anything that goes in public_files must be pre-built and checked in git
copy src/mra /mra

# If desired, the deployment tester can pass in the flag from the yaml
ARG THE_FLAG="OOO{this is a test flag}"
RUN touch /flag && chmod 644 /flag && echo $THE_FLAG > /flag

copy service.conf /service.conf
copy banner_fail /banner_fail
copy wrapper /wrapper

expose 8000
cmd ["/usr/sbin/xinetd", "-filelog", "/dev/stderr", "-dontfork", "-f", "/service.conf"]
# ^^ If ps would be too revealing, replace with the line below.
#    AFAIK, this also disables the built-in printf(%n) protection, so YMMV.
#cmd chmod go-rwx /proc && /usr/sbin/xinetd -filelog /dev/stderr -dontfork -f /service.conf
