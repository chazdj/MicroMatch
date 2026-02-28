import { cn } from "./utils";

export function Input({ className, ...props }) {
  return (
    <input
      className={cn(
        "w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none",
        className
      )}
      {...props}
    />
  );
}