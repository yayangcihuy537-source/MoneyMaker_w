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
//  FUNCTION CURL (DENGAN COOKIE)
// ============================================================
function curl($url, $post = 0, $httpheader = 0, $proxy = 0) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 30);
    curl_setopt($ch, CURLOPT_TIMEOUT, 60);
    curl_setopt($ch, CURLOPT_COOKIEFILE, 'cookie.txt');
    curl_setopt($ch, CURLOPT_COOKIEJAR, 'cookie.txt');
    
    if ($post) {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $post);
    }
    if ($httpheader) {
        curl_setopt($ch, CURLOPT_HTTPHEADER, $httpheader);
    }
    if ($proxy) {
        curl_setopt($ch, CURLOPT_HTTPPROXYTUNNEL, true);
        curl_setopt($ch, CURLOPT_PROXY, $proxy);
    }
    curl_setopt($ch, CURLOPT_HEADER, true);
    $response = curl_exec($ch);
    if (!$response) {
        return "Curl Error: " . curl_error($ch);
    }
    $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $header = substr($response, 0, $header_size);
    $body = substr($response, $header_size);
    @curl_close($ch);
    return array($header, $body);
}

// ============================================================
//  FUNCTION CURL REQUEST (TANPA HEADER UNTUK BYPASS)
// ============================================================
function curl_request($url, $method = 'GET', $post = null, $headers = []) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 30);
    curl_setopt($ch, CURLOPT_TIMEOUT, 60);
    if ($headers) curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    if ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $post);
    }
    $response = curl_exec($ch);
    $error = curl_error($ch);
    @curl_close($ch);
    if ($error) return false;
    return $response;
}

// ============================================================
//  DISPLAY BANNER
// ============================================================
function displayBanner($username = '') {
    system('clear');
    $line = str_repeat('═', 56);
    echo B_CYAN . "╔" . $line . "╗" . RESET . "\n";
    echo B_CYAN . "║" . RESET . str_repeat(' ', 8) . B_MAGENTA . ":: ⚡️LightningQuest⚡️ ::" . RESET . str_repeat(' ', 9) . B_CYAN . "║" . RESET . "\n";
    echo B_CYAN . "║" . RESET . str_repeat(' ', 14) . B_RED . "🔥AUTO EARN BOT🔥" . RESET . str_repeat(' ', 15) . B_CYAN . "║" . RESET . "\n";
    echo B_CYAN . "╚" . $line . "╝" . RESET . "\n";
    echo "\n";
    echo B_CYAN . "  [+] Website : " . B_WHITE . "⚡️lightningquest.net ⚡️" . RESET . "\n";
    echo B_CYAN . "  [+] ScriptMaker : " . B_YELLOW . "@SouuXso 🔥" . RESET . "\n";
    echo B_CYAN . "  [+] Bot : " . B_GREEN . "ONLINE 🟢" . RESET . "\n";
    echo B_CYAN . str_repeat('═', 56) . RESET . "\n";
    echo "\n";
    if ($username) {
        echo B_CYAN . "  [+] Welcome, " . B_WHITE . $username . RESET . "\n\n";
    }
}

// ============================================================
//  TIMER
// ============================================================
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
        echo "\r" . B_CYAN . "  ⏳ Cooldown: " . B_WHITE . $time_formatted . " " . $spinner . "   " . RESET;
        sleep(1);
        $wait_time--;
        $current_frame = ($current_frame + 1) % count($frames);
    }
    echo "\r" . str_repeat(" ", 50) . "\r";
}

// ============================================================
//  SAVE DATA
// ============================================================
function Save($namadata) {
    if (file_exists($namadata)) {
        $data = file_get_contents($namadata);
    } else {
        echo B_CYAN . "  [!] " . B_WHITE . "Input " . $namadata . " : " . RESET;
        $data = trim(fgets(STDIN));
        file_put_contents($namadata, $data);
    }
    return $data;
}

