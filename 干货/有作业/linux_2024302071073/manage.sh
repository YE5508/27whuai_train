#!/bin/bash

cd -- "$(dirname -- "${BASH_SOURCE[0]}")" || exit 1 

usage()
{
    echo "使用方法:"
    echo "  ./manage.sh tree"
    echo "  ./manage.sh check"
    echo "  ./manage.sh submit"
}

files=(
    "info.txt"
    "materials/commands.txt"
    "materials/bash.txt"
    "homework/task1.txt"
    "homework/task2.txt"
)

check_files()
{
    local missing=0
    local file

    for file in "${files[@]}"; do
        if [[ ! -f "$file" ]]; then
            echo "缺少文件: $file"
            missing=1
        else
            echo "文件存在: $file"
        fi
    done

    if [[ $missing -eq 0 ]]; then
        echo "所有文件都存在。"
    fi
    return "$missing"
}

if [[ $# -eq 0 ]]; then
    usage
    exit 0
fi

if [ "$#" -gt 1 ]; then
    echo "错误: 只能传递一个参数"
    usage
    exit 1
fi

case "$1" in
    tree)
        echo "个人信息"
        if [[ -f "info.txt" ]]; then
            cat "info.txt"
        else
            echo "缺少文件: info.txt"
        fi

        echo
        echo "项目目录"
        tree -I 'submit'  # 排除submit目录
        ;;
    check)
        check_files
        exit "$?"
        ;;
    submit)
        if check_files; then
            echo "提交作业..."
            # 在这里添加提交作业的逻辑
        else
            echo "请先修复缺失的文件，然后再提交作业。"
            exit 1
        fi
        if cp -- "${files[@]}" submit/; then
            echo "作业已成功提交到 submit 目录。"
            tree submit
        else
            echo "提交作业失败，请检查权限或路径。"
            exit 1
        fi
        ;;
    *)
        echo "错误: 未知参数 '$1'"
        usage
        exit 1
        ;;
esac

