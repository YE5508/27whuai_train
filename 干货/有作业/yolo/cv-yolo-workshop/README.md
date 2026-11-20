# Ubuntu 学生安装与实操指南

本目录新增了 **CPU / ORB 课后作业 B**，独立环境与复现方法见本文第 12 节。该作业的最小依赖环境不包含 PyTorch、Ultralytics；运行原有 YOLO 示例仍需安装原课程依赖。

OpenCV + CNN + YOLOv8 水瓶检测｜2026-11-14。

所有同学均使用 Ubuntu。本指南只保留 Ubuntu 原生 Python 和教学 Docker 两条路线。示例不依赖 Docker API；Docker 只是预先安装好依赖的环境。原生 Ubuntu 安装相同依赖后可以运行同一份代码，所有检测示例使用 CPU，不要求 NVIDIA 显卡。

## 1. 取得学生包，确认 Ubuntu 和 Python 版本

解压“学生实操包.zip”，进入 cv-yolo-workshop 文件夹。以下命令均在这个目录执行。若资料放在其他位置，先 cd 到自己的实际位置，不要原样复制不存在的示例路径。

```bash
cd ~/cv-yolo-workshop
cat /etc/os-release
python3 --version
uname -m
```

本套固定版本面向 x86_64 Ubuntu、Python 3.8–3.11。20.04 默认通常是 Python 3.8，22.04 默认通常是 Python 3.10；这两种可以走第 2 节。24.04 默认通常是 Python 3.12，应走第 3 节，不能直接将这里固定的 NumPy 1.24.4 安装到 Python 3.12。

已实际验证：Ubuntu 20.04 / Python 3.8.10 的独立教学容器、全部代码与素材，以及学生包解压后的独立目录运行。22.04、24.04 的原生安装步骤尚未在对应系统实机执行，课前应完成本指南的导入与图片检测验证。

不要替换系统 /usr/bin/python3，也不要用 sudo pip 安装本课程依赖。每名学生创建自己的 .venv。

## 2. Ubuntu 20.04 / 22.04：创建虚拟环境

先安装解释器对应的基础工具和 OpenCV 所需系统动态库：

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip libgl1 libglib2.0-0
python3 -m venv .venv
source .venv/bin/activate
python --version
python -m pip install --upgrade pip
```

确认当前 Python 是 3.8、3.9、3.10 或 3.11，然后跳到第 4 节安装软件。重新打开终端时，只需进入同一资料目录并再次 source .venv/bin/activate，不需要重建环境或重复安装。

## 3. Ubuntu 24.04：另外准备 Python 3.10

本节只用于默认 Python 3.12 的电脑。通过 uv 管理一份独立 Python 3.10，不更换 Ubuntu 系统 Python：

```bash
sudo apt-get update
sudo apt-get install -y python3-venv libgl1 libglib2.0-0
# bootstrap 环境仅用来安装 uv
python3 -m venv .python-bootstrap
.python-bootstrap/bin/python -m pip install uv -i https://pypi.tuna.tsinghua.edu.cn/simple
.python-bootstrap/bin/uv python install 3.10
.python-bootstrap/bin/uv venv --python 3.10 --seed .venv
source .venv/bin/activate
python --version
```

此处预期显示 Python 3.10.x，然后继续第 4 节。uv 下载 Python 时需要联网，课前先验证网络；不要临时更改系统 Python 的符号链接。若机器已经安装了 Python 3.10/3.11，可直接用 python3.10 -m venv .venv 或 python3.11 -m venv .venv，不必额外安装 uv。

## 4. 下载并安装 OpenCV

在已激活的 .venv 中执行：

```bash
python -m pip install numpy==1.24.4 opencv-python==4.10.0.84 -i https://pypi.tuna.tsinghua.edu.cn/simple
python -c "import cv2; print(cv2.__version__)"
```

预期输出 4.10.0。发行包名是 opencv-python，Python 导入名是 cv2。现在就可以先运行读图和固定卷积核实验：

```bash
python examples/01_opencv_basics.py --show
python examples/02_convolution.py
```

普通 opencv-python 支持本课的图形窗口；不要另行混装 opencv-python-headless 或多个共享 cv2 名称的 OpenCV wheel。

## 5. 下载并安装 PyTorch、Ultralytics

先安装官方 CPU 版 PyTorch 和 torchvision：

```bash
python -m pip install --no-deps torch==2.2.2 torchvision==0.17.2 --index-url https://download.pytorch.org/whl/cpu
```

--no-deps 表示这一步先安装两个主包，下一步再完整安装通用依赖，避免把所有通用依赖都从较慢的 PyTorch 下载站获取。完成下一步之前不要急着导入 torch。

从学生包根目录执行完整安装：

```bash
python -m pip install -r requirements-student.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip check
```

若使用教师电脑原“培训资料”目录而不是精简学生包，将 requirements-student.txt 改为 environment/requirements-student.txt。

安装清单已包含 numpy、opencv-python、torch、torchvision、ultralytics 的固定版本。所谓“安装 YOLO”，这里实际安装的是 Ultralytics Python 接口；YOLOv8 模型权重在下一节。

课堂解释单个包名时可以展示这条命令：

```bash
python -m pip install ultralytics==8.3.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

