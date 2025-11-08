import ftplib
import os
from typing import List, Tuple, Callable, Optional
from io import BytesIO


class FTPHandler:
    """Třída pro práci s FTP serverem"""
    
    def __init__(self):
        self.ftp = None
        self.connected = False
        self.current_path = "/"
    
    def connect(self, host: str, port: int, username: str, password: str) -> Tuple[bool, str]:
        """
        Připojí se k FTP serveru
        Returns: (success, message)
        """
        try:
            self.ftp = ftplib.FTP()
            self.ftp.connect(host, port, timeout=10)
            self.ftp.login(username, password)
            self.connected = True
            self.current_path = self.ftp.pwd()
            return True, "Připojeno úspěšně"
        except ftplib.error_perm as e:
            return False, f"Chyba přihlášení: {str(e)}"
        except Exception as e:
            return False, f"Chyba připojení: {str(e)}"
    
    def disconnect(self):
        """Odpojí se od FTP serveru"""
        if self.ftp and self.connected:
            try:
                self.ftp.quit()
            except:
                pass
            finally:
                self.connected = False
                self.ftp = None
    
    def list_directory(self, path: str = None) -> List[Tuple[str, bool]]:
        """
        Vrátí seznam souborů a složek v daném adresáři
        Returns: List of (name, is_directory)
        """
        if not self.connected:
            return []
        
        try:
            if path:
                self.ftp.cwd(path)
                self.current_path = self.ftp.pwd()
            
            items = []
            
            # Použijeme MLSD pokud je k dispozici, jinak LIST
            try:
                for name, facts in self.ftp.mlsd():
                    if name in ['.', '..']:
                        continue
                    is_dir = facts.get('type', '') == 'dir'
                    items.append((name, is_dir))
            except:
                # Fallback na starší metodu
                lines = []
                self.ftp.dir(lines.append)
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 9:
                        name = ' '.join(parts[8:])
                        is_dir = line.startswith('d')
                        items.append((name, is_dir))
            
            return sorted(items, key=lambda x: (not x[1], x[0].lower()))
        except Exception as e:
            print(f"Chyba při listování adresáře: {e}")
            return []
    
    def create_directory(self, dirname: str) -> Tuple[bool, str]:
        """Vytvoří nový adresář"""
        if not self.connected:
            return False, "Nepřipojeno"
        
        try:
            self.ftp.mkd(dirname)
            return True, f"Složka '{dirname}' vytvořena"
        except ftplib.error_perm as e:
            if "exists" in str(e).lower():
                return True, f"Složka '{dirname}' již existuje"
            return False, f"Chyba: {str(e)}"
        except Exception as e:
            return False, f"Chyba při vytváření složky: {str(e)}"
    
    def upload_file(self, local_path: str, remote_path: str, 
                   progress_callback: Optional[Callable[[int, int], None]] = None) -> Tuple[bool, str]:
        """
        Nahraje soubor na FTP
        progress_callback: funkce(bytes_uploaded, total_bytes)
        """
        if not self.connected:
            return False, "Nepřipojeno"
        
        try:
            file_size = os.path.getsize(local_path)
            uploaded = [0]  # Použijeme list kvůli closure
            
            def callback(data):
                uploaded[0] += len(data)
                if progress_callback:
                    progress_callback(uploaded[0], file_size)
            
            with open(local_path, 'rb') as f:
                self.ftp.storbinary(f'STOR {remote_path}', f, callback=callback)
            
            return True, "Nahráno"
        except Exception as e:
            return False, f"Chyba při nahrávání: {str(e)}"
    
    def upload_bytes(self, data: bytes, remote_path: str,
                    progress_callback: Optional[Callable[[int, int], None]] = None) -> Tuple[bool, str]:
        """
        Nahraje data (bytes) na FTP
        """
        if not self.connected:
            return False, "Nepřipojeno"
        
        try:
            file_size = len(data)
            uploaded = [0]
            
            def callback(chunk):
                uploaded[0] += len(chunk)
                if progress_callback:
                    progress_callback(uploaded[0], file_size)
            
            bio = BytesIO(data)
            self.ftp.storbinary(f'STOR {remote_path}', bio, callback=callback)
            return True, "Nahráno"
        except Exception as e:
            return False, f"Chyba při nahrávání: {str(e)}"
    
    def download_file(self, remote_path: str, local_path: str = None) -> Tuple[bool, bytes, str]:
        """
        Stáhne soubor z FTP
        Returns: (success, data, message)
        """
        if not self.connected:
            return False, b"", "Nepřipojeno"
        
        try:
            bio = BytesIO()
            self.ftp.retrbinary(f'RETR {remote_path}', bio.write)
            data = bio.getvalue()
            
            if local_path:
                with open(local_path, 'wb') as f:
                    f.write(data)
            
            return True, data, "Staženo"
        except Exception as e:
            return False, b"", f"Chyba při stahování: {str(e)}"
    
    def delete_file(self, remote_path: str) -> Tuple[bool, str]:
        """Smaže soubor z FTP"""
        if not self.connected:
            return False, "Nepřipojeno"
        
        try:
            self.ftp.delete(remote_path)
            return True, "Smazáno"
        except Exception as e:
            return False, f"Chyba při mazání: {str(e)}"
    
    def delete_directory(self, dirname: str) -> Tuple[bool, str]:
        """Smaže prázdný adresář"""
        if not self.connected:
            return False, "Nepřipojeno"
        
        try:
            self.ftp.rmd(dirname)
            return True, "Složka smazána"
        except Exception as e:
            return False, f"Chyba při mazání složky: {str(e)}"
    
    def change_directory(self, path: str) -> Tuple[bool, str]:
        """Změní aktuální adresář"""
        if not self.connected:
            return False, "Nepřipojeno"
        
        try:
            self.ftp.cwd(path)
            self.current_path = self.ftp.pwd()
            return True, self.current_path
        except Exception as e:
            return False, f"Chyba: {str(e)}"
    
    def get_current_path(self) -> str:
        """Vrátí aktuální cestu"""
        return self.current_path if self.connected else ""
    
    def path_exists(self, path: str) -> bool:
        """Zkontroluje, zda cesta existuje"""
        if not self.connected:
            return False
        
        try:
            current = self.ftp.pwd()
            self.ftp.cwd(path)
            self.ftp.cwd(current)
            return True
        except:
            return False
    
    def has_photo_structure(self, path: str = None) -> Tuple[bool, List[str]]:
        """
        Zkontroluje, zda složka obsahuje strukturu thumbnail/original/compress
        Returns: (has_structure, list_of_found_folders)
        """
        if not self.connected:
            return False, []
        
        try:
            if path:
                current = self.ftp.pwd()
                self.ftp.cwd(path)
            
            items = self.list_directory()
            folder_names = [name.lower() for name, is_dir in items if is_dir]
            
            expected = ['thumbnail', 'original', 'compress']
            found = [f for f in expected if f in folder_names]
            
            if path:
                self.ftp.cwd(current)
            
            return len(found) == 3, found
        except:
            return False, []
