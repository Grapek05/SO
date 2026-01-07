#include <iostream>
#include <fstream>
#include <vector>
#include <thread>
#include <mutex>
#include <cmath>
#include <string>
#include <cctype>
#include <sstream>

// Zdefiniowana w zadaniu struktura
#define LETTER_COUNT 26

struct context {
    std::string content;
    unsigned long count[LETTER_COUNT] = {0};
    double sumOfSquares = 0; // Uwaga: Mimo nazwy 'sumOfSquares', będziemy tu sumować pierwiastki zgodnie z treścią zadania
    std::mutex mutex;
};

// Funkcja wykonywana przez każdy wątek
void process_chunk(context& ctx, size_t start_index, size_t end_index) {
    // === OPTYMALIZACJA ===
    // Zamiast blokować mutex przy każdym znaku, tworzymy lokalne liczniki.
    // Dzięki temu wątki pracują niezależnie i nie czekają na siebie (brak contention).
    // Zużywamy nieco więcej RAM (na stosie), ale zyskujemy ogromnie na wydajności.
    
    unsigned long local_count[LETTER_COUNT] = {0};
    double local_sum_roots = 0.0;

    for (size_t i = start_index; i < end_index; ++i) {
        unsigned char c = static_cast<unsigned char>(ctx.content[i]);

        // 1. Zliczanie liter (case insensitive)
        // Sprawdzamy czy to litera
        if (std::isalpha(c)) {
            char lower = std::tolower(c);
            // Upewniamy się, że to zakres a-z (dla bezpieczeństwa przy dziwnych locale)
            if (lower >= 'a' && lower <= 'z') {
                local_count[lower - 'a']++;
            }
        }

        // 2. Zliczanie pierwiastków kodów ASCII WSZYSTKICH znaków
        // Kod ASCII to po prostu wartość liczbowa znaku c
        local_sum_roots += std::sqrt(static_cast<double>(c));
    }

    // === SEKCJA KRYTYCZNA ===
    // Blokujemy mutex tylko RAZ na wątek, aby przepisać wyniki lokalne do globalnych.
    std::lock_guard<std::mutex> lock(ctx.mutex);
    
    for (int i = 0; i < LETTER_COUNT; ++i) {
        ctx.count[i] += local_count[i];
    }
    ctx.sumOfSquares += local_sum_roots;
}

int main(int argc, char* argv[]) {
    // Sprawdzenie argumentów
    if (argc < 2) {
        std::cerr << "Uzycie: " << argv[0] << " <sciezka_do_pliku> [ilosc_watkow]" << std::endl;
        return 1;
    }

    std::string filepath = argv[1];
    
    // Ustalenie liczby wątków
    unsigned int num_threads = std::thread::hardware_concurrency(); // Domyślnie
    if (argc >= 3) {
        try {
            int arg_threads = std::stoi(argv[2]);
            if (arg_threads >= 1) {
                num_threads = static_cast<unsigned int>(arg_threads);
            } else {
                std::cerr << "Ostrzezenie: Podano nieprawidlowa ilosc watkow. Uzywam domyslnej: " << num_threads << std::endl;
            }
        } catch (...) {
            std::cerr << "Ostrzezenie: Blad parsowania ilosci watkow. Uzywam domyslnej: " << num_threads << std::endl;
        }
    }
    // Fallback gdyby hardware_concurrency zwróciło 0
    if (num_threads == 0) num_threads = 1;

    std::cout << "Uruchamianie na " << num_threads << " watkach..." << std::endl;

    // Inicjalizacja struktury
    context ctx;

    // 1. Wczytanie całego pliku do pamięci
    try {
        std::ifstream file(filepath, std::ios::binary); // binary, aby uniknąć konwersji znaków końca linii
        if (!file.is_open()) {
            std::cerr << "Blad: Nie mozna otworzyc pliku " << filepath << std::endl;
            return 1;
        }
        
        // Szybkie wczytanie pliku do stringa
        std::ostringstream ss;
        ss << file.rdbuf();
        ctx.content = ss.str();
        file.close();
    } catch (const std::exception& e) {
        std::cerr << "Blad podczas odczytu pliku: " << e.what() << std::endl;
        return 1;
    }

    if (ctx.content.empty()) {
        std::cout << "Plik jest pusty." << std::endl;
        return 0;
    }

    size_t total_length = ctx.content.length();
    size_t chunk_size = total_length / num_threads;
    
    std::vector<std::thread> threads;
    threads.reserve(num_threads);

    // 2. Uruchomienie wątków
    size_t start_index = 0;
    for (unsigned int i = 0; i < num_threads; ++i) {
        size_t end_index;
        
        // Ostatni wątek bierze wszystko co zostało (w przypadku reszty z dzielenia)
        if (i == num_threads - 1) {
            end_index = total_length;
        } else {
            end_index = start_index + chunk_size;
        }

        // Przekazujemy ctx przez referencję
        threads.emplace_back(process_chunk, std::ref(ctx), start_index, end_index);
        
        start_index = end_index;
    }

    // 3. Oczekiwanie na zakończenie (join)
    for (auto& t : threads) {
        if (t.joinable()) {
            t.join();
        }
    }

    // 4. Wypisanie wyników
    std::cout << "--- Wyniki ---" << std::endl;
    for (int i = 0; i < LETTER_COUNT; ++i) {
        char current_char = 'a' + i;
        std::cout << current_char << ": " << ctx.count[i] << std::endl;
    }
    
    std::cout << "\nSuma pierwiastkow kodow ASCII: " << ctx.sumOfSquares << std::endl;

    return 0;
}