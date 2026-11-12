#include "graphics/draw.h"
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>

namespace graphics
{
    bool make_image(const std::string& file_path)
    {
        cv::Mat img(480, 720, CV_8UC3, cv::Scalar(245, 245, 245));
        cv::rectangle(img, cv::Point(60, 80), cv::Point(660, 400), cv::Scalar(240, 225, 210), cv::FILLED);
        cv::circle(img, cv::Point(260, 240), 85, cv::Scalar(60, 130, 245), cv::FILLED);
        cv::rectangle(img, cv::Point(380, 180), cv::Point(580, 300), cv::Scalar(95, 180, 90), cv::FILLED);
        cv::putText(img, "I Finished CMake Homework, Check it!", cv::Point(70, 55), cv::FONT_HERSHEY_SIMPLEX, 1.0, cv::Scalar(30, 30, 30), 2, cv::LINE_AA);
        return cv::imwrite(file_path, img);
    }
}