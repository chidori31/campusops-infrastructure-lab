FROM debian:12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        samba \
        samba-ad-provision \
        samba-dsdb-modules \
        samba-vfs-modules \
        winbind \
        krb5-user \
        smbclient \
        ldap-utils \
        dnsutils \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh

RUN sed -i 's/\r$//' /entrypoint.sh \
    && chmod +x /entrypoint.sh

EXPOSE 53 53/udp
EXPOSE 88 88/udp
EXPOSE 135
EXPOSE 137/udp
EXPOSE 138/udp
EXPOSE 139
EXPOSE 389 389/udp
EXPOSE 445
EXPOSE 464 464/udp
EXPOSE 636
EXPOSE 3268
EXPOSE 3269

ENTRYPOINT ["/entrypoint.sh"]