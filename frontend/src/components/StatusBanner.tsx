interface StatusBannerProps {
  loading?: boolean;
  loadingText?: string;
  error?: string | null;
}

export function StatusBanner({ loading, loadingText, error }: StatusBannerProps) {
  if (loading) {
    return (
      <div className="status-banner status-banner--loading" role="status">
        {loadingText ?? "Loading..."}
      </div>
    );
  }

  if (error) {
    return (
      <div className="status-banner status-banner--error" role="alert">
        {error}
      </div>
    );
  }

  return null;
}
