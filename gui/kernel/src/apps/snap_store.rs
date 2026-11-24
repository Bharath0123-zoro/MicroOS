extern crate alloc;

use alloc::format;
use alloc::string::String;
use alloc::vec::Vec;
use crate::graphics::color::Color;
use crate::graphics::surface::Surface;

#[derive(Clone, Copy)]
pub struct SnapItem {
    pub id: &'static str,
    pub name: &'static str,
    pub summary: &'static str,
    pub version: &'static str,
    pub channel: &'static str,
    pub size: &'static str,
    pub confinement: &'static str,
    pub publisher: &'static str,
    pub category_idx: usize, // 1: Dev, 2: Prod, 3: Media, 4: Util
    pub is_installed: bool,
}

pub struct SnapStoreApp {
    pub selected_idx: usize,
    pub active_category: usize, // 0: Featured, 1: Dev, 2: Prod, 3: Media, 4: Util
    pub items: Vec<SnapItem>,
    pub status_log: String,
    pub progress: usize,
    pub is_installing: bool,
    pub request_fullscreen: bool,
}

impl SnapStoreApp {
    pub fn new() -> Self {
        let initial_items = alloc::vec![
            SnapItem {
                id: "code",
                name: "Visual Studio Code",
                summary: "Code editing. Redefined. Official Microsoft IDE.",
                version: "1.95.3",
                channel: "latest/stable",
                size: "94 MB",
                confinement: "classic",
                publisher: "Microsoft*",
                category_idx: 1,
                is_installed: true,
            },
            SnapItem {
                id: "firefox",
                name: "Firefox Web Browser",
                summary: "Fast, private and secure web browser by Mozilla.",
                version: "132.0.2",
                channel: "latest/stable",
                size: "82 MB",
                confinement: "strict",
                publisher: "Mozilla*",
                category_idx: 2,
                is_installed: true,
            },
            SnapItem {
                id: "spotify",
                name: "Spotify Music",
                summary: "Stream millions of songs and podcasts on your desktop.",
                version: "1.2.50",
                channel: "latest/stable",
                size: "112 MB",
                confinement: "strict",
                publisher: "Spotify*",
                category_idx: 3,
                is_installed: false,
            },
            SnapItem {
                id: "vlc",
                name: "VLC Media Player",
                summary: "The ultimate open source media player for video & audio.",
                version: "3.0.21",
                channel: "latest/stable",
                size: "48 MB",
                confinement: "strict",
                publisher: "VideoLAN*",
                category_idx: 3,
                is_installed: true,
            },
            SnapItem {
                id: "docker",
                name: "Docker CE Engine",
                summary: "Pack, ship and run any application as containers.",
                version: "27.3.1",
                channel: "latest/stable",
                size: "145 MB",
                confinement: "classic",
                publisher: "Docker Inc.*",
                category_idx: 1,
                is_installed: false,
            },
            SnapItem {
                id: "blender",
                name: "Blender 3D Suite",
                summary: "Free and open source 3D modeling & animation pipeline.",
                version: "4.2.3",
                channel: "latest/stable",
                size: "230 MB",
                confinement: "classic",
                publisher: "Blender Fdn*",
                category_idx: 3,
                is_installed: false,
            },
            SnapItem {
                id: "postman",
                name: "Postman API Platform",
                summary: "Build, test, and collaborate on REST & GraphQL APIs.",
                version: "11.19.0",
                channel: "latest/stable",
                size: "118 MB",
                confinement: "classic",
                publisher: "Postman Inc.*",
                category_idx: 1,
                is_installed: false,
            },
            SnapItem {
                id: "telegram",
                name: "Telegram Desktop",
                summary: "Fast, encrypted and secure desktop messaging app.",
                version: "5.7.1",
                channel: "latest/stable",
                size: "64 MB",
                confinement: "strict",
                publisher: "Telegram FZ*",
                category_idx: 2,
                is_installed: false,
            },
            SnapItem {
                id: "discord",
                name: "Discord Chat",
                summary: "All-in-one voice and text chat for developers & communities.",
                version: "0.0.71",
                channel: "latest/stable",
                size: "89 MB",
                confinement: "strict",
                publisher: "Snapcrafters",
                category_idx: 2,
                is_installed: false,
            },
            SnapItem {
                id: "htop",
                name: "Htop Process Viewer",
                summary: "Interactive process viewer and system hardware monitor.",
                version: "3.3.0",
                channel: "latest/stable",
                size: "2.1 MB",
                confinement: "classic",
                publisher: "MaxiBerta",
                category_idx: 4,
                is_installed: true,
            },
            SnapItem {
                id: "obs-studio",
                name: "OBS Studio",
                summary: "Professional software for video recording and live streaming.",
                version: "30.2.3",
                channel: "latest/stable",
                size: "124 MB",
                confinement: "classic",
                publisher: "Snapcrafters",
                category_idx: 3,
                is_installed: false,
            },
            SnapItem {
                id: "calculator",
                name: "GNOME Calculator",
                summary: "Solve financial, scientific and programmer equations.",
                version: "47.0",
                channel: "latest/stable",
                size: "4.8 MB",
                confinement: "strict",
                publisher: "Canonical*",
                category_idx: 4,
                is_installed: true,
            },
        ];

        Self {
            selected_idx: 0,
            active_category: 0,
            items: initial_items,
            status_log: String::from("Snap Store ready. Connected to Canonical Snapcraft repository."),
            progress: 100,
            is_installing: false,
            request_fullscreen: false,
        }
    }

