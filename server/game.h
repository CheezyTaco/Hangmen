#ifndef __GAME_H__
#define __GAME_H__

#include <stdbool.h>
#include <stdlib.h>
#include <pthread.h>

typedef struct game_t game_t;

game_t *game_create(char *word, size_t player_cnt, long long box_timeout_ms);
void game_free(game_t *game);

void game_add_player(game_t *game, void *player_id);
void **game_get_player_ids(game_t *game);

bool game_request_box(game_t *game, void *player_id, unsigned int box_index);
bool game_guess(game_t *game, void *player_id, unsigned int box_index, char *guess);
void game_unlock_boxes(game_t *game, void *player_id);

char *game_get_boxes_state(game_t *game);
bool game_is_won(game_t *game);

#endif // __GAME_H__