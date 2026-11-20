"""Reproducible CPU-only ORB experiment; run from any working directory."""
import csv
import hashlib
import json
import math
import random
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/homework_b'
SEED = 42
KS = (10, 30, 100)
SIGMAS = (0, 15, 45)


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False),
                    encoding='utf-8')


def write_image(path, image):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image):
        raise RuntimeError(f'Cannot save {path}')


def project(points, matrix):
    return cv2.perspectiveTransform(np.asarray(points, np.float32).reshape(-1, 1, 2),
                                    matrix).reshape(-1, 2)


def prepare(record, index):
    path = ROOT / record['file']
    if hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
        raise ValueError(f'Original changed: {path}')
    original = cv2.imread(str(path))
    if original is None:
        raise ValueError(f'Cannot read {path}')
    scale = min(1.0, 900 / max(original.shape[:2]))
    image = cv2.resize(original, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    h, w = image.shape[:2]
    # Expanded canvas preserves all four original corners.
    affine = cv2.getRotationMatrix2D((w / 2, h / 2), 30, 1.0)
    new_w = math.ceil(h * abs(affine[0, 1]) + w * abs(affine[0, 0]))
    new_h = math.ceil(h * abs(affine[0, 0]) + w * abs(affine[0, 1]))
    affine[:, 2] += [(new_w - w) / 2, (new_h - h) / 2]
    truth = np.vstack([affine, [0, 0, 1]]).astype(np.float64)
    rotated = cv2.warpAffine(image, affine, (new_w, new_h))
    valid = cv2.warpAffine(np.full((h, w), 255, np.uint8), affine, (new_w, new_h),
                           flags=cv2.INTER_NEAREST)
    # Keep synthetic canvas boundaries out of the feature detector.
    mask = cv2.erode(valid, np.ones((31, 31), np.uint8))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create(nfeatures=1000)
    kp1, des1 = orb.detectAndCompute(gray, None)
    standard_noise = np.random.default_rng(SEED + index).standard_normal(valid.shape)
    cases = []
    write_image(OUT / 'inputs' / f"{record['book']}_resized.png", image)
    for sigma in SIGMAS:
        noisy = np.clip(rotated.astype(np.float32) + sigma * standard_noise[:, :, None],
                        0, 255).astype(np.uint8)
        noisy[valid == 0] = 0
        target = cv2.cvtColor(noisy, cv2.COLOR_BGR2GRAY)
        kp2, des2 = orb.detectAndCompute(target, mask)
        matches = []
        if des1 is not None and des2 is not None:
            matches = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(des1, des2),
                             key=lambda m: (m.distance, m.queryIdx, m.trainIdx))
        write_image(OUT / 'transforms' / f"{record['book']}_sigma{sigma}.png", noisy)
        cases.append(dict(book=record['book'], sigma=sigma, image=image, target=noisy,
                          kp1=kp1, kp2=kp2, matches=matches, truth=truth))
    return cases


def evaluate(case, k, split):
    chosen = case['matches'][:k]
    n = len(chosen)
    p = np.array([case['kp1'][m.queryIdx].pt for m in chosen], np.float32).reshape(-1, 2)
    q = np.array([case['kp2'][m.trainIdx].pt for m in chosen], np.float32).reshape(-1, 2)
    correct = np.zeros(n, dtype=bool)
    if n:
        correct = np.linalg.norm(project(p, case['truth']) - q, axis=1) <= 3.0
    matrix, inliers = None, None
    if n >= 4:
        cv2.setRNGSeed(SEED)
        matrix, inliers = cv2.findHomography(p, q, cv2.RANSAC, 3.0,
                                            maxIters=2000, confidence=0.995)
    error = None
    if matrix is not None and np.isfinite(matrix).all():
        h, w = case['image'].shape[:2]
        corners = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])
        predicted = project(corners, matrix)
        if np.isfinite(predicted).all():
            error = float(np.linalg.norm(predicted - project(corners, case['truth']), axis=1).mean())
    diagonal = float(np.hypot(*case['target'].shape[:2]))
    return dict(split=split, book=case['book'], sigma=case['sigma'], requested_k=k,
                available=len(case['matches']), actual_k=n,
                keypoints_original=len(case['kp1']), keypoints_target=len(case['kp2']),
                correct_matches=int(correct.sum()),
                precision=float(correct.mean()) if n else 0.0,
                ransac_inliers=int(inliers.sum()) if inliers is not None else 0,
                corner_error_px=error, success=error is not None and error <= 10.0,
                selection_error_px=min(error, 2 * diagonal) if error is not None else 2 * diagonal,
                status='no_descriptors' if not case['kp1'] or not case['kp2'] else
                       'insufficient_matches' if n < 4 else
                       'homography_failed' if error is None else
                       'ok' if error <= 10 else 'localization_error')


def summarize(rows):
    result = []
    for split in ('tune', 'test'):
        for k in KS:
            group = [r for r in rows if r['split'] == split and r['requested_k'] == k]
            if not group:
                continue
            errors = [r['corner_error_px'] for r in group if r['corner_error_px'] is not None]
            result.append(dict(split=split, k=k, cases=len(group),
                               successes=sum(r['success'] for r in group),
                               success_rate=float(np.mean([r['success'] for r in group])),
                               mean_precision=float(np.mean([r['precision'] for r in group])),
                               mean_corner_error_px=float(np.mean(errors)) if errors else None,
                               estimated_homographies=len(errors),
                               selection_error_px=float(np.mean([r['selection_error_px'] for r in group]))))
    return result


