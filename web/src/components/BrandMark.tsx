// Atlas Nội Tâm: Compass mark là tín hiệu định vị nhỏ, không thay thế bằng icon thư viện chung chung.
export function BrandMark({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-3 text-[#122b2c]">
      <img
        className="size-10 shrink-0"
        src={`${import.meta.env.BASE_URL}images/compass-mark.webp`}
        alt=""
      />
      {!compact && (
        <span className="font-serif text-xl font-semibold tracking-[-0.04em]">SoulMap AI</span>
      )}
    </div>
  );
}
