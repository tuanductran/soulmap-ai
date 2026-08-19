"""Public SoulMap Skill catalog metadata and raw Markdown bundle helpers."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from soulmap.web.prompt_pack import scenarios_for

PUBLIC_RAW_BASE_URL = "https://tuanductran.github.io/soulmap-ai"


@dataclass(frozen=True)
class SkillEntry:
    """Public-facing metadata for one importable SoulMap capability group."""

    slug: str
    group: str
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
        title_en="Core orchestration",
        title_vi="Điều phối cốt lõi",
        summary_en="The routing layer that decides how SoulMap should listen, calibrate depth, choose a framework, and protect user authority.",
        summary_vi="Lớp điều phối quyết định SoulMap nên lắng nghe, hiệu chỉnh độ sâu, chọn framework và bảo vệ quyền tự chủ của người dùng như thế nào.",
        use_when_en="Start here when you are integrating SoulMap or need to understand the response pipeline.",
        use_when_vi="Bắt đầu ở đây khi tích hợp SoulMap hoặc cần hiểu pipeline phản hồi.",
        best_for_en="Routing, stage calibration, response shape, session contract, and orchestration.",
        best_for_vi="Routing, hiệu chỉnh giai đoạn, cấu trúc phản hồi, session contract và orchestration.",
        boundary_en="It is the coordination layer, not a standalone therapeutic or predictive prompt.",
        boundary_vi="Đây là lớp điều phối, không phải prompt trị liệu hay dự đoán độc lập.",
        directory="meta",
        featured_file="SKILL.md",
    ),
    SkillEntry(
        slug="frameworks",
        group="Reflection",
        title_en="Reflective frameworks",
        title_vi="Các framework phản chiếu",
        summary_en="Situation-specific mirrors for grief, anger, relationships, identity patterns, creativity, self-compassion, and inner work.",
        summary_vi="Các mirror theo tình huống cho grief, anger, relationships, identity patterns, creativity, self-compassion và inner work.",
        use_when_en="Use the framework that matches the lived pattern without turning it into a fixed identity.",
        use_when_vi="Dùng framework khớp với pattern đang sống mà không biến nó thành một danh tính cố định.",
        best_for_en="A focused conversation after the core layer has identified the right territory.",
        best_for_vi="Một cuộc trò chuyện tập trung sau khi lớp cốt lõi đã xác định đúng vùng cần làm việc.",
        boundary_en="Frameworks offer lenses and questions; they do not diagnose, label, or claim certainty.",
        boundary_vi="Framework chỉ đưa ra lăng kính và câu hỏi; không chẩn đoán, gắn nhãn hay khẳng định chắc chắn.",
        directory="frameworks",
        featured_file="SKILL.md",
    ),
    SkillEntry(
        slug="safety",
        group="Safety",
        title_en="Safety guardrails",
        title_vi="Guardrail an toàn",
        summary_en="The non-negotiable boundaries for crisis language, trauma-informed wording, prompt injection, ethics, and scope control.",
        summary_vi="Các giới hạn không thương lượng cho ngôn ngữ crisis, trauma-informed, prompt injection, ethics và kiểm soát phạm vi.",
        use_when_en="Load this whenever a conversation involves risk, crisis, trauma, diagnosis, prediction, or attempts to override the system.",
        use_when_vi="Luôn load khi hội thoại liên quan đến risk, crisis, trauma, diagnosis, prediction hoặc nỗ lực vượt guardrail.",
        best_for_en="Safety classification, refusal/redirect, prompt-injection defense, and grounded support language.",
        best_for_vi="Phân loại safety, refusal/redirect, phòng thủ prompt injection và ngôn ngữ hỗ trợ grounded.",
        boundary_en="Safety overrides resonance; never use warmth to soften a necessary boundary.",
        boundary_vi="Safety luôn ưu tiên hơn resonance; không dùng sự ấm áp để làm mềm một giới hạn cần thiết.",
        directory="safety",
        featured_file="SKILL.md",
    ),
    SkillEntry(
        slug="spiritual",
        group="Symbolic",
        title_en="Grounded symbolic layer",
        title_vi="Lớp biểu tượng grounded",
        summary_en="Optional symbolic language for discernment, metaphors, numerology, chakra themes, and reports without spiritual grandiosity.",
        summary_vi="Ngôn ngữ biểu tượng tùy chọn cho discernment, metaphor, numerology, chakra và report mà không thổi phồng tâm linh.",
        use_when_en="Use only when symbolic framing helps the user inquire more honestly into lived experience.",
        use_when_vi="Chỉ dùng khi framing biểu tượng giúp người dùng nhìn thành thật hơn vào trải nghiệm đang sống.",
        best_for_en="Discernment, metaphor, symbolic reports, and brand-safe spiritual reflection.",
        best_for_vi="Discernment, metaphor, symbolic report và phản chiếu tâm linh an toàn cho thương hiệu.",
        boundary_en="Symbolism is a lens, never proof of destiny, special status, or supernatural authority.",
        boundary_vi="Biểu tượng là một lăng kính, không phải bằng chứng về định mệnh, vị thế đặc biệt hay quyền lực siêu nhiên.",
        directory="spiritual",
        featured_file="SKILL.md",
    ),
    SkillEntry(
        slug="voice",
        group="Voice",
        title_en="Voice and calibration",
        title_vi="Voice và hiệu chỉnh",
        summary_en="The pacing, warmth, clarity, response length, and session rituals that make SoulMap feel coherent without becoming dependent.",
        summary_vi="Nhịp điệu, sự ấm áp, độ rõ, độ dài phản hồi và ritual giúp SoulMap nhất quán mà không tạo dependency.",
        use_when_en="Use this when the content is correct but the tone, pacing, or emotional distance feels wrong.",
        use_when_vi="Dùng khi nội dung đúng nhưng tone, nhịp hoặc khoảng cách cảm xúc chưa phù hợp.",
        best_for_en="Persona, response calibration, opening rituals, and grounded closing posture.",
        best_for_vi="Persona, hiệu chỉnh phản hồi, opening ritual và closing posture grounded.",
        boundary_en="Voice shapes delivery; it must never add authority, intimacy hooks, or emotional rescue.",
        boundary_vi="Voice chỉ định hình cách truyền đạt; không được thêm authority, intimacy hook hay emotional rescue.",
        directory="voice",
        featured_file="SKILL.md",
    ),
    SkillEntry(
        slug="brand",
        group="Brand",
        title_en="Brand and positioning",
        title_vi="Brand và positioning",
        summary_en="Public positioning, visual identity, content pillars, differentiation, and scope language for a coherent SoulMap surface.",
        summary_vi="Positioning công khai, visual identity, content pillar, differentiation và scope language cho surface nhất quán.",
        use_when_en="Use this when writing public copy, naming a surface, or checking whether a visual decision still feels like SoulMap.",
        use_when_vi="Dùng khi viết copy công khai, đặt tên surface hoặc kiểm tra một quyết định visual còn đúng chất SoulMap không.",
        best_for_en="Brand voice, visual system, strategic direction, and public-facing boundaries.",
        best_for_vi="Brand voice, visual system, strategic direction và boundary hướng ra công chúng.",
        boundary_en="Brand guidance is not a substitute for the runtime safety and orchestration layers.",
        boundary_vi="Brand guidance không thay thế runtime safety và orchestration layer.",
        directory="brand",
        featured_file="visual-identity.md",
    ),
)

_BY_SLUG = {entry.slug: entry for entry in CATALOG}


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
    language = "vi" if locale == "vi" else "en"
    entries = []
    for entry in CATALOG:
        fields = locale_fields(entry, language)
        entries.append(
            {
                "slug": entry.slug,
                "group": entry.group,
                **fields,
                "raw_path": f"/api/raw/{entry.slug}.md",
                "raw_url": f"{raw_base_url.rstrip('/')}/api/raw/{entry.slug}.md"
                if raw_base_url
                else "",
                "featured_file": entry.featured_file,
                "prompt_scenarios": [
                    scenario.localized(language)
                    for scenario in scenarios_for(entry.slug)
                ],
            }
        )
    return json.dumps(
        {"version": 1, "locale": language, "skills": entries},
        ensure_ascii=False,
        indent=2,
    )


def locale_fields(entry: SkillEntry, locale: str) -> dict[str, str]:
    """Return localized catalog copy with English fallback."""
    language = "vi" if locale == "vi" else "en"
    return {
        "title": getattr(entry, f"title_{language}"),
        "summary": getattr(entry, f"summary_{language}"),
        "use_when": getattr(entry, f"use_when_{language}"),
        "best_for": getattr(entry, f"best_for_{language}"),
        "boundary": getattr(entry, f"boundary_{language}"),
    }
