#!/usr/bin/env python3

import os
import pwd

def znajdz_procesy():
    pidy = []
    for entry in os.scandir('/proc'):
        if entry.name.isdigit() and entry.is_dir():
            pidy.append(entry.name)
    return pidy

def dane_procesu(pid):
    try:
        with open(f'/proc/{pid}/status') as plik:
            for linia in plik:
                if linia.startswith('Name:'):
                    nazwa = linia.split()[1]
                elif linia.startswith('Uid:'):
                    uid = linia.split()[1]
        return nazwa, uid
    except:
        return None, None

def uid_do_nazwy(uid):
    try:
        return pwd.getpwuid(int(uid)).pw_name
    except:
        return uid

def main():
    print(f"{'UŻYTKOWNIK'} {'PID'} {'PROCES'}")
    
    for pid in znajdz_procesy():
        nazwa, uid = dane_procesu(pid)
        if nazwa and uid:
            uzytkownik = uid_do_nazwy(uid)
            print(f"{uzytkownik} {pid} {nazwa}")

if __name__ == "__main__":
    main()