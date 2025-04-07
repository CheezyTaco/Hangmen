#ifndef __TOKEN_H__
#define __TOKEN_H__

#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct token_parser_t token_parser_t;

typedef enum
{
    PAYLOAD_TYPE_NONE,
    PAYLOAD_TYPE_STR,
    PAYLOAD_TYPE_BOOL,
    PAYLOAD_TYPE_INT,
} payload_type_e;

typedef struct
{
    payload_type_e type;
    union
    {
        char *string_val;
        bool bool_val;
        int64_t int_val;
    };
} payload_t;

typedef struct
{
    char *name;
    payload_t *payloads;
    size_t payloads_cnt;
} token_t;

/**
 * Create a token parser.
 *
 * delim is the delimiting character between the name and value of a token
 * message
 *
 * returns a heap allocated token_parser_t, which should be freed with
 * token_parser_free
 */
token_parser_t *token_parser_create(char *delim);
void token_parser_free(token_parser_t *parser);

/**
 * Add a token variant to a parser
 *
 * A token variant defines a token 'type'. It comprises a unique name and
 * payload types. For example, a token variant for a player's x,y position in a
 * game could use the name "PLAYER_POS", type PAYLOAD_TYPE_INT for x and type
 * PAYLOAD_TYPE_INT for y.
 *
 * Payload types are passed to this function in the vararg, terminated by a
 * PAYLOAD_TYPE_NONE. If a variant takes no payload, the vararg should just be
 * PAYLOAD_TYPE_NONE.
 */
void token_parser_add_variant(token_parser_t *parser, char *name, ...);

/**
 * Parse a raw string into a token_t with a token parser
 *
 * Splits raw_msg into a name and payload with the set delimiter of the token
 * parser, then tries to match the name to one of the variants of the parser.
 * If the name matches a variant, then it parses the payload into the type
 * defined by the variant.
 *
 * If parsed successfully, returns a heap allocated token_t, which should be
 * freed with token_free. Returns NULL if the name does not match a variant,
 * or if the payload cannot be parsed into the type defined by a matched
 * variant.
 */
token_t *token_parser_parse(token_parser_t *parser, char *raw_msg);
void token_free(token_t *token);

void token_print(token_t *token);

#endif // __TOKEN_H__