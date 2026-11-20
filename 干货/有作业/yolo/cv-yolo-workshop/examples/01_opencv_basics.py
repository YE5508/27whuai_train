"""从培训资料目录运行。保存结果；--show 可选打开图形窗口。"""
import argparse
from pathlib import Path

import cv2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    path = root / "assets/bottle_single.jpg"
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"无法读图，请检查文件与编码: {path}")
    height, width = image.shape[:2]
    print("shape:", image.shape, "dtype:", image.dtype)
    print("top-left BGR:", image[0, 0])
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(image, (640, max(1, round(height * 640 / width))))
    crop = image[height // 4:3 * height // 4, width // 4:3 * width // 4]
    annotated = image.copy()
    # 人工框仅演示坐标与绘图，不代表模型检测。
    p1, p2 = (width // 4, height // 4), (3 * width // 4, 3 * height // 4)
    cv2.rectangle(annotated, p1, p2, (0, 220, 0), 3)
    cv2.circle(annotated, (width // 2, height // 2), 6, (0, 0, 255), -1)
    cv2.putText(annotated, "MANUAL EXAMPLE", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    out_dir = root / "outputs"
    out_dir.mkdir(exist_ok=True)
    for name, value in [("gray.jpg", gray), ("resized.jpg", resized),
                        ("crop.jpg", crop), ("manual_box.jpg", annotated)]:
        if not cv2.imwrite(str(out_dir / name), value):
            raise RuntimeError(f"保存失败: {name}")
    if args.show:
        try:
            cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
            cv2.namedWindow("Manual example", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Original", 600, 800)
            cv2.resizeWindow("Manual example", 600, 800)
            cv2.imshow("Original", image)
            cv2.imshow("Manual example", annotated)
            cv2.waitKey(0)
        finally:
            cv2.destroyAllWindows()
    print("结果已保存到:", out_dir)


if __name__ == "__main__":
    main()
