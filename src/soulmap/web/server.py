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
from soulmap.web.templates import render_template

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


def _read_static_css() -> str:
    return (Path(__file__).with_name("static") / "site.css").read_text(encoding="utf-8")


def tr(locale: str, key: str) -> str:
    return TEXT.get(locale, TEXT["en"]).get(key, TEXT["en"].get(key, key))


def _nav_path(route: str, locale: str) -> str:
    if locale == "en":
        return route or "/"
    return f"/{locale}{route if route != '/' else ''}"


def _text(locale: str, key: str) -> str:
    return escape(tr(locale, key))


def _nav(path: str, locale: str) -> str:
    links = (
        ("/", "home"),
        ("/how-it-works", "how"),
        ("/boundaries", "boundaries"),
        ("/notes", "notes"),
        ("/about", "about"),
        ("/skills", "skills"),
    )
    rendered = "".join(
        '<a href="{}"{}>{}</a>'.format(
            escape(_nav_path(href, locale), quote=True),
            ' aria-current="page"' if path == href else "",
            _text(locale, label_key),
        )
        for href, label_key in links
    )
    other_locale = "vi" if locale == "en" else "en"
    return render_template(
        "partials/nav.html",
        brand_home=escape(_nav_path("/", locale), quote=True),
        nav_links=rendered,
        language_label=_text(locale, "language"),
        locale_href=escape(_nav_path(path, other_locale), quote=True),
        other_locale=other_locale,
        other_locale_upper=other_locale.upper(),
    )


def _layout(title: str, description: str, path: str, content: str, locale: str) -> str:
    language = "vi" if locale == "vi" else "en"
    footer = render_template(
        "partials/footer.html",
        footer_label=_text(locale, "footer"),
        download_href=escape(_nav_path("/download", locale), quote=True),
        download_label=_text(locale, "download"),
        repository_url=escape(REPOSITORY_URL, quote=True),
        repository_label=_text(locale, "repository"),
    )
    return render_template(
        "layout.html",
        language=language,
        description=escape(description, quote=True),
        title=escape(title),
        site_name=escape(SITE_NAME),
        skip_label=_text(locale, "skip"),
        nav=_nav(path, locale),
        content=content,
        footer=footer,
        htmx_url=escape(HTMX_URL, quote=True),
        htmx_sri=escape(HTMX_SRI, quote=True),
        alpine_url=escape(ALPINE_URL, quote=True),
        alpine_sri=escape(ALPINE_SRI, quote=True),
    )


def _home(locale: str) -> str:
    principles = "".join(
        f'<article class="card"><span class="number">0{index}</span><h3>{_text(locale, title_key)}</h3><p>{_text(locale, body_key)}</p></article>'
        for index, (title_key, body_key) in enumerate(
            (
                ("mirror_first", "mirror_first_body"),
                ("bounded", "bounded_body"),
                ("independence", "independence_body"),
            ),
            1,
        )
    )
    return render_template(
        "pages/home.html",
        home_eyebrow=_text(locale, "home_eyebrow"),
        home_h1=_text(locale, "home_h1"),
        home_lede=_text(locale, "home_lede"),
        how_href=escape(_nav_path("/how-it-works", locale), quote=True),
        home_how=_text(locale, "home_how"),
        skills_href=escape(_nav_path("/skills", locale), quote=True),
        home_skills=_text(locale, "home_skills"),
        home_principle=_text(locale, "home_principle"),
        home_section_eyebrow=_text(locale, "home_section_eyebrow"),
        home_section_h2=_text(locale, "home_section_h2"),
        home_section_lede=_text(locale, "home_section_lede"),
        principles=principles,
        quiet_eyebrow=_text(locale, "quiet_eyebrow"),
        quiet_h2=_text(locale, "quiet_h2"),
        quiet_p1=_text(locale, "quiet_p1"),
        quiet_p2=_text(locale, "quiet_p2"),
        boundaries_href=escape(_nav_path("/boundaries", locale), quote=True),
        read_boundaries=_text(locale, "read_boundaries"),
    )


