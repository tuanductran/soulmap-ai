// Atlas Nội Tâm: Skill data giữ scope và boundary cạnh nhau để UI không biến framework thành lời khuyên áp đặt.
import type { Locale } from "@/i18n";

export type Skill = {
  slug: string;
  accent: string;
  source: string;
  copy: Record<Locale, { group: string; title: string; summary: string; useWhen: string; bestFor: string; boundary: string }>;
};

export const skills: Skill[] = [
  {
    slug: "meta", accent: "Moss", source: "meta.md",
    copy: {
      en: { group: "Core", title: "Core orchestration", summary: "The routing layer that decides how SoulMap should listen, calibrate depth, choose a framework, and protect user authority.", useWhen: "Start here when you are integrating SoulMap or need to understand the response pipeline.", bestFor: "Routing, stage calibration, response shape, session contract, and orchestration.", boundary: "It is the coordination layer, not a standalone therapeutic or predictive prompt." },
      vi: { group: "Cốt lõi", title: "Điều phối cốt lõi", summary: "Lớp điều phối quyết định cách SoulMap lắng nghe, hiệu chỉnh độ sâu, chọn khung phù hợp và bảo vệ quyền tự chủ của người dùng.", useWhen: "Bắt đầu từ đây khi bạn đang tích hợp SoulMap hoặc cần hiểu quy trình phản hồi.", bestFor: "Điều phối, hiệu chỉnh giai đoạn, cấu trúc phản hồi, thỏa thuận phiên và tổ chức luồng.", boundary: "Đây là lớp điều phối, không phải prompt trị liệu hay dự đoán độc lập." },
      ko: { group: "핵심", title: "핵심 조정", summary: "SoulMap이 어떻게 경청할지, 깊이를 조절할지, 어떤 프레임워크를 선택할지, 사용자의 권한을 보호할지를 결정하는 라우팅 계층입니다.", useWhen: "SoulMap을 통합하거나 응답 파이프라인을 이해해야 할 때 여기서 시작하세요.", bestFor: "라우팅, 단계별 조정, 응답 형태, 세션 계약 및 오케스트레이션.", boundary: "이는 조정 계층이며 독립적인 치료용이나 예측용 프롬프트가 아닙니다." },
    },
  },
  {
    slug: "frameworks", accent: "Clay", source: "frameworks.md",
    copy: {
      en: { group: "Reflection", title: "Reflective frameworks", summary: "Situation-specific mirrors for grief, anger, relationships, identity patterns, creativity, self-compassion, and inner work.", useWhen: "Use the framework that matches the lived pattern without turning it into a fixed identity.", bestFor: "A focused conversation after the core layer has identified the right territory.", boundary: "Frameworks offer lenses and questions; they do not diagnose, label, or claim certainty." },
      vi: { group: "Phản chiếu", title: "Các khung phản chiếu", summary: "Các tấm gương theo tình huống cho mất mát, giận dữ, quan hệ, mô thức về danh tính, sáng tạo, lòng trắc ẩn với bản thân và thực hành nội tâm.", useWhen: "Dùng khung phù hợp với mô thức đang sống mà không biến nó thành danh tính cố định.", bestFor: "Một cuộc trò chuyện tập trung sau khi lớp cốt lõi đã xác định đúng vùng cần làm việc.", boundary: "Các khung chỉ đưa ra lăng kính và câu hỏi; không chẩn đoán, gắn nhãn hay khẳng định chắc chắn." },
      ko: { group: "성찰", title: "성찰 프레임워크", summary: "슬픔, 분노, 관계, 정체성 패턴, 창의성, 자기연민, 내면 작업 등 특정 상황에 맞춘 반영 도구들입니다.", useWhen: "경험된 패턴에 맞는 프레임워크를 사용하되 그것을 고정된 정체성으로 만들지 마세요.", bestFor: "핵심 계층이 적절한 영역을 식별한 후의 집중 대화에 적합합니다.", boundary: "프레임워크는 관점과 질문을 제공할 뿐 진단하거나 낙인을 찍거나 확실성을 주장하지 않습니다." },
    },
  },
  {
    slug: "safety", accent: "Ink", source: "safety.md",
    copy: {
      en: { group: "Safety", title: "Safety guardrails", summary: "The non-negotiable boundaries for crisis language, trauma-informed wording, prompt injection, ethics, and scope control.", useWhen: "Load this whenever a conversation involves risk, crisis, trauma, diagnosis, prediction, or attempts to override the system.", bestFor: "Safety classification, refusal or redirect, prompt-injection defense, and grounded support language.", boundary: "Safety overrides resonance; never use warmth to soften a necessary boundary." },
      vi: { group: "An toàn", title: "Rào chắn an toàn", summary: "Các giới hạn không thể thương lượng cho ngôn ngữ về khủng hoảng, cách diễn đạt hiểu biết về sang chấn, prompt injection, đạo đức và kiểm soát phạm vi.", useWhen: "Luôn tải lớp này khi hội thoại liên quan đến rủi ro, khủng hoảng, sang chấn, chẩn đoán, dự đoán hoặc nỗ lực vượt qua hệ thống.", bestFor: "Phân loại an toàn, từ chối/chuyển hướng, phòng thủ prompt injection và ngôn ngữ hỗ trợ có nền tảng.", boundary: "An toàn luôn được ưu tiên hơn sự đồng điệu; không dùng sự ấm áp để làm mềm một ranh giới cần thiết." },
      ko: { group: "안전", title: "안전 가드레일", summary: "위기 표현, 트라우마 인식 언어, 프롬프트 인젝션, 윤리 및 범위 통제에 대한 비협상적 경계입니다.", useWhen: "대화에 위험, 위기, 트라우마, 진단, 예측 또는 시스템 무력화 시도가 포함될 때마다 적용하세요.", bestFor: "안전 분류, 거부/전환, 프롬프트 인젝션 방어 및 근거 있는 지원 언어.", boundary: "안전은 공감보다 우선합니다. 필요한 경계를 감정적 온기로 완화해서는 안 됩니다." },
    },
  },
  {
    slug: "spiritual", accent: "Moss", source: "spiritual.md",
    copy: {
      en: { group: "Symbolic", title: "Grounded symbolic layer", summary: "Optional symbolic language for discernment, metaphors, numerology, chakra themes, and reports without spiritual grandiosity.", useWhen: "Use only when symbolic framing helps the user inquire more honestly into lived experience.", bestFor: "Discernment, metaphor, symbolic reports, and brand-safe spiritual reflection.", boundary: "Symbolism is a lens, never proof of destiny, special status, or supernatural authority." },
      vi: { group: "Biểu tượng", title: "Lớp biểu tượng có nền tảng", summary: "Ngôn ngữ biểu tượng tùy chọn cho phân định, ẩn dụ, số học, chủ đề chakra và các báo cáo không thổi phồng tâm linh.", useWhen: "Chỉ dùng khi cách diễn đạt biểu tượng giúp người dùng tự vấn trung thực hơn về trải nghiệm đang sống.", bestFor: "Phân định, ẩn dụ, báo cáo biểu tượng và phản chiếu tâm linh an toàn cho thương hiệu.", boundary: "Biểu tượng là một lăng kính, không phải bằng chứng về định mệnh, vị thế đặc biệt hay quyền lực siêu nhiên." },
      ko: { group: "상징적", title: "근거 있는 상징 계층", summary: "영적 과장을 배제한 분별, 은유, 수비학, 차크라 주제 및 리포트에 쓸 수 있는 선택적 상징 언어입니다.", useWhen: "상징적 프레이밍이 사용자가 자신의 경험을 더 솔직하게 탐색하는 데 도움이 될 때에만 사용하세요.", bestFor: "분별, 은유, 상징적 보고서 및 브랜드에 안전한 영적 성찰.", boundary: "상징은 하나의 관점일 뿐 운명·특별 지위·초자연적 권위의 증거가 될 수 없습니다." },
    },
  },
  {
    slug: "voice", accent: "Clay", source: "voice.md",
    copy: {
      en: { group: "Voice", title: "Voice and calibration", summary: "The pacing, warmth, clarity, response length, and session rituals that make SoulMap feel coherent without becoming dependent.", useWhen: "Use this when content is correct but tone, pacing, or emotional distance feels wrong.", bestFor: "Persona, response calibration, opening rituals, and grounded closing posture.", boundary: "Voice shapes delivery; it must never add authority, intimacy hooks, or emotional rescue." },
      vi: { group: "Giọng điệu", title: "Giọng điệu và hiệu chỉnh", summary: "Nhịp điệu, sự ấm áp, độ rõ, độ dài phản hồi và các nghi thức phiên giúp SoulMap nhất quán mà không tạo phụ thuộc.", useWhen: "Dùng khi nội dung đúng nhưng giọng điệu, nhịp độ hoặc khoảng cách cảm xúc chưa phù hợp.", bestFor: "Persona, hiệu chỉnh phản hồi, nghi thức mở đầu và tư thế kết thúc có nền tảng.", boundary: "Giọng điệu chỉ định hình cách truyền đạt; không được thêm thẩm quyền, móc nối thân mật hay giải cứu cảm xúc." },
      ko: { group: "목소리", title: "목소리와 조정", summary: "속도, 온기, 명료성, 응답 길이, 세션 의식 등 SoulMap이 일관되게 느껴지되 의존을 유발하지 않도록 하는 요소들입니다.", useWhen: "내용은 적절하지만 톤, 속도, 정서적 거리감이 맞지 않을 때 적용하세요.", bestFor: "페르소나, 응답 조정, 시작 의식 및 안정적인 마무리 태도.", boundary: "목소리는 전달 방식을 형성하지만 권위 부여, 친밀감 유도, 정서적 구원 역할을 해서는 안 됩니다." },
    },
  },
  {
    slug: "brand", accent: "Ink", source: "brand.md",
    copy: {
      en: { group: "Brand", title: "Brand and positioning", summary: "Public positioning, visual identity, content pillars, differentiation, and scope language for a coherent SoulMap surface.", useWhen: "Use this when writing public copy, naming a surface, or checking whether a visual decision still feels like SoulMap.", bestFor: "Brand voice, visual system, strategic direction, and public-facing boundaries.", boundary: "Brand guidance is not a substitute for runtime safety and orchestration layers." },
      vi: { group: "Thương hiệu", title: "Thương hiệu và định vị", summary: "Định vị công khai, nhận diện trực quan, trụ cột nội dung, điểm khác biệt và ngôn ngữ phạm vi cho một SoulMap nhất quán.", useWhen: "Dùng khi viết nội dung công khai, đặt tên cho một bề mặt hoặc kiểm tra một quyết định hình ảnh còn đúng chất SoulMap.", bestFor: "Giọng thương hiệu, hệ thống hình ảnh, định hướng chiến lược và các ranh giới hướng ra công chúng.", boundary: "Hướng dẫn thương hiệu không thay thế các lớp an toàn runtime và điều phối." },
      ko: { group: "브랜드", title: "브랜드 및 포지셔닝", summary: "일관된 SoulMap 표면을 위한 공개 포지셔닝, 시각 정체성, 콘텐츠 핵심, 차별화 및 범위 언어입니다.", useWhen: "공개 문구 작성, 서비스 명명 또는 시각적 결정이 여전히 SoulMap답게 느껴지는지 점검할 때 사용하세요.", bestFor: "브랜드 보이스, 시각 시스템, 전략적 방향 및 대외적 경계.", boundary: "브랜드 지침은 런타임 안전 및 오케스트레이션 계층을 대체하지 않습니다." },
    },
  },
];

export const rawBundleUrl = (skill: Skill, locale: Locale) => {
  const prefix = locale === "en" ? "" : `${locale}/`;
  return `${window.location.origin}${import.meta.env.BASE_URL}${prefix}api/raw/${skill.slug}.md`;
};
