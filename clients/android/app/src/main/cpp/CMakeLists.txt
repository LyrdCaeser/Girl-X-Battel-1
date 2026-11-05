cmake_minimum_required(VERSION 3.22.1)
project(gxb_battle)

set(LUAJIT_HEADERS "${CMAKE_CURRENT_LIST_DIR}/../../../../native/include")
set(LUAJIT_LIB "${CMAKE_CURRENT_LIST_DIR}/../jniLibs/${ANDROID_ABI}/libluajit.so")

if(NOT EXISTS "${LUAJIT_LIB}")
    message(FATAL_ERROR "Missing LuaJIT runtime for ABI ${ANDROID_ABI}: ${LUAJIT_LIB}")
endif()

add_library(luajit SHARED IMPORTED)
set_target_properties(luajit PROPERTIES
    IMPORTED_LOCATION "${LUAJIT_LIB}"
    INTERFACE_INCLUDE_DIRECTORIES "${LUAJIT_HEADERS}"
)

add_library(gxb_battle SHARED BattleRuntimeBridge.cpp)
target_include_directories(gxb_battle PRIVATE "${LUAJIT_HEADERS}")
target_compile_features(gxb_battle PRIVATE cxx_std_17)
target_compile_options(gxb_battle PRIVATE -fvisibility=hidden -Wall -Wextra -Werror)
target_link_libraries(gxb_battle PRIVATE luajit log m dl)
