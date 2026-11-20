"""本地视频逐帧检测与方向判断；默认 CPU，--show 可选显示。"""
import argparse
import math
from pathlib import Path
from time import perf_counter

import cv2
from ultralytics import YOLO


def direction(cx, width, deadband=0.15):
    error = (cx - width / 2) / (width / 2)
    label = "LEFT" if error < -deadband else "RIGHT" if error > deadband else "CENTER"
    return label, error


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("video", nargs="?", default=str(root / "assets/bottle_move.mp4"))
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()
    if not 0 <= args.conf <= 1 or args.imgsz <= 0:
        parser.error("conf 必须在 [0,1]，imgsz 必须为正数")
    weights = root / "models/yolov8n.pt"
    if not weights.is_file():
        raise FileNotFoundError(f"请准备权重: {weights}")
    model = YOLO(str(weights))  # 只加载一次。
    bottle_ids = [int(i) for i, name in model.names.items() if name == "bottle"]
    if not bottle_ids:
        raise ValueError("当前模型没有 bottle 类")
    cap = cv2.VideoCapture(args.video)
    writer = None
    output_size = None
    count = 0
    out_dir = root / "outputs"
    out_dir.mkdir(exist_ok=True)
    target = out_dir / "bottle_move_detected.mp4"
    try:
        if not cap.isOpened():
            raise RuntimeError(f"无法打开视频: {args.video}")
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not math.isfinite(fps) or fps <= 0:
            print("无法读取源帧率，输出明确回退到 25 FPS")
            fps = 25.0
        if args.show:
            cv2.namedWindow("Bottle video", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Bottle video", 540, 720)
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            start = perf_counter()
            height, width = frame.shape[:2]
            if writer is None:
                output_size = (width, height)
                writer = cv2.VideoWriter(str(target), cv2.VideoWriter_fourcc(*"mp4v"),
                                         fps, output_size)
                if not writer.isOpened():
                    raise RuntimeError("无法创建输出视频，请检查编码与输出目录")
            if (width, height) != output_size:
                raise RuntimeError("视频帧尺寸发生变化，需先统一尺寸")
            result = model.predict(frame, classes=bottle_ids, conf=args.conf,
                                   imgsz=args.imgsz, device="cpu", verbose=False)[0]
            canvas = result.plot()
            cv2.line(canvas, (width // 2, 0), (width // 2, height - 1),
                     (255, 180, 0), 2)
            status = "LOST"
            boxes = result.boxes
            if boxes is not None and len(boxes):
                best = boxes[int(boxes.conf.argmax().item())]
                x1, y1, x2, y2 = best.xyxy[0].cpu().tolist()
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                status, error = direction(cx, width)
                status = f"{status}  ex={error:+.2f}"
                cv2.circle(canvas, (round(cx), round(cy)), 6, (0, 0, 255), -1)
            cv2.putText(canvas, status, (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                        0.9, (0, 220, 255), 2)
            # 此数值只覆盖读取成功后的推理与绘制，不是端到端 FPS。
            proc_fps = 1 / max(perf_counter() - start, 1e-9)
            cv2.putText(canvas, f"PROC FPS: {proc_fps:.1f}", (20, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 220, 255), 2)
            writer.write(canvas)
            count += 1
            if args.show:
                cv2.imshow("Bottle video", canvas)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        if count == 0:
            raise RuntimeError("没有读取到任何视频帧")
        print(f"写入 {count} 帧: {target}")
    finally:
        cap.release()
        if writer is not None:
            writer.release()
        if args.show:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
