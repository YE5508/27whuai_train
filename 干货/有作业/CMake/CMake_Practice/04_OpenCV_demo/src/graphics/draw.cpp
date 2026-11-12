#include "graphics/draw.h"
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#include <filesystem>
#include <iostream>
#include <system_error>
#include <vector>

namespace graphics
{
    bool make_image(const std::string& input_path, const std::string& output_dir)
    {
        try
        {
            const cv::Mat img = cv::imread(input_path, cv::IMREAD_COLOR);
            if (img.empty())
            {
                std::cerr << "Failed to read image: " << input_path << '\n';
                return false;
            }

            std::error_code ec;
            std::filesystem::create_directories(output_dir, ec);
            if (ec)
            {
                std::cerr << "Failed to create output directory: " << ec.message() << '\n';
                return false;
            }

            // 先转灰度、去噪，再使用 Otsu 自动选择阈值进行二值化。
            cv::Mat gray, blurred, binary;
            cv::cvtColor(img, gray, cv::COLOR_BGR2GRAY);
            cv::GaussianBlur(gray, blurred, cv::Size(5, 5), 0);
            cv::threshold(blurred, binary, 0, 255, cv::THRESH_BINARY | cv::THRESH_OTSU);

            // 从二值图中提取所有轮廓（包括内部轮廓）。
            std::vector<std::vector<cv::Point>> contours;
            cv::findContours(binary.clone(), contours, cv::RETR_LIST,
                             cv::CHAIN_APPROX_SIMPLE);
            cv::Mat contour_image = cv::Mat::zeros(img.size(), CV_8UC1);
            cv::drawContours(contour_image, contours, -1, cv::Scalar(255), 1);

            const auto directory = std::filesystem::path(output_dir);
            const bool binary_saved = cv::imwrite((directory / "1_binary.png").string(), binary);
            const bool contours_saved = cv::imwrite((directory / "1_contours.png").string(), contour_image);
            if (!binary_saved || !contours_saved)
            {
                std::cerr << "Failed to save processed images: " << output_dir << '\n';
                return false;
            }
            std::cout << "Contours found: " << contours.size() << '\n';
            return true;
        }
        catch (const cv::Exception& error)
        {
            std::cerr << "Image processing failed: " << error.what() << '\n';
            return false;
        }
    }
}
