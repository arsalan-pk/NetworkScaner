"""
UI styling and theme management for Network Scanner.

This module provides centralized styling management with support
for different themes and professional appearance.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional
from ..core.exceptions import UIError
from ..config.settings import Settings


class UIStyles:
    """
    Centralized UI styling manager for Network Scanner.
    
    Provides consistent theming across all UI components with
    support for different color schemes and professional appearance.
    """
    
    def __init__(self, settings: Optional[Settings] = None) -> None:
        """
        Initialize UI styles manager.
        
        Args:
            settings: Application settings instance
        """
        self.settings = settings or Settings()
        self.theme = self.settings.get('ui.theme', 'dark')
        self._style_cache: Dict[str, Any] = {}
        
    def configure_styles(self) -> None:
        """Configure all ttk styles for the application."""
        try:
            style = ttk.Style()
            
            # Set theme
            available_themes = style.theme_names()
            if 'clam' in available_themes:
                style.theme_use('clam')
            elif 'alt' in available_themes:
                style.theme_use('alt')
            else:
                style.theme_use(available_themes[0])
            
            # Configure base styles
            self._configure_frame_styles(style)
            self._configure_label_styles(style)
            self._configure_button_styles(style)
            self._configure_entry_styles(style)
            self._configure_combobox_styles(style)
            self._configure_notebook_styles(style)
            self._configure_progressbar_styles(style)
            self._configure_treeview_styles(style)
            
        except Exception as e:
            raise UIError(
                f"Failed to configure UI styles: {str(e)}",
                component="StyleManager"
            )
    
    def _configure_frame_styles(self, style: ttk.Style) -> None:
        """Configure frame styles."""
        bg_color = self.settings.get('ui.bg_color', '#2b2b2b')
        
        style.configure("TFrame", background=bg_color)
        style.configure("Card.TFrame", 
                       background=bg_color,
                       relief='raised',
                       borderwidth=1)
        style.configure("Sidebar.TFrame",
                       background=bg_color,
                       relief='sunken',
                       borderwidth=1)
    
    def _configure_label_styles(self, style: ttk.Style) -> None:
        """Configure label styles."""
        bg_color = self.settings.get('ui.bg_color', '#2b2b2b')
        fg_color = self.settings.get('ui.fg_color', '#e0e0e0')
        accent_color = self.settings.get('ui.accent_color', '#4a90e2')
        
        # Base label
        style.configure("TLabel", 
                       background=bg_color,
                       foreground=fg_color,
                       font=("Helvetica", 11))
        
        # Header label
        style.configure("Header.TLabel",
                       font=("Helvetica", 16, "bold"),
                       foreground=accent_color,
                       background=bg_color)
        
        # Subheader label
        style.configure("Subheader.TLabel",
                       font=("Helvetica", 12, "bold"),
                       foreground=fg_color,
                       background=bg_color)
        
        # Status label
        style.configure("Status.TLabel",
                       font=("Helvetica", 10),
                       foreground="#888888",
                       background=bg_color)
        
        # Success label
        style.configure("Success.TLabel",
                       font=("Helvetica", 10, "bold"),
                       foreground="#28a745",
                       background=bg_color)
        
        # Warning label
        style.configure("Warning.TLabel",
                       font=("Helvetica", 10, "bold"),
                       foreground="#ffc107",
                       background=bg_color)
        
        # Error label
        style.configure("Error.TLabel",
                       font=("Helvetica", 10, "bold"),
                       foreground="#dc3545",
                       background=bg_color)
    
    def _configure_button_styles(self, style: ttk.Style) -> None:
        """Configure button styles."""
        bg_color = self.settings.get('ui.bg_color', '#2b2b2b')
        accent_color = self.settings.get('ui.accent_color', '#4a90e2')
        
        # Primary button
        style.configure("TButton",
                       font=("Helvetica", 11, "bold"),
                       background=accent_color,
                       foreground="white",
                       padding=5,
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('TButton',
                 background=[('active', '#357abd'),
                           ('pressed', '#2968a3'),
                           ('disabled', '#cccccc')])
        
        # Secondary button
        style.configure("Secondary.TButton",
                       font=("Helvetica", 11),
                       background="#6c757d",
                       foreground="white",
                       padding=5,
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Secondary.TButton',
                 background=[('active', '#5a6268'),
                           ('pressed', '#495057')])
        
        # Success button
        style.configure("Success.TButton",
                       font=("Helvetica", 11, "bold"),
                       background="#28a745",
                       foreground="white",
                       padding=5,
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Success.TButton',
                 background=[('active', '#218838'),
                           ('pressed', '#1e7e34')])
        
        # Danger button
        style.configure("Danger.TButton",
                       font=("Helvetica", 11, "bold"),
                       background="#dc3545",
                       foreground="white",
                       padding=5,
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Danger.TButton',
                 background=[('active', '#c82333'),
                           ('pressed', '#bd2130')])
    
    def _configure_entry_styles(self, style: ttk.Style) -> None:
        """Configure entry field styles."""
        field_bg = "#3c3f41"
        fg_color = "#ffffff"
        
        style.configure("TEntry",
                       fieldbackground=field_bg,
                       foreground=fg_color,
                       borderwidth=1,
                       relief='solid',
                       font=("Helvetica", 11))
        
        style.map('TEntry',
                 focuscolor=[('focus', accent_color)],
                 bordercolor=[('focus', accent_color)])
    
    def _configure_combobox_styles(self, style: ttk.Style) -> None:
        """Configure combobox styles."""
        field_bg = "#3c3f41"
        fg_color = "#ffffff"
        
        style.configure("TCombobox",
                       fieldbackground=field_bg,
                       foreground=fg_color,
                       borderwidth=1,
                       relief='solid',
                       font=("Helvetica", 11))
        
        style.map('TCombobox',
                 focuscolor=[('focus', accent_color)],
                 bordercolor=[('focus', accent_color)])
    
    def _configure_notebook_styles(self, style: ttk.Style) -> None:
        """Configure notebook (tab) styles."""
        bg_color = self.settings.get('ui.bg_color', '#2b2b2b')
        fg_color = self.settings.get('ui.fg_color', '#e0e0e0')
        accent_color = self.settings.get('ui.accent_color', '#4a90e2')
        
        style.configure("TNotebook",
                       background=bg_color,
                       borderwidth=0)
        
        style.configure("TNotebook.Tab",
                       background="#404040",
                       foreground=fg_color,
                       padding=[12, 8],
                       font=("Helvetica", 10, "bold"))
        
        style.map("TNotebook.Tab",
                 background=[('selected', accent_color),
                           ('active', '#505050')],
                 foreground=[('selected', 'white'),
                           ('active', fg_color)])
    
    def _configure_progressbar_styles(self, style: ttk.Style) -> None:
        """Configure progressbar styles."""
        accent_color = self.settings.get('ui.accent_color', '#4a90e2')
        
        style.configure("TProgressbar",
                       background=accent_color,
                       troughcolor="#404040",
                       borderwidth=0,
                       lightcolor=accent_color,
                       darkcolor=accent_color)
    
    def _configure_treeview_styles(self, style: ttk.Style) -> None:
        """Configure treeview styles."""
        bg_color = self.settings.get('ui.bg_color', '#2b2b2b')
        fg_color = self.settings.get('ui.fg_color', '#e0e0e0')
        accent_color = self.settings.get('ui.accent_color', '#4a90e2')
        
        style.configure("Treeview",
                       background="#3c3f41",
                       foreground=fg_color,
                       fieldbackground="#3c3f41",
                       borderwidth=0,
                       font=("Consolas", 10))
        
        style.configure("Treeview.Heading",
                       background=accent_color,
                       foreground="white",
                       font=("Helvetica", 10, "bold"),
                       relief='flat')
        
        style.map("Treeview",
                 background=[('selected', accent_color)],
                 foreground=[('selected', 'white')])
    
    def get_color_palette(self) -> Dict[str, str]:
        """
        Get the current color palette.
        
        Returns:
            Dictionary of color names to hex values
        """
        return {
            'background': self.settings.get('ui.bg_color', '#2b2b2b'),
            'foreground': self.settings.get('ui.fg_color', '#e0e0e0'),
            'accent': self.settings.get('ui.accent_color', '#4a90e2'),
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'info': '#17a2b8',
            'secondary': '#6c757d',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'field_background': '#3c3f41',
            'border': '#495057',
            'hover': '#505050'
        }
    
    def create_scrolled_text_style(self, widget: tk.Text) -> None:
        """
        Apply styling to scrolled text widgets.
        
        Args:
            widget: Text widget to style
        """
        colors = self.get_color_palette()
        
        widget.configure(
            bg=colors['field_background'],
            fg=colors['success'],  # Green text for terminal-like appearance
            font=("Consolas", 10),
            relief='flat',
            borderwidth=1,
            insertbackground=colors['foreground'],
            selectbackground=colors['accent'],
            selectforeground='white'
        )
    
    def create_card_frame(self, parent: tk.Widget, **kwargs) -> ttk.Frame:
        """
        Create a styled card frame.
        
        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
            
        Returns:
            Styled frame widget
        """
        frame = ttk.Frame(parent, style="Card.TFrame", **kwargs)
        return frame
    
    def create_header_label(self, parent: tk.Widget, text: str, **kwargs) -> ttk.Label:
        """
        Create a styled header label.
        
        Args:
            parent: Parent widget
            text: Label text
            **kwargs: Additional label arguments
            
        Returns:
            Styled label widget
        """
        label = ttk.Label(parent, text=text, style="Header.TLabel", **kwargs)
        return label
    
    def create_primary_button(self, parent: tk.Widget, text: str, command=None, **kwargs) -> ttk.Button:
        """
        Create a styled primary button.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Button command
            **kwargs: Additional button arguments
            
        Returns:
            Styled button widget
        """
        button = ttk.Button(parent, text=text, command=command, **kwargs)
        return button
    
    def create_secondary_button(self, parent: tk.Widget, text: str, command=None, **kwargs) -> ttk.Button:
        """
        Create a styled secondary button.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Button command
            **kwargs: Additional button arguments
            
        Returns:
            Styled button widget
        """
        button = ttk.Button(parent, text=text, command=command, style="Secondary.TButton", **kwargs)
        return button
    
    def create_success_button(self, parent: tk.Widget, text: str, command=None, **kwargs) -> ttk.Button:
        """
        Create a styled success button.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Button command
            **kwargs: Additional button arguments
            
        Returns:
            Styled button widget
        """
        button = ttk.Button(parent, text=text, command=command, style="Success.TButton", **kwargs)
        return button
    
    def create_danger_button(self, parent: tk.Widget, text: str, command=None, **kwargs) -> ttk.Button:
        """
        Create a styled danger button.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Button command
            **kwargs: Additional button arguments
            
        Returns:
            Styled button widget
        """
        button = ttk.Button(parent, text=text, command=command, style="Danger.TButton", **kwargs)
        return button
    
    def apply_theme(self, theme_name: str) -> None:
        """
        Apply a different theme.
        
        Args:
            theme_name: Name of the theme to apply
        """
        if theme_name in ['dark', 'light', 'blue', 'green']:
            self.theme = theme_name
            self.settings.set('ui.theme', theme_name)
            self.configure_styles()
        else:
            raise UIError(f"Unknown theme: {theme_name}")
    
    def get_available_themes(self) -> list:
        """
        Get list of available themes.
        
        Returns:
            List of theme names
        """
        return ['dark', 'light', 'blue', 'green']
