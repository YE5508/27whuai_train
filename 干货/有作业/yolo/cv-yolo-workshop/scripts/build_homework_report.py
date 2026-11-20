"""Build a one-page Chinese PDF from the actual ORB experiment results."""
import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/homework_b'


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def main():
    config, selection = read('config.json'), read('selection.json')
    summary, rows = read('summary.json'), read('metrics.json')
    failure = read('failure_case.json')
    sources = json.loads((ROOT / 'book_sources.json').read_text(encoding='utf-8'))
    font = Path('/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf')
    if not font.exists():
        raise FileNotFoundError('Install a Chinese TTF font, then update font path in this script')
    pdfmetrics.registerFont(TTFont('Chinese', str(font)))
    pdfmetrics.registerFontFamily('Chinese', normal='Chinese', bold='Chinese', italic='Chinese')
    latin_font = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    pdfmetrics.registerFont(TTFont('Latin', str(latin_font)))
    pdfmetrics.registerFontFamily('Latin', normal='Latin', bold='Latin', italic='Latin')

    def mixed(text):
        # DroidSansFallback intentionally lacks Latin/digits: combine two embedded fonts.
        pieces = re.split(r'(<[^>]*>)', text)
        result = []
        for piece in pieces:
            if piece.startswith('<'):
                result.append(piece)
                continue
            for run in re.findall(r'[\u2e80-\u9fff\uf900-\ufaff\uff00-\uffef]+|[^\u2e80-\u9fff\uf900-\ufaff\uff00-\uffef]+', piece):
                family = 'Chinese' if ord(run[0]) >= 0x2e80 else 'Latin'
                result.append(f'<font name="{family}">{run}</font>')
        return ''.join(result)

    styles = {
        'title': ParagraphStyle('title', fontName='Chinese', fontSize=19, leading=26,
                                textColor=colors.HexColor('#16324d')),
        'sub': ParagraphStyle('sub', fontName='Chinese', fontSize=8, leading=12,
                              textColor=colors.HexColor('#526779')),
        'head': ParagraphStyle('head', fontName='Chinese', fontSize=10, leading=15,
                               spaceBefore=7, spaceAfter=3,
                               textColor=colors.HexColor('#16324d')),
        'body': ParagraphStyle('body', fontName='Chinese', fontSize=9, leading=13,
                               wordWrap='CJK', spaceAfter=3),
        'small': ParagraphStyle('small', fontName='Chinese', fontSize=7.2, leading=10,
                                wordWrap='CJK', textColor=colors.HexColor('#4b5563')),
        'cell': ParagraphStyle('cell', fontName='Chinese', fontSize=8, leading=12,
                               alignment=TA_CENTER),
    }
    story = []
    def p(text, style='body'):
        story.append(Paragraph(mixed(text), styles[style]))

    def head(text):
        p(text, 'head')

    p('ORB 特征匹配：匹配线存在适当范围吗？', 'title')
    p('课后作业 B · CPU 对照实验 · 2026-11-20 · 原图、代码与完整数据另附', 'sub')
    head('1  猜想与实验设计')
    p('我的猜想是：匹配数量过少时定位不稳定；过多时可能引入低质量匹配，对噪声更敏感。'
      '本实验检验这一趋势，不预设最佳范围，也不把匹配增多直接称为“过拟合”。')
    p(f'下载 6 本不同书的封面，按书本分组（随机种子 42）：调参集为 '
      f'{", ".join(config["tune"])}；测试集为 {", ".join(config["test"])}。'
      '原图最长边缩至不超过 900 像素，再旋转 30°并扩展画布；'
      '添加高斯噪声，标准差为 0、15、45（像素范围 0–255）。同组不同 K 使用完全相同的输入。')
    p('固定 ORB 最多 1000 个特征，采用 Hamming 距离与双向一致匹配，按距离从小到大保留 '
      'K=10、30、100 个匹配，实际不足则全部保留。每组 3 本×3 噪声×3 个 K，两组共 54 项实验。'
      '仅在调参集按定位成功率最高、再按惩罚后平均误差最低选择 K，测试前锁定。')
    head('2  评价与实测结果')
    p('将原图匹配点按真实变换投影，距离目标匹配点≤3 像素记为正确；正确率按每项实验分别计算后平均。'
      '另用 RANSAC 估计单应矩阵（阈值 3 像素）；四角平均误差≤10 像素记为定位成功。'
      '真实变换用于评价，不将 RANSAC 自判内点当作真值。')
    data = [['保留数量 K', '调参成功', '测试成功', '噪声0/15/45<br/>测试成功数', '测试匹配<br/>正确率', '测试平均<br/>角点误差']]
    for k in config['ks']:
        tune = next(s for s in summary if s['split'] == 'tune' and s['k'] == k)
        test = next(s for s in summary if s['split'] == 'test' and s['k'] == k)
        err = test['mean_corner_error_px']
        noise_counts = [sum(r['success'] for r in rows if r['split'] == 'test' and
                            r['requested_k'] == k and r['sigma'] == sigma)
                        for sigma in config['noise_sigmas']]
        data.append([str(k) + ('（选定）' if k == selection['k'] else ''),
                     f'{tune["successes"]}/{tune["cases"]}',
                     f'{test["successes"]}/{test["cases"]}',
                     ' / '.join(str(n) for n in noise_counts),
                     f'{test["mean_precision"]:.1%}',
                     f'{err:.2f} px' if err is not None else '无法估计'])
    table = Table([[Paragraph(mixed(str(v)), styles['cell']) for v in row] for row in data],
                  colWidths=[85, 65, 65, 108, 95, 105], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5eef6')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f4f7fa')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, 0), .5, colors.HexColor('#afc0cf')),
    ]))
    story.append(table)
    p('注：每个 K 共 9 项测试，每个噪声等级 3 项。角点误差均值包含定位错误的大误差；无法估计项不纳入该均值，'
      '其失败仍计入成功率。调参时无法估计项以目标图对角线的 2 倍惩罚，大于此值的误差按此值截断。', 'small')
    selected = next(s for s in summary if s['split'] == 'test' and s['k'] == selection['k'])
    p(f'调参集选定 K={selection["k"]}，锁定后测试定位成功 {selected["successes"]}/9；'
      '测试集另外两个 K 仅作预先约定的对照，不用于重新选参。')
    head('3  对照图与失败分析')
    images = []
    for k in (10, 100):
        im = Image(str(OUT / f'comparison_k{k}.jpg'))
        ratio = min(255 / im.imageWidth, 139 / im.imageHeight)
        im.drawWidth, im.drawHeight = im.imageWidth * ratio, im.imageHeight * ratio
        images.append(im)
    figure = Table([images], colWidths=[261.5, 261.5])
    figure.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 0)]))
    story.append(figure)
    p(f'图：测试中定位最差的条件 {failure["book"]}、噪声 {failure["sigma"]}；'
      '左 K=10，右 K=100。绿色为真实变换验证的正确匹配，红色为错误匹配。', 'small')
    failure_error = failure['corner_error_px']
    error_text = f'{failure_error:.2f} 像素' if failure_error is not None else '无法估计'
    p(f'该条件在 K={failure["requested_k"]} 时保留 {failure["actual_k"]} 条线，'
      f'正确 {failure["correct_matches"]} 条，角点误差为 {error_text}。'
      '少量匹配即使多数正确，也可能集中在局部，无法稳定约束整张封面的四角；'
      '增大 K 会同时改变匹配质量和空间覆盖，因此不能仅凭线数解释全部变化。')
    head('4  结论与边界')
    low = next(s for s in summary if s['split'] == 'test' and s['k'] == 10)
    high = next(s for s in summary if s['split'] == 'test' and s['k'] == 100)
    if high['success_rate'] >= low['success_rate']:
        conclusion = ('本次从 10 增至 100 条匹配后，整体定位成功率没有下降；'
                      '因此数据不足以支持“超过某个数量必然变差”的说法。')
    else:
        conclusion = ('本次 100 条匹配的定位成功率低于 10 条，支持数量增大可能降低定位稳定性，'
                      '但不足以证明存在通用上限。')
    p(conclusion + '较可靠的判断应结合正确率、空间覆盖和定位误差。'
      '本次仅 6 本书，每本每个噪声等级仅 1 次采样，且只有合成旋转；'
      '不能据此给出通用阈值、证明过拟合，或推广到真实拍摄与透视变化。')
    p('复现：.venv/bin/python examples/05_orb_homework.py；随后运行 '
      '.venv/bin/python scripts/build_homework_report.py。原始指标见 outputs/homework_b/metrics.csv。', 'small')
    p('来源：6 张封面来自 Open Library，各图来源、下载链接及授权说明见根目录 book_sources.json；'
      '<link href="https://docs.opencv.org/4.x/dc/dc3/tutorial_py_matcher.html" color="#305f8c">'
      'OpenCV Feature Matching 官方文档</link>。', 'small')

    def footer(canvas, doc):
        canvas.setTitle('ORB 特征匹配课后作业报告')
        canvas.setAuthor('CV Workshop')
        canvas.setFont('Latin', 7)
        canvas.setFillColor(colors.HexColor('#6b7280'))
        canvas.drawRightString(A4[0] - 36, 21, f'{doc.page} / 1')

    target = OUT / 'ORB课后作业报告.pdf'
    doc = SimpleDocTemplate(str(target), pagesize=A4, leftMargin=36, rightMargin=36,
                            topMargin=27, bottomMargin=33)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(target)


if __name__ == '__main__':
    main()
