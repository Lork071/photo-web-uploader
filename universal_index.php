<?php
/**
 * Auto Photo Index Generator
 * Automaticky projde složky thumbnail, original, compress a vrátí JSON s fotkami
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// Definuj složky které se budou prohledávat
$folders = ['thumbnail', 'original', 'compress'];

// Podporované formáty obrázků
$imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'];

/**
 * Získá všechny obrázky ve složce
 */
function getImagesInFolder($folderPath) {
    global $imageExtensions;
    $images = [];
    
    if (!is_dir($folderPath)) {
        return $images;
    }
    
    $files = scandir($folderPath);
    
    foreach ($files as $file) {
        if ($file === '.' || $file === '..') {
            continue;
        }
        
        $filePath = $folderPath . '/' . $file;
        
        // Pouze soubory, ne složky
        if (is_file($filePath)) {
            $extension = strtolower(pathinfo($file, PATHINFO_EXTENSION));
            
            if (in_array($extension, $imageExtensions)) {
                $images[] = $file;
            }
        }
    }
    
    sort($images);
    return $images;
}

/**
 * Získá base URL (protokol + doména + cesta ke složce)
 */
function getBaseUrl() {
    $protocol = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https://' : 'http://';
    $host = $_SERVER['HTTP_HOST'];
    $scriptPath = dirname($_SERVER['SCRIPT_NAME']);
    
    // Odstranění případného trailing slashe a přidání jednoho
    $scriptPath = rtrim($scriptPath, '/') . '/';
    
    return $protocol . $host . $scriptPath;
}

/**
 * Hlavní funkce - sestaví pole fotek
 */
function buildPhotoArray() {
    global $folders;
    
    // Získej base URL
    $baseUrl = getBaseUrl();
    
    // Zkontroluj zda složky existují
    $folderExists = [];
    foreach ($folders as $folder) {
        $folderExists[$folder] = is_dir($folder);
    }
    
    // Pokud žádná složka neexistuje, vrať prázdné pole
    if (!in_array(true, $folderExists)) {
        return [
            'success' => false,
            'message' => 'Složky thumbnail, original nebo compress nebyly nalezeny',
            'photos' => [],
            'base_url' => $baseUrl
        ];
    }
    
    // Získej seznam všech obrázků z thumbnail složky (nebo první dostupné)
    $referenceFolder = null;
    $allFiles = [];
    
    if ($folderExists['thumbnail']) {
        $referenceFolder = 'thumbnail';
        $allFiles = getImagesInFolder('thumbnail');
    } elseif ($folderExists['original']) {
        $referenceFolder = 'original';
        $allFiles = getImagesInFolder('original');
    } elseif ($folderExists['compress']) {
        $referenceFolder = 'compress';
        $allFiles = getImagesInFolder('compress');
    }
    
    if (empty($allFiles)) {
        return [
            'success' => false,
            'message' => 'Ve složkách nebyly nalezeny žádné obrázky',
            'photos' => [],
            'base_url' => $baseUrl
        ];
    }
    
    // Sestav pole fotek
    $photos = [];
    
    foreach ($allFiles as $filename) {
        $photo = [];
        
        // Pro každou složku zkontroluj zda soubor existuje a vytvoř plnou URL
        foreach ($folders as $folder) {
            $filePath = $folder . '/' . $filename;
            
            if (file_exists($filePath)) {
                // Relativní cesta
                $photo[$folder] = $filePath;
                // Plná URL
                $photo[$folder . '_url'] = $baseUrl . $filePath;
            } else {
                $photo[$folder] = null;
                $photo[$folder . '_url'] = null;
            }
        }
        
        // Přidej metadata
        $photo['filename'] = $filename;
        
        // Získej velikost souboru z první dostupné verze
        if (isset($photo['original']) && $photo['original']) {
            $photo['size'] = filesize($photo['original']);
        } elseif (isset($photo['compress']) && $photo['compress']) {
            $photo['size'] = filesize($photo['compress']);
        } elseif (isset($photo['thumbnail']) && $photo['thumbnail']) {
            $photo['size'] = filesize($photo['thumbnail']);
        }
        
        $photos[] = $photo;
    }
    
    return [
        'success' => true,
        'message' => 'Nalezeno ' . count($photos) . ' obrázků',
        'count' => count($photos),
        'base_url' => $baseUrl,
        'photos' => $photos,
        'folders' => $folderExists
    ];
}

// Vrať JSON
$result = buildPhotoArray();
echo json_encode($result, JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
?>
