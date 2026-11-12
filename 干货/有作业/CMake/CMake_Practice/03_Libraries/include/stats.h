#ifndef STATS_H
#define STATS_H

#include <vector>

namespace stats
{
    double average(const std::vector<double>& scores);
    double maximum(const std::vector<double>& scores);
}

#endif