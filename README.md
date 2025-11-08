# FTP Photo Manager

Python aplikace pro nahrávání a správu fotografií na FTP serveru s automatickým vytvářením thumbnailů a komprimací.

## Funkce

- **Nahrávání fotek na FTP**
  - Automatické vytváření thumbnailů (400px)
  - Komprimace originálních fotek
  - Organizace do složek: thumbnail/, original/, compress/
  - Progress bar při nahrávání

- **Správa FTP připojení**
  - Ukládání více FTP konfigurací
  - Snadné přepínání mezi servery

- **Procházení a mazání**
  - Zobrazení fotek ze serveru
  - Mazání jednotlivých fotek nebo výběru
  - Automatické mazání všech verzí (thumbnail, compress, original)

## Instalace

```bash
pip install -r requirements.txt
```

## Spuštění

```bash
python main.py
```

## Struktura projektu

- `main.py` - vstupní bod aplikace
- `gui/` - GUI komponenty
- `core/` - jádro aplikace (FTP, zpracování obrázků)
- `config/` - konfigurace
