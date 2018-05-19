cmake_minimum_required(VERSION 3.1)
project(swe1r-tools)

set(CMAKE_C_STANDARD 11)

if(CMAKE_COMPILER_IS_GNUCC)
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -pedantic -Wextra -Wno-unused-parameter -Werror")
endif()

add_definitions(-D__cdecl=)

add_executable(decompress decompress.c)
add_executable(extract-data extract-data.c)