它用于说明包名；完整环境安装仍按 requirements-student.txt，避免单独安装时自动选到不同版本依赖。

验证环境：

```bash
python -c "import sys; print(sys.executable)"
python -c "import cv2; print('OpenCV:',cv2.__version__)"
python -c "import torch,torchvision; print('torch:',torch.__version__,'torchvision:',torchvision.__version__)"
python -c "import ultralytics; print('ultralytics:',ultralytics.__version__)"
```

预期 OpenCV 4.10.0、torch 2.2.2+cpu、torchvision 0.17.2+cpu、ultralytics 8.3.0；pip check 没有损坏的依赖。所有安装都在学生自己的 .venv 内。

## 6. 下载 YOLOv8 权重

学生包已附 models/yolov8n.pt，正常上课可以直接使用，不必重复下载。软件包是接口代码与依赖；.pt 文件保存预训练模型数据。

需要完整演示下载过程时，从资料根目录执行：

```bash
python -c "from urllib.request import urlretrieve; urlretrieve('https://huggingface.co/Ultralytics/YOLOv8/resolve/main/yolov8n.pt','models/yolov8n.pt')"
```

官方站超时时，可使用本次可访问的镜像，并核对官方 SHA256：

```bash
python -c "from urllib.request import urlretrieve; urlretrieve('https://hf-mirror.com/Ultralytics/YOLOv8/resolve/main/yolov8n.pt','models/yolov8n.pt')"
python -c "import hashlib; from pathlib import Path; s=hashlib.sha256(Path('models/yolov8n.pt').read_bytes()).hexdigest(); print(s); assert s=='31e20dde3def09e2cf938c7be6fe23d9150bbbe503982af13345706515f2ef95'"
```

本课使用官方预训练权重进行推理，不用这五张图片重新训练。

## 7. 运行图片与视频检测

下面命令在已激活的虚拟环境、资料根目录执行，不使用 Docker 命令：

```bash
# 图片检测，按任意键关闭窗口
python examples/03_detect_bottle.py assets/bottle_01.jpg --show
# 换图并调整阈值
python examples/03_detect_bottle.py assets/bottle_04.jpg --conf 0.50 --show
# 第一张置信度约 0.912，0.95 阈值会过滤这次预测
python examples/03_detect_bottle.py assets/bottle_01.jpg --conf 0.95 --show
# 视频与方向判断，按 q 退出
python examples/04_video_bottle.py assets/bottle_move.mp4 --show
# 原 HEVC 视频无法解码时，使用随包提供的 H.264 兼容副本
python examples/04_video_bottle.py assets/bottle_move_h264.mp4 --show
```

