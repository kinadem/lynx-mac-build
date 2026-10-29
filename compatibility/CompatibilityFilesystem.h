#pragma once

// ghc::filesystem provides file operations on systems whose libc++ predates
// std::filesystem. Its pinned implementation and MIT notice accompany the build.
#include "core/ghc_filesystem.hpp"

namespace lynx
{
namespace compatfs = ghc::filesystem;
namespace compatio
{
using ifstream = ghc::filesystem::ifstream;
using ofstream = ghc::filesystem::ofstream;
}
}
