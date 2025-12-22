//! Analytics Dashboard
//!
//! Real-time performance and usage analytics.
//! Features: metrics charts, query performance, storage stats.

use crate::theme::*;
use crate::types::{ActivityEntry, ActivityType, AnalyticsMetrics, MetricsSnapshot, QueryLogEntry};
use chrono::Local;
use eframe::egui::{self, Color32, Pos2, Rect, RichText, Rounding, Stroke, Vec2};
use std::collections::VecDeque;
use std::time::{Duration, Instant};
use sutra_storage::ConcurrentMemory;

/// Maximum history entries to keep
const MAX_HISTORY: usize = 1440; // 24 hours at 1 per minute
const MAX_ACTIVITY: usize = 100;
const MAX_QUERIES: usize = 200;

/// Analytics Dashboard
pub struct AnalyticsDashboard {
    pub metrics: AnalyticsMetrics,
    pub history: VecDeque<MetricsSnapshot>,
    pub activity_log: VecDeque<ActivityEntry>,
    pub query_log: VecDeque<QueryLogEntry>,

    // Time range selection
    pub time_range: TimeRange,

    // Query latency tracking
    latency_samples: VecDeque<f32>,

    // Top queries
    pub top_queries: Vec<(String, usize)>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum TimeRange {
    LastHour,
    #[default]
    Last24Hours,
    LastWeek,
    AllTime,
}

impl Default for AnalyticsDashboard {
    fn default() -> Self {
        Self {
            metrics: AnalyticsMetrics::default(),
            history: VecDeque::with_capacity(MAX_HISTORY),
            activity_log: VecDeque::with_capacity(MAX_ACTIVITY),
            query_log: VecDeque::with_capacity(MAX_QUERIES),
            time_range: TimeRange::Last24Hours,
            latency_samples: VecDeque::with_capacity(100),
            top_queries: Vec::new(),
        }
    }
}

impl AnalyticsDashboard {
    /// Update metrics from storage
    pub fn update(&mut self, storage: &ConcurrentMemory) {
        let stats = storage.stats();
        let hnsw = storage.hnsw_stats();

        self.metrics.total_concepts = stats.snapshot.concept_count;
        self.metrics.total_edges = stats.snapshot.edge_count;
        self.metrics.hnsw_indexed = hnsw.indexed_vectors;

        if stats.snapshot.concept_count > 0 {
            self.metrics.hnsw_coverage =
                hnsw.indexed_vectors as f32 / stats.snapshot.concept_count as f32;
        }

        // Calculate latency percentiles
        if !self.latency_samples.is_empty() {
            let mut sorted: Vec<f32> = self.latency_samples.iter().cloned().collect();
            // Phase 3: Safe comparison (handles NaN gracefully)
            sorted.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));

            self.metrics.avg_query_latency_ms = sorted.iter().sum::<f32>() / sorted.len() as f32;
            self.metrics.p95_query_latency_ms = sorted
                .get((sorted.len() as f32 * 0.95) as usize)
                .copied()
                .unwrap_or(0.0);
            self.metrics.p99_query_latency_ms = sorted
                .get((sorted.len() as f32 * 0.99) as usize)
                .copied()
                .unwrap_or(0.0);
        }

        // Add history snapshot
        self.history.push_back(MetricsSnapshot {
            timestamp: Instant::now(),
            concept_count: stats.snapshot.concept_count,
            query_latency_ms: self.metrics.avg_query_latency_ms,
        });

        if self.history.len() > MAX_HISTORY {
            self.history.pop_front();
        }

