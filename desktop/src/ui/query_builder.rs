//! Query Builder Panel
//!
//! Visual query construction without coding.
//! Features: query type selection, filters, saved queries, results display.

use crate::theme::*;
use crate::types::ConceptInfo;
use crate::types::{QueryFilters, QueryType};
use eframe::egui::{self, Color32, RichText, Rounding, ScrollArea, Stroke, Vec2};

/// Query Builder Panel
pub struct QueryBuilder {
    // Query settings
    pub query_type: QueryType,
    pub query_text: String,
    pub filters: QueryFilters,

    // Results
    pub results: Vec<ConceptInfo>,
    pub is_searching: bool,
    pub error_message: Option<String>,
    pub last_search_time_ms: Option<u64>,

    // Saved queries
    pub saved_queries: Vec<SavedQueryEntry>,
    pub save_query_name: String,
    pub show_saved_queries: bool,
}

#[derive(Debug, Clone)]
pub struct SavedQueryEntry {
    pub name: String,
    pub query_text: String,
    pub query_type: QueryType,
    pub filters: QueryFilters,
}

impl Default for QueryBuilder {
    fn default() -> Self {
        Self {
            query_type: QueryType::TextSearch,
            query_text: String::new(),
            filters: QueryFilters::new(),
            results: Vec::new(),
            is_searching: false,
            error_message: None,
            last_search_time_ms: None,
            saved_queries: Vec::new(),
            save_query_name: String::new(),
            show_saved_queries: false,
        }
    }
}

impl QueryBuilder {
    /// Render the query builder
    pub fn ui(&mut self, ui: &mut egui::Ui) -> Option<QueryBuilderAction> {
        let mut action = None;

        ui.vertical(|ui| {
            // Header
            self.render_header(ui);

            ui.add_space(16.0);

            // Query type selector
            self.render_query_type_selector(ui);

            ui.add_space(16.0);

            // Query input and parameters
            self.render_query_input(ui);

            ui.add_space(16.0);

            // Filters
            self.render_filters(ui);

            ui.add_space(16.0);

            // Action buttons
            self.render_actions(ui, &mut action);

            ui.add_space(16.0);

            // Results
            self.render_results(ui, &mut action);
        });

        action
    }

    fn render_header(&mut self, ui: &mut egui::Ui) {
        ui.horizontal(|ui| {
            ui.label(RichText::new("🔍").size(20.0));
            ui.add_space(4.0);
            ui.label(
                RichText::new("Advanced Query Builder")
                    .size(22.0)
                    .color(TEXT_PRIMARY)
                    .strong(),
            );

            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                // Saved queries toggle
                let saved_text = if self.show_saved_queries {
                    "📁 Hide Saved"
                } else {
                    "📁 Saved Queries"
                };
                if ui.button(RichText::new(saved_text).size(12.0)).clicked() {
                    self.show_saved_queries = !self.show_saved_queries;
                }
            });
        });

        // Saved queries dropdown
        if self.show_saved_queries {
            ui.add_space(8.0);
            self.render_saved_queries(ui);
        }
    }

    fn render_query_type_selector(&mut self, ui: &mut egui::Ui) {
        ui.label(
            RichText::new("Query Type:")
                .size(13.0)
                .color(TEXT_MUTED)
                .strong(),
        );
        ui.add_space(8.0);

        ui.horizontal(|ui| {
            self.query_type_button(ui, "📝 Text Search", QueryType::TextSearch);
            ui.add_space(8.0);
            self.query_type_button(ui, "🧠 Semantic", QueryType::SemanticSearch);
            ui.add_space(8.0);
            self.query_type_button(ui, "🔗 Path Finding", QueryType::PathFinding);
        });

        // Description for selected type
        ui.add_space(8.0);
        let description = match self.query_type {
            QueryType::TextSearch => "Keyword-based search through concept content",
            QueryType::SemanticSearch => "Vector similarity search for semantic matches",
            QueryType::PathFinding => "Find reasoning paths between two concepts",
        };
        ui.label(
            RichText::new(description)
                .size(11.0)
                .color(TEXT_MUTED)
                .italics(),
        );
    }

    fn query_type_button(&mut self, ui: &mut egui::Ui, label: &str, query_type: QueryType) {
        let is_selected = self.query_type == query_type;
        let bg = if is_selected {
            PRIMARY.gamma_multiply(0.25)
        } else {
            BG_WIDGET
        };
        let border = if is_selected {
            PRIMARY.gamma_multiply(0.5)
        } else {
            Color32::TRANSPARENT
        };
        let text_color = if is_selected { PRIMARY } else { TEXT_SECONDARY };

        egui::Frame::none()
            .fill(bg)
            .stroke(Stroke::new(1.0, border))
            .rounding(Rounding::same(10.0))
            .inner_margin(egui::Margin::symmetric(16.0, 10.0))
            .show(ui, |ui| {
                if ui
                    .add(
                        egui::Label::new(RichText::new(label).size(13.0).color(text_color))
                            .sense(egui::Sense::click()),
                    )
                    .clicked()
                {
                    self.query_type = query_type;
                }
            });
    }

    fn render_query_input(&mut self, ui: &mut egui::Ui) {
        egui::Frame::none()
            .fill(BG_WIDGET.gamma_multiply(0.7))
            .stroke(Stroke::new(1.0, BG_WIDGET))
            .rounding(Rounding::same(12.0))
            .inner_margin(16.0)
            .show(ui, |ui| {
                match self.query_type {
                    QueryType::TextSearch | QueryType::SemanticSearch => {
                        ui.label(RichText::new("Query Text:").size(12.0).color(TEXT_MUTED));
                        ui.add_space(4.0);

                        ui.add_sized(
                            Vec2::new(ui.available_width(), 40.0),
                            egui::TextEdit::multiline(&mut self.query_text)
                                .hint_text("Enter your search query...")
                                .font(egui::FontId::proportional(14.0)),
                        );

                        if self.query_type == QueryType::SemanticSearch {
                            ui.add_space(12.0);
                            ui.horizontal(|ui| {
                                ui.label(
                                    RichText::new("Top K Results:").size(12.0).color(TEXT_MUTED),
                                );
                                ui.add(egui::Slider::new(&mut self.filters.max_results, 1..=100));

                                ui.add_space(16.0);

                                ui.label(RichText::new("EF Search:").size(12.0).color(TEXT_MUTED));
                                ui.add(egui::Slider::new(&mut self.filters.ef_search, 10..=200));
                            });
                        }
                    }
                    QueryType::PathFinding => {
                        ui.horizontal(|ui| {
                            ui.vertical(|ui| {
                                ui.label(
                                    RichText::new("From Concept:").size(12.0).color(TEXT_MUTED),
                                );
                                ui.add_sized(
                                    Vec2::new(200.0, 28.0),
                                    egui::TextEdit::singleline(&mut self.query_text)
                                        .hint_text("Starting concept..."),
                                );
                            });

                            ui.add_space(16.0);

                            ui.vertical(|ui| {
                                ui.label(RichText::new("To Concept:").size(12.0).color(TEXT_MUTED));
                                // This would need a second field - storing in query_text for now
                                // In production, add path_target field
                            });
                        });
                    }
                }
            });
    }

    fn render_filters(&mut self, ui: &mut egui::Ui) {
        egui::CollapsingHeader::new(RichText::new("🎛️ Filters").size(13.0).color(TEXT_PRIMARY))
            .default_open(true)
            .show(ui, |ui| {
                egui::Frame::none()
                    .fill(BG_WIDGET.gamma_multiply(0.5))
                    .rounding(Rounding::same(8.0))
                    .inner_margin(12.0)
                    .show(ui, |ui| {
                        // Confidence threshold
                        let confidence_enabled = self.filters.min_confidence > 0.0;
                        let confidence_text =
                            format!("{:.0}%", self.filters.min_confidence * 100.0);
                        ui.horizontal(|ui| {
                            let mut enabled = confidence_enabled;
                            if ui.checkbox(&mut enabled, "Confidence Threshold:").changed() {
                                self.filters.min_confidence = if enabled { 0.5 } else { 0.0 };
                            }
                            ui.add_enabled(
                                confidence_enabled,
                                egui::Slider::new(&mut self.filters.min_confidence, 0.0..=1.0)
                                    .text(confidence_text),
                            );
                        });

                        ui.add_space(8.0);

                        // Max results
                        ui.horizontal(|ui| {
                            ui.label(
                                RichText::new("Max Results:")
                                    .size(12.0)
                                    .color(TEXT_SECONDARY),
                            );
                            ui.add(egui::Slider::new(&mut self.filters.max_results, 1..=100));
                        });

                        ui.add_space(8.0);

                        // Relationship filters
                        ui.label(
                            RichText::new("Relationship Filters:")
                                .size(12.0)
                                .color(TEXT_MUTED),
                        );
                        ui.horizontal(|ui| {
                            ui.checkbox(&mut self.filters.has_causal, "Must have CAUSAL");
                            ui.add_space(16.0);
                            ui.checkbox(&mut self.filters.has_temporal, "Must have TEMPORAL");
                        });

                        ui.add_space(8.0);

                        ui.horizontal(|ui| {
                            ui.label(
                                RichText::new("Min neighbors:")
                                    .size(12.0)
                                    .color(TEXT_SECONDARY),
                            );
                            ui.add(egui::Slider::new(&mut self.filters.min_neighbors, 0..=20));
                        });
                    });
            });
    }

    fn render_actions(&mut self, ui: &mut egui::Ui, action: &mut Option<QueryBuilderAction>) {
        ui.horizontal(|ui| {
            // Clear button
            if ui
                .button(RichText::new("Clear All").size(12.0).color(TEXT_SECONDARY))
                .clicked()
            {
                self.query_text.clear();
                self.filters = QueryFilters::new();
                self.results.clear();
                self.error_message = None;
            }

            ui.add_space(8.0);

            // Save query button
            egui::Frame::none()
                .fill(BG_WIDGET)
                .rounding(Rounding::same(8.0))
                .inner_margin(egui::Margin::symmetric(8.0, 4.0))
                .show(ui, |ui| {
                    ui.horizontal(|ui| {
                        ui.add_sized(
                            Vec2::new(120.0, 20.0),
                            egui::TextEdit::singleline(&mut self.save_query_name)
                                .hint_text("Query name..."),
                        );
                        if ui
                            .add_enabled(
                                !self.save_query_name.is_empty() && !self.query_text.is_empty(),
                                egui::Button::new(RichText::new("💾").size(12.0)),
                            )
                            .clicked()
                        {
                            self.saved_queries.push(SavedQueryEntry {
                                name: self.save_query_name.clone(),
                                query_text: self.query_text.clone(),
                                query_type: self.query_type,
                                filters: self.filters.clone(),
                            });
                            self.save_query_name.clear();
                        }
                    });
                });

            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                // Run query button
                let can_run = !self.query_text.is_empty() && !self.is_searching;

                if ui
                    .add_enabled(
                        can_run,
                        egui::Button::new(
                            RichText::new("▶ Run Query")
                                .size(14.0)
                                .color(Color32::WHITE),
                        )
                        .fill(PRIMARY)
                        .min_size(Vec2::new(120.0, 36.0)),
                    )
                    .clicked()
                {
                    *action = Some(QueryBuilderAction::RunQuery {
                        query_type: self.query_type,
                        query: self.query_text.clone(),
                        filters: self.filters.clone(),
                    });
                }
            });
        });
    }

    fn render_results(&mut self, ui: &mut egui::Ui, action: &mut Option<QueryBuilderAction>) {
        // Results header
        ui.horizontal(|ui| {
            ui.label(
                RichText::new("Results")
                    .size(14.0)
                    .color(TEXT_PRIMARY)
                    .strong(),
            );

            if !self.results.is_empty() {
                ui.add_space(8.0);
                egui::Frame::none()
                    .fill(SUCCESS.gamma_multiply(0.2))
                    .rounding(Rounding::same(8.0))
                    .inner_margin(egui::Margin::symmetric(8.0, 2.0))
                    .show(ui, |ui| {
                        ui.label(
                            RichText::new(format!("{} found", self.results.len()))
                                .size(11.0)
                                .color(SUCCESS),
                        );
                    });

                if let Some(ms) = self.last_search_time_ms {
                    ui.label(
                        RichText::new(format!("({}ms)", ms))
                            .size(11.0)
                            .color(TEXT_MUTED),
                    );
                }
            }

            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                if !self.results.is_empty() {
                    if ui.button(RichText::new("📤 Export").size(12.0)).clicked() {
                        *action = Some(QueryBuilderAction::ExportResults);
                    }

                    ui.add_space(8.0);

                    if ui
                        .button(RichText::new("📊 Visualize").size(12.0))
                        .clicked()
                    {
                        *action = Some(QueryBuilderAction::VisualizeResults);
                    }
                }
            });
        });

        ui.add_space(8.0);

        // Error message
        if let Some(err) = &self.error_message {
            egui::Frame::none()
                .fill(ERROR.gamma_multiply(0.15))
                .rounding(Rounding::same(8.0))
                .inner_margin(12.0)
                .show(ui, |ui| {
                    ui.label(RichText::new(format!("⚠️ {}", err)).size(12.0).color(ERROR));
                });
            return;
        }

        // Loading state
        if self.is_searching {
            ui.vertical_centered(|ui| {
                ui.add_space(20.0);
                ui.spinner();
                ui.label(RichText::new("Searching...").size(12.0).color(TEXT_MUTED));
            });
            return;
        }

        // Results list
        if self.results.is_empty() {
            egui::Frame::none()
                .fill(BG_WIDGET.gamma_multiply(0.5))
                .rounding(Rounding::same(8.0))
                .inner_margin(20.0)
                .show(ui, |ui| {
                    ui.vertical_centered(|ui| {
                        ui.label(RichText::new("🔍").size(32.0));
                        ui.add_space(8.0);
                        ui.label(
                            RichText::new("Enter a query and click Run")
                                .size(13.0)
                                .color(TEXT_MUTED),
                        );
                    });
                });
        } else {
            ScrollArea::vertical()
                .max_height(300.0)
                .auto_shrink([false; 2])
                .show(ui, |ui| {
                    for (i, result) in self.results.iter().enumerate() {
                        self.render_result_card(ui, i, result, action);
                        ui.add_space(6.0);
                    }
                });
        }
    }

    fn render_result_card(
        &self,
        ui: &mut egui::Ui,
        index: usize,
        result: &ConceptInfo,
        _action: &mut Option<QueryBuilderAction>,
    ) {
        egui::Frame::none()
            .fill(BG_WIDGET.gamma_multiply(0.6))
            .stroke(Stroke::new(1.0, BG_WIDGET))
            .rounding(Rounding::same(8.0))
            .inner_margin(12.0)
            .show(ui, |ui| {
                ui.horizontal(|ui| {
                    // Rank number
                    egui::Frame::none()
                        .fill(PRIMARY.gamma_multiply(0.2))
                        .rounding(Rounding::same(6.0))
                        .inner_margin(egui::Margin::symmetric(8.0, 4.0))
                        .show(ui, |ui| {
                            ui.label(
                                RichText::new(format!("{}", index + 1))
                                    .size(12.0)
                                    .color(PRIMARY)
                                    .strong(),
                            );
                        });

                    ui.add_space(8.0);

                    // Content
                    ui.vertical(|ui| {
                        let content_preview = if result.content.len() > 100 {
                            format!("{}...", &result.content[..100])
                        } else {
                            result.content.clone()
                        };

                        ui.label(
                            RichText::new(&content_preview)
                                .size(13.0)
                                .color(TEXT_PRIMARY),
                        );

                        ui.add_space(4.0);

                        ui.horizontal(|ui| {
                            // Confidence
                            let conf_color = if result.confidence > 0.8 {
                                SUCCESS
                            } else if result.confidence > 0.5 {
                                ACCENT
                            } else {
                                WARNING
                            };
                            ui.label(
                                RichText::new(format!(
                                    "Confidence: {:.0}%",
                                    result.confidence * 100.0
                                ))
                                .size(11.0)
                                .color(conf_color),
                            );

                            ui.add_space(12.0);

                            // ID
                            ui.label(
                                RichText::new(format!("ID: {}...", &result.id[..8]))
                                    .size(10.0)
                                    .color(TEXT_MUTED)
                                    .monospace(),
                            );

                            // Neighbors
                            if !result.neighbors.is_empty() {
                                ui.add_space(12.0);
                                ui.label(
                                    RichText::new(format!(
                                        "{} connections",
                                        result.neighbors.len()
                                    ))
                                    .size(10.0)
                                    .color(SECONDARY),
                                );
                            }
                        });
                    });
                });
            });
    }

    fn render_saved_queries(&mut self, ui: &mut egui::Ui) {
        egui::Frame::none()
            .fill(BG_WIDGET.gamma_multiply(0.7))
            .rounding(Rounding::same(8.0))
            .inner_margin(12.0)
            .show(ui, |ui| {
                if self.saved_queries.is_empty() {
                    ui.label(
                        RichText::new("No saved queries yet")
                            .size(12.0)
                            .color(TEXT_MUTED),
                    );
                } else {
                    for (i, saved) in self.saved_queries.clone().iter().enumerate() {
                        ui.horizontal(|ui| {
                            if ui.button(RichText::new(&saved.name).size(12.0)).clicked() {
                                self.query_type = saved.query_type;
                                self.query_text = saved.query_text.clone();
                                self.filters = saved.filters.clone();
                                self.show_saved_queries = false;
                            }

                            ui.with_layout(
                                egui::Layout::right_to_left(egui::Align::Center),
                                |ui| {
                                    if ui
                                        .button(RichText::new("🗑").size(11.0).color(ERROR))
                                        .clicked()
                                    {
                                        self.saved_queries.remove(i);
                                    }
                                },
                            );
                        });
                    }
                }
            });
    }

    /// Set search results
    pub fn set_results(&mut self, results: Vec<ConceptInfo>, search_time_ms: u64) {
        self.results = results;
        self.last_search_time_ms = Some(search_time_ms);
        self.is_searching = false;
        self.error_message = None;
    }

    /// Set error message
    pub fn set_error(&mut self, message: String) {
        self.error_message = Some(message);
        self.is_searching = false;
    }
}

/// Actions from query builder
#[derive(Debug, Clone)]
pub enum QueryBuilderAction {
    RunQuery {
        query_type: QueryType,
        query: String,
        filters: QueryFilters,
    },
    ExportResults,
    VisualizeResults,
}
