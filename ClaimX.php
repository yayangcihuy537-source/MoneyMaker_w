<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');

// ============================================================
//  COLOR CONSTANTS
// ============================================================
define('RESET', "\033[0m");
define('RED', "\033[31m");
define('GREEN', "\033[32m");
define('YELLOW', "\033[33m");
define('CYAN', "\033[36m");
define('WHITE', "\033[37m");
define('B_RED', "\033[1;31m");
define('B_GREEN', "\033[1;32m");
define('B_YELLOW', "\033[1;33m");
define('B_CYAN', "\033[1;36m");
define('B_WHITE', "\033[1;37m");

// ============================================================
//  CONFIG
// ============================================================
const HOST = 'https://claimx.online';
const MAX_RUNTIME = 21600;
const CONFIG_FILE = 'claimx_config.json';
const COOKIE_FILE = 'claimx_cookie.txt';

// ============================================================
//  FUNGSI BANTU
// ============================================================

function clearScreen() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function printBanner() {
    clearScreen();
    echo B_CYAN . "==================================================\n";
    echo B_CYAN . "  " . B_WHITE . "ClaimX Auto Claim Bot" . B_CYAN . "  \n";
    echo B_CYAN . "==================================================\n";
    echo B_CYAN . "  Mode   : " . WHITE . "Icon Captcha Bypass\n";
    echo B_CYAN . "  Website: " . WHITE . HOST . "\n";
    echo B_CYAN . "  Runtime: " . WHITE . "Maks 6 jam\n";
    echo B_CYAN . "  Jeda   : " . WHITE . "14-19 detik (human-like)\n";
    echo B_CYAN . "==================================================\n\n";
}

function timer($seconds) {
    $wait_time = (int)$seconds;
    if ($wait_time <= 0) $wait_time = 5;
    $frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'];
    $current_frame = 0;
    while ($wait_time > 0) {
        $hours = floor($wait_time / 3600);
        $minutes = floor(($wait_time % 3600) / 60);
        $seconds_left = $wait_time % 60;
        $time_formatted = sprintf('%02d:%02d:%02d', $hours, $minutes, $seconds_left);
        $spinner = $frames[$current_frame];
        echo "\r" . B_YELLOW . "  ⏳ Waiting: " . B_WHITE . $time_formatted . " " . $spinner . "   " . RESET;
        sleep(1);
        $wait_time--;
        $current_frame = ($current_frame + 1) % count($frames);
    }
    echo "\r" . str_repeat(" ", 50) . "\r";
}

// ============================================================
//  HTTP REQUEST
// ============================================================
function httpRequest($url, $method = 'GET', $postData = null, $extraHeaders = []) {
    static $cookieFile = COOKIE_FILE;
    $ch = curl_init();
    $headers = [
        'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language: id-ID,en;q=0.9',
        'Accept-Encoding: gzip, deflate, br',
        'Connection: keep-alive',
        'Upgrade-Insecure-Requests: 1',
    ];
    foreach ($extraHeaders as $h) $headers[] = $h;

    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_MAXREDIRS => 10,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_COOKIEFILE => $cookieFile,
        CURLOPT_COOKIEJAR => $cookieFile,
        CURLOPT_HEADER => false,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_ENCODING => '',
    ]);
    if (strtoupper($method) === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    }
    $response = curl_exec($ch);
    $errno = curl_errno($ch);
    curl_close($ch);
    if ($errno) return false;
    return $response;
}

// ============================================================
//  PARSE CSRF
// ============================================================
function parseCSRF($html) {
    $patterns = [
        '/<input\s+[^>]*name\s*=\s*["\']csrf_token["\'][^>]*value\s*=\s*["\']([^"\']+)["\'][^>]*>/si',
        '/<input\s+[^>]*value\s*=\s*["\']([^"\']+)["\'][^>]*name\s*=\s*["\']csrf_token["\'][^>]*>/si',
        '/<input\s+[^>]*name\s*=\s*csrf_token[^>]*value\s*=\s*["\']([^"\']+)["\'][^>]*>/si',
        '/<meta\s+name=["\']csrf-token["\']\s+content=["\']([^"\']+)["\'][^>]*>/si',
        '/csrf_token\s*=\s*["\']([^"\']+)["\']/si',
        '/<form[^>]*data-csrf=["\']([^"\']+)["\'][^>]*>/si',
    ];
    foreach ($patterns as $p) {
        if (preg_match($p, $html, $m)) return $m[1];
    }
    return null;
}

