add_library(graphics STATIC draw.cpp)
target_include_directories(graphics PUBLIC ${PROJECT_SOURCE_DIR}/include)
include_directories(${OpenCV_INCLUDE_DIRS})
target_link_libraries(graphics ${OpenCV_LIBS})