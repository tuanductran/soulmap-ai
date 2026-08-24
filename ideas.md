# Hướng thiết kế cho SoulMap AI public interface

## Ba hướng cân nhắc

### Bản đồ Biên Độ

**Very Brief Intro:** Một giao diện biên tập kiểu field guide, dùng các cột mốc, rule line và khoảng trắng có chủ đích để biến nội dung phản chiếu thành một không gian định hướng rõ ràng. Nó điềm tĩnh, chính xác và giúp người đọc luôn thấy mình đang ở đâu.

**Probability:** 0.06

### Lưu trữ Thềm Đá

**Very Brief Intro:** Một hệ lưu trữ mang tinh thần brutalist nhẹ, dùng khối chữ lớn, nhãn kỹ thuật và bề mặt gần như không trang trí để nhấn mạnh tính công khai, giới hạn và khả năng kiểm chứng. Cảm xúc được giữ trong văn bản thay vì hiệu ứng thị giác.

**Probability:** 0.03

### Ghi chép Hoàng Hôn

**Very Brief Intro:** Một hướng mềm, có cảm giác nhật ký và màu hoàng hôn nhạt, ưu tiên hình ảnh, nhịp đọc chậm và các vùng giấy có chiều sâu. Hướng này ấm hơn nhưng dễ làm giảm tính cấu trúc của catalog Skills.

**Probability:** 0.08

---

## Hướng được chọn: Bản đồ Biên Độ

### Design Movement

Đây là **Swiss editorial field-guide**: tính kỷ luật của thiết kế thông tin Thụy Sĩ kết hợp với chất liệu của bản đồ khảo sát và ghi chép thực địa. Giao diện không mô phỏng trị liệu hay huyền học; nó tổ chức quyền lựa chọn của người dùng qua trật tự, measure đọc, và dấu mốc rõ ràng.

### Core Principles

1. **Một hệ trục xuyên suốt.** Masthead, eyebrow, title, search, card và footer dùng cùng outer gutter và cùng giới hạn content; không có template tự tạo hệ căn lề riêng.
2. **Mật độ theo nhiệm vụ.** Trang định hướng có khoảng thở lớn, catalog có card compact, tài liệu có reading measure hẹp; khác nhau về density nhưng không khác nhau về token.
3. **Cấu trúc trước trang trí.** Rule line, index, nhãn và vùng bề mặt phải tạo hierarchy trước khi hình ảnh hoặc shadow xuất hiện.
4. **Đọc là tương tác chính.** Button, disclosure và menu rõ trạng thái nhưng không cạnh tranh với text; hình động chỉ xác nhận hành động.

### Color Philosophy

Nền giấy khoáng **Chalk** mang cảm giác trung tính và ít gây mỏi. **Atlas Green** là màu định hướng duy nhất cho active states, focus và hành động chính; **Terracotta** chỉ đánh dấu các nuance/cảnh báo nội dung, không dùng làm CTA. Màu xanh rêu nhạt tạo surface phụ để bề mặt có cấp bậc mà không cần gradient hay neon.

| Vai trò | Token định hướng | Ý nghĩa |
| --- | --- | --- |
| Nền chính | Chalk `#F7F6EF` | Giấy khảo sát, bề mặt đọc dài |
| Mực chính | Ink `#173837` | Tương phản trầm, không tuyệt đối đen |
| Màu thương hiệu | Atlas Green `#1D6A62` | Hướng đi, focus, CTA chính |
| Surface phụ | Moss `#E7EFE8` | Vùng callout, transition mềm |
| Dấu hiệu phụ | Terracotta `#9B5540` | Metadata/marker không khẩn cấp |
| Rule | Line `#D6DED7` | Căn chỉnh và phân lớp, không tạo card-heavy UI |

### Layout Paradigm

Desktop dùng **biên trái metadata + trường đọc chính**: masthead một hàng, dưới đó một rail hẹp chứa section index/eyebrow và một reading field thay đổi theo nhiệm vụ. Home dùng hero split 5/7 với hình ảnh ở cột phụ; Skills dùng rail 3/9 và catalog cards 2 cột; Documents/Info dùng rail 3/9 nhưng vùng văn bản giữ `max-width` nhỏ hơn. Tablet chuyển thành header stack gọn và một content field; mobile giữ một trục 20px, metadata nằm trên title thay vì tạo sidebar giả.

### Signature Elements

1. **Coordinate labels:** metadata chữ hoa nhỏ theo mẫu `01 / ORIENTATION`, luôn neo cùng baseline với title hoặc content block.
2. **Survey rules:** đường rule mảnh, ngắn ở rail và dài ở content, tạo continuity thay cho việc bao mọi thứ bằng border radius.
3. **Numbered markers:** số serif lớn, nhẹ, xuất hiện ở index/card mà không chiếm vai trò headline.

### Interaction Philosophy

Navigation active là một marker nền nhẹ thay vì pill dày. CTA chính là mực xanh solid, CTA phụ là text link có arrow; card toàn phần không trở thành button nếu chỉ hành động một chỗ. Menu nổi theo anchor, không làm dịch layout. Search là một công cụ đọc, không phải một khối UI tách biệt.

### Animation

Chỉ transition opacity/transform 160-220ms với `cubic-bezier(0.23, 1, 0.32, 1)`. Dropdown scale từ `0.98` tại trigger, cards nâng tối đa 1px khi hover, icon arrow dịch 2px. Focus, keyboard navigation và reduced motion luôn tức thời; `prefers-reduced-motion` tắt toàn bộ motion không thiết yếu.

### Typography System

**Georgia** là display serif: title `clamp(3rem, 6vw, 6.25rem)` ở desktop, giảm theo mobile nhưng giữ line-height 0.94-1.0. **Manrope Variable** là sans cho body, labels, controls và data; body dùng 16-18px với line-height 1.65. Eyebrow luôn 11px uppercase, tracking 0.16-0.2em. Không dùng cỡ title tùy tiện theo từng page; Documents và Info dùng title scale thấp hơn Home/Skills một bậc.

### Brand Essence

**SoulMap AI là field guide phản chiếu dành cho người muốn định hướng bằng ngôn ngữ rõ ràng mà không trao quyền diễn giải cho hệ thống.** Tính cách: **điềm tĩnh, có cấu trúc, không chiếm hữu**.

### Brand Voice

Headline nêu một hướng hoặc giới hạn cụ thể, không hứa hẹn chuyển hóa. CTA diễn tả hành động đọc/khảo sát, không dùng áp lực hay lời mời chung chung.

> "Chọn một lớp, không phải một câu trả lời."
> "Đọc các ranh giới trước khi dùng một công cụ."

### Wordmark & Logo

Giữ compass mark là biểu tượng không chữ. Wordmark là `SoulMap AI` bằng Georgia đậm vừa, với khoảng cách chữ optical và chiều cao được căn theo mark; nó luôn xuất hiện như một field mark, không như logo SaaS thuần sans.

### Signature Brand Color

**Atlas Green `#1D6A62`** là màu nhận diện duy nhất: dùng cho mực hành động, active map marker, focus và icon định hướng.
