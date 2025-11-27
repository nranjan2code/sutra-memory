//! Knowledge browser panel - Premium visual design

use eframe::egui::{self, Color32, RichText, Rounding, ScrollArea, Stroke, Vec2};
use crate::types::ConceptInfo;
use crate::theme::{PRIMARY, SECONDARY, ACCENT, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, SUCCESS, BG_PANEL, BG_WIDGET, card_frame};

pub struct KnowledgePanel {
    pub concepts: Vec<ConceptInfo>,
    pub selected_concept: Option<String>,
    pub search_query: String,
    pub is_loading: bool,
    pub delete_confirmation: Option<String>,
}

impl Default for KnowledgePanel {
    fn default() -> Self {
        Self {
            concepts: Vec::new(),
            selected_concept: None,
            search_query: String::new(),
            is_loading: false,
            delete_confirmation: None,
        }
    }
}

impl KnowledgePanel {
    pub fn ui(&mut self, ui: &mut egui::Ui) -> Option<KnowledgeAction> {
        let mut action = None;
        
        ui.vertical(|ui| {
            // Clean header
            ui.horizontal(|ui| {
                ui.label(RichText::new("📚 Knowledge").size(20.0).color(TEXT_PRIMARY).strong());
                
                ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                    // Refresh button
                    if ui.button("🔄").on_hover_text("Refresh").clicked() {
                        action = Some(KnowledgeAction::Refresh);
                    }
                    
                    ui.add_space(8.0);
                    
                    // Count
                    ui.label(RichText::new(format!("{} concepts", self.concepts.len()))
                        .size(12.0).color(TEXT_MUTED));
                });
            });
            
            ui.add_space(12.0);
            
            // Search bar - full width
            let search_resp = ui.add(
                egui::TextEdit::singleline(&mut self.search_query)
                    .hint_text("🔍 Search concepts...")
                    .desired_width(ui.available_width())
            );
            if search_resp.changed() {
                action = Some(KnowledgeAction::Search(self.search_query.clone()));
            }
            
            ui.add_space(16.0);
            
            // Content area
            if self.is_loading {
                ui.vertical_centered(|ui| {
                    ui.add_space(40.0);
                    ui.spinner();
                    ui.add_space(8.0);
                    ui.label(RichText::new("Loading...").color(TEXT_MUTED));
                });
            } else if self.concepts.is_empty() {
                if let Some(act) = self.empty_state(ui) {
                    action = Some(act);
                }
            } else {
                // Concepts grid
                ScrollArea::vertical()
                    .auto_shrink([false; 2])
                    .show(ui, |ui| {
                        self.concepts_grid(ui, &mut action);
                    });
            }
        });

        // Delete confirmation modal
        if let Some(concept_id) = &self.delete_confirmation {
            let mut should_close = false;
            let mut confirmed = false;
            let id_to_delete = concept_id.clone();

            egui::Window::new("Delete Concept")
                .collapsible(false)
                .resizable(false)
                .anchor(egui::Align2::CENTER_CENTER, Vec2::ZERO)
                .show(ui.ctx(), |ui| {
                    ui.vertical_centered(|ui| {
                        ui.add_space(8.0);
                        ui.label(RichText::new("Are you sure you want to delete this concept?").size(16.0));
                        ui.label(RichText::new("This action cannot be undone.").size(12.0).color(TEXT_MUTED));
                        ui.add_space(16.0);
                        
                        ui.horizontal(|ui| {
                            if ui.button("Cancel").clicked() {
                                should_close = true;
                            }
                            
                            let delete_btn = egui::Button::new(RichText::new("Delete").color(Color32::WHITE))
                                .fill(crate::theme::ERROR);
                            
                            if ui.add(delete_btn).clicked() {
                                confirmed = true;
                                should_close = true;
                            }
                        });
                        ui.add_space(8.0);
                    });
                });

            if should_close {
                self.delete_confirmation = None;
            }
            if confirmed {
                action = Some(KnowledgeAction::DeleteConcept(id_to_delete));
            }
        }
        
        action
    }
    
    fn concepts_grid(&mut self, ui: &mut egui::Ui, action: &mut Option<KnowledgeAction>) {
        let available_width = ui.available_width();
        let card_width = 300.0;
        let spacing = 12.0;
        let columns = ((available_width + spacing) / (card_width + spacing)).floor().max(1.0) as usize;
        
        egui::Grid::new("concepts_grid")
            .min_col_width(card_width)
            .spacing(Vec2::splat(spacing))
            .show(ui, |ui| {
                for (i, concept) in self.concepts.iter().enumerate() {
                    if i > 0 && i % columns == 0 {
                        ui.end_row();
                    }
                    
                    // Render card
                    let response = self.compact_concept_card(ui, concept);
                    
                    // Handle click
                    if response.clicked() {
                        *action = Some(KnowledgeAction::SelectConcept(concept.id.clone()));
                    }
                    
                    // Context menu for delete
                    response.context_menu(|ui| {
                        if ui.button(RichText::new("🗑 Delete").color(crate::theme::ERROR)).clicked() {
                            self.delete_confirmation = Some(concept.id.clone());
                            ui.close_menu();
                        }
                    });
                }
            });
    }
    
    fn render_concept_card(&self, ui: &mut egui::Ui, concept: &ConceptInfo) -> bool {
        egui::Frame::none()
            .fill(BG_WIDGET)
            .stroke(Stroke::new(1.0, BG_WIDGET.gamma_multiply(1.5)))
            .rounding(Rounding::same(8.0))
            .inner_margin(12.0)
            .show(ui, |ui| {
                ui.horizontal(|ui| {
                    // Icon
                    ui.label(RichText::new("📎").size(16.0));
                    
                    ui.add_space(8.0);
                    
                    // Content
                    ui.vertical(|ui| {
                        let preview = if concept.content.len() > 80 {
                            format!("{}...", &concept.content[..80])
                        } else {
                            concept.content.clone()
                        };
                        
                        ui.label(RichText::new(preview).size(14.0).color(TEXT_PRIMARY));
                        
                        ui.add_space(4.0);
                        
                        ui.horizontal(|ui| {
                            ui.label(RichText::new(format!("ID: {}", &concept.id[..8])).size(11.0).color(TEXT_MUTED));
                            ui.add_space(12.0);
                            ui.label(RichText::new(format!("Confidence: {:.1}%", concept.confidence * 100.0)).size(11.0).color(TEXT_MUTED));
                        });
                    });
                });
            })
            .response
            .clicked()
    }
    
    fn compact_concept_card(&self, ui: &mut egui::Ui, concept: &ConceptInfo) -> egui::Response {
        egui::Frame::none()
            .fill(BG_WIDGET)
            .stroke(Stroke::new(1.0, BG_WIDGET.gamma_multiply(1.5)))
            .rounding(Rounding::same(8.0))
            .inner_margin(12.0)
            .show(ui, |ui| {
                ui.set_width(ui.available_width());
                
                ui.vertical(|ui| {
                    // Content preview
                    let content = if concept.content.len() > 120 {
                        format!("{}...", &concept.content[..117])
                    } else {
                        concept.content.clone()
                    };
                    
                    ui.label(RichText::new(content).size(14.0).color(TEXT_PRIMARY));
                    ui.add_space(8.0);
                    
                    // Bottom row with stats
                    ui.horizontal(|ui| {
                        // Confidence badge
                        let conf_color = if concept.confidence > 0.8 { 
                            SUCCESS 
                        } else if concept.confidence > 0.6 { 
                            ACCENT 
                        } else { 
                            TEXT_MUTED 
                        };
                        
                        ui.label(RichText::new(format!("{}%", (concept.confidence * 100.0) as u8))
                            .size(11.0).color(conf_color))
                            .on_hover_text("Confidence");
                        
                        ui.add_space(12.0);
                        
                        // Connections
                        if !concept.neighbors.is_empty() {
                            ui.label(RichText::new(format!("🔗 {}", concept.neighbors.len()))
                                .size(11.0).color(TEXT_MUTED))
                                .on_hover_text("Connections");
                        }
                        
                        ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                            // Short ID
                            ui.label(RichText::new(&concept.id[..8])
                                .size(10.0).color(TEXT_MUTED).monospace())
                                .on_hover_text(&concept.id);
                        });
                    });
                });
            }).response
    }
    
    fn empty_state(&self, ui: &mut egui::Ui) -> Option<KnowledgeAction> {
        let mut action = None;
        ui.vertical_centered(|ui| {
            ui.add_space(40.0);
            
            // Simple empty state
            ui.label(RichText::new("📚").size(48.0));
            ui.add_space(16.0);
            
            ui.label(RichText::new("No concepts yet").size(16.0).color(TEXT_PRIMARY));
            ui.add_space(8.0);
            
            ui.label(RichText::new("Start learning by going to Chat and typing:").size(13.0).color(TEXT_MUTED));
            ui.add_space(12.0);
            
            // Example command
            egui::Frame::none()
                .fill(BG_WIDGET)
                .rounding(Rounding::same(6.0))
                .inner_margin(12.0)
                .show(ui, |ui| {
                    ui.label(RichText::new("/learn The sky is blue").size(12.0).color(TEXT_PRIMARY).monospace());
                });
                
            ui.add_space(20.0);
            
            // Start Learning button
            let btn = egui::Button::new(RichText::new("Start Learning").color(Color32::WHITE))
                .fill(PRIMARY)
                .rounding(Rounding::same(8.0))
                .min_size(Vec2::new(120.0, 32.0));
                
            if ui.add(btn).clicked() {
                action = Some(KnowledgeAction::SwitchToChat);
            }
        });
        action
    }
    
    pub fn set_concepts(&mut self, concepts: Vec<ConceptInfo>) {
        self.concepts = concepts;
        self.is_loading = false;
    }
}

#[derive(Debug, Clone)]
pub enum KnowledgeAction {
    Search(String),
    Refresh,
    SelectConcept(String),
    DeleteConcept(String),
    SwitchToChat,
}
