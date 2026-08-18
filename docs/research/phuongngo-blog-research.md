# Phân tích blog Phuong Ngo và phạm vi chuyển hóa cho SoulMap AI

**Ngày nghiên cứu:** 2026-08-18. **Nguồn chính:** [Phuong Ngo Blog][1]. **Mục tiêu:** xác định cơ chế phân trang, lập corpus công khai để phân tích chủ đề, rồi chỉ chuyển hóa những nguyên tắc phù hợp với doctrine **mirror-not-guide** của SoulMap AI. Báo cáo này không phải bản sao nội dung nguồn.

## Kết luận điều hành

Blog có cấu trúc **Squarespace server-rendered**, không cần endpoint AJAX riêng cho danh sách bài. Trang `/blog` hiển thị 20 bài và liên kết `Older Posts` bằng `rel="next"` tới URL dạng `?offset=<timestamp>`. Việc lần theo 16 trang danh sách kết thúc tự nhiên khi không còn liên kết `Older Posts`. Sitemap công khai liệt kê **301 URL bài viết**, khớp hoàn toàn với 301 URL thu được từ pagination.

Phần lớn các chủ đề có giá trị nhân văn đã có chỗ tương ứng trong SoulMap, đặc biệt là `divine-guidance`, `spiritual-discernment`, `empath-boundary`, `life-direction`, `creative-drought`, `grief` và các lớp voice/safety. Vì vậy, tạo một framework mới dựa trên blog sẽ làm trùng lặp cấu trúc hiện tại. Phần đáng tích hợp nhất là một refinement nhỏ cho `skills/spiritual/spiritual-discernment.md`: **information hygiene và symbolic translation**, tức giữ một diễn giải tâm linh ở trạng thái tạm thời, đưa nó trở lại trải nghiệm quan sát được, bối cảnh cảm xúc, đời sống thường ngày và quyền tự quyết của người dùng.

Ngoài ra, đã thêm phrase packs tiếng Việt được **viết mới cho SoulMap** vào bốn nhóm phát hiện spiritual bypass, cùng regression tests tương ứng. Không có câu nào được bê nguyên từ bài blog vào skill hay test.

## Khám phá cơ chế blog

| Thành phần | Kết quả quan sát |
| --- | --- |
| Nền tảng | Squarespace, nhận diện qua class collection và asset/script markers |
| Kiểu danh sách | HTML server-rendered, grid 20 bài mỗi trang |
| Pagination | Link `Older Posts`, `rel="next"`, dạng `/blog?offset=<timestamp>` |
| Trang trước | Khi có, link `Newer Posts`, `rel="prev"`, có `reversePaginate=true` |
| AJAX/API | Không cần gọi endpoint AJAX cho blog list; `/api/` còn bị robots disallow |
| Sitemap | `/sitemap.xml` chứa 330 URL, trong đó 301 URL thuộc `/blog/<slug>` |
| Phạm vi crawl | 16 trang listing, 301 bài chi tiết, 301 canonical duy nhất |
| Kết quả tải | 301/301 thành công, không lỗi, không trùng canonical |

Crawler Python chỉ gửi GET tuần tự với user-agent nghiên cứu riêng, delay giữa các request, không tải hình ảnh, không gọi API bị hạn chế và không thực thi JavaScript từ nguồn. `robots.txt` cho phép đường dẫn `/blog` đối với user-agent chung nhưng cấm các khu vực cấu hình, tìm kiếm, static và API không liên quan đến nghiên cứu.

## Phân tích corpus

Cấu trúc bài chi tiết ổn định: tiêu đề nằm ở `.entry-title`, ngày ở `time.dt-published`, còn phần nội dung chính ở `.blog-item-content.e-content`. Corpus phân tích gồm khoảng **351.182 token dạng từ theo bộ đếm heuristic**, với độ dài bài trung vị khoảng **1.011 từ**. Con số này dùng để mô tả corpus đã crawl, không phải đo lường chất lượng hay tầm quan trọng của từng bài.

Một bước semantic analysis theo lô được dùng như công cụ phụ trợ để tránh kết luận chỉ từ từ khóa. Các kết quả được kiểm tra lại against doctrine hiện hữu và không được dùng để sao chép văn phong, câu chữ, case của khách hàng, bản dịch sách hoặc các khẳng định siêu hình.

| Nhóm chủ đề quan sát được | Quyết định đối với SoulMap |
| --- | --- |
| Tự thành thật, tự chủ, khôi phục agency | Phù hợp cao; đã có trong brand doctrine, mirror, direction và meaning integration |
| Trực giác, phóng chiếu, urgency, tìm xác nhận bên ngoài | Phù hợp cao; đã có trong `divine-guidance` và `spiritual-discernment`, cần refinement về reality contact |
| Được nhìn thấy, ranh giới, nhạy cảm và quan hệ | Phù hợp có điều kiện; đã có `fear-of-visibility`, `empath-boundary` và `relationship-reflection` |
| Grounding, nhịp sống thường ngày, áp lực phải thức tỉnh | Phù hợp cao; nên diễn đạt bằng grounded reflection, không biến thành lời khuyên hay nghi thức |
| Sáng tạo, ý nghĩa công việc và cạn động lực | Đã có `creative-drought` và `life-direction`; không cần framework mới |
| Tang chế, mất mát sinh sản, cái chết | Chỉ dùng với grief/safety guardrails; không nhập khẩu giải thích afterlife hoặc case riêng tư |
| Guides, channeling, past lives, cosmology | Chỉ theo frame do user đưa vào; không xác nhận, giảng giải hay biến thành authority |
| Marketing, booking, shop, khóa học | Loại trừ hoàn toàn khỏi SoulMap knowledge |

