#include <jni.h>
#include <android/log.h>

#include <cerrno>
#include <cstdio>
#include <cstring>
#include <string>
#include <unistd.h>

extern "C" {
#include "lua.h"
#include "lauxlib.h"
#include "lualib.h"
}

namespace {
constexpr const char* TAG = "GxbBattleRuntime";

struct OutputCapture {
    std::string output;
};

thread_local OutputCapture* current_capture = nullptr;

std::string lua_error(lua_State* state, const char* phase) {
    const char* message = lua_tostring(state, -1);
    std::string result = phase;
    result += ": ";
    result += message ? message : "unknown Lua error";
    return result;
}

int capture_print(lua_State* state) {
    if (current_capture == nullptr) return 0;
    int count = lua_gettop(state);
    for (int i = 1; i <= count; ++i) {
        if (i > 1) current_capture->output.push_back('\t');
        const char* value = lua_tostring(state, i);
        if (value != nullptr) current_capture->output += value;
    }
    current_capture->output.push_back('\n');
    return 0;
}

bool valid_mode(const char* mode) {
    return mode != nullptr && (std::strcmp(mode, "battle") == 0 || std::strcmp(mode, "attrs") == 0);
}

void push_arg(lua_State* state, int index, const char* value) {
    lua_pushstring(state, value);
    lua_rawseti(state, -2, index);
}

std::string last_nonempty_line(const std::string& output) {
    size_t end = output.size();
    while (end > 0 && (output[end - 1] == '\n' || output[end - 1] == '\r')) --end;
    size_t begin = output.rfind('\n', end == 0 ? 0 : end - 1);
    begin = begin == std::string::npos ? 0 : begin + 1;
    return output.substr(begin, end - begin);
}

jstring throw_error(JNIEnv* env, const std::string& message) {
    __android_log_print(ANDROID_LOG_ERROR, TAG, "%s", message.c_str());
    jclass exception = env->FindClass("java/lang/IllegalStateException");
    if (exception != nullptr) env->ThrowNew(exception, message.c_str());
    return nullptr;
}
} // namespace

extern "C" JNIEXPORT jstring JNICALL
Java_com_quangho_goddess_battle_BattleRuntimeBridge_nativeRunBattle(
        JNIEnv* env, jclass /* clazz */, jstring runtime_root, jstring input_path, jstring mode) {
    if (runtime_root == nullptr || input_path == nullptr || mode == nullptr) {
        return throw_error(env, "battle JNI: null argument");
    }

    const char* root_chars = env->GetStringUTFChars(runtime_root, nullptr);
    const char* input_chars = env->GetStringUTFChars(input_path, nullptr);
    const char* mode_chars = env->GetStringUTFChars(mode, nullptr);
    if (root_chars == nullptr || input_chars == nullptr || mode_chars == nullptr) {
        if (root_chars) env->ReleaseStringUTFChars(runtime_root, root_chars);
        if (input_chars) env->ReleaseStringUTFChars(input_path, input_chars);
        if (mode_chars) env->ReleaseStringUTFChars(mode, mode_chars);
        return throw_error(env, "battle JNI: cannot read arguments");
    }

    const std::string root(root_chars);
    const std::string input(input_chars);
    const std::string selected_mode(mode_chars);
    env->ReleaseStringUTFChars(runtime_root, root_chars);
    env->ReleaseStringUTFChars(input_path, input_chars);
    env->ReleaseStringUTFChars(mode, mode_chars);

    if (!valid_mode(selected_mode.c_str())) return throw_error(env, "battle JNI: unsupported mode");
    if (root.empty() || input.empty() || root.find("..") != std::string::npos || input.find("..") != std::string::npos) {
        return throw_error(env, "battle JNI: invalid runtime path");
    }

    const std::string host = root + "/battle_host.lua";
    if (access(host.c_str(), R_OK) != 0 || access(input.c_str(), R_OK) != 0) {
        return throw_error(env, std::string("battle JNI: runtime/input unavailable: ") + std::strerror(errno));
    }

    lua_State* state = luaL_newstate();
    if (state == nullptr) return throw_error(env, "battle JNI: luaL_newstate failed");
    luaL_openlibs(state);

    OutputCapture capture;
    current_capture = &capture;
    lua_pushcfunction(state, capture_print);
    lua_setglobal(state, "print");

    // Reproduce battle_host.lua's CLI contract: arg[1]=module root,
    // arg[2]=mode, arg[3]=input file. The host remains the source of truth
    // for battle rules and report generation.
    lua_newtable(state);
    push_arg(state, 1, root.c_str());
    push_arg(state, 2, selected_mode.c_str());
    push_arg(state, 3, input.c_str());
    lua_setglobal(state, "arg");

    int status = luaL_loadfile(state, host.c_str());
    if (status == 0) status = lua_pcall(state, 0, 0, 0);
    if (status != 0) {
        std::string message = lua_error(state, status == LUA_ERRMEM ? "battle JNI memory error" : "battle JNI Lua error");
        current_capture = nullptr;
        lua_close(state);
        return throw_error(env, message);
    }
    current_capture = nullptr;
    lua_close(state);

    std::string report = last_nonempty_line(capture.output);
    if (report.empty() || report.front() != '{' || report.back() != '}') {
        return throw_error(env, "battle JNI: battle_host.lua returned no JSON report");
    }
    return env->NewStringUTF(report.c_str());
}
