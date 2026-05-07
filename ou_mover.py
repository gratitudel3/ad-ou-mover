#!/usr/bin/env python3

import argparse
import getpass
import os
from ldap3 import Server, Connection, ALL, NTLM, SASL, KERBEROS


class ADClient:
    def __init__(self, dc_ip, dc_host, domain, user,
                 password=None, kerberos=False, no_pass=False):

        self.dc_ip = dc_ip
        self.dc_host = dc_host
        self.domain = domain
        self.user = user
        self.password = password
        self.kerberos = kerberos
        self.no_pass = no_pass

        self.dc = self._resolve_dc()
        self.conn = self._connect()

    
    # Resolve DC
    def _resolve_dc(self):
        if self.dc_ip:
            return self.dc_ip
        if self.dc_host:
            return self.dc_host
        raise Exception("Provide --dc-ip or --dc-host")

    
    # LDAP connect (password)
    def _ldap_connect(self):
        server = Server(
            f"ldap://{self.dc}",
            get_info=ALL,
            connect_timeout=5
        )

        print("[*] LDAP auth via password")

        conn = Connection(
            server,
            user=f"{self.domain}\\{self.user}",
            password=self.password,
            authentication=NTLM,
            auto_bind=False
        )

        if not conn.bind():
            print("[-] LDAP bind failed:", conn.result)
            raise Exception("Authentication failed")

        return conn

    
    # Kerberos authentication
    def _kerberos_connect(self):
        server = Server(
            self.dc,
            get_info=ALL,
            connect_timeout=5
        )

        print("[*] Kerberos auth via ticket")
        print(f"[*] DC: {self.dc}")
        print(f"[*] KRB5CCNAME: {os.getenv('KRB5CCNAME')}")

        conn = Connection(
            server,
            authentication=SASL,
            sasl_mechanism=KERBEROS,
            auto_bind=True
        )

        return conn

    
    def _connect(self):
        if self.kerberos:
            return self._kerberos_connect()
        return self._ldap_connect()

    
    # MOVE OBJECT
    def move_object(self, user_dn, target_ou, new_cn=None):
        if new_cn is None:
            new_cn = user_dn.split(",")[0].split("=")[1]

        result = self.conn.modify_dn(
            dn=user_dn,
            relative_dn=f"CN={new_cn}",
            new_superior=target_ou
        )

        return {
            "success": result,
            "user": new_cn,
            "from": user_dn,
            "to": target_ou
        }

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--dc-ip")
    parser.add_argument("--dc-host")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password")

    parser.add_argument("-k", "--kerberos", action="store_true")
    parser.add_argument("--no-pass", action="store_true")

    sub = parser.add_subparsers(dest="cmd")

    move = sub.add_parser("move")
    move.add_argument("--user-dn", required=True)
    move.add_argument("--target-ou", required=True)
    move.add_argument("--new-cn")

    args = parser.parse_args()

    # VALIDATION
    if not args.dc_ip and not args.dc_host:
        parser.error("Provide --dc-ip or --dc-host")

    if args.kerberos and args.password:
        parser.error("Cannot use password with Kerberos")

    if args.no_pass and not args.kerberos:
        parser.error("--no-pass requires Kerberos (-k)")

    if not args.kerberos and not args.password and not args.no_pass:
        args.password = getpass.getpass("Password: ")

    # CLIENT INIT
    client = ADClient(
        args.dc_ip,
        args.dc_host,
        args.domain,
        args.user,
        password=args.password,
        kerberos=args.kerberos,
        no_pass=args.no_pass
    )

    
    # MOVE PARAMETERS
    if args.cmd == "move":
        res = client.move_object(
            args.user_dn,
            args.target_ou,
            args.new_cn
        )

        if res["success"]:
            print(f"[+] Moved user '{res['user']}'")
            print(f"[+] From: {res['from']}")
            print(f"[+] To:   {res['to']}")
        else:
            print("[-] Operation failed")
            print("[-] LDAP result:", client.conn.result)


if __name__ == "__main__":
    main()
