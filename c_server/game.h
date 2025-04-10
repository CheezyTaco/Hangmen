#ifndef __GAME_H__
#define __GAME_H__

#include <stdbool.h>
#include <stdlib.h>
#include <pthread.h>

typedef struct game_t game_t;

/**
 * Create a hangman game instance
 * 
 * Returns heap allocated game_t, which should be freed with game_free()
 */
game_t *game_create(char *word, size_t player_cnt, long long box_timeout_ms);
void game_free(game_t *game);

/**
 * Add a player to the game
 * 
 * player_id can be any unique identifier, be it a pointer to a string of the
 * player's name or an integer. It cannot be NULL or 0.
 */
void game_add_player(game_t *game, void *player_id);

/**
 * Get an array of currently added players.
 * 
 * The returned array has the same size as the player_cnt parameter passed to
 * game_create. Empty slots are NULL.
 * 
 * The array is heap allocated, and should be freed with free()
 */
void **game_get_player_ids(game_t *game);

/**
 * Try to take ownership of the box at box_index for player_id
 * 
 * Returns true if the box is successfully taken. 
 * Returns false if
 * - the box is already taken by another player
 * - the box has already been correctly guessed
 * - box_index is out of bounds.
 */
bool game_request_box(game_t *game, void *player_id, unsigned int box_index);

/**
 * Make a guess at box_index for player_id
 * 
 * Returns true if the guess was correct. 
 * Returns false if
 * - player_id does not own the box
 * - player_id's ownership of the box expired
 * - the box has already been correctly guessed (can happen if the whole word
 *  was guessed correctly)
 * - box_index is out of bounds
 */
bool game_guess(game_t *game, void *player_id, unsigned int box_index, char *guess);

/**
 * Unlock all boxes owned by player_id
 */
void game_unlock_boxes(game_t *game, void *player_id);

/**
 * Get the current state of guesses
 * 
 * Returns the word, but with letters that haven't correctly been guessed 
 * replaced with '-' characters.
 * 
 * If the word to guess is 'money', this would initially return '-----'.
 * After the m, o, and y have been correctly guessed, it would return 'mo--y'
 */
char *game_get_boxes_state(game_t *game);

/**
 * Check if the game has been won
 */
bool game_is_won(game_t *game);

const char *game_get_word(game_t *game);

#endif // __GAME_H__