// ============================================================
//  PARSE ICON CAPTCHA
// ============================================================
function parseIconCaptcha($html) {
    $targetIcon = null;
    
    // Cari target icon (berbagai kemungkinan)
    $patterns = [
        '/<div[^>]*class="[^"]*bg-dark[^"]*border-warning[^"]*"[^>]*>.*?<i[^>]*class="([^"]+)"[^>]*><\/i>/si',
        '/<div[^>]*class="[^"]*d-inline-flex[^"]*"[^>]*>.*?<i[^>]*class="([^"]+)"[^>]*><\/i>/si',
        '/<div[^>]*class="[^"]*text-warning[^"]*"[^>]*>.*?<i[^>]*class="([^"]+)"[^>]*><\/i>/si',
        '/<div[^>]*style="[^"]*background[^"]*"[^>]*>.*?<i[^>]*class="([^"]+)"[^>]*><\/i>/si',
    ];
    foreach ($patterns as $p) {
        if (preg_match($p, $html, $m)) {
            $targetIcon = $m[1];
            break;
        }
    }

    // Cari pilihan tombol
    $choices = [];
    if (preg_match_all('/<button[^>]*data-key="([^"]+)"[^>]*>.*?<i[^>]*class="([^"]+)"[^>]*><\/i>.*?<\/button>/si', $html, $matches, PREG_SET_ORDER)) {
        foreach ($matches as $m) {
            $choices[] = ['key' => $m[1], 'icon' => $m[2]];
        }
    }
    // Alternatif: cari tombol dengan class icon-captcha-btn
    if (empty($choices)) {
        if (preg_match_all('/<button[^>]*class="[^"]*icon-captcha-btn[^"]*"[^>]*>.*?<i[^>]*class="([^"]+)"[^>]*><\/i>.*?<\/button>/si', $html, $matches, PREG_SET_ORDER)) {
            foreach ($matches as $m) {
                if (preg_match('/data-key="([^"]+)"/i', $m[0], $k)) {
                    $choices[] = ['key' => $k[1], 'icon' => $m[1]];
                }
            }
        }
    }

    return [$targetIcon, $choices];
}

// ============================================================
//  GET BALANCE DARI DASHBOARD
// ============================================================
function getBalance() {
    $html = httpRequest(HOST . '/dashboard');
    if (!$html) return '0.00000000';
    
    // Cari balance di berbagai tempat
    $patterns = [
        '/Earnings Balance.*?<h3[^>]*class="[^"]*fs-4[^"]*"[^>]*>([0-9.]+)/si',
        '/stat-card[^>]*>.*?text-success[^>]*>([0-9.]+)/si',
        '/balance[^>]*>([0-9.]+)/si',
        '/text-success[^>]*>([0-9.]+)/si',
    ];
    foreach ($patterns as $p) {
        if (preg_match($p, $html, $m)) {
            return $m[1];
        }
    }
    return '0.00000000';
}

