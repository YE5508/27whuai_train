"""固定边缘核用于讲解卷积，不是训练好的水瓶检测器。"""
from pathlib import Path

import cv2
import numpy as np


def main():
    root = Path(__file__).resolve().parents[1]
    path = root / "assets/bottle_single.jpg"
    gray = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise FileNotFoundError(f"无法读图: {path}")
    kernel = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
    response = cv2.filter2D(gray.astype(np.float32), cv2.CV_32F, kernel)
    # 保留计算中的正负响应；这里只把绝对值归一化为显示图。
    display = cv2.normalize(np.abs(response), None, 0, 255,
                            cv2.NORM_MINMAX).astype(np.uint8)
    out_dir = root / "outputs"
    out_dir.mkdir(exist_ok=True)
    if not cv2.imwrite(str(out_dir / "fixed_kernel_edges.jpg"), display):
        raise RuntimeError("保存边缘示意失败")
    patch = np.arange(1, 10, dtype=np.float32).reshape(3, 3)
    print("手算局部响应（预期 6）:", float((patch * kernel).sum()))
    print("这张结果仅用于说明固定核响应，不代表模型特征可视化。")


if __name__ == "__main__":
    main()
