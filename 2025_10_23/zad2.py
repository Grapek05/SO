import sys
import time

def main():
    if len(sys.argv) < 2:
        print("Użycie: python zad2.py <nazwa_pliku>")
        sys.exit(1)

    filename = sys.argv[1]

    with open(filename, "a") as f:
        i = 0
        while True:
            f.write(f"{i}\n")
            f.flush()
            i += 1
            time.sleep(1)

if __name__ == "__main__":
    main()
