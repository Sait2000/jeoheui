# coding: utf-8

import io
import re
import sys

import template


# noinspection PyShadowingBuiltins
def compile(source, out_file, newline_in=(u'\r\n', u'\n', u'\r'),
            naive_border=False, nop_character=u'ㅇ',
            newline_out=u'\n', nop_pattern=(
                ('nop_ignored', 'nop_ignored_v', 'nop_ignored'),
                ('nop_ignored_h', 'nop', 'nop_ignored_h'),
                ('nop_ignored', 'nop_ignored_v', 'nop_ignored'),
            ), remove_trailing_newline=True,
            remove_leading_newline=False):
    re_splitlines = re.compile(u'|'.join(
        re.escape(s)
        for s in reversed(sorted(newline_in, key=len))
    ))
    lines = re_splitlines.split(source)

    if remove_trailing_newline == -1:
        remove_trailing_newline = len(lines)
    for __ in range(remove_trailing_newline):
        if not lines or lines[-1]:
            break
        lines.pop()

    if remove_leading_newline == -1:
        remove_leading_newline = len(lines)
    offset = 0
    for __ in range(remove_leading_newline):
        if len(lines) <= offset or lines[offset]:
            break
        offset += 1
    if offset:
        lines = lines[offset:]

    height = len(lines)
    width = max(len(line) for line in lines) if lines else 0

    left_end = [0] * height
    right_end = [len(line) for line in lines]
    top_end = [height] * width
    bottom_end = [0] * width

    for r in range(height):
        for c in range(len(lines[r])):
            top_end[c] = min(top_end[c], r)
            bottom_end[c] = r

    for c in range(width):
        if top_end[c] > bottom_end[c]:
            bottom_end[c] = top_end[c]

    # templates
    border_intersection = template.template_border_intersection
    if naive_border:
        border_top = template.template_border_top_naive
        border_left = template.template_border_left_naive
    else:
        border_top = template.template_border_top
        border_left = template.template_border_left

    # TODO: XXX
    nop = [
        [getattr(template, 'template_' + s) for s in r]
        for r in nop_pattern
    ]

    hangul_templates = template.hangul_templates

    # top border
    for r_t in range(len(border_intersection)):
        translate_table = {
            0x3147: ord(nop_character),  # ord(u'ㅇ') == 0x3147
        }
        out_file.write(border_intersection[r_t].translate(translate_table))
        for c in range(width):
            out_file.write(border_top[r_t].translate(translate_table))
        out_file.write(newline_out)

    for r, line in enumerate(lines):
        for r_t in range(len(border_left)):
            translate_table = {
                0x3147: ord(nop_character),  # ord(u'ㅇ') == 0x3147
            }
            out_file.write(border_left[r_t].translate(translate_table))
            for c in range(width):
                translate_table = {
                    0x3147: ord(nop_character),  # ord(u'ㅇ') == 0x3147
                }
                if c >= len(line) or not (u'\uAC00' <= line[c] <= u'\uD7A3'):
                    cell_char = None

                    left_over = c < left_end[r]
                    right_over = c >= right_end[r]
                    top_over = r < top_end[c]
                    bottom_over = r >= bottom_end[c]

                    # XXX
                    cell_template = nop[1 - top_over + bottom_over][1 - left_over + right_over]
                else:
                    cell_char = line[c]
                    code_point = ord(cell_char)
                    vowel = (code_point - 0xAC00) // 28 % 21
                    consonants = code_point - vowel * 28

                    translate_table.update({
                        0xCC28: consonants,        # ord(u'차') == 0xCC28
                        0xCC98: consonants + 112,  # ord(u'처') == 0xCC98
                        0xCD08: consonants + 224,  # ord(u'초') == 0xCD08
                        0xCD94: consonants + 364,  # ord(u'추') == 0xCD94
                    })

                    cell_template = hangul_templates[vowel]

                out_file.write(cell_template[r_t].translate(translate_table))
            out_file.write(newline_out)


def main(filename_in, filename_out):
    with io.open(filename_in, 'r', encoding='utf-8', newline=u'') as file_in:
        source = file_in.read()

    with io.open(filename_out, 'w', encoding='utf-8', newline=u'') as file_out:
        compile(source, file_out)


if __name__ == '__main__':
    main(*sys.argv[1:])