// ============================================================
//  GET SITEKEY DARI API CONFIG
// ============================================================
function getSitekeyFromConfig($access_token, $api) {
    $headers = [
        'User-Agent: '.$api,
        'Authorization: Bearer ' . $access_token,
        'x-requested-with: XMLHttpRequest',
        'Content-Type: application/json',
    ];
    list($header, $body) = curl('https://lightningquest.net/api/config', 0, $headers);
    $data = json_decode($body, true);
    
    if (isset($data['hcaptchaSiteKey']) && $data['hcaptchaSiteKey']) {
        return $data['hcaptchaSiteKey'];
    }
    if (isset($data['turnstileSiteKey']) && $data['turnstileSiteKey']) {
        return $data['turnstileSiteKey'];
    }
    return null;
}

// ============================================================
//  GET CSRF 
// ============================================================
function getCSRF() {
    if (file_exists('csrf_cache.txt')) {
        $csrf = trim(file_get_contents('csrf_cache.txt'));
        if (strlen($csrf) > 5) return $csrf;
    }
    
    if (file_exists('cookie.txt')) {
        $cookie = file_get_contents('cookie.txt');
        if (preg_match('/XSRF-TOKEN[=\s]+([^;\s]+)/i', $cookie, $match)) {
            $csrf = urldecode($match[1]);
            if (strlen($csrf) > 5) {
                file_put_contents('csrf_cache.txt', $csrf);
                return $csrf;
            }
        }
        if (preg_match('/csrf_token[=\s]+([^;\s]+)/i', $cookie, $match)) {
            $csrf = urldecode($match[1]);
            if (strlen($csrf) > 5) {
                file_put_contents('csrf_cache.txt', $csrf);
                return $csrf;
            }
        }
    }
    
    $headers = [
        'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        'x-requested-with: XMLHttpRequest',
    ];
    if (file_exists('access_token.txt')) {
        $token = trim(file_get_contents('access_token.txt'));
        $headers[] = 'Authorization: Bearer ' . $token;
    }
    list($header, $html) = curl('https://lightningquest.net/faucet', 0, $headers);
    
    $patterns = [
        '/<meta name="csrf-token" content="([^"]+)"/i',
        '/<meta name="csrf_token" content="([^"]+)"/i',
        '/<input[^>]*name="csrf_token"[^>]*value="([^"]+)"/i',
        '/csrfToken\s*=\s*"([^"]+)"/i',
        '/"csrf_token"\s*:\s*"([^"]+)"/i',
        '/<script[^>]*>.*?csrf_token["\']?\s*[:=]\s*["\']([^"\']+)["\']/si',
    ];
    foreach ($patterns as $pattern) {
        if (preg_match($pattern, $html, $match)) {
            $csrf = $match[1];
            if (strlen($csrf) > 5) {
                file_put_contents('csrf_cache.txt', $csrf);
                return $csrf;
            }
        }
    }
    
    return 'fallback_' . md5(time());
}

// ============================================================
//  BYPASS CAPTCHA
// ============================================================
function bypassCaptcha($sitekey, $method, $pageurl) {
    $apiKey = trim(file_get_contents('bypass_api_key.txt'));
    if (!$apiKey) {
        echo B_RED . "  [!] API Key bypass tidak ditemukan!\n" . RESET;
        return false;
    }
    $url = "https://bypassallshortlinks.space/in.php?key=" . urlencode($apiKey) . "&method=" . urlencode($method) . "&sitekey=" . urlencode($sitekey) . "&pageurl=" . urlencode($pageurl);
    $response = curl_request($url);
    if ($response === false || strpos($response, 'ERROR') !== false) {
        echo B_RED . "  [!] Bypass submit error\n" . RESET;
        return false;
    }
    $parts = explode('|', $response);
    if (count($parts) < 2) {
        echo B_RED . "  [!] Invalid response\n" . RESET;
        return false;
    }
    $taskId = trim($parts[1]);
    echo B_YELLOW . "  [BYPASS] Task ID: " . $taskId . "\n" . RESET;
    for ($i = 0; $i < 30; $i++) {
        sleep(3);
        $resUrl = "https://bypassallshortlinks.space/res.php?key=" . urlencode($apiKey) . "&id=" . urlencode($taskId);
        $result = curl_request($resUrl);
        if ($result === false) continue;
        if (strpos($result, 'OK|') === 0) {
            $token = substr($result, 3);
            echo B_GREEN . "  [BYPASS] Token obtained\n" . RESET;
            return $token;
        }
        if (strpos($result, 'ERROR') !== false) {
            echo B_RED . "  [BYPASS] Error: " . $result . "\n" . RESET;
            return false;
        }
    }
    echo B_RED . "  [BYPASS] Timeout\n" . RESET;
    return false;
}

