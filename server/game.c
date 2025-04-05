#include "game.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define TIMEOUT_MS 10000

#if 1
#define DEBUG_LOG(...) printf(__VA_ARGS__);
#else
#define DEBUG_LOG(...)
#endif

typedef struct
{
    pthread_mutex_t mtx;

    void *owner;
    void *prev_owner;
    long long owned_at_time;
} boxlock_t;

struct game_t
{
    char *word;
    size_t wlen;
    char *boxes_state;
    boxlock_t *locks;
    void **player_ids;
    size_t player_cnt;
    long long box_timeout;

    pthread_mutex_t player_ids_mtx;
};

long long timestamp_ms()
{
    struct timespec ts;
    timespec_get(&ts, CLOCK_MONOTONIC);
    return ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

static void init_locks(game_t *game)
{
    for (size_t i = 0; i <= game->wlen; i++)
    {
        game->locks[i] = (boxlock_t){
            .mtx = PTHREAD_MUTEX_INITIALIZER,
            .owned_at_time = 0,
            .owner = NULL,
            .prev_owner = NULL,
        };
    }
}

game_t *game_create(char *word, size_t player_cnt, long long box_timeout_ms)
{
    game_t *g = malloc(sizeof(*g));
    g->box_timeout = box_timeout_ms;
    g->wlen = strlen(word);
    g->word = strdup(word);

    g->boxes_state = strdup(word);
    memset(g->boxes_state, '-', g->wlen);

    g->player_cnt = player_cnt;
    g->locks = malloc((g->wlen + 1) * sizeof(*g->locks));
    g->player_ids = malloc(player_cnt * sizeof(*g->player_ids));
    pthread_mutex_init(&g->player_ids_mtx, NULL);

    for (size_t i = 0; i < player_cnt; i++)
        g->player_ids[i] = NULL;

    init_locks(g);

    return g;
}

void game_free(game_t *game)
{
    free(game->player_ids);
    free(game->locks);
    free(game->word);
    free(game->boxes_state);
    free(game);
}

void game_add_player(game_t *game, void *player_id)
{
    pthread_mutex_lock(&game->player_ids_mtx);
    for (size_t i = 0; i < game->player_cnt; i++)
    {
        if (!game->player_ids[i])
        {
            game->player_ids[i] = player_id;
            break;
        }
    }
    pthread_mutex_unlock(&game->player_ids_mtx);
}

void **game_get_player_ids(game_t *game)
{
    return game->player_ids;
}

void update_lock_timeout(boxlock_t *lock)
{
    if (lock->owner && (timestamp_ms() - lock->owned_at_time > TIMEOUT_MS))
    {
        lock->prev_owner = lock->owner;
        lock->owner = NULL;
    }
}

bool box_is_guessable(game_t *game, unsigned int box_index)
{
    DEBUG_LOG("check if box %u is guessable\n", box_index);
    if (box_index == game->wlen)
    {
        if (!strcmp(game->boxes_state, game->word))
            return false;
    }
    else if (game->boxes_state[box_index] == game->word[box_index])
    {
        return false;
    }

    return true;
}

bool game_request_box(game_t *game, void *player_id, unsigned int box_index)
{
    if (box_index > game->wlen)
        return false;

    if (!box_is_guessable(game, box_index))
        return false;

    boxlock_t *lock = &game->locks[box_index];
    bool ret = false;

    pthread_mutex_lock(&lock->mtx);

    update_lock_timeout(lock);

    if (!lock->owner)
    {
        lock->owned_at_time = timestamp_ms();
        lock->owner = player_id;
        ret = true;
    }

    pthread_mutex_unlock(&game->locks[box_index].mtx);

    return ret;
}

bool check_guess(game_t *game, char *guess, unsigned int box_index)
{
    bool ret;
    if (box_index == game->wlen)
    { // whole word guess
        DEBUG_LOG("guessing whole word %s: %s\n", game->word, guess);
        ret = !strcmp(game->word, guess);
        if (ret)
        {
            strcpy(game->boxes_state, game->word);
            DEBUG_LOG("boxes state: %s\n", game->boxes_state);
        }
    }
    else
    { // letter guess
        DEBUG_LOG("guessing letter %u of %s: %s\n", box_index, game->word, guess);
        ret = game->word[box_index] == guess[0] && guess[1] == '\0';
        if (ret)
        {
            game->boxes_state[box_index] = game->word[box_index];
            DEBUG_LOG("boxes state: %s\n", game->boxes_state);
        }
    }

    return ret;
}

bool game_guess(game_t *game, void *player_id, unsigned int box_index, char *guess)
{
    if (box_index > game->wlen)
        return false;

    assert(guess);

    boxlock_t *lock = &game->locks[box_index];
    bool ret = false;

    pthread_mutex_lock(&lock->mtx);

    update_lock_timeout(lock);

    if (lock->owner && lock->owner == player_id)
    {
        if (check_guess(game, guess, box_index))
            ret = true;

        lock->prev_owner = lock->owner;
        lock->owner = NULL;
    }

    pthread_mutex_unlock(&lock->mtx);

    return ret;
}

void game_unlock_boxes(game_t *game, void *player_id)
{
    for (size_t i = 0; i <= game->wlen; i++)
    {
        boxlock_t *lock = &game->locks[i];

        pthread_mutex_lock(&lock->mtx);

        update_lock_timeout(lock);

        if (lock->owner == player_id)
            lock->prev_owner = lock->owner;
        lock->owner = NULL;

        pthread_mutex_unlock(&lock->mtx);
    }
}

char *game_get_boxes_state(game_t *game)
{
    return strdup(game->boxes_state);
}

const char *game_get_word(game_t *game)
{
    return game->word;
}