from dataclasses import dataclass

from ldap3 import ALL, BASE, SUBTREE, Connection, Server
from ldap3.core.exceptions import LDAPException
from ldap3.utils.conv import escape_filter_chars

from app.config import settings


GROUP_ROLE_MAP = {
    "App-Admins": "admin",
    "HelpDesk": "support",
    "Employees": "user",
}


class ActiveDirectoryError(Exception):
    pass


class ActiveDirectoryUnavailable(ActiveDirectoryError):
    pass


class ActiveDirectoryUserNotFound(ActiveDirectoryError):
    pass


@dataclass
class ActiveDirectoryUser:
    username: str
    full_name: str
    email: str
    distinguished_name: str
    groups: list[str]
    role: str


def _connection() -> Connection:
    try:
        server = Server(
            settings.ad_server,
            port=settings.ad_port,
            get_info=ALL,
            connect_timeout=5,
        )

        return Connection(
            server,
            user=settings.ad_bind_user,
            password=settings.ad_bind_password,
            auto_bind=True,
            receive_timeout=5,
        )

    except LDAPException as exc:
        raise ActiveDirectoryUnavailable(
            f"Unable to connect to Active Directory: {exc}"
        ) from exc


def _group_name_from_dn(dn: str) -> str:
    first_part = dn.split(",", 1)[0]

    if first_part.upper().startswith("CN="):
        return first_part[3:]

    return first_part


def _calculate_role(groups: list[str]) -> str:
    for group, role in GROUP_ROLE_MAP.items():
        if group in groups:
            return role

    return "user"


def check_active_directory() -> dict[str, str | bool]:
    if not settings.ad_enabled:
        return {
            "enabled": False,
            "status": "disabled",
        }

    connection = _connection()

    try:
        success = connection.search(
            search_base=settings.ad_base_dn,
            search_filter="(objectClass=domain)",
            search_scope=BASE,
            attributes=["distinguishedName"],
        )

        if not success:
            raise ActiveDirectoryUnavailable(
                "Active Directory base DN is unavailable"
            )

        return {
            "enabled": True,
            "status": "available",
            "server": settings.ad_server,
            "domain": settings.ad_domain,
        }

    finally:
        connection.unbind()


def get_active_directory_user(
    username: str,
) -> ActiveDirectoryUser:

    escaped_username = escape_filter_chars(
        username
    )

    connection = _connection()

    try:
        success = connection.search(
            search_base=settings.ad_base_dn,
            search_filter=(
                "(&(objectClass=user)"
                f"(sAMAccountName={escaped_username}))"
            ),
            search_scope=SUBTREE,
            attributes=[
                "sAMAccountName",
                "displayName",
                "cn",
                "mail",
                "distinguishedName",
                "memberOf",
            ],
        )

        if not success or len(connection.entries) == 0:
            raise ActiveDirectoryUserNotFound(
                f"AD user not found: {username}"
            )

        entry = connection.entries[0]

        data = entry.entry_attributes_as_dict

        username_values = data.get(
            "sAMAccountName",
            [],
        )

        cn_values = data.get(
            "cn",
            [],
        )

        display_values = data.get(
            "displayName",
            [],
        )

        mail_values = data.get(
            "mail",
            [],
        )

        dn_values = data.get(
            "distinguishedName",
            [],
        )

        memberships = data.get(
            "memberOf",
            [],
        )

        groups = [
            _group_name_from_dn(str(group_dn))
            for group_dn in memberships
        ]

        resolved_username = (
            str(username_values[0])
            if username_values
            else username
        )

        if display_values:
            full_name = str(display_values[0])
        elif cn_values:
            full_name = str(cn_values[0])
        else:
            full_name = resolved_username

        if mail_values:
            email = str(mail_values[0])
        else:
            email = (
                f"{resolved_username}@"
                f"{settings.ad_domain}"
            )

        distinguished_name = (
            str(dn_values[0])
            if dn_values
            else str(entry.entry_dn)
        )

        return ActiveDirectoryUser(
            username=resolved_username,
            full_name=full_name,
            email=email,
            distinguished_name=distinguished_name,
            groups=groups,
            role=_calculate_role(groups),
        )

    finally:
        connection.unbind()