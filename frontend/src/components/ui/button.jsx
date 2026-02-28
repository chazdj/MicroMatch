import { cn } from "./utils";

export function Button({ className, ...props }) {
  return (
    <button
      className={cn(
        "bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 w-full",
        className
      )}
      {...props}
    />
  );
}