// ============================================================
//  LOGIN
// ============================================================
function doLogin($email, $password) {
    if (file_exists(COOKIE_FILE)) unlink(COOKIE_FILE);
    echo B_CYAN . "  [LOGIN] Attempting login...\n" . RESET;
    
    $html = httpRequest(HOST . '/login');
    if (!$html) {
        echo B_RED . "  [ERROR] Gagal mengambil halaman login.\n" . RESET;
        return false;
    }
    
    $csrf = parseCSRF($html);
    if (!$csrf) {
        echo B_RED . "  [ERROR] CSRF token tidak ditemukan.\n" . RESET;
        return false;
    }
    
    list($targetIcon, $choices) = parseIconCaptcha($html);
    
    if (!$targetIcon || empty($choices)) {
        echo B_RED . "  [ERROR] Captcha tidak ditemukan di halaman login.\n" . RESET;
        return false;
    }
    
    $selectedKey = null;
    foreach ($choices as $choice) {
        $targetParts = explode(' ', $targetIcon);
        $choiceParts = explode(' ', $choice['icon']);
        foreach ($targetParts as $tp) {
            foreach ($choiceParts as $cp) {
                if (strcasecmp($tp, $cp) === 0 && strpos($tp, 'bi-') !== false) {
                    $selectedKey = $choice['key'];
                    break 3;
                }
            }
        }
        if (!$selectedKey && strcasecmp($targetIcon, $choice['icon']) === 0) {
            $selectedKey = $choice['key'];
        }
    }
    
    if (!$selectedKey) {
        echo B_RED . "  [ERROR] Tidak ada pilihan yang cocok.\n" . RESET;
        return false;
    }

    $postData = http_build_query([
        'csrf_token' => $csrf,
        'email' => $email,
        'password' => $password,
        'icon_captcha_selected' => $selectedKey
    ]);
    $extraHeaders = [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: ' . HOST,
        'Referer: ' . HOST . '/login',
    ];
    $response = httpRequest(HOST . '/login', 'POST', $postData, $extraHeaders);
    if ($response === false) {
        echo B_RED . "  [ERROR] Login request gagal.\n" . RESET;
        return false;
    }
    
    if (strpos($response, 'Dashboard') !== false || strpos($response, 'Welcome back') !== false) {
        echo B_GREEN . "  [SUCCESS] Login berhasil!\n" . RESET;
        return true;
    } else {
        echo B_RED . "  [ERROR] Login gagal.\n" . RESET;
        return false;
    }
}

// ============================================================
//  CLAIM FAUCET (DENGAN DETEKSI CAPTCHA OTOMATIS)
// ============================================================
function claimFaucet(&$rewardInfo) {
    $html = httpRequest(HOST . '/faucet');
    if (!$html) {
        echo B_RED . "  [ERROR] Gagal mengakses faucet.\n" . RESET;
        return false;
    }

    // Cek cooldown
    if (preg_match('/id="countdownClock"[^>]*data-seconds="(\d+)"/i', $html, $m)) {
        $seconds = (int)$m[1];
        if ($seconds > 0) {
            echo B_YELLOW . "  [COOLDOWN] " . $seconds . "s tersisa.\n" . RESET;
            timer($seconds);
            return 'cooldown';
        }
    }

    // Cek apakah ada form claim
    if (strpos($html, 'faucetForm') === false) {
        echo B_YELLOW . "  [INFO] Form claim tidak ditemukan.\n" . RESET;
        return 'no_form';
    }

    // Ambil CSRF
    $csrf = parseCSRF($html);
    if (!$csrf) {
        echo B_RED . "  [ERROR] CSRF tidak ditemukan.\n" . RESET;
        return false;
    }

    // Cek apakah ada captcha di halaman
    list($targetIcon, $choices) = parseIconCaptcha($html);
    
    // Jika tidak ada captcha, langsung claim
    if (!$targetIcon || empty($choices)) {
        echo B_YELLOW . "  [INFO] Tidak ada captcha, claim langsung...\n" . RESET;
        $postData = http_build_query([
            'csrf_token' => $csrf
        ]);
    } else {
        // Ada captcha, cari jawaban
        echo B_YELLOW . "  [INFO] Captcha ditemukan, menyelesaikan...\n" . RESET;
        $selectedKey = null;
        foreach ($choices as $choice) {
            $targetParts = explode(' ', $targetIcon);
            $choiceParts = explode(' ', $choice['icon']);
            foreach ($targetParts as $tp) {
                foreach ($choiceParts as $cp) {
                    if (strcasecmp($tp, $cp) === 0 && strpos($tp, 'bi-') !== false) {
                        $selectedKey = $choice['key'];
                        break 3;
                    }
                }
            }
            if (!$selectedKey && strcasecmp($targetIcon, $choice['icon']) === 0) {
                $selectedKey = $choice['key'];
            }
        }
        
        if (!$selectedKey) {
            echo B_RED . "  [ERROR] Ikon target tidak cocok.\n" . RESET;
            return false;
        }
        
        $postData = http_build_query([
            'csrf_token' => $csrf,
            'icon_captcha_selected' => $selectedKey
        ]);
    }
    
    // Kirim POST claim
    $extraHeaders = [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: ' . HOST,
        'Referer: ' . HOST . '/faucet',
    ];
    $response = httpRequest(HOST . '/faucet/claim', 'POST', $postData, $extraHeaders);
    if ($response === false) {
        echo B_RED . "  [ERROR] Claim request gagal.\n" . RESET;
        return false;
    }

    // Cek hasil claim
    if (preg_match('/alert-success[^>]*>Claim successful! Received \+([0-9.]+) USDT\./i', $response, $m)) {
        echo B_GREEN . "  [SUCCESS] +{$m[1]} USDT\n" . RESET;
        $rewardInfo = ['amount' => $m[1]];
        return true;
    } else {
        // Cek apakah ada error karena captcha
        if (strpos($response, 'Invalid captcha') !== false || strpos($response, 'captcha') !== false) {
            echo B_RED . "  [ERROR] Captcha salah.\n" . RESET;
        } else {
            echo B_RED . "  [ERROR] Claim gagal.\n" . RESET;
        }
        return false;
    }
}