def draw_case(case, k, path):
    selected = case['matches'][:k]
    # Colour correctness against known transform, not RANSAC's own labels.
    n = len(selected)
    correct = np.zeros(n, dtype=bool)
    if n:
        p = [case['kp1'][m.queryIdx].pt for m in selected]
        q = np.array([case['kp2'][m.trainIdx].pt for m in selected])
        correct = np.linalg.norm(project(p, case['truth']) - q, axis=1) <= 3
    canvas = cv2.drawMatches(case['image'], case['kp1'], case['target'], case['kp2'],
                             selected, None, matchColor=(30, 40, 230),
                             matchesMask=[int(not c) for c in correct], flags=2)
    canvas = cv2.drawMatches(case['image'], case['kp1'], case['target'], case['kp2'],
                             selected, canvas, matchColor=(40, 210, 40),
                             matchesMask=[int(c) for c in correct],
                             flags=cv2.DrawMatchesFlags_DRAW_OVER_OUTIMG |
                                   cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    banner = np.full((60, canvas.shape[1], 3), 245, np.uint8)
    label = f"{case['book']} | sigma={case['sigma']} | K={k}, actual={n} | correct={int(correct.sum())}/{n}"
    cv2.putText(banner, label, (12, 36), cv2.FONT_HERSHEY_SIMPLEX, .65, (30, 30, 30), 1)
    canvas = np.vstack([banner, canvas])
    write_image(path, canvas)


def main():
    start = perf_counter()
    cv2.setNumThreads(1)
    cv2.ocl.setUseOpenCL(False)
    OUT.mkdir(parents=True, exist_ok=True)
    records = json.loads((ROOT / 'book_sources.json').read_text(encoding='utf-8'))
    if len(records) != 6 or len({r['sha256'] for r in records}) != 6:
        raise ValueError('Need six distinct originals')
    names = sorted(r['book'] for r in records)
    random.Random(SEED).shuffle(names)
    tune, test = names[:3], names[3:]
    assert not set(tune) & set(test)
    config = dict(seed=SEED, tune=tune, test=test, ks=KS, noise_sigmas=SIGMAS,
                  rotation_degrees=30, max_original_side=900, nfeatures=1000,
                  cross_check=True, correctness_threshold_px=3,
                  success_corner_error_px=10, ransac_threshold_px=3,
                  noise_repeats=1,
                  selection_rule='highest tune success rate; then lowest mean corner error '
                                 '(missing/capped errors penalized at twice target diagonal); then smallest K')
    # Pre-register split, conditions, and selection rule before any evaluation.
    save_json(OUT / 'config.json', config)
    rows, cases = [], []
    for split, books in [('tune', tune), ('test', test)]:
        if split == 'test':
            ranking = sorted(summarize(rows), key=lambda s:
                             (-s['success_rate'], s['selection_error_px'], s['k']))
            selection = dict(k=ranking[0]['k'], tune_ranking=ranking,
                             rule=config['selection_rule'])
            save_json(OUT / 'selection.json', selection)
            print('Locked K before test:', selection['k'], flush=True)
        for book in books:
            record = next(r for r in records if r['book'] == book)
            group = prepare(record, sorted(r['book'] for r in records).index(book))
            cases.extend(group)
            for case in group:
                for k in KS:
                    row = evaluate(case, k, split)
                    rows.append(row)
                    draw_case(case, k, OUT / 'matches' / f'{book}_sigma{case["sigma"]}_k{k}.jpg')
            print(split, book, 'complete', flush=True)
    with (OUT / 'metrics.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = summarize(rows)
    save_json(OUT / 'metrics.json', rows)
    save_json(OUT / 'summary.json', summary)
    noise_summary = []
    for split in ('tune', 'test'):
        for k in KS:
            for sigma in SIGMAS:
                group = [r for r in rows if r['split'] == split and
                         r['requested_k'] == k and r['sigma'] == sigma]
                noise_summary.append(dict(split=split, k=k, sigma=sigma,
                    cases=len(group), successes=sum(r['success'] for r in group),
                    mean_precision=float(np.mean([r['precision'] for r in group]))))
    save_json(OUT / 'noise_summary.json', noise_summary)
    transforms = {c['book']: c['truth'].tolist() for c in cases}
    save_json(OUT / 'transforms.json', transforms)
    # Representative worst test condition; descriptive selection only, no retuning.
    test_rows = [r for r in rows if r['split'] == 'test']
    worst = max(test_rows, key=lambda r: (not r['success'], r['selection_error_px']))
    save_json(OUT / 'failure_case.json', worst)
    case = next(c for c in cases if c['book'] == worst['book'] and c['sigma'] == worst['sigma'])
    for k in (10, 100):
        draw_case(case, k, OUT / f'comparison_k{k}.jpg')
    originals = []
    for record in records:
        im = cv2.imread(str(ROOT / record['file']))
        ratio = min(155 / im.shape[1], 215 / im.shape[0])
        im = cv2.resize(im, None, fx=ratio, fy=ratio)
        tile = np.full((250, 170, 3), 250, np.uint8)
        tile[:im.shape[0], :im.shape[1]] = im
        label = record['book'] + (' / tune' if record['book'] in tune else ' / test')
        cv2.putText(tile, label, (4, 238), cv2.FONT_HERSHEY_SIMPLEX, .4, (30, 30, 30), 1)
        originals.append(tile)
    write_image(OUT / 'book_contact_sheet.jpg', np.hstack(originals))
    elapsed = perf_counter() - start
    save_json(OUT / 'run_info.json', dict(python=__import__('sys').version,
              opencv=cv2.__version__, numpy=np.__version__, device='CPU',
              elapsed_seconds=elapsed, rows=len(rows)))
    print(json.dumps(dict(summary=summary, worst=worst, elapsed_seconds=elapsed), indent=2))


if __name__ == '__main__':
    main()