// ============================================================
//  LOGIN
// ============================================================
if (!file_exists("cookie.txt") || !file_exists("access_token.txt")) {
    login:
    @unlink("cookie.txt");
    @unlink("access_token.txt");
    @unlink("csrf_cache.txt");
    
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://lightningquest.net/api/auth/login',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => '',
        CURLOPT_MAXREDIRS => 10,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
        CURLOPT_CUSTOMREQUEST => 'POST',
        CURLOPT_POSTFIELDS => '{"email":"'.$email.'","password":"'.$pass.'","trafficExchangeBonus":false}',
        CURLOPT_COOKIEJAR => 'cookie.txt',
        CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_HTTPHEADER => [
            'User-Agent: '.$api,
            'sec-ch-ua-platform: "Android"',
            'x-requested-with: XMLHttpRequest',
            'sec-ch-ua: "Chromium";v="146", "Not-A.Brand";v="24", "Android WebView";v="146"',
            'Content-Type: application/json',
            'sec-ch-ua-mobile: ?1',
            'origin: https://lightningquest.net',
            'sec-fetch-site: same-origin',
            'sec-fetch-mode: cors',
            'sec-fetch-dest: empty',
            'referer: https://lightningquest.net/login',
            'accept-language: en-GB,en-US;q=0.9,en;q=0.8',
            'priority: u=1, i',
        ],
    ]);
    $response = curl_exec($curl);
    $data = json_decode($response, true);
    
    if (!empty($data['access_token']) && !empty($data['user']['user_metadata']['username'])) {
        file_put_contents('access_token.txt', $data['access_token']);
        $username = $data['user']['user_metadata']['username'];
        displayBanner($username);
    } else {
        echo B_RED . "  [!] Login Gagal! Cek email/password." . RESET . "\n";
        exit;
    }
} else {
    $username = "LightGarap";
    displayBanner($username);
}

$email = Save("Email");
$pass = Save("Password");
$api = Save("user-agent");
$access_token = trim(file_get_contents('access_token.txt'));

// ============================================================
//  QUESTS
// ============================================================
function doQuests($api, $access_token) {
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://lightningquest.net/api/quests/progress',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_COOKIEJAR => 'cookie.txt',
        CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => [
            'x-requested-with: XMLHttpRequest',
            'User-Agent: '.$api,
            'sec-ch-ua-platform: "Android"',
            'sec-ch-ua: "Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
            'upgrade-insecure-requests: 1',
            'sec-ch-ua-mobile: ?1',
            'sec-fetch-site: same-origin',
            'sec-fetch-mode: navigate',
            'sec-fetch-dest: empty',
            'referer: https://lightningquest.net/quests',
            'accept-language: en-GB,en-US;q=0.9,hi;q=0.7',
            'priority: u=0, i',
            'Authorization: Bearer ' . $access_token,
        ],
    ]);
    $res = curl_exec($curl);
    $data = json_decode($res, true);
    
    if (($data['error'] ?? '') === 'unauthorized') return 'unauthorized';
    
    $claimId = null;
    foreach ($data['progress'] ?? [] as $q) {
        if ($q['complete'] && !$q['claimed']) {
            $claimId = $q['id'];
            break;
        }
    }
    if (!$claimId) {
        echo B_YELLOW . "      ⚠️ No quest to claim." . RESET . "\n";
        return true;
    }
    
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => "https://lightningquest.net/api/quests/$claimId/claim",
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_COOKIEJAR => 'cookie.txt',
        CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_CUSTOMREQUEST => 'POST',
        CURLOPT_HTTPHEADER => [
            'x-requested-with: XMLHttpRequest',
            'User-Agent: '.$api,
            'sec-ch-ua-platform: "Android"',
            'sec-ch-ua: "Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
            'upgrade-insecure-requests: 1',
            'sec-ch-ua-mobile: ?1',
            'sec-fetch-site: same-origin',
            'sec-fetch-mode: navigate',
            'sec-fetch-dest: empty',
            'referer: https://lightningquest.net/quests',
            'accept-language: en-GB,en-US;q=0.9,hi;q=0.7',
            'priority: u=0, i',
            'Authorization: Bearer ' . $access_token,
        ],
    ]);
    $res = curl_exec($curl);
    $data = json_decode($res, true);
    
    if (($data['ok'] ?? false) === true) {
        $coins = $data['reward']['coins'] ?? 0;
        $xp = $data['reward']['xp'] ?? 0;
        echo B_GREEN . "      ✓ Quest claimed! +{$coins} Coins, +{$xp} XP" . RESET . "\n";
        return true;
    }
    echo B_YELLOW . "      ⚠️ No quest to claim." . RESET . "\n";
    return true;
}

