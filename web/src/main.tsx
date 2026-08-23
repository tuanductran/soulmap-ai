// Atlas Nội Tâm: Bootstrap giữ i18n và Router ở một điểm vào nhẹ, phù hợp static GitHub Pages.
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import "./i18n";
import App from "./App";

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
