#include <iostream>
#include <exception>
#include "calculator.h"

int main()
{
    double a, b;
    char op;
    std::cout<<"Enter Expression:";
    if(!(std::cin>>a>>op>>b))
    {
        std::cerr<<"Invalid Input!"<<std::endl;
        return 1;
    }
    try 
    {
        double result;
        switch(op)
        {
            case '+':
            {
                result = add(a, b);
                break;
            }
            case '-':
            {
                result = sub(a, b);
                break;
            }
            case '*':
            {
                result = mult(a, b);
                break;
            }
            case '/':
            {
                result = div(a, b);
                break;
            }

            default:
            {
                std::cerr<<"Wrong Operator!"<<std::endl;
                return 1;
            }
        }
        std::cout<<"Result = "<<result<<std::endl;
    }
    catch(const std::exception& e)
    {
        std::cerr<<"Error:"<<e.what()<<std::endl;
        return 1;
    }
    return 0;
}