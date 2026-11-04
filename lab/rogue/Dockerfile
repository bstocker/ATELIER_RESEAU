FROM alpine:3.20

RUN apk add --no-cache dnsmasq iproute2 tcpdump

COPY dnsmasq.conf /etc/dnsmasq.conf

CMD ["dnsmasq", "--keep-in-foreground", "--log-dhcp", \
     "--log-facility=-", "--conf-file=/etc/dnsmasq.conf"]
