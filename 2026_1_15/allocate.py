class Slab:
    def __init__(self, object_size, objects_per_slab):
        self.object_size = object_size
        self.objects_per_slab = objects_per_slab
        # Symulacja ciągłej pamięci
        self.memory = bytearray(object_size * objects_per_slab)
        # Mapa bitowa: False = wolny, True = zajęty
        self.bitmap = [False] * objects_per_slab
        self.free_slots = objects_per_slab

    def alloc(self):
        if self.free_slots == 0:
            return None
        
        for i in range(self.objects_per_slab):
            if not self.bitmap[i]:
                self.bitmap[i] = True
                self.free_slots -= 1
                # Zwracamy "adres" (indeks startowy w memory)
                return i * self.object_size
        return None

    def free(self, offset):
        index = offset // self.object_size
        if 0 <= index < self.objects_per_slab and self.bitmap[index]:
            self.bitmap[index] = False
            self.free_slots += 1
            return True
        return False

    def contains_address(self, offset):
        return 0 <= offset < (self.object_size * self.objects_per_slab)

    def is_empty(self):
        return self.free_slots == self.objects_per_slab
    
class SlabCache:
    def __init__(self, object_size, objects_per_slab):
        self.object_size = object_size
        self.objects_per_slab = objects_per_slab
        self.slabs = []

    def alloc(self):
        # 1. Próbuj znaleźć wolne miejsce w istniejących slabach
        for i, slab in enumerate(self.slabs):
            offset = slab.alloc()
            if offset is not None:
                print(f"[Alloc] Znaleziono miejsce w Slab {i}")
                return (slab, offset)

        # 2. Brak miejsca - stwórz nowy slab
        print(f"[Alloc] Brak wolnego miejsca. Tworzenie Slab {len(self.slabs)}")
        new_slab = Slab(self.object_size, self.objects_per_slab)
        self.slabs.append(new_slab)
        offset = new_slab.alloc()
        return (new_slab, offset)

    def free(self, ptr):
        slab_obj, offset = ptr
        # Wyszukiwanie slaba i zwalnianie
        if slab_obj.free(offset):
            print(f"[Free] Zwolniono obiekt w slabie pod offsetem {offset}")
            # Opcjonalnie: usuń slab, jeśli jest całkowicie pusty (poza ostatnim)
            if slab_obj.is_empty() and len(self.slabs) > 1:
                self.slabs.remove(slab_obj)
                print("[Cache] Usunięto pusty slab z pamięci")
        else:
            print("[Error] Nie udało się zwolnić pamięci")

# Inicjalizacja: obiekty 64-bajtowe, po 2 na każdy slab
cache = SlabCache(object_size=64, objects_per_slab=2)

print("--- KROK 1: Alokacja 3 obiektów ---")
addr1 = cache.alloc() # Slab 0
addr2 = cache.alloc() # Slab 0 (pełny)
addr3 = cache.alloc() # Slab 1 (nowy)

print(f"\nLiczba aktywnych slabów: {len(cache.slabs)}")

print("\n--- KROK 2: Zwalnianie i ponowna alokacja ---")
cache.free(addr1) # Zwalnia slot w Slab 0
addr4 = cache.alloc() # Powinien trafić do Slab 0 zamiast tworzyć Slab 2

print("\n--- KROK 3: Czyszczenie ---")
cache.free(addr2)
cache.free(addr4)
# Slab 0 jest teraz pusty i zostanie usunięty przy restrykcyjnej polityce