    pub fn tick(&mut self) {
        if self.is_installing {
            self.progress += 10;
            if self.progress >= 100 {
                self.progress = 100;
                self.is_installing = false;
                if self.selected_idx < self.items.len() {
                    let snap_id = self.items[self.selected_idx].id;
                    self.items[self.selected_idx].is_installed = true;
                    self.status_log = format!(
                        "[+] Snap '{}' successfully installed & mounted to /snap/{}/current",
                        snap_id, snap_id
                    );
                }
            }
        }
    }

    pub fn filtered_indices(&self) -> Vec<usize> {
        let mut list = Vec::new();
        for (i, item) in self.items.iter().enumerate() {
            if self.active_category == 0 || item.category_idx == self.active_category {
                list.push(i);
            }
        }
        list
    }

    pub fn handle_click(&mut self, rel_x: i32, rel_y: i32) {
        // 1. Category Tab clicks (rel_y: 46..72)
        if rel_y >= 46 && rel_y <= 72 {
            let tab_w = 110;
            let tab_start_x = 16;
            for cat in 0..5 {
                let tx = tab_start_x + (cat as i32 * (tab_w + 6));
                if rel_x >= tx && rel_x < tx + tab_w {
                    self.active_category = cat;
                    let filtered = self.filtered_indices();
                    if !filtered.is_empty() {
                        self.selected_idx = filtered[0];
                    }
                    return;
                }
            }
        }

        // 2. Fullscreen Toggle Button in Store Header: rel_x: 610..740, rel_y: 12..38
        if rel_x >= 610 && rel_x <= 740 && rel_y >= 12 && rel_y <= 38 {
            self.request_fullscreen = true;
            self.status_log = String::from("[*] Toggling Full Screen mode for Snap Store workspace.");
            return;
        }

        // 3. Package row selection: rel_x: 16..460, rel_y: 104..380
        if rel_x >= 16 && rel_x <= 460 && rel_y >= 104 {
            let row = (rel_y - 104) / 28;
            let filtered = self.filtered_indices();
            if (row as usize) < filtered.len() {
                self.selected_idx = filtered[row as usize];
                return;
            }
        }

        // 4. Action Button [ Install / Remove / Launch ] in right preview pane:
        // rel_x: 480..740, rel_y: 260..300
        if rel_x >= 480 && rel_x <= 740 && rel_y >= 260 && rel_y <= 300 {
            if self.selected_idx < self.items.len() {
                if !self.items[self.selected_idx].is_installed {
                    // Start install
                    self.is_installing = true;
                    self.progress = 10;
                    let snap_id = self.items[self.selected_idx].id;
                    self.status_log = format!(
                        "[*] Fetching squashfs snap for '{}' from canonical snapcraft CDN...",
                        snap_id
                    );
                } else {
                    // Remove
                    self.items[self.selected_idx].is_installed = false;
                    let snap_id = self.items[self.selected_idx].id;
                    self.status_log = format!(
                        "[-] Snap '{}' unmounted and removed from /var/lib/snapd/snaps",
                        snap_id
                    );
                }
            }
        }
    }

