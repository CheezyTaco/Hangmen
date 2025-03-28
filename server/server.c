#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <sys/socket.h>

#define DEFAULT_CLIENT_COUNT 4

#define handle_error(msg)   \
    do                      \
    {                       \
        perror(msg);        \
        exit(EXIT_FAILURE); \
    } while (0)

int main(int argc, char *argv[])
{
    uint16_t port;
    size_t client_cnt;

    if (argc < 2)
    {
        fprintf(stderr, "usage: ./%s <PORT_NUM> [CLIENT_COUNT]\t (CLIENT_COUNT is optional. defaults to 4)\n", argv[0]);
        return 0;
    }

    if (argc < 3)
    {
        client_cnt = DEFAULT_CLIENT_COUNT;
    }
    else if ((client_cnt = atoi(argv[2])) < 1)
    {
        handle_error("Must have at least 1 client");
    }

    uint16_t port = atoi(argv[1]);

    return EXIT_SUCCESS;
}