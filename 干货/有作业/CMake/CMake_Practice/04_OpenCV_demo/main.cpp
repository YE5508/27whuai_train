#include <iostream>
#include <string>
#include "graphics/draw.h"
#include "utils/file_utils.h"

int main()
{
    const std::string output_dir = "output";
    const std::string output_file = output_dir + "/homework.png";
    if(!utils::ensure_directory(output_dir))
    {
        std::cerr <<"Failed to create output directory!"<<std::endl;
        return 1;
    }

    if(!graphics::make_image(output_file))
    {
        std::cerr << "Failed to create image!"<<std::endl;
        return 1;
    }
    std::cout << "Image Saved:"<<output_file<<std::endl;
    return 0;

}