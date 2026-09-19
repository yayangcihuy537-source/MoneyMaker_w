<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');

// ============================================================
//  COLOR
// ============================================================
define('RESET', "\033[0m");
define('RED', "\033[31m");
define('GREEN', "\033[32m");
define('YELLOW', "\033[33m");
define('BLUE', "\033[34m");
define('MAGENTA', "\033[35m");
define('CYAN', "\033[36m");
define('WHITE', "\033[37m");
define('GRAY', "\033[90m");
define('B_RED', "\033[1;31m");
define('B_GREEN', "\033[1;32m");
define('B_YELLOW', "\033[1;33m");
define('B_CYAN', "\033[1;36m");
define('B_WHITE', "\033[1;37m");

// ============================================================
//  CONFIG
// ============================================================
const HOST = 'https://claimx.online';
const MAX_DAILY_CLAIMS = 100;
const CONFIG_FILE  = 'claimx_config.json';
const COOKIE_FILE  = 'claimx_cookie.txt';
const DAILY_FILE   = 'claimx_daily.txt';
const AD_SECRET    = 'claimx_ad_secret_2026';

// ============================================================
//  UTILS
// ============================================================
function clearScreen() { (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w')); }

function printBanner() {
    clearScreen();
    echo B_CYAN . "==================================================\n";
    echo B_CYAN . "  " . B_WHITE . "ClaimX Auto Claim Bot" . B_CYAN . "  \n";
    echo B_CYAN . "==================================================\n";
    echo B_CYAN . "  Mode   : " . WHITE . "Icon Captcha Bypass + Ad-Verify Bypass\n";
    echo B_CYAN . "  Website: " . WHITE . HOST . "\n";
    echo B_CYAN . "  Limit  : " . WHITE . MAX_DAILY_CLAIMS . " claim/hari (free member)\n";
    echo B_CYAN . "  Jeda   : " . WHITE . "14-19 detik (human-like)\n";
    echo B_CYAN . "==================================================\n\n";
}

function timer($seconds) {
    $w = (int)$seconds;
    if ($w <= 0) return;
    $f = ['⣾','⣽','⣻','⢿','⡿','⣟','⣯','⣷'];
    $i = 0;
    while ($w > 0) {
        $tf = sprintf('%02d:%02d:%02d', floor($w/3600), floor(($w%3600)/60), $w%60);
        echo "\r" . B_YELLOW . "  ⏳ Waiting: " . B_WHITE . $tf . " " . $f[$i] . "   " . RESET;
        sleep(1);
        $w--;
        $i = ($i + 1) % count($f);
    }
    echo "\r" . str_repeat(" ", 60) . "\r";
}

// ============================================================
//  HTTP
// ============================================================
function req($url, $method = 'GET', $post = null, $extra = []) {
    $ch = curl_init();
    $headers = array_merge([
        'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language: id-ID,id;q=0.9,en;q=0.8',
        'Accept-Encoding: gzip, deflate, br',
        'Connection: keep-alive',
        'Upgrade-Insecure-Requests: 1',
    ], $extra);
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_MAXREDIRS => 10,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_COOKIEFILE => COOKIE_FILE,
        CURLOPT_COOKIEJAR  => COOKIE_FILE,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_CONNECTTIMEOUT => 15,
        CURLOPT_ENCODING => '',
    ]);
    if (strtoupper($method) === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $post);
    }
    $r = curl_exec($ch);
    $err = curl_errno($ch);
    curl_close($ch);
    return $err ? false : $r;
}

// ============================================================
//  PARSERS
// ============================================================
function parseCSRF($html) {
    $pats = [
        '/<input\s+[^>]*name\s*=\s*["\']csrf_token["\'][^>]*value\s*=\s*["\']([^"\']+)["\'][^>]*>/si',
        '/<input\s+[^>]*value\s*=\s*["\']([^"\']+)["\'][^>]*name\s*=\s*["\']csrf_token["\'][^>]*>/si',
        '/name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']/si',
        '/csrf_token\s*[:=]\s*["\']([^"\']+)["\']/si',
    ];
    foreach ($pats as $p) if (preg_match($p, $html, $m)) return $m[1];
    return null;
}

function parseAdSeed($html) {
    if (preg_match('/const\s+adSeed\s*=\s*["\']([a-f0-9]{16,})["\']/i', $html, $m)) return $m[1];
    if (preg_match('/adSeed\s*[:=]\s*["\']([a-f0-9]{16,})["\']/i', $html, $m)) return $m[1];
    return null;
}