// ============================================================
//  DAILY BONUS
// ============================================================
function doDaily($api, $access_token) {
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => "https://lightningquest.net/api/claim/daily",
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_COOKIEJAR => 'cookie.txt',
        CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_CUSTOMREQUEST => 'POST',
        CURLOPT_POSTFIELDS => '{}',
        CURLOPT_HTTPHEADER => [
            'x-requested-with: XMLHttpRequest',
            'User-Agent: '.$api,
            'sec-ch-ua-platform: "Android"',
            'sec-ch-ua: "Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
            'upgrade-insecure-requests: 1',
            'sec-ch-ua-mobile: ?1',
            'sec-fetch-site: same-origin',
            'sec-fetch-mode: navigate',
            'sec-fetch-dest: empty',
            'referer: https://lightningquest.net/daily',
            'accept-language: en-GB,en-US;q=0.9,hi;q=0.7',
            'priority: u=0, i',
            'Authorization: Bearer ' . $access_token,
        ],
    ]);
    $res = curl_exec($curl);
    $data = json_decode($res, true);
    
    if (($data['ok'] ?? false) === true) {
        $coins = $data['reward']['coins'] ?? 0;
        $xp = $data['reward']['xp'] ?? 0;
        echo B_GREEN . "      ✓ Daily bonus claimed! +{$coins} Coins, +{$xp} XP" . RESET . "\n";
        return true;
    }
    echo B_YELLOW . "      ⚠️ Daily bonus already claimed." . RESET . "\n";
    return false;
}

