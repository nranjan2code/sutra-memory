//! Centralized configuration for Sutra Desktop Edition
//!
//! Single source of truth for all configuration values.
//! Eliminates scattered hardcoded constants across 8+ files.

use once_cell::sync::Lazy;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// Desktop application configuration
///
/// All configuration values centralized here to eliminate hardcoding.
/// Uses const for compile-time constants and runtime config for user settings.
#[derive(Debug, Clone)]
pub struct AppConfig {
    /// Vector dimension for embeddings (matches all-mpnet-base-v2)
    pub vector_dimension: usize,

    /// Memory threshold for adaptive reconciler (concepts before persistence)
    pub memory_threshold: usize,

    /// Reconciler base interval in milliseconds
    pub reconciler_interval_ms: u64,

    /// Maximum analytics history entries (24 hours at 1 entry/min)
    pub analytics_max_history: usize,

    /// Maximum undo/redo history entries
    pub undo_max_history: usize,

    /// Maximum activity log entries
    pub activity_log_max: usize,

    /// Default font size
    pub default_font_size: f32,

    /// Batch learning chunk size
    pub batch_chunk_size: usize,

    /// Default window width
    pub default_window_width: f32,

    /// Default window height
    pub default_window_height: f32,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            vector_dimension: 768, // Matches all-mpnet-base-v2 model
            memory_threshold: 10_000, // Desktop default (smaller than server)
            reconciler_interval_ms: 100, // Performance tuned
            analytics_max_history: 1440, // 24 hours at 1 entry/min
            undo_max_history: 100, // Memory bound
            activity_log_max: 100, // UI display limit
            default_font_size: 14.0, // Readable default
            batch_chunk_size: 50, // Batch learning chunk size
            default_window_width: 1200.0,
            default_window_height: 800.0,
        }
    }
}

/// Global application configuration (lazy-initialized)
pub static CONFIG: Lazy<AppConfig> = Lazy::new(AppConfig::default);

/// Persistent user settings
///
/// Settings that persist across app restarts.
/// Stored in JSON format in platform-appropriate location.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserSettings {
    /// Selected theme mode
    pub theme_mode: String, // "dark", "light", "high_contrast"

    /// Font size
    pub font_size: f32,

    /// Window width
    pub window_width: f32,

    /// Window height
    pub window_height: f32,

    /// Show onboarding on next launch
    pub show_onboarding: bool,

    /// Last used data directory
    pub last_data_dir: Option<String>,

    /// Auto-save interval in seconds (0 = disabled)
    pub auto_save_interval: u64,
}

impl Default for UserSettings {
    fn default() -> Self {
        Self {
            theme_mode: "dark".to_string(),
            font_size: CONFIG.default_font_size,
            window_width: CONFIG.default_window_width,
            window_height: CONFIG.default_window_height,
            show_onboarding: true, // Show on first launch
            last_data_dir: None,
            auto_save_interval: 300, // 5 minutes
        }
    }
}

impl UserSettings {
    /// Get path to settings file
    fn config_path() -> PathBuf {
        if let Some(proj_dirs) = directories::ProjectDirs::from("ai", "sutra", "SutraDesktop") {
            let config_dir = proj_dirs.config_dir();
            std::fs::create_dir_all(config_dir).ok();
            config_dir.join("settings.json")
        } else {
            // Fallback to current directory
            PathBuf::from("settings.json")
        }
    }

    /// Load settings from disk
    pub fn load() -> Self {
        let path = Self::config_path();

        match std::fs::read_to_string(&path) {
            Ok(data) => {
                match serde_json::from_str(&data) {
                    Ok(settings) => settings,
                    Err(e) => {
                        tracing::warn!("Failed to parse settings: {}, using defaults", e);
                        Default::default()
                    }
                }
            }
            Err(_) => {
                // First launch or settings deleted
                Default::default()
            }
        }
    }

    /// Save settings to disk
    pub fn save(&self) -> Result<(), std::io::Error> {
        let path = Self::config_path();

        let json = serde_json::to_string_pretty(self)
            .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;

        std::fs::write(path, json)?;

        Ok(())
    }

