// Atlas Nội Tâm: Nội dung giao diện được tách khỏi component, ưu tiên ngôn ngữ rõ ràng và quyền tự chủ.
import i18n from "i18next";
import { initReactI18next } from "react-i18next";

export const supportedLocales = ["en", "vi", "ko"] as const;
export type Locale = (typeof supportedLocales)[number];

const resources = {
  en: {
    translation: {
      nav: { home: "Atlas", how: "How it works", boundaries: "Boundaries", notes: "Notes", skills: "Skill layers", more: "More", primaryLabel: "Primary navigation", scrollMore: "Scroll navigation right", about: "About", faq: "FAQ", download: "Download", privacy: "Privacy" },
      common: { language: "Language", explore: "Explore layers", inspect: "Inspect", close: "Close", source: "Open source", copy: "Copy prompt", copied: "Copied", coordinates: "Coordinates", repository: "Repository" },
      home: {
        eyebrow: "A reflective field guide",
        title: "Find the next honest coordinate.",
        body: "SoulMap is a structured collection of reflective layers. It helps you notice what is happening without deciding what it must mean.",
        primary: "Browse the layers",
        secondary: "Read the boundaries",
        mapTitle: "Three ways to orient",
        mapBody: "Choose a layer for the kind of attention you need. No layer asks you to hand over authorship.",
        steps: ["Name the pattern", "Choose a lens", "Keep your authorship"],
        fieldTitle: "A system with room to breathe.",
        fieldBody: "SoulMap keeps safety, reflection, language, and public-facing guidance in distinct layers so each can be used without pretending to be the whole answer.",
      },
      skills: {
        eyebrow: "The public skill catalog",
        title: "Choose a layer, not an answer.",
        body: "Start with the territory that is actually present. Each layer names its scope and its boundary before you use it.",
        search: "Search by layer, use case, or boundary…",
        count: "layers in view",
        useWhen: "Use this when",
        boundary: "Boundary",
        bestFor: "Best for",
        openPrompt: "Use a starter prompt",
        dialogTitle: "Choose how to continue",
        dialogBody: "Copy the prompt first, then open the AI tool you use. Provider pages may require sign-in and do not rely on fragile prefilled links.",
        chooseProvider: "Open after copying",
        raw: "Read the canonical source",
        promptLanguage: "This starter prompt stays in English so AI tools receive the canonical wording.",
        noResults: "No layers match this coordinate. Try a broader word or clear the search.",
      },
      info: {
        about: { eyebrow: "Scope and boundaries", title: "A mirror, not an authority.", body: "SoulMap is a reflective framework for language, structure, and careful inquiry. It is not a therapist, a diagnostic system, a crisis service, or a source of prediction." },
        faq: { eyebrow: "Practical answers", title: "What this surface can and cannot do.", body: "The website presents public skills and their boundaries. It does not collect a private session history or make decisions in place of a person." },
        note: "SoulMap and Soulmate remain domain artifacts and local developer tooling. This static website does not operate an AI host or infer personal outcomes.",
      },
      footer: "A mirror, not a guru.",
    },
  },
  vi: {
    translation: {
      nav: { home: "Bản đồ", how: "Cách hoạt động", boundaries: "Ranh giới", notes: "Ghi chú", skills: "Các lớp Skill", more: "Thêm", primaryLabel: "Điều hướng chính", scrollMore: "Cuộn sang phải để xem thêm mục", about: "Giới thiệu", faq: "FAQ", download: "Tải về", privacy: "Quyền riêng tư" },
      common: { language: "Ngôn ngữ", explore: "Khám phá các lớp", inspect: "Xem kỹ", close: "Đóng", source: "Mở nguồn", copy: "Sao chép prompt", copied: "Đã sao chép", coordinates: "Tọa độ", repository: "Kho mã nguồn" },
      home: {
        eyebrow: "Field guide để phản chiếu",
        title: "Tìm tọa độ chân thật tiếp theo.",
        body: "SoulMap là một tập hợp có cấu trúc các lớp phản chiếu. Nó giúp bạn nhận ra điều đang diễn ra mà không quyết định thay ý nghĩa của nó.",
        primary: "Xem các lớp",
        secondary: "Đọc ranh giới",
        mapTitle: "Ba cách để định vị",
        mapBody: "Chọn lớp phù hợp với kiểu chú ý bạn cần. Không lớp nào đòi bạn giao quyền làm chủ.",
        steps: ["Gọi tên mô thức", "Chọn một lăng kính", "Giữ quyền làm chủ"],
        fieldTitle: "Một hệ thống có khoảng thở.",
        fieldBody: "SoulMap tách an toàn, phản chiếu, ngôn ngữ và hướng dẫn công khai thành các lớp riêng để mỗi lớp có thể được dùng mà không giả làm toàn bộ câu trả lời.",
      },
      skills: {
        eyebrow: "Danh mục Skill công khai",
        title: "Chọn một lớp, không phải một đáp án.",
        body: "Bắt đầu bằng vùng đang hiện diện thật sự. Mỗi lớp nêu phạm vi và ranh giới trước khi được sử dụng.",
        search: "Tìm theo lớp, tình huống hoặc ranh giới…",
        count: "lớp đang hiển thị",
        useWhen: "Dùng khi",
        boundary: "Ranh giới",
        bestFor: "Phù hợp nhất với",
        openPrompt: "Dùng prompt bắt đầu",
        dialogTitle: "Chọn cách tiếp tục",
        dialogBody: "Hãy sao chép prompt trước, rồi mở công cụ AI bạn dùng. Trang nhà cung cấp có thể cần đăng nhập; giao diện không dựa vào link prefill dễ hỏng.",
        chooseProvider: "Mở sau khi sao chép",
        raw: "Đọc nguồn chuẩn",
        promptLanguage: "Prompt khởi đầu được giữ bằng tiếng Anh để công cụ AI nhận đúng wording chuẩn.",
        noResults: "Không có lớp phù hợp với tọa độ này. Hãy thử từ rộng hơn hoặc xóa nội dung tìm kiếm.",
      },
      info: {
        about: { eyebrow: "Phạm vi và ranh giới", title: "Một tấm gương, không phải thẩm quyền.", body: "SoulMap là framework phản chiếu cho ngôn ngữ, cấu trúc và sự tự vấn cẩn trọng. Nó không phải nhà trị liệu, hệ thống chẩn đoán, dịch vụ khủng hoảng hay nguồn dự đoán." },
        faq: { eyebrow: "Câu trả lời thực tế", title: "Bề mặt này có thể và không thể làm gì.", body: "Website trình bày các Skill công khai và ranh giới của chúng. Nó không thu thập lịch sử phiên riêng tư hoặc quyết định thay con người." },
        note: "SoulMap và Soulmate vẫn là domain artifacts và công cụ phát triển cục bộ. Website tĩnh này không vận hành AI host hoặc suy diễn kết quả cá nhân.",
      },
      footer: "Một tấm gương, không phải đạo sư.",
    },
  },
  ko: {
    translation: {
      nav: { home: "아틀라스", how: "작동 방식", boundaries: "경계", notes: "노트", skills: "Skill 계층", more: "더 보기", primaryLabel: "주요 탐색", scrollMore: "더 많은 탐색 항목을 보려면 오른쪽으로 스크롤", about: "소개", faq: "FAQ", download: "다운로드", privacy: "개인정보" },
      common: { language: "언어", explore: "계층 살펴보기", inspect: "자세히 보기", close: "닫기", source: "원문 열기", copy: "프롬프트 복사", copied: "복사됨", coordinates: "좌표", repository: "저장소" },
      home: {
        eyebrow: "성찰을 위한 필드 가이드",
        title: "다음의 정직한 좌표를 찾으세요.",
        body: "SoulMap은 성찰 계층을 구조화한 모음입니다. 무엇을 의미해야 하는지 결정하지 않고, 지금 일어나는 일을 알아차리도록 돕습니다.",
        primary: "계층 둘러보기",
        secondary: "경계 읽기",
        mapTitle: "방향을 잡는 세 가지 방법",
        mapBody: "필요한 주의의 방식에 맞는 계층을 선택하세요. 어떤 계층도 해석의 주도권을 넘기라고 요구하지 않습니다.",
        steps: ["패턴 이름 붙이기", "관점 선택하기", "주도권 유지하기"],
        fieldTitle: "숨 쉴 여백이 있는 시스템.",
        fieldBody: "SoulMap은 안전, 성찰, 언어, 공개 안내를 구분된 계층으로 두어 어느 하나도 전체 답인 척하지 않도록 합니다.",
      },
      skills: {
        eyebrow: "공개 Skill 카탈로그",
        title: "답이 아니라 계층을 고르세요.",
        body: "실제로 존재하는 영역에서 시작하세요. 각 계층은 사용 전에 범위와 경계를 밝힙니다.",
        search: "계층, 사용 사례 또는 경계로 검색…",
        count: "개 계층 표시 중",
        useWhen: "사용 시점",
        boundary: "경계",
        bestFor: "적합한 상황",
        openPrompt: "시작 프롬프트 사용",
        dialogTitle: "계속할 방법 선택",
        dialogBody: "먼저 프롬프트를 복사한 다음 사용하는 AI 도구를 여세요. 공급자 페이지에는 로그인이 필요할 수 있으며, 깨지기 쉬운 prefill 링크에 의존하지 않습니다.",
        chooseProvider: "복사 후 열기",
        raw: "정식 원문 읽기",
        promptLanguage: "AI 도구에 canonical wording을 전달하기 위해 시작 프롬프트는 영어로 유지됩니다.",
        noResults: "이 좌표와 일치하는 계층이 없습니다. 더 넓은 단어를 사용하거나 검색어를 지워 보세요.",
      },
      info: {
        about: { eyebrow: "범위와 경계", title: "권위가 아닌 거울.", body: "SoulMap은 언어, 구조, 신중한 탐구를 위한 성찰 프레임워크입니다. 치료사, 진단 시스템, 위기 서비스 또는 예측의 원천이 아닙니다." },
        faq: { eyebrow: "실용적인 답변", title: "이 표면이 할 수 있는 것과 할 수 없는 것.", body: "이 웹사이트는 공개 Skill과 그 경계를 제시합니다. 개인 세션 기록을 수집하거나 사람을 대신하여 결정하지 않습니다." },
        note: "SoulMap과 Soulmate는 도메인 아티팩트와 로컬 개발 도구로 유지됩니다. 이 정적 웹사이트는 AI 호스트를 운영하거나 개인적 결과를 추론하지 않습니다.",
      },
      footer: "권위가 아닌 거울.",
    },
  },
} as const;

i18n.use(initReactI18next).init({
  resources,
  lng: "en",
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

export default i18n;
