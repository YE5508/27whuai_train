题目：制作一个课程项目管理工具

为本次的学习项目建立目录，并编写 manage.sh，实现查看目录、检查文件和提交作业三个功能。

## 一、准备项目目录：20 分

要求使用终端建立以下结构，将 2026001 替换为自己的学号：

linux_2026001/
├── manage.sh
├── info.txt
├── materials/
│   ├── commands.txt
│   └── bash.txt
├── homework/
│   ├── task1.txt
│   └── task2.txt
└── submit/

文件内容要求：

- info.txt：填写姓名和学号。
- commands.txt：填写本次用到的 Linux 命令及其作用。
- bash.txt：填写脚本首行的作用。
- task1.txt、task2.txt：分别填写一句学习心得。


### 二、查看目录：20 分

实现以下调用：

./manage.sh tree

要求：

1. 显示 info.txt 中的个人信息。
2. 使用 tree 展示项目目录。
3. 展示时不包含 submit 目录及其内容。
4. 不生成额外的目录清单文件。


### 三、检查作业是否齐全：25 分

实现：

./manage.sh check

检查以下 3 个文件是否存在：

info.txt
homework/task1.txt
homework/task2.txt

输出格式示例：

[存在] info.txt
[存在] homework/task1.txt
[缺失] homework/task2.txt

要求：

- 必须逐项显示检查结果，不能发现第一个缺失文件就直接停止。
- 这里只检查文件存在，不检查内容是否正确。
- 使用 if /for 循环。


### 四、生成提交目录：20 分

实现：

./manage.sh submit

要求：

1. 先检查 info.txt、task1.txt、task2.txt 是否都存在。
2. 缺少任意一个文件时，提示不能提交，并且不复制文件。
3. 文件齐全时，将这 3 个文件复制到 submit 目录，保留原文件。
4. 使用 tree 展示提交目录。

提交后的结果：

submit/
├── info.txt
├── task1.txt
└── task2.txt


### 五、参数和权限：15 分

要求：

- 脚本具有执行权限，能够使用 ./manage.sh 运行。
- 不提供参数时，显示使用说明。
- 输入不支持的操作时，提示“未知操作”，并显示支持的操作。
- 参数只能有一个，多于一个时提示参数数量错误。

例如：

使用方法：
./manage.sh tree
./manage.sh check
./manage.sh submit