def _how_it_works(locale: str) -> str:
    steps = "".join(
        f'<article class="step"><div><h2 class="step-title">{_text(locale, title_key)}</h2><p>{_text(locale, body_key)}</p></div></article>'
        for title_key, body_key in (
            ("step_1", "step_1_body"),
            ("step_2", "step_2_body"),
            ("step_3", "step_3_body"),
        )
    )
    return render_template(
        "pages/how-it-works.html",
        how_eyebrow=_text(locale, "how_eyebrow"),
        how_h1=_text(locale, "how_h1"),
        how_lede=_text(locale, "how_lede"),
        steps=steps,
        changes=_text(locale, "changes"),
        changes_h2=_text(locale, "changes_h2"),
        changes_body=_text(locale, "changes_body"),
    )


def _boundaries(locale: str) -> str:
    cards = "".join(
        f'<article class="card"><h2 class="card-title">{_text(locale, title_key)}</h2><p>{_text(locale, body_key)}</p></article>'
        for title_key, body_key in (
            ("no_diagnose", "no_diagnose_body"),
            ("no_predict", "no_predict_body"),
            ("no_replace", "no_replace_body"),
        )
    )
    privacy_items = "".join(
        f"<li>{_text(locale, key)}</li>"
        for key in ("privacy_1", "privacy_2", "privacy_3", "privacy_4")
    )
    return render_template(
        "pages/boundaries.html",
        boundaries_eyebrow=_text(locale, "boundaries_eyebrow"),
        boundaries_h1=_text(locale, "boundaries_h1"),
        boundaries_lede=_text(locale, "boundaries_lede"),
        boundary_cards=cards,
        privacy=_text(locale, "privacy"),
        privacy_h2=_text(locale, "privacy_h2"),
        privacy_items=privacy_items,
    )


def _download(locale: str) -> str:
    return render_template(
        "pages/download.html",
        download_eyebrow=_text(locale, "download_eyebrow"),
        download_h1=_text(locale, "download_h1"),
        download_lede=_text(locale, "download_lede"),
        skill_package=_text(locale, "skill_package"),
        skill_package_body=_text(locale, "skill_package_body"),
        knowledge_archive=_text(locale, "knowledge_archive"),
        knowledge_archive_body=_text(locale, "knowledge_archive_body"),
        release_url=escape(RELEASE_URL, quote=True),
        open_releases=_text(locale, "open_releases"),
        view_release=_text(locale, "view_release"),
        before_import=_text(locale, "before_import"),
        start_artifact=_text(locale, "start_artifact"),
        artifact_body=_text(locale, "artifact_body"),
    )


def _notes(locale: str) -> str:
    labels = ("Self-recognition", "Relational honesty", "Grounded inner work")
    cards = "".join(
        f'<article class="card"><span class="note-label">{label}</span><h2 class="card-title">{_text(locale, title_key)}</h2><p>{_text(locale, body_key)}</p></article>'
        for label, title_key, body_key in zip(
            labels,
            ("note_1", "note_2", "note_3"),
            ("note_1_body", "note_2_body", "note_3_body"),
            strict=True,
        )
    )
    return render_template(
        "pages/notes.html",
        notes_eyebrow=_text(locale, "notes_eyebrow"),
        notes_h1=_text(locale, "notes_h1"),
        notes_lede=_text(locale, "notes_lede"),
        note_cards=cards,
        notes_callout=_text(locale, "notes_callout"),
    )


