#ifndef __CONFIG_H__
#define __CONFIG_H__

#define PORT_NUM 5555
#define DICT_PATH "dictionary3.txt"
#define DEFAULT_CLIENT_COUNT 4
#define BOX_TIMEOUT_MS 5000

#define WORD_LEN_MIN 4
#define WORD_LEN_MAX 10

#if 1
#define TEST_WORD "banana"
#define TEST_SEED 0
#define DEBUG_LOG(...) printf(__VA_ARGS__)
#else
#define DEBUG_LOG(...)
#endif

#endif // __CONFIG_H__