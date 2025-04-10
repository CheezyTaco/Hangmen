#define _POSIX_SOURCE 200809L
#include "tokens.h"

#include <assert.h>
#include <ctype.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

include <sys/queue.h>

typedef struct token_variant_s
{
    char *name;
    payload_type_e *types;
    size_t type_cnt;
    SLIST_ENTRY(token_variant_s)
    entries;
} token_variant_t;

struct token_parser_t
{
    char *delim;
    SLIST_HEAD(, token_variant_s)
    variant_list;
};

token_parser_t *token_parser_create(char *delim)
{
    token_parser_t *parser;

    parser = malloc(sizeof(token_parser_t));
    parser->delim = delim;
    SLIST_INIT(&parser->variant_list);

    return parser;
}

void token_parser_free(token_parser_t *parser)
{
    token_variant_t *variant;

    while (!SLIST_EMPTY(&parser->variant_list))
    {
        variant = SLIST_FIRST(&parser->variant_list);
        SLIST_REMOVE_HEAD(&parser->variant_list, entries);
        free(variant->types);
        free(variant);
    }

    free(parser);
}

void token_parser_add_variant(token_parser_t *parser, char *name, ...)
{
    va_list args;
    token_variant_t *variant;
    payload_type_e payload_type;

    assert(parser);
    assert(name);

    variant = malloc(sizeof(token_variant_t));
    variant->name = name;
    variant->type_cnt = 0;

    va_start(args, name);

    while (va_arg(args, payload_type_e) != PAYLOAD_TYPE_NONE)
        variant->type_cnt++;

    va_end(args);

    if (variant->type_cnt > 0)
    {
        variant->types = malloc(variant->type_cnt * sizeof(variant->types[0]));

        va_start(args, name);

        for (size_t i = 0; i < variant->type_cnt; i++)
        {
            payload_type = va_arg(args, payload_type_e);
            assert(payload_type != PAYLOAD_TYPE_NONE);
            variant->types[i] = payload_type;
        }

        va_end(args);
    }

    SLIST_INSERT_HEAD(&parser->variant_list, variant, entries);
}

static const token_variant_t *match_variant(token_parser_t *parser, char *token_name)
{
    token_variant_t *variant;
    SLIST_FOREACH(variant, &parser->variant_list, entries)
    {
        if (!strcmp(variant->name, token_name))
            return variant;
    }

    return NULL;
}

char *strtriml(char *s)
{
    while(isspace(*s)) s++;
    return s;
}

char *strtrimr(char *s)
{
    char* back = s + strlen(s);
    while(isspace(*--back));
    *(back+1) = '\0';
    return s;
}

char *strtrim(char *s)
{
    return strtrimr(strtriml(s)); 
}

token_t *token_parser_parse(token_parser_t *parser, char *raw_msg)
{
    size_t i;
    char *saveptr;
    char *token_name;
    char *payload_str;
    token_t *token;
    const token_variant_t *variant;

    if (!raw_msg)
        return NULL;

    assert(parser);

    raw_msg = strtrim(raw_msg);

    token_name = strtok_r(raw_msg, parser->delim, &saveptr);

    if (!(variant = match_variant(parser, token_name)))
        return NULL;

    token = malloc(sizeof(*token));
    token->name = variant->name;
    token->payloads_cnt = variant->type_cnt;
    if (token->payloads_cnt)
        token->payloads = malloc(variant->type_cnt *
                                 sizeof(*token->payloads));

    for (i = 0; i < token->payloads_cnt; i++)
        token->payloads[i].type = PAYLOAD_TYPE_NONE;

    for (i = 0; i < token->payloads_cnt; i++)
    {
        if (!(payload_str = strtok_r(NULL, parser->delim, &saveptr)))
        {
            token_free(token);
            return NULL;
        }

        token->payloads[i].type = variant->types[i];
        switch (token->payloads[i].type)
        {
        case PAYLOAD_TYPE_STR:
            token->payloads[i].string_val = strdup(payload_str);
            break;
        case PAYLOAD_TYPE_BOOL:
            token->payloads[i].bool_val = (*payload_str == '0' &&
                                           *(payload_str + 1) == '\0');
            break;
        case PAYLOAD_TYPE_INT:
            token->payloads[i].int_val = atol(payload_str);
            break;
        default:
            token_free(token);
            return NULL;
        }
    }

    return token;
}

void token_free(token_t *token)
{
    if (token->payloads_cnt > 0)
    {
        for (size_t i = 0; i < token->payloads_cnt; i++)
        {
            if (token->payloads[i].type == PAYLOAD_TYPE_STR)
                free(token->payloads[i].string_val);
        }
        free(token->payloads);
    }

    free(token);
}

void token_print(token_t *token)
{
    assert(token);

    printf("token: %s\n", token->name);
    for (size_t i = 0; i < token->payloads_cnt; i++)
    {
        payload_t *pl = &token->payloads[i];
        switch (pl->type)
        {
        case PAYLOAD_TYPE_STR:
            printf("\tstr: %s\n", pl->string_val);
            break;
        case PAYLOAD_TYPE_BOOL:
            printf("\tbool: %s\n", pl->bool_val ? "true" : "false");
            break;
        case PAYLOAD_TYPE_INT:
            printf("\tint: %ld\n", pl->int_val);
            break;
        default:
            break;
        }
    }
}