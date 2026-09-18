export default function FallbackBadge({ show, message }) {
  if (!show) return null;
  return (
    <span className="fallback-badge" title={message || 'Using cached or demo data'}>
      Using cached demo data
    </span>
  );
}
