cmake_minimum_required(VERSION 3.18)
project(hangman_server
    VERSION 1.0 
    LANGUAGES C
)

set(CMAKE_C_STANDARD 11)
add_definitions(-D_POSIX_C_SOURCE=200809L)
add_compile_options(-Wall -Wextra -Werror -g)

add_compile_options(-pthread)
add_link_options(-pthread)

file(GLOB SOURCES "*.c")
add_executable(hangman_server ${SOURCES})