// ============================================================
//  FAUCET (FIXED - PAYLOAD CAPTCHA)
// ============================================================
function doFaucet($api, $access_token, &$reward_info) {
    echo B_CYAN . "  [💧] Faucet" . RESET . "\n";
    echo "      Status      : " . B_YELLOW . "Checking...\n" . RESET;

    // Cek cooldown dulu
    $headers = [
        'x-requested-with: XMLHttpRequest',
        'User-Agent: '.$api,
        'Authorization: Bearer ' . $access_token,
    ];
    list($header, $body) = curl('https://lightningquest.net/api/claim-status', 0, $headers);
    $data0 = json_decode($body, true);
    
    if (isset($data0['error']) && $data0['error'] === 'unauthorized') {
        return 'unauthorized';
    }
    
    if ($data0 && isset($data0['faucet']['ready']) && $data0['faucet']['ready'] === false) {
        $nextAt = strtotime($data0['faucet']['nextAt']);
        $next = max(0, $nextAt - time());
        $min = floor($next / 60);
        $sec = $next % 60;
        echo "      Status      : " . B_YELLOW . "⏳ Cooldown\n" . RESET;
        echo "      Next Claim  : " . B_WHITE . "{$min}m {$sec}s\n" . RESET;
        timer($next);
        return 'cooldown';
    }

    $captchaRequired = $data0['faucet']['captchaRequired'] ?? false;
    $captchaProvider = $data0['faucet']['captchaProvider'] ?? 'hcaptcha';
    
    // Ambil CSRF
    $csrf = getCSRF();
    if (!$csrf || strlen($csrf) < 3) {
        echo "      Status      : " . B_RED . "❌ CSRF token tidak ditemukan\n" . RESET;
        return false;
    }
    
    // GET challenge
    $challengeHeaders = [
        'User-Agent: '.$api,
        'Authorization: Bearer ' . $access_token,
        'Content-Type: application/json',
        'x-requested-with: XMLHttpRequest',
        'referer: https://lightningquest.net/faucet',
        'X-CSRF-TOKEN: ' . $csrf,
    ];
    list($header3, $body3) = curl('https://lightningquest.net/api/faucet/challenge', 0, $challengeHeaders);
    $data3 = json_decode($body3, true);
    
    if (!isset($data3['claimToken'])) {
        echo "      Status      : " . B_RED . "❌ Failed to get claimToken\n" . RESET;
        return false;
    }
    
    $claimToken = $data3['claimToken'];
    $minWaitSeconds = $data3['minWaitSeconds'] ?? 5;
    echo "      ⏳ Waiting   : " . B_WHITE . "{$minWaitSeconds}s\n" . RESET;
    timer($minWaitSeconds);

    // Build payload
    if ($captchaRequired) {
        echo "      Status      : " . B_YELLOW . "Bypassing {$captchaProvider}...\n" . RESET;
        
        // AMBIL SITEKEY
        $sitekey = getSitekeyFromConfig($access_token, $api);
        
        if (!$sitekey) {
            $headers2 = [
                'User-Agent: ' . $api,
                'Authorization: Bearer ' . $access_token,
                'referer: https://lightningquest.net/faucet',
                'X-CSRF-TOKEN: ' . $csrf,
            ];
            list($header2, $html) = curl('https://lightningquest.net/faucet', 0, $headers2);
            
            $patterns = [
                '/data-sitekey="([^"]+)"/i',
                '/data-turnstile-widget="[^"]+"[^>]*data-sitekey="([^"]+)"/i',
                '/hcaptcha-sitekey="([^"]+)"/i',
                '/turnstile-sitekey="([^"]+)"/i',
            ];
            foreach ($patterns as $pattern) {
                if (preg_match($pattern, $html, $match)) {
                    $sitekey = $match[1];
                    break;
                }
            }
        }
        
        if (!$sitekey) {
            echo "      Status      : " . B_RED . "❌ Sitekey not found\n" . RESET;
            return false;
        }
        
        echo B_YELLOW . "  [DEBUG] Sitekey: " . $sitekey . "\n" . RESET;
        
        $token = bypassCaptcha($sitekey, $captchaProvider, 'https://lightningquest.net/faucet');
        if (!$token) {
            echo "      Status      : " . B_RED . "❌ Bypass failed\n" . RESET;
            return false;
        }
        
        // FORMAT PAYLOAD YANG BENAR - SERVER MINTA captchaToken BUKAN captcha_token
        $payload = json_encode([
            'csrf_token' => $csrf,
            'claimToken' => $claimToken,
            'captchaToken' => $token,
            'captchaProvider' => $captchaProvider,
        ]);
    } else {
        echo "      Status      : " . B_GREEN . "No captcha required\n" . RESET;
        $payload = json_encode([
            'csrf_token' => $csrf,
            'claimToken' => $claimToken,
        ]);
    }

    // Claim
    $claimHeaders = [
        'User-Agent: '.$api,
        'Content-Type: application/json',
        'Authorization: Bearer ' . $access_token,
        'X-CSRF-TOKEN: ' . $csrf,
        'x-requested-with: XMLHttpRequest',
        'referer: https://lightningquest.net/faucet',
    ];
    list($header4, $body4) = curl('https://lightningquest.net/api/claim/faucet', $payload, $claimHeaders);
    $data4 = json_decode($body4, true);
    
    if ($data4 && ($data4['ok'] ?? false)) {
        $coins = $data4['reward']['coins'] ?? 0;
        $xp = $data4['reward']['xp'] ?? 0;
        $balance = $data4['reward']['snapshot']['balance'] ?? 0;
        $level = $data4['reward']['snapshot']['level'] ?? 0;
        $multiplier = $data4['reward']['snapshot']['multiplier'] ?? 1;
        $nextAt = strtotime($data4['nextAt'] ?? date('Y-m-d H:i:s', time() + 60));
        $next = max(0, $nextAt - time());
        $min = floor($next / 60);
        $sec = $next % 60;

        $reward_info = [
            'coins' => $coins,
            'xp' => $xp,
            'balance' => number_format($balance, 0, '.', ','),
            'level' => $level,
            'multiplier' => $multiplier,
            'next_min' => $min,
            'next_sec' => $sec
        ];

        echo "      ✓ " . B_GREEN . "Claim Successful!\n" . RESET;
        return true;
    } else {
        $errorMsg = $data4['message'] ?? 'Unknown error';
        echo "      Status      : " . B_RED . "❌ Claim failed: $errorMsg\n" . RESET;
        return false;
    }
}

