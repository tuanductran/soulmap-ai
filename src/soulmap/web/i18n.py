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
        "catalog_count": "{count} groups · raw bundles available",
        "search_label": "Find a Skill or question",
        "search_query_label": "Search the Skill catalog",
        "search_query_placeholder": "Search Skills by use case, group, boundary, or question…",
        "search_query_hint": "Search only changes the Skill list below; Enter stays on this page.",
        "ask_query_label": "Describe what you want to ask",
        "ask_query_placeholder": "Describe the moment, question, or support you need…",
        "ask_query_hint": "Ask matches existing public scenarios; it does not generate an answer.",
        "search_panel_title": "Browse Skills",
        "search_panel_lede": "Find the layer that matches your words, then open its details or raw bundle.",
        "ask_panel_title": "Choose a question to begin",
        "ask_panel_lede": "Choose an existing Skill scenario as a grounded starting point. Your text stays on this page.",
        "ask_results_heading": "Matching questions",
        "ask_browse_label": "Browse all Skills",
        "ask_details_label": "View Skill",
        "search_hint": "Choose Search or Ask; results update as you type and Enter stays on this page.",
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
        "raw_heading": "Public raw bundle",
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
        "catalog_count": "{count} nhóm · có bundle Markdown gốc",
        "search_label": "Tìm Skill hoặc câu hỏi",
        "search_query_label": "Tìm trong danh mục Skills",
        "search_query_placeholder": "Tìm Skills theo trường hợp sử dụng, nhóm, ranh giới hoặc câu hỏi…",
        "search_query_hint": "Tìm kiếm chỉ thay đổi danh sách Skills bên dưới; Enter vẫn ở trang này.",
        "ask_query_label": "Mô tả điều bạn muốn hỏi",
        "ask_query_placeholder": "Mô tả khoảnh khắc, câu hỏi hoặc kiểu hỗ trợ bạn cần…",
        "ask_query_hint": "Hỏi chỉ khớp với các kịch bản công khai; không tự tạo câu trả lời.",
        "search_panel_title": "Khám phá Skills",
        "search_panel_lede": "Tìm lớp phù hợp với điều bạn viết, rồi mở chi tiết hoặc bundle gốc.",
        "ask_panel_title": "Chọn một câu hỏi để bắt đầu",
        "ask_panel_lede": "Chọn một kịch bản Skill có sẵn làm điểm bắt đầu có nền tảng. Nội dung của bạn ở lại trên trang này.",
        "ask_results_heading": "Các câu hỏi phù hợp",
        "ask_browse_label": "Xem tất cả Skills",
        "ask_details_label": "Xem Skill",
        "search_hint": "Chọn Tìm kiếm hoặc Hỏi; kết quả cập nhật khi nhập và Enter vẫn ở trang này.",
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
        "raw_heading": "Gói Markdown công khai",
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
}

SUPPORTED_LOCALES: Final[tuple[str, ...]] = ("en", "vi")


def messages_for(locale: str) -> dict[str, str]:
    """Return the requested locale with English fallback for future additions."""
    return LOCALES.get(locale, LOCALES["en"])


def messages_json(locale: str) -> str:
    """Serialize localized copy for an inert JSON DOM payload."""
    payload = json.dumps(
        messages_for(locale), ensure_ascii=False, separators=(",", ":")
    )
    return payload.replace("<", "\u003c").replace(">", "\u003e").replace("&", "\u0026")