Phân tích heuristic cũng cho thấy tín hiệu rủi ro xuất hiện dày trong corpus: ngôn ngữ siêu hình/xác tín, nội dung có dấu hiệu dịch hoặc trích từ nguồn khác, và các chủ đề chạm tới chẩn đoán, tổn thất hoặc tâm lý nhạy cảm. Đây là lý do các phần này được dùng như **negative boundary evidence**, không phải nguồn nội dung để nhập vào SoulMap.

## Phần đã tích hợp

### Information hygiene và symbolic translation

`skills/spiritual/spiritual-discernment.md` hiện có một section mới yêu cầu phân biệt bốn lớp: **trải nghiệm trực tiếp, diễn giải được gán, bối cảnh cảm xúc và reality contact**. Section này không phủ nhận ngôn ngữ tâm linh, nhưng ngăn nó trở thành quyền lực cao hơn đời sống quan sát được.

Section cũng mô tả cách chuyển một biểu tượng về ngôn ngữ trải nghiệm mà không dạy hệ thống siêu hình. Chẳng hạn, "guide" có thể trở thành câu hỏi về inner authority, "chakra" có thể trở thành câu hỏi về nơi cảm giác được nhận biết trong cơ thể, còn "karma" có thể trở thành câu hỏi về pattern và responsibility. Đây là **lenses for reflection**, không phải tuyên bố sự thật khách quan.

Với quyết định rủi ro cao, lựa chọn không thể đảo ngược, distress nghiêm trọng hoặc nguy cơ gây hại, skill mới nhấn mạnh rằng diễn giải tâm linh không được là authority duy nhất. SoulMap phải trở về observed reality, trusted human support và professional care khi phù hợp.

### Vietnamese spiritual-bypass phrase packs

Đã bổ sung các cụm tiếng Việt được authored cho bốn nhóm parser hiện có:

| Nhóm | Mục đích |
| --- | --- |
| `Dismissing Pain` | Phát hiện cách dùng "bài học", "buông bỏ", "biết ơn" để bỏ qua cảm xúc chưa được cảm nhận |
| `Premature Acceptance` | Phát hiện tuyên bố đã bình an/tha thứ/vượt qua khi tiến trình vẫn chưa được nhìn rõ |
| `Spiritual Inflation` | Phát hiện ngôn ngữ specialness, tầng cao hơn hoặc dùng identity tâm linh để tạo khoảng cách |
| `Bypassing Accountability` | Phát hiện cách đẩy trách nhiệm sang nghiệp, vũ trụ, "người đến để dạy mình" hoặc manifesting |
| `Genuine Integration Signals` | Giảm false positive khi người dùng vẫn đang cảm nhận, xử lý, mâu thuẫn hoặc chưa hoàn toàn chấp nhận |

Regression coverage mới nằm ở `tests/regression/test_soulmap_vietnamese_bypass_phrases.py`. Detector vẫn là **secondary layer**, không trở thành primary framework.

## Nội dung không được tích hợp

Không đưa vào SoulMap các bản dịch hoặc đoạn trích dài từ sách, transcript channeling, thư/case của khách hàng, thông tin nhận diện cá nhân, nội dung thương mại, quy trình gọi guides hoặc nghi thức, kỹ thuật regression/past-life recall, lời hứa chữa lành, dự đoán, chẩn đoán, hoặc khẳng định về cơ chế afterlife, spirit entities, cosmic hierarchy và numerical consciousness maps.

Cũng không chuyển các recommendation mang tính prescriptive thành "action steps" trong conversational SoulMap, vì AGENTS.md cấm biến mirror thành advisor và cấm ngôn ngữ tạo phụ thuộc. Những ý tưởng như consumer literacy hay source hygiene chỉ được giữ ở mức boundary/reflection, không thành chứng chỉ, nghi thức hay hệ thống chấm điểm tâm linh.

## Provenance và trạng thái dữ liệu

Corpus HTML/JSONL chỉ được lưu tạm ngoài repository tại `/tmp/phuongngo_research` để phân tích nội bộ. Repository chỉ giữ báo cáo provenance và phần Markdown authored đã tích hợp. Không có raw article text, hình ảnh, bản dịch, client anecdote hay source prose nào được thêm vào artifact SoulMap.

Các thay đổi này chỉ là thay đổi local trên branch hiện tại và chưa được commit/push trong bước nghiên cứu này. Sau khi chạy đầy đủ validation, có thể tạo commit/PR riêng để user review; không tự merge.

## References

[1]: https://www.phuongngo.co/blog "Phuong Ngo Blog"
[2]: https://www.phuongngo.co/sitemap.xml "Phuong Ngo XML Sitemap"
[3]: https://www.phuongngo.co/robots.txt "Phuong Ngo robots.txt"
[4]: https://www.phuongngo.co/blog/5-s-tht-bn-s-nhn-ra-sau-khi-thc-tnh-tm-linh "Phuong Ngo blog article sample"
