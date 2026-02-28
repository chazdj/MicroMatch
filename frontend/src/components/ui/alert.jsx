import { cn } from "./utils";

export function Alert({ className = "", ...props }) {
  return (
    <div
      className={cn(
        "bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 text-sm",
        className
      )}
      {...props}
    />
  );
}

export function AlertDescription({ className = "", ...props }) {
  return <div className={cn("", className)} {...props} />;
}