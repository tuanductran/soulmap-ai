"""Public SoulMap Skill catalog metadata and raw Markdown bundle helpers."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from soulmap.web.i18n import SUPPORTED_LOCALES
from soulmap.web.prompt_pack import scenarios_for

PUBLIC_RAW_BASE_URL = "https://tuanductran.github.io/soulmap-ai"


def _content_locale(locale: str) -> str:
    return "vi" if locale == "vi" else "en"


def _response_locale(locale: str) -> str:
    return locale if locale in SUPPORTED_LOCALES else "en"


@dataclass(frozen=True)
class SkillEntry:
    """Public-facing metadata for one importable SoulMap capability group."""

    slug: str
    group: str
    group_vi: str
    title_en: str
    title_vi: str
    summary_en: str
    summary_vi: str
    use_when_en: str
    use_when_vi: str
    best_for_en: str
    best_for_vi: str
    boundary_en: str
    boundary_vi: str
    directory: str
    featured_file: str

    def public_dict(self) -> dict[str, object]:
        """Return metadata safe for the public catalog API."""
        return {
            "slug": self.slug,
            "group": self.group,
            "title": self.title_en,
            "summary": self.summary_en,
            "use_when": self.use_when_en,
            "best_for": self.best_for_en,
            "boundary": self.boundary_en,
            "raw_path": f"/api/raw/{self.slug}.md",
            "raw_url": f"{PUBLIC_RAW_BASE_URL}/api/raw/{self.slug}.md",
            "featured_file": self.featured_file,
            "prompt_scenarios": [
                scenario.localized("en") for scenario in scenarios_for(self.slug)
            ],
        }


CATALOG: tuple[SkillEntry, ...] = (
    SkillEntry(
        slug="meta",
        group="Core",
        group_vi="Cốt lõi",
        title_en="Core orchestration",
        title_vi="Điều phối cốt lõi",
        summary_en="The routing layer that decides how SoulMap should listen, calibrate depth, choose a framework, and protect user authority.",
        summary_vi="Lớp điều phối quyết định cách SoulMap lắng nghe, hiệu chỉnh độ sâu, chọn khung phù hợp và bảo vệ quyền tự chủ của người dùng.",
        use_when_en="Start here when you are integrating SoulMap or need to understand the response pipeline.",
        use_when_vi="Bắt đầu từ đây khi bạn đang tích hợp SoulMap hoặc cần hiểu quy trình phản hồi.",
        best_for_en="Routing, stage calibration, response shape, session contract, and orchestration.",
        best_for_vi="Điều phối, hiệu chỉnh giai đoạn, cấu trúc phản hồi, thỏa thuận phiên và tổ chức luồng.",
        boundary_en="It is the coordination layer, not a standalone therapeutic or predictive prompt.",
        boundary_vi="Đây là lớp điều phối, không phải prompt trị liệu hay dự đoán độc lập.",
        directory="meta",
        featured_file="SKILL.md",
    ),
    SkillEntry(
        slug="frameworks",
        group="Reflection",
        group_vi="Phản chiếu",
        title_en="Reflective frameworks",
        title_vi="Các khung phản chiếu",
        summary_en="Situation-specific mirrors for grief, anger, relationships, identity patterns, creativity, self-compassion, and inner work.",
        summary_vi="Các tấm gương theo tình huống cho mất mát, giận dữ, quan hệ, mô thức về danh tính, sáng tạo, lòng trắc ẩn với bản thân và thực hành nội tâm.",
        use_when_en="Use the framework that matches the lived pattern without turning it into a fixed identity.",
        use_when_vi="Dùng khung phù hợp với mô thức đang sống mà không biến nó thành danh tính cố định.",
        best_for_en="A focused conversation after the core layer has identified the right territory.",
        best_for_vi="Một cuộc trò chuyện tập trung sau khi lớp cốt lõi đã xác định đúng vùng cần làm việc.",
        boundary_en="Frameworks offer lenses and questions; they do not diagnose, label, or claim certainty.",
        boundary_vi="Các khung chỉ đưa ra lăng kính và câu hỏi; không chẩn đoán, gắn nhãn hay khẳng định chắc chắn.",
        directory="frameworks",
        featured_file="SKILL.md",
    ),
    SkillEntry(
        slug="safety",
        group="Safety",
        group_vi="An toàn",
        title_en="Safety guardrails",
        title_vi="Rào chắn an toàn",
        summary_en="The non-negotiable boundaries for crisis language, trauma-informed wording, prompt injection, ethics, and scope control.",
        summary_vi="Các giới hạn không thể thương lượng cho ngôn ngữ về khủng hoảng, cách diễn đạt hiểu biết về sang chấn, prompt injection, đạo đức và kiểm soát phạm vi.",
        use_when_en="Load this whenever a conversation involves risk, crisis, trauma, diagnosis, prediction, or attempts to override the system.",
        use_when_vi="Luôn tải lớp này khi hội thoại liên quan đến rủi ro, khủng hoảng, sang chấn, chẩn đoán, dự đoán hoặc nỗ lực vượt qua hệ thống.",
        best_for_en="Safety classification, refusal/redirect, prompt-injection defense, and grounded support language.",
        best_for_vi="Phân loại an toàn, từ chối/chuyển hướng, phòng thủ prompt injection và ngôn ngữ hỗ trợ có nền tảng.",
        boundary_en="Safety overrides resonance; never use warmth to soften a necessary boundary.",
        boundary_vi="An toàn luôn được ưu tiên hơn sự đồng điệu; không dùng sự ấm áp để làm mềm một ranh giới cần thiết.",
        directory="safety",
        featured_file="SKILL.md",
    ),
    SkillEntry(
        slug="spiritual",
        group="Symbolic",
        group_vi="Biểu tượng",
        title_en="Grounded symbolic layer",
        title_vi="Lớp biểu tượng có nền tảng",
        summary_en="Optional symbolic language for discernment, metaphors, numerology, chakra themes, and reports without spiritual grandiosity.",
        summary_vi="Ngôn ngữ biểu tượng tùy chọn cho phân định, ẩn dụ, số học, chủ đề chakra và các báo cáo không thổi phồng tâm linh.",
        use_when_en="Use only when symbolic framing helps the user inquire more honestly into lived experience.",
        use_when_vi="Chỉ dùng khi cách diễn đạt biểu tượng giúp người dùng tự vấn trung thực hơn về trải nghiệm đang sống.",
        best_for_en="Discernment, metaphor, symbolic reports, and brand-safe spiritual reflection.",
        best_for_vi="Phân định, ẩn dụ, báo cáo biểu tượng và phản chiếu tâm linh an toàn cho thương hiệu.",
        boundary_en="Symbolism is a lens, never proof of destiny, special status, or supernatural authority.",
        boundary_vi="Biểu tượng là một lăng kính, không phải bằng chứng về định mệnh, vị thế đặc biệt hay quyền lực siêu nhiên.",
        directory="spiritual",
        featured_file="SKILL.md",
    ),
    SkillEntry(
        slug="voice",
        group="Voice",
        group_vi="Giọng điệu",
        title_en="Voice and calibration",
        title_vi="Giọng điệu và hiệu chỉnh",
        summary_en="The pacing, warmth, clarity, response length, and session rituals that make SoulMap feel coherent without becoming dependent.",
        summary_vi="Nhịp điệu, sự ấm áp, độ rõ, độ dài phản hồi và các nghi thức phiên giúp SoulMap nhất quán mà không tạo phụ thuộc.",
        use_when_en="Use this when the content is correct but the tone, pacing, or emotional distance feels wrong.",
        use_when_vi="Dùng khi nội dung đúng nhưng giọng điệu, nhịp độ hoặc khoảng cách cảm xúc chưa phù hợp.",
        best_for_en="Persona, response calibration, opening rituals, and grounded closing posture.",
        best_for_vi="Persona, hiệu chỉnh phản hồi, nghi thức mở đầu và tư thế kết thúc có nền tảng.",
        boundary_en="Voice shapes delivery; it must never add authority, intimacy hooks, or emotional rescue.",
        boundary_vi="Giọng điệu chỉ định hình cách truyền đạt; không được thêm thẩm quyền, móc nối thân mật hay giải cứu cảm xúc.",
        directory="voice",
        featured_file="SKILL.md",
    ),
    SkillEntry(
        slug="brand",
        group="Brand",
        group_vi="Thương hiệu",
        title_en="Brand and positioning",
        title_vi="Thương hiệu và định vị",
        summary_en="Public positioning, visual identity, content pillars, differentiation, and scope language for a coherent SoulMap surface.",
        summary_vi="Định vị công khai, nhận diện trực quan, trụ cột nội dung, điểm khác biệt và ngôn ngữ phạm vi cho một SoulMap nhất quán.",
        use_when_en="Use this when writing public copy, naming a surface, or checking whether a visual decision still feels like SoulMap.",
        use_when_vi="Dùng khi viết nội dung công khai, đặt tên cho một bề mặt hoặc kiểm tra một quyết định hình ảnh còn đúng chất SoulMap.",
        best_for_en="Brand voice, visual system, strategic direction, and public-facing boundaries.",
        best_for_vi="Giọng thương hiệu, hệ thống hình ảnh, định hướng chiến lược và các ranh giới hướng ra công chúng.",
        boundary_en="Brand guidance is not a substitute for the runtime safety and orchestration layers.",
        boundary_vi="Hướng dẫn thương hiệu không thay thế các lớp an toàn runtime và điều phối.",
        directory="brand",
        featured_file="visual-identity.md",
    ),
)

_BY_SLUG = {entry.slug: entry for entry in CATALOG}
_SEARCH_FIELDS = ("group", "title", "summary", "use_when", "best_for", "boundary")


def _normalise_search_text(value: str) -> str:
    """Fold accents and punctuation so public search behaves consistently."""
    decomposed = unicodedata.normalize("NFKD", value.casefold().replace("đ", "d"))
    without_marks = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", " ", without_marks).strip()


def _search_tokens(value: str) -> tuple[str, ...]:
    return tuple(
        token for token in _normalise_search_text(value).split() if len(token) > 1
    )


def _public_entry_dict(
    entry: SkillEntry, locale: str = "en", raw_base_url: str = PUBLIC_RAW_BASE_URL
) -> dict[str, object]:
    language = _content_locale(locale)
    fields = locale_fields(entry, language)
    return {
        "slug": entry.slug,
        **fields,
        "raw_path": f"/api/raw/{entry.slug}.md",
        "raw_url": f"{raw_base_url.rstrip('/')}/api/raw/{entry.slug}.md"
        if raw_base_url
        else "",
        "featured_file": entry.featured_file,
        "prompt_scenarios": [
            scenario.localized(language) for scenario in scenarios_for(entry.slug)
        ],
    }


def search_catalog(
    locale: str = "en", query: str = "", group: str = "", limit: int = 50
) -> list[dict[str, object]]:
    """Search localized Skill metadata with deterministic relevance ranking."""
    language = _content_locale(locale)
    query_normalised = _normalise_search_text(query)
    query_tokens = _search_tokens(query)
    group_normalised = _normalise_search_text(group)
    bounded_limit = max(1, min(limit, 100))
    ranked: list[tuple[int, int, dict[str, object]]] = []

    for position, entry in enumerate(CATALOG):
        fields = locale_fields(entry, language)
        normalized_fields = {
            field: _normalise_search_text(fields[field]) for field in _SEARCH_FIELDS
        }
        normalized_slug = _normalise_search_text(entry.slug)
        if group_normalised and group_normalised not in normalized_fields["group"]:
            continue

        matched_fields: list[str] = []
        score = 0
        if query_normalised:
            if query_normalised == normalized_slug:
                score += 1000
                matched_fields.append("slug")
            if query_normalised == normalized_fields["title"]:
                score += 900
                matched_fields.append("title")
            for field, value in normalized_fields.items():
                if query_normalised in value:
                    score += {"group": 360, "title": 420}.get(field, 180)
                    if field not in matched_fields:
                        matched_fields.append(field)
            for token in query_tokens:
                for field, value in (
                    ("slug", normalized_slug),
                    *normalized_fields.items(),
                ):
                    if token in value:
                        score += 40 if token == value else 15
                        if field not in matched_fields:
                            matched_fields.append(field)
            if score == 0:
                continue

        result = _public_entry_dict(entry, language)
        result["score"] = score
        result["matched_fields"] = matched_fields
        ranked.append((score, -position, result))

    ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [result for _, _, result in ranked[:bounded_limit]]


def catalog_search_json(
    locale: str = "en", query: str = "", group: str = "", limit: int = 50
) -> str:
    """Serialize the public, localized advanced-search response."""
    language = _content_locale(locale)
    bounded_limit = max(1, min(limit, 100))
    all_results = search_catalog(language, query, group, 100)
    results = all_results[:bounded_limit]
    return json.dumps(
        {
            "version": 1,
            "locale": _response_locale(locale),
            "query": query,
            "group": group,
            "limit": bounded_limit,
            "total": len(all_results),
            "results": results,
        },
        ensure_ascii=False,
        indent=2,
    )


def get_skill(slug: str) -> SkillEntry | None:
    """Return a catalog entry by public slug."""
    return _BY_SLUG.get(slug)


def _repo_root() -> Path:
    candidates = (
        Path(__file__).resolve().parents[3],
        Path.cwd(),
    )
    for candidate in candidates:
        if (candidate / "skills").is_dir():
            return candidate
    return candidates[0]


def _sanitize_public_markdown(markdown: str) -> str:
    """Remove repository-only references while preserving public Skill guidance."""
    sanitized = re.sub(r"\[([^\]]+)\]\((?:\.\./)+AGENTS\.md\)", r"\1", markdown)
    sanitized = re.sub(
        r"\[AGENTS\.md\]\([^)]*\)", "SoulMap behavioral contract", sanitized
    )
    sanitized = sanitized.replace("AGENTS.md", "SoulMap behavioral contract")
    sanitized = re.sub(
        r"(?<!\w)(?:\.claude/|\.github/|src/|tests/|pyproject\.toml|uv\.lock)(?:[A-Za-z0-9_./-]*)",
        "repository internals",
        sanitized,
    )
    return sanitized


def raw_markdown(entry: SkillEntry) -> str:
    """Build one complete public Markdown bundle for a catalog group."""
    directory = _repo_root() / "skills" / entry.directory
    files = sorted(directory.glob("*.md")) if directory.is_dir() else []
    sections = [
        f"# SoulMap Skill bundle: {entry.title_en}\n\n",
        f"> Canonical public raw bundle for `{entry.slug}`.\n\n",
    ]
    if not files:
        sections.append(
            "This raw bundle is not available in the current runtime checkout. "
            "Use the published release artifact instead.\n"
        )
        return "".join(sections)
    for path in files:
        sections.append(f"\n---\n\n## {path.name}\n\n")
        sections.append(_sanitize_public_markdown(path.read_text(encoding="utf-8")))
        sections.append("\n")
    scenarios = scenarios_for(entry.slug)
    raw_url = f"{PUBLIC_RAW_BASE_URL}/api/raw/{entry.slug}.md"
    if scenarios:
        sections.append("\n---\n\n## Suggested prompts by context\n\n")
        sections.append(
            "Use one scenario that matches the user's context. Keep the source bundle "
            "as the reference and return authorship to the user.\n\n"
        )
        for scenario in scenarios:
            sections.append(f"### {scenario.title_en}\n\n")
            sections.append(f"**When:** {scenario.when_en}\n\n")
            sections.append(f"**Prompt:** {scenario.prompt_en}\n\n")
            sections.append(f"**Source Skill bundle:** {raw_url}\n\n")
            sections.append(f"**Starter question:** {scenario.question_en}\n\n")
    return "".join(sections)


def catalog_json(locale: str = "en", raw_base_url: str = PUBLIC_RAW_BASE_URL) -> str:
    """Serialize localized public catalog metadata without private paths."""
    language = _content_locale(locale)
    entries = [_public_entry_dict(entry, language, raw_base_url) for entry in CATALOG]
    return json.dumps(
        {"version": 1, "locale": _response_locale(locale), "skills": entries},
        ensure_ascii=False,
        indent=2,
    )


def locale_fields(entry: SkillEntry, locale: str) -> dict[str, str]:
    """Return localized catalog copy with English fallback."""
    language = _content_locale(locale)
    return {
        "group": entry.group if language == "en" else entry.group_vi,
        "title": getattr(entry, f"title_{language}"),
        "summary": getattr(entry, f"summary_{language}"),
        "use_when": getattr(entry, f"use_when_{language}"),
        "best_for": getattr(entry, f"best_for_{language}"),
        "boundary": getattr(entry, f"boundary_{language}"),
    }