// ============================================================
//  MAIN
// ============================================================
printBanner();

if (!file_exists(CONFIG_FILE)) {
    echo WHITE . "Email: " . CYAN;
    $email = trim(fgets(STDIN));
    echo WHITE . "Password: " . CYAN;
    $password = trim(fgets(STDIN));
    file_put_contents(CONFIG_FILE, json_encode(['email' => $email, 'password' => $password], JSON_PRETTY_PRINT));
    echo B_GREEN . "Config saved.\n\n" . RESET;
} else {
    $config = json_decode(file_get_contents(CONFIG_FILE), true);
    $email = $config['email'];
    $password = $config['password'];
}

if (!doLogin($email, $password)) exit(1);

// Ambil balance awal
$balance = getBalance();
echo B_CYAN . "  [BALANCE] " . B_WHITE . $balance . " USDT\n" . RESET;

$startTime = time();
$claims = 0;
$failures = 0;
$maxFailures = 10; // Dinaikkan karena captcha kadang muncul

echo B_CYAN . "  [START] Bot dimulai...\n\n" . RESET;

while (true) {
    if (time() - $startTime >= MAX_RUNTIME) {
        echo B_YELLOW . "  [STOP] 6 jam berlalu.\n" . RESET;
        break;
    }

    // Cek session
    $html = httpRequest(HOST . '/dashboard');
    if (!$html || strpos($html, 'Welcome back') === false) {
        echo B_YELLOW . "  [INFO] Session expired, login ulang...\n" . RESET;
        if (!doLogin($email, $password)) {
            echo B_RED . "  [ERROR] Login ulang gagal.\n" . RESET;
            break;
        }
        $balance = getBalance();
        echo B_CYAN . "  [BALANCE] " . B_WHITE . $balance . " USDT\n" . RESET;
        continue;
    }

    $rewardInfo = [];
    $result = claimFaucet($rewardInfo);

    if ($result === 'cooldown' || $result === 'no_form') {
        $delay = rand(14, 19);
        echo B_YELLOW . "  ⏳ Human delay: {$delay}s\n" . RESET;
        sleep($delay);
        continue;
    }

    if ($result === true) {
        $claims++;
        $failures = 0;
        // Update balance setiap claim (ambil dari dashboard)
        $balance = getBalance();
        echo B_CYAN . "  [BALANCE] " . B_WHITE . $balance . " USDT\n" . RESET;
        echo B_GREEN . "  [TOTAL] Claims: {$claims}\n" . RESET;
        $delay = rand(14, 19);
        echo B_YELLOW . "  ⏳ Human delay: {$delay}s\n" . RESET;
        sleep($delay);
    } else {
        $failures++;
        echo B_RED . "  [FAIL] ({$failures}/{$maxFailures})\n" . RESET;
        if ($failures >= $maxFailures) {
            echo B_RED . "  [STOP] Terlalu banyak gagal.\n" . RESET;
            break;
        }
        $delay = rand(14, 19);
        echo B_YELLOW . "  ⏳ Human delay: {$delay}s\n" . RESET;
        sleep($delay);
    }
}

// Balance akhir
$balance = getBalance();
echo B_CYAN . "\n  [FINAL BALANCE] " . B_WHITE . $balance . " USDT\n" . RESET;
echo B_CYAN . "  Total claims: " . B_WHITE . $claims . "\n" . RESET;
