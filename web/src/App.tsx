// Atlas Nội Tâm: App chỉ chịu trách nhiệm cung cấp TanStack Router, không trộn domain/runtime Python vào frontend static.
import { RouterProvider } from "@tanstack/react-router";
import { router } from "@/router";

export default function App() {
  return <RouterProvider router={router} />;
}
