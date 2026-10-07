#!/usr/bin/env python3
"""Optional PDF build; install reportlab. The audit itself has no dependencies."""
from html import escape
from pathlib import Path
import posixpath
import re
import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables/elev8-one-page-memo.pdf'
FONTS = Path(reportlab.__file__).parent / 'fonts'
pdfmetrics.registerFont(TTFont('Vera', str(FONTS / 'Vera.ttf')))
pdfmetrics.registerFont(TTFont('Vera-Bold', str(FONTS / 'VeraBd.ttf')))
pdfmetrics.registerFontFamily('Vera', normal='Vera', bold='Vera-Bold', italic='Vera', boldItalic='Vera-Bold')


def inline(text):
    text = text.replace('\u2011', '-').replace('\u2013', '-').replace('\u2014', '-')
    text = escape(text)
    def link(m):
        label, url = m.groups()
        if not url.startswith('https://'):
            url = 'https://github.com/MojoMinistry/elev8demo/blob/main/' + posixpath.normpath('deliverables/' + url)
        return f'<link href="{url}" color="#126579">{label}</link>'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return text


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#d1dce2'))
    canvas.line(38, 33, 574, 33)
    canvas.setFont('Vera', 8)
    canvas.setFillColor(colors.HexColor('#536471'))
    canvas.drawString(38, 21, 'Public evidence | 38 pages | OpenAI Codex-assisted assessment')
    canvas.drawRightString(574, 21, str(doc.page))
    canvas.restoreState()


doc = SimpleDocTemplate(str(OUT), pagesize=letter, rightMargin=38, leftMargin=38,
                        topMargin=33, bottomMargin=42, title='elev8 | Five priorities for qualified patient inquiries',
                        author='Prepared for the elev8 Product Performance Lead exercise')
body = ParagraphStyle('body', fontName='Vera', fontSize=10.2, leading=13.5,
                      textColor=colors.HexColor('#243748'), spaceAfter=8, alignment=TA_LEFT)
title = ParagraphStyle('title', parent=body, fontName='Vera-Bold', fontSize=19, leading=23, spaceAfter=8,
                       textColor=colors.HexColor('#17364a'))
meta = ParagraphStyle('meta', parent=body, fontSize=9, leading=12, spaceAfter=10)
story = []
paragraphs = (ROOT / 'deliverables/memo.md').read_text().strip().split('\n\n')
for i, p in enumerate(paragraphs):
    p = ' '.join(p.splitlines())
    if p.startswith('# '):
        story.append(Paragraph(inline(p[2:]), title))
    elif i == 1:
        story.append(Paragraph(inline(p), meta))
        story.append(HRFlowable(width='100%', color=colors.HexColor('#2b7989'), thickness=1.5))
        story.append(Spacer(1, 10))
    else:
        story.append(Paragraph(inline(p), body))
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
