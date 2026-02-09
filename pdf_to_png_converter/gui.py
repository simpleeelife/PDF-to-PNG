import tkinter as tk
from tkinter import ttk, messagebox
import windnd
import threading
import queue
from pathlib import Path
from . import config, converter

class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF → PNG 変換ツール")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # Output directory setup
        self.output_dir = config.get_default_output_dir()
        
        # UI Elements
        self._setup_ui()
        
        # Hook Drag & Drop
        windnd.hook_dropfiles(self.root, func=self._on_drop)
        
        # Queue for thread communication
        self.msg_queue = queue.Queue()
        self.root.after(100, self._process_queue)

    def _setup_ui(self):
        # Main Container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Drop Area (Visual only, actual hook is on root)
        self.drop_frame = ttk.LabelFrame(main_frame, text=" ファイル入力 ", padding="20")
        self.drop_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        self.drop_label = tk.Label(
            self.drop_frame, 
            text="ここにPDFファイルを\nドラッグ＆ドロップしてください\n\n📄",
            font=("Meiryo UI", 12),
            fg="#555555"
        )
        self.drop_label.pack(expand=True)

        # Status Area
        self.status_var = tk.StringVar(value="待機中")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.pack(fill=tk.X, pady=(0, 5))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var, 
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        # Output Path Info
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X)
        
        ttk.Label(path_frame, text="出力先: ", font=("Meiryo UI", 8, "bold")).pack(side=tk.LEFT)
        self.path_label = ttk.Label(
            path_frame, 
            text=str(self.output_dir), 
            font=("Meiryo UI", 8),
            foreground="#666666"
        )
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _on_drop(self, filenames):
        """Callback from windnd."""
        decoded_files = []
        for f in filenames:
            if isinstance(f, bytes):
                try:
                    decoded = f.decode('mbcs')
                    decoded_files.append(decoded)
                except:
                    decoded_files.append(f.decode('utf-8', errors='ignore'))
            else:
                decoded_files.append(f)
        
        if len(decoded_files) > 0:
            target_file = decoded_files[0]
            self.start_conversion(target_file)

    def start_conversion(self, file_path):
        if self.status_var.get().startswith("変換中"):
            return # Busy

        self._update_status(f"検証中: {Path(file_path).name}...", 0)
        
        # Run in thread
        thread = threading.Thread(target=self._run_conversion_logic, args=(file_path,))
        thread.daemon = True
        thread.start()

    def _run_conversion_logic(self, file_path):
        try:
            converter.convert_pdf(
                file_path, 
                self.output_dir, 
                progress_callback=self._progress_callback
            )
            self._queue_msg("success", f"完了しました！\n出力先: {self.output_dir}")
        except converter.ValidationError as e:
            self._queue_msg("error", f"検証エラー:\n{str(e)}")
        except converter.ConversionError as e:
            self._queue_msg("error", f"変換エラー:\n{str(e)}")
        except Exception as e:
            self._queue_msg("error", f"予期せぬエラー:\n{str(e)}")

    def _progress_callback(self, current, total, filename):
        percent = (current / total) * 100
        msg = f"変換中 ({current}/{total}): {filename}"
        self._queue_msg("progress", (msg, percent))

    def _queue_msg(self, type_, data):
        self.msg_queue.put((type_, data))

    def _process_queue(self):
        try:
            while True:
                type_, data = self.msg_queue.get_nowait()
                if type_ == "progress":
                    msg, percent = data
                    self._update_status(msg, percent)
                elif type_ == "success":
                    self._update_status("完了", 100)
                    messagebox.showinfo("成功", data)
                    self._reset_status()
                elif type_ == "error":
                    self._update_status("エラー発生", 0)
                    messagebox.showerror("エラー", data)
                    self._reset_status()
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._process_queue)

    def _update_status(self, text, percent):
        self.status_var.set(text)
        self.progress_var.set(percent)

    def _reset_status(self):
        self.status_var.set("待機中")
        self.progress_var.set(0)
