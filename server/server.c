#include "config.h"

#include "game.h"
#include "tokens.h"
#include "dict.h"

#include <arpa/inet.h>
#include <assert.h>
#include <errno.h>
#include <error.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/queue.h>
#include <sys/socket.h>
#include <unistd.h>

#define handle_error(msg)   \
    do                      \
    {                       \
        perror(msg);        \
        exit(EXIT_FAILURE); \
    } while (0)

typedef struct
{
    pthread_t thread_id;
    int fd;
    struct server *server;
    struct sockaddr_in addr;
} client_t;

typedef struct server
{
    int socket_fd;
    int wait_timeout;

    token_parser_t *token_parser;
    game_t *game;
} server_t;

static int started_client_cnt = 0;

static void server_init(server_t *server, uint16_t port, size_t num_clients)
{
    token_parser_t *parser = token_parser_create(",");

    token_parser_add_variant(parser, "Client_Ready", PAYLOAD_TYPE_STR, PAYLOAD_TYPE_NONE);
    token_parser_add_variant(parser, "Request_Box", PAYLOAD_TYPE_INT, PAYLOAD_TYPE_NONE);
    token_parser_add_variant(parser, "Guess", PAYLOAD_TYPE_STR, PAYLOAD_TYPE_INT, PAYLOAD_TYPE_NONE);
    token_parser_add_variant(parser, "Request_Update", PAYLOAD_TYPE_NONE);
    token_parser_add_variant(parser, "Get_Word", PAYLOAD_TYPE_NONE);
    token_parser_add_variant(parser, "Unlock_Box", PAYLOAD_TYPE_NONE);

    char *word = dict_get_random_word_len_range(DICT_PATH, WORD_LEN_MIN, WORD_LEN_MAX);

    DEBUG_LOG("word: %s\n", word);

    server->token_parser = parser;
    server->game = game_create(word, num_clients, BOX_TIMEOUT_MS);

    free(word);

    if ((server->socket_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
        handle_error("create server socket");

    if (setsockopt(server->socket_fd,
                   SOL_SOCKET,
                   SO_REUSEADDR,
                   &(int){1},
                   sizeof(int)) < 0)
        handle_error("set sockopt");

    // bind socket to localhost on the provided port
    if ((bind(server->socket_fd,
              (struct sockaddr *)&(struct sockaddr_in){
                  .sin_family = AF_INET,
                  .sin_port = htons(port),
                  .sin_addr.s_addr = htonl(INADDR_LOOPBACK),
              },
              sizeof(struct sockaddr_in))) < 0)
        handle_error("bind");

    // start listening for connections
    if (listen(server->socket_fd, num_clients) < 0)
        handle_error("listen");
}

static void client_close_connection(client_t *client)
{
    close(client->fd);
    free(client);
}

static void *client_handler(void *arg)
{
    DEBUG_LOG("Starting client %d thread\n", started_client_cnt);
    int client_index = started_client_cnt++;
    (void)client_index;

    client_t *client = arg;
    server_t *server = client->server;

    ssize_t in_len;
    char in_buf[1024];

    // todo: receive player name here before entering game

    while (1)
    {
        in_len = recv(client->fd, in_buf, 1024, 0);

        if (in_len < 0)
        {
            if (errno != EAGAIN || errno != EWOULDBLOCK)
                handle_error("client recv");
            else
                continue;
        }

        assert(in_len < (ssize_t)sizeof(in_buf));

        // if received length 0, the client disconnected gracefully
        if (in_len == 0)
        {
            client_close_connection(client);
            DEBUG_LOG("client closed connection\n");
            break;
        }

        in_buf[in_len] = '\0';

        DEBUG_LOG("received: %s\n", in_buf);

        token_t *token = token_parser_parse(server->token_parser, in_buf);

        if (!token)
            continue;

        printf("client %d sent ", client_index);
        token_print(token);

        if (!strcmp(token->name, "Request_Box"))
        {
            if (game_request_box(server->game, client, token->payloads[0].int_val))
                send(client->fd, "1", 1, 0);
            else
                send(client->fd, "0", 1, 0);
        }
        else if (!strcmp(token->name, "Guess"))
        {
            if (game_guess(server->game,
                           client,
                           token->payloads[1].int_val,
                           token->payloads[0].string_val))
                send(client->fd, "1", 1, 0);
            else
                send(client->fd, "0", 1, 0);
        }
        else if (!strcmp(token->name, "Request_Update"))
        {
            char *box_state = game_get_boxes_state(server->game);
            send(client->fd, box_state, strlen(box_state), 0);
            free(box_state);
        }
        else if (!strcmp(token->name, "Get_Word"))
        {
            const char *word = game_get_word(server->game);
            send(client->fd, word, strlen(word), 0);
        }
        else if (!strcmp(token->name, "Unlock_Box"))
        {
            game_unlock_boxes(server->game, client);
        }

        token_free(token);
    }

    return NULL;
}

int main(int argc, char *argv[])
{
    uint16_t port;
    size_t client_cnt;
    server_t server;

    if (argc < 2)
        port = PORT_NUM;
    else
        port = atoi(argv[1]);

    if (argc < 3)
        client_cnt = DEFAULT_CLIENT_COUNT;
    else if ((client_cnt = atoi(argv[2])) < 1)
        handle_error("Must have at least 1 client");

    DEBUG_LOG("port: %u\n", port);
    DEBUG_LOG("client count: %lu\n", client_cnt);

    server_init(&server, port, client_cnt);

    while (1)
    {
        int client_fd;
        struct sockaddr_in addr;
        socklen_t addr_len;
        if ((client_fd = accept(server.socket_fd, (struct sockaddr *)&addr, &addr_len)) < 0)
            handle_error("accept client");

        client_t *new_client = malloc(sizeof(*new_client));
        if (!new_client)
            handle_error("malloc client");

        new_client->fd = client_fd;
        new_client->addr = addr;
        new_client->server = &server;

        if (pthread_create(&new_client->thread_id, NULL, client_handler, new_client) < 0)
            handle_error("create client thread");
    }

    return EXIT_SUCCESS;
}