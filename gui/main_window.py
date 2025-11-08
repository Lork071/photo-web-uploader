import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from core.config_manager import FTPConfig
from core.ftp_handler import FTPHandler
from core.image_processor import ImageProcessor
from gui.upload_tab import UploadTab
from gui.browse_tab import BrowseTab


class MainApplication(tk.Tk):
    """Hlavní aplikace pro správu fotek na FTP"""
    
    def __init__(self):
        super().__init__()
        
        self.title("FTP Photo Manager")
        self.geometry("1000x700")
        
        # Inicializace komponent
        self.config_manager = FTPConfig()
        self.ftp_handler = FTPHandler()
        self.image_processor = ImageProcessor()
        
        # Vytvoř hlavní menu
        self._create_menu()
        
        # Vytvoř hlavní kontejner
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_bar = ttk.Label(self, text="Odpojeno", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Vytvoř notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Vytvoř záložky
        self.upload_tab = UploadTab(
            self.notebook, 
            self.config_manager, 
            self.ftp_handler, 
            self.image_processor,
            self.update_status
        )
        self.browse_tab = BrowseTab(
            self.notebook,
            self.ftp_handler,
            self.image_processor,
            self.update_status
        )
        
        self.notebook.add(self.upload_tab, text="📤 Nahrát fotky")
        self.notebook.add(self.browse_tab, text="🗂️ Procházet & Mazat")
        
        # Při zavření aplikace odpoj FTP
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _create_menu(self):
        """Vytvoří menu bar"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # FTP menu
        ftp_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="FTP", menu=ftp_menu)
        ftp_menu.add_command(label="Správa konfigurací", command=self._manage_configs)
        ftp_menu.add_separator()
        ftp_menu.add_command(label="Odpojit", command=self._disconnect_ftp)
        
        # Nastavení menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Nastavení", menu=settings_menu)
        settings_menu.add_command(label="Velikost thumbnailů", command=self._set_thumbnail_size)
        settings_menu.add_command(label="Kvalita komprimace", command=self._set_compress_quality)
        
        # O aplikaci
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Nápověda", menu=help_menu)
        help_menu.add_command(label="O aplikaci", command=self._show_about)
    
    def _manage_configs(self):
        """Otevře okno pro správu FTP konfigurací"""
        ConfigManagerWindow(self, self.config_manager)
    
    def _disconnect_ftp(self):
        """Odpojí FTP spojení"""
        if self.ftp_handler.connected:
            self.ftp_handler.disconnect()
            self.update_status("Odpojeno")
            messagebox.showinfo("FTP", "Odpojeno od FTP serveru")
        else:
            messagebox.showinfo("FTP", "Již odpojeno")
    
    def _set_thumbnail_size(self):
        """Nastaví velikost thumbnailů"""
        size = simpledialog.askinteger(
            "Velikost thumbnailů",
            "Zadejte maximální velikost thumbnailů (px):",
            initialvalue=self.image_processor.thumbnail_size,
            minvalue=100,
            maxvalue=1000
        )
        if size:
            self.image_processor.set_thumbnail_size(size)
            messagebox.showinfo("Nastavení", f"Velikost thumbnailů nastavena na {size}px")
    
    def _set_compress_quality(self):
        """Nastaví kvalitu komprimace"""
        quality = simpledialog.askinteger(
            "Kvalita komprimace",
            "Zadejte kvalitu komprimace (1-100):",
            initialvalue=self.image_processor.compress_quality,
            minvalue=1,
            maxvalue=100
        )
        if quality:
            self.image_processor.set_compress_quality(quality)
            messagebox.showinfo("Nastavení", f"Kvalita komprimace nastavena na {quality}")
    
    def _show_about(self):
        """Zobrazí informace o aplikaci"""
        messagebox.showinfo(
            "O aplikaci",
            "FTP Photo Manager v1.0\n\n"
            "Aplikace pro nahrávání a správu fotografií na FTP serveru.\n\n"
            "Funkce:\n"
            "• Automatické vytváření thumbnailů\n"
            "• Komprimace obrázků\n"
            "• Správa více FTP serverů\n"
            "• Procházení a mazání fotek"
        )
    
    def update_status(self, message: str):
        """Aktualizuje status bar"""
        self.status_bar.config(text=message)
        self.update_idletasks()
    
    def on_closing(self):
        """Handler při zavírání aplikace"""
        if self.ftp_handler.connected:
            self.ftp_handler.disconnect()
        self.destroy()


class ConfigManagerWindow(tk.Toplevel):
    """Okno pro správu FTP konfigurací"""
    
    def __init__(self, parent, config_manager: FTPConfig):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.title("Správa FTP konfigurací")
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()
        
        # Seznam konfigurací
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(list_frame, text="Uložené konfigurace:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Listbox s scrollbarem
        scroll_frame = ttk.Frame(list_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.config_listbox = tk.Listbox(scroll_frame, yscrollcommand=scrollbar.set, height=10)
        self.config_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.config_listbox.yview)
        
        # Tlačítka
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="➕ Přidat", command=self._add_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Upravit", command=self._edit_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Smazat", command=self._delete_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Zavřít", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        
        self._refresh_list()
    
    def _refresh_list(self):
        """Obnoví seznam konfigurací"""
        self.config_listbox.delete(0, tk.END)
        for name in self.config_manager.get_config_names():
            self.config_listbox.insert(tk.END, name)
    
    def _add_config(self):
        """Přidá novou konfiguraci"""
        dialog = ConfigDialog(self, "Přidat konfiguraci")
        self.wait_window(dialog)
        
        if dialog.result:
            success = self.config_manager.add_config(**dialog.result)
            if success:
                self._refresh_list()
                messagebox.showinfo("Úspěch", "Konfigurace přidána")
            else:
                messagebox.showerror("Chyba", "Konfigurace s tímto názvem již existuje")
    
    def _edit_config(self):
        """Upraví vybranou konfiguraci"""
        selection = self.config_listbox.curselection()
        if not selection:
            messagebox.showwarning("Upozornění", "Vyberte konfiguraci k úpravě")
            return
        
        name = self.config_listbox.get(selection[0])
        config = self.config_manager.get_config(name)
        
        dialog = ConfigDialog(self, "Upravit konfiguraci", config)
        self.wait_window(dialog)
        
        if dialog.result:
            success = self.config_manager.update_config(name, **dialog.result)
            if success:
                self._refresh_list()
                messagebox.showinfo("Úspěch", "Konfigurace aktualizována")
    
    def _delete_config(self):
        """Smaže vybranou konfiguraci"""
        selection = self.config_listbox.curselection()
        if not selection:
            messagebox.showwarning("Upozornění", "Vyberte konfiguraci ke smazání")
            return
        
        name = self.config_listbox.get(selection[0])
        if messagebox.askyesno("Potvrzení", f"Opravdu smazat konfiguraci '{name}'?"):
            self.config_manager.remove_config(name)
            self._refresh_list()
            messagebox.showinfo("Úspěch", "Konfigurace smazána")


class ConfigDialog(tk.Toplevel):
    """Dialog pro přidání/úpravu FTP konfigurace"""
    
    def __init__(self, parent, title: str, config: dict = None):
        super().__init__(parent)
        
        self.result = None
        self.title(title)
        self.geometry("400x250")
        self.transient(parent)
        self.grab_set()
        
        # Formulář
        form_frame = ttk.Frame(self, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Název
        ttk.Label(form_frame, text="Název:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=5)
        
        # Host
        ttk.Label(form_frame, text="Host:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.host_entry = ttk.Entry(form_frame, width=30)
        self.host_entry.grid(row=1, column=1, pady=5)
        
        # Port
        ttk.Label(form_frame, text="Port:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.port_entry = ttk.Entry(form_frame, width=30)
        self.port_entry.grid(row=2, column=1, pady=5)
        self.port_entry.insert(0, "21")
        
        # Username
        ttk.Label(form_frame, text="Uživatel:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=3, column=1, pady=5)
        
        # Password
        ttk.Label(form_frame, text="Heslo:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.password_entry.grid(row=4, column=1, pady=5)
        
        # Pokud upravujeme, předvyplň hodnoty
        if config:
            self.name_entry.insert(0, config['name'])
            self.host_entry.insert(0, config['host'])
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, str(config['port']))
            self.username_entry.insert(0, config['username'])
            self.password_entry.insert(0, config['password'])
        
        # Tlačítka
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(button_frame, text="Uložit", command=self._save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Zrušit", command=self.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _save(self):
        """Uloží konfiguraci"""
        name = self.name_entry.get().strip()
        host = self.host_entry.get().strip()
        port = self.port_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not all([name, host, port, username]):
            messagebox.showerror("Chyba", "Vyplňte všechna povinná pole")
            return
        
        try:
            port = int(port)
        except ValueError:
            messagebox.showerror("Chyba", "Port musí být číslo")
            return
        
        self.result = {
            'name': name,
            'host': host,
            'port': port,
            'username': username,
            'password': password
        }
        
        self.destroy()
