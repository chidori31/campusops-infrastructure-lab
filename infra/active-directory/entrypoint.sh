#!/usr/bin/env bash

set -euo pipefail

REALM="${AD_REALM:-CORP.LAB}"
DOMAIN="${AD_NETBIOS_DOMAIN:-CORP}"

ADMIN_PASSWORD="${AD_ADMIN_PASSWORD:-CampusOpsAdmin123!}"
SERVICE_PASSWORD="${AD_SERVICE_PASSWORD:-SvcCampusOps123!}"
USER_PASSWORD="${AD_USER_PASSWORD:-LabUser123!}"

SAMBA_DB="/var/lib/samba/private/sam.ldb"
XATTR_DB="/var/lib/samba/private/xattr.tdb"


echo
echo "======================================"
echo " CampusOps Samba Active Directory"
echo "======================================"
echo
echo "Realm:  ${REALM}"
echo "Domain: ${DOMAIN}"
echo


# ==========================================================
# PROVISION DOMAIN
# ==========================================================

if [ ! -f "${SAMBA_DB}" ]; then

    echo "[AD] Provisioning new Active Directory domain..."

    rm -f /etc/samba/smb.conf

    samba-tool domain provision \
        --server-role=dc \
        --use-rfc2307 \
        --dns-backend=SAMBA_INTERNAL \
        --realm="${REALM}" \
        --domain="${DOMAIN}" \
        --adminpass="${ADMIN_PASSWORD}" \
        --option="ldap server require strong auth = no" \
        --option="vfs objects = dfs_samba4 acl_xattr xattr_tdb" \
        --option="xattr_tdb:file = ${XATTR_DB}"

    echo
    echo "[AD] Domain provisioned successfully."

    # Make the container-safe xattr backend persistent
    # in the generated Samba configuration.

    sed -i '/^\[global\]/a\
        ldap server require strong auth = no\
        vfs objects = dfs_samba4 acl_xattr xattr_tdb\
        xattr_tdb:file = /var/lib/samba/private/xattr.tdb' \
        /etc/samba/smb.conf

else

    echo "[AD] Existing domain database found."

fi


# ==========================================================
# KERBEROS CONFIG
# ==========================================================

if [ -f /var/lib/samba/private/krb5.conf ]; then

    cp \
        /var/lib/samba/private/krb5.conf \
        /etc/krb5.conf

fi


echo
echo "[AD] Samba configuration:"
echo

cat /etc/samba/smb.conf

echo


# ==========================================================
# START DOMAIN CONTROLLER
# ==========================================================

echo "[AD] Starting Samba AD DC..."

samba -i -M single &

SAMBA_PID=$!


echo "[AD] Waiting for LDAP..."

LDAP_READY=false

for i in $(seq 1 60); do

    if ! kill -0 "${SAMBA_PID}" 2>/dev/null; then
        echo "[ERROR] Samba process terminated."
        wait "${SAMBA_PID}" || true
        exit 1
    fi

    if nc -z 127.0.0.1 389; then
        LDAP_READY=true
        break
    fi

    sleep 1

done


if [ "${LDAP_READY}" != "true" ]; then
    echo "[ERROR] LDAP did not start within 60 seconds."
    exit 1
fi


echo "[AD] LDAP is available."


# ==========================================================
# HELPERS
# ==========================================================

create_group() {

    local group="$1"

    if samba-tool group show "$group" >/dev/null 2>&1; then

        echo "[AD] Group exists: $group"

    else

        samba-tool group add "$group"

        echo "[AD] Group created: $group"

    fi
}


create_user() {

    local username="$1"
    local password="$2"

    if samba-tool user show "$username" >/dev/null 2>&1; then

        echo "[AD] User exists: $username"

    else

        samba-tool user create \
            "$username" \
            "$password"

        echo "[AD] User created: $username"

    fi

    samba-tool user setexpiry \
        "$username" \
        --noexpiry \
        >/dev/null
}


add_member() {

    local group="$1"
    local username="$2"

    if samba-tool group listmembers "$group" |
        grep -Fxq "$username"; then

        echo "[AD] Membership exists: $username -> $group"

    else

        samba-tool group addmembers \
            "$group" \
            "$username"

        echo "[AD] Membership created: $username -> $group"

    fi
}


# ==========================================================
# LAB DIRECTORY STRUCTURE
# ==========================================================

echo
echo "[AD] Creating laboratory groups..."

create_group "Employees"
create_group "HelpDesk"
create_group "App-Admins"
create_group "VPN-Users"


echo
echo "[AD] Creating laboratory users..."

create_user \
    "svc-campusops" \
    "${SERVICE_PASSWORD}"

create_user \
    "tivanov" \
    "${USER_PASSWORD}"

create_user \
    "petrov" \
    "${USER_PASSWORD}"

create_user \
    "admin.demo" \
    "${USER_PASSWORD}"


echo
echo "[AD] Configuring group membership..."

add_member \
    "Employees" \
    "tivanov"

add_member \
    "HelpDesk" \
    "tivanov"

add_member \
    "Employees" \
    "petrov"

add_member \
    "Employees" \
    "admin.demo"

add_member \
    "App-Admins" \
    "admin.demo"


# ==========================================================
# RESULT
# ==========================================================

echo
echo "======================================"
echo " Active Directory ready"
echo "======================================"
echo

echo "Domain:"
samba-tool domain info 127.0.0.1 || true

echo
echo "Users:"
samba-tool user list

echo
echo "HelpDesk:"
samba-tool group listmembers HelpDesk

echo
echo "App-Admins:"
samba-tool group listmembers App-Admins

echo
echo "[AD] DC01.CORP.LAB is ready."

echo


wait "${SAMBA_PID}"