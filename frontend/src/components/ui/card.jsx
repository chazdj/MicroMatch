import { cn } from "./utils";

export function Card({ className, ...props }) {
  return (
    <div
      className={cn(
        "bg-white rounded-xl border shadow-sm flex flex-col gap-6",
        className
      )}
      {...props}
    />
  );
}

export function CardHeader({ className, ...props }) {
  return <div className={cn("px-6 pt-6", className)} {...props} />;
}

export function CardContent({ className, ...props }) {
  return <div className={cn("px-6 pb-6", className)} {...props} />;
}

export function CardTitle({ className, ...props }) {
  return <h4 className={cn("text-xl font-semibold", className)} {...props} />;
}

export function CardDescription({ className, ...props }) {
  return (
    <p className={cn("text-sm text-gray-500", className)} {...props} />
  );
}