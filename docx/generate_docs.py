#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Book Match documentation with full Vietnamese diacritics."""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import os

doc = Document()

# -- Global style defaults --
style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(13)
style.paragraph_format.line_spacing = 1.5
style.paragraph_format.space_after = Pt(6)
style.element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')

for level in range(1, 4):
    hs = doc.styles[f'Heading {level}']
    hs.font.name = 'Times New Roman'
    hs.font.color.rgb = RGBColor(0x1A, 0x3C, 0x6E)
    hs.element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    if level == 1:
        hs.font.size = Pt(18)
        hs.paragraph_format.space_before = Pt(24)
    elif level == 2:
        hs.font.size = Pt(15)
        hs.paragraph_format.space_before = Pt(18)
    else:
        hs.font.size = Pt(13)
        hs.paragraph_format.space_before = Pt(12)

# -- Helper functions --

def add_hr(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    pPr = p._p.get_or_add_pPr()
    pBdr = parse_xml(
        '<w:pBdr %s>'
        '  <w:bottom w:val="single" w:sz="6" w:space="1" w:color="1A3C6E"/>'
        '</w:pBdr>' % nsdecls('w')
    )
    pPr.append(pBdr)

def add_para(doc, text, bold=False, italic=False, align=None, size=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    if bold:
        run.bold = True
    if italic:
        run.italic = True
    if size:
        run.font.size = Pt(size)
    if align:
        p.alignment = align
    return p

def add_heading2(doc, title):
    return doc.add_heading(title, level=2)

def add_bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    if bold_prefix:
        run = p.add_run(bold_prefix)
        run.bold = True
        p.add_run(text)
    else:
        p.add_run(text)
    return p

def add_body(doc, text, bold=False, italic=False, align=None, size=None):
    return add_para(doc, text, bold=bold, italic=italic, align=align, size=size)

# =====================================================================
#  TRANG BÌA
# =====================================================================

for _ in range(4):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('ĐẠI HỌC THỦ DẦU MỘT')
run.bold = True
run.font.size = Pt(16)
run.font.color.rgb = RGBColor(0x1A, 0x3C, 0x6E)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('\u2014' * 30)
run.font.color.rgb = RGBColor(0x1A, 0x3C, 0x6E)

doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('BOOK MATCH')
run.bold = True
run.font.size = Pt(28)
run.font.color.rgb = RGBColor(0x1A, 0x3C, 0x6E)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('AI ĐỒNG HÀNH CÙNG VĂN HÓA ĐỌC')
run.bold = True
run.font.size = Pt(18)
run.font.color.rgb = RGBColor(0x2D, 0x5F, 0x8A)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Sáng kiến phần mềm hỗ trợ đọc sách\nvới sự trợ giúp của Trí tuệ Nhân tạo (AI)')
run.font.size = Pt(14)
run.italic = True

doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Tài liệu dự thi — Đại sứ Văn hóa Đọc')
run.font.size = Pt(14)
run.bold = True

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Năm 2026')
run.font.size = Pt(14)

doc.add_page_break()

# =====================================================================
#  MỤC LỤC
# =====================================================================

doc.add_heading('MỤC LỤC', level=1)

toc_items = [
    'LỜI NÓI ĐẦU',
    'Chương 1: GIỚI THIỆU VỀ DỰ ÁN BOOK MATCH',
    '  1.1. Bối cảnh ra đời',
    '  1.2. Mục tiêu và sứ mệnh',
    '  1.3. Đối tượng hướng đến',
    'Chương 2: VAI TRÒ CỦA TRÍ TUỆ NHÂN TẠO TRONG VĂN HÓA ĐỌC',
    '  2.1. Thách thức của văn hóa đọc trong thời đại số',
    '  2.2. AI — Người bạn đồng hành đọc sách',
    '  2.3. Cơ chế gợi ý sách thông minh',
    'Chương 3: CÁC TÍNH NĂNG HỖ TRỢ ĐỌC SÁCH',
    '  3.1. Khảo sát sở thích và gợi ý sách cá nhân hóa',
    '  3.2. Hệ thống thử thách và mục tiêu đọc',
    '  3.3. Đồng hồ Pomodoro — Tập trung đọc sách',
    '  3.4. Chuỗi ngày đọc và bảng xếp hạng',
    '  3.5. Thư viện sách trực tuyến',
    'Chương 4: LỘ TRÌNH NGƯỜI DÙNG',
    '  4.1. Hành trình khám phá sách',
    '  4.2. Vòng lặp thói quen: Đọc — Ghi nhận — Tiến bộ',
    'Chương 5: KẾT LUẬN VÀ ĐỊNH HƯỚNG PHÁT TRIỂN',
    '  5.1. Ý nghĩa và giá trị của dự án',
    '  5.2. Tầm nhìn tương lai',
]

for item in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    is_chapter = item.startswith('Chương')
    is_sub = item.startswith('  ')
    run = p.add_run(item.strip())
    if is_chapter or (not is_sub and item != 'LỜI NÓI ĐẦU' and not item.startswith('  ')):
        run.bold = True
        run.font.size = Pt(13)
    elif is_sub:
        run.font.size = Pt(12)

doc.add_page_break()

# =====================================================================
#  LỜI NÓI ĐẦU
# =====================================================================

doc.add_heading('LỜI NÓI ĐẦU', level=1)

add_body(doc, (
    'Văn hóa đọc là nền tảng quan trọng cho sự phát triển tri thức của mỗi cá nhân '
    'và toàn xã hội. Trong bối cảnh công nghệ số bùng nổ, việc duy trì thói quen đọc '
    'sách đang đối mặt với nhiều thách thức: sự cạnh tranh từ mạng xã hội, video ngắn '
    'và các hình thức giải trí nhanh. Đặc biệt, giới trẻ ngày nay dễ dàng bị cuốn vào '
    'dòng chảy thông tin hỗn tạp, thiếu định hướng trong việc lựa chọn sách phù hợp.'
))

add_body(doc, (
    'Xuất phát từ thực tế đó, Book Match ra đời như một giải pháp công nghệ nhân văn, '
    'nơi Trí tuệ Nhân tạo (AI) đóng vai trò người bạn đồng hành, giúp người đọc khám phá '
    'những cuốn sách phù hợp với sở thích, tâm trạng và độ tuổi của mình. Không chỉ dừng '
    'lại ở việc gợi ý sách, Book Match còn xây dựng một hệ sinh thái khuyến đọc toàn diện: '
    'từ thiết lập mục tiêu, theo dõi tiến độ, đến tạo động lực qua các thử thách và '
    'bảng xếp hạng.'
))

add_body(doc, (
    'Tài liệu này được viết nhằm giới thiệu về dự án Book Match — sáng kiến phần mềm '
    'phục vụ cuộc thi Đại sứ Văn hóa Đọc. Chúng tôi tin rằng, với sự hỗ trợ của AI, '
    'việc đọc sách sẽ trở nên thú vị, dễ dàng và hiệu quả hơn bao giờ hết, góp phần '
    'xây dựng một thế hệ trẻ yêu sách, ham học hỏi và giàu tri thức.'
))

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
run = p.add_run('Trân trọng,\nNhóm phát triển Book Match')
run.italic = True
run.font.size = Pt(12)

doc.add_page_break()

# =====================================================================
#  CHƯƠNG 1
# =====================================================================

doc.add_heading('Chương 1: GIỚI THIỆU VỀ DỰ ÁN BOOK MATCH', level=1)

add_heading2(doc, '1.1. Bối cảnh ra đời')
add_body(doc, (
    'Cuộc thi Đại sứ Văn hóa Đọc là một hoạt động ý nghĩa nhằm khơi dậy niềm đam mê '
    'đọc sách trong cộng đồng, đặc biệt là thế hệ trẻ. Tại Trường Đại học Thủ Dầu Một, '
    'phong trào đọc sách luôn được nhà trường quan tâm và đẩy mạnh. Tuy nhiên, thực tế '
    'cho thấy sinh viên gặp nhiều rào cản trong việc duy trì thói quen đọc:'
))

add_bullet(doc, ' Không biết nên đọc sách gì giữa hàng ngàn đầu sách khác nhau')
add_bullet(doc, ' Thiếu động lực và kỷ luật để duy trì đọc sách hàng ngày')
add_bullet(doc, ' Không có công cụ để theo dõi tiến độ và thành quả đọc sách')
add_bullet(doc, ' Khó tìm được cộng đồng cùng chung sở thích đọc sách')

add_body(doc, (
    'Book Match được phát triển để giải quyết những rào cản trên. Dự án kết hợp giữa '
    'công nghệ AI hiện đại và các nguyên lý gamification (trò chơi hóa) để tạo ra một '
    'nền tảng đọc sách toàn diện, giúp người dùng không chỉ tìm được sách hay mà còn '
    'có động lực để đọc mỗi ngày.'
))

add_heading2(doc, '1.2. Mục tiêu và sứ mệnh')

add_body(doc, 'Book Match hướng đến ba mục tiêu chiến lược:', bold=True)

p = doc.add_paragraph()
run = p.add_run('a) Cá nhân hóa trải nghiệm đọc: ')
run.bold = True
p.add_run(
    'Sử dụng AI để thấu hiểu sở thích, tâm trạng và nhu cầu của từng người đọc, '
    'từ đó đưa ra những gợi ý sách phù hợp nhất, giúp việc chọn sách trở nên dễ dàng và chính xác.'
)

p = doc.add_paragraph()
run = p.add_run('b) Xây dựng thói quen đọc bền vững: ')
run.bold = True
p.add_run(
    'Thông qua hệ thống mục tiêu, thử thách và theo dõi chuỗi ngày đọc, '
    'Book Match giúp người dùng hình thành thói quen đọc sách đều đặn, '
    'biến việc đọc thành một phần không thể thiếu trong cuộc sống hàng ngày.'
)

p = doc.add_paragraph()
run = p.add_run('c) Tạo dựng cộng đồng đọc sách: ')
run.bold = True
p.add_run(
    'Bảng xếp hạng, thử thách nhóm và các danh hiệu (badge) tạo nên một sân chơi '
    'lành mạnh, nơi người đọc có thể giao lưu, học hỏi và cùng nhau tiến bộ.'
)

add_heading2(doc, '1.3. Đối tượng hướng đến')
add_body(doc, (
    'Book Match được thiết kế dành cho sinh viên và giảng viên Trường Đại học Thủ Dầu Một '
    'nói riêng, và đông đảo bạn đọc trẻ tuổi nói chung. Dự án đặc biệt phù hợp với những '
    'người muốn xây dựng thói quen đọc sách nhưng chưa biết bắt đầu từ đâu, '
    'cũng như những bạn đọc có kinh nghiệm muốn khám phá thêm nhiều đầu sách mới và '
    'kết nối với cộng đồng yêu sách.'
))

doc.add_page_break()

# =====================================================================
#  CHƯƠNG 2
# =====================================================================

doc.add_heading('Chương 2: VAI TRÒ CỦA TRÍ TUỆ NHÂN TẠO TRONG VĂN HÓA ĐỌC', level=1)

add_heading2(doc, '2.1. Thách thức của văn hóa đọc trong thời đại số')
add_body(doc, (
    'Thời đại công nghệ số mang đến cho con người vô vàn tiện ích, nhưng cũng đặt ra '
    'không ít thách thức cho văn hóa đọc. Sự bùng nổ của mạng xã hội, nền tảng video ngắn '
    'và các ứng dụng giải trí đã làm giảm đáng kể thời gian dành cho việc đọc sách của '
    'giới trẻ. Theo nhiều khảo sát, sinh viên ngày nay đọc sách ít hơn các thế hệ trước, '
    'và khi đọc, họ thường gặp khó khăn trong việc tập trung và duy trì.'
))

add_body(doc, (
    'Bên cạnh đó, \u201cnghịch lý lựa chọn\u201d cũng là một rào cản lớn. Khi có quá nhiều đầu '
    'sách, người đọc dễ bị choáng ngợp và không biết nên chọn cuốn nào. Việc thiếu '
    'một người hướng dẫn, một người bạn đồng hành để giới thiệu sách phù hợp khiến '
    'nhiều bạn trẻ từ bỏ ý định đọc sách ngay từ khi chưa bắt đầu.'
))

add_heading2(doc, '2.2. AI — Người bạn đồng hành đọc sách')
add_body(doc, (
    'Book Match ứng dụng Trí tuệ Nhân tạo (AI) để giải quyết những thách thức trên. '
    'AI trong Book Match hoạt động như một người bạn đồng hành thông minh, có khả năng:'
))

add_bullet(doc, ' Thấu hiểu người đọc: Qua bài khảo sát ban đầu về độ tuổi, sở thích và tâm trạng, AI xây dựng một \u201cchân dung đọc\u201d (reading profile) cho mỗi người dùng.')
add_bullet(doc, ' Gợi ý sách thông minh: Dựa trên chân dung đọc, AI đề xuất những cuốn sách phù hợp nhất, kèm theo tỷ lệ phù hợp (match rate), lý giải tại sao cuốn sách này phù hợp với người đọc.')
add_bullet(doc, ' Thích ứng theo thời gian: AI điều chỉnh gợi ý dựa trên mùa trong năm, các sự kiện văn hóa (ví dụ: gợi ý sách lịch sử vào dịp 30/4, sách Tết vào dịp đầu năm mới).')
add_bullet(doc, ' Cải thiện liên tục: Khi người dùng đọc nhiều hơn, AI hiểu rõ hơn về gu đọc của họ và đưa ra những gợi ý ngày càng chính xác.')

add_body(doc, (
    'Điểm đặc biệt của Book Match là AI không chỉ dừng lại ở việc gợi ý sách. '
    'AI còn đưa ra những nhận xét, đánh giá bằng tiếng Việt tự nhiên, thân thiện, '
    'giúp người đọc có cái nhìn tổng quan về cuốn sách trước khi quyết định đọc.'
))

add_heading2(doc, '2.3. Cơ chế gợi ý sách thông minh')
add_body(doc, (
    'Cơ chế gợi ý sách của Book Match được thiết kế theo quy trình ba bước:'
))

p = doc.add_paragraph()
run = p.add_run('Bước 1 — Khảo sát: ')
run.bold = True
p.add_run(
    'Người dùng điền vào bảng khảo sát với ba thông tin cơ bản: độ tuổi, '
    'sở thích đọc sách và tâm trạng hiện tại. Đây là những dữ liệu đầu vào '
    'quan trọng giúp AI hiểu được nhu cầu của người đọc.'
)

p = doc.add_paragraph()
run = p.add_run('Bước 2 — Phân tích: ')
run.bold = True
p.add_run(
    'Dựa trên thông tin từ bước 1, cùng với dữ liệu về lịch sử đọc (số ngày đọc liên tiếp, '
    'tổng thời gian đọc, số sách đã hoàn thành), AI phân tích và xây dựng một bộ lọc '
    'thông minh để chọn ra những cuốn sách phù hợp nhất.'
)

p = doc.add_paragraph()
run = p.add_run('Bước 3 — Gợi ý: ')
run.bold = True
p.add_run(
    'AI trả về ba gợi ý sách, mỗi gợi ý bao gồm: tên sách, tác giả, mô tả ngắn, '
    'tỷ lệ phù hợp (từ 75% đến 99%), lý do cuốn sách phù hợp với người đọc, '
    'và một số từ khóa gợi ý hình ảnh cho cuốn sách.'
)

add_body(doc, (
    'Người dùng có thể yêu cầu AI gợi ý lại nếu chưa hài lòng với các đề xuất hiện tại. '
    'AI sẽ loại trừ những cuốn sách đã gợi ý trước đó để đảm bảo sự đa dạng và mới mẻ. '
    'Ngoài ra, thông tin khảo sát cũng được lưu lại để người dùng có thể chỉnh sửa '
    'khi sở thích thay đổi.'
))

add_hr(doc)

p = doc.add_paragraph()
run = p.add_run('Ví dụ gợi ý của AI: ')
run.bold = True
run.italic = True

add_body(doc, (
    '\u201cChào bạn! Dựa trên sở thích văn học và tâm trạng muốn tìm kiếm sự đồng cảm, '
    'mình nghĩ bạn sẽ rất thích cuốn \u201cTôi thấy hoa vàng trên cỏ xanh\u201d của nhà văn '
    'Nguyễn Nhật Ánh (tỷ lệ phù hợp: 92%). Tuổi thơ trong trẻo và những rung động '
    'đầu đời trong tác phẩm sẽ chạm đến trái tim bạn đấy!\u201d'
), italic=True)

doc.add_page_break()

# =====================================================================
#  CHƯƠNG 3
# =====================================================================

doc.add_heading('Chương 3: CÁC TÍNH NĂNG HỖ TRỢ ĐỌC SÁCH', level=1)

add_body(doc, (
    'Book Match được xây dựng với năm nhóm tính năng chính, tạo thành một hệ sinh thái '
    'khuyến đọc toàn diện. Mỗi tính năng đều được thiết kế với mục tiêu hỗ trợ người '
    'đọc trên từng chặng đường của hành trình văn hóa đọc.'
))

add_heading2(doc, '3.1. Khảo sát sở thích và gợi ý sách cá nhân hóa')
add_body(doc, (
    'Tính năng cốt lõi và khác biệt nhất của Book Match chính là khả năng gợi ý sách '
    'cá nhân hóa dựa trên AI. Ngay sau khi đăng ký tài khoản, người dùng sẽ được mời '
    'tham gia một bài khảo sát nhanh với ba câu hỏi:'
))

add_bullet(doc, ' Độ tuổi của bạn? (giúp AI chọn sách phù hợp với lứa tuổi)')
add_bullet(doc, ' Sở thích đọc sách của bạn? (văn học, khoa học, kinh tế, phát triển bản thân\u2026)')
add_bullet(doc, ' Tâm trạng hiện tại của bạn? (vui, buồn, muốn tìm cảm hứng, muốn thư giãn\u2026)')

add_body(doc, (
    'Dựa trên câu trả lời, Book Match sẽ hiển thị ba gợi ý sách được AI cá nhân hóa '
    'cho từng người dùng. Giao diện hiển thị trực quan, đẹp mắt với thẻ sách (book card) '
    'hiện đại, giúp người đọc dễ dàng so sánh và lựa chọn. Tính năng \u201cGợi ý lại\u201d cho '
    'phép người dùng nhận thêm các đề xuất mới mà không trùng lặp với những gợi ý trước.'
))

add_heading2(doc, '3.2. Hệ thống thử thách và mục tiêu đọc')
add_body(doc, (
    'Để giúp người dùng duy trì động lực đọc sách lâu dài, Book Match xây dựng một '
    'hệ thống nhiệm vụ và thử thách phong phú:'
))

p = doc.add_paragraph()
run = p.add_run('Nhiệm vụ hàng ngày (Daily Missions): ')
run.bold = True
p.add_run(
    'Bao gồm các mục tiêu nhỏ như \u201cĐọc 15 phút\u201d, \u201cHoàn thành 1 chương sách\u201d, '
    '\u201cĐọc buổi sáng\u201d, \u201cĐọc buổi tối\u201d, \u201cFocus 25 phút\u201d, \u201cĐọc 20 trang\u201d, '
    '\u201cChia sẻ cuốn sách\u201d, \u201cLưu 5 trích dẫn\u201d. Mỗi nhiệm vụ hoàn thành sẽ mang lại '
    'điểm kinh nghiệm (XP) cho người dùng.'
)

p = doc.add_paragraph()
run = p.add_run('Thử thách dài hạn (Challenges): ')
run.bold = True
p.add_run(
    'Gồm các thử thách như \u201cĐọc 7 ngày liên tiếp\u201d (trong tuần), '
    '\u201cHoàn thành 2 cuốn sách\u201d (trong tháng), \u201cTích lũy 10 giờ đọc\u201d (trong tháng). '
    'Đây là những mục tiêu lớn hơn, đòi hỏi sự kiên trì và nỗ lực bền bỉ.'
)

p = doc.add_paragraph()
run = p.add_run('Danh hiệu (Badges): ')
run.bold = True
p.add_run(
    'Khi đạt được những cột mốc quan trọng, người dùng sẽ được mở khóa các danh hiệu '
    'như \u201cNgười Mới\u201d (hoàn thành 1 nhiệm vụ), \u201cTốc Độ\u201d (đọc 30+ phút), '
    '\u201cKim Cương\u201d (chuỗi 30 ngày), \u201cHọc Giả\u201d (10 cuốn sách), \u201cCú Đêm\u201d (đọc đêm 5+ lần), '
    '\u201cGhi Chép\u201d (lưu 100+ trích dẫn). Mỗi danh hiệu là một minh chứng cho sự nỗ lực '
    'và thành quả đọc sách của người dùng.'
)

add_heading2(doc, '3.3. Đồng hồ Pomodoro — Tập trung đọc sách')
add_body(doc, (
    'Một trong những rào cản lớn nhất của việc đọc sách là sự xao nhãng. Book Match '
    'tích hợp đồng hồ Pomodoro trực quan (hình tròn SVG) giúp người dùng tập trung '
    'tối đa vào việc đọc trong một khoảng thời gian nhất định.'
))

add_body(doc, (
    'Quy trình sử dụng đồng hồ Pomodoro rất đơn giản: Người dùng chọn một nhiệm vụ '
    'đọc sách (ví dụ: \u201cĐọc 15 phút\u201d), kích hoạt nhiệm vụ, sau đó bắt đầu hẹn giờ. '
    'Đồng hồ đếm ngược với vòng tròn tiến trình trực quan giúp người đọc dễ dàng '
    'theo dõi thời gian còn lại. Khi hoàn thành, người dùng được khuyến khích viết '
    'một vài dòng nhật ký về những gì vừa đọc — một cách để ghi nhớ và suy ngẫm '
    'về nội dung đã tiếp thu.'
))

add_body(doc, (
    'Điểm đặc biệt: Người dùng bắt buộc phải kích hoạt nhiệm vụ trước khi sử dụng '
    'đồng hồ Pomodoro, đảm bảo mỗi phiên đọc đều có mục tiêu rõ ràng. Sau khi hoàn '
    'thành, hệ thống tự động ghi nhận thời gian đọc, cập nhật chuỗi ngày đọc và trao '
    'thưởng XP.'
))

add_heading2(doc, '3.4. Chuỗi ngày đọc và bảng xếp hạng')
add_body(doc, (
    'Book Match ghi nhận mỗi ngày người dùng đọc sách và xây dựng chuỗi ngày đọc '
    'liên tiếp (streak). Chuỗi ngày càng dài, động lực đọc càng lớn. Giao diện '
    'lịch tháng trực quan hiển thị những ngày đã đọc với biểu tượng ngọn lửa, '
    'giúp người dùng dễ dàng hình dung tiến độ của mình.'
))

add_body(doc, (
    'Bảng xếp hạng (Leaderboard) hiển thị top 50 người dùng có thành tích đọc sách '
    'tốt nhất, được sắp xếp dựa trên chuỗi ngày đọc và tổng thời gian đọc. Ba vị trí '
    'cao nhất được vinh danh với huy chương vàng, bạc, đồng. Đây là nguồn động lực '
    'mạnh mẽ, khuyến khích người dùng đọc sách chăm chỉ hơn mỗi ngày.'
))

add_heading2(doc, '3.5. Thư viện sách trực tuyến')
add_body(doc, (
    'Book Match đi kèm một thư viện sách trực tuyến với hơn 100 đầu sách thuộc 11 '
    'thể loại khác nhau: Văn học, Kinh tế, Phát triển bản thân, Khoa học, Công nghệ, '
    'Marketing, Ngôn ngữ, Nghệ thuật, Truyện tranh, Hồi ký và các thể loại khác.'
))

add_body(doc, (
    'Người dùng có thể tìm kiếm sách theo tên, lọc theo thể loại, xem chi tiết nội '
    'dung sách và tham gia thảo luận qua phần bình luận. Thư viện được cập nhật '
    'thường xuyên với các đầu sách mới, đảm bảo người dùng luôn có nội dung phong '
    'phú để khám phá.'
))

doc.add_page_break()

# =====================================================================
#  CHƯƠNG 4
# =====================================================================

doc.add_heading('Chương 4: LỘ TRÌNH NGƯỜI DÙNG', level=1)

add_heading2(doc, '4.1. Hành trình khám phá sách')
add_body(doc, (
    'Hành trình của người dùng trên Book Match được thiết kế như một vòng tròn khép kín, '
    'mỗi bước đều dẫn đến bước tiếp theo, tạo nên một thói quen đọc sách bền vững:'
))

steps = [
    ('Bước 1 — Đăng ký và Khảo sát: ',
     'Người dùng tạo tài khoản và điền bài khảo sát sở thích đọc sách. AI bắt đầu xây dựng chân dung đọc.'),
    ('Bước 2 — Nhận gợi ý sách: ',
     'Dựa trên kết quả khảo sát, AI gợi ý ba cuốn sách phù hợp. Người dùng có thể yêu cầu gợi ý lại nếu chưa hài lòng.'),
    ('Bước 3 — Chọn nhiệm vụ đọc: ',
     'Người dùng chọn một nhiệm vụ đọc sách (ví dụ: \u201cĐọc 15 phút\u201d) và kích hoạt.'),
    ('Bước 4 — Đọc sách tập trung: ',
     'Sử dụng đồng hồ Pomodoro, người dùng đọc sách trong khoảng thời gian đã định. Sau khi hoàn thành, viết nhật ký ngắn về nội dung vừa đọc.'),
    ('Bước 5 — Ghi nhận và tiến bộ: ',
     'Hệ thống tự động cập nhật thời gian đọc, chuỗi ngày đọc và điểm XP. Người dùng có thể xem tiến độ trên bảng thống kê và lịch đọc.'),
    ('Bước 6 — Quay lại Bước 2: ',
     'Với thành tích mới, AI hiểu rõ hơn về người đọc và đưa ra những gợi ý ngày càng chính xác. Vòng tròn đọc sách tiếp tục.'),
]

for prefix, content in steps:
    p = doc.add_paragraph()
    run = p.add_run(prefix)
    run.bold = True
    p.add_run(content)

add_heading2(doc, '4.2. Vòng lặp thói quen: Đọc — Ghi nhận — Tiến bộ')
add_body(doc, (
    'Book Match áp dụng nguyên lý \u201chabit loop\u201d (vòng lặp thói quen) của Charles Duhigg '
    'để thiết kế trải nghiệm người dùng. Mỗi chu kỳ đọc sách bao gồm ba yếu tố:'
))

p = doc.add_paragraph()
run = p.add_run('Tín hiệu (Cue): ')
run.bold = True
p.add_run(
    'Lời nhắc từ nhiệm vụ đọc, thông báo chuỗi ngày đọc, '
    'hoặc gợi ý sách mới từ AI.'
)

p = doc.add_paragraph()
run = p.add_run('Hành động (Routine): ')
run.bold = True
p.add_run('Việc đọc sách tập trung với đồng hồ Pomodoro.')

p = doc.add_paragraph()
run = p.add_run('Phần thưởng (Reward): ')
run.bold = True
p.add_run(
    'Điểm XP, danh hiệu, cập nhật chuỗi ngày đọc, '
    'sự hài lòng khi hoàn thành mục tiêu.'
)

add_body(doc, (
    'Sau mỗi chu kỳ, người dùng cảm thấy có thành tựu và được khuyến khích tiếp tục '
    'chu kỳ mới. Qua thời gian, việc đọc sách trở thành một thói quen tự nhiên, '
    'không cần quá nhiều nỗ lực ý chí. Đây chính là chìa khóa giúp Book Match xây dựng '
    'văn hóa đọc bền vững cho cộng đồng.'
))

doc.add_page_break()

# =====================================================================
#  CHƯƠNG 5
# =====================================================================

doc.add_heading('Chương 5: KẾT LUẬN VÀ ĐỊNH HƯỚNG PHÁT TRIỂN', level=1)

add_heading2(doc, '5.1. Ý nghĩa và giá trị của dự án')
add_body(doc, (
    'Book Match không đơn thuần là một ứng dụng công nghệ. Đây là một sáng kiến văn hóa, '
    'một giải pháp nhân văn cho bài toán phát triển văn hóa đọc trong thời đại số. '
    'Với sự trợ giúp của AI, Book Match mang đến những giá trị thiết thực:'
))

add_bullet(doc, ' Cá nhân hóa: Không còn lo lắng \u201ckhông biết đọc sách gì\u201d. AI thấu hiểu và gợi ý sách phù hợp với từng người.')
add_bullet(doc, ' Động lực bền vững: Hệ thống nhiệm vụ, thử thách, danh hiệu và bảng xếp hạng tạo nên động lực đọc sách lâu dài.')
add_bullet(doc, ' Thói quen khoa học: Đồng hồ Pomodoro và theo dõi chuỗi ngày đọc giúp hình thành thói quen đọc đều đặn, có kỷ luật.')
add_bullet(doc, ' Cộng đồng gắn kết: Bảng xếp hạng và các thử thách chung tạo nên một cộng đồng đọc sách năng động, tích cực.')
add_bullet(doc, ' Tiếp cận tri thức rộng mở: Thư viện trực tuyến với đa dạng thể loại giúp người dùng dễ dàng tiếp cận nhiều lĩnh vực tri thức khác nhau.')

add_heading2(doc, '5.2. Tầm nhìn tương lai')
add_body(doc, (
    'Book Match được xây dựng với tầm nhìn trở thành nền tảng đồng hành đọc sách '
    'hàng đầu cho sinh viên Việt Nam. Trong tương lai, nhóm phát triển dự định:'
))

add_bullet(doc, ' Mở rộng kho sách với hàng ngàn đầu sách chất lượng từ nhiều nhà xuất bản.')
add_bullet(doc, ' Phát triển tính năng gợi ý sách theo nhóm, cho phép bạn bè cùng khám phá và thảo luận về sách.')
add_bullet(doc, ' Tích hợp AI đàm thoại, cho phép người dùng trò chuyện trực tiếp với AI về nội dung sách.')
add_bullet(doc, ' Mở rộng ra các trường đại học khác trên cả nước, tạo nên một mạng lưới văn hóa đọc rộng khắp.')
add_bullet(doc, ' Phát triển ứng dụng di động để người dùng có thể đọc sách mọi lúc, mọi nơi.')

add_body(doc, '')
add_hr(doc)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run(
    '\u201cSách là ánh sáng dẫn đường cho tri thức —\n'
    'AI là người bạn đồng hành trên con đường ấy\u201d'
)
run.italic = True
run.font.size = Pt(13)
run.font.color.rgb = RGBColor(0x1A, 0x3C, 0x6E)

add_body(doc, '')
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('— Book Match —')
run.bold = True
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(0x1A, 0x3C, 0x6E)

# =====================================================================
#  SAVE
# =====================================================================

output_path = os.path.join(os.path.dirname(__file__), 'Book_Match_Tai_Lieu_Du_Thi.docx')
doc.save(output_path)
import sys
sys.stdout.reconfigure(encoding='utf-8')
print(f'Da tao tai lieu tai: {output_path}')
