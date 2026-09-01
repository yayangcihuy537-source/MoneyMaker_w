<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');

// ============================================================
//  COLOR CONSTANTS
// ============================================================
define('RESET', "\033[0m");
define('BOLD', "\033[1m");
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
define('B_BLUE', "\033[1;34m");
define('B_CYAN', "\033[1;36m");
define('B_WHITE', "\033[1;37m");
define('B_MAGENTA', "\033[1;35m");

// ============================================================
//  CONFIG
// ============================================================
const HOST = 'https://claimx.online';
const MAX_DAILY_CLAIMS = 100;
const CONFIG_FILE = 'claimx_config.json';
const COOKIE_FILE = 'claimx_cookie.txt';
const DAILY_FILE = 'claimx_daily.txt';

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
    echo B_CYAN . "  Limit  : " . WHITE . MAX_DAILY_CLAIMS . " claim/hari (free member)\n";
    echo B_CYAN . "  Jeda   : " . WHITE . "14-19 detik (human-like) untuk faucet biasa\n";
    echo B_CYAN . "  Pop    : " . WHITE . "Tanpa jeda (langsung)\n";
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
//  DAILY COUNTER
// ============================================================
function getDailyCount() {
    $today = date('Y-m-d');
    if (file_exists(DAILY_FILE)) {
        $data = json_decode(file_get_contents(DAILY_FILE), true);
        if ($data['date'] == $today) {
            return $data['count'];
        }
    }
    return 0;
}

function updateDailyCount($count) {
    $today = date('Y-m-d');
    file_put_contents(DAILY_FILE, json_encode(['date' => $today, 'count' => $count]));
}

function resetDailyIfNeeded() {
    $today = date('Y-m-d');
    if (file_exists(DAILY_FILE)) {
        $data = json_decode(file_get_contents(DAILY_FILE), true);
        if ($data['date'] != $today) {
            updateDailyCount(0);
            return true;
        }
    }
    return false;
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
    
    $patterns = [
        '/<div[^>]*class="[^"]*bg-dark[^"]*border-warning[^"]*"[^>]*>.*?<i[^>]*class="([^"]+)"[^>]*><\/i>/si',
        '/<div[^>]*class="[^"]*d-inline-flex[^"]*"[^>]*>.*?<i[^>]*class="([^"]+)"[^>]*><\/i>/si',
        '/<div[^>]*class="[^"]*text-warning[^"]*"[^>]*>.*?<i[^>]*class="([^"]+)"[^>]*><\/i>/si',
    ];
    foreach ($patterns as $p) {
        if (preg_match($p, $html, $m)) {
            $targetIcon = $m[1];
            break;
        }
    }

    $choices = [];
    if (preg_match_all('/<button[^>]*data-key="([^"]+)"[^>]*>.*?<i[^>]*class="([^"]+)"[^>]*><\/i>.*?<\/button>/si', $html, $matches, PREG_SET_ORDER)) {
        foreach ($matches as $m) {
            $choices[] = ['key' => $m[1], 'icon' => $m[2]];
        }
    }
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
//  GET BALANCE
// ============================================================
function getBalance() {
    $html = httpRequest(HOST . '/dashboard');
    if (!$html) return '0.00000000';
    
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
//  CHECK DAILY LIMIT DARI HTML
// ============================================================
function checkDailyLimit($html) {
    if (strpos($html, 'Daily Limit Reached') !== false || 
        strpos($html, 'You have completed all') !== false ||
        strpos($html, 'Upgrade Membership') !== false) {
        return true;
    }
    return false;
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
        echo B_RED . "  [ERROR] Captcha tidak ditemukan.\n" . RESET;
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
//  CLAIM FAUCET BIASA
// ============================================================
function claimFaucet(&$rewardInfo, $retry = 0) {
    if ($retry > 3) {
        echo B_RED . "  [ERROR] Gagal setelah 3 percobaan.\n" . RESET;
        return false;
    }
    
    $html = httpRequest(HOST . '/faucet');
    if (!$html) {
        echo B_RED . "  [ERROR] Gagal mengakses faucet.\n" . RESET;
        return false;
    }

    if (checkDailyLimit($html)) {
        echo B_RED . "  [LIMIT] Daily limit reached (100 claims). Bot berhenti.\n" . RESET;
        return 'limit_reached';
    }

    if (preg_match('/id="countdownClock"[^>]*data-seconds="(\d+)"/i', $html, $m)) {
        $seconds = (int)$m[1];
        if ($seconds > 0) {
            echo B_YELLOW . "  [COOLDOWN] " . $seconds . "s tersisa.\n" . RESET;
            timer($seconds);
            return 'cooldown';
        }
    }

    if (strpos($html, 'faucetForm') === false) {
        echo B_YELLOW . "  [INFO] Form claim tidak ditemukan.\n" . RESET;
        return 'no_form';
    }

    $csrf = parseCSRF($html);
    if (!$csrf) {
        echo B_YELLOW . "  [INFO] CSRF tidak ditemukan, refresh...\n" . RESET;
        sleep(2);
        return claimFaucet($rewardInfo, $retry + 1);
    }

    list($targetIcon, $choices) = parseIconCaptcha($html);
    
    if (!$targetIcon || empty($choices)) {
        echo B_YELLOW . "  [INFO] Tidak ada captcha, claim langsung...\n" . RESET;
        $postData = http_build_query(['csrf_token' => $csrf]);
    } else {
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

    if (checkDailyLimit($response)) {
        echo B_RED . "  [LIMIT] Daily limit reached. Bot berhenti.\n" . RESET;
        return 'limit_reached';
    }

    if (preg_match('/alert-success[^>]*>Claim successful! Received \+([0-9.]+) USDT\./i', $response, $m)) {
        echo B_GREEN . "  [SUCCESS] +{$m[1]} USDT\n" . RESET;
        $rewardInfo = ['amount' => $m[1]];
        return true;
    } else {
        if (strlen($response) < 100) {
            echo B_YELLOW . "  [INFO] Response pendek, retry...\n" . RESET;
            sleep(2);
            return claimFaucet($rewardInfo, $retry + 1);
        }
        echo B_RED . "  [ERROR] Claim gagal.\n" . RESET;
        return false;
    }
}

// ============================================================
//  CLAIM POP-UNDER FAUCET (UNLIMITED)
// ============================================================
function claimPopFaucet(&$rewardInfo, $retry = 0) {
    if ($retry > 3) {
        echo B_RED . "  [ERROR] Gagal setelah 3 percobaan.\n" . RESET;
        return false;
    }
    
    $html = httpRequest(HOST . '/pop-faucet');
    if (!$html) {
        echo B_RED . "  [ERROR] Gagal mengakses pop faucet.\n" . RESET;
        return false;
    }

    if (preg_match('/Cooldown Timer.*?<h4[^>]*>([0-9.]+)\s*Minutes?/i', $html, $m)) {
        $minutes = (float)$m[1];
        if ($minutes > 0) {
            $seconds = ceil($minutes * 60);
            echo B_YELLOW . "  [COOLDOWN] " . $seconds . "s tersisa.\n" . RESET;
            timer($seconds);
            return 'cooldown';
        }
    }

    if (strpos($html, 'Pop-Under Faucet claim successful!') !== false) {
        echo B_YELLOW . "  [INFO] Pop claim sudah berhasil sebelumnya.\n" . RESET;
        if (preg_match('/Received \+([0-9.]+) USDT\./i', $html, $m)) {
            $rewardInfo = ['amount' => $m[1]];
            return true;
        }
        return true;
    }

    $csrf = parseCSRF($html);
    if (!$csrf) {
        echo B_YELLOW . "  [INFO] CSRF tidak ditemukan, refresh...\n" . RESET;
        sleep(2);
        return claimPopFaucet($rewardInfo, $retry + 1);
    }

    list($targetIcon, $choices) = parseIconCaptcha($html);
    
    if (!$targetIcon || empty($choices)) {
        echo B_YELLOW . "  [INFO] Tidak ada captcha, claim langsung...\n" . RESET;
        $postData = http_build_query(['csrf_token' => $csrf]);
    } else {
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
    
    $extraHeaders = [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: ' . HOST,
        'Referer: ' . HOST . '/pop-faucet',
    ];
    $response = httpRequest(HOST . '/pop-faucet/claim', 'POST', $postData, $extraHeaders);
    if ($response === false) {
        echo B_RED . "  [ERROR] Claim request gagal.\n" . RESET;
        return false;
    }

    if (preg_match('/Pop-Under Faucet claim successful! Received \+([0-9.]+) USDT\./i', $response, $m)) {
        echo B_GREEN . "  [SUCCESS] +{$m[1]} USDT (Pop)\n" . RESET;
        $rewardInfo = ['amount' => $m[1]];
        return true;
    } else {
        if (strlen($response) < 100) {
            echo B_YELLOW . "  [INFO] Response pendek, retry...\n" . RESET;
            sleep(2);
            return claimPopFaucet($rewardInfo, $retry + 1);
        }
        echo B_RED . "  [ERROR] Claim pop gagal.\n" . RESET;
        return false;
    }
}

// ============================================================
//  FUNGSI FARMING (POP TANPA DELAY)
// ============================================================
function startFarming($email, $password, $mode) {
    if (!doLogin($email, $password)) {
        echo B_RED . "  [ERROR] Login gagal. Keluar.\n" . RESET;
        return;
    }

    $balance = getBalance();
    $dailyCount = getDailyCount();
    echo B_CYAN . "  [BALANCE] " . B_WHITE . $balance . " USDT\n" . RESET;
    echo B_CYAN . "  [DAILY] " . B_WHITE . $dailyCount . " / " . MAX_DAILY_CLAIMS . " claims\n" . RESET;

    $startTime = time();
    $claims = 0;
    $failures = 0;
    $maxFailures = 10;
    $popClaims = 0;

    echo B_CYAN . "  [START] Bot dimulai...\n\n" . RESET;

    while (true) {
        if (resetDailyIfNeeded()) {
            $dailyCount = 0;
            echo B_CYAN . "  [DAILY] Reset counter harian.\n" . RESET;
        }

        $html = httpRequest(HOST . '/dashboard');
        if (!$html || strpos($html, 'Welcome back') === false) {
            echo B_YELLOW . "  [INFO] Session expired, login ulang...\n" . RESET;
            if (!doLogin($email, $password)) {
                echo B_RED . "  [ERROR] Login ulang gagal.\n" . RESET;
                break;
            }
            $balance = getBalance();
            continue;
        }

        // ===== MODE 1: FAUCET BIASA =====
        if ($mode == 1 || $mode == 3) {
            if ($dailyCount >= MAX_DAILY_CLAIMS) {
                echo B_RED . "  [LIMIT] Sudah mencapai " . MAX_DAILY_CLAIMS . " claim hari ini.\n" . RESET;
                if ($mode == 3) {
                    echo B_YELLOW . "  [INFO] Lanjut ke Pop Faucet...\n" . RESET;
                } else {
                    echo B_YELLOW . "  [WAIT] Tunggu hingga tengah malam untuk reset.\n" . RESET;
                    $tomorrow = strtotime('tomorrow 00:00:00');
                    $wait = $tomorrow - time();
                    echo B_YELLOW . "  [WAIT] " . gmdate("H:i:s", $wait) . " tersisa.\n" . RESET;
                    timer($wait);
                    continue;
                }
            } else {
                $rewardInfo = [];
                $result = claimFaucet($rewardInfo);
                if ($result === 'limit_reached') {
                    echo B_RED . "  [STOP] Limit harian tercapai.\n" . RESET;
                    if ($mode == 3) {
                        // lanjut ke pop
                    } else {
                        break;
                    }
                } elseif ($result === 'cooldown' || $result === 'no_form') {
                    $delay = rand(14, 19);
                    echo B_YELLOW . "  ⏳ Human delay: {$delay}s\n" . RESET;
                    sleep($delay);
                    continue;
                } elseif ($result === true) {
                    $claims++;
                    $dailyCount++;
                    updateDailyCount($dailyCount);
                    $failures = 0;
                    $balance = getBalance();
                    echo B_CYAN . "  [BALANCE] " . B_WHITE . $balance . " USDT\n" . RESET;
                    echo B_CYAN . "  [DAILY] " . B_WHITE . $dailyCount . " / " . MAX_DAILY_CLAIMS . " claims\n" . RESET;
                    echo B_GREEN . "  [TOTAL] Claims: {$claims}\n" . RESET;
                } else {
                    $failures++;
                    echo B_RED . "  [FAIL] ({$failures}/{$maxFailures})\n" . RESET;
                    if ($failures >= $maxFailures) {
                        echo B_RED . "  [STOP] Terlalu banyak gagal.\n" . RESET;
                        break;
                    }
                }
                if ($result !== 'cooldown' && $result !== 'no_form') {
                    $delay = rand(14, 19);
                    echo B_YELLOW . "  ⏳ Human delay: {$delay}s\n" . RESET;
                    sleep($delay);
                }
            }
        }

        // ===== MODE 2: POP-UNDER FAUCET (UNLIMITED) - TANPA DELAY =====
        if ($mode == 2 || $mode == 3) {
            $rewardInfoPop = [];
            $resultPop = claimPopFaucet($rewardInfoPop);
            if ($resultPop === 'cooldown') {
                // timer sudah di handle di dalam function
                continue;
            } elseif ($resultPop === true) {
                $popClaims++;
                $failures = 0;
                $balance = getBalance();
                echo B_CYAN . "  [BALANCE] " . B_WHITE . $balance . " USDT\n" . RESET;
                echo B_CYAN . "  [POP CLAIMS] " . B_WHITE . $popClaims . "\n" . RESET;
            } else {
                $failures++;
                echo B_RED . "  [FAIL] Pop ({$failures}/{$maxFailures})\n" . RESET;
                if ($failures >= $maxFailures) {
                    echo B_RED . "  [STOP] Terlalu banyak gagal.\n" . RESET;
                    break;
                }
            }
            // TIDAK ADA DELAY UNTUK POP
        }

        if ($mode == 1 && $dailyCount >= MAX_DAILY_CLAIMS) {
            echo B_GREEN . "  [DONE] " . MAX_DAILY_CLAIMS . " claims selesai.\n" . RESET;
            break;
        }
    }

    $balance = getBalance();
    echo B_CYAN . "\n  [FINAL BALANCE] " . B_WHITE . $balance . " USDT\n" . RESET;
    echo B_CYAN . "  Total claims (biasa): " . B_WHITE . $claims . "\n" . RESET;
    echo B_CYAN . "  Pop claims: " . B_WHITE . $popClaims . "\n" . RESET;
}

// ============================================================
//  MENU
// ============================================================
function printMenu() {
    clearScreen();
    echo B_CYAN . "==================================================\n";
    echo B_CYAN . "  " . B_WHITE . "ClaimX Auto Claim Bot" . B_CYAN . "  \n";
    echo B_CYAN . "==================================================\n";
    echo B_CYAN . "  [1] " . B_GREEN . "Claim Faucet (100 limit/hari)\n";
    echo B_CYAN . "  [2] " . B_GREEN . "Unlimited Pop-Under Faucet (tanpa delay)\n";
    echo B_CYAN . "  [3] " . B_GREEN . "All (Faucet + Pop)\n";
    echo B_CYAN . "  [4] " . B_YELLOW . "Config Email & Password\n";
    echo B_CYAN . "  [0] " . B_RED . "Exit\n";
    echo B_CYAN . "==================================================\n";
    echo B_WHITE . "  Pilih menu: " . RESET;
}

function configEmailPassword() {
    clearScreen();
    echo B_CYAN . "==================================================\n";
    echo B_CYAN . "  " . B_WHITE . "Konfigurasi Akun\n";
    echo B_CYAN . "==================================================\n\n";
    
    echo B_WHITE . "Email: " . RESET;
    $email = trim(fgets(STDIN));
    echo B_WHITE . "Password: " . RESET;
    $password = trim(fgets(STDIN));
    
    file_put_contents(CONFIG_FILE, json_encode(['email' => $email, 'password' => $password], JSON_PRETTY_PRINT));
    echo B_GREEN . "\n✅ Konfigurasi disimpan!\n" . RESET;
    echo B_WHITE . "\nTekan Enter untuk kembali...\n" . RESET;
    fgets(STDIN);
}

// ============================================================
//  MAIN
// ============================================================
printBanner();

if (!file_exists(CONFIG_FILE)) {
    echo B_YELLOW . "  [!] Konfigurasi belum ada. Silakan atur Email & Password.\n" . RESET;
    configEmailPassword();
}

$config = json_decode(file_get_contents(CONFIG_FILE), true);
$email = $config['email'];
$password = $config['password'];

while (true) {
    printMenu();
    $choice = trim(fgets(STDIN));
    
    switch ($choice) {
        case '1':
            startFarming($email, $password, 1);
            echo B_WHITE . "\nTekan Enter untuk kembali ke menu...\n" . RESET;
            fgets(STDIN);
            break;
        case '2':
            startFarming($email, $password, 2);
            echo B_WHITE . "\nTekan Enter untuk kembali ke menu...\n" . RESET;
            fgets(STDIN);
            break;
        case '3':
            startFarming($email, $password, 3);
            echo B_WHITE . "\nTekan Enter untuk kembali ke menu...\n" . RESET;
            fgets(STDIN);
            break;
        case '4':
            configEmailPassword();
            $config = json_decode(file_get_contents(CONFIG_FILE), true);
            $email = $config['email'];
            $password = $config['password'];
            break;
        case '0':
            echo B_GREEN . "\nTerima kasih! Sampai jumpa.\n" . RESET;
            exit(0);
        default:
            echo B_RED . "\nPilihan tidak valid!\n" . RESET;
            echo B_WHITE . "Tekan Enter untuk melanjutkan...\n" . RESET;
            fgets(STDIN);
    }
}
