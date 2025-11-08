import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from io import BytesIO
import threading
from typing import List, Dict
from core.ftp_handler import FTPHandler
from core.image_processor import ImageProcessor


class BrowseTab(ttk.Frame):
    """Záložka pro procházení a mazání fotek z FTP"""
    
    def __init__(self, parent, ftp_handler: FTPHandler, image_processor: ImageProcessor, status_callback):
        super().__init__(parent)
        
        self.ftp_handler = ftp_handler
        self.image_processor = image_processor
        self.status_callback = status_callback
        
        self.current_folder = None
        self.photos = []  # List of (filename, has_structure)
        self.photo_thumbnails = {}  # Cache pro thumbnaily
        self.selected_photos = set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Vytvoří widgety"""
        
        # Control Panel
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="🔄 Načíst složku", 
                  command=self._load_folder).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="🗑️ Smazat vybrané", 
                  command=self._delete_selected).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="🗑️ Smazat všechny", 
                  command=self._delete_all).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="☑️ Vybrat vše", 
                  command=self._select_all).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="☐ Zrušit výběr", 
                  command=self._deselect_all).pack(side=tk.LEFT, padx=5)
        
        self.folder_label = ttk.Label(control_frame, text="Žádná složka", foreground="gray")
        self.folder_label.pack(side=tk.LEFT, padx=20)
        
        # Info panel
        info_frame = ttk.Frame(self)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.photo_count_label = ttk.Label(info_frame, text="0 fotek | 0 vybráno")
        self.photo_count_label.pack(side=tk.LEFT, padx=5)
        
        self.structure_label = ttk.Label(info_frame, text="", foreground="blue")
        self.structure_label.pack(side=tk.LEFT, padx=20)
        
        # Main container (split)
        main_container = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left: Photo list
        left_frame = ttk.Frame(main_container)
        main_container.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Fotky:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=5, pady=5)
        
        list_container = ttk.Frame(left_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.photo_listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set, 
                                       selectmode=tk.MULTIPLE)
        self.photo_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.photo_listbox.bind('<<ListboxSelect>>', self._on_photo_select)
        scrollbar.config(command=self.photo_listbox.yview)
        
        # Right: Preview
        right_frame = ttk.Frame(main_container)
        main_container.add(right_frame, weight=1)
        
        ttk.Label(right_frame, text="Náhled:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=5, pady=5)
        
        preview_container = ttk.Frame(right_frame, relief=tk.SUNKEN, borderwidth=2)
        preview_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.preview_label = ttk.Label(preview_container, text="Vyberte fotku pro náhled", 
                                      anchor=tk.CENTER)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # Info about selected photo
        self.photo_info_label = ttk.Label(right_frame, text="", justify=tk.LEFT, 
                                         font=('Arial', 9))
        self.photo_info_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # Delete buttons for single photo
        single_delete_frame = ttk.Frame(right_frame)
        single_delete_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(single_delete_frame, text="🗑️ Smazat tuto fotku", 
                  command=self._delete_current_photo).pack(side=tk.LEFT, padx=5)
    
    def _load_folder(self):
        """Načte fotky ze složky"""
        if not self.ftp_handler.connected:
            messagebox.showwarning("Upozornění", "Nejprve se připojte k FTP (záložka Nahrát)")
            return
        
        # Otevři browser dialog
        FolderBrowserDialog(self, self.ftp_handler, self._on_folder_selected)
    
    def _on_folder_selected(self, folder_path: str):
        """Callback když je vybrána složka"""
        self.current_folder = folder_path
        self.folder_label.config(text=folder_path, foreground="black")
        self.status_callback(f"Načítám fotky z {folder_path}...")
        
        # Načti v novém vlákně
        thread = threading.Thread(target=self._load_photos_thread, daemon=True)
        thread.start()
    
    def _load_photos_thread(self):
        """Načte fotky ve vlákně"""
        try:
            # Zkontroluj zda složka má strukturu
            has_structure, found = self.ftp_handler.has_photo_structure(self.current_folder)
            
            if has_structure:
                # Načti z thumbnail složky
                self.ftp_handler.change_directory(self.current_folder + "/thumbnail")
                items = self.ftp_handler.list_directory()
                
                self.photos = []
                for name, is_dir in items:
                    if not is_dir and self.image_processor.is_image(name):
                        self.photos.append((name, True))
                
                self.after(0, lambda: self.structure_label.config(
                    text="✓ Detekována struktura (thumbnail/original/compress)", 
                    foreground="green"
                ))
            else:
                # Načti přímo ze složky
                items = self.ftp_handler.list_directory(self.current_folder)
                
                self.photos = []
                for name, is_dir in items:
                    if not is_dir and self.image_processor.is_image(name):
                        self.photos.append((name, False))
                
                self.after(0, lambda: self.structure_label.config(
                    text="⚠ Není detekována struktura", 
                    foreground="orange"
                ))
            
            # Aktualizuj UI
            self.after(0, self._update_photo_list)
            self.after(0, lambda: self.status_callback(f"Načteno {len(self.photos)} fotek"))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Chyba", f"Chyba při načítání: {e}"))
            self.after(0, lambda: self.status_callback("Chyba při načítání"))
    
    def _update_photo_list(self):
        """Aktualizuje seznam fotek"""
        self.photo_listbox.delete(0, tk.END)
        self.selected_photos.clear()
        
        for filename, has_structure in self.photos:
            self.photo_listbox.insert(tk.END, filename)
        
        self._update_counts()
    
    def _on_photo_select(self, event):
        """Handler pro výběr fotky"""
        selection = self.photo_listbox.curselection()
        
        # Aktualizuj selected_photos set
        self.selected_photos = set(selection)
        self._update_counts()
        
        if len(selection) == 1:
            idx = selection[0]
            filename, has_structure = self.photos[idx]
            self._load_preview(filename, has_structure)
        else:
            self.preview_label.config(image='', text=f"{len(selection)} fotek vybráno")
            self.photo_info_label.config(text="")
    
    def _load_preview(self, filename: str, has_structure: bool):
        """Načte náhled fotky"""
        self.preview_label.config(text="Načítám...")
        self.photo_info_label.config(text=f"Fotka: {filename}")
        
        # Načti v novém vlákně
        thread = threading.Thread(
            target=self._load_preview_thread, 
            args=(filename, has_structure),
            daemon=True
        )
        thread.start()
    
    def _load_preview_thread(self, filename: str, has_structure: bool):
        """Načte náhled ve vlákně"""
        try:
            # Zkus načíst z cache
            if filename in self.photo_thumbnails:
                img_data = self.photo_thumbnails[filename]
            else:
                # Stáhni thumbnail
                if has_structure:
                    remote_path = f"{self.current_folder}/thumbnail/{filename}"
                else:
                    remote_path = f"{self.current_folder}/{filename}"
                
                success, img_data, msg = self.ftp_handler.download_file(remote_path)
                
                if not success:
                    self.after(0, lambda: self.preview_label.config(
                        text=f"Chyba načítání: {msg}"
                    ))
                    return
                
                # Pokud nemá strukturu, vytvoř thumbnail
                if not has_structure:
                    success, img_data, msg = self.image_processor.create_thumbnail_from_bytes(img_data)
                
                # Ulož do cache
                self.photo_thumbnails[filename] = img_data
            
            # Zobraz
            image = Image.open(BytesIO(img_data))
            
            # Resize pro zobrazení (max 400x400)
            image.thumbnail((400, 400), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            
            self.after(0, lambda: self._display_preview(photo, filename, image))
            
        except Exception as e:
            self.after(0, lambda: self.preview_label.config(
                text=f"Chyba zobrazení: {str(e)}"
            ))
    
    def _display_preview(self, photo, filename: str, image):
        """Zobrazí náhled"""
        self.preview_label.config(image=photo, text='')
        self.preview_label.image = photo  # Uchovej referenci
        
        info = f"Fotka: {filename}\nRozměry: {image.width}x{image.height}px"
        self.photo_info_label.config(text=info)
    
    def _update_counts(self):
        """Aktualizuje počty"""
        total = len(self.photos)
        selected = len(self.selected_photos)
        self.photo_count_label.config(text=f"{total} fotek | {selected} vybráno")
    
    def _select_all(self):
        """Vybere všechny fotky"""
        self.photo_listbox.selection_set(0, tk.END)
        self.selected_photos = set(range(len(self.photos)))
        self._update_counts()
    
    def _deselect_all(self):
        """Zruší výběr všech fotek"""
        self.photo_listbox.selection_clear(0, tk.END)
        self.selected_photos.clear()
        self._update_counts()
    
    def _delete_selected(self):
        """Smaže vybrané fotky"""
        if not self.selected_photos:
            messagebox.showwarning("Upozornění", "Nevybrali jste žádné fotky")
            return
        
        count = len(self.selected_photos)
        if not messagebox.askyesno("Potvrzení", f"Opravdu smazat {count} {'fotku' if count == 1 else 'fotek'}?"):
            return
        
        # Získej seznam souborů k smazání
        files_to_delete = [self.photos[i] for i in self.selected_photos]
        
        self.status_callback(f"Mažu {count} fotek...")
        thread = threading.Thread(
            target=self._delete_photos_thread, 
            args=(files_to_delete,),
            daemon=True
        )
        thread.start()
    
    def _delete_current_photo(self):
        """Smaže aktuálně zobrazenou fotku"""
        selection = self.photo_listbox.curselection()
        if len(selection) != 1:
            messagebox.showwarning("Upozornění", "Vyberte jednu fotku")
            return
        
        idx = selection[0]
        filename, has_structure = self.photos[idx]
        
        if not messagebox.askyesno("Potvrzení", f"Opravdu smazat fotku '{filename}'?"):
            return
        
        self._delete_photos_thread([(filename, has_structure)])
    
    def _delete_all(self):
        """Smaže všechny fotky"""
        if not self.photos:
            messagebox.showwarning("Upozornění", "Žádné fotky k smazání")
            return
        
        count = len(self.photos)
        if not messagebox.askyesno("Potvrzení", f"OPRAVDU smazat VŠECH {count} fotek?"):
            return
        
        self.status_callback(f"Mažu všech {count} fotek...")
        thread = threading.Thread(
            target=self._delete_photos_thread, 
            args=(self.photos,),
            daemon=True
        )
        thread.start()
    
    def _delete_photos_thread(self, photos_list: List):
        """Smaže fotky ve vlákně"""
        try:
            deleted = 0
            errors = []
            
            for filename, has_structure in photos_list:
                try:
                    if has_structure:
                        # Smaž ze všech tří složek
                        self.ftp_handler.delete_file(f"{self.current_folder}/thumbnail/{filename}")
                        self.ftp_handler.delete_file(f"{self.current_folder}/original/{filename}")
                        self.ftp_handler.delete_file(f"{self.current_folder}/compress/{filename}")
                    else:
                        # Smaž přímo
                        self.ftp_handler.delete_file(f"{self.current_folder}/{filename}")
                    
                    deleted += 1
                    
                    # Odstraň z cache
                    if filename in self.photo_thumbnails:
                        del self.photo_thumbnails[filename]
                    
                except Exception as e:
                    errors.append(f"{filename}: {str(e)}")
            
            # Znovu načti
            self.after(0, self._reload_current_folder)
            
            # Zobraz výsledek
            if errors:
                error_msg = f"Smazáno {deleted} fotek\n\nChyby:\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    error_msg += f"\n... a dalších {len(errors)-5} chyb"
                self.after(0, lambda: messagebox.showwarning("Dokončeno s chybami", error_msg))
            else:
                self.after(0, lambda: messagebox.showinfo("Hotovo", f"Smazáno {deleted} fotek"))
            
            self.after(0, lambda: self.status_callback(f"Smazáno {deleted} fotek"))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Chyba", f"Chyba při mazání: {e}"))
    
    def _reload_current_folder(self):
        """Znovu načte aktuální složku"""
        if self.current_folder:
            self._on_folder_selected(self.current_folder)


class FolderBrowserDialog(tk.Toplevel):
    """Dialog pro výběr složky k procházení"""
    
    def __init__(self, parent, ftp_handler: FTPHandler, callback):
        super().__init__(parent)
        
        self.ftp_handler = ftp_handler
        self.callback = callback
        self.current_path = ftp_handler.get_current_path()
        
        self.title("Vybrat složku")
        self.geometry("500x400")
        self.transient(parent)
        self.grab_set()
        
        # Path
        path_frame = ttk.Frame(self)
        path_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(path_frame, text="Cesta:").pack(side=tk.LEFT, padx=5)
        self.path_label = ttk.Label(path_frame, text=self.current_path, 
                                    relief=tk.SUNKEN, width=40)
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(path_frame, text="⬆️", command=self._go_up, width=3).pack(side=tk.LEFT, padx=2)
        
        # List
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
        ttk.Button(button_frame, text="Vybrat", command=self._select).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Zavřít", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        self._refresh_list()
    
    def _refresh_list(self):
        """Obnoví seznam"""
        self.folder_listbox.delete(0, tk.END)
        items = self.ftp_handler.list_directory()
        
        for name, is_dir in items:
            if is_dir:
                self.folder_listbox.insert(tk.END, f"📁 {name}")
        
        self.current_path = self.ftp_handler.get_current_path()
        self.path_label.config(text=self.current_path)
    
    def _enter_folder(self):
        """Vstoupí do složky"""
        selection = self.folder_listbox.curselection()
        if not selection:
            return
        
        item = self.folder_listbox.get(selection[0])
        folder_name = item.replace("📁 ", "")
        
        success, new_path = self.ftp_handler.change_directory(folder_name)
        if success:
            self._refresh_list()
    
    def _go_up(self):
        """Jde nahoru"""
        success, new_path = self.ftp_handler.change_directory("..")
        if success:
            self._refresh_list()
    
    def _select(self):
        """Vybere složku"""
        self.callback(self.current_path)
        self.destroy()
