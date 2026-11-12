#include "report.h"
#include <sstream>
#include <iomanip>

namespace report
{
    std::string make_report(double avg, double maximum)
    {
        std::ostringstream oss;
        oss<<std::fixed <<std::setprecision(2);
        oss<<"Average="<<avg<<"\n";
        oss<<"Maximum="<<maximum<<"\n";
        return oss.str();
    }
} 