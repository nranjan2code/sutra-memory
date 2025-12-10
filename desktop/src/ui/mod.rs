//! UI components for Sutra Desktop
//!
//! This module contains all UI panels and components for the enhanced desktop application.
//! Each panel is designed to leverage the full capabilities of the sutra-storage engine
//! while maintaining a clean, production-grade user experience.

// Core panels (original)
pub mod chat;
pub mod knowledge;
pub mod quick_learn;
pub mod settings;
pub mod sidebar;
pub mod status_bar;

// Enhanced panels (new)
pub mod analytics;
pub mod causal_view;
pub mod export_import;
pub mod graph_view;
pub mod query_builder;
pub mod reasoning_paths;
pub mod temporal_view;

// New UX features (v3.4.0)
pub mod home;
pub mod onboarding;
pub mod undo_redo;

// Re-exports for core panels
pub use chat::{ChatAction, ChatPanel};
pub use knowledge::{KnowledgeAction, KnowledgePanel};
pub use quick_learn::{QuickLearnAction, QuickLearnPanel};
pub use settings::{SettingsAction, SettingsPanel, StorageStatsUI, StorageStatus};
pub use sidebar::{Sidebar, SidebarView};
pub use status_bar::{ConnectionStatus, StatusBar};

// Re-exports for enhanced panels (use actual struct/enum names from modules)
pub use analytics::{AnalyticsAction, AnalyticsDashboard};
pub use causal_view::{CausalView, CausalViewAction};
pub use export_import::{ExportImportAction, ExportImportPanel};
pub use graph_view::{GraphAction, GraphView};
pub use query_builder::{QueryBuilder, QueryBuilderAction};
pub use reasoning_paths::{ReasoningPathsAction, ReasoningPathsPanel};
pub use temporal_view::{TemporalView, TemporalViewAction};

// Re-exports for new UX features
pub use home::{DashboardActivityType, HomeAction, HomeDashboard};
pub use onboarding::{is_first_launch, mark_onboarding_complete, OnboardingAction, OnboardingTour};
pub use undo_redo::{Command, CommandHistory, UndoRedoResult};
