"""YOLOv8 图片检测参考；使用本地预训练权重和相邻素材目录。"""
import argparse
from pathlib import Path

import cv2
from ultralytics import YOLO


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", default=str(root / "assets/bottle_single.jpg"))
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    if not 0 <= args.conf <= 1 or args.imgsz <= 0:
        parser.error("conf 必须在 [0,1]，imgsz 必须为正数")
    weights = root / "models/yolov8n.pt"
    if not weights.is_file():
        raise FileNotFoundError(f"请先准备本地权重: {weights}")
    image = cv2.imread(args.image)
    if image is None:
        raise FileNotFoundError(f"无法读图: {args.image}")
    model = YOLO(str(weights))
    bottle_ids = [int(i) for i, name in model.names.items() if name == "bottle"]
    if not bottle_ids:
        raise ValueError("当前权重的类别映射中没有 bottle")
    result = model.predict(image, conf=args.conf, imgsz=args.imgsz,
                           classes=bottle_ids, device="cpu", verbose=False)[0]
    canvas = result.plot()
    boxes = result.boxes
    if boxes is None or len(boxes) == 0:
        print("LOST: 未检测到水瓶")
        cv2.putText(canvas, "LOST", (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (0, 0, 255), 2)
    else:
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().tolist()
            conf = float(box.conf[0].item())
            cls = int(box.cls[0].item())
            print(result.names[cls], f"conf={conf:.3f}",
                  "xyxy=", (x1, y1, x2, y2),
                  "center=", ((x1 + x2) / 2, (y1 + y2) / 2))
    out_dir = root / "outputs"
    out_dir.mkdir(exist_ok=True)
    target = out_dir / f"{Path(args.image).stem}_conf{args.conf:.2f}_detected.jpg"
    if not cv2.imwrite(str(target), canvas):
        raise RuntimeError(f"保存失败: {target}")
    if args.show:
        try:
            cv2.namedWindow("Bottle detection", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Bottle detection", 600, 800)
            cv2.imshow("Bottle detection", canvas)
            cv2.waitKey(0)
        finally:
            cv2.destroyAllWindows()
    print("结果:", target)


if __name__ == "__main__":
    main()
