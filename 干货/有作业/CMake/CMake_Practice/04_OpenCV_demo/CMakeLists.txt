cmake_minimum_required(VERSION 3.10)
project(image_processing)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(OpenCV REQUIRED COMPONENTS core imgproc imgcodecs)

set(SRC_DIR ${PROJECT_SOURCE_DIR}/src)
set(INC_DIR ${PROJECT_SOURCE_DIR}/include)
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)
set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib)


add_library(graphics STATIC ./src/graphics/draw.cpp)
target_include_directories(graphics PUBLIC ${INC_DIR})
target_include_directories(graphics SYSTEM PRIVATE ${OpenCV_INCLUDE_DIRS})
target_link_libraries(graphics PUBLIC ${OpenCV_LIBS})

# 可执行文件处只需要添加库之外的源文件
add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} graphics)
