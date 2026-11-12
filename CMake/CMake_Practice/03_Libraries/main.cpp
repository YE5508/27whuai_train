#include <iostream>
#include <vector>
#include "stats.h"
#include "report.h"

int main()
{
    std::vector<double> scores = {90, 85, 96, 79, 91};
    double avg = stats::average(scores);
    double max = stats::maximum(scores);
    std::cout<<"Students Score Report\n";
    std::cout<<report::make_report(avg, max)<<std::endl;
    return 0;
}