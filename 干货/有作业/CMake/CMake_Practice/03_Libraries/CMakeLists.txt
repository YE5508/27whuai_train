cmake_minimum_required(VERSION 3.10)

project(score_system)

set(SRC_DIR ${PROJECT_SOURCE_DIR}/src)
set(INC_DIR ${PROJECT_SOURCE_DIR}/include)
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)
set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib)


include_directories(${INC_DIR})

# library按照功能和类型的不同分别制成库
add_library(stats STATIC ${SRC_DIR}/stats.cpp)
add_library(report SHARED ${SRC_DIR}/report.cpp)

# 可执行文件处只需要添加库之外的
add_executable(${PROJECT_NAME} main.cpp)

# 添加完可执行文件后,由于可执行文件依赖于库,所以需要将库链接到可执行文件上
target_link_libraries(${PROJECT_NAME} stats report)

#target_include_directories(${PROJECT_NAME} PUBLIC ${INC_DIR})
