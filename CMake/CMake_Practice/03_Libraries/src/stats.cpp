#include "stats.h"
#include <algorithm>
#include <numeric>

namespace stats
{
    double average(const std::vector<double>& scores)
    {
        if(scores.empty())
        {
            return 0.0;
        }
        double total = std::accumulate(scores.begin(), scores.end(), 0.0);
        return total / scores.size();
    }
    double maximum(const std::vector<double>& scores)
    {
        if(scores.empty())
        {
            return 0.0;
        }
        return *std::max_element(scores.begin(), scores.end());
    }
}