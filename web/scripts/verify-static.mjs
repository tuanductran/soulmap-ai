// Atlas Nội Tâm: fail-closed static verification, bảo đảm Pages artifact chứa routes fallback, raw bundle và không rò storage preview URL.
import { access, readFile, readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dist = path.join(root, "dist");
const required = ["index.html", "404.html", "api/raw/meta.md", "vi/api/raw/frameworks.md", "ko/api/raw/safety.md", "images/hero.webp", "images/compass-mark.webp"];
for (const entry of required) await access(path.join(dist, entry));
const html = await readFile(path.join(dist, "index.html"), "utf8");
if (html.includes("/manus-storage/") || html.includes("src/web")) throw new Error("Static output contains a preview-only or legacy Python web reference.");
const assets = await readdir(path.join(dist, "assets"));
if (!assets.some((name) => name.endsWith(".js")) || !assets.some((name) => name.endsWith(".css"))) throw new Error("Static output is missing bundled JS or CSS.");