def _about(locale: str) -> str:
    return render_template(
        "pages/about.html",
        about_eyebrow=_text(locale, "about_eyebrow"),
        about_h1=_text(locale, "about_h1"),
        about_lede=_text(locale, "about_lede"),
        posture=_text(locale, "posture"),
        posture_h2=_text(locale, "posture_h2"),
        posture_p1=_text(locale, "posture_p1"),
        posture_p2=_text(locale, "posture_p2"),
        about_callout=_text(locale, "about_callout"),
    )


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
    return render_template(
        "partials/skill-detail.html",
        group=escape(entry.group),
        slug=escape(entry.slug),
        title=escape(fields["title"]),
        summary=escape(fields["summary"]),
        use_when_label=_text(locale, "use_when"),
        use_when=escape(fields["use_when"]),
        best_for_label=_text(locale, "best_for"),
        best_for=escape(fields["best_for"]),
        boundary_label=_text(locale, "boundary"),
        boundary=escape(fields["boundary"]),
        raw_note=_text(locale, "raw_note"),
        raw_href=escape(f"/api/raw/{entry.slug}.md", quote=True),
        raw_label=_text(locale, "raw"),
        raw_url=escape(raw_url, quote=True),
        copied_label=_text(locale, "copied"),
        copy_raw_label=_text(locale, "copy_raw"),
        chatgpt_url=escape(_provider_url("chatgpt", raw_url, locale), quote=True),
        claude_url=escape(_provider_url("claude", raw_url, locale), quote=True),
        claude_code_url=escape(
            _provider_url("claude-code", raw_url, locale), quote=True
        ),
        chatgpt_label=_text(locale, "open_chatgpt"),
        claude_label=_text(locale, "open_claude"),
        claude_code_label=_text(locale, "open_claude_code"),
        handoff_note=_text(locale, "handoff_note"),
    )


def _skill_catalog(locale: str) -> str:
    cards = []
    for entry in CATALOG:
        fields = locale_fields(entry, locale)
        search_text = " ".join(fields.values()).lower()
        cards.append(
            f'<article class="skill-card" data-search="{escape(search_text)}" x-show="matches($el.dataset.search)" x-transition>'
            f'<div class="skill-card__meta"><span>{escape(entry.group)}</span><span class="code-pill">{escape(entry.slug)}</span></div>'
            f'<div class="skill-card__body"><h2>{escape(fields["title"])}</h2><p>{escape(fields["summary"])}</p></div>'
            f'<div class="skill-card__actions"><a class="button small" href="{escape(_nav_path("/skills/" + entry.slug, locale), quote=True)}" aria-haspopup="dialog" aria-controls="skill-modal" hx-get="/partials/skill/{escape(entry.slug)}.{locale}.html?lang={locale}" hx-target="#skill-modal-content" hx-swap="innerHTML" hx-indicator="#skill-loading" x-on:click="open(\'{escape(entry.slug)}\', $event.currentTarget)">{_text(locale, "details")}</a><a class="link-button small secondary" href="/api/raw/{escape(entry.slug)}.md" target="_blank" rel="noopener">{_text(locale, "raw")}</a><span id="skill-loading" class="htmx-indicator" aria-live="polite">Loading…</span></div>'
            "</article>"
        )
    return render_template(
        "pages/skill-catalog.html",
        catalog_eyebrow=_text(locale, "catalog_eyebrow"),
        catalog_h1=_text(locale, "catalog_h1"),
        catalog_lede=_text(locale, "catalog_lede"),
        search_label=_text(locale, "search_label"),
        search_placeholder=_text(locale, "search_placeholder"),
        catalog_count=str(len(CATALOG)),
        skill_cards="".join(cards),
        close_label=_text(locale, "close"),
        details_label=_text(locale, "details"),
    )


def _skill_page(entry_slug: str, locale: str) -> str:
    entry = get_skill(entry_slug)
    if entry is None:
        return _not_found(locale)
    fields = locale_fields(entry, locale)
    return render_template(
        "pages/skill-page.html",
        group=escape(entry.group),
        title=escape(fields["title"]),
        summary=escape(fields["summary"]),
        skills_href=escape(_nav_path("/skills", locale), quote=True),
        skills_label=_text(locale, "skills"),
        detail=_skill_detail_fragment(entry_slug, locale),
    )


def _not_found(locale: str) -> str:
    return render_template(
        "pages/not-found.html",
        not_found=_text(locale, "not_found"),
        not_found_body=_text(locale, "not_found_body"),
        home_href=escape(_nav_path("/", locale), quote=True),
        return_home=_text(locale, "return_home"),
    )


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
            _read_static_css(),
            [("Cache-Control", "public, max-age=300")],
        )
    if path == "/static/site.js":
        js_path = Path(__file__).with_name("static") / "site.js"
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
    (output / "static" / "site.css").write_text(_read_static_css(), encoding="utf-8")
    (output / "static" / "site.js").write_text(
        (Path(__file__).with_name("static") / "site.js").read_text(encoding="utf-8"),
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