function parseIconCaptcha($html) {
    $target = null;
    if (preg_match('/<div[^>]*class="[^"]*text-warning[^"]*"[^>]*>.*?<i[^>]*class="([^"]+)"[^>]*><\/i>/si', $html, $m)) {
        $target = $m[1];
    } elseif (preg_match('/<div[^>]*class="[^"]*bg-dark[^"]*border-warning[^"]*"[^>]*>.*?<i[^>]*class="([^"]+)"[^>]*><\/i>/si', $html, $m)) {
        $target = $m[1];
    }
    $choices = [];
    if (preg_match_all('/<button[^>]*data-key="([^"]+)"[^>]*>.*?<i[^>]*class="([^"]+)"[^>]*><\/i>.*?<\/button>/si', $html, $ms, PREG_SET_ORDER)) {
        foreach ($ms as $m) $choices[] = ['key'=>$m[1], 'icon'=>$m[2]];
    }
    return [$target, $choices];
}

function matchIcon($target, $choices) {
    if (!$target || empty($choices)) return null;
    foreach ($choices as $c) {
        $tp = explode(' ', $target);
        $cp = explode(' ', $c['icon']);
        foreach ($tp as $a) foreach ($cp as $b) {
            if (strcasecmp($a, $b) === 0 && strpos($a, 'bi-') !== false) return $c['key'];
        }
        if (strcasecmp($target, $c['icon']) === 0) return $c['key'];
    }
    return null;
}

// ============================================================
//  TOKEN GENERATOR
// ============================================================
function generateToken($seed) {
    return hash_hmac('sha256', $seed, AD_SECRET);
}

// ============================================================
//  DAILY COUNTER
// ============================================================
function getDailyCount() {
    if (file_exists(DAILY_FILE)) {
        $d = json_decode(file_get_contents(DAILY_FILE), true);
        if (($d['date'] ?? '') === date('Y-m-d')) return (int)$d['count'];
    }
    return 0;
}
function updateDailyCount($c) {
    file_put_contents(DAILY_FILE, json_encode(['date'=>date('Y-m-d'), 'count'=>$c]));
}
function resetDailyIfNeeded() {
    if (file_exists(DAILY_FILE)) {
        $d = json_decode(file_get_contents(DAILY_FILE), true);
        if (($d['date'] ?? '') !== date('Y-m-d')) { updateDailyCount(0); return true; }
    }
    return false;
}

// ============================================================
//  BALANCE / LIMIT
// ============================================================
function getBalance() {
    $html = req(HOST . '/dashboard');
    if (!$html) return '0.00000000';
    $pats = [
        '/Earnings Balance.*?<h3[^>]*class="[^"]*fs-4[^"]*"[^>]*>([0-9.]+)/si',
        '/balance[^>]*>([0-9.]+)/si',
        '/text-success[^>]*>([0-9.]+)/si',
    ];
    foreach ($pats as $p) if (preg_match($p, $html, $m)) return $m[1];
    return '0.00000000';
}
function checkDailyLimit($html) {
    return strpos($html, 'Daily Limit Reached') !== false
        || strpos($html, 'You have completed all') !== false
        || strpos($html, 'Upgrade Membership') !== false;
}

// ============================================================
//  LOGIN
// ============================================================
function doLogin($email, $password) {
    if (file_exists(COOKIE_FILE)) unlink(COOKIE_FILE);
    echo B_CYAN . "  [LOGIN] Attempting login...\n" . RESET;

    $html = req(HOST . '/login');
    if (!$html) { echo B_RED . "  [ERROR] Gagal ambil /login\n" . RESET; return false; }

    $csrf = parseCSRF($html);
    if (!$csrf) { echo B_RED . "  [ERROR] CSRF login ga ketemu\n" . RESET; return false; }

    list($target, $choices) = parseIconCaptcha($html);
    if (!$target || empty($choices)) { echo B_RED . "  [ERROR] Captcha login ga ketemu\n" . RESET; return false; }

    $key = matchIcon($target, $choices);
    if (!$key) { echo B_RED . "  [ERROR] Ikon login ga match\n" . RESET; return false; }

    $post = http_build_query([
        'csrf_token' => $csrf,
        'email' => $email,
        'password' => $password,
        'icon_captcha_selected' => $key
    ]);
    $r = req(HOST . '/login', 'POST', $post, [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: ' . HOST,
        'Referer: ' . HOST . '/login',
    ]);
    if ($r === false) { echo B_RED . "  [ERROR] POST login gagal\n" . RESET; return false; }

    if (strpos($r, 'Dashboard') !== false || strpos($r, 'Welcome back') !== false) {
        echo B_GREEN . "  [SUCCESS] Login OK\n" . RESET;
        return true;
    }
    echo B_RED . "  [ERROR] Login reject\n" . RESET;
    return false;
}