结果保存到自动创建的 outputs。无图形桌面时去掉 --show，先保存再查看。H.264 兼容副本保留全部 257 帧、去掉音轨；视觉实验不需要声音。

## 8. 学生包目录和代码位置

```text
cv-yolo-workshop/
  README.md                         本指南
  课堂课件.pptx                    含 Ubuntu 安装命令与课堂内容
  requirements-student.txt          学生安装清单
  examples/
    01_opencv_basics.py             读取、显示、裁剪、标注、保存
    02_convolution.py               固定卷积核响应
    03_detect_bottle.py             图片检测与阈值
    04_video_bottle.py              视频检测与方向
  assets/
    bottle_single.jpg
    bottle_01.jpg ... bottle_05.jpg
    bottle_move.mp4
    bottle_move_h264.mp4
  models/
    yolov8n.pt
    model-source.json
```

保留 examples、assets、models 的相对关系。脚本根据自身位置寻找默认素材；命令行参数中的相对文件路径则相对当前工作目录。只复制 .py 文件会找不到权重与默认素材。

## 9. 已有教学 Docker 的同学

教师电脑已经配好 cv_yolo_teach，可以直接进入：

```bash
docker start cv_yolo_teach
docker exec -it cv_yolo_teach bash
cd /workshop
python3 examples/03_detect_bottle.py assets/bottle_01.jpg --show
```

学生自己电脑不一定已经有这个容器。要从头使用 Docker，教师资料里的 environment/Dockerfile 是完整构建配方，environment/install_python.sh 是本次容器 Python 安装脚本；使用已安装环境看《环境与演示操作.md》。

从完整“培训资料”目录构建新镜像：

```bash
docker build -t opencv-yolov8-student:local -f environment/Dockerfile .
```

构建镜像不自动创建教师容器，也不自动配置 GUI。学生选择原生 Ubuntu 路线时，执行第 2–7 节即可，不需要执行本节。

## 10. 常见问题

| 现象 | 首先检查 |
| --- | --- |
| No matching distribution found | 是否 Python 3.8–3.11、x86_64，而不是默认 3.12 |
| No module named cv2/torch | sys.executable 与 python -m pip 是否属于同一 .venv |
| externally-managed-environment | 是否忘记激活虚拟环境；不要强行破坏系统包管理 |
| 找不到模型/图片 | 是否完整解压、保留目录关系、从资料根目录执行相对路径 |
| imshow 报错 | 是否普通 opencv-python、有图形桌面；可去掉 --show |
| 缺少 libGL.so.1 | 安装 libgl1；缺其他动态库时按报错定位 |
| 原视频读不到第一帧 | 使用 H.264 兼容副本，检查文件路径与解码支持 |
| 没有 NVIDIA 显卡 | 示例明确使用 CPU，可以继续运行 |
| 目标没检出 | 检查阈值、输入与权重，正确处理 LOST |

容器原始 requirements-lock.txt 含本机 /opt/wheelhouse 路径和 pkg_resources 占位记录，不能直接当作学生安装清单。学生用 requirements-student.txt。

## 11. 官方参考与验证范围

- PyTorch 2.2.2 CPU 安装方式：https://pytorch.org/get-started/previous-versions/#v222
- Python 虚拟环境：https://docs.python.org/3.11/library/venv.html
- uv 安装与独立 Python 管理：https://docs.astral.sh/uv/getting-started/installation/ ；https://docs.astral.sh/uv/guides/install-python/
- Ultralytics 8.3.0：https://pypi.org/project/ultralytics/8.3.0/
- YOLOv8：https://docs.ultralytics.com/models/yolov8/
- 权重及官方 SHA256：https://huggingface.co/Ultralytics/YOLOv8/blob/main/yolov8n.pt

学生包已在当前已配置好的 Ubuntu 教学容器中解压到全新英文目录，运行相同图片检测命令，成功检出 bottle、分数约 0.912。这个检查验证资料包自带代码/素材/权重路径完整；不等于已经在每个 Ubuntu 版本从头安装过。