    pub fn render(&self, surface: &mut Surface, win_x: i32, win_y: i32, win_w: usize, win_h: usize) {
        // Background
        surface.draw_rect(win_x, win_y, win_w, win_h, Color::WIN_BG);

        // Header Banner (Ubuntu Aubergine/Dark Slate Theme)
        let header_h = 42;
        surface.draw_rect(win_x, win_y, win_w, header_h, Color::rgb(44, 21, 56)); // Ubuntu dark aubergine
        surface.draw_line_h(win_x, win_y + header_h as i32, win_w, Color::rgb(233, 84, 32)); // Snapcraft Orange accent

        // Draw Snapcraft Origami Diamond Logo
        let logo_x = win_x + 16;
        let logo_y = win_y + 9;
        // Orange diamond / origami polygons
        surface.draw_rect(logo_x, logo_y + 4, 16, 16, Color::rgb(233, 84, 32)); // Snap orange
        surface.draw_line_h(logo_x + 3, logo_y + 12, 10, Color::WHITE);
        surface.draw_line_v(logo_x + 8, logo_y + 7, 10, Color::WHITE);

        // Title and Subtitle
        surface.draw_string(win_x + 40, win_y + 8, "SNAP STORE", Color::WHITE);
        surface.draw_string(win_x + 150, win_y + 12, "Canonical Snapcraft Software Center (Ubuntu & Linux)", Color::rgb(216, 180, 254));

        // Fullscreen Toggle Quick Button in Header
        let fs_btn_x = win_x + win_w as i32 - 145;
        surface.draw_rect(fs_btn_x, win_y + 9, 130, 24, Color::rgb(77, 33, 98));
        surface.draw_rect_outline(fs_btn_x, win_y + 9, 130, 24, Color::rgb(233, 84, 32));
        surface.draw_string(fs_btn_x + 8, win_y + 14, "[ Full Screen ]", Color::WHITE);

        // Category Navigation Tabs (rel_y: 46..72)
        let tab_bar_y = win_y + 46;
        let tab_w = 110;
        let categories = [
            "All Featured",
            "Development",
            "Productivity",
            "Games & Media",
            "Utilities",
        ];

        for (i, cat_name) in categories.iter().enumerate() {
            let tx = win_x + 16 + (i as i32 * (tab_w + 6));
            let is_active = self.active_category == i;
            let tab_bg = if is_active { Color::rgb(233, 84, 32) } else { Color::SLATE_CARD };
            let tab_fg = if is_active { Color::WHITE } else { Color::SLATE_DARK };
            let tab_border = if is_active { Color::rgb(194, 65, 12) } else { Color::TASKBAR_BORDER };

            surface.draw_rect(tx, tab_bar_y, tab_w as usize, 24, tab_bg);
            surface.draw_rect_outline(tx, tab_bar_y, tab_w as usize, 24, tab_border);
            surface.draw_string(tx + 8, tab_bar_y + 5, cat_name, tab_fg);
        }

        // Layout divider
        let content_y = tab_bar_y + 30;
        let footer_h = 36;
        let avail_h = win_h.saturating_sub(content_y as usize - win_y as usize + footer_h);

        // Left Pane: Snap List Table (Width: 63% of win_w in full-screen)
        let list_w = if win_w > 650 { (win_w * 63) / 100 } else { win_w - 32 };
        let list_x = win_x + 16;

        // Table Header
        surface.draw_rect(list_x, content_y, list_w, 22, Color::SLATE_CARD);
        surface.draw_rect_outline(list_x, content_y, list_w, 22, Color::TASKBAR_BORDER);
        surface.draw_string(list_x + 8, content_y + 4, "PACKAGE", Color::SLATE_DARK);
        surface.draw_string(list_x + 195, content_y + 4, "VERSION", Color::SLATE_DARK);
        surface.draw_string(list_x + 285, content_y + 4, "CONFINEMENT", Color::SLATE_DARK);
        surface.draw_string(list_x + 395, content_y + 4, "STATUS", Color::SLATE_DARK);

        let filtered = self.filtered_indices();
        let max_rows = avail_h.saturating_sub(26) / 28;

        for (row_idx, &orig_idx) in filtered.iter().enumerate().take(max_rows) {
            let item = &self.items[orig_idx];
            let row_y = content_y + 24 + (row_idx as i32 * 28);
            let is_selected = orig_idx == self.selected_idx;

            if is_selected {
                surface.draw_rect(list_x, row_y - 1, list_w, 26, Color::rgb(254, 243, 199)); // highlight gold/amber
                surface.draw_rect_outline(list_x, row_y - 1, list_w, 26, Color::rgb(245, 158, 11));
            } else if row_idx % 2 == 1 {
                surface.draw_rect(list_x, row_y - 1, list_w, 26, Color::rgb(248, 250, 252));
            }

            // Package Name
            surface.draw_string(list_x + 8, row_y + 4, item.name, Color::SLATE_DARK);
            // Version
            surface.draw_string(list_x + 195, row_y + 4, item.version, Color::MUTED_TEXT);

            // Confinement badge
            let conf_bg = if item.confinement == "classic" { Color::rgb(254, 226, 226) } else { Color::rgb(224, 231, 255) };
            let conf_fg = if item.confinement == "classic" { Color::ACCENT_RED } else { Color::ACCENT_BLUE };
            surface.draw_rect(list_x + 285, row_y + 2, 72, 18, conf_bg);
            surface.draw_string(list_x + 292, row_y + 4, item.confinement, conf_fg);

            // Status
            if item.is_installed {
                surface.draw_string(list_x + 395, row_y + 4, "[ Installed ]", Color::ACCENT_GREEN);
            } else {
                surface.draw_string(list_x + 395, row_y + 4, "Available", Color::rgb(148, 163, 184));
            }
        }

        // Right Pane: Snap Details & Actions (Width: remaining area if win_w > 650)
        if win_w > 650 {
            let preview_x = list_x + list_w as i32 + 12;
            let preview_w = win_w.saturating_sub((preview_x - win_x) as usize + 16);

            surface.draw_rect(preview_x, content_y, preview_w, avail_h, Color::WHITE);
            surface.draw_rect_outline(preview_x, content_y, preview_w, avail_h, Color::TASKBAR_BORDER);

            if self.selected_idx < self.items.len() {
                let sel = &self.items[self.selected_idx];

                // Detail Header Card
                surface.draw_rect(preview_x + 12, content_y + 12, preview_w.saturating_sub(24), 65, Color::SLATE_CARD);
                surface.draw_rect_outline(preview_x + 12, content_y + 12, preview_w.saturating_sub(24), 65, Color::TASKBAR_BORDER);

                // Big App Icon
                surface.draw_rect(preview_x + 20, content_y + 20, 48, 48, Color::rgb(233, 84, 32));
                surface.draw_string(preview_x + 30, content_y + 34, "SNAP", Color::WHITE);

                // Title & Publisher
                surface.draw_string(preview_x + 76, content_y + 18, sel.name, Color::SLATE_DARK);
                surface.draw_string(preview_x + 76, content_y + 34, &format!("by {}", sel.publisher), Color::MUTED_TEXT);
                surface.draw_string(preview_x + 76, content_y + 48, &format!("Channel: {}", sel.channel), Color::ACCENT_BLUE);

                // Summary / Description
                surface.draw_string(preview_x + 12, content_y + 90, "Description:", Color::SLATE_DARK);
                surface.draw_string(preview_x + 12, content_y + 108, sel.summary, Color::MUTED_TEXT);

                // Metadata Rows
                let meta_y = content_y + 140;
                surface.draw_line_h(preview_x + 12, meta_y, preview_w.saturating_sub(24), Color::TASKBAR_BORDER);

                surface.draw_string(preview_x + 12, meta_y + 8, "Version:", Color::MUTED_TEXT);
                surface.draw_string(preview_x + 90, meta_y + 8, sel.version, Color::SLATE_DARK);

                surface.draw_string(preview_x + 12, meta_y + 26, "Download:", Color::MUTED_TEXT);
                surface.draw_string(preview_x + 90, meta_y + 26, sel.size, Color::SLATE_DARK);

                surface.draw_string(preview_x + 12, meta_y + 44, "Confinement:", Color::MUTED_TEXT);
                surface.draw_string(preview_x + 115, meta_y + 44, sel.confinement, Color::SLATE_DARK);

                // Install / Remove Action Button (content_y + 205)
                let btn_action_y = content_y + 195;
                let btn_action_w = preview_w.saturating_sub(24);

                if self.is_installing {
                    // Installing Progress Bar
                    surface.draw_rect(preview_x + 12, btn_action_y, btn_action_w, 28, Color::SLATE_CARD);
                    surface.draw_rect_outline(preview_x + 12, btn_action_y, btn_action_w, 28, Color::TASKBAR_BORDER);
                    let bar_w = (btn_action_w * self.progress) / 100;
                    surface.draw_rect(preview_x + 12, btn_action_y, bar_w, 28, Color::rgb(233, 84, 32));
                    surface.draw_string(preview_x + 24, btn_action_y + 7, &format!("Installing... {}%", self.progress), Color::WHITE);
                } else if !sel.is_installed {
                    // Green Install Button
                    surface.draw_rect(preview_x + 12, btn_action_y, btn_action_w, 28, Color::ACCENT_GREEN);
                    surface.draw_rect_outline(preview_x + 12, btn_action_y, btn_action_w, 28, Color::rgb(22, 101, 52));
                    surface.draw_string(preview_x + 24, btn_action_y + 7, "Install Snap Package", Color::WHITE);
                } else {
                    // Red Remove Button
                    surface.draw_rect(preview_x + 12, btn_action_y, btn_action_w, 28, Color::rgb(239, 68, 68));
                    surface.draw_rect_outline(preview_x + 12, btn_action_y, btn_action_w, 28, Color::rgb(185, 28, 28));
                    surface.draw_string(preview_x + 24, btn_action_y + 7, "Installed (Click to Remove)", Color::WHITE);
                }
            }
        }

        // Bottom Telemetry / Status Bar
        let footer_y = win_y + win_h as i32 - 32;
        let footer_w = win_w.saturating_sub(32);
        surface.draw_rect(win_x + 16, footer_y, footer_w, 24, Color::TERMINAL_BG);
        surface.draw_rect_outline(win_x + 16, footer_y, footer_w, 24, Color::SLATE_DARK);
        surface.draw_string(win_x + 24, footer_y + 5, &self.status_log, Color::TERMINAL_GREEN);
    }
}
