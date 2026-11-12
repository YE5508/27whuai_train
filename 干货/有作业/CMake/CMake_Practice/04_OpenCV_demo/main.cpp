#include <iostream>
#include <string>
#include <filesystem>
#include "graphics/draw.h"

int main()
{
    // 支持从工作区根目录或 04_OpenCV_demo 目录运行。
    const std::filesystem::path project_dir =
        std::filesystem::is_directory("04_OpenCV_demo") ? "04_OpenCV_demo" : ".";
    const std::string input_file = (project_dir / "images/raw/1.jpg").string();
    const std::string output_dir = (project_dir / "images/processed").string();

    if(!graphics::make_image(input_file, output_dir))
    {
        std::cerr << "Failed to process image!"<<std::endl;
        return 1;
    }
    std::cout << "Images saved to: " << output_dir << std::endl;
    return 0;

}
