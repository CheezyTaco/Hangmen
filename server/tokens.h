#include <stdint.h>
#include <stdlib.h>

typedef enum
{
    TOKEN_TYPE_EMPTY,
    TOKEN_TYPE_STR,
    TOKEN_TYPE_BOOL,
    TOKEN_TYPE_INT,
    TOKEN_TYPE_ARR,
} token_type_e;

typedef struct
{
    token_type_e type;
    union
    {
        char *string_data;
        bool bool_data;
        int64_t int_data;
        struct
        {
            size_t len;
            uint8_t *arr;
        } array_data;
    } payload;
} token_t;

typedef struct
{
    const char *name;
    token_type_e payload_type;
    int (*reply_fn)(token_t *, uint8_t **, size_t *);
} token_map_t;

typedef enum
{
    TOKEN_NONE = -1,
    TOKEN_CLIENT_READY,
    TOKEN_GUESS,
    TOKEN_REQUEST_BOX,
    TOKEN_REQUEST_UPDATE,

    TOKEN_cnt,
} token_id;

const token_map_t TOKEN_MAP[TOKEN_cnt] = {
    [TOKEN_CLIENT_READY] = {.name = "Client_Ready", .payload_type = TOKEN_TYPE_STR},
    [TOKEN_GUESS] = {.name = "Guess", .payload_type = TOKEN_TYPE_STR},
    [TOKEN_REQUEST_BOX] = {.name = "Request_Box", .payload_type = TOKEN_TYPE_INT},
    [TOKEN_REQUEST_UPDATE] = {.name = "Request_Update", .payload_type = TOKEN_TYPE_EMPTY},
};
