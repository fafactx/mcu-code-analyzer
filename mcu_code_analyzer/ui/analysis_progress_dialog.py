"""
Analysis Progress Dialog - Real-time analysis log display
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import queue
import time
from typing import Callable, Optional


class AnalysisProgressDialog:
    """Analysis progress dialog with real-time log display"""
    
    def __init__(self, parent, title="Analysis Progress"):
        self.parent = parent
        self.title = title
        self.dialog = None
        self.log_text = None
        self.progress_bar = None
        self.status_label = None
        self.cancel_btn = None
        self.close_btn = None
        
        # Progress tracking
        self.progress_value = 0
        self.status_text = "Initializing..."
        self.is_cancelled = False
        self.is_completed = False
        
        # Log queue for thread-safe updates
        self.log_queue = queue.Queue()
        self.update_timer = None
        
        # Callbacks
        self.cancel_callback: Optional[Callable] = None
        
    def show(self, cancel_callback: Optional[Callable] = None):
        """Show the progress dialog"""
        self.cancel_callback = cancel_callback
        self.is_cancelled = False
        self.is_completed = False
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"800x600+{x}+{y}")
        
        self._create_widgets()
        self._start_update_timer()
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
        
    def _create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="MCU Code Analysis Progress",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Status
        self.status_label = ctk.CTkLabel(
            main_frame,
            text=self.status_text,
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", pady=(0, 20))
        self.progress_bar.set(0)
        
        # Log area
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        log_label = ctk.CTkLabel(
            log_frame,
            text="Analysis Log:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        log_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Log text with scrollbar
        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=10),
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Button frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel Analysis",
            command=self._on_cancel,
            width=120,
            height=32,
            fg_color="#DC3545",
            hover_color="#C82333"
        )
        self.cancel_btn.pack(side="left")
        
        # Close button (initially disabled)
        self.close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self._on_close,
            width=120,
            height=32,
            state="disabled"
        )
        self.close_btn.pack(side="right")
        
    def _start_update_timer(self):
        """Start the update timer for processing log queue"""
        self._process_log_queue()
        self.update_timer = self.dialog.after(100, self._start_update_timer)
        
    def _process_log_queue(self):
        """Process pending log messages from queue"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self._append_log_message(message)
        except queue.Empty:
            pass
            
    def _append_log_message(self, message: str):
        """Append message to log text"""
        if self.log_text:
            timestamp = time.strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"
            self.log_text.insert("end", formatted_message)
            self.log_text.see("end")
            
    def _on_cancel(self):
        """Handle cancel button click"""
        if not self.is_cancelled and not self.is_completed:
            result = messagebox.askyesno(
                "Confirm Cancel",
                "Are you sure you want to cancel the analysis?",
                parent=self.dialog
            )
            if result:
                self.is_cancelled = True
                self.cancel_btn.configure(state="disabled", text="Cancelling...")
                self.update_status("Cancelling analysis...")
                
                if self.cancel_callback:
                    self.cancel_callback()
                    
    def _on_close(self):
        """Handle dialog close"""
        if not self.is_completed and not self.is_cancelled:
            self._on_cancel()
            return
            
        if self.update_timer:
            self.dialog.after_cancel(self.update_timer)
            
        self.dialog.grab_release()
        self.dialog.destroy()
        
    def update_progress(self, value: float):
        """Update progress bar (0-100)"""
        self.progress_value = value
        if self.progress_bar:
            self.progress_bar.set(value / 100.0)
            
    def update_status(self, status: str):
        """Update status text"""
        self.status_text = status
        if self.status_label:
            self.status_label.configure(text=status)
            
    def add_log(self, message: str):
        """Add log message (thread-safe)"""
        self.log_queue.put(message)
        
    def set_completed(self, success: bool = True):
        """Mark analysis as completed"""
        self.is_completed = True
        
        if self.cancel_btn:
            self.cancel_btn.configure(state="disabled")
            
        if self.close_btn:
            self.close_btn.configure(state="normal")
            
        if success:
            self.update_status("✅ Analysis completed successfully!")
            self.add_log("Analysis completed successfully!")
        else:
            self.update_status("❌ Analysis failed!")
            self.add_log("Analysis failed!")
            
    def set_cancelled(self):
        """Mark analysis as cancelled"""
        self.is_cancelled = True
        self.is_completed = True
        
        if self.cancel_btn:
            self.cancel_btn.configure(state="disabled")
            
        if self.close_btn:
            self.close_btn.configure(state="normal")
            
        self.update_status("Analysis cancelled")
        self.add_log("Analysis was cancelled by user")
