import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from typing import List
from core.config_manager import FTPConfig
from core.ftp_handler import FTPHandler
from core.image_processor import ImageProcessor


class UploadTab(ttk.Frame):
    """Záložka pro nahrávání fotek na FTP"""
    
    def __init__(self, parent, config_manager: FTPConfig, ftp_handler: FTPHandler, 
                 image_processor: ImageProcessor, status_callback):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.ftp_handler = ftp_handler
        self.image_processor = image_processor
        self.status_callback = status_callback
        
        self.source_folder = None
        self.selected_images = []
        self.uploading = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Vytvoří widgety"""
        
        # FTP Connection Section
        connection_frame = ttk.LabelFrame(self, text="1. Připojení k FTP", padding=10)
        connection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(connection_frame, text="FTP Server:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.ftp_combo = ttk.Combobox(connection_frame, state='readonly', width=30)
        self.ftp_combo.grid(row=0, column=1, padx=5, pady=5)
        self._refresh_ftp_list()
        
        self.connect_btn = ttk.Button(connection_frame, text="Připojit", command=self._connect_ftp)
        self.connect_btn.grid(row=0, column=2, padx=5, pady=5)
        
        self.disconnect_btn = ttk.Button(connection_frame, text="Odpojit", command=self._disconnect_ftp, state=tk.DISABLED)
        self.disconnect_btn.grid(row=0, column=3, padx=5, pady=5)
        
        self.connection_status = ttk.Label(connection_frame, text="● Odpojeno", foreground="red")
        self.connection_status.grid(row=0, column=4, padx=10, pady=5)
        
        # Target Folder Section
        target_frame = ttk.LabelFrame(self, text="2. Cílová složka na FTP", padding=10)
        target_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(target_frame, text="Aktuální cesta:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.path_label = ttk.Label(target_frame, text="/", relief=tk.SUNKEN, width=40)
        self.path_label.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Button(target_frame, text="📁 Procházet", command=self._browse_ftp).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(target_frame, text="➕ Nová složka", command=self._create_folder).grid(row=0, column=4, padx=5, pady=5)
        
        target_frame.columnconfigure(1, weight=1)
        
        # Source Images Section
        source_frame = ttk.LabelFrame(self, text="3. Zdrojové fotky", padding=10)
        source_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Button(source_frame, text="📂 Vybrat složku s fotkami", 
                  command=self._select_source_folder).pack(anchor=tk.W, padx=5, pady=5)
        
        self.source_label = ttk.Label(source_frame, text="Žádná složka nevybrána", foreground="gray")
        self.source_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # Seznam obrázků
        list_container = ttk.Frame(source_frame)
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.image_listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set, height=8)
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.image_listbox.yview)
        
        self.image_count_label = ttk.Label(source_frame, text="0 obrázků", font=('Arial', 9))
        self.image_count_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # Upload Section
        upload_frame = ttk.LabelFrame(self, text="4. Nahrát", padding=10)
        upload_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.upload_btn = ttk.Button(upload_frame, text="🚀 Začít nahrávání", 
                                     command=self._start_upload, state=tk.DISABLED)
        self.upload_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.cancel_btn = ttk.Button(upload_frame, text="⛔ Zrušit", 
                                     command=self._cancel_upload, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Separator(upload_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        self.generate_index_btn = ttk.Button(upload_frame, text="📄 Generovat index.php", 
                                            command=self._manual_generate_index, state=tk.DISABLED)
        self.generate_index_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.upload_universal_btn = ttk.Button(upload_frame, text="📤 Nahrát univerzální PHP", 
                                              command=self._upload_universal_php, state=tk.DISABLED)
        self.upload_universal_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Progress
        progress_container = ttk.Frame(self)
        progress_container.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_label = ttk.Label(progress_container, text="Připraveno k nahrávání")
        self.progress_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.progress_bar = ttk.Progressbar(progress_container, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=5, pady=2)
        
        self.progress_detail = ttk.Label(progress_container, text="", font=('Arial', 8), foreground="gray")
        self.progress_detail.pack(anchor=tk.W, padx=5, pady=2)
    
    def _refresh_ftp_list(self):
        """Obnoví seznam FTP serverů"""
        names = self.config_manager.get_config_names()
        self.ftp_combo['values'] = names
        if names and not self.ftp_combo.get():
            self.ftp_combo.current(0)
    
    def _connect_ftp(self):
        """Připojí se k FTP"""
        config_name = self.ftp_combo.get()
        if not config_name:
            messagebox.showwarning("Upozornění", "Vyberte FTP server")
            return
        
        config = self.config_manager.get_config(config_name)
        self.status_callback("Připojování k FTP...")
        
        success, message = self.ftp_handler.connect(
            config['host'], 
            config['port'], 
            config['username'], 
            config['password']
        )
        
        if success:
            self.connection_status.config(text="● Připojeno", foreground="green")
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            self.path_label.config(text=self.ftp_handler.get_current_path())
            self.status_callback(f"Připojeno k {config['host']}")
            self._update_upload_button_state()
            messagebox.showinfo("Úspěch", message)
        else:
            messagebox.showerror("Chyba", message)
            self.status_callback("Připojení selhalo")
    
    def _disconnect_ftp(self):
        """Odpojí se od FTP"""
        self.ftp_handler.disconnect()
        self.connection_status.config(text="● Odpojeno", foreground="red")
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.path_label.config(text="/")
        self.status_callback("Odpojeno")
        self._update_upload_button_state()
    
    def _browse_ftp(self):
        """Otevře dialog pro procházení FTP složek"""
        if not self.ftp_handler.connected:
            messagebox.showwarning("Upozornění", "Nejprve se připojte k FTP")
            return
        
        FTPBrowserDialog(self, self.ftp_handler, self.path_label)
    
    def _create_folder(self):
        """Vytvoří novou složku na FTP"""
        if not self.ftp_handler.connected:
            messagebox.showwarning("Upozornění", "Nejprve se připojte k FTP")
            return
        
        folder_name = tk.simpledialog.askstring("Nová složka", "Zadejte název složky:")
        if folder_name:
            success, message = self.ftp_handler.create_directory(folder_name)
            if success:
                # Změň do nové složky
                self.ftp_handler.change_directory(folder_name)
                self.path_label.config(text=self.ftp_handler.get_current_path())
                messagebox.showinfo("Úspěch", message)
            else:
                messagebox.showerror("Chyba", message)
    
    def _select_source_folder(self):
        """Vybere zdrojovou složku s fotkami"""
        folder = filedialog.askdirectory(title="Vyberte složku s fotkami")
        if folder:
            self.source_folder = folder
            self._scan_images()
            self.source_label.config(text=folder, foreground="black")
            self._update_upload_button_state()
    
    def _scan_images(self):
        """Naskenuje obrázky ve složce"""
        if not self.source_folder:
            return
        
        self.selected_images = []
        self.image_listbox.delete(0, tk.END)
        
        try:
            for filename in os.listdir(self.source_folder):
                if self.image_processor.is_image(filename):
                    self.selected_images.append(filename)
                    self.image_listbox.insert(tk.END, filename)
            
            count = len(self.selected_images)
            self.image_count_label.config(text=f"{count} {'obrázek' if count == 1 else 'obrázků'}")
        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba při načítání obrázků: {e}")
    
    def _update_upload_button_state(self):
        """Aktualizuje stav tlačítka pro nahrávání"""
        if self.ftp_handler.connected and self.selected_images and not self.uploading:
            self.upload_btn.config(state=tk.NORMAL)
        else:
            self.upload_btn.config(state=tk.DISABLED)
        
        # Tlačítko pro generování index.php je aktivní když jsme připojeni
        if self.ftp_handler.connected:
            self.generate_index_btn.config(state=tk.NORMAL)
            self.upload_universal_btn.config(state=tk.NORMAL)
        else:
            self.generate_index_btn.config(state=tk.DISABLED)
            self.upload_universal_btn.config(state=tk.DISABLED)
    
    def _upload_universal_php(self):
        """Nahraje univerzální PHP soubor který automaticky skenuje složky"""
        if not self.ftp_handler.connected:
            messagebox.showwarning("Upozornění", "Nejprve se připojte k FTP")
            return
        
        # Cesta k univerzálnímu PHP
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        universal_php_path = os.path.join(script_dir, "universal_index.php")
        
        if not os.path.exists(universal_php_path):
            messagebox.showerror(
                "Chyba", 
                f"Soubor universal_index.php nebyl nalezen v:\n{universal_php_path}"
            )
            return
        
        current_path = self.ftp_handler.get_current_path()
        
        if not messagebox.askyesno(
            "Potvrdit nahrání",
            f"Nahrát universal_index.php do složky:\n{current_path}\n\n"
            "Tento soubor automaticky projde složky thumbnail/original/compress\n"
            "a vytvoří dynamický index všech fotek."
        ):
            return
        
        try:
            # Načti obsah souboru
            with open(universal_php_path, 'rb') as f:
                php_content = f.read()
            
            # Ujisti se že jsme ve správné složce
            self.ftp_handler.change_directory(current_path)
            
            # Nahrát na FTP
            self.status_callback("Nahrávám universal_index.php...")
            success, msg = self.ftp_handler.upload_bytes(php_content, "index.php")
            
            if success:
                messagebox.showinfo(
                    "Hotovo",
                    f"universal_index.php byl nahrán jako index.php do:\n{current_path}\n\n"
                    f"Přístup: {current_path}/index.php"
                )
                self.status_callback("universal_index.php nahrán")
            else:
                messagebox.showerror("Chyba", f"Chyba při nahrávání: {msg}")
                self.status_callback("Chyba při nahrávání")
                
        except Exception as e:
            messagebox.showerror("Chyba", f"Chyba: {e}")
            self.status_callback("Chyba")
    
    def _manual_generate_index(self):
        """Ručně generuje index.php pro aktuální složku"""
        if not self.ftp_handler.connected:
            messagebox.showwarning("Upozornění", "Nejprve se připojte k FTP")
            return
        
        current_path = self.ftp_handler.get_current_path()
        
        # Zkontroluj zda má složka strukturu
        has_structure, found = self.ftp_handler.has_photo_structure()
        
        if not has_structure:
            if not messagebox.askyesno(
                "Struktura nenalezena",
                "Aktuální složka neobsahuje strukturu thumbnail/original/compress.\n\n"
                "Chcete přesto vygenerovat index.php?"
            ):
                return
        
        self.status_callback("Načítám seznam fotek...")
        
        # Načti v novém vlákně
        thread = threading.Thread(
            target=self._manual_generate_thread, 
            args=(current_path, has_structure),
            daemon=True
        )
        thread.start()
    
    def _manual_generate_thread(self, base_path: str, has_structure: bool):
        """Vlákno pro ruční generování index.php"""
        try:
            filenames = []
            
            if has_structure:
                # Načti z thumbnail složky
                items = self.ftp_handler.list_directory(base_path + "/thumbnail")
                for name, is_dir in items:
                    if not is_dir and self.image_processor.is_image(name):
                        filenames.append(name)
            else:
                # Načti přímo ze složky
                items = self.ftp_handler.list_directory(base_path)
                for name, is_dir in items:
                    if not is_dir and self.image_processor.is_image(name):
                        filenames.append(name)
            
            if not filenames:
                self.after(0, lambda: messagebox.showwarning(
                    "Žádné fotky", 
                    "Ve složce nebyly nalezeny žádné obrázky"
                ))
                self.after(0, lambda: self.status_callback("Žádné fotky k indexování"))
                return
            
            # Ujisti se že jsme ve správné složce
            self.ftp_handler.change_directory(base_path)
            
            # Generuj index.php
            self.after(0, lambda: self.status_callback(f"Generuji index.php pro {len(filenames)} fotek..."))
            self._generate_index_php(base_path, filenames)
            
            self.after(0, lambda: messagebox.showinfo(
                "Hotovo", 
                f"index.php vygenerován pro {len(filenames)} fotek"
            ))
            self.after(0, lambda: self.status_callback("index.php vygenerován"))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(
                "Chyba", 
                f"Chyba při generování: {e}"
            ))
            self.after(0, lambda: self.status_callback("Chyba při generování"))
    
    def _start_upload(self):
        """Zahájí nahrávání"""
        if not self.ftp_handler.connected or not self.selected_images:
            return
        
        self.uploading = True
        self.upload_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.connect_btn.config(state=tk.DISABLED)
        
        # Spusť v novém vlákně
        thread = threading.Thread(target=self._upload_thread, daemon=True)
        thread.start()
    
    def _upload_thread(self):
        """Vlákno pro nahrávání"""
        try:
            total = len(self.selected_images)
            current_path = self.ftp_handler.get_current_path()
            
            # Vytvoř složky
            self.ftp_handler.create_directory("thumbnail")
            self.ftp_handler.create_directory("original")
            self.ftp_handler.create_directory("compress")
            
            uploaded_files = []
            
            for i, filename in enumerate(self.selected_images):
                if not self.uploading:  # Kontrola zrušení
                    break
                
                self._update_progress(i, total, f"Zpracovávám: {filename}")
                
                local_path = os.path.join(self.source_folder, filename)
                
                try:
                    # 1. Thumbnail
                    success, thumb_data, msg = self.image_processor.create_thumbnail(local_path)
                    if success:
                        thumb_path = f"thumbnail/{filename}"
                        self.ftp_handler.upload_bytes(thumb_data, thumb_path)
                    
                    # 2. Compress
                    success, comp_data, msg = self.image_processor.compress_image(local_path)
                    if success:
                        comp_path = f"compress/{filename}"
                        self.ftp_handler.upload_bytes(comp_data, comp_path)
                    
                    # 3. Original
                    orig_path = f"original/{filename}"
                    self.ftp_handler.upload_file(local_path, orig_path)
                    
                    # Přidej do seznamu úspěšně nahraných
                    uploaded_files.append(filename)
                    
                except Exception as e:
                    print(f"Chyba při nahrávání {filename}: {e}")
            
            # Generuj index.php
            if uploaded_files:
                self._update_progress(total, total, "Generuji index.php...")
                self._generate_index_php(current_path, uploaded_files)
            
            # Dokončeno
            self._update_progress(total, total, "Nahrávání dokončeno!")
            self.after(100, lambda: messagebox.showinfo("Hotovo", f"Nahráno {total} obrázků"))
            
        except Exception as e:
            self.after(100, lambda: messagebox.showerror("Chyba", f"Chyba při nahrávání: {e}"))
        
        finally:
            self.uploading = False
            self.after(100, self._reset_upload_ui)
    
    def _generate_index_php(self, base_path: str, filenames: List[str]):
        """Generuje index.php soubor s cestami k fotkám"""
        try:
            # Ujisti se že jsme ve správné složce (base_path)
            current = self.ftp_handler.get_current_path()
            if current != base_path:
                self.ftp_handler.change_directory(base_path)
            
            # Vytvoř PHP kód
            php_code = "<?php\n"
            php_code += "// Auto-generated photo index\n"
            php_code += "// Generated by FTP Photo Manager\n\n"
            php_code += "// Get base URL\n"
            php_code += "$protocol = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https://' : 'http://';\n"
            php_code += "$host = $_SERVER['HTTP_HOST'];\n"
            php_code += "$scriptPath = dirname($_SERVER['SCRIPT_NAME']);\n"
            php_code += "$scriptPath = rtrim($scriptPath, '/') . '/';\n"
            php_code += "$baseUrl = $protocol . $host . $scriptPath;\n\n"
            php_code += "$photos = [\n"
            
            for filename in filenames:
                # Escapuj uvozovky v názvu souboru
                safe_filename = filename.replace("'", "\\'")
                
                php_code += "    [\n"
                php_code += f"        'thumbnail' => 'thumbnail/{safe_filename}',\n"
                php_code += f"        'thumbnail_url' => $baseUrl . 'thumbnail/{safe_filename}',\n"
                php_code += f"        'original' => 'original/{safe_filename}',\n"
                php_code += f"        'original_url' => $baseUrl . 'original/{safe_filename}',\n"
                php_code += f"        'compress' => 'compress/{safe_filename}',\n"
                php_code += f"        'compress_url' => $baseUrl . 'compress/{safe_filename}',\n"
                php_code += f"        'filename' => '{safe_filename}'\n"
                php_code += "    ],\n"
            
            php_code += "];\n\n"
            php_code += "$result = [\n"
            php_code += "    'success' => true,\n"
            php_code += "    'count' => count($photos),\n"
            php_code += "    'base_url' => $baseUrl,\n"
            php_code += "    'photos' => $photos\n"
            php_code += "];\n\n"
            php_code += "// Return JSON\n"
            php_code += "header('Content-Type: application/json');\n"
            php_code += "echo json_encode($result, JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);\n"
            php_code += "?>"
            
            # Nahrát na FTP do aktuální složky (která je base_path)
            php_bytes = php_code.encode('utf-8')
            success, msg = self.ftp_handler.upload_bytes(php_bytes, "index.php")
            
            if success:
                print(f"index.php vygenerován a nahrán do {base_path}")
            else:
                print(f"Chyba při nahrávání index.php: {msg}")
                
        except Exception as e:
            print(f"Chyba při generování index.php: {e}")
    
    def _update_progress(self, current: int, total: int, message: str):
        """Aktualizuje progress bar"""
        def update():
            progress = (current / total) * 100 if total > 0 else 0
            self.progress_bar['value'] = progress
            self.progress_label.config(text=message)
            self.progress_detail.config(text=f"{current} / {total}")
            self.status_callback(message)
        
        self.after(0, update)
    
    def _cancel_upload(self):
        """Zruší nahrávání"""
        if messagebox.askyesno("Zrušit", "Opravdu zrušit nahrávání?"):
            self.uploading = False
    
    def _reset_upload_ui(self):
        """Resetuje UI po nahrávání"""
        self.cancel_btn.config(state=tk.DISABLED)
        self.connect_btn.config(state=tk.NORMAL)
        self._update_upload_button_state()


class FTPBrowserDialog(tk.Toplevel):
    """Dialog pro procházení FTP složek"""
    
    def __init__(self, parent, ftp_handler: FTPHandler, path_label):
        super().__init__(parent)
        
        self.ftp_handler = ftp_handler
        self.path_label = path_label
        self.current_path = ftp_handler.get_current_path()
        
        self.title("Procházet FTP")
        self.geometry("500x400")
        self.transient(parent)
        self.grab_set()
        
        # Path label
        path_frame = ttk.Frame(self)
        path_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(path_frame, text="Aktuální cesta:").pack(side=tk.LEFT, padx=5)
        self.current_path_label = ttk.Label(path_frame, text=self.current_path, 
                                           relief=tk.SUNKEN, width=40)
        self.current_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(path_frame, text="⬆️", command=self._go_up, width=3).pack(side=tk.LEFT, padx=2)
        
        # Listbox
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.folder_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.folder_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.folder_listbox.bind('<Double-Button-1>', lambda e: self._enter_folder())
        scrollbar.config(command=self.folder_listbox.yview)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Otevřít", command=self._enter_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Vybrat tuto složku", command=self._select).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Zavřít", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        self._refresh_list()
    
    def _refresh_list(self):
        """Obnoví seznam složek"""
        self.folder_listbox.delete(0, tk.END)
        items = self.ftp_handler.list_directory()
        
        for name, is_dir in items:
            if is_dir:
                self.folder_listbox.insert(tk.END, f"📁 {name}")
        
        self.current_path = self.ftp_handler.get_current_path()
        self.current_path_label.config(text=self.current_path)
    
    def _enter_folder(self):
        """Vstoupí do vybrané složky"""
        selection = self.folder_listbox.curselection()
        if not selection:
            return
        
        item = self.folder_listbox.get(selection[0])
        folder_name = item.replace("📁 ", "")
        
        success, new_path = self.ftp_handler.change_directory(folder_name)
        if success:
            self._refresh_list()
    
    def _go_up(self):
        """Jde o úroveň výš"""
        success, new_path = self.ftp_handler.change_directory("..")
        if success:
            self._refresh_list()
    
    def _select(self):
        """Vybere aktuální složku"""
        self.path_label.config(text=self.current_path)
        messagebox.showinfo("Vybráno", f"Vybrána složka: {self.current_path}")
        self.destroy()
