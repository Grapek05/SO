import math


# Buddy allocator zarządza pamięcią w blokach o rozmiarach będących potęgami dwójki, dzieląc większe bloki podczas alokacji i scalając „bliźniacze” bloki podczas zwalniania.

class BuddyAllocator:
    def __init__(self, memory_size: int, split_limit: int):
        self.memory_size = memory_size
        self.split_limit = split_limit

        # Maksymalna liczba podziałów bloku - split_limit
        # Określa minimalny rozmiar bloku

        self.min_block_size = memory_size // (2 ** split_limit)

        self.free_blocks = {}
        size = memory_size
        while size >= self.min_block_size:
            self.free_blocks[size] = set()
            size //= 2

        # Limit podziałów zapobiega dzieleniu pamięci w nieskończoność.

        self.free_blocks[memory_size].add(0)
        self.allocated = {}

        # Mapa wolnych bloków pamięci

    def _next_power_of_two(self, size: int) -> int:
        return 2 ** math.ceil(math.log2(size))

    def alloc(self, size: int):
        block_size = self._next_power_of_two(size)
        if block_size < self.min_block_size:
            block_size = self.min_block_size

        current_size = block_size
        while current_size <= self.memory_size:
            if self.free_blocks[current_size]:
                address = self.free_blocks[current_size].pop()
                break
            current_size *= 2
        else:
            raise MemoryError("Brak pamięci")

        while current_size > block_size:
            current_size //= 2
            buddy_address = address + current_size
            self.free_blocks[current_size].add(buddy_address)

        self.allocated[address] = block_size
        return address, block_size

    def free(self, address: int):
        if address not in self.allocated:
            raise ValueError("Double free lub invalid free")

        block_size = self.allocated.pop(address)

        while True:
            buddy_address = address ^ block_size
            if buddy_address in self.free_blocks[block_size]:
                self.free_blocks[block_size].remove(buddy_address)
                address = min(address, buddy_address)
                block_size *= 2
                if block_size > self.memory_size:
                    break
            else:
                self.free_blocks[block_size].add(address)
                break


# ======= TEST / SYMULACJA =======
if __name__ == "__main__":
    allocator = BuddyAllocator(2048, 6)

    print("Alloc 100")
    a1 = allocator.alloc(100)
    print(a1)

    print("Alloc 200")
    a2 = allocator.alloc(200)
    print(a2)

    print("Free pierwszego")
    allocator.free(a1[0])

    print("Free drugiego")
    allocator.free(a2[0])

    print("Koniec")
