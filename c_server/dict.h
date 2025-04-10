#ifndef __DICT_H__
#define __DICT_H__

#include <stdlib.h>

/**
 * Get a random word from a file consisting of words delimited by newline
 * characters.
 */
char *dict_get_random_word(char *dict_path);

/**
 * Get a random word whose length is in the range [minlen, maxlen] from a file
 * consisting of words delimited by newline characters.
 */
char *dict_get_random_word_len_range(char *dict_path, size_t minlen, size_t maxlen);

#endif // __DICT_H__