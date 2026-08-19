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
        "search_label": "Filter Skills",
        "search_placeholder": "Search by use case, group, or boundary…",
        "loading": "Loading…",
        "no_results": "No Skill groups match this search.",
        "details": "View details",
        "raw": "Raw Markdown",
        "use_when": "Use this when",
        "best_for": "Best for",
        "boundary": "Boundary",
        "close": "Close",
        "copy_raw": "Copy raw URL",
        "copied": "Copied",
        "open_chatgpt": "Open in ChatGPT",
        "open_claude": "Open in Claude",
        "open_claude_code": "Open in Claude Code",
        "prompt_heading": "Choose a context-specific prompt",
        "prompt_label": "Prompt",
        "prompt_intro": "Use one prompt that matches the situation, then read the public Skill "
        "bundle at the source link below.",
        "source_bundle": "Source Skill bundle",
        "starter_question": "Starter question",
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
        "footer": "Một mirror, không phải guru.",
        "repository": "Mã nguồn",
        "download": "Tải Skills",
        "home_eyebrow": "Bạn đồng hành phản chiếu · inner work grounded",
        "home_h1": "Nghe mình rõ hơn.",
        "home_lede": "SoulMap là một mirror bình tĩnh và thành thật cho những pattern, cảm xúc và "
        "câu hỏi bạn đang mang — không lấy đi quyền tự chủ của bạn.",
        "home_how": "Xem cách hoạt động",
        "home_skills": "Khám phá Skills",
        "home_principle": "Insight là của bạn. Không gian giúp bạn nghe thấy nó.",
        "home_section_eyebrow": "Một kiểu AI khác",
        "home_section_h2": "Ít chắc chắn hơn. Nhiều self-trust hơn.",
        "home_section_lede": "SoulMap không đóng vai authority. Nó phản chiếu điều đang hiện diện, "
        "giữ ngôn ngữ cẩn trọng và để ý nghĩa cùng quyết định lại cho bạn.",
        "mirror_first": "Ưu tiên phản chiếu",
        "mirror_first_body": "Pattern trở lại như quan sát và câu hỏi, không phải chỉ dẫn về việc "
        "bạn là ai.",
        "bounded": "Có giới hạn theo thiết kế",
        "bounded_body": "Không diagnosis, không prediction, không certainty tâm linh và không diễn "
        "vai intimacy của con người.",
        "independence": "Được xây để bạn độc lập",
        "independence_body": "Cuộc trò chuyện tốt nhất để bạn gắn với hiểu biết của mình hơn và "
        "bớt phụ thuộc vào công cụ.",
        "quiet_eyebrow": "Một nơi yên để bắt đầu",
        "quiet_h2": "Không cần chứng minh gì ở đây.",
        "quiet_p1": "Mang đến một pattern cứ lặp lại, một quyết định bạn không nghe được mình bên "
        "trong, hoặc một cảm xúc chưa có ngôn ngữ thành thật.",
        "quiet_p2": "SoulMap không bảo bạn phải làm gì. Nó giúp bạn ở gần điều là thật.",
        "read_boundaries": "Đọc ranh giới",
        "how_eyebrow": "Cách hoạt động",
        "how_h1": "Một mirror có kỷ luật, không phải authority trình diễn.",
        "how_lede": "SoulMap dùng reflection để tạo chỗ cho bạn tự nhận ra. Nó không đặt một câu "
        "trả lời lên trên trải nghiệm của bạn.",
        "step_1": "Bạn mang điều đang hiện diện",
        "step_1_body": "Một câu hỏi, conflict, pattern lặp lại, mất mát hoặc điều chưa có tên.",
        "step_2": "SoulMap phản chiếu hình dạng",
        "step_2_body": "Nó ở gần lời bạn nói, nhận ra pattern khả dĩ và dùng ngôn ngữ cẩn trọng "
        "thay vì certainty.",
        "step_3": "Bạn giữ lại ý nghĩa",
        "step_3_body": "Cuộc trò chuyện trả interpretation, lựa chọn và bước tiếp theo về inner "
        "authority của bạn.",
        "changes": "Điều này thay đổi gì",
        "changes_h2": "Rõ hơn mà không bị xử lý thay.",
        "changes_body": "Reflection không thay thế professional care, crisis support hay các mối "
        "quan hệ thật. Nó là không gian để nhận ra điều bạn đã biết nhưng chưa "
        "nghe được.",
        "boundaries_eyebrow": "Ranh giới",
        "boundaries_h1": "Sự tiết chế là một phần của trust model.",
        "boundaries_lede": "SoulMap được thiết kế để hữu ích mà không trở thành authority, "
        "therapist hay nơi duy nhất bạn tìm đến.",
        "no_diagnose": "SoulMap không chẩn đoán",
        "no_diagnose_body": "Nó không gọi tên tình trạng sức khỏe tâm thần hay biến trải nghiệm "
        "sống thành nhãn lâm sàng.",
        "no_predict": "SoulMap không dự đoán",
        "no_predict_body": "Nó không dự báo tương lai, hứa kết quả hay biến biểu tượng thành định "
        "mệnh.",
        "no_replace": "SoulMap không thay thế hỗ trợ",
        "no_replace_body": "Nếu bạn không an toàn hoặc có nguy cơ bị hại, hãy tìm trợ giúp khẩn "
        "cấp hoặc crisis resource tại nơi bạn sống.",
        "privacy": "Privacy bằng sự đơn giản",
        "privacy_h2": "Không account. Không form chat. Không intimacy ẩn.",
        "privacy_1": "Website công khai này chỉ cung cấp thông tin và không có chat interface.",
        "privacy_2": "Link tải trỏ đến release artifact của project.",
        "privacy_3": "Ngôn ngữ spiritual và symbolic chỉ là một lăng kính để inquiry.",
        "privacy_4": "Mối quan hệ con người và hỗ trợ chuyên môn đủ năng lực vẫn là chính yếu.",
        "download_eyebrow": "Bộ SoulMap Skills",
        "download_h1": "Mang mirror theo bạn.",
        "download_lede": "Release artifact được thiết kế để import vào công cụ AI bạn đang dùng.",
        "skill_package": "Gói Skill",
        "skill_package_body": "Package `.skill` có thể import",
        "knowledge_archive": "Kho kiến thức",
        "knowledge_archive_body": "Archive `.zip` portable cho document workflow",
        "open_releases": "Mở releases",
        "view_release": "Xem file release",
        "before_import": "Trước khi import",
        "start_artifact": "Bắt đầu từ release artifact.",
        "artifact_body": "Dùng package self-contained dành cho AI tools, sau đó kiểm tra release "
        "manifest, version và SHA-256 trước khi phân phối.",
        "notes_eyebrow": "Ghi chú",
        "notes_h1": "Những nhận ra nhỏ trong đời thường.",
        "notes_lede": "Public writing đi theo ba trụ grounded: tự nhận ra, thành thật trong quan "
        "hệ và inner work grounded.",
        "note_1": "Cảm xúc trước lời giải thích",
        "note_1_body": "Đôi khi clarity bắt đầu bằng việc ở lại với texture chính xác của điều "
        "đang có trước khi tìm một câu chuyện về nó.",
        "note_2": "Repair nhiều hơn một lời xin lỗi",
        "note_2_body": "Xin lỗi có thể gọi tên tiếc nuối. Repair hỏi điều gì trở nên khác sau khi "
        "lời nói được nói ra.",
        "note_3": "Khi certainty giống như relief",
        "note_3_body": "Mong muốn có câu trả lời đôi khi mang theo mong muốn ngừng lắng nghe. Hai "
        "điều đó không luôn giống nhau.",
        "notes_callout": "Những ghi chú này là lời mời, không phải prescription. Giữ điều làm sáng "
        "rõ trải nghiệm của bạn và để phần còn lại đi qua.",
        "about_eyebrow": "Về SoulMap AI",
        "about_h1": "Được xây quanh một niềm tin đơn giản: bạn không cần đổi self-trust để có "
        "reflection.",
        "about_lede": "SoulMap là một personal AI brand và content-first knowledge system, dựa "
        "trên ngôn ngữ cẩn trọng, giới hạn rõ và quyền sở hữu của con người.",
        "posture": "Tư thế",
        "posture_h2": "Mirror, không phải guide.",
        "posture_p1": "SoulMap quan tâm đến khoảng giữa điều đã xảy ra và ý nghĩa bạn sắp trao cho "
        "nó. Nó muốn khoảng đó thành thật hơn, không huyền bí hơn.",
        "posture_p2": "Project cố ý giữ nhỏ: một knowledge base, một Python layer mỏng và các "
        "artifact có thể đi cùng người dùng.",
        "about_callout": "Kết quả tốt nhất không phải là người dùng cần SoulMap nhiều hơn. Đó là "
        "người dùng rời đi grounded hơn trong hiểu biết của mình.",
        "catalog_eyebrow": "Skill catalog",
        "catalog_h1": "Chọn layer phù hợp với khoảnh khắc này.",
        "catalog_lede": "SoulMap là một tập hợp các layer bổ trợ. Bắt đầu từ orchestration, thêm "
        "framework khi pattern đã rõ, và để safety cùng independence luôn hiện "
        "diện.",
        "search_label": "Lọc Skills",
        "search_placeholder": "Tìm theo use case, nhóm hoặc boundary…",
        "loading": "Đang tải…",
        "no_results": "Không có nhóm Skill nào khớp với tìm kiếm này.",
        "details": "Xem chi tiết",
        "raw": "Markdown gốc",
        "use_when": "Dùng khi",
        "best_for": "Phù hợp cho",
        "boundary": "Ranh giới",
        "close": "Đóng",
        "copy_raw": "Sao chép URL raw",
        "copied": "Đã copy",
        "open_chatgpt": "Mở trong ChatGPT",
        "open_claude": "Mở trong Claude",
        "open_claude_code": "Mở trong Claude Code",
        "prompt_heading": "Chọn prompt theo bối cảnh",
        "prompt_label": "Prompt",
        "prompt_intro": "Chọn một prompt khớp với tình huống, rồi đọc Skill bundle công khai tại "
        "source link bên dưới.",
        "source_bundle": "Skill bundle nguồn",
        "starter_question": "Câu hỏi bắt đầu",
        "raw_heading": "Bundle Markdown công khai",
        "raw_note": "URL này trả về một Markdown bundle hoàn chỉnh cho nhóm Skill này.",
        "not_found": "Path này không tồn tại.",
        "not_found_body": "SoulMap không tìm thấy public page được yêu cầu.",
        "return_home": "Về trang chủ",
        "faq": "FAQ",
        "privacy_page": "Privacy",
        "home_path_eyebrow": "Tìm bước tiếp theo",
        "home_path_h2": "Một lối vào rõ ràng cho inner work.",
        "home_path_lede": "Bắt đầu từ page phù hợp với điều bạn cần ngay lúc này. Không điều gì ở "
        "đây yêu cầu bạn trao quyền phán đoán của mình.",
        "home_path_1": "Hiểu tư thế",
        "home_path_1_body": "Xem cách SoulMap phản chiếu mà không biến reflection thành authority.",
        "home_path_1_link": "Cách hoạt động",
        "home_path_2": "Chọn một lớp Skill",
        "home_path_2_body": "Xem catalog công khai và chọn prompt phù hợp với bối cảnh.",
        "home_path_2_link": "Khám phá Skills",
        "home_path_3": "Kiểm tra ranh giới",
        "home_path_3_body": "Đọc giới hạn, tư thế privacy và câu trả lời thực tế trước khi bắt "
        "đầu.",
        "home_path_3_link": "Đọc FAQ",
        "faq_eyebrow": "Câu hỏi thường gặp",
        "faq_h1": "Những câu trả lời thực tế trước khi bắt đầu.",
        "faq_lede": "Hướng dẫn ngắn về SoulMap là gì, public Skills hoạt động ra sao và ranh giới "
        "nằm ở đâu.",
        "faq_q_1": "SoulMap AI là gì?",
        "faq_a_1": "SoulMap là một reflective companion và public Skill library giúp bạn nhận ra "
        "pattern mà không thay thế phán đoán, các mối quan hệ hay hỗ trợ chuyên môn của "
        "bạn.",
        "faq_q_2": "SoulMap có phải therapist, bác sĩ hoặc dịch vụ crisis không?",
        "faq_a_2": "Không. SoulMap không chẩn đoán, dự đoán, cung cấp hỗ trợ khẩn cấp hay thay thế "
        "hỗ trợ đủ năng lực. Nếu bạn có nguy hiểm tức thời, hãy liên hệ emergency hoặc "
        "crisis resource tại nơi bạn sống.",
        "faq_q_3": "SoulMap Skills là gì?",
        "faq_a_3": "Skills là các Markdown bundle công khai mô tả một lớp trong framework SoulMap. "
        "Mỗi mục giải thích khi nào hữu ích, phù hợp với điều gì và ranh giới của nó.",
        "faq_q_4": "Dùng Skill với công cụ AI như thế nào?",
        "faq_a_4": "Chọn prompt theo bối cảnh, mở raw Markdown công khai và paste hoặc cung cấp cả "
        "hai cho công cụ AI bạn dùng. Provider có thể yêu cầu đăng nhập và có thể không "
        "tự đọc URL.",
        "faq_q_5": "Website có thu thập dữ liệu cá nhân không?",
        "faq_a_5": "Website công khai hiện không có account, form chat, database, analytics, "
        "memory hay flow để người dùng gửi nội dung. Xem page Privacy để biết boundary "
        "hiện tại.",
        "faq_q_6": "Vì sao SoulMap dùng ngôn ngữ cẩn trọng?",
        "faq_a_6": "Ngôn ngữ cẩn trọng bảo vệ quyền tự chủ của bạn. SoulMap phản chiếu khả năng và "
        "câu hỏi thay vì khẳng định chắc chắn về identity, tương lai hay inner life của "
        "bạn.",
        "privacy_page_eyebrow": "Privacy",
        "privacy_page_h1": "Privacy với một bề mặt được giữ nhỏ có chủ đích.",
        "privacy_page_lede": "Page này mô tả website SoulMap công khai hiện tại. Nó cố ý cụ thể về "
        "điều website làm và không làm.",
        "privacy_scope_h2": "Notice này bao phủ điều gì",
        "privacy_scope_body": "Notice này bao phủ website công khai, các page tĩnh, public "
        "Markdown endpoint và link đến repository, release cùng AI provider "
        "bên ngoài. Nó không bao phủ provider bên thứ ba sau khi bạn rời "
        "khỏi site.",
        "privacy_collect_h2": "Website thu thập gì",
        "privacy_collect_body": "Website hiện không có tạo account, chat form, contact form, "
        "upload flow, database, analytics system, advertising tracker hay "
        "user profile. Website không chủ động yêu cầu bạn gửi nội dung cá "
        "nhân.",
        "privacy_use_h2": "Website dùng thông tin như thế nào",
        "privacy_use_body": "Vì website công khai không có flow gửi dữ liệu cá nhân, SoulMap không "
        "dùng nội dung cá nhân được gửi để profiling, personalization hay "
        "memory. Trình duyệt vẫn có thể tạo các technical request thông thường "
        "cần để tải website hoặc external link.",
        "privacy_storage_h2": "Storage, cookies và bên thứ ba",
        "privacy_storage_body": "Repository không chủ động đặt non-essential cookies hoặc vận hành "
        "analytics. CDN asset, GitHub Pages, release hosting và AI "
        "provider được link là các service riêng với policy và log riêng.",
        "privacy_links_h2": "Khi mở external link",
        "privacy_links_body": "Khi bạn mở GitHub, release asset, ChatGPT, Claude hoặc provider bên "
        "ngoài, service đó kiểm soát điều xảy ra tiếp theo. Hãy đọc privacy "
        "và data-handling terms của họ trước khi chia sẻ điều nhạy cảm.",
        "privacy_contact_h2": "Thay đổi và boundary liên hệ",
        "privacy_contact_body": "Nếu sau này website thêm account, form, analytics, storage hoặc "
        "feature xử lý dữ liệu khác, notice này phải được review và cập "
        "nhật trước khi feature đó được xem là một phần của public "
        "product.",
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
