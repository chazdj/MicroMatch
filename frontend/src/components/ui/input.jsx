import { cn } from "./utils";

export function Input({ className, ...props }) {
  return (
    <input
      className={cn(
        "w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary outline-none",
        className
      )}
      {...props}
    />
  );
}