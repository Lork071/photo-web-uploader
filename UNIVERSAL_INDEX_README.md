# Univerzální Photo Index (universal_index.php)

## 📋 Popis

Univerzální PHP skript který automaticky projde složky `thumbnail`, `original`, `compress` a vrátí JSON se všemi nalezenými obrázky.

## 🎯 Výhody

- **Automatický** - nemusíš regenerovat při přidání nových fotek
- **Dynamický** - vždy vrátí aktuální stav
- **Inteligentní** - automaticky detekuje dostupné složky
- **Kompletní** - vrací metadata o souborech

## 📤 Použití v GUI

1. Připoj se k FTP
2. Naviguj do složky se strukturou (thumbnail/original/compress)
3. Klikni na **"📤 Nahrát univerzální PHP"**
4. Soubor se nahraje jako `index.php`

## 🔧 Manuální instalace

Nahraj `universal_index.php` na FTP a přejmenuj na `index.php` nebo přistupuj přímo:
```
http://tvujserver.cz/slozka/universal_index.php
```

## 📊 Formát výstupu

### Úspěšný výstup:
```json
{
    "success": true,
    "message": "Nalezeno 3 obrázků",
    "count": 3,
    "photos": [
        {
            "thumbnail": "thumbnail/foto1.jpg",
            "original": "original/foto1.jpg",
            "compress": "compress/foto1.jpg",
            "filename": "foto1.jpg",
            "size": 1234567
        },
        {
            "thumbnail": "thumbnail/foto2.jpg",
            "original": "original/foto2.jpg",
            "compress": "compress/foto2.jpg",
            "filename": "foto2.jpg",
            "size": 987654
        }
    ],
    "folders": {
        "thumbnail": true,
        "original": true,
        "compress": true
    }
}
```

### Když nejsou nalezeny fotky:
```json
{
    "success": false,
    "message": "Ve složkách nebyly nalezeny žádné obrázky",
    "photos": []
}
```

## 🆚 Rozdíl oproti statickému index.php

| Feature | Statický index.php | Univerzální index.php |
|---------|-------------------|---------------------|
| Aktualizace při nových fotkách | ❌ Musíš regenerovat | ✅ Automaticky |
| Rychlost | ⚡ Rychlejší (statický) | 🔄 O trochu pomalejší (skenuje) |
| Velikost souboru | 📄 Větší | 📄 Menší (kód) |
| Použití | Fixní galerie | Dynamická galerie |

## 💡 Kdy použít co?

**Statický index.php** (generovaný GUI):
- Když máš fixní sadu fotek
- Pro maximální výkon
- Když nechceš skenování při každém požadavku

**Univerzální index.php**:
- Když často přidáváš nové fotky
- Pro dynamické galerie
- Když chceš vždy aktuální stav
- Pro prototypování a vývoj

## 🔒 Bezpečnost

Skript je bezpečný protože:
- ✅ Nepřijímá žádné vstupy od uživatele
- ✅ Pouze čte existující soubory
- ✅ Vrací pouze JSON, nic nespouští
- ✅ Filtruje pouze obrazové formáty
- ✅ Nastavuje správné CORS hlavičky

## 📝 Podporované formáty

- JPG / JPEG
- PNG
- GIF
- BMP
- WEBP

## 🌐 CORS

Skript má nastaven `Access-Control-Allow-Origin: *` pro použití z jiných domén.
