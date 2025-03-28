#include "tokens.h"

#include <string.h>

token_id match_token(char *name)
{
    token_id id = TOKEN_NONE;
    for (size_t i = 0; i < TOKEN_cnt; i++)
    {
        if (strcmp(TOKEN_MAP[i].name, name) == 0)
        {
            id = i;
            break;
        }
    }

    return id;
}

token_t *token_from_raw_msg(char *msg)
{
    char *p = msg;
    char *token_name = msg;
    char *raw_payload = NULL;

    while (1)
    {
        if (*p == '\0')
        {
            break;
        }

        if (*p == ',')
        {
            *p = '\0';
            p++;
            raw_payload = p;
            break;
        }

        p++;
    }

    token_id token_id = match_token(token_name);

    if (token_id == TOKEN_NONE)
    {
        return NULL;
    }
    else if (TOKEN_MAP[token_id].payload_type != TOKEN_TYPE_EMPTY && raw_payload == NULL)
    {
        return NULL;
    }

    token_t *token = malloc(sizeof(token_t));

    token->type = TOKEN_MAP[token_id].payload_type;

    switch (token->type)
    {
    case TOKEN_TYPE_EMPTY:
        break;
    case TOKEN_TYPE_STR:
        token->payload.string_data = raw_payload;
        break;
    case TOKEN_TYPE_BOOL:
        break;
    case TOKEN_TYPE_INT:
        break;
    case TOKEN_TYPE_ARR:
        break;
    }
}