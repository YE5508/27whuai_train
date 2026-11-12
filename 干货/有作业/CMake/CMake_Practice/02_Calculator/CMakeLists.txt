cmake_minimum_required(VERSION 3.10)

project(Calculator)

set(SRC_DIR ${PROJECT_SOURCE_DIR}/src)
set(INC_DIR ${PROJECT_SOURCE_DIR}/include)
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)

include_directories(${INC_DIR})

file(GLOB SRC_FILES ${SRC_DIR}/*.cpp)
add_executable(${PROJECT_NAME} ${SRC_FILES})

#target_include_directories(${PROJECT_NAME} PUBLIC ${INC_DIR})
