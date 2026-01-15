#include <iostream>      // cout, cerr
#include <fcntl.h>       // open
#include <unistd.h>      // fork, close
#include <sys/mman.h>    // mmap, munmap
#include <sys/stat.h>    // fstat
#include <sys/wait.h>    // waitpid
#include <cmath>         // sqrt
#include <cctype>        // isalpha, tolower
#include <pthread.h>     // pthread_mutex_t

#define LETTER_COUNT 26

// Struktura umieszczona w pamięci współdzielonej
struct SharedData {
    unsigned int count[LETTER_COUNT]; // liczniki liter
    double sumOfSquares;              // suma pierwiastków ASCII
    pthread_mutex_t mutex;            // mutex procesowy
};

int main(int argc, char* argv[]) {
    // Sprawdzenie argumentów
    if (argc < 2) {
        std::cerr << "Brak ścieżki do pliku\n";
        return 1;
    }

    // Otwarcie pliku
    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) {
        std::cerr << "Nie można otworzyć pliku\n";
        return 1;
    }

    // Pobranie rozmiaru pliku
    struct stat sb;
    fstat(fd, &sb);
    size_t fileSize = sb.st_size;

    // Mapowanie pliku do pamięci (tylko do odczytu)
    char* fileData = (char*)mmap(
        NULL, fileSize, PROT_READ, MAP_PRIVATE, fd, 0
    );

    // Alokacja pamięci współdzielonej
    SharedData* shared = (SharedData*)mmap(
        NULL, sizeof(SharedData),
        PROT_READ | PROT_WRITE,
        MAP_SHARED | MAP_ANONYMOUS,
        -1, 0
    );

    // Inicjalizacja danych
    for (int i = 0; i < LETTER_COUNT; i++)
        shared->count[i] = 0;

    shared->sumOfSquares = 0;

    // Inicjalizacja mutexa międzyprocesowego
    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
    pthread_mutex_init(&shared->mutex, &attr);

    // Liczba procesów
    unsigned int processCount = sysconf(_SC_NPROCESSORS_ONLN);
    if (argc >= 3)
        processCount = std::stoi(argv[2]);

    size_t chunkSize = fileSize / processCount;

    // Tworzenie procesów
    for (unsigned int i = 0; i < processCount; i++) {
        pid_t pid = fork();

        if (pid == 0) { // proces potomny
            size_t start = i * chunkSize;
            size_t end = (i == processCount - 1) ? fileSize : start + chunkSize;

            unsigned int localCount[LETTER_COUNT] = {0};
            double localSum = 0;

            for (size_t j = start; j < end; j++) {
                unsigned char c = fileData[j];
                localSum += sqrt((int)c);

                if (isalpha(c)) {
                    c = tolower(c);
                    localCount[c - 'a']++;
                }
            }

            // Sekcja krytyczna
            pthread_mutex_lock(&shared->mutex);

            for (int k = 0; k < LETTER_COUNT; k++)
                shared->count[k] += localCount[k];

            shared->sumOfSquares += localSum;

            pthread_mutex_unlock(&shared->mutex);

            _exit(0); // zakończenie procesu potomnego
        }
    }

    // Oczekiwanie na wszystkie procesy
    for (unsigned int i = 0; i < processCount; i++)
        wait(NULL);

    // Wypisanie wyników
    for (int i = 0; i < LETTER_COUNT; i++)
        std::cout << char('a' + i) << ": " << shared->count[i] << std::endl;

    std::cout << "Suma pierwiastków ASCII: " << shared->sumOfSquares << std::endl;

    // Sprzątanie
    pthread_mutex_destroy(&shared->mutex);
    munmap(shared, sizeof(SharedData));
    munmap(fileData, fileSize);
    close(fd);

    return 0;
}
