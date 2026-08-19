"""A small, dependency-free responsive website for SoulMap AI.

The website is separate from the shipped knowledge artifacts at runtime, while the
public catalog exposes curated Skill bundles through explicit raw endpoints.
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections.abc import Callable
from html import escape
from pathlib import Path
from urllib.parse import parse_qs, quote
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server
from wsgiref.types import StartResponse

from soulmap.web.catalog import (
    CATALOG,
    catalog_json,
    get_skill,
    locale_fields,
    raw_markdown,
)

HOST = "127.0.0.1"
PORT = 8765
SITE_NAME = "SoulMap AI"
RELEASE_URL = "https://github.com/tuanductran/soulmap-ai/releases/latest"
REPOSITORY_URL = "https://github.com/tuanductran/soulmap-ai"
PUBLIC_SITE_URL = "https://tuanductran.github.io/soulmap-ai"
HTMX_URL = "https://cdn.jsdelivr.net/npm/htmx.org@2.0.10/dist/htmx.min.js"
ALPINE_URL = "https://cdn.jsdelivr.net/npm/@alpinejs/csp@3.16.2/dist/cdn.min.js"
HTMX_SRI = "sha384-H5SrcfygHmAuTDZphMHqBJLc3FhssKjG7w/CeCpFReSfwBWDTKpkzPP8c+cLsK+V"
ALPINE_SRI = "sha384-V/6+qWbzTJSzEweFWozPRF8In+k5cIL398rKMOn3YTJwFQAubV91vSnII3clycgX"

TEXT: dict[str, dict[str, str]] = {
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
        "home_lede": "SoulMap is a calm, honest mirror for the patterns, feelings, and questions you are already carrying — without handing your authority away.",
        "home_how": "See how it works",
        "home_skills": "Explore the Skills",
        "home_principle": "The insight is yours. The space helps you hear it.",
        "home_section_eyebrow": "A different kind of AI",
        "home_section_h2": "Less certainty. More self-trust.",
        "home_section_lede": "SoulMap does not perform authority. It reflects what is present, keeps language careful, and leaves the meaning and decision with you.",
        "mirror_first": "Mirror-first",
        "mirror_first_body": "Patterns come back as observations and questions, not instructions about who you are.",
        "bounded": "Bounded by design",
        "bounded_body": "No diagnosis, no prediction, no spiritual certainty, and no performance of human intimacy.",
        "independence": "Built for independence",
        "independence_body": "The best conversation leaves you more connected to your own knowing and less attached to the tool.",
        "quiet_eyebrow": "A quiet place to begin",
        "quiet_h2": "Nothing to prove here.",
        "quiet_p1": "Bring a pattern you keep repeating, a decision you cannot hear yourself inside, or a feeling that has not found honest language yet.",
        "quiet_p2": "SoulMap will not tell you what to do. It will help you stay close to what is real.",
        "read_boundaries": "Read the boundaries",
        "how_eyebrow": "How it works",
        "how_h1": "A disciplined mirror, not a performing authority.",
        "how_lede": "SoulMap uses reflection to make room for your own recognition. It does not install an answer on top of your experience.",
        "step_1": "You bring what is present",
        "step_1_body": "A question, a conflict, a repeating pattern, a loss, or something that does not yet have a name.",
        "step_2": "SoulMap reflects the shape",
        "step_2_body": "It stays close to your words, notices possible patterns, and uses careful language rather than certainty.",
        "step_3": "You keep the meaning",
        "step_3_body": "The conversation returns interpretation, choice, and next movement to your own inner authority.",
        "changes": "What this changes",
        "changes_h2": "Clarity without being handled.",
        "changes_body": "Reflection is not a replacement for professional care, crisis support, or real-world relationships. It is a space for noticing what you already know and may not yet be able to hear.",
        "boundaries_eyebrow": "Boundaries",
        "boundaries_h1": "Restraint is part of the trust model.",
        "boundaries_lede": "SoulMap is designed to be useful without becoming your authority, your therapist, or your only place to turn.",
        "no_diagnose": "SoulMap does not diagnose",
        "no_diagnose_body": "It does not name mental health conditions or turn a lived experience into a clinical label.",
        "no_predict": "SoulMap does not predict",
        "no_predict_body": "It does not forecast your future, promise outcomes, or turn symbolism into destiny.",
        "no_replace": "SoulMap does not replace support",
        "no_replace_body": "If you are unsafe or at risk of harm, seek immediate help from local emergency or crisis resources.",
        "privacy": "Privacy by simplicity",
        "privacy_h2": "No account. No conversation form. No hidden intimacy.",
        "privacy_1": "This public website is informational and does not provide a chat interface.",
        "privacy_2": "Download links point to the project's release artifacts.",
        "privacy_3": "Spiritual and symbolic language is offered only as a lens for inquiry.",
        "privacy_4": "Human relationships and qualified professional support remain primary.",
        "download_eyebrow": "SoulMap Skills",
        "download_h1": "Take the mirror with you.",
        "download_lede": "The release artifacts are designed to be imported into the AI tool you already use.",
        "skill_package": "Skill package",
        "skill_package_body": "Importable `.skill` release package",
        "knowledge_archive": "Knowledge archive",
        "knowledge_archive_body": "Portable `.zip` archive for document workflows",
        "open_releases": "Open releases",
        "view_release": "View release files",
        "before_import": "Before importing",
        "start_artifact": "Start with the release artifact.",
        "artifact_body": "Use the self-contained package intended for AI tools, then check the release manifest for version and SHA-256 information.",
        "notes_eyebrow": "Notes",
        "notes_h1": "Small recognitions for ordinary life.",
        "notes_lede": "Public writing follows three grounded pillars: self-recognition, relational honesty, and grounded inner work.",
        "note_1": "The feeling before the explanation",
        "note_1_body": "Sometimes clarity begins by staying with the exact texture of what is here before reaching for a story about it.",
        "note_2": "Repair is more than apology",
        "note_2_body": "An apology can name regret. Repair asks what becomes different after the words have been spoken.",
        "note_3": "When certainty feels like relief",
        "note_3_body": "The wish for an answer may be carrying a wish to stop listening. The two are not always the same.",
        "notes_callout": "These notes are invitations, not prescriptions. Keep what clarifies something in your own experience and leave the rest.",
        "about_eyebrow": "About SoulMap AI",
        "about_h1": "Built around a simple belief: you should not have to trade self-trust for reflection.",
        "about_lede": "SoulMap is a personal AI brand and a content-first knowledge system built around careful language, clear limits, and human ownership.",
        "posture": "The posture",
        "posture_h2": "Mirror, not guide.",
        "posture_p1": "SoulMap is interested in the space between what happened and the meaning you are about to give it. It aims to make that space more honest, not more mystical.",
        "posture_p2": "The project stays deliberately small: a knowledge base, a thin Python layer, and artifacts that can travel with the user.",
        "about_callout": "The best outcome is not a user who needs SoulMap more. It is a user who leaves more grounded in their own knowing.",
        "catalog_eyebrow": "The Skill catalog",
        "catalog_h1": "Choose the layer that fits the moment.",
        "catalog_lede": "SoulMap is a set of complementary layers. Start with orchestration, add a framework when the pattern is clear, and let safety and independence stay in the room.",
        "search_label": "Filter Skills",
        "search_placeholder": "Search by use case, group, or boundary…",
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
        "handoff_note": "Provider links may require sign-in. When a provider does not support prefilled prompts, use the raw Markdown URL.",
        "raw_heading": "Public raw bundle",
        "raw_note": "This URL returns one complete Markdown bundle for this Skill group.",
        "not_found": "That path is not here.",
        "not_found_body": "SoulMap could not find the requested public page.",
        "return_home": "Return home",
    },
    "vi": {
        "skip": "Bỏ qua đến nội dung",
        "home": "Trang chủ",
        "how": "Cách hoạt động",
        "boundaries": "Ranh giới",
        "notes": "Ghi chú",
        "about": "Giới thiệu",
        "skills": "Skills",
        "language": "Ngôn ngữ",
        "footer": "Một mirror, không phải guru.",
        "repository": "Repository",
        "download": "Tải Skills",
        "home_eyebrow": "Bạn đồng hành phản chiếu · inner work grounded",
        "home_h1": "Nghe mình rõ hơn.",
        "home_lede": "SoulMap là một mirror bình tĩnh và thành thật cho những pattern, cảm xúc và câu hỏi bạn đang mang — không lấy đi quyền tự chủ của bạn.",
        "home_how": "Xem cách hoạt động",
        "home_skills": "Khám phá Skills",
        "home_principle": "Insight là của bạn. Không gian giúp bạn nghe thấy nó.",
        "home_section_eyebrow": "Một kiểu AI khác",
        "home_section_h2": "Ít chắc chắn hơn. Nhiều self-trust hơn.",
        "home_section_lede": "SoulMap không đóng vai authority. Nó phản chiếu điều đang hiện diện, giữ ngôn ngữ cẩn trọng và để ý nghĩa cùng quyết định lại cho bạn.",
        "mirror_first": "Mirror-first",
        "mirror_first_body": "Pattern trở lại như quan sát và câu hỏi, không phải chỉ dẫn về việc bạn là ai.",
        "bounded": "Bounded by design",
        "bounded_body": "Không diagnosis, không prediction, không certainty tâm linh và không diễn vai intimacy của con người.",
        "independence": "Được xây để bạn độc lập",
        "independence_body": "Cuộc trò chuyện tốt nhất để bạn gắn với hiểu biết của mình hơn và bớt phụ thuộc vào công cụ.",
        "quiet_eyebrow": "Một nơi yên để bắt đầu",
        "quiet_h2": "Không cần chứng minh gì ở đây.",
        "quiet_p1": "Mang đến một pattern cứ lặp lại, một quyết định bạn không nghe được mình bên trong, hoặc một cảm xúc chưa có ngôn ngữ thành thật.",
        "quiet_p2": "SoulMap không bảo bạn phải làm gì. Nó giúp bạn ở gần điều là thật.",
        "read_boundaries": "Đọc ranh giới",
        "how_eyebrow": "Cách hoạt động",
        "how_h1": "Một mirror có kỷ luật, không phải authority trình diễn.",
        "how_lede": "SoulMap dùng reflection để tạo chỗ cho bạn tự nhận ra. Nó không đặt một câu trả lời lên trên trải nghiệm của bạn.",
        "step_1": "Bạn mang điều đang hiện diện",
        "step_1_body": "Một câu hỏi, conflict, pattern lặp lại, mất mát hoặc điều chưa có tên.",
        "step_2": "SoulMap phản chiếu hình dạng",
        "step_2_body": "Nó ở gần lời bạn nói, nhận ra pattern khả dĩ và dùng ngôn ngữ cẩn trọng thay vì certainty.",
        "step_3": "Bạn giữ lại ý nghĩa",
        "step_3_body": "Cuộc trò chuyện trả interpretation, lựa chọn và bước tiếp theo về inner authority của bạn.",
        "changes": "Điều này thay đổi gì",
        "changes_h2": "Rõ hơn mà không bị xử lý thay.",
        "changes_body": "Reflection không thay thế professional care, crisis support hay các mối quan hệ thật. Nó là không gian để nhận ra điều bạn đã biết nhưng chưa nghe được.",
        "boundaries_eyebrow": "Ranh giới",
        "boundaries_h1": "Sự tiết chế là một phần của trust model.",
        "boundaries_lede": "SoulMap được thiết kế để hữu ích mà không trở thành authority, therapist hay nơi duy nhất bạn tìm đến.",
        "no_diagnose": "SoulMap không chẩn đoán",
        "no_diagnose_body": "Nó không gọi tên tình trạng sức khỏe tâm thần hay biến trải nghiệm sống thành nhãn lâm sàng.",
        "no_predict": "SoulMap không dự đoán",
        "no_predict_body": "Nó không dự báo tương lai, hứa kết quả hay biến biểu tượng thành định mệnh.",
        "no_replace": "SoulMap không thay thế hỗ trợ",
        "no_replace_body": "Nếu bạn không an toàn hoặc có nguy cơ bị hại, hãy tìm trợ giúp khẩn cấp hoặc crisis resource tại nơi bạn sống.",
        "privacy": "Privacy bằng sự đơn giản",
        "privacy_h2": "Không account. Không form chat. Không intimacy ẩn.",
        "privacy_1": "Website công khai này chỉ cung cấp thông tin và không có chat interface.",
        "privacy_2": "Link tải trỏ đến release artifact của project.",
        "privacy_3": "Ngôn ngữ spiritual và symbolic chỉ là một lăng kính để inquiry.",
        "privacy_4": "Mối quan hệ con người và hỗ trợ chuyên môn đủ năng lực vẫn là chính yếu.",
        "download_eyebrow": "SoulMap Skills",
        "download_h1": "Mang mirror theo bạn.",
        "download_lede": "Release artifact được thiết kế để import vào công cụ AI bạn đang dùng.",
        "skill_package": "Skill package",
        "skill_package_body": "Package `.skill` có thể import",
        "knowledge_archive": "Knowledge archive",
        "knowledge_archive_body": "Archive `.zip` portable cho document workflow",
        "open_releases": "Mở releases",
        "view_release": "Xem file release",
        "before_import": "Trước khi import",
        "start_artifact": "Bắt đầu từ release artifact.",
        "artifact_body": "Dùng package self-contained dành cho AI tools, sau đó kiểm tra release manifest, version và SHA-256 trước khi phân phối.",
        "notes_eyebrow": "Ghi chú",
        "notes_h1": "Những nhận ra nhỏ trong đời thường.",
        "notes_lede": "Public writing đi theo ba trụ grounded: tự nhận ra, thành thật trong quan hệ và inner work grounded.",
        "note_1": "Cảm xúc trước lời giải thích",
        "note_1_body": "Đôi khi clarity bắt đầu bằng việc ở lại với texture chính xác của điều đang có trước khi tìm một câu chuyện về nó.",
        "note_2": "Repair nhiều hơn một lời xin lỗi",
        "note_2_body": "Xin lỗi có thể gọi tên tiếc nuối. Repair hỏi điều gì trở nên khác sau khi lời nói được nói ra.",
        "note_3": "Khi certainty giống như relief",
        "note_3_body": "Mong muốn có câu trả lời đôi khi mang theo mong muốn ngừng lắng nghe. Hai điều đó không luôn giống nhau.",
        "notes_callout": "Những ghi chú này là lời mời, không phải prescription. Giữ điều làm sáng rõ trải nghiệm của bạn và để phần còn lại đi qua.",
        "about_eyebrow": "Về SoulMap AI",
        "about_h1": "Được xây quanh một niềm tin đơn giản: bạn không cần đổi self-trust để có reflection.",
        "about_lede": "SoulMap là một personal AI brand và content-first knowledge system, dựa trên ngôn ngữ cẩn trọng, giới hạn rõ và quyền sở hữu của con người.",
        "posture": "Tư thế",
        "posture_h2": "Mirror, không phải guide.",
        "posture_p1": "SoulMap quan tâm đến khoảng giữa điều đã xảy ra và ý nghĩa bạn sắp trao cho nó. Nó muốn khoảng đó thành thật hơn, không huyền bí hơn.",
        "posture_p2": "Project cố ý giữ nhỏ: một knowledge base, một Python layer mỏng và các artifact có thể đi cùng người dùng.",
        "about_callout": "Kết quả tốt nhất không phải là người dùng cần SoulMap nhiều hơn. Đó là người dùng rời đi grounded hơn trong hiểu biết của mình.",
        "catalog_eyebrow": "Skill catalog",
        "catalog_h1": "Chọn layer phù hợp với khoảnh khắc này.",
        "catalog_lede": "SoulMap là một tập hợp các layer bổ trợ. Bắt đầu từ orchestration, thêm framework khi pattern đã rõ, và để safety cùng independence luôn hiện diện.",
        "search_label": "Lọc Skills",
        "search_placeholder": "Tìm theo use case, nhóm hoặc boundary…",
        "details": "Xem chi tiết",
        "raw": "Raw Markdown",
        "use_when": "Dùng khi",
        "best_for": "Phù hợp cho",
        "boundary": "Boundary",
        "close": "Đóng",
        "copy_raw": "Copy raw URL",
        "copied": "Đã copy",
        "open_chatgpt": "Mở trong ChatGPT",
        "open_claude": "Mở trong Claude",
        "open_claude_code": "Mở trong Claude Code",
        "handoff_note": "Provider link có thể yêu cầu đăng nhập. Khi provider không hỗ trợ prompt prefill, hãy dùng raw Markdown URL.",
        "raw_heading": "Public raw bundle",
        "raw_note": "URL này trả về một Markdown bundle hoàn chỉnh cho nhóm Skill này.",
        "not_found": "Path này không tồn tại.",
        "not_found_body": "SoulMap không tìm thấy public page được yêu cầu.",
        "return_home": "Về trang chủ",
    },
}


CSS = """
:root {
  color-scheme: light;
  --font-sans: Inter, InterVariable, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --ink: #26333a;
  --muted: #5d6b70;
  --paper: #f7f5ef;
  --surface: rgba(255, 255, 255, .78);
  --surface-strong: rgba(255, 255, 255, .92);
  --line: rgba(38, 51, 58, .13);
  --teal: #2f6f6b;
  --teal-dark: #1f514e;
  --gold: #8a681f;
  --focus: #0b5c58;
  --danger: #8b3a3a;
  --shadow: 0 22px 60px rgba(42, 57, 59, .11);
  --shadow-card: 0 12px 35px rgba(42, 57, 59, .05);
  --radius: 24px;
  --radius-hero: 32px;
  --space-1: .25rem;
  --space-2: .5rem;
  --space-3: .75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-12: 3rem;
  --space-16: 4rem;
  --container: 1120px;
  font-family: var(--font-sans);
  font-feature-settings: "liga" 1, "calt" 1;
}
* { box-sizing: border-box; }
[x-cloak] { display: none !important; }
html { scroll-behavior: smooth; scroll-padding-top: 6rem; }
body { margin: 0; min-width: 320px; color: var(--ink); background: radial-gradient(circle at 10% 0%, rgba(201,155,80,.12), transparent 30rem), radial-gradient(circle at 90% 12%, rgba(47,111,107,.10), transparent 28rem), var(--paper); line-height: 1.65; overflow-x: hidden; font-family: var(--font-sans); }
a { color: inherit; }
a:focus-visible, button:focus-visible, input:focus-visible { outline: 3px solid var(--focus); outline-offset: 4px; border-radius: 8px; }
button, input { font: inherit; }
button { cursor: pointer; }
.container { width: min(var(--container), calc(100% - 40px)); margin: 0 auto; }
.skip-link { position: absolute; left: 1rem; top: -5rem; padding: .7rem 1rem; background: var(--ink); color: white; border-radius: 999px; z-index: 10; }
.skip-link:focus { top: 1rem; }
.site-header { position: sticky; top: 0; z-index: 4; backdrop-filter: blur(16px); background: rgba(247,245,239,.84); border-bottom: 1px solid var(--line); padding-top: env(safe-area-inset-top); }
.nav { display: flex; align-items: center; justify-content: space-between; min-height: 76px; gap: 1rem; }
.brand { display: inline-flex; align-items: center; min-height: 44px; gap: .7rem; text-decoration: none; font-weight: 700; letter-spacing: -.02em; }
.brand-mark { display: grid; place-items: center; width: 36px; height: 36px; border-radius: 50%; color: var(--teal-dark); background: rgba(47,111,107,.13); font-size: 1.2rem; }
.nav-links { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: .25rem; }
.nav-links a { display: inline-flex; align-items: center; min-height: 44px; padding: .55rem .75rem; color: var(--muted); font-size: .93rem; text-decoration: none; border-radius: 999px; }
.nav-links a:hover, .nav-links a[aria-current="page"] { color: var(--teal-dark); background: rgba(47,111,107,.09); }
.locale-switcher { display: inline-flex; align-items: center; gap: .25rem; padding-left: .35rem; border-left: 1px solid var(--line); }
.locale-switcher a { min-height: 36px; padding-inline: .55rem; font-size: .78rem; }
.page-hero, .hero { padding: clamp(4.5rem, 10vw, 8rem) 0 5rem; }
.hero-grid { display: grid; grid-template-columns: 1.08fr .92fr; align-items: center; gap: clamp(2rem, 7vw, 6rem); }
.eyebrow { color: var(--teal); font-size: .78rem; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }
h1, h2, h3 { margin: 0 0 1rem; line-height: 1.12; letter-spacing: -.03em; text-wrap: balance; }
h1 { max-width: 850px; font-size: clamp(2.8rem, 6vw, 5rem); font-weight: 800; }
.hero h1 { max-width: 720px; font-size: clamp(3rem, 7vw, 6rem); }
h2 { font-size: clamp(2rem, 4vw, 3.25rem); }
h3 { font-size: 1.25rem; letter-spacing: -.02em; }
.card-title, .step-title, .download-card h2, .skill-card h2 { font-size: 1.25rem; letter-spacing: -.02em; }
p { margin: 0 0 1rem; text-wrap: pretty; }
.lede { max-width: 700px; color: var(--muted); font-size: clamp(1.08rem, 2vw, 1.32rem); }
.actions, .cluster { display: flex; flex-wrap: wrap; gap: .8rem; margin-top: 2rem; align-items: center; }
.button, .link-button { display: inline-flex; align-items: center; justify-content: center; min-height: 48px; padding: .75rem 1.15rem; border: 1px solid var(--teal); border-radius: 999px; color: white; background: var(--teal); text-decoration: none; font-weight: 700; transition: transform .2s ease, background .2s ease, border-color .2s ease; }
.button:hover, .link-button:hover { transform: translateY(-2px); background: var(--teal-dark); }
.button.secondary, .link-button.secondary { color: var(--teal-dark); background: transparent; border-color: var(--line); }
.button.secondary:hover, .link-button.secondary:hover { background: rgba(47,111,107,.08); }
.button.small, .link-button.small { min-height: 42px; padding: .55rem .8rem; font-size: .9rem; }
.mirror-card { position: relative; padding: clamp(2rem, 5vw, 3.5rem); border: 1px solid rgba(47,111,107,.16); border-radius: var(--radius-hero) 36px 28px 32px; background: linear-gradient(145deg, rgba(255,255,255,.88), rgba(222,238,231,.62)); box-shadow: var(--shadow); }
.mirror-card blockquote { position: relative; margin: 0; font-size: clamp(1.45rem, 3vw, 2.1rem); line-height: 1.25; letter-spacing: -.03em; }
.mirror-card cite { position: relative; display: block; margin-top: 1.4rem; color: var(--muted); font-size: .9rem; font-style: normal; }
.section { padding: 5.5rem 0; }
.section.tinted { background: rgba(255,255,255,.48); border-block: 1px solid var(--line); }
.section-heading { max-width: 700px; margin-bottom: 2rem; }
.grid, .skill-grid, .provider-grid { display: grid; gap: 1rem; }
.grid { grid-template-columns: repeat(3, 1fr); }
.card, .step, .download-card, .skill-card { transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease; }
.card { height: 100%; padding: 1.5rem; border: 1px solid var(--line); border-radius: var(--radius); background: var(--surface); box-shadow: var(--shadow-card); }
@media (hover: hover) { .card:hover, .step:hover, .download-card:hover, .skill-card:hover { transform: translateY(-2px); border-color: rgba(47,111,107,.28); box-shadow: 0 16px 40px rgba(42,57,59,.10); } }
.card p, .skill-card p, .download-card p { color: var(--muted); }
.card .number { color: var(--gold); font-size: .8rem; font-weight: 800; letter-spacing: .15em; }
.split { display: grid; grid-template-columns: repeat(2, 1fr); gap: clamp(1.5rem, 5vw, 4rem); align-items: start; }
.list { display: grid; gap: .8rem; margin: 0; padding: 0; list-style: none; }
.list li { display: flex; gap: .75rem; align-items: flex-start; padding: .95rem 0; border-bottom: 1px solid var(--line); }
.list li::before { content: "—"; color: var(--gold); font-weight: 800; }
.callout { padding: 1.4rem 1.5rem; border-left: 3px solid var(--gold); border-radius: 0 var(--radius) var(--radius) 0; background: rgba(201,155,80,.10); }
.steps { counter-reset: step; display: grid; gap: 1rem; }
.step { display: grid; grid-template-columns: 64px 1fr; gap: 1.2rem; align-items: start; padding: 1.4rem; border: 1px solid var(--line); border-radius: var(--radius); background: var(--surface); }
.step::before { counter-increment: step; content: counter(step, decimal-leading-zero); display: grid; place-items: center; width: 56px; height: 56px; border-radius: 50%; color: var(--teal-dark); background: rgba(47,111,107,.12); font-weight: 800; }
.download-card { display: flex; justify-content: space-between; gap: 1.5rem; align-items: center; padding: 1.5rem; border: 1px solid var(--line); border-radius: var(--radius); background: var(--surface); }
.download-card + .download-card { margin-top: 1rem; }
.download-card p { margin-bottom: 0; }
.note-label { color: var(--teal); font-size: .76rem; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; }
.site-footer { margin-top: 5rem; padding: 2.5rem 0 calc(2.5rem + env(safe-area-inset-bottom)); border-top: 1px solid var(--line); color: var(--muted); font-size: .92rem; }
.footer-grid { display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.footer-links { display: flex; gap: 1rem; flex-wrap: wrap; }
.footer-links a { color: var(--muted); }
.catalog-toolbar { display: flex; justify-content: space-between; gap: 1rem; align-items: end; margin-bottom: 2rem; }
.field { display: grid; gap: .35rem; flex: 1; max-width: 680px; }
.field label { font-size: .82rem; font-weight: 800; color: var(--teal-dark); }
.input { width: 100%; min-height: 48px; padding: .7rem .9rem; border: 1px solid var(--line); border-radius: 12px; color: var(--ink); background: var(--surface-strong); }
.skill-grid { grid-template-columns: repeat(3, 1fr); }
.skill-card { display: flex; flex-direction: column; min-height: 100%; padding: 1.35rem; border: 1px solid var(--line); border-radius: var(--radius); background: var(--surface); box-shadow: var(--shadow-card); }
.skill-card__meta { display: flex; justify-content: space-between; gap: .75rem; align-items: center; margin-bottom: .8rem; color: var(--teal); font-size: .74rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; }
.skill-card__body { flex: 1; }
.skill-card__actions { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: 1rem; }
.code-pill { display: inline-flex; align-items: center; padding: .2rem .45rem; border: 1px solid var(--line); border-radius: 8px; color: var(--teal-dark); background: rgba(47,111,107,.06); font-size: .82rem; }
.modal-shell { position: fixed; inset: 0; z-index: 20; display: grid; place-items: center; padding: 1rem; }
.modal-backdrop { position: absolute; inset: 0; background: rgba(20,31,32,.56); backdrop-filter: blur(4px); }
.modal-dialog { position: relative; width: min(720px, 100%); max-height: min(760px, calc(100dvh - 2rem)); overflow: auto; padding: clamp(1.25rem, 4vw, 2rem); border: 1px solid var(--line); border-radius: 20px; color: var(--ink); background: var(--surface-strong); box-shadow: var(--shadow); }
.modal-close { position: absolute; top: .8rem; right: .8rem; width: 44px; height: 44px; border: 1px solid var(--line); border-radius: 50%; color: var(--teal-dark); background: transparent; }
.modal-dialog__header { padding-right: 3rem; }
.provider-grid { grid-template-columns: repeat(3, 1fr); margin-top: 1rem; }
.provider-grid .button { min-height: 44px; padding: .6rem .7rem; font-size: .82rem; text-align: center; }
.modal-note { margin-top: 1rem; color: var(--muted); font-size: .9rem; }
.htmx-indicator { display: none; color: var(--muted); font-size: .85rem; }
.htmx-request .htmx-indicator, .htmx-request.htmx-indicator { display: inline; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
@media (max-width: 900px) { .skill-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 820px) { .hero-grid, .split { grid-template-columns: 1fr; } .hero { padding-top: 4rem; } .mirror-card { max-width: 680px; } }
@media (prefers-color-scheme: dark) {
  :root { color-scheme: dark; --ink: #f0f3ef; --muted: #b7c3bf; --paper: #192322; --surface: rgba(34,48,46,.9); --surface-strong: rgba(31,43,41,.98); --line: rgba(224,239,233,.16); --teal: #84c5ba; --teal-dark: #a2dfd0; --gold: #e0b86a; --focus: #a2dfd0; --shadow: 0 22px 60px rgba(0,0,0,.28); --shadow-card: 0 12px 35px rgba(0,0,0,.18); }
  .site-header { background: rgba(25,35,34,.9); }
  .skip-link { color: var(--paper); background: var(--ink); }
  .button { color: #132522; background: var(--teal); border-color: var(--teal); }
  .button.secondary, .link-button.secondary { color: var(--teal-dark); background: transparent; border-color: var(--line); }
  .mirror-card { background: linear-gradient(145deg, rgba(49,70,66,.9), rgba(38,67,61,.75)); }
  .section.tinted { background: rgba(34,48,46,.48); }
  .callout { background: rgba(224,184,106,.14); }
}
@media (prefers-reduced-transparency: reduce) { .site-header { backdrop-filter: none; background: var(--paper); } .modal-backdrop { backdrop-filter: none; } }
@media (max-width: 640px) {
  .container { width: min(100% - 28px, 560px); }
  .nav { align-items: flex-start; flex-direction: column; padding: .8rem 0; }
  .nav-links { justify-content: flex-start; width: 100%; overflow-x: auto; flex-wrap: nowrap; padding-bottom: .25rem; }
  .nav-links a { flex: 0 0 auto; }
  .locale-switcher { border-left: 0; padding-left: 0; }
  .grid, .skill-grid, .provider-grid { grid-template-columns: 1fr; }
  .catalog-toolbar { align-items: stretch; flex-direction: column; }
  .field { max-width: none; }
  .section { padding: 4rem 0; }
  .download-card { align-items: flex-start; flex-direction: column; }
  .step { grid-template-columns: 48px 1fr; gap: .85rem; }
  .step::before { width: 44px; height: 44px; }
}
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { scroll-behavior: auto !important; transition: none !important; animation: none !important; } }
"""


def tr(locale: str, key: str) -> str:
    return TEXT.get(locale, TEXT["en"]).get(key, TEXT["en"].get(key, key))


def _nav_path(route: str, locale: str) -> str:
    if locale == "en":
        return route or "/"
    return f"/{locale}{route if route != '/' else ''}"


def _nav(path: str, locale: str) -> str:
    links = (
        ("/", tr(locale, "home")),
        ("/how-it-works", tr(locale, "how")),
        ("/boundaries", tr(locale, "boundaries")),
        ("/notes", tr(locale, "notes")),
        ("/about", tr(locale, "about")),
        ("/skills", tr(locale, "skills")),
    )
    rendered = "".join(
        '<a href="{}"{}>{}</a>'.format(
            _nav_path(href, locale),
            ' aria-current="page"' if path == href else "",
            escape(label),
        )
        for href, label in links
    )
    other_locale = "vi" if locale == "en" else "en"
    return f"""
    <header class="site-header">
      <div class="container nav">
        <a class="brand" href="{_nav_path("/", locale)}" aria-label="SoulMap AI home">
          <span class="brand-mark" aria-hidden="true">◌</span>
          <span>SoulMap AI</span>
        </a>
        <nav class="nav-links" aria-label="Primary navigation">{rendered}
          <span class="locale-switcher" aria-label="{escape(tr(locale, "language"))}">
            <a href="{_nav_path(path, other_locale)}" lang="{other_locale}">{other_locale.upper()}</a>
          </span>
        </nav>
      </div>
    </header>
    """


def _layout(title: str, description: str, path: str, content: str, locale: str) -> str:
    safe_title = escape(title)
    safe_description = escape(description)
    language = "vi" if locale == "vi" else "en"
    return f"""<!doctype html>
<html lang="{language}">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
    <meta name="description" content="{safe_description}">
    <meta name="theme-color" content="#f7f5ef" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#192322" media="(prefers-color-scheme: dark)">
    <link rel="preconnect" href="https://rsms.me/">
    <link rel="stylesheet" href="https://rsms.me/inter/inter.css">
    <link rel="stylesheet" href="/static/site.css">
    <script defer src="{HTMX_URL}" integrity="{HTMX_SRI}" crossorigin="anonymous"></script>
    <script defer src="/static/site.js"></script>
    <script defer src="{ALPINE_URL}" integrity="{ALPINE_SRI}" crossorigin="anonymous"></script>
    <title>{safe_title} · {SITE_NAME}</title>
  </head>
  <body>
    <a class="skip-link" href="#main-content">{escape(tr(locale, "skip"))}</a>
    {_nav(path, locale)}
    <main id="main-content">{content}</main>
    <footer class="site-footer">
      <div class="container footer-grid">
        <span>{escape(tr(locale, "footer"))}</span>
        <span class="footer-links">
          <a href="{_nav_path("/download", locale)}">{escape(tr(locale, "download"))}</a>
          <a href="{REPOSITORY_URL}">{escape(tr(locale, "repository"))}</a>
        </span>
      </div>
    </footer>
  </body>
</html>"""


def _home(locale: str) -> str:
    return f"""
    <section class="hero"><div class="container hero-grid"><div>
      <p class="eyebrow">{tr(locale, "home_eyebrow")}</p><h1>{tr(locale, "home_h1")}</h1>
      <p class="lede">{tr(locale, "home_lede")}</p><div class="actions">
        <a class="button" href="{_nav_path("/how-it-works", locale)}">{tr(locale, "home_how")}</a>
        <a class="button secondary" href="{_nav_path("/skills", locale)}">{tr(locale, "home_skills")}</a>
      </div>
    </div><div class="mirror-card" aria-label="SoulMap principle"><blockquote>“{tr(locale, "home_principle")}”</blockquote><cite>SoulMap principle</cite></div></div></section>
    <section class="section tinted"><div class="container"><div class="section-heading"><p class="eyebrow">{tr(locale, "home_section_eyebrow")}</p><h2>{tr(locale, "home_section_h2")}</h2><p class="lede">{tr(locale, "home_section_lede")}</p></div><div class="grid">
      <article class="card"><span class="number">01</span><h3>{tr(locale, "mirror_first")}</h3><p>{tr(locale, "mirror_first_body")}</p></article>
      <article class="card"><span class="number">02</span><h3>{tr(locale, "bounded")}</h3><p>{tr(locale, "bounded_body")}</p></article>
      <article class="card"><span class="number">03</span><h3>{tr(locale, "independence")}</h3><p>{tr(locale, "independence_body")}</p></article>
    </div></div></section>
    <section class="section"><div class="container split"><div><p class="eyebrow">{tr(locale, "quiet_eyebrow")}</p><h2>{tr(locale, "quiet_h2")}</h2></div><div><p>{tr(locale, "quiet_p1")}</p><p>{tr(locale, "quiet_p2")}</p><a class="button secondary" href="{_nav_path("/boundaries", locale)}">{tr(locale, "read_boundaries")}</a></div></div></section>
    """


def _how_it_works(locale: str) -> str:
    return f"""
    <section class="page-hero"><div class="container"><p class="eyebrow">{tr(locale, "how_eyebrow")}</p><h1>{tr(locale, "how_h1")}</h1><p class="lede">{tr(locale, "how_lede")}</p></div></section>
    <section class="section tinted"><div class="container steps">
      <article class="step"><div><h2 class="step-title">{tr(locale, "step_1")}</h2><p>{tr(locale, "step_1_body")}</p></div></article>
      <article class="step"><div><h2 class="step-title">{tr(locale, "step_2")}</h2><p>{tr(locale, "step_2_body")}</p></div></article>
      <article class="step"><div><h2 class="step-title">{tr(locale, "step_3")}</h2><p>{tr(locale, "step_3_body")}</p></div></article>
    </div></section>
    <section class="section"><div class="container split"><div><p class="eyebrow">{tr(locale, "changes")}</p><h2>{tr(locale, "changes_h2")}</h2></div><div class="callout"><p>{tr(locale, "changes_body")}</p></div></div></section>
    """


def _boundaries(locale: str) -> str:
    return f"""
    <section class="page-hero"><div class="container"><p class="eyebrow">{tr(locale, "boundaries_eyebrow")}</p><h1>{tr(locale, "boundaries_h1")}</h1><p class="lede">{tr(locale, "boundaries_lede")}</p></div></section>
    <section class="section tinted"><div class="container grid">
      <article class="card"><h2 class="card-title">{tr(locale, "no_diagnose")}</h2><p>{tr(locale, "no_diagnose_body")}</p></article>
      <article class="card"><h2 class="card-title">{tr(locale, "no_predict")}</h2><p>{tr(locale, "no_predict_body")}</p></article>
      <article class="card"><h2 class="card-title">{tr(locale, "no_replace")}</h2><p>{tr(locale, "no_replace_body")}</p></article>
    </div></section>
    <section class="section"><div class="container split"><div><p class="eyebrow">{tr(locale, "privacy")}</p><h2>{tr(locale, "privacy_h2")}</h2></div><ul class="list"><li>{tr(locale, "privacy_1")}</li><li>{tr(locale, "privacy_2")}</li><li>{tr(locale, "privacy_3")}</li><li>{tr(locale, "privacy_4")}</li></ul></div></section>
    """


def _download(locale: str) -> str:
    return f"""
    <section class="page-hero"><div class="container"><p class="eyebrow">{tr(locale, "download_eyebrow")}</p><h1>{tr(locale, "download_h1")}</h1><p class="lede">{tr(locale, "download_lede")}</p></div></section>
    <section class="section tinted"><div class="container"><div class="download-card"><div><h2>{tr(locale, "skill_package")}</h2><p>{tr(locale, "skill_package_body")}</p></div><a class="button" href="{RELEASE_URL}">{tr(locale, "open_releases")}</a></div><div class="download-card"><div><h2>{tr(locale, "knowledge_archive")}</h2><p>{tr(locale, "knowledge_archive_body")}</p></div><a class="button secondary" href="{RELEASE_URL}">{tr(locale, "view_release")}</a></div></div></section>
    <section class="section"><div class="container split"><div><p class="eyebrow">{tr(locale, "before_import")}</p><h2>{tr(locale, "start_artifact")}</h2></div><div><p>{tr(locale, "artifact_body")}</p></div></div></section>
    """


def _notes(locale: str) -> str:
    return f"""
    <section class="page-hero"><div class="container"><p class="eyebrow">{tr(locale, "notes_eyebrow")}</p><h1>{tr(locale, "notes_h1")}</h1><p class="lede">{tr(locale, "notes_lede")}</p></div></section>
    <section class="section tinted"><div class="container grid"><article class="card"><span class="note-label">Self-recognition</span><h2 class="card-title">{tr(locale, "note_1")}</h2><p>{tr(locale, "note_1_body")}</p></article><article class="card"><span class="note-label">Relational honesty</span><h2 class="card-title">{tr(locale, "note_2")}</h2><p>{tr(locale, "note_2_body")}</p></article><article class="card"><span class="note-label">Grounded inner work</span><h2 class="card-title">{tr(locale, "note_3")}</h2><p>{tr(locale, "note_3_body")}</p></article></div></section>
    <section class="section"><div class="container callout"><p>{tr(locale, "notes_callout")}</p></div></section>
    """


def _about(locale: str) -> str:
    return f"""
    <section class="page-hero"><div class="container"><p class="eyebrow">{tr(locale, "about_eyebrow")}</p><h1>{tr(locale, "about_h1")}</h1><p class="lede">{tr(locale, "about_lede")}</p></div></section>
    <section class="section tinted"><div class="container split"><div><p class="eyebrow">{tr(locale, "posture")}</p><h2>{tr(locale, "posture_h2")}</h2></div><div><p>{tr(locale, "posture_p1")}</p><p>{tr(locale, "posture_p2")}</p></div></div></section>
    <section class="section"><div class="container callout"><p>{tr(locale, "about_callout")}</p></div></section>
    """


def _provider_url(provider: str, raw_url: str, locale: str) -> str:
    prompt = (
        tr(locale, "handoff_note")
        + "\n\nUse this public SoulMap Markdown bundle: "
        + raw_url
    )
    encoded = quote(prompt, safe="")
    if provider == "chatgpt":
        return f"https://chatgpt.com/?q={encoded}"
    if provider == "claude":
        return f"https://claude.ai/new?q={encoded}"
    return f"claude-cli://open?q={encoded}"


def _skill_detail_fragment(entry_slug: str, locale: str) -> str:
    entry = get_skill(entry_slug)
    if entry is None:
        return "<p>Skill not found.</p>"
    fields = locale_fields(entry, locale)
    raw_url = f"{PUBLIC_SITE_URL}/api/raw/{entry.slug}.md"
    return f"""
    <div class="modal-dialog__header"><p class="eyebrow">{escape(entry.group)}</p><h2 id="skill-title-{escape(entry.slug)}">{escape(fields["title"])}</h2><p class="lede">{escape(fields["summary"])}</p></div>
    <div class="split"><div><h3>{escape(tr(locale, "use_when"))}</h3><p>{escape(fields["use_when"])}</p><h3>{escape(tr(locale, "best_for"))}</h3><p>{escape(fields["best_for"])}</p></div><div><h3>{escape(tr(locale, "boundary"))}</h3><p>{escape(fields["boundary"])}</p><p class="modal-note">{escape(tr(locale, "raw_note"))}</p></div></div>
    <div class="cluster"><a class="button small" href="/api/raw/{escape(entry.slug)}.md" target="_blank" rel="noopener">{escape(tr(locale, "raw"))}</a><span x-data="clipboard"><button class="button small secondary" type="button" x-on:click="copy('{escape(raw_url)}')"><span x-text="copied ? '{escape(tr(locale, "copied"))}' : '{escape(tr(locale, "copy_raw"))}'"></span></button></span></div>
    <div class="provider-grid"><a class="button secondary" href="{escape(_provider_url("chatgpt", raw_url, locale))}" target="_blank" rel="noopener">{escape(tr(locale, "open_chatgpt"))}</a><a class="button secondary" href="{escape(_provider_url("claude", raw_url, locale))}" target="_blank" rel="noopener">{escape(tr(locale, "open_claude"))}</a><a class="button secondary" href="{escape(_provider_url("claude-code", raw_url, locale))}">{escape(tr(locale, "open_claude_code"))}</a></div>
    <p class="modal-note">{escape(tr(locale, "handoff_note"))}</p>
    """


def _skill_catalog(locale: str) -> str:
    cards = []
    for entry in CATALOG:
        fields = locale_fields(entry, locale)
        search_text = " ".join(fields.values()).lower()
        cards.append(f"""
        <article class="skill-card" data-search="{escape(search_text)}" x-show="matches($el.dataset.search)" x-transition>
          <div class="skill-card__meta"><span>{escape(entry.group)}</span><span class="code-pill">{escape(entry.slug)}</span></div>
          <div class="skill-card__body"><h2>{escape(fields["title"])}</h2><p>{escape(fields["summary"])}</p></div>
          <div class="skill-card__actions"><a class="button small" href="{_nav_path("/skills/" + entry.slug, locale)}" aria-haspopup="dialog" aria-controls="skill-modal" hx-get="/partials/skill/{escape(entry.slug)}.{locale}.html?lang={locale}" hx-target="#skill-modal-content" hx-swap="innerHTML" hx-indicator="#skill-loading" x-on:click="open('{escape(entry.slug)}', $event.currentTarget)">{escape(tr(locale, "details"))}</a><a class="link-button small secondary" href="/api/raw/{escape(entry.slug)}.md" target="_blank" rel="noopener">{escape(tr(locale, "raw"))}</a><span id="skill-loading" class="htmx-indicator" aria-live="polite">Loading…</span></div>
        </article>""")
    return f"""
    <section class="page-hero"><div class="container"><p class="eyebrow">{tr(locale, "catalog_eyebrow")}</p><h1>{tr(locale, "catalog_h1")}</h1><p class="lede">{tr(locale, "catalog_lede")}</p></div></section>
    <section class="section tinted" x-data="skillCatalog"><div class="container"><div class="catalog-toolbar"><div class="field"><label for="skill-search">{tr(locale, "search_label")}</label><input class="input" id="skill-search" type="search" x-model="query" placeholder="{tr(locale, "search_placeholder")}" autocomplete="off"></div><p class="muted">{len(CATALOG)} groups · raw bundles available</p></div><div class="skill-grid">{"".join(cards)}</div></div><div class="modal-shell" id="skill-modal" x-show="openSlug" x-cloak x-on:keydown="trap($event)" role="presentation"><div class="modal-backdrop" x-on:click="close" aria-hidden="true"></div><div class="modal-dialog" role="dialog" aria-modal="true" tabindex="-1" aria-labelledby="skill-modal-title" x-show="openSlug"><button class="modal-close" type="button" x-on:click="close" aria-label="{escape(tr(locale, "close"))}">x</button><h2 class="sr-only" id="skill-modal-title">SoulMap Skill details</h2><div id="skill-modal-content"><p>{escape(tr(locale, "details"))}</p></div></div></div></section>
    """


def _skill_page(entry_slug: str, locale: str) -> str:
    entry = get_skill(entry_slug)
    if entry is None:
        return _not_found(locale)
    fields = locale_fields(entry, locale)
    return f"""
    <section class="page-hero"><div class="container"><p class="eyebrow">{escape(entry.group)}</p><h1>{escape(fields["title"])}</h1><p class="lede">{escape(fields["summary"])}</p><a class="button secondary" href="{_nav_path("/skills", locale)}">{escape(tr(locale, "skills"))}</a></div></section>
    <section class="section tinted"><div class="container card">{_skill_detail_fragment(entry_slug, locale)}</div></section>
    """


def _not_found(locale: str) -> str:
    return f'<section class="page-hero"><div class="container"><p class="eyebrow">404</p><h1>{escape(tr(locale, "not_found"))}</h1><p class="lede">{escape(tr(locale, "not_found_body"))}</p><a class="button" href="{_nav_path("/", locale)}">{escape(tr(locale, "return_home"))}</a></div></section>'


def _pages() -> dict[str, tuple[str, str, Callable[[str], str]]]:
    return {
        "/": (
            "Hear yourself more clearly",
            "A reflective companion built around self-trust.",
            _home,
        ),
        "/how-it-works": (
            "How it works",
            "How SoulMap uses reflection without taking authority away.",
            _how_it_works,
        ),
        "/boundaries": (
            "Boundaries",
            "The safety and scope boundaries behind SoulMap.",
            _boundaries,
        ),
        "/download": (
            "Download SoulMap Skills",
            "Import the SoulMap Skill or knowledge archive into an AI tool.",
            _download,
        ),
        "/notes": ("Notes", "Grounded public writing from SoulMap AI.", _notes),
        "/about": (
            "About SoulMap AI",
            "The brand posture and purpose behind SoulMap AI.",
            _about,
        ),
        "/skills": (
            "SoulMap Skills",
            "Choose the SoulMap layer that fits the moment.",
            _skill_catalog,
        ),
    }


def _response(
    start_response: StartResponse,
    status: str,
    content_type: str,
    body: str,
    extra_headers: list[tuple[str, str]] | None = None,
) -> list[bytes]:
    payload = body.encode("utf-8")
    headers = [
        ("Content-Type", f"{content_type}; charset=utf-8"),
        ("Content-Length", str(len(payload))),
        ("X-Content-Type-Options", "nosniff"),
        (
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' https://rsms.me; font-src 'self' https://rsms.me; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; object-src 'none'",
        ),
        ("Permissions-Policy", "camera=(), microphone=(), geolocation=()"),
        ("Referrer-Policy", "strict-origin-when-cross-origin"),
    ]
    if extra_headers:
        headers.extend(extra_headers)
    start_response(status, headers)
    return [payload]


def _normalise_request_path(path: str) -> tuple[str, str]:
    normal = "/" + path.strip("/") if path.strip("/") else "/"
    parts = normal.strip("/").split("/") if normal != "/" else []
    if parts and parts[0] in {"en", "vi"}:
        locale = parts.pop(0)
        route = "/" + "/".join(parts) if parts else "/"
        return route, locale
    return normal, "en"


def application(
    environ: dict[str, object], start_response: StartResponse
) -> list[bytes]:
    """Serve the public SoulMap website using the WSGI protocol."""
    raw_path = str(environ.get("PATH_INFO") or "/")
    path, locale = _normalise_request_path(raw_path)
    query = parse_qs(str(environ.get("QUERY_STRING") or ""))
    locale = (
        query.get("lang", [locale])[0]
        if query.get("lang", [locale])[0] in {"en", "vi"}
        else locale
    )
    if path == "/static/site.css":
        return _response(
            start_response,
            "200 OK",
            "text/css",
            CSS,
            [("Cache-Control", "public, max-age=300")],
        )
    if path == "/static/site.js":
        js_path = Path(__file__).with_name("site.js")
        return _response(
            start_response,
            "200 OK",
            "text/javascript",
            js_path.read_text(encoding="utf-8"),
            [("Cache-Control", "public, max-age=300")],
        )
    if path == "/robots.txt":
        return _response(
            start_response, "200 OK", "text/plain", "User-agent: *\nAllow: /\n"
        )
    if path == "/api/skills.json":
        return _response(
            start_response,
            "200 OK",
            "application/json",
            catalog_json(locale),
            [
                ("Access-Control-Allow-Origin", "*"),
                ("Cache-Control", "public, max-age=300"),
            ],
        )
    if path.startswith("/api/skills/") and path.endswith(".json"):
        entry = get_skill(path.removeprefix("/api/skills/").removesuffix(".json"))
        if entry is None:
            return _response(
                start_response,
                "404 Not Found",
                "application/json",
                json.dumps({"error": "skill_not_found"}),
            )
        data = locale_fields(entry, locale) | {
            "slug": entry.slug,
            "group": entry.group,
            "raw_path": f"/api/raw/{entry.slug}.md",
        }
        return _response(
            start_response,
            "200 OK",
            "application/json",
            json.dumps(data, ensure_ascii=False),
            [
                ("Access-Control-Allow-Origin", "*"),
                ("Cache-Control", "public, max-age=300"),
            ],
        )
    if path.startswith("/api/raw/") and path.endswith(".md"):
        entry = get_skill(path.removeprefix("/api/raw/").removesuffix(".md"))
        if entry is None:
            return _response(
                start_response, "404 Not Found", "text/plain", "Skill not found.\n"
            )
        return _response(
            start_response,
            "200 OK",
            "text/markdown",
            raw_markdown(entry),
            [
                ("Access-Control-Allow-Origin", "*"),
                ("Content-Disposition", "inline"),
                ("Cache-Control", "public, max-age=300"),
            ],
        )
    if path.startswith("/partials/skill/") and path.endswith(".html"):
        filename = path.removeprefix("/partials/skill/").removesuffix(".html")
        slug, _, partial_locale = filename.rpartition(".")
        if not slug:
            slug, partial_locale = filename, locale
        partial_locale = partial_locale if partial_locale in {"en", "vi"} else locale
        return _response(
            start_response,
            "200 OK",
            "text/html",
            _skill_detail_fragment(slug, partial_locale),
        )
    if path.startswith("/skills/") and path.count("/") == 2:
        slug = path.removeprefix("/skills/")
        entry = get_skill(slug)
        if entry is None:
            return _response(
                start_response,
                "404 Not Found",
                "text/html",
                _layout(
                    "Not found",
                    "Page not found.",
                    "/skills",
                    _not_found(locale),
                    locale,
                ),
            )
        content = _skill_page(slug, locale)
        return _response(
            start_response,
            "200 OK",
            "text/html",
            _layout(
                entry.title_en, entry.summary_en, "/skills/" + slug, content, locale
            ),
        )
    pages = _pages()
    if path not in pages:
        return _response(
            start_response,
            "404 Not Found",
            "text/html",
            _layout("Not found", "Page not found.", path, _not_found(locale), locale),
        )
    title, description, renderer = pages[path]
    return _response(
        start_response,
        "200 OK",
        "text/html",
        _layout(title, description, path, renderer(locale), locale),
    )


def _normalise_base_path(base_path: str) -> str:
    cleaned = base_path.strip()
    if not cleaned or cleaned == "/":
        return ""
    return "/" + cleaned.strip("/")


def _apply_base_path(content: str, base_path: str) -> str:
    if not base_path:
        return content
    for attribute in ("href", "src", "hx-get"):
        content = content.replace(f'{attribute}="/', f'{attribute}="{base_path}/')
    return content


def _write_page(
    output: Path, route: str, page: str, written: list[Path], base_path: str
) -> None:
    destination = output / ("index.html" if route == "/" else route.strip("/"))
    destination = destination if destination.suffix else destination / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(_apply_base_path(page, base_path), encoding="utf-8")
    written.append(destination)


def export_static(output: Path, base_path: str = "") -> list[Path]:
    """Export public pages, locale variants, API JSON, raw bundles and partials."""
    output = output.resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    normalised_base = _normalise_base_path(base_path)
    written: list[Path] = []
    pages = _pages()
    for locale in ("en", "vi"):
        locale_prefix = "" if locale == "en" else "/vi"
        for route, (title, description, renderer) in pages.items():
            page_route = f"{locale_prefix}{route if route != '/' else ''}" or "/"
            _write_page(
                output,
                page_route,
                _layout(title, description, route, renderer(locale), locale),
                written,
                normalised_base,
            )
        if locale == "en":
            for route, (title, description, renderer) in pages.items():
                page_route = f"/en{route if route != '/' else ''}"
                _write_page(
                    output,
                    page_route,
                    _layout(title, description, route, renderer(locale), locale),
                    written,
                    normalised_base,
                )
    for entry in CATALOG:
        for locale in ("en", "vi"):
            prefix = "" if locale == "en" else "/vi"
            _write_page(
                output,
                f"{prefix}/skills/{entry.slug}",
                _layout(
                    entry.title_en,
                    entry.summary_en,
                    f"/skills/{entry.slug}",
                    _skill_page(entry.slug, locale),
                    locale,
                ),
                written,
                normalised_base,
            )
            partial = output / f"partials/skill/{entry.slug}.{locale}.html"
            partial.parent.mkdir(parents=True, exist_ok=True)
            partial.write_text(
                _skill_detail_fragment(entry.slug, locale), encoding="utf-8"
            )
            written.append(partial)
    api_dir = output / "api"
    (api_dir / "raw").mkdir(parents=True, exist_ok=True)
    (api_dir / "skills").mkdir(parents=True, exist_ok=True)
    (api_dir / "skills.json").write_text(catalog_json(), encoding="utf-8")
    written.append(api_dir / "skills.json")
    for entry in CATALOG:
        raw_path = api_dir / "raw" / f"{entry.slug}.md"
        raw_path.write_text(raw_markdown(entry), encoding="utf-8")
        written.append(raw_path)
        data_path = api_dir / "skills" / f"{entry.slug}.json"
        data_path.write_text(
            json.dumps(entry.public_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        written.append(data_path)
    (output / "static").mkdir()
    (output / "static" / "site.css").write_text(CSS, encoding="utf-8")
    (output / "static" / "site.js").write_text(
        Path(__file__).with_name("site.js").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (output / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    written.extend(
        [
            output / "static" / "site.css",
            output / "static" / "site.js",
            output / "robots.txt",
        ]
    )
    return written


def serve(host: str = HOST, port: int = PORT) -> None:
    """Run the local website server until interrupted."""

    class QuietRequestHandler(WSGIRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            print(format % args)

    with make_server(
        host,
        port,
        application,
        server_class=WSGIServer,
        handler_class=QuietRequestHandler,
    ) as httpd:
        print(f"SoulMap website running at http://{host}:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nSoulMap website stopped.")


def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="soulmap web", description="Run or export the SoulMap public website."
    )
    parser.add_argument("--host", default=HOST, help=f"Bind host (default: {HOST})")
    parser.add_argument(
        "--port", type=int, default=PORT, help=f"Bind port (default: {PORT})"
    )
    parser.add_argument(
        "--export-static",
        action="store_true",
        help="Write static files instead of serving.",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("site"), help="Static output directory."
    )
    parser.add_argument(
        "--base-path",
        default="",
        help="URL path prefix for a GitHub Pages project site.",
    )
    parsed = parser.parse_args(args)
    if parsed.export_static:
        written = export_static(parsed.output, parsed.base_path)
        print(f"Exported {len(written)} static website files to {parsed.output}")
        return 0
    serve(parsed.host, parsed.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
