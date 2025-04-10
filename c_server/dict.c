#include "config.h"

#include "dict.h"

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <time.h>

#define MAX_WORD_LEN 30

#ifdef TEST_WORD

char *dict_get_random_word(char *dict_path)
{
    (void)dict_path;

    return strdup(TEST_WORD);
}

char *dict_get_random_word_len_range(char *dict_path, size_t minlen, size_t maxlen)
{
    (void)dict_path;
    (void)minlen;
    (void)maxlen;

    return strdup(TEST_WORD);
}

#else
static size_t count_lines(FILE *fp)
{
    int ch;
    size_t lines = 0;
    while ((ch = fgetc(fp)) != EOF)
    {
        if (ch == '\n')
            lines++;
    }

    if (!feof(fp))
    {
        perror("count lines");
        exit(EXIT_FAILURE);
    }

    fseek(fp, 0, SEEK_SET);

    return lines;
}

static int get_line(FILE *fp, char *buf, size_t buf_siz)
{
    int ret = -1;

    if (!fgets(buf, buf_siz, fp))
    {
        perror("get line");
        exit(EXIT_FAILURE);
    }

    if (buf[0] == '\0')
        goto cleanup;

    buf[strlen(buf) - 1] = '\0';

    ret = 0;

cleanup:
    return ret;
}

static int get_line_at_index(FILE *fp, size_t line_index, char *buf, size_t buf_siz)
{
    int ch;
    size_t lines = 0;
    int ret = -1;

    while (lines != line_index && (ch = fgetc(fp)) != EOF)
    {
        if (ch == '\n')
            lines++;
    }

    if (feof(fp))
    {
        return -1;
    }
    else if (ferror(fp))
    {
        perror("count lines");
        exit(EXIT_FAILURE);
    }

    if (get_line(fp, buf, buf_siz) < 0)
        goto cleanup;

    ret = 0;
cleanup:
    fseek(fp, 0, SEEK_SET);

    return ret;
}

char *dict_get_random_word(char *dict_path)
{
    char *word;
    FILE *dict_file;
    size_t word_cnt;
    size_t word_i;

    word = NULL;

    dict_file = fopen(dict_path, "r");
    if (!dict_file)
    {
        perror("open file");
        exit(EXIT_FAILURE);
    }

    word_cnt = count_lines(dict_file);

    if (!word_cnt)
        goto cleanup;

#ifdef TEST_SEED
    srand(time(TEST_SEED));
#else
    srand(time(NULL));
#endif
    word_i = rand() % word_cnt;

    if (!(word = malloc(MAX_WORD_LEN)))
    {
        perror("alloc word");
        exit(EXIT_FAILURE);
    }

    if (get_line_at_index(dict_file, word_i, word, MAX_WORD_LEN) < 0)
    {
        free(word);
        word = NULL;
    }

cleanup:
    fclose(dict_file);

    return word;
}

char *dict_get_random_word_len_range(char *dict_path, size_t minlen, size_t maxlen)
{
    char *word;
    FILE *dict_file;
    size_t word_len;
    size_t word_cnt;
    size_t word_i;
    size_t *candidates;
    size_t candidate_cnt;
    size_t line_i;
    char buf[MAX_WORD_LEN];

    assert(minlen < maxlen);

    word = NULL;

    dict_file = fopen(dict_path, "r");
    if (!dict_file)
    {
        perror("open file");
        exit(EXIT_FAILURE);
    }

    word_cnt = count_lines(dict_file);
    if (!word_cnt)
        goto cleanup;

    candidate_cnt = 0;
    candidates = malloc(word_cnt * sizeof(*candidates));

    line_i = 0;
    while (!feof(dict_file) && line_i < word_cnt)
    {
        if (get_line(dict_file, buf, MAX_WORD_LEN) < 0)
            goto cleanup0;

        word_len = strlen(buf);
        if (word_len > minlen && word_len < maxlen)
        {
            candidates[candidate_cnt++] = line_i;
        }

        line_i++;
    }

    fseek(dict_file, 0, SEEK_SET);

#ifdef TEST_SEED
    srand(time(TEST_SEED));
#else
    srand(time(NULL));
#endif
    word_i = candidates[rand() % candidate_cnt];

    word = malloc(MAX_WORD_LEN);
    if (!word)
    {
        perror("alloc word");
        exit(EXIT_FAILURE);
    }

    if (get_line_at_index(dict_file, word_i, word, MAX_WORD_LEN) < 0)
    {
        free(word);
        word = NULL;
    }

cleanup0:
    free(candidates);

cleanup:
    fclose(dict_file);

    return word;
}
#endif