## 12. 课后作业 B：CPU / ORB 特征匹配

作业使用 Python 3.10、NumPy 1.24.4、OpenCV 4.10.0.84，ReportLab 用于生成一页中文 PDF。环境位于本项目 `.venv`，不继承系统 Python 包；uv 缓存位于 `.cache/uv`。已锁定全部依赖及下载哈希，参考 uv 版本为 0.10.9。

在项目根目录重建环境：

```bash
uv venv --python /usr/bin/python3 .venv
uv pip sync --python .venv/bin/python --require-hashes requirements-homework.lock
uv pip check --python .venv/bin/python
```

上述解释器路径适用于本机 Ubuntu 22.04 / Python 3.10；其他机器需指定自己的 Python 3.10。无需激活也可以直接调用 `.venv/bin/python`。`sync` 将该虚拟环境同步为作业 B 的最小依赖；不要将其他项目的软件装入这个环境。

根目录的 `book_*.jpg` 是六本不同书从 Open Library 获取的封面；`book_sources.json` 保存来源、授权说明、下载尺寸和 SHA256。API 未提供各封面的单独授权，不能据此声称封面属于公有领域。没有修改下载的原始图片。重新获取素材需联网：

```bash
.venv/bin/python scripts/download_books.py
```

下载脚本不覆盖内容不同的已有同名图片。素材已经齐全时无需联网，按顺序运行：

```bash
.venv/bin/python examples/05_orb_homework.py
.venv/bin/python scripts/build_homework_report.py
pdfinfo outputs/homework_b/ORB课后作业报告.pdf
```

PDF 生成使用本机已有的 DroidSansFallbackFull 中文字体与 DejaVuSans 西文字体，分别位于 `/usr/share/fonts/truetype/droid/` 和 `/usr/share/fonts/truetype/dejavu/`；在其他电脑上需提供这些字体或调整报告脚本中的字体路径。

实验按书本进行 3/3 调参与测试划分，随机种子为 42；所有变换图留在原书所属分组。最长边不超过 900 像素，旋转 30°，灰度等效高斯噪声标准差为 0/15/45，每个等级仅一次固定随机采样。固定 ORB 1000 个特征，双向一致 Hamming 匹配后按距离保留前 10/30/100 个。原图及同一噪声图在不同 K 下完全相同，真实旋转矩阵用于判断匹配正确性与四角定位误差。正样本均为合成变换，本次未做跨书本负对照或真实拍摄实验。

调参规则在实验前写入 `config.json`；调参集评估后把选定 K 写入 `selection.json`，再处理测试集。调参优先比较定位成功率，同分比较惩罚后的平均角点误差，再同分选择较小 K。无法估计的误差按目标图对角线两倍惩罚，大于此值的误差按此值截断。报告公开测试集三个 K 的预定对照结果，但不据此重新调参。

输出均位于 `outputs/homework_b/`：

- `ORB课后作业报告.pdf`：一页中文报告，包含猜想、方法、数据、对照图与失败分析。
- `metrics.csv` / `metrics.json`：54 项实验的匹配正确率、定位成功与角点误差；`summary.json` 为分组汇总。
- `config.json` / `selection.json` / `transforms.json`：分组、参数、调参选择及真实变换矩阵。
- `inputs/` / `transforms/` / `matches/`：缩放图、变换图及全部匹配连线图。绿色表示真实变换验证正确的匹配，红色表示错误匹配。
- `failure_case.json`、`comparison_k10.jpg`、`comparison_k100.jpg`：测试集中定位最差条件的数据与对照图。

实验不训练模型权重。小样本结果用于检验猜想，不能确定通用最佳数量范围或证明“过拟合”。若需重新锁定依赖，执行 `uv pip compile requirements-homework.in --generate-hashes -o requirements-homework.lock`，再同步环境。