// ============================================================
//  CLAIM
// ============================================================
function claimFaucet(&$info, $retry = 0) {
    if ($retry > 5) { echo B_RED . "  [ERROR] Retry limit\n" . RESET; return false; }

    $html = req(HOST . '/faucet');
    if (!$html) { sleep(2); return claimFaucet($info, $retry + 1); }

    if (checkDailyLimit($html)) {
        echo B_RED . "  [LIMIT] Daily limit reached.\n" . RESET;
        return 'limit_reached';
    }

    $hasForm = strpos($html, 'id="faucetForm"') !== false || strpos($html, 'name="csrf_token"') !== false;

    if (!$hasForm) {
        if (preg_match('/id="countdownClock"[^>]*data-seconds=["\']?(\d+)/i', $html, $m)) {
            $s = (int)$m[1];
            if ($s > 0) {
                echo B_YELLOW . "  [COOLDOWN] {$s}s\n" . RESET;
                timer($s);
                return 'cooldown';
            }
        }
        sleep(3);
        return claimFaucet($info, $retry + 1);
    }

    $csrf = parseCSRF($html);
    if (!$csrf) { sleep(2); return claimFaucet($info, $retry + 1); }

    $seed = parseAdSeed($html);
    if (!$seed) {
        echo B_YELLOW . "  [AD] seed tidak ditemukan, retry...\n" . RESET;
        sleep(2);
        return claimFaucet($info, $retry + 1);
    }

    $token = generateToken($seed);
    echo B_CYAN . "  [AD] seed=" . substr($seed, 0, 8) . "... token=" . substr($token, 0, 16) . "...\n" . RESET;

    list($target, $choices) = parseIconCaptcha($html);
    $key = matchIcon($target, $choices);

    $postArr = [
        'csrf_token' => $csrf,
        'ad_verification_token' => $token,
    ];
    if ($key) $postArr['icon_captcha_selected'] = $key;

    $r = req(HOST . '/faucet/claim', 'POST', http_build_query($postArr), [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: ' . HOST,
        'Referer: ' . HOST . '/faucet',
        'sec-fetch-site: same-origin',
        'sec-fetch-mode: navigate',
        'sec-fetch-dest: document',
    ]);
    if ($r === false) { sleep(2); return claimFaucet($info, $retry + 1); }

    if (checkDailyLimit($r)) {
        echo B_RED . "  [LIMIT] Daily limit reached.\n" . RESET;
        return 'limit_reached';
    }

    // Success
    if (preg_match('/Claim successful!\s*Received\s*\+?([0-9.]+)\s*USDT/i', $r, $m)) {
        echo B_GREEN . "  [SUCCESS] +{$m[1]} USDT\n" . RESET;
        $info = ['amount' => $m[1]];
        return true;
    }
    if (preg_match('/alert-success[^>]*>([^<]*?Received[^<]*?)</i', $r, $m)) {
        if (preg_match('/([0-9.]+)/', $m[1], $n)) {
            echo B_GREEN . "  [SUCCESS] +{$n[1]} USDT\n" . RESET;
            $info = ['amount' => $n[1]];
            return true;
        }
    }

    // Error
    if (preg_match('/alert-(?:danger|warning)[^>]*>([^<]+)</i', $r, $m)) {
        $err = trim($m[1]);
        echo B_RED . "  [SERVER] {$err}\n" . RESET;

        if (stripos($err, 'adblock') !== false) return 'cooldown';
        if (stripos($err, 'wait') !== false || stripos($err, 'cooldown') !== false) {
            if (preg_match('/(\d+)\s*second/i', $err, $s)) timer((int)$s[1]);
            return 'cooldown';
        }
        if (stripos($err, 'captcha') !== false || stripos($err, 'verification') !== false) {
            sleep(2);
            return claimFaucet($info, $retry + 1);
        }
    }

    if (strlen($r) < 100) { sleep(2); return claimFaucet($info, $retry + 1); }

    echo B_RED . "  [ERROR] Claim gagal (unknown).\n" . RESET;
    return false;
}

