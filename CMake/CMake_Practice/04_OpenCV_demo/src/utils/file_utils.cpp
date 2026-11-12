#include "utils/file_utils.h"
#include <filesystem>
#include <system_error>

namespace utils
{
    bool ensure_directory(const std::string& directory)
    {
        std::error_code ec;
        std::filesystem::create_directories(directory, ec);
        return !ec;
    }
}
