export function Label({ className = "", ...props }) {
  return (
    <label className={`text-sm font-medium ${className}`} {...props} />
  );
}