// ============================================================
//  FARMING
// ============================================================
function startFarming($email, $password) {
    if (!doLogin($email, $password)) return;

    $balance = getBalance();
    $dailyCount = getDailyCount();
    echo B_CYAN . "  [BALANCE] " . B_WHITE . $balance . " USDT\n" . RESET;
    echo B_CYAN . "  [DAILY] " . B_WHITE . $dailyCount . "/" . MAX_DAILY_CLAIMS . "\n" . RESET;
    echo B_CYAN . "  [START] Bot jalan...\n\n" . RESET;

    $claims = 0;
    $failures = 0;
    $maxFailures = 10;

    while (true) {
        if (resetDailyIfNeeded()) $dailyCount = 0;

        $dash = req(HOST . '/dashboard');
        if (!$dash || strpos($dash, 'Welcome back') === false) {
            echo B_YELLOW . "  [INFO] Session expired, re-login...\n" . RESET;
            if (!doLogin($email, $password)) break;
            continue;
        }

        if ($dailyCount >= MAX_DAILY_CLAIMS) {
            echo B_RED . "  [LIMIT] Habis kuota harian.\n" . RESET;
            $wait = strtotime('tomorrow 00:00:00') - time();
            timer($wait);
            continue;
        }

        $info = [];
        $res = claimFaucet($info);

        if ($res === 'limit_reached') {
            echo B_RED . "  [STOP] Limit harian.\n" . RESET;
            break;
        } elseif ($res === 'cooldown') {
            $delay = rand(14, 19);
            echo B_YELLOW . "  ⏳ delay {$delay}s\n" . RESET;
            sleep($delay);
            continue;
        } elseif ($res === true) {
            $claims++;
            $dailyCount++;
            updateDailyCount($dailyCount);
            $failures = 0;
            $balance = getBalance();
            echo B_CYAN . "  [BALANCE] " . B_WHITE . $balance . " USDT\n" . RESET;
            echo B_CYAN . "  [DAILY] " . B_WHITE . $dailyCount . "/" . MAX_DAILY_CLAIMS . "\n" . RESET;
            echo B_GREEN . "  [TOTAL] {$claims}\n" . RESET;
        } else {
            $failures++;
            echo B_RED . "  [FAIL] {$failures}/{$maxFailures}\n" . RESET;
            if ($failures >= $maxFailures) {
                echo B_RED . "  [STOP] Gagal terus.\n" . RESET;
                break;
            }
        }

        if ($res !== 'cooldown') {
            $delay = rand(14, 19);
            echo B_YELLOW . "  ⏳ delay {$delay}s\n" . RESET;
            sleep($delay);
        }
    }

    $balance = getBalance();
    echo B_CYAN . "\n  [FINAL] " . B_WHITE . $balance . " USDT | Total: {$claims}\n" . RESET;
}

// ============================================================
//  MENU
// ============================================================
function printMenu() {
    printBanner();
    echo B_CYAN . "  [1] " . B_GREEN . "Start Farming\n";
    echo B_CYAN . "  [2] " . B_YELLOW . "Config Email & Password\n";
    echo B_CYAN . "  [0] " . B_RED . "Exit\n";
    echo B_CYAN . "==================================================\n";
    echo B_WHITE . "  Pilih: " . RESET;
}

function configEmailPassword() {
    clearScreen();
    echo B_CYAN . "==================================================\n";
    echo B_CYAN . "  " . B_WHITE . "Konfigurasi Akun\n";
    echo B_CYAN . "==================================================\n\n";

    echo B_WHITE . "Email: " . RESET;
    $e = trim(fgets(STDIN));
    echo B_WHITE . "Password: " . RESET;
    $p = trim(fgets(STDIN));

    file_put_contents(CONFIG_FILE, json_encode(['email'=>$e, 'password'=>$p], JSON_PRETTY_PRINT));
    echo B_GREEN . "\n✅ Konfigurasi disimpan!\n" . RESET;
    echo B_WHITE . "\nTekan Enter untuk kembali...\n" . RESET;
    fgets(STDIN);
}

// ============================================================
//  MAIN
// ============================================================
printBanner();

if (!file_exists(CONFIG_FILE)) {
    echo B_YELLOW . "  [!] Config belum ada. Silakan isi dulu.\n" . RESET;
    echo B_WHITE . "  Enter untuk lanjut...\n" . RESET;
    fgets(STDIN);
    configEmailPassword();
}

$cfg = json_decode(file_get_contents(CONFIG_FILE), true);
$email = $cfg['email'] ?? '';
$password = $cfg['password'] ?? '';

while (true) {
    printMenu();
    $choice = trim(fgets(STDIN));

    switch ($choice) {
        case '1':
            startFarming($email, $password);
            echo B_WHITE . "\nEnter untuk kembali...\n" . RESET;
            fgets(STDIN);
            break;
        case '2':
            configEmailPassword();
            $cfg = json_decode(file_get_contents(CONFIG_FILE), true);
            $email = $cfg['email'] ?? '';
            $password = $cfg['password'] ?? '';
            break;
        case '0':
            echo B_GREEN . "\nBye.\n" . RESET;
            exit(0);
        default:
            echo B_RED . "\nSalah pilihan.\n" . RESET;
            echo B_WHITE . "Enter...\n" . RESET;
            fgets(STDIN);
    }
}
