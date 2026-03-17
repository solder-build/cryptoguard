export default function Footer() {
  return (
    <footer className="border-t border-border py-8 mt-auto">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="text-text-secondary text-sm">
          CryptoGuard &mdash; Multi-Agent Crypto Threat Intelligence
        </p>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface border border-border">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="#0069FF" strokeWidth="2" />
            <circle cx="12" cy="12" r="4" fill="#0069FF" />
          </svg>
          <span className="text-xs text-text-secondary">
            Powered by DigitalOcean Gradient AI
          </span>
        </div>
      </div>
    </footer>
  );
}
