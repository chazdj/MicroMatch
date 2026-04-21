import { cn } from "./utils";

export function Button({ className, ...props }) {
  return (
    <button
      className={cn(
        "bg-primary text-white px-4 py-2 rounded-lg hover:bg-primaryLight transition disabled:opacity-50 w-full",
        className
      )}
      {...props}
    />
  );
}