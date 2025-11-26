//! Export/Import Panel
//!
//! Data portability: JSON/CSV/GraphML export, import with validation.
//! Features: format selection, filters, batch operations, progress tracking.

use std::path::PathBuf;
use eframe::egui::{self, Color32, RichText, Rounding, ScrollArea, Stroke, Vec2};
use sutra_storage::ConcurrentMemory;
use crate::theme::*;
use crate::types::{ExportFormat, ExportOptions, ImportMode, ImportPreview, BatchProgress};

/// Export/Import Panel
pub struct ExportImportPanel {
    // Export settings
    pub export_format: ExportFormat,
    pub export_options: ExportOptions,
    pub export_path: String,
    
    // Import settings
    pub import_path: String,
    pub import_mode: ImportMode,
    pub validate_before_import: bool,
    pub show_preview: bool,
    pub import_preview: Option<ImportPreview>,
    
    // Batch import
    pub batch_path: String,
    pub batch_progress: BatchProgress,
    
    // State
    pub last_export_result: Option<ExportResult>,
    pub last_import_result: Option<ImportResult>,
    pub active_tab: ExportImportTab,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum ExportImportTab {
    #[default]
    Export,
    Import,
    Batch,
}

#[derive(Debug, Clone)]
pub struct ExportResult {
    pub success: bool,
    pub path: String,
    pub concepts_exported: usize,
    pub edges_exported: usize,
    pub message: String,
}

#[derive(Debug, Clone)]
pub struct ImportResult {
    pub success: bool,
    pub concepts_imported: usize,
    pub edges_imported: usize,
    pub errors: usize,
    pub message: String,
}

impl Default for ExportImportPanel {
    fn default() -> Self {
        Self {
            export_format: ExportFormat::Json,
            export_options: ExportOptions::default(),
            export_path: String::new(),
            import_path: String::new(),
            import_mode: ImportMode::Merge,
            validate_before_import: true,
            show_preview: true,
            import_preview: None,
            batch_path: String::new(),
            batch_progress: BatchProgress::default(),
            last_export_result: None,
            last_import_result: None,
            active_tab: ExportImportTab::Export,
        }
    }
}

impl ExportImportPanel {
    /// Generate export content in selected format
    pub fn generate_export(&self, storage: &ConcurrentMemory) -> Result<String, String> {
        let snapshot = storage.get_snapshot();
        let concepts = snapshot.all_concepts();
        
        // Apply filters
        let filtered: Vec<_> = concepts
            .iter()
            .filter(|c| c.confidence >= self.export_options.min_confidence)
            .filter(|c| {
                if self.export_options.filter_query.is_empty() {
                    true
                } else {
                    let content = String::from_utf8_lossy(&c.content).to_lowercase();
                    content.contains(&self.export_options.filter_query.to_lowercase())
                }
            })
            .collect();
        
        match self.export_format {
            ExportFormat::Json => self.export_json(&filtered),
            ExportFormat::Csv => self.export_csv(&filtered),
            ExportFormat::GraphML => self.export_graphml(&filtered),
            ExportFormat::Cypher => self.export_cypher(&filtered),
        }
    }
    
    fn export_json(&self, concepts: &[&sutra_storage::ConceptNode]) -> Result<String, String> {
        let data = serde_json::json!({
            "version": "2.0.0",
            "exported_at": chrono::Utc::now().to_rfc3339(),
            "format": "sutra-desktop",
            "concepts": concepts.iter().map(|c| {
                serde_json::json!({
                    "id": c.id.to_hex(),
                    "content": String::from_utf8_lossy(&c.content),
                    "confidence": c.confidence,
                    "strength": c.strength,
                    "neighbors": c.neighbors.iter().map(|n| n.to_hex()).collect::<Vec<_>>(),
                })
            }).collect::<Vec<_>>(),
            "edges": concepts.iter().flat_map(|c| {
                c.neighbors.iter().map(move |n| {
                    serde_json::json!({
                        "from": c.id.to_hex(),
                        "to": n.to_hex(),
                    })
                })
            }).collect::<Vec<_>>(),
        });
        
        serde_json::to_string_pretty(&data)
            .map_err(|e| format!("JSON serialization failed: {}", e))
    }
    
    fn export_csv(&self, concepts: &[&sutra_storage::ConceptNode]) -> Result<String, String> {
        let mut output = String::from("id,content,confidence,strength,neighbor_count\n");
        
        for c in concepts {
            let content = String::from_utf8_lossy(&c.content).replace(',', ";").replace('\n', " ");
            output.push_str(&format!(
                "{},{},{:.4},{:.4},{}\n",
                c.id.to_hex(),
                content,
                c.confidence,
                c.strength,
                c.neighbors.len(),
            ));
        }
        
        Ok(output)
    }
    
    fn export_graphml(&self, concepts: &[&sutra_storage::ConceptNode]) -> Result<String, String> {
        let mut output = String::from(r#"<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="content" for="node" attr.name="content" attr.type="string"/>
  <key id="confidence" for="node" attr.name="confidence" attr.type="double"/>
  <key id="strength" for="node" attr.name="strength" attr.type="double"/>
  <graph id="sutra" edgedefault="directed">
"#);
        
        // Nodes
        for c in concepts {
            let content = String::from_utf8_lossy(&c.content)
                .replace('&', "&amp;")
                .replace('<', "&lt;")
                .replace('>', "&gt;")
                .replace('"', "&quot;");
            
            output.push_str(&format!(
                r#"    <node id="{}">
      <data key="content">{}</data>
      <data key="confidence">{:.4}</data>
      <data key="strength">{:.4}</data>
    </node>
"#,
                c.id.to_hex(),
                content,
                c.confidence,
                c.strength,
            ));
        }
        
        // Edges
        let mut edge_id = 0;
        for c in concepts {
            for neighbor in &c.neighbors {
                output.push_str(&format!(
                    r#"    <edge id="e{}" source="{}" target="{}"/>
"#,
                    edge_id,
                    c.id.to_hex(),
                    neighbor.to_hex(),
                ));
                edge_id += 1;
            }
        }
        
        output.push_str("  </graph>\n</graphml>");
        Ok(output)
    }
    
    fn export_cypher(&self, concepts: &[&sutra_storage::ConceptNode]) -> Result<String, String> {
        let mut output = String::from("// Sutra Desktop Export - Cypher Script\n");
        output.push_str("// Import into Neo4j using :source command or APOC\n\n");
        
        // Create constraints
        output.push_str("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE;\n\n");
        
        // Create nodes
        for c in concepts {
            let content = String::from_utf8_lossy(&c.content)
                .replace('\\', "\\\\")
                .replace('"', "\\\"")
                .replace('\n', "\\n");
            
            output.push_str(&format!(
                "CREATE (c{}:Concept {{id: '{}', content: \"{}\", confidence: {:.4}, strength: {:.4}}});\n",
                &c.id.to_hex()[..8],
                c.id.to_hex(),
                content,
                c.confidence,
                c.strength,
            ));
        }
        
        output.push_str("\n// Create relationships\n");
        
        // Create relationships
        for c in concepts {
            for neighbor in &c.neighbors {
                output.push_str(&format!(
                    "MATCH (a:Concept {{id: '{}'}}), (b:Concept {{id: '{}'}}) CREATE (a)-[:RELATES_TO]->(b);\n",
                    c.id.to_hex(),
                    neighbor.to_hex(),
                ));
            }
        }
        
        Ok(output)
    }
    
    /// Render the panel
    pub fn ui(&mut self, ui: &mut egui::Ui) -> Option<ExportImportAction> {
        let mut action = None;
        
        ui.vertical(|ui| {
            // Header
            self.render_header(ui);
            
            ui.add_space(16.0);
            
            // Tab selector
            self.render_tabs(ui);
            
            ui.add_space(16.0);
            
            // Tab content
            match self.active_tab {
                ExportImportTab::Export => self.render_export_tab(ui, &mut action),
                ExportImportTab::Import => self.render_import_tab(ui, &mut action),
                ExportImportTab::Batch => self.render_batch_tab(ui, &mut action),
            }
        });
        
        action
    }
    
    fn render_header(&self, ui: &mut egui::Ui) {
        ui.horizontal(|ui| {
            ui.label(RichText::new("📤").size(20.0));
            ui.add_space(4.0);
            ui.label(RichText::new("Export / Import").size(22.0).color(TEXT_PRIMARY).strong());
        });
    }
    
    fn render_tabs(&mut self, ui: &mut egui::Ui) {
        ui.horizontal(|ui| {
            self.tab_button(ui, "Export", ExportImportTab::Export);
            ui.add_space(4.0);
            self.tab_button(ui, "Import", ExportImportTab::Import);
            ui.add_space(4.0);
            self.tab_button(ui, "Batch", ExportImportTab::Batch);
        });
    }
    
    fn tab_button(&mut self, ui: &mut egui::Ui, label: &str, tab: ExportImportTab) {
        let is_selected = self.active_tab == tab;
        let bg = if is_selected { PRIMARY.gamma_multiply(0.2) } else { BG_WIDGET };
        let text_color = if is_selected { PRIMARY } else { TEXT_SECONDARY };
        
        egui::Frame::none()
            .fill(bg)
            .rounding(Rounding::same(8.0))
            .inner_margin(egui::Margin::symmetric(16.0, 8.0))
            .show(ui, |ui| {
                if ui.add(egui::Label::new(RichText::new(label).size(13.0).color(text_color)).sense(egui::Sense::click())).clicked() {
                    self.active_tab = tab;
                }
            });
    }
    
    fn render_export_tab(&mut self, ui: &mut egui::Ui, action: &mut Option<ExportImportAction>) {
        egui::Frame::none()
            .fill(BG_WIDGET.gamma_multiply(0.7))
            .stroke(Stroke::new(1.0, BG_WIDGET))
            .rounding(Rounding::same(12.0))
            .inner_margin(20.0)
            .show(ui, |ui| {
                // Format selection
                ui.label(RichText::new("Export Format:").size(13.0).color(TEXT_PRIMARY).strong());
                ui.add_space(8.0);
                
                ui.horizontal(|ui| {
                    for format in [ExportFormat::Json, ExportFormat::Csv, ExportFormat::GraphML, ExportFormat::Cypher] {
                        let is_selected = self.export_format == format;
                        let bg = if is_selected { PRIMARY.gamma_multiply(0.3) } else { BG_DARK };
                        let border = if is_selected { PRIMARY.gamma_multiply(0.5) } else { Color32::TRANSPARENT };
                        
                        egui::Frame::none()
                            .fill(bg)
                            .stroke(Stroke::new(1.0, border))
                            .rounding(Rounding::same(8.0))
                            .inner_margin(egui::Margin::symmetric(12.0, 8.0))
                            .show(ui, |ui| {
                                if ui.add(egui::Label::new(
                                    RichText::new(format.name()).size(12.0).color(if is_selected { PRIMARY } else { TEXT_SECONDARY })
                                ).sense(egui::Sense::click())).clicked() {
                                    self.export_format = format;
                                }
                            });
                    }
                });
                
                ui.add_space(16.0);
                
                // Options
                ui.label(RichText::new("Options:").size(13.0).color(TEXT_PRIMARY).strong());
                ui.add_space(8.0);
                
                ui.checkbox(&mut self.export_options.include_vectors, "Include vectors");
                ui.checkbox(&mut self.export_options.include_metadata, "Include metadata (timestamps)");
                
                ui.add_space(8.0);
                
                ui.horizontal(|ui| {
                    ui.label(RichText::new("Min confidence:").size(12.0).color(TEXT_SECONDARY));
                    ui.add(egui::Slider::new(&mut self.export_options.min_confidence, 0.0..=1.0).show_value(true));
                });
                
                ui.add_space(8.0);
                
                ui.horizontal(|ui| {
                    ui.label(RichText::new("Filter query:").size(12.0).color(TEXT_SECONDARY));
                    ui.add_sized(
                        Vec2::new(200.0, 24.0),
                        egui::TextEdit::singleline(&mut self.export_options.filter_query)
                            .hint_text("Filter concepts...")
                    );
                });
                
                ui.add_space(16.0);
                
                // Export button
                ui.horizontal(|ui| {
                    if ui.button(RichText::new("📁 Choose Location...").size(13.0)).clicked() {
                        // In a real app, this would open a file dialog
                        self.export_path = format!("~/Documents/sutra_export.{}", self.export_format.extension());
                    }
                    
                    ui.add_space(8.0);
                    
                    ui.label(RichText::new(&self.export_path).size(11.0).color(TEXT_MUTED));
                });
                
                ui.add_space(12.0);
                
                if ui.add_enabled(
                    !self.export_path.is_empty(),
                    egui::Button::new(RichText::new("⬇ Export").size(14.0).color(Color32::WHITE))
                        .fill(PRIMARY)
                        .min_size(Vec2::new(120.0, 36.0))
                ).clicked() {
                    *action = Some(ExportImportAction::Export(self.export_path.clone()));
                }
                
                // Result message
                if let Some(result) = &self.last_export_result {
                    ui.add_space(12.0);
                    let (icon, color) = if result.success { ("✓", SUCCESS) } else { ("✗", ERROR) };
                    ui.label(RichText::new(format!("{} {}", icon, result.message)).size(12.0).color(color));
                }
            });
    }
    
    fn render_import_tab(&mut self, ui: &mut egui::Ui, action: &mut Option<ExportImportAction>) {
        egui::Frame::none()
            .fill(BG_WIDGET.gamma_multiply(0.7))
            .stroke(Stroke::new(1.0, BG_WIDGET))
            .rounding(Rounding::same(12.0))
            .inner_margin(20.0)
            .show(ui, |ui| {
                // File selection
                ui.label(RichText::new("Select File:").size(13.0).color(TEXT_PRIMARY).strong());
                ui.add_space(8.0);
                
                ui.horizontal(|ui| {
                    if ui.button(RichText::new("📁 Choose File...").size(13.0)).clicked() {
                        // In a real app, this would open a file dialog
                        self.import_path = "~/Documents/sutra_export.json".to_string();
                    }
                    
                    ui.add_space(8.0);
                    
                    if self.import_path.is_empty() {
                        ui.label(RichText::new("No file selected").size(11.0).color(TEXT_MUTED));
                    } else {
                        ui.label(RichText::new(&self.import_path).size(11.0).color(TEXT_PRIMARY));
                    }
                });
                
                ui.add_space(16.0);
                
                // Import mode
                ui.label(RichText::new("Import Mode:").size(13.0).color(TEXT_PRIMARY).strong());
                ui.add_space(8.0);
                
                ui.radio_value(&mut self.import_mode, ImportMode::Merge, "Merge with existing (skip duplicates)");
                ui.radio_value(&mut self.import_mode, ImportMode::Overwrite, "Overwrite existing");
                ui.radio_value(&mut self.import_mode, ImportMode::NewWorkspace, "Create new workspace");
                
                ui.add_space(16.0);
                
                // Options
                ui.checkbox(&mut self.validate_before_import, "Validate data before import");
                ui.checkbox(&mut self.show_preview, "Show preview before committing");
                
                ui.add_space(16.0);
                
                // Preview (if available)
                if let Some(preview) = &self.import_preview {
                    egui::Frame::none()
                        .fill(BG_DARK)
                        .rounding(Rounding::same(8.0))
                        .inner_margin(12.0)
                        .show(ui, |ui| {
                            ui.label(RichText::new("Preview:").size(12.0).color(TEXT_MUTED).strong());
                            ui.add_space(4.0);
                            ui.label(RichText::new(format!("Concepts: {}", preview.concepts_count)).size(12.0).color(TEXT_PRIMARY));
                            ui.label(RichText::new(format!("Edges: {}", preview.edges_count)).size(12.0).color(TEXT_PRIMARY));
                            ui.label(RichText::new(format!("New: {}, Duplicates: {}", preview.new_count, preview.duplicates_count)).size(12.0).color(TEXT_SECONDARY));
                        });
                    ui.add_space(12.0);
                }
                
                // Import button
                if ui.add_enabled(
                    !self.import_path.is_empty(),
                    egui::Button::new(RichText::new("⬆ Import").size(14.0).color(Color32::WHITE))
                        .fill(SUCCESS)
                        .min_size(Vec2::new(120.0, 36.0))
                ).clicked() {
                    *action = Some(ExportImportAction::Import(self.import_path.clone()));
                }
                
                // Result message
                if let Some(result) = &self.last_import_result {
                    ui.add_space(12.0);
                    let (icon, color) = if result.success { ("✓", SUCCESS) } else { ("✗", ERROR) };
                    ui.label(RichText::new(format!("{} {}", icon, result.message)).size(12.0).color(color));
                }
            });
    }
    
    fn render_batch_tab(&mut self, ui: &mut egui::Ui, action: &mut Option<ExportImportAction>) {
        egui::Frame::none()
            .fill(BG_WIDGET.gamma_multiply(0.7))
            .stroke(Stroke::new(1.0, BG_WIDGET))
            .rounding(Rounding::same(12.0))
            .inner_margin(20.0)
            .show(ui, |ui| {
                ui.label(RichText::new("Batch Import from CSV/TSV").size(13.0).color(TEXT_PRIMARY).strong());
                ui.add_space(4.0);
                ui.label(RichText::new("Import multiple concepts from a CSV file with format: content, confidence (optional)")
                    .size(11.0).color(TEXT_MUTED));
                
                ui.add_space(16.0);
                
                ui.horizontal(|ui| {
                    if ui.button(RichText::new("📁 Choose CSV...").size(13.0)).clicked() {
                        self.batch_path = "~/Documents/concepts.csv".to_string();
                    }
                    
                    ui.add_space(8.0);
                    
                    if self.batch_path.is_empty() {
                        ui.label(RichText::new("No file selected").size(11.0).color(TEXT_MUTED));
                    } else {
                        ui.label(RichText::new(&self.batch_path).size(11.0).color(TEXT_PRIMARY));
                    }
                });
                
                ui.add_space(16.0);
                
                // Progress bar (if running)
                if self.batch_progress.is_running || self.batch_progress.completed > 0 {
                    ui.label(RichText::new(format!(
                        "Progress: {}/{} ({:.0}%)",
                        self.batch_progress.completed,
                        self.batch_progress.total,
                        self.batch_progress.percent()
                    )).size(12.0).color(TEXT_SECONDARY));
                    
                    ui.add_space(4.0);
                    
                    let bar_rect = ui.allocate_exact_size(Vec2::new(ui.available_width() - 20.0, 12.0), egui::Sense::hover()).0;
                    ui.painter().rect_filled(bar_rect, Rounding::same(6.0), BG_DARK);
                    
                    let fill_width = bar_rect.width() * (self.batch_progress.percent() / 100.0);
                    let fill_rect = egui::Rect::from_min_size(bar_rect.min, Vec2::new(fill_width, bar_rect.height()));
                    ui.painter().rect_filled(fill_rect, Rounding::same(6.0), PRIMARY);
                    
                    if self.batch_progress.errors > 0 {
                        ui.add_space(4.0);
                        ui.label(RichText::new(format!("Errors: {}", self.batch_progress.errors)).size(11.0).color(ERROR));
                    }
                    
                    ui.add_space(12.0);
                }
                
                // Process button
                if ui.add_enabled(
                    !self.batch_path.is_empty() && !self.batch_progress.is_running,
                    egui::Button::new(RichText::new("▶ Process Batch").size(14.0))
                        .min_size(Vec2::new(140.0, 36.0))
                ).clicked() {
                    *action = Some(ExportImportAction::BatchImport(self.batch_path.clone()));
                }
            });
    }
    
    /// Set export result
    pub fn set_export_result(&mut self, success: bool, path: &str, concepts: usize, edges: usize, message: &str) {
        self.last_export_result = Some(ExportResult {
            success,
            path: path.to_string(),
            concepts_exported: concepts,
            edges_exported: edges,
            message: message.to_string(),
        });
    }
    
    /// Set import result
    pub fn set_import_result(&mut self, success: bool, concepts: usize, edges: usize, errors: usize, message: &str) {
        self.last_import_result = Some(ImportResult {
            success,
            concepts_imported: concepts,
            edges_imported: edges,
            errors,
            message: message.to_string(),
        });
    }
}

/// Actions from export/import panel
#[derive(Debug, Clone)]
pub enum ExportImportAction {
    Export(String),
    Import(String),
    BatchImport(String),
    CancelBatch,
}