        // Calculate top queries
        self.calculate_top_queries();
    }

    /// Record a query for analytics
    pub fn record_query(&mut self, query: &str, duration: Duration, results: usize) {
        let duration_ms = duration.as_millis() as f32;

        self.latency_samples.push_back(duration_ms);
        if self.latency_samples.len() > 100 {
            self.latency_samples.pop_front();
        }

        self.query_log.push_back(QueryLogEntry {
            timestamp: Instant::now(),
            query: query.to_string(),
            duration_ms: duration.as_millis() as u64,
            results_count: results,
        });

        if self.query_log.len() > MAX_QUERIES {
            self.query_log.pop_front();
        }

        self.metrics.queries_today += 1;

        // Add to activity log
        self.log_activity(
            ActivityType::Query,
            query.to_string(),
            Some(duration.as_millis() as u64),
        );
    }

    /// Record a learning event
    pub fn record_learn(&mut self, content: &str) {
        self.metrics.concepts_today += 1;
        self.metrics.concepts_this_hour += 1;
        self.log_activity(ActivityType::Learn, content.to_string(), None);
    }

    /// Log an activity
    pub fn log_activity(
        &mut self,
        activity_type: ActivityType,
        description: String,
        duration_ms: Option<u64>,
    ) {
        self.activity_log.push_back(ActivityEntry {
            timestamp: Local::now(),
            activity_type,
            description,
            duration_ms,
        });

        if self.activity_log.len() > MAX_ACTIVITY {
            self.activity_log.pop_front();
        }
    }

    /// Calculate top queries by frequency
    fn calculate_top_queries(&mut self) {
        use std::collections::HashMap;

        let mut counts: HashMap<String, usize> = HashMap::new();
        for entry in &self.query_log {
            // Normalize query (lowercase, trim)
            let normalized = entry.query.to_lowercase().trim().to_string();
            if !normalized.is_empty() {
                *counts.entry(normalized).or_default() += 1;
            }
        }

        let mut sorted: Vec<_> = counts.into_iter().collect();
        sorted.sort_by(|a, b| b.1.cmp(&a.1));

        self.top_queries = sorted.into_iter().take(10).collect();
    }

    /// Render the dashboard
    pub fn ui(&mut self, ui: &mut egui::Ui) -> Option<AnalyticsAction> {
        let mut action = None;

        ui.vertical(|ui| {
            // Header
            self.render_header(ui, &mut action);

            ui.add_space(16.0);

            // Main stats grid
            ui.horizontal(|ui| {
                ui.vertical(|ui| {
                    ui.set_width(ui.available_width() * 0.5);
                    self.render_knowledge_growth(ui);
                    ui.add_space(16.0);
                    self.render_query_performance(ui);
                });

                ui.vertical(|ui| {
                    self.render_learning_activity(ui);
                    ui.add_space(16.0);
                    self.render_storage_stats(ui);
                });
            });

            ui.add_space(16.0);

            // Bottom row
            ui.horizontal(|ui| {
                ui.vertical(|ui| {
                    ui.set_width(ui.available_width() * 0.5);
                    self.render_top_queries(ui);
                });

                ui.vertical(|ui| {
                    self.render_hnsw_health(ui);
                });
            });

            ui.add_space(16.0);

            // Activity timeline
            self.render_activity_timeline(ui);
        });

        action
    }

    fn render_header(&mut self, ui: &mut egui::Ui, action: &mut Option<AnalyticsAction>) {
        ui.horizontal(|ui| {
            ui.label(RichText::new("📊").size(20.0));
            ui.add_space(4.0);
            ui.label(
                RichText::new("Analytics Dashboard")
                    .size(22.0)
                    .color(TEXT_PRIMARY)
                    .strong(),
            );

            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                // Time range selector
                egui::ComboBox::from_id_salt("time_range")
                    .selected_text(match self.time_range {
                        TimeRange::LastHour => "Last Hour",
                        TimeRange::Last24Hours => "Last 24h",
                        TimeRange::LastWeek => "Last Week",
                        TimeRange::AllTime => "All Time",
                    })
                    .width(100.0)
                    .show_ui(ui, |ui| {
                        ui.selectable_value(&mut self.time_range, TimeRange::LastHour, "Last Hour");
                        ui.selectable_value(
                            &mut self.time_range,
                            TimeRange::Last24Hours,
                            "Last 24h",
                        );
                        ui.selectable_value(&mut self.time_range, TimeRange::LastWeek, "Last Week");
                        ui.selectable_value(&mut self.time_range, TimeRange::AllTime, "All Time");
                    });

                ui.add_space(8.0);

                if ui
                    .button(RichText::new("📤 Export Report").size(12.0))
                    .clicked()
                {
                    *action = Some(AnalyticsAction::ExportReport);
                }
            });
        });
    }

    fn render_knowledge_growth(&self, ui: &mut egui::Ui) {
        self.stat_card(ui, "Knowledge Growth", |ui| {
            ui.horizontal(|ui| {
                ui.label(
                    RichText::new(format!("{}", self.metrics.total_concepts))
                        .size(36.0)
                        .color(PRIMARY)
                        .strong(),
                );

                // Growth indicator
                if self.metrics.concepts_today > 0 {
                    ui.label(
                        RichText::new(format!("↗ +{}", self.metrics.concepts_today))
                            .size(14.0)
                            .color(SUCCESS),
                    );
                }
            });

            ui.label(RichText::new("concepts").size(12.0).color(TEXT_MUTED));

            ui.add_space(12.0);

            // Mini sparkline chart
            let chart_rect = ui
                .allocate_exact_size(
                    Vec2::new(ui.available_width() - 20.0, 40.0),
                    egui::Sense::hover(),
                )
                .0;
            self.draw_sparkline(ui, chart_rect, PRIMARY);
        });
    }

    fn render_learning_activity(&self, ui: &mut egui::Ui) {
        self.stat_card(ui, "Learning Activity", |ui| {
            ui.horizontal(|ui| {
                ui.label(
                    RichText::new(format!("+{}", self.metrics.concepts_today))
                        .size(36.0)
                        .color(SUCCESS)
                        .strong(),
                );
            });

            ui.label(RichText::new("concepts today").size(12.0).color(TEXT_MUTED));

            ui.add_space(8.0);

            ui.horizontal(|ui| {
                egui::Frame::none()
                    .fill(BG_WIDGET)
                    .rounding(Rounding::same(6.0))
                    .inner_margin(egui::Margin::symmetric(8.0, 4.0))
                    .show(ui, |ui| {
                        ui.label(
                            RichText::new(format!(
                                "This hour: +{}",
                                self.metrics.concepts_this_hour
                            ))
                            .size(11.0)
                            .color(TEXT_SECONDARY),
                        );
                    });
            });
        });
    }

    fn render_query_performance(&self, ui: &mut egui::Ui) {
        self.stat_card(ui, "Query Performance", |ui| {
            ui.horizontal(|ui| {
                ui.vertical(|ui| {
                    ui.label(RichText::new("Avg").size(10.0).color(TEXT_MUTED));
                    ui.label(
                        RichText::new(format!("{:.0}ms", self.metrics.avg_query_latency_ms))
                            .size(24.0)
                            .color(SECONDARY)
                            .strong(),
                    );
                });

                ui.add_space(16.0);

                ui.vertical(|ui| {
                    ui.label(RichText::new("P95").size(10.0).color(TEXT_MUTED));
                    ui.label(
                        RichText::new(format!("{:.0}ms", self.metrics.p95_query_latency_ms))
                            .size(24.0)
                            .color(ACCENT)
                            .strong(),
                    );
                });

                ui.add_space(16.0);

                ui.vertical(|ui| {
                    ui.label(RichText::new("P99").size(10.0).color(TEXT_MUTED));
                    ui.label(
                        RichText::new(format!("{:.0}ms", self.metrics.p99_query_latency_ms))
                            .size(24.0)
                            .color(WARNING)
                            .strong(),
                    );
                });
            });

            ui.add_space(8.0);

            // Latency chart
            let chart_rect = ui
                .allocate_exact_size(
                    Vec2::new(ui.available_width() - 20.0, 30.0),
                    egui::Sense::hover(),
                )
                .0;
            self.draw_latency_bars(ui, chart_rect);
        });
    }

    fn render_storage_stats(&self, ui: &mut egui::Ui) {
        self.stat_card(ui, "Storage Statistics", |ui| {
            let stats = [
                (
                    "Concepts",
                    format!("{}", self.metrics.total_concepts),
                    PRIMARY,
                ),
                ("Edges", format!("{}", self.metrics.total_edges), SECONDARY),
                ("Vectors", format!("{}", self.metrics.hnsw_indexed), ACCENT),
            ];

            for (label, value, color) in stats {
                ui.horizontal(|ui| {
                    ui.label(RichText::new(label).size(12.0).color(TEXT_MUTED));
                    ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                        ui.label(RichText::new(&value).size(14.0).color(color).strong());
                    });
                });
                ui.add_space(4.0);
            }
        });
    }

    fn render_top_queries(&self, ui: &mut egui::Ui) {
        self.stat_card(ui, "Top Queries Today", |ui| {
            if self.top_queries.is_empty() {
                ui.label(RichText::new("No queries yet").size(12.0).color(TEXT_MUTED));
            } else {
                for (i, (query, count)) in self.top_queries.iter().take(5).enumerate() {
                    ui.horizontal(|ui| {
                        ui.label(
                            RichText::new(format!("{}.", i + 1))
                                .size(11.0)
                                .color(TEXT_MUTED),
                        );

                        let display_query = if query.len() > 30 {
                            format!("{}...", &query[..30])
                        } else {
                            query.clone()
                        };

                        ui.label(RichText::new(&display_query).size(12.0).color(TEXT_PRIMARY));

                        ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                            ui.label(
                                RichText::new(format!("({})", count))
                                    .size(11.0)
                                    .color(SECONDARY),
                            );
                        });
                    });
                }
            }
        });
    }

    fn render_hnsw_health(&self, ui: &mut egui::Ui) {
        self.stat_card(ui, "HNSW Index Health", |ui| {
            // Coverage bar
            ui.horizontal(|ui| {
                ui.label(RichText::new("Coverage:").size(12.0).color(TEXT_MUTED));
                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    ui.label(
                        RichText::new(format!("{:.0}%", self.metrics.hnsw_coverage * 100.0))
                            .size(14.0)
                            .color(SUCCESS)
                            .strong(),
                    );
                });
            });

            ui.add_space(4.0);

            // Progress bar
            let bar_rect = ui
                .allocate_exact_size(
                    Vec2::new(ui.available_width() - 20.0, 8.0),
                    egui::Sense::hover(),
                )
                .0;
            ui.painter()
                .rect_filled(bar_rect, Rounding::same(4.0), BG_DARK);

            let fill_width = bar_rect.width() * self.metrics.hnsw_coverage;
            let fill_rect =
                Rect::from_min_size(bar_rect.min, Vec2::new(fill_width, bar_rect.height()));
            ui.painter()
                .rect_filled(fill_rect, Rounding::same(4.0), SUCCESS);

            ui.add_space(8.0);

            ui.horizontal(|ui| {
                ui.label(
                    RichText::new(format!(
                        "Indexed: {}/{}",
                        self.metrics.hnsw_indexed, self.metrics.total_concepts
                    ))
                    .size(11.0)
                    .color(TEXT_SECONDARY),
                );
            });

            // Health status
            ui.add_space(8.0);
            let (status_icon, status_text, status_color) = if self.metrics.hnsw_coverage > 0.9 {
                ("✓", "Healthy", SUCCESS)
            } else if self.metrics.hnsw_coverage > 0.7 {
                ("⚠", "Building", ACCENT)
            } else {
                ("○", "Needs Rebuild", WARNING)
            };

            ui.horizontal(|ui| {
                ui.label(RichText::new(status_icon).size(14.0).color(status_color));
                ui.label(RichText::new(status_text).size(12.0).color(status_color));
            });
        });
    }

    fn render_activity_timeline(&self, ui: &mut egui::Ui) {
        self.stat_card(ui, "Recent Activity", |ui| {
            egui::ScrollArea::vertical()
                .max_height(150.0)
                .auto_shrink([false; 2])
                .show(ui, |ui| {
                    if self.activity_log.is_empty() {
                        ui.label(
                            RichText::new("No recent activity")
                                .size(12.0)
                                .color(TEXT_MUTED),
                        );
                    } else {
                        for entry in self.activity_log.iter().rev().take(20) {
                            self.render_activity_entry(ui, entry);
                        }
                    }
                });
        });
    }

    fn render_activity_entry(&self, ui: &mut egui::Ui, entry: &ActivityEntry) {
        ui.horizontal(|ui| {
            // Timestamp
            ui.label(
                RichText::new(entry.timestamp.format("%H:%M").to_string())
                    .size(10.0)
                    .color(TEXT_MUTED)
                    .monospace(),
            );

            ui.add_space(8.0);

            // Activity type icon and color
            let (icon, _color) = match entry.activity_type {
                ActivityType::Learn => ("📚", SUCCESS),
                ActivityType::Query => ("🔍", SECONDARY),
                ActivityType::Search => ("🔎", PRIMARY),
                ActivityType::Export => ("📤", ACCENT),
                ActivityType::Import => ("📥", WARNING),
            };

            ui.label(RichText::new(icon).size(12.0));

            // Description
            let desc = if entry.description.len() > 50 {
                format!("{}...", &entry.description[..50])
            } else {
                entry.description.clone()
            };

            ui.label(RichText::new(&desc).size(12.0).color(TEXT_PRIMARY));

            // Duration if available
            if let Some(ms) = entry.duration_ms {
                ui.label(
                    RichText::new(format!("({}ms)", ms))
                        .size(10.0)
                        .color(TEXT_MUTED),
                );
            }
        });
    }

    fn stat_card(&self, ui: &mut egui::Ui, title: &str, content: impl FnOnce(&mut egui::Ui)) {
        egui::Frame::none()
            .fill(BG_WIDGET.gamma_multiply(0.7))
            .stroke(Stroke::new(1.0, BG_WIDGET))
            .rounding(Rounding::same(12.0))
            .inner_margin(16.0)
            .show(ui, |ui| {
                ui.label(RichText::new(title).size(12.0).color(TEXT_MUTED).strong());
                ui.add_space(8.0);
                content(ui);
            });
    }

    fn draw_sparkline(&self, ui: &mut egui::Ui, rect: Rect, color: Color32) {
        ui.painter().rect_filled(rect, Rounding::same(4.0), BG_DARK);

        if self.history.len() < 2 {
            return;
        }

        let points: Vec<_> = self
            .history
            .iter()
            .enumerate()
            .map(|(i, h)| {
                let x = rect.min.x + (i as f32 / self.history.len() as f32) * rect.width();
                let max_val = self
                    .history
                    .iter()
                    .map(|h| h.concept_count)
                    .max()
                    .unwrap_or(1) as f32;
                let y = rect.max.y - (h.concept_count as f32 / max_val) * rect.height() * 0.8;
                Pos2::new(x, y)
            })
            .collect();

        if points.len() > 1 {
            for window in points.windows(2) {
                ui.painter().line_segment(
                    [window[0], window[1]],
                    Stroke::new(2.0, color.gamma_multiply(0.7)),
                );
            }
        }
    }

    fn draw_latency_bars(&self, ui: &mut egui::Ui, rect: Rect) {
        ui.painter().rect_filled(rect, Rounding::same(4.0), BG_DARK);

        if self.latency_samples.is_empty() {
            return;
        }

        let max_latency = self.latency_samples.iter().cloned().fold(1.0f32, f32::max);
        let bar_width = rect.width() / self.latency_samples.len().min(50) as f32;

        for (i, &latency) in self.latency_samples.iter().rev().take(50).enumerate() {
            let height = (latency / max_latency) * rect.height() * 0.9;
            let x = rect.max.x - (i as f32 + 1.0) * bar_width;

            let color = if latency < 50.0 {
                SUCCESS
            } else if latency < 100.0 {
                ACCENT
            } else {
                WARNING
            };

            let bar = Rect::from_min_size(
                Pos2::new(x, rect.max.y - height),
                Vec2::new(bar_width - 1.0, height),
            );

            ui.painter()
                .rect_filled(bar, Rounding::same(1.0), color.gamma_multiply(0.7));
        }
    }
}

/// Actions from analytics dashboard
#[derive(Debug, Clone)]
pub enum AnalyticsAction {
    ExportReport,
    ClearHistory,
}