// ============================================================
//  MAIN LOOP
// ============================================================
if (!file_exists('bypass_api_key.txt')) {
    echo B_CYAN . "  [!] Masukkan API Key bypass (dari bypassallshortlinks.space): " . RESET;
    $key = trim(fgets(STDIN));
    file_put_contents('bypass_api_key.txt', $key);
}

$email = Save("Email");
$pass = Save("Password");
$api = Save("user-agent");

echo B_YELLOW . "  🔄 Starting auto loop...\n\n" . RESET;

$fail_count = 0;
$loop_count = 0;

while (true) {
    $loop_count++;
    echo B_CYAN . "  ===== Loop #{$loop_count} ===== " . RESET . "\n\n";
    
    // 1. QUESTS
    echo B_CYAN . "  [📋] Quest" . RESET . "\n";
    $quest_result = doQuests($api, $access_token);
    if ($quest_result === 'unauthorized') {
        echo B_RED . "  [!] Session expired. Re-login..." . RESET . "\n";
        unlink('access_token.txt');
        unlink('cookie.txt');
        unlink('csrf_cache.txt');
        goto login;
    }
    echo "\n";
    
    // 2. DAILY BONUS
    echo B_CYAN . "  [🎁] Daily" . RESET . "\n";
    $daily_result = doDaily($api, $access_token);
    echo "\n";
    
    // 3. FAUCET
    $reward_info = [];
    $faucet_result = doFaucet($api, $access_token, $reward_info);
    
    if ($faucet_result === 'unauthorized') {
        echo B_RED . "  [!] Session expired. Re-login..." . RESET . "\n";
        unlink('access_token.txt');
        unlink('cookie.txt');
        unlink('csrf_cache.txt');
        goto login;
    }
    
    if ($faucet_result === true && !empty($reward_info)) {
        echo "\n" . B_CYAN . "  ==================== REWARD ====================" . RESET . "\n\n";
        echo B_WHITE . "      [+] Coins      : " . B_GREEN . "+" . $reward_info['coins'] . "⚡️" . RESET . "\n";
        echo B_WHITE . "      [+] XP         : " . B_GREEN . "+" . $reward_info['xp'] . "⭐️" . RESET . "\n";
        echo B_WHITE . "      [+] Balance    : " . B_YELLOW . $reward_info['balance'] . "⚡️" . RESET . "\n";
        echo B_WHITE . "      [+] Level      : " . B_MAGENTA . $reward_info['level'] . "📍" . RESET . "\n";
        echo B_WHITE . "      [+] Multiplier : " . B_CYAN . "x" . $reward_info['multiplier'] . "🥇" . RESET . "\n";
        echo B_WHITE . "      [+] Next Claim : " . B_YELLOW . $reward_info['next_min'] . "m " . sprintf("%02d", $reward_info['next_sec']) . "s" . RESET . "\n";
        echo B_CYAN . "\n  ================================================" . RESET . "\n";
    }
    
    if ($faucet_result === 'cooldown') {
        // Timer already handled
    }
    
    if ($faucet_result === false) {
        $fail_count++;
        if ($fail_count >= 5) {
            echo B_RED . "  [!] Too many failures. Waiting 60s..." . RESET . "\n";
            timer(60);
            $fail_count = 0;
        }
        timer(10);
    } else {
        $fail_count = 0;
    }
    
    echo "\n" . B_CYAN . "  🔄 Preparing next loop..." . RESET . "\n\n";
    sleep(5);
}
