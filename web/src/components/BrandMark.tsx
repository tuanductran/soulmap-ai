// Bản đồ Biên Độ: Compass mark và wordmark được cân theo cùng baseline để masthead không lấn át reading field.
export function BrandMark({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-2.5 text-[#173837]">
      <img
        className="size-8 shrink-0 sm:size-9"
        src={`${import.meta.env.BASE_URL}images/compass-mark.webp`}
        alt=""
      />
      {!compact && (
        <span className="font-serif text-lg font-semibold tracking-[-0.04em] sm:text-xl">
          SoulMap AI
        </span>
      )}
    </div>
  );
}
