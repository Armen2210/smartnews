from dataclasses import dataclass, field


@dataclass
class PipelineMetrics:
    sources_total: int = 0
    sources_active: int = 0
    entries_found: int = 0
    news_created: int = 0
    duplicates: int = 0
    errors_count: int = 0
    published_at_missing_count: int = 0
    text_empty_count: int = 0
    errors_sample: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        self.errors_count += 1
        if len(self.errors_sample) < 5:
            self.errors_sample.append(message)

    def to_meta(self) -> dict:
        return {
            "sources_total": self.sources_total,
            "sources_active": self.sources_active,
            "entries_found": self.entries_found,
            "news_created": self.news_created,
            "duplicates": self.duplicates,
            "errors_count": self.errors_count,
            "published_at_missing_count": self.published_at_missing_count,
            "text_empty_count": self.text_empty_count,
            "errors_sample": self.errors_sample,
        }