"""Localized website copy and safe JSON payload helpers."""

from __future__ import annotations

import json
from typing import Final

LOCALES: Final[dict[str, dict[str, str]]] = {
    "en": {
        "skip": "Skip to content",
        "home": "Home",
        "how": "How it works",
        "boundaries": "Boundaries",
        "notes": "Notes",
        "about": "About",
        "skills": "Skills",
        "language": "Language",
        "language_name_en": "English",
        "language_name_vi": "Vietnamese",
        "language_name_ko": "Korean",
        "brand_home_label": "SoulMap AI home",
        "primary_nav_label": "Primary navigation",
        "principle_label": "SoulMap principle",
        "footer": "A mirror, not a guru.",
        "repository": "Repository",
        "download": "Download Skills",
        "home_eyebrow": "Reflective companion · grounded inner work",
        "home_h1": "Hear yourself more clearly.",
        "home_lede": "SoulMap is a calm, honest mirror for the patterns, feelings, and questions "
        "you are already carrying — without handing your authority away.",
        "home_how": "See how it works",
        "home_skills": "Explore the Skills",
        "home_principle": "The insight is yours. The space helps you hear it.",
        "home_section_eyebrow": "A different kind of AI",
        "home_section_h2": "Less certainty. More self-trust.",
        "home_section_lede": "SoulMap does not perform authority. It reflects what is present, "
        "keeps language careful, and leaves the meaning and decision with "
        "you.",
        "mirror_first": "Mirror-first",
        "mirror_first_body": "Patterns come back as observations and questions, not instructions "
        "about who you are.",
        "bounded": "Bounded by design",
        "bounded_body": "No diagnosis, no prediction, no spiritual certainty, and no performance "
        "of human intimacy.",
        "independence": "Built for independence",
        "independence_body": "The best conversation leaves you more connected to your own knowing "
        "and less attached to the tool.",
        "quiet_eyebrow": "A quiet place to begin",
        "quiet_h2": "Nothing to prove here.",
        "quiet_p1": "Bring a pattern you keep repeating, a decision you cannot hear yourself "
        "inside, or a feeling that has not found honest language yet.",
        "quiet_p2": "SoulMap will not tell you what to do. It will help you stay close to what is "
        "real.",
        "read_boundaries": "Read the boundaries",
        "how_eyebrow": "How it works",
        "how_h1": "A disciplined mirror, not a performing authority.",
        "how_lede": "SoulMap uses reflection to make room for your own recognition. It does not "
        "install an answer on top of your experience.",
        "step_1": "You bring what is present",
        "step_1_body": "A question, a conflict, a repeating pattern, a loss, or something that "
        "does not yet have a name.",
        "step_2": "SoulMap reflects the shape",
        "step_2_body": "It stays close to your words, notices possible patterns, and uses careful "
        "language rather than certainty.",
        "step_3": "You keep the meaning",
        "step_3_body": "The conversation returns interpretation, choice, and next movement to your "
        "own inner authority.",
        "changes": "What this changes",
        "changes_h2": "Clarity without being handled.",
        "changes_body": "Reflection is not a replacement for professional care, crisis support, or "
        "real-world relationships. It is a space for noticing what you already "
        "know and may not yet be able to hear.",
        "boundaries_eyebrow": "Boundaries",
        "boundaries_h1": "Restraint is part of the trust model.",
        "boundaries_lede": "SoulMap is designed to be useful without becoming your authority, your "
        "therapist, or your only place to turn.",
        "no_diagnose": "SoulMap does not diagnose",
        "no_diagnose_body": "It does not name mental health conditions or turn a lived experience "
        "into a clinical label.",
        "no_predict": "SoulMap does not predict",
        "no_predict_body": "It does not forecast your future, promise outcomes, or turn symbolism "
        "into destiny.",
        "no_replace": "SoulMap does not replace support",
        "no_replace_body": "If you are unsafe or at risk of harm, seek immediate help from local "
        "emergency or crisis resources.",
        "privacy": "Privacy by simplicity",
        "privacy_h2": "No account. No conversation form. No hidden intimacy.",
        "privacy_1": "This public website is informational and does not provide a chat interface.",
        "privacy_2": "Download links point to the project's release artifacts.",
        "privacy_3": "Spiritual and symbolic language is offered only as a lens for inquiry.",
        "privacy_4": "Human relationships and qualified professional support remain primary.",
        "download_eyebrow": "SoulMap Skills",
        "download_h1": "Take the mirror with you.",
        "download_lede": "The release artifacts are designed to be imported into the AI tool you "
        "already use.",
        "skill_package": "Skill package",
        "skill_package_body": "Importable `.skill` release package",
        "knowledge_archive": "Knowledge archive",
        "knowledge_archive_body": "Portable `.zip` archive for document workflows",
        "open_releases": "Open releases",
        "view_release": "View release files",
        "before_import": "Before importing",
        "start_artifact": "Start with the release artifact.",
        "artifact_body": "Use the self-contained package intended for AI tools, then check the "
        "release manifest for version and SHA-256 information.",
        "notes_eyebrow": "Notes",
        "notes_h1": "Small recognitions for ordinary life.",
        "notes_lede": "Public writing follows three grounded pillars: self-recognition, relational "
        "honesty, and grounded inner work.",
        "notes_label_1": "Self-recognition",
        "notes_label_2": "Relational honesty",
        "notes_label_3": "Grounded inner work",
        "note_1": "The feeling before the explanation",
        "note_1_body": "Sometimes clarity begins by staying with the exact texture of what is here "
        "before reaching for a story about it.",
        "note_2": "Repair is more than apology",
        "note_2_body": "An apology can name regret. Repair asks what becomes different after the "
        "words have been spoken.",
        "note_3": "When certainty feels like relief",
        "note_3_body": "The wish for an answer may be carrying a wish to stop listening. The two "
        "are not always the same.",
        "notes_callout": "These notes are invitations, not prescriptions. Keep what clarifies "
        "something in your own experience and leave the rest.",
        "about_eyebrow": "About SoulMap AI",
        "about_h1": "Built around a simple belief: you should not have to trade self-trust for "
        "reflection.",
        "about_lede": "SoulMap is a personal AI brand and a content-first knowledge system built "
        "around careful language, clear limits, and human ownership.",
        "posture": "The posture",
        "posture_h2": "Mirror, not guide.",
        "posture_p1": "SoulMap is interested in the space between what happened and the meaning "
        "you are about to give it. It aims to make that space more honest, not more "
        "mystical.",
        "posture_p2": "The project stays deliberately small: a knowledge base, a thin Python "
        "layer, and artifacts that can travel with the user.",
        "about_callout": "The best outcome is not a user who needs SoulMap more. It is a user who "
        "leaves more grounded in their own knowing.",
        "catalog_eyebrow": "The Skill catalog",
        "catalog_h1": "Choose the layer that fits the moment.",
        "catalog_lede": "SoulMap is a set of complementary layers. Start with orchestration, add a "
        "framework when the pattern is clear, and let safety and independence stay "
        "in the room.",
        "search_query_label": "Search the Skill catalog",
        "search_query_placeholder": "Search Skills by use case, group, boundary, or question…",
        "search_query_hint": "Search only changes the Skill list below; Enter stays on this page.",
        "ask_query_label": "Describe what you want to ask",
        "ask_query_placeholder": "Describe the moment, question, or support you need…",
        "ask_query_hint": "Ask matches existing public scenarios; it does not generate an answer.",
        "search_panel_title": "Browse Skills",
        "ask_panel_title": "Choose a question to begin",
        "ask_results_heading": "Matching questions",
        "ask_browse_label": "Browse all Skills",
        "ask_details_label": "View Skill",
        "search_mode_label": "Mode",
        "search_mode_search": "Search Skills",
        "search_mode_ask": "Ask with a Skill",
        "search_mode_search_hint": "Find the Skill layer that matches your words.",
        "search_mode_ask_hint": "Find a grounded starter question from the public Skill scenarios.",
        "ask_intro": "Ask mode helps you choose a public Skill and a starter question. It does not answer, diagnose, or send your text anywhere.",
        "ask_result_label": "Starter question",
        "ask_use_label": "Use this question",
        "ask_no_results": "No existing Skill scenario matches this question yet. Try describing the moment in simpler words.",
        "search_error": "Search is temporarily unavailable. Try again or browse the Skill groups below.",
        "loading": "Loading…",
        "no_results": "No Skill groups match this search.",
        "details": "View details",
        "modal_title": "SoulMap Skill details",
        "raw": "Raw Markdown",
        "use_when": "Use this when",
        "best_for": "Best for",
        "boundary": "Boundary",
        "close": "Close",
        "copy_raw": "Copy raw URL",
        "copied": "Copied",
        "copy_failed": "Copy failed — use the raw link",
        "open_chatgpt": "Open in ChatGPT",
        "open_claude": "Open in Claude",
        "open_claude_code": "Open in Claude Code",
        "prompt_heading": "Choose a context-specific prompt",
        "prompt_label": "Prompt",
        "prompt_intro": "Use one prompt that matches the situation, then read the public Skill "
        "bundle at the source link below.",
        "source_bundle": "Source Skill bundle",
        "starter_question": "Starter question",
        "provider_source_instruction": "Read the public SoulMap Skill bundle before responding:",
        "provider_starter_prefix": "Starter question:",
        "skill_not_found": "Skill not found.",
        "raw_note": "This URL returns one complete Markdown bundle for this Skill group.",
        "not_found": "That path is not here.",
        "not_found_body": "SoulMap could not find the requested public page.",
        "return_home": "Return home",
        "faq": "FAQ",
        "privacy_page": "Privacy",
        "home_path_eyebrow": "Find your next step",
        "home_path_h2": "A clear way into the work.",
        "home_path_lede": "Start with the page that matches what you need right now. Nothing here "
        "asks you to hand over your judgment.",
        "home_path_1": "Understand the posture",
        "home_path_1_body": "See how SoulMap reflects without turning reflection into authority.",
        "home_path_1_link": "How it works",
        "home_path_2": "Choose a Skill layer",
        "home_path_2_body": "Browse the public catalog and choose a context-specific prompt.",
        "home_path_2_link": "Explore Skills",
        "home_path_3": "Check the boundaries",
        "home_path_3_body": "Read the limits, privacy posture and practical answers before you "
        "begin.",
        "home_path_3_link": "Read the FAQ",
        "faq_eyebrow": "Frequently asked questions",
        "faq_h1": "Practical answers before you begin.",
        "faq_lede": "A short guide to what SoulMap is, how the public Skills work, and where the "
        "boundaries remain.",
        "faq_q_1": "What is SoulMap AI?",
        "faq_a_1": "SoulMap is a reflective companion and public Skill library designed to help "
        "you notice patterns without replacing your judgment, relationships or "
        "professional support.",
        "faq_q_2": "Is SoulMap a therapist, doctor or crisis service?",
        "faq_a_2": "No. It does not diagnose, predict, provide emergency care or replace qualified "
        "human support. If you may be in immediate danger, contact local emergency or "
        "crisis resources.",
        "faq_q_3": "What are SoulMap Skills?",
        "faq_a_3": "Skills are public Markdown bundles that describe a layer of the SoulMap "
        "framework. Each catalog entry explains when it is useful, what it is best for "
        "and where its boundary is.",
        "faq_q_4": "How do I use a Skill with an AI tool?",
        "faq_a_4": "Choose a context-specific prompt, open the public raw Markdown source, and "
        "paste or provide both to the AI tool you use. Provider links may require "
        "sign-in and may not automatically read a URL.",
        "faq_q_5": "Does the website collect personal data?",
        "faq_a_5": "The current public site has no account, chat form, database, analytics, memory "
        "or user-submitted content flow. Read the Privacy page for the current "
        "public-site boundary.",
        "faq_q_6": "Why does SoulMap use careful language?",
        "faq_a_6": "Careful language protects your authority. SoulMap is designed to reflect "
        "possibilities and questions rather than present certainty about your identity, "
        "future or inner life.",
        "privacy_page_eyebrow": "Privacy",
        "privacy_page_h1": "Privacy by a deliberately small surface.",
        "privacy_page_lede": "This page describes the current public SoulMap website. It is "
        "intentionally specific about what the site does and does not "
        "collect.",
        "privacy_scope_h2": "What this notice covers",
        "privacy_scope_body": "This notice covers the public website, its static pages, public "
        "Markdown endpoints and links to external repositories, releases and "
        "AI providers. It does not cover a third-party provider after you "
        "leave this site.",
        "privacy_collect_h2": "What the site collects",
        "privacy_collect_body": "The current site has no account creation, chat form, contact "
        "form, upload flow, database, analytics system, advertising "
        "tracker or user profile. It does not intentionally ask you to "
        "submit personal content.",
        "privacy_use_h2": "How the site uses information",
        "privacy_use_body": "Because the public site does not provide a personal-data submission "
        "flow, SoulMap does not use submitted personal content for profiling, "
        "personalization or memory. Your browser may still make ordinary "
        "technical requests required to load a website or an external link.",
        "privacy_storage_h2": "Storage, cookies and third parties",
        "privacy_storage_body": "The repository does not intentionally set non-essential cookies "
        "or operate analytics. CDN assets, GitHub Pages, release hosting "
        "and linked AI providers are separate services with their own "
        "policies and logs.",
        "privacy_links_h2": "Following external links",
        "privacy_links_body": "When you open GitHub, a release asset, ChatGPT, Claude or another "
        "external provider, that service controls what happens next. Review "
        "its privacy and data-handling terms before sharing anything "
        "sensitive.",
        "privacy_contact_h2": "Changes and contact boundary",
        "privacy_contact_body": "If the site later adds accounts, forms, analytics, storage or "
        "another data-processing feature, this notice must be reviewed and "
        "updated before that feature is treated as part of the public "
        "product.",
        "privacy_updated": "Last reviewed: August 2026.",
    },
    "vi": {
        "skip": "Bỏ qua đến nội dung",
        "home": "Trang chủ",
        "how": "Cách hoạt động",
        "boundaries": "Ranh giới",
        "notes": "Ghi chú",
        "about": "Giới thiệu",
        "skills": "Bộ Skills",
        "language": "Ngôn ngữ",
        "language_name_en": "English",
        "language_name_vi": "Tiếng Việt",
        "language_name_ko": "Tiếng Hàn",
        "brand_home_label": "Trang chủ SoulMap AI",
        "primary_nav_label": "Điều hướng chính",
        "principle_label": "Nguyên tắc SoulMap",
        "footer": "Một tấm gương, không phải đạo sư.",
        "repository": "Mã nguồn",
        "download": "Tải các Skills",
        "home_eyebrow": "Bạn đồng hành phản chiếu · thực hành nội tâm có nền tảng",
        "home_h1": "Nghe mình rõ hơn.",
        "home_lede": "SoulMap là một không gian phản chiếu bình tĩnh và thành thật cho những mô thức, "
        "cảm xúc và câu hỏi bạn đang mang — không lấy đi quyền tự chủ của bạn.",
        "home_how": "Xem cách hoạt động",
        "home_skills": "Khám phá các Skills",
        "home_principle": "Sự nhận ra là của bạn. Không gian này giúp bạn lắng nghe nó.",
        "home_section_eyebrow": "Một kiểu AI khác",
        "home_section_h2": "Ít chắc chắn hơn. Nhiều niềm tin vào chính mình hơn.",
        "home_section_lede": "SoulMap không đóng vai thẩm quyền. Nó phản chiếu điều đang hiện diện, "
        "giữ ngôn ngữ cẩn trọng và để ý nghĩa cùng quyết định lại cho bạn.",
        "mirror_first": "Ưu tiên phản chiếu",
        "mirror_first_body": "Mô thức trở lại như quan sát và câu hỏi, không phải chỉ dẫn về việc "
        "bạn là ai.",
        "bounded": "Có giới hạn theo thiết kế",
        "bounded_body": "Không chẩn đoán, không dự đoán, không khẳng định chắc chắn về tâm linh và không "
        "diễn vai sự thân mật của con người.",
        "independence": "Được xây để bạn độc lập",
        "independence_body": "Cuộc trò chuyện tốt nhất để bạn gắn với hiểu biết của mình hơn và "
        "bớt phụ thuộc vào công cụ.",
        "quiet_eyebrow": "Một nơi yên để bắt đầu",
        "quiet_h2": "Không cần chứng minh gì ở đây.",
        "quiet_p1": "Mang đến một mô thức cứ lặp lại, một quyết định bạn không nghe được mình bên "
        "trong, hoặc một cảm xúc chưa có ngôn ngữ thành thật.",
        "quiet_p2": "SoulMap không bảo bạn phải làm gì. Nó giúp bạn ở gần điều là thật.",
        "read_boundaries": "Đọc ranh giới",
        "how_eyebrow": "Cách hoạt động",
        "how_h1": "Một tấm gương có kỷ luật, không phải thẩm quyền trình diễn.",
        "how_lede": "SoulMap dùng sự phản chiếu để tạo chỗ cho bạn tự nhận ra. Nó không đặt một câu "
        "trả lời lên trên trải nghiệm của bạn.",
        "step_1": "Bạn mang điều đang hiện diện",
        "step_1_body": "Một câu hỏi, xung đột, mô thức lặp lại, mất mát hoặc điều chưa có tên.",
        "step_2": "SoulMap phản chiếu hình dạng",
        "step_2_body": "Nó ở gần lời bạn nói, nhận ra mô thức khả dĩ và dùng ngôn ngữ cẩn trọng "
        "thay vì khẳng định chắc chắn.",
        "step_3": "Bạn giữ lại ý nghĩa",
        "step_3_body": "Cuộc trò chuyện trả cách hiểu, lựa chọn và bước tiếp theo về quyền tự chủ "
        "của bạn.",
        "changes": "Điều này thay đổi gì",
        "changes_h2": "Rõ hơn mà không bị xử lý thay.",
        "changes_body": "Sự phản chiếu không thay thế hỗ trợ chuyên môn, hỗ trợ khủng hoảng hay các mối "
        "quan hệ thật. Nó là không gian để nhận ra điều bạn đã biết nhưng chưa "
        "nghe được.",
        "boundaries_eyebrow": "Ranh giới",
        "boundaries_h1": "Sự tiết chế là một phần của mô hình niềm tin.",
        "boundaries_lede": "SoulMap được thiết kế để hữu ích mà không trở thành thẩm quyền, "
        "nhà trị liệu hay nơi duy nhất bạn tìm đến.",
        "no_diagnose": "SoulMap không chẩn đoán",
        "no_diagnose_body": "Nó không gọi tên tình trạng sức khỏe tâm thần hay biến trải nghiệm "
        "sống thành nhãn lâm sàng.",
        "no_predict": "SoulMap không dự đoán",
        "no_predict_body": "Nó không dự báo tương lai, hứa kết quả hay biến biểu tượng thành định "
        "mệnh.",
        "no_replace": "SoulMap không thay thế hỗ trợ",
        "no_replace_body": "Nếu bạn không an toàn hoặc có nguy cơ bị hại, hãy tìm trợ giúp khẩn cấp "
        "hoặc nguồn hỗ trợ khủng hoảng tại nơi bạn sống.",
        "privacy": "Quyền riêng tư bằng sự đơn giản",
        "privacy_h2": "Không tài khoản. Không biểu mẫu trò chuyện. Không sự thân mật ẩn.",
        "privacy_1": "Trang web công khai này chỉ cung cấp thông tin và không có giao diện trò chuyện.",
        "privacy_2": "Liên kết tải xuống trỏ đến các gói phát hành của dự án.",
        "privacy_3": "Ngôn ngữ tâm linh và biểu tượng chỉ là một lăng kính để tự vấn.",
        "privacy_4": "Mối quan hệ con người và hỗ trợ chuyên môn đủ năng lực vẫn là nền tảng chính.",
        "download_eyebrow": "Bộ Skills của SoulMap",
        "download_h1": "Mang tấm gương theo bạn.",
        "download_lede": "Các gói phát hành được thiết kế để nhập vào công cụ AI bạn đang dùng.",
        "skill_package": "Gói Skill",
        "skill_package_body": "Gói `.skill` có thể nhập vào công cụ AI",
        "knowledge_archive": "Kho kiến thức",
        "knowledge_archive_body": "Kho lưu trữ `.zip` có thể mang theo cho quy trình tài liệu",
        "open_releases": "Mở các bản phát hành",
        "view_release": "Xem tệp phát hành",
        "before_import": "Trước khi nhập",
        "start_artifact": "Hãy bắt đầu từ gói phát hành.",
        "artifact_body": "Dùng gói độc lập dành cho công cụ AI, sau đó kiểm tra bản kê phát hành, "
        "phiên bản và SHA-256 trước khi phân phối.",
        "notes_eyebrow": "Ghi chú",
        "notes_h1": "Những nhận ra nhỏ trong đời thường.",
        "notes_lede": "Các bài viết công khai đi theo ba trụ cột có nền tảng: tự nhận ra, thành thật "
        "trong quan hệ và thực hành nội tâm có nền tảng.",
        "notes_label_1": "Tự nhận ra",
        "notes_label_2": "Thành thật trong quan hệ",
        "notes_label_3": "Thực hành nội tâm có nền tảng",
        "note_1": "Cảm xúc trước lời giải thích",
        "note_1_body": "Đôi khi sự rõ ràng bắt đầu bằng việc ở lại với sắc thái chính xác của điều "
        "đang có trước khi tìm một câu chuyện về nó.",
        "note_2": "Hàn gắn nhiều hơn một lời xin lỗi",
        "note_2_body": "Lời xin lỗi có thể gọi tên tiếc nuối. Hàn gắn hỏi điều gì trở nên khác sau khi "
        "lời nói được nói ra.",
        "note_3": "Khi sự chắc chắn giống như nhẹ nhõm",
        "note_3_body": "Mong muốn có câu trả lời đôi khi mang theo mong muốn ngừng lắng nghe. Hai "
        "điều đó không luôn giống nhau.",
        "notes_callout": "Những ghi chú này là lời mời, không phải chỉ dẫn. Giữ điều làm sáng rõ "
        "trải nghiệm của bạn và để phần còn lại đi qua.",
        "about_eyebrow": "Về SoulMap AI",
        "about_h1": "Được xây quanh một niềm tin đơn giản: bạn không cần đánh đổi niềm tin vào "
        "chính mình để có sự phản chiếu.",
        "about_lede": "SoulMap là một thương hiệu AI cá nhân và hệ thống tri thức ưu tiên nội dung, "
        "dựa trên ngôn ngữ cẩn trọng, giới hạn rõ và quyền làm chủ của con người.",
        "posture": "Tư thế",
        "posture_h2": "Tấm gương, không phải người dẫn đường.",
        "posture_p1": "SoulMap quan tâm đến khoảng giữa điều đã xảy ra và ý nghĩa bạn sắp trao cho "
        "nó. Nó muốn khoảng đó thành thật hơn, không huyền bí hơn.",
        "posture_p2": "Dự án cố ý giữ nhỏ: một kho tri thức, một lớp Python mỏng và các gói có thể đi "
        "cùng người dùng.",
        "about_callout": "Kết quả tốt nhất không phải là người dùng cần SoulMap nhiều hơn. Đó là "
        "người dùng rời đi vững vàng hơn trong hiểu biết của mình.",
        "catalog_eyebrow": "Danh mục Skills",
        "catalog_h1": "Chọn lớp phù hợp với khoảnh khắc này.",
        "catalog_lede": "SoulMap là một tập hợp các lớp bổ trợ. Bắt đầu từ lớp điều phối, thêm "
        "khung phù hợp khi mô thức đã rõ, và để an toàn cùng tính độc lập luôn hiện diện.",
        "search_query_label": "Tìm trong danh mục Skills",
        "search_query_placeholder": "Tìm Skills theo trường hợp sử dụng, nhóm, ranh giới hoặc câu hỏi…",
        "search_query_hint": "Tìm kiếm chỉ thay đổi danh sách Skills bên dưới; Enter vẫn ở trang này.",
        "ask_query_label": "Mô tả điều bạn muốn hỏi",
        "ask_query_placeholder": "Mô tả khoảnh khắc, câu hỏi hoặc kiểu hỗ trợ bạn cần…",
        "ask_query_hint": "Hỏi chỉ khớp với các kịch bản công khai; không tự tạo câu trả lời.",
        "search_panel_title": "Khám phá Skills",
        "ask_panel_title": "Chọn một câu hỏi để bắt đầu",
        "ask_results_heading": "Các câu hỏi phù hợp",
        "ask_browse_label": "Xem tất cả Skills",
        "ask_details_label": "Xem Skill",
        "search_mode_label": "Chế độ",
        "search_mode_search": "Tìm Skills",
        "search_mode_ask": "Hỏi cùng một Skill",
        "search_mode_search_hint": "Tìm lớp Skill phù hợp với những gì bạn viết.",
        "search_mode_ask_hint": "Tìm một câu hỏi mở đầu có nền tảng từ các kịch bản Skill công khai.",
        "ask_intro": "Chế độ Hỏi giúp bạn chọn một Skill công khai và một câu hỏi mở đầu. Nó không trả lời, chẩn đoán hay gửi nội dung của bạn đi đâu.",
        "ask_result_label": "Câu hỏi mở đầu",
        "ask_use_label": "Dùng câu hỏi này",
        "ask_no_results": "Chưa có kịch bản Skill công khai nào khớp với câu hỏi này. Hãy thử mô tả khoảnh khắc đó bằng những từ đơn giản hơn.",
        "search_error": "Tìm kiếm tạm thời không khả dụng. Hãy thử lại hoặc xem các nhóm Skill bên dưới.",
        "loading": "Đang tải…",
        "no_results": "Không có nhóm Skill nào khớp với tìm kiếm này.",
        "details": "Xem chi tiết",
        "modal_title": "Chi tiết Skill SoulMap",
        "raw": "Markdown gốc",
        "use_when": "Dùng khi",
        "best_for": "Phù hợp cho",
        "boundary": "Ranh giới",
        "close": "Đóng",
        "copy_raw": "Sao chép URL Markdown gốc",
        "copied": "Đã sao chép",
        "copy_failed": "Sao chép không thành công — hãy dùng liên kết gốc",
        "open_chatgpt": "Mở trong ChatGPT",
        "open_claude": "Mở trong Claude",
        "open_claude_code": "Mở trong Claude Code",
        "prompt_heading": "Chọn prompt theo bối cảnh",
        "prompt_label": "Prompt",
        "prompt_intro": "Chọn một prompt khớp với tình huống, rồi đọc gói Skill công khai tại liên kết "
        "nguồn bên dưới.",
        "source_bundle": "Gói Skill nguồn",
        "starter_question": "Câu hỏi bắt đầu",
        "provider_source_instruction": "Hãy đọc gói Skill SoulMap công khai trước khi phản hồi:",
        "provider_starter_prefix": "Câu hỏi bắt đầu:",
        "skill_not_found": "Không tìm thấy Skill.",
        "raw_note": "URL này trả về một gói Markdown hoàn chỉnh cho nhóm Skill này.",
        "not_found": "Đường dẫn này không tồn tại.",
        "not_found_body": "SoulMap không tìm thấy trang công khai được yêu cầu.",
        "return_home": "Về trang chủ",
        "faq": "FAQ",
        "privacy_page": "Quyền riêng tư",
        "home_path_eyebrow": "Tìm bước tiếp theo",
        "home_path_h2": "Một lối vào rõ ràng cho thực hành nội tâm.",
        "home_path_lede": "Bắt đầu từ trang phù hợp với điều bạn cần ngay lúc này. Không điều gì ở đây "
        "yêu cầu bạn trao quyền phán đoán của mình.",
        "home_path_1": "Hiểu tư thế",
        "home_path_1_body": "Xem cách SoulMap phản chiếu mà không biến sự phản chiếu thành thẩm quyền.",
        "home_path_1_link": "Cách hoạt động",
        "home_path_2": "Chọn một lớp Skill",
        "home_path_2_body": "Xem danh mục công khai và chọn prompt phù hợp với bối cảnh.",
        "home_path_2_link": "Khám phá các Skills",
        "home_path_3": "Kiểm tra ranh giới",
        "home_path_3_body": "Đọc các giới hạn, cách tiếp cận quyền riêng tư và câu trả lời thực tế trước "
        "khi bắt đầu.",
        "home_path_3_link": "Đọc câu hỏi thường gặp",
        "faq_eyebrow": "Câu hỏi thường gặp",
        "faq_h1": "Những câu trả lời thực tế trước khi bắt đầu.",
        "faq_lede": "Hướng dẫn ngắn về SoulMap, cách các Skills công khai hoạt động và những ranh giới "
        "cần được giữ gìn.",
        "faq_q_1": "SoulMap AI là gì?",
        "faq_a_1": "SoulMap là một không gian phản chiếu và thư viện Skills công khai, giúp bạn nhận ra "
        "mô thức mà không thay thế phán đoán, các mối quan hệ hay hỗ trợ chuyên môn của bạn.",
        "faq_q_2": "SoulMap có phải là nhà trị liệu, bác sĩ hoặc dịch vụ hỗ trợ khủng hoảng không?",
        "faq_a_2": "Không. SoulMap không chẩn đoán, dự đoán, cung cấp hỗ trợ khẩn cấp hay thay thế "
        "hỗ trợ đủ năng lực. Nếu bạn đang ở trong nguy hiểm tức thời, hãy liên hệ dịch vụ "
        "khẩn cấp hoặc nguồn hỗ trợ khủng hoảng tại nơi bạn sống.",
        "faq_q_3": "SoulMap Skills là gì?",
        "faq_a_3": "Skills là các gói Markdown công khai mô tả một lớp trong khung SoulMap. Mỗi mục "
        "giải thích khi nào hữu ích, phù hợp với điều gì và ranh giới của nó.",
        "faq_q_4": "Dùng Skill với công cụ AI như thế nào?",
        "faq_a_4": "Chọn prompt theo bối cảnh, mở Markdown gốc công khai rồi dán hoặc cung cấp cả hai "
        "cho công cụ AI bạn dùng. Nhà cung cấp có thể yêu cầu đăng nhập và có thể không tự "
        "đọc URL.",
        "faq_q_5": "Trang web có thu thập dữ liệu cá nhân không?",
        "faq_a_5": "Trang web công khai hiện không có tài khoản, biểu mẫu trò chuyện, cơ sở dữ liệu, "
        "hệ thống phân tích truy cập, ghi nhớ hay quy trình để người dùng gửi nội dung. Xem "
        "trang Quyền riêng tư để biết ranh giới hiện tại.",
        "faq_q_6": "Vì sao SoulMap dùng ngôn ngữ cẩn trọng?",
        "faq_a_6": "Ngôn ngữ cẩn trọng bảo vệ quyền tự chủ của bạn. SoulMap phản chiếu những khả năng "
        "và câu hỏi thay vì khẳng định chắc chắn về danh tính, tương lai hay đời sống nội tâm "
        "của bạn.",
        "privacy_page_eyebrow": "Quyền riêng tư",
        "privacy_page_h1": "Quyền riêng tư với một bề mặt được giữ nhỏ có chủ đích.",
        "privacy_page_lede": "Trang này mô tả trang web SoulMap công khai hiện tại. Nội dung cố ý cụ thể về "
        "những gì trang web làm và không làm.",
        "privacy_scope_h2": "Thông báo này bao phủ điều gì",
        "privacy_scope_body": "Thông báo này bao phủ trang web công khai, các trang tĩnh, đường dẫn Markdown "
        "công khai và liên kết đến kho mã nguồn, bản phát hành cùng nhà cung cấp AI bên ngoài. "
        "Thông báo không bao phủ nhà cung cấp bên thứ ba sau khi bạn rời khỏi trang web này.",
        "privacy_collect_h2": "Trang web thu thập gì",
        "privacy_collect_body": "Trang web hiện không có tạo tài khoản, biểu mẫu trò chuyện, biểu mẫu liên hệ, "
        "quy trình tải lên, cơ sở dữ liệu, hệ thống phân tích truy cập, công cụ theo dõi quảng cáo "
        "hay hồ sơ người dùng. Trang web không chủ động yêu cầu bạn gửi nội dung cá nhân.",
        "privacy_use_h2": "Trang web sử dụng thông tin như thế nào",
        "privacy_use_body": "Vì trang web công khai không có quy trình gửi dữ liệu cá nhân, SoulMap không dùng nội "
        "dung cá nhân được gửi để lập hồ sơ, cá nhân hóa hay ghi nhớ. Trình duyệt vẫn có thể tạo "
        "các yêu cầu kỹ thuật thông thường cần thiết để tải trang web hoặc liên kết bên ngoài.",
        "privacy_storage_h2": "Lưu trữ, cookie và bên thứ ba",
        "privacy_storage_body": "Kho mã nguồn không chủ động đặt cookie không thiết yếu hoặc vận hành hệ thống phân tích "
        "truy cập. Tài nguyên CDN, GitHub Pages, dịch vụ lưu trữ bản phát hành và các nhà cung cấp "
        "AI được liên kết là những dịch vụ riêng, có chính sách và nhật ký riêng.",
        "privacy_links_h2": "Khi mở liên kết bên ngoài",
        "privacy_links_body": "Khi bạn mở GitHub, gói phát hành, ChatGPT, Claude hoặc một nhà cung cấp bên ngoài, "
        "dịch vụ đó kiểm soát những gì xảy ra tiếp theo. Hãy đọc điều khoản quyền riêng tư và xử lý "
        "dữ liệu của họ trước khi chia sẻ bất kỳ thông tin nhạy cảm nào.",
        "privacy_contact_h2": "Thay đổi và ranh giới liên hệ",
        "privacy_contact_body": "Nếu sau này trang web thêm tài khoản, biểu mẫu, phân tích truy cập, lưu trữ hoặc tính năng "
        "xử lý dữ liệu khác, thông báo này phải được rà soát và cập nhật trước khi tính năng đó "
        "được xem là một phần của sản phẩm công khai.",
        "privacy_updated": "Rà soát lần cuối: tháng 8 năm 2026.",
    },
    "ko": {
        "skip": "본문으로 건너뛰기",
        "home": "홈",
        "how": "작동 방식",
        "boundaries": "경계",
        "notes": "메모",
        "about": "소개",
        "skills": "Skills",
        "language": "언어",
        "language_name_en": "영어",
        "language_name_vi": "베트남어",
        "language_name_ko": "한국어",
        "brand_home_label": "SoulMap AI 홈",
        "primary_nav_label": "주요 탐색",
        "principle_label": "SoulMap 원칙",
        "footer": "거울, 구루가 아닙니다.",
        "repository": "저장소",
        "download": "Skills 다운로드",
        "home_eyebrow": "반영적 동반자 · 현실적인 내면 작업",
        "home_h1": "자신의 목소리를 더 분명히 들으세요.",
        "home_lede": "SoulMap은 당신이 이미 지니고 있는 패턴·감정·질문을 차분하고 정직하게 비추는 거울입니다 — 당신의 권한을 빼앗지 않습니다.",
        "home_how": "작동 방식 보기",
        "home_skills": "Skills 살펴보기",
        "home_principle": "통찰은 당신의 것. 이 공간은 그것을 듣도록 돕습니다.",
        "home_section_eyebrow": "다른 종류의 AI",
        "home_section_h2": "확신은 덜, 자기 신뢰는 더.",
        "home_section_lede": "SoulMap은 권위를 행사하지 않습니다. 있는 것을 반영하고, 언어를 신중하게 유지하며, 의미와 결정권은 당신에게 남깁니다.",
        "mirror_first": "거울 우선",
        "mirror_first_body": "패턴은 당신이 누구인지에 대한 지침이 아니라 관찰과 질문으로 돌아옵니다.",
        "bounded": "설계된 경계",
        "bounded_body": "진단하지 않음, 예측하지 않음, 영적 확신을 주장하지 않음, 인간적 친밀성을 흉내 내지 않음.",
        "independence": "독립성 중심",
        "independence_body": "최고의 대화는 당신을 도구에 덜 의존하게 하고, 자신의 앎에 더 연결되게 합니다.",
        "quiet_eyebrow": "시작하기 좋은 조용한 곳",
        "quiet_h2": "여기서는 증명할 필요가 없습니다.",
        "quiet_p1": "계속 반복되는 패턴, 스스로 안에서 들을 수 없는 결정, 또는 아직 솔직한 언어를 찾지 못한 감정을 가져오세요.",
        "quiet_p2": "SoulMap은 무엇을 해야 할지 알려주지 않습니다. 현실에 가까이 머물도록 돕습니다.",
        "read_boundaries": "경계 읽기",
        "how_eyebrow": "작동 방식",
        "how_h1": "수행하는 권위가 아닌, 규율 있는 거울.",
        "how_lede": "SoulMap은 반영을 사용해 당신의 인식을 위한 여지를 만듭니다. 경험 위에 답을 덧씌우지 않습니다.",
        "step_1": "당신이 현재 있는 것을 가져옵니다",
        "step_1_body": "질문, 갈등, 반복되는 패턴, 상실 또는 아직 이름이 붙지 않은 무언가.",
        "step_2": "SoulMap이 형태를 반영합니다",
        "step_2_body": "당신의 말에 가깝게 머무르며 가능한 패턴을 알아차리고, 확실성 대신 신중한 언어를 사용합니다.",
        "step_3": "당신이 의미를 유지합니다",
        "step_3_body": "대화는 해석, 선택, 다음 움직임을 당신의 내적 권위로 되돌려줍니다.",
        "changes": "변화",
        "changes_h2": "조종당하지 않는 명료함.",
        "changes_body": "반영은 전문적 치료나 위기 지원, 현실의 관계를 대체하지 않습니다. 이는 이미 알고 있지만 아직 들을 수 없었던 것을 알아차리는 공간입니다.",
        "boundaries_eyebrow": "경계",
        "boundaries_h1": "절제는 신뢰 모델의 일부입니다.",
        "boundaries_lede": "SoulMap은 당신의 권위, 치료사, 또는 의지할 수 있는 유일한 장소가 되지 않도록 유용하도록 설계되었습니다.",
        "no_diagnose": "SoulMap은 진단하지 않습니다",
        "no_diagnose_body": "정신건강 상태에 이름을 붙이거나 경험을 임상적 레이블로 바꾸지 않습니다.",
        "no_predict": "SoulMap은 예측하지 않습니다",
        "no_predict_body": "미래를 예측하거나 결과를 약속하거나 상징을 운명으로 바꾸지 않습니다.",
        "no_replace": "SoulMap은 지원을 대신하지 않습니다",
        "no_replace_body": "위험하거나 해를 입을 우려가 있다면 지역 긴급 서비스나 위기 자원에 즉시 도움을 요청하세요.",
        "privacy": "단순성 기반의 프라이버시",
        "privacy_h2": "계정 없음. 대화 폼 없음. 숨겨진 친밀감 없음.",
        "privacy_1": "이 공개 웹사이트는 정보 제공용이며 채팅 인터페이스를 제공하지 않습니다.",
        "privacy_2": "다운로드 링크는 프로젝트의 릴리스 아티팩트를 가리킵니다.",
        "privacy_3": "영적 및 상징적 언어는 탐구의 렌즈로만 제공됩니다.",
        "privacy_4": "인간 관계와 자격 있는 전문가의 지원이 우선입니다.",
        "download_eyebrow": "SoulMap Skills",
        "download_h1": "거울을 지니고 가세요.",
        "download_lede": "릴리스 아티팩트는 이미 사용 중인 AI 도구로 가져오도록 설계되어 있습니다.",
        "skill_package": "Skill 패키지",
        "skill_package_body": "가져오기 가능한 `.skill` 릴리스 패키지",
        "knowledge_archive": "지식 아카이브",
        "knowledge_archive_body": "문서 워크플로를 위한 휴대 가능한 `.zip` 아카이브",
        "open_releases": "릴리스 열기",
        "view_release": "릴리스 파일 보기",
        "before_import": "가져오기 전에",
        "start_artifact": "릴리스 아티팩트로 시작하세요.",
        "artifact_body": "AI 도구용으로 설계된 자체 포함 패키지를 사용한 뒤 릴리스 매니페스트에서 버전 및 SHA-256 정보를 확인하세요.",
        "notes_eyebrow": "메모",
        "notes_h1": "일상에 대한 작은 통찰.",
        "notes_lede": "공개 글은 자기 인식, 관계의 정직성, 현실적인 내면 작업의 세 기둥을 따릅니다.",
        "notes_label_1": "자기 인식",
        "notes_label_2": "관계의 정직성",
        "notes_label_3": "현실적인 내면 작업",
        "note_1": "설명 이전의 감각",
        "note_1_body": "때때로 명료함은 이야기로 손을 뻗기 전에 여기 있는 것의 정확한 감촉을 함께 머무르며 시작됩니다.",
        "note_2": "수리는 사과 그 이상입니다.",
        "note_2_body": "사과는 후회를 말할 수 있지만, 수리는 말한 이후에 무엇이 달라지는지를 묻습니다.",
        "note_3": "확실함이 안도처럼 느껴질 때",
        "note_3_body": "답을 바라는 마음은 듣기를 멈추고 싶은 소망을 품고 있을 수 있습니다. 둘은 항상 같지 않습니다.",
        "notes_callout": "이 글들은 처방이 아니라 초대입니다. 당신의 경험에서 명확해지는 것은 취하고, 나머지는 남겨두세요.",
        "about_eyebrow": "SoulMap AI 소개",
        "about_h1": "단순한 믿음을 중심으로 만들어졌습니다: 반영을 위해 자기 신뢰를 포기해서는 안 됩니다.",
        "about_lede": "SoulMap은 신중한 언어, 분명한 한계, 인간의 소유권을 중심으로 한 개인용 AI 브랜드이자 콘텐츠 우선의 지식 시스템입니다.",
        "posture": "태도",
        "posture_h2": "거울, 안내자가 아닙니다.",
        "posture_p1": "SoulMap은 발생한 일과 당신이 부여하려는 의미 사이의 공간에 관심이 있습니다. 그 공간을 더 정직하게 만들고자 하며, 더 신비롭게 만들려는 것이 아닙니다.",
        "posture_p2": "이 프로젝트는 의도적으로 작게 유지됩니다: 지식 베이스, 얇은 Python 레이어, 사용자와 함께 이동할 수 있는 아티팩트들.",
        "about_callout": "최선의 결과는 SoulMap에 더 의존하는 사용자가 아닙니다. 자신의 앎에 더 단단히 서서 떠나는 사용자입니다.",
        "catalog_eyebrow": "Skill 카탈로그",
        "catalog_h1": "현재 상황에 맞는 레이어를 선택하세요.",
        "catalog_lede": "SoulMap은 상호 보완적인 레이어들입니다. 우선 오케스트레이션을 시작하고, 패턴이 분명해지면 프레임워크를 추가하며, 안전성과 독립성을 유지하세요.",
        "search_query_label": "Skill 카탈로그 검색",
        "search_query_placeholder": "사용 사례, 그룹, 경계 또는 질문으로 Skills 검색…",
        "search_query_hint": "검색은 아래 Skills 목록만 변경합니다; Enter는 이 페이지에 머무릅니다.",
        "ask_query_label": "묻고 싶은 내용을 설명하세요",
        "ask_query_placeholder": "지금의 순간, 질문, 필요로 하는 지원을 설명하세요…",
        "ask_query_hint": "Ask는 기존 공개 시나리오와 일치하는 항목을 찾습니다; 답변을 생성하지 않습니다.",
        "search_panel_title": "Skills 찾아보기",
        "ask_panel_title": "시작할 질문을 선택하세요",
        "ask_results_heading": "일치하는 질문들",
        "ask_browse_label": "모든 Skills 보기",
        "ask_details_label": "Skill 보기",
        "search_mode_label": "모드",
        "search_mode_search": "Skills 검색",
        "search_mode_ask": "Skill로 묻기",
        "search_mode_search_hint": "당신의 말과 일치하는 Skill 레이어를 찾습니다.",
        "search_mode_ask_hint": "공개 Skill 시나리오에서 기초 질문을 찾습니다.",
        "ask_intro": "Ask 모드는 공개 Skill과 시작 질문을 고르는 데 도움을 줍니다. 답을 제공하거나 진단하지 않으며, 텍스트를 어디론가 전송하지 않습니다.",
        "ask_result_label": "시작 질문",
        "ask_use_label": "이 질문 사용",
        "ask_no_results": "해당 질문과 일치하는 공개 Skill 시나리오가 아직 없습니다. 순간을 더 단순한 말로 설명해 보세요.",
        "search_error": "검색을 일시적으로 사용할 수 없습니다. 다시 시도하거나 아래 Skill 그룹을 찾아보세요.",
        "loading": "로딩…",
        "no_results": "이 검색과 일치하는 Skill 그룹이 없습니다.",
        "details": "상세 보기",
        "modal_title": "SoulMap Skill 상세",
        "raw": "원시 Markdown",
        "use_when": "사용 시기",
        "best_for": "적합한 경우",
        "boundary": "경계",
        "close": "닫기",
        "copy_raw": "원시 URL 복사",
        "copied": "복사됨",
        "copy_failed": "복사 실패 — 원시 링크를 사용하세요",
        "open_chatgpt": "ChatGPT에서 열기",
        "open_claude": "Claude에서 열기",
        "open_claude_code": "Claude Code에서 열기",
        "prompt_heading": "상황별 프롬프트 선택",
        "prompt_label": "프롬프트",
        "prompt_intro": "상황에 맞는 하나의 프롬프트를 사용한 뒤 아래의 공개 Skill 번들을 읽으세요.",
        "source_bundle": "원본 Skill 번들",
        "starter_question": "시작 질문",
        "provider_source_instruction": "응답하기 전에 공개 SoulMap Skill 번들을 읽으세요:",
        "provider_starter_prefix": "시작 질문:",
        "skill_not_found": "Skill을 찾을 수 없습니다.",
        "raw_note": "이 URL은 해당 Skill 그룹의 완전한 Markdown 번들을 반환합니다.",
        "not_found": "해당 경로가 없습니다.",
        "not_found_body": "SoulMap은 요청한 공개 페이지를 찾을 수 없습니다.",
        "return_home": "홈으로 돌아가기",
        "faq": "FAQ",
        "privacy_page": "개인정보",
        "home_path_eyebrow": "다음 단계 찾기",
        "home_path_h2": "내면 작업으로 들어가는 명확한 길.",
        "home_path_lede": "지금 필요한 것에 맞는 페이지로 시작하세요. 여기에는 판단을 넘기게 하는 어떤 것도 없습니다.",
        "home_path_1": "태도 이해하기",
        "home_path_1_body": "SoulMap이 어떻게 반영을 하면서도 반영을 권위로 바꾸지 않는지 보세요.",
        "home_path_1_link": "작동 방식",
        "home_path_2": "Skill 레이어 선택",
        "home_path_2_body": "공개 카탈로그를 둘러보고 상황별 프롬프트를 선택하세요.",
        "home_path_2_link": "Skills 살펴보기",
        "home_path_3": "경계 확인하기",
        "home_path_3_body": "시작하기 전에 제한, 프라이버시 태도 및 실용적 답변을 읽으세요.",
        "home_path_3_link": "FAQ 읽기",
        "faq_eyebrow": "자주 묻는 질문",
        "faq_h1": "시작 전에 실용적 답변",
        "faq_lede": "SoulMap이 무엇인지, 공개 Skills가 어떻게 작동하는지, 경계가 어디에 있는지에 대한 짧은 안내.",
        "faq_q_1": "SoulMap AI는 무엇인가요?",
        "faq_a_1": "SoulMap은 당신의 판단, 관계 또는 전문적 지원을 대체하지 않고 패턴을 알아차리도록 돕는 반영적 동반자이자 공개 Skill 라이브러리입니다.",
        "faq_q_2": "SoulMap은 치료사, 의사 또는 위기 서비스인가요?",
        "faq_a_2": "아니요. 진단하거나 예측하지 않으며 응급 처치를 제공하거나 자격 있는 인간 지원을 대체하지 않습니다. 즉시 위험에 처했을 수 있다면 지역 긴급 서비스나 위기 자원에 연락하세요.",
        "faq_q_3": "SoulMap Skills란 무엇인가요?",
        "faq_a_3": "Skills는 SoulMap 프레임워크의 한 레이어를 설명하는 공개 Markdown 번들입니다. 각 카탈로그 항목은 언제 유용한지, 어떤 경우에 적합한지, 그리고 그 경계가 어디인지 설명합니다.",
        "faq_q_4": "AI 도구에서 Skill을 어떻게 사용하나요?",
        "faq_a_4": "상황별 프롬프트를 선택하고 공개 원본 Markdown을 열어, 둘 다 사용 중인 AI 도구에 붙여넣거나 제공합니다. 제공자 링크는 로그인이 필요할 수 있으며 URL을 자동으로 읽지 않을 수 있습니다.",
        "faq_q_5": "이 웹사이트는 개인 데이터를 수집하나요?",
        "faq_a_5": "현재 공개 사이트에는 계정, 채팅 폼, 데이터베이스, 분석, 기억 기능 또는 사용자 제출 콘텐츠 흐름이 없습니다. 현재 공개 사이트의 경계는 개인정보 페이지를 읽어보세요.",
        "faq_q_6": "왜 SoulMap은 신중한 언어를 사용하나요?",
        "faq_a_6": "신중한 언어는 당신의 권한을 보호합니다. SoulMap은 정체성, 미래 또는 내면에 대해 확실성을 제시하기보다 가능성과 질문을 반영하도록 설계되었습니다.",
        "privacy_page_eyebrow": "개인정보",
        "privacy_page_h1": "의도적으로 작은 범위로 지키는 프라이버시.",
        "privacy_page_lede": "이 페이지는 현재 공개된 SoulMap 웹사이트를 설명합니다. 사이트가 무엇을 수집하고 수집하지 않는지에 대해 의도적으로 구체적입니다.",
        "privacy_scope_h2": "이 고지가 적용되는 범위",
        "privacy_scope_body": "이 고지는 공개 웹사이트, 정적 페이지, 공개 Markdown 엔드포인트 및 외부 저장소, 릴리스 및 AI 제공자에 대한 링크를 포함합니다. 사용자가 사이트를 떠난 이후의 타사 제공자는 이 고지에 포함되지 않습니다.",
        "privacy_collect_h2": "사이트가 수집하는 항목",
        "privacy_collect_body": "현재 사이트에는 계정 생성, 채팅 폼, 연락 폼, 업로드 흐름, 데이터베이스, 분석 시스템, 광고 추적기 또는 사용자 프로필이 없습니다. 개인 정보를 제출하도록 의도적으로 요구하지 않습니다.",
        "privacy_use_h2": "사이트가 정보를 사용하는 방식",
        "privacy_use_body": "공개 사이트는 개인 데이터 제출 흐름을 제공하지 않기 때문에 SoulMap은 제출된 개인 콘텐츠를 프로파일링, 개인화 또는 기억에 사용하지 않습니다. 브라우저는 여전히 웹사이트나 외부 링크를 불러오는 데 필요한 일반적인 기술 요청을 보낼 수 있습니다.",
        "privacy_storage_h2": "저장, 쿠키 및 제3자",
        "privacy_storage_body": "저장소는 의도적으로 비필수 쿠키를 설정하거나 분석을 운영하지 않습니다. CDN 자산, GitHub Pages, 릴리스 호스팅 및 링크된 AI 제공자는 자체 정책과 로그를 가진 별도 서비스입니다.",
        "privacy_links_h2": "외부 링크 열기",
        "privacy_links_body": "GitHub, 릴리스 자산, ChatGPT, Claude 또는 다른 외부 제공자를 열면 해당 서비스가 이후 상황을 제어합니다. 민감한 내용을 공유하기 전에 해당 서비스의 개인정보 및 데이터 처리 정책을 검토하세요.",
        "privacy_contact_h2": "변경 및 연락 범위",
        "privacy_contact_body": "사이트가 이후 계정, 폼, 분석, 저장 또는 다른 데이터 처리 기능을 추가하는 경우, 해당 기능이 공개 제품의 일부로 간주되기 전에 이 고지를 검토하고 업데이트해야 합니다.",
        "privacy_updated": "최종 검토: 2026년 8월.",
    },
}

SUPPORTED_LOCALES: Final[tuple[str, ...]] = ("en", "vi", "ko")


def messages_for(locale: str) -> dict[str, str]:
    """Return the requested locale with English fallback for future additions."""
    return LOCALES.get(locale, LOCALES["en"])


def messages_json(locale: str) -> str:
    """Serialize localized copy for an inert JSON DOM payload."""
    payload = json.dumps(
        messages_for(locale), ensure_ascii=False, separators=(",", ":")
    )
    return payload.replace("<", "\u003c").replace(">", "\u003e").replace("&", "\u0026")
