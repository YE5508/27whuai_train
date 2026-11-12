#include "calculator.h"
#include <stdexcept>
double div(double a, double b)
{
	if(b == 0)
	{
		throw std::invalid_argument("Divided by ZERO");

	}
	return a / b;
}
	

