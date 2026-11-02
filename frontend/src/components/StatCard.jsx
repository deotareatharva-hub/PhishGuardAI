
export default function StatCard({
  title,
  value,
  description,
  icon: Icon,
  accent = "cyan",
}) {
  return (
    <article className={`stat-card accent-${accent}`}>
      <div className="stat-card-top">
        <span>{title}</span>

        <div className="stat-icon">
          <Icon size={21} strokeWidth={1.8} />
        </div>
      </div>

      <h3>{value}</h3>
      <p>{description}</p>
    </article>
  );
}
