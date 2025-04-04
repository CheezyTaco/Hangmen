#ifndef __DICT_H__
#define __DICT_H__

#include <stdlib.h>

char *dict_get_random_word(char *dict_path);
char *dict_get_random_word_len_range(char *dict_path, size_t minlen, size_t maxlen);

#endif // __DICT_H__