    /// Validate settings (ensure values are within reasonable bounds)
    pub fn validate(&mut self) {
        // Font size bounds
        self.font_size = self.font_size.clamp(8.0, 32.0);

        // Window size bounds
        self.window_width = self.window_width.clamp(800.0, 4096.0);
        self.window_height = self.window_height.clamp(600.0, 2160.0);

        // Auto-save interval bounds (0 = disabled, max 1 hour)
        if self.auto_save_interval > 3600 {
            self.auto_save_interval = 3600;
        }

        // Validate theme mode
        if !["dark", "light", "high_contrast"].contains(&self.theme_mode.as_str()) {
            tracing::warn!("Invalid theme mode: {}, using dark", self.theme_mode);
            self.theme_mode = "dark".to_string();
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    // ========================================================================
    // AppConfig Tests
    // ========================================================================

    #[test]
    fn test_config_defaults() {
        let config = AppConfig::default();
        assert_eq!(config.vector_dimension, 768);
        assert_eq!(config.memory_threshold, 10_000);
        assert_eq!(config.analytics_max_history, 1440);
    }

    #[test]
    fn test_config_all_fields() {
        let config = AppConfig::default();
        assert_eq!(config.reconciler_interval_ms, 100);
        assert_eq!(config.undo_max_history, 100);
        assert_eq!(config.activity_log_max, 100);
        assert_eq!(config.default_font_size, 14.0);
        assert_eq!(config.batch_chunk_size, 50);
        assert_eq!(config.default_window_width, 1200.0);
        assert_eq!(config.default_window_height, 800.0);
    }

    #[test]
    fn test_config_singleton() {
        // Verify CONFIG is accessible
        assert_eq!(CONFIG.vector_dimension, 768);
        assert_eq!(CONFIG.memory_threshold, 10_000);
    }

    #[test]
    fn test_config_clone() {
        let config1 = AppConfig::default();
        let config2 = config1.clone();
        assert_eq!(config1.vector_dimension, config2.vector_dimension);
        assert_eq!(config1.memory_threshold, config2.memory_threshold);
    }

    // ========================================================================
    // UserSettings Tests
    // ========================================================================

    #[test]
    fn test_user_settings_defaults() {
        let settings = UserSettings::default();
        assert_eq!(settings.theme_mode, "dark");
        assert_eq!(settings.font_size, 14.0);
        assert_eq!(settings.window_width, 1200.0);
        assert_eq!(settings.window_height, 800.0);
        assert_eq!(settings.show_onboarding, true);
        assert_eq!(settings.last_data_dir, None);
        assert_eq!(settings.auto_save_interval, 300);
    }

    #[test]
    fn test_font_size_validation_upper_bound() {
        let mut settings = UserSettings::default();
        settings.font_size = 100.0;
        settings.validate();
        assert_eq!(settings.font_size, 32.0);
    }

    #[test]
    fn test_font_size_validation_lower_bound() {
        let mut settings = UserSettings::default();
        settings.font_size = 4.0;
        settings.validate();
        assert_eq!(settings.font_size, 8.0);
    }

    #[test]
    fn test_font_size_validation_valid_range() {
        let mut settings = UserSettings::default();
        settings.font_size = 16.0;
        settings.validate();
        assert_eq!(settings.font_size, 16.0);
    }

    #[test]
    fn test_window_width_validation() {
        let mut settings = UserSettings::default();
        settings.window_width = 10000.0;
        settings.validate();
        assert_eq!(settings.window_width, 4096.0);

        settings.window_width = 500.0;
        settings.validate();
        assert_eq!(settings.window_width, 800.0);
    }

    #[test]
    fn test_window_height_validation() {
        let mut settings = UserSettings::default();
        settings.window_height = 3000.0;
        settings.validate();
        assert_eq!(settings.window_height, 2160.0);

        settings.window_height = 400.0;
        settings.validate();
        assert_eq!(settings.window_height, 600.0);
    }

    #[test]
    fn test_auto_save_interval_validation() {
        let mut settings = UserSettings::default();
        settings.auto_save_interval = 5000;
        settings.validate();
        assert_eq!(settings.auto_save_interval, 3600);

        settings.auto_save_interval = 0;
        settings.validate();
        assert_eq!(settings.auto_save_interval, 0); // 0 is valid (disabled)
    }

    #[test]
    fn test_theme_mode_validation_invalid() {
        let mut settings = UserSettings::default();
        settings.theme_mode = "invalid".to_string();
        settings.validate();
        assert_eq!(settings.theme_mode, "dark");
    }

    #[test]
    fn test_theme_mode_validation_valid() {
        let mut settings = UserSettings::default();

        settings.theme_mode = "light".to_string();
        settings.validate();
        assert_eq!(settings.theme_mode, "light");

        settings.theme_mode = "high_contrast".to_string();
        settings.validate();
        assert_eq!(settings.theme_mode, "high_contrast");
    }

    #[test]
    fn test_settings_serialization() {
        let settings = UserSettings::default();
        let json = serde_json::to_string(&settings).unwrap();
        let deserialized: UserSettings = serde_json::from_str(&json).unwrap();

        assert_eq!(settings.theme_mode, deserialized.theme_mode);
        assert_eq!(settings.font_size, deserialized.font_size);
        assert_eq!(settings.window_width, deserialized.window_width);
        assert_eq!(settings.window_height, deserialized.window_height);
    }

    #[test]
    fn test_settings_with_last_data_dir() {
        let mut settings = UserSettings::default();
        settings.last_data_dir = Some("/custom/path".to_string());

        let json = serde_json::to_string(&settings).unwrap();
        let deserialized: UserSettings = serde_json::from_str(&json).unwrap();

        assert_eq!(deserialized.last_data_dir, Some("/custom/path".to_string()));
    }

    #[test]
    fn test_settings_clone() {
        let settings1 = UserSettings::default();
        let settings2 = settings1.clone();
        assert_eq!(settings1.theme_mode, settings2.theme_mode);
        assert_eq!(settings1.font_size, settings2.font_size);
    }

    // ========================================================================
    // Validation Edge Cases
    // ========================================================================

    #[test]
    fn test_multiple_validation_calls() {
        let mut settings = UserSettings::default();
        settings.font_size = 100.0;
        settings.window_width = 10000.0;
        settings.theme_mode = "invalid".to_string();

        settings.validate();

        assert_eq!(settings.font_size, 32.0);
        assert_eq!(settings.window_width, 4096.0);
        assert_eq!(settings.theme_mode, "dark");
    }

    #[test]
    fn test_validation_idempotent() {
        let mut settings = UserSettings::default();
        settings.font_size = 100.0;

        settings.validate();
        let first_result = settings.font_size;

        settings.validate();
        assert_eq!(settings.font_size, first_result);
    }
}
