#!/bin/bash 
# 字符串变量创建和赋值,如果要取用(常用作地址)变量,需要加上$符号
name="叶劭铨"
student_id="2024302071073"
project="linux_${student_id}"

# 目录创建
mkdir -p "$project"/{materials,homework,submit}

# 文件创建
touch "$project/manage.sh"

# 文件权限修改
chmod +x "$project/manage.sh"


# cat命令用于创建并写入文件,第一个EOF前写地址,第二个EOF前写内容,EOF前不能有空格
cat >"$project/info.txt" <<EOF
姓名: $name
学号: $student_id
EOF

cat >"$project/materials/commands.txt" <<EOF
mkdir -p: 创建目录,如果上级目录不存在,则一并创建
touch: 创建文件,如果文件已存在,则更新文件的访问和修改时间
chmod: 修改文件权限,常用的权限有r(读),w(写),x(执行)
cat: 查看文件内容,也可用于创建文件并写入内容
cd: 切换目录,cd ..表示切换到上级目录
cp: 复制文件或目录,cp -r表示递归复制目录
mv: 移动文件或目录,也可用于重命名文件或目录
EOF

cat >"$project/materials/bash.txt" <<EOF
#!/bin/bash: 声明脚本的解释器为bash,有点类似于给某一编程语言指定编译器
EOF

cat >"$project/homework/task1.txt" <<EOF
学会Linux常用命令,并能熟练使用
EOF

cat >"$project/homework/task2.txt" <<EOF
学会bash脚本语法
包括变量、条件判断、case多分支,循环,函数等
EOF



