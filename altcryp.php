<?php
// ============================================================
// ALTCRYP AUTO BOT - PHP (Cookie Only) - FIX V6
// Stop otomatis setelah 2x claim gagal berturut-turut
// ============================================================

error_reporting(E_ALL);
date_default_timezone_set('Asia/Jakarta');

define('MERAH', "\033[0;31m");
define('HIJAU', "\033[0;32m");
define('KUNING', "\033[0;33m");
define('CYAN', "\033[0;36m");
define('PUTIH', "\033[0;37m");
define('RESET', "\033[0m");
define('BOLD', "\033[1m");
define('DIM', "\033[2m");

define('BASE_URL', 'https://altcryp.com');
define('SOLVER_BASE', 'https://bypassallshortlinks.space');
define('CONFIG_FILE', 'config_altcryp.json');
define('CLAIM_INTERVAL', 300);  // default 5 menit
define('RETRY_INTERVAL', 60);
define('MAX_FAILURES', 2);      // <-- batas gagal sebelum stop

class CookieJar {
    private $cookies = [];
    
    public function set($name, $value) {
        $this->cookies[$name] = $value;
    }
    
    public function get($name) {
        return isset($this->cookies[$name]) ? $this->cookies[$name] : null;
    }
    
    public function getAll() {
        return $this->cookies;
    }
    
    public function parseSetCookie($header) {
        preg_match_all('/Set-Cookie:\s*([^;]+)/i', $header, $matches);
        if (!empty($matches[1])) {
            foreach ($matches[1] as $cookie_line) {
                $parts = explode('=', $cookie_line, 2);
                if (count($parts) == 2) {
                    $name = trim($parts[0]);
                    $value = trim($parts[1]);
                    if ($value === 'deleted' || strpos($cookie_line, 'expires=') !== false && strtotime(explode('expires=', $cookie_line)[1]) < time()) {
                        unset($this->cookies[$name]);
                    } else {
                        $this->cookies[$name] = $value;
                    }
                }
            }
        }
    }
    
    public function toString() {
        $str = '';
        foreach ($this->cookies as $k => $v) {
            $str .= "$k=$v; ";
        }
        return rtrim($str, '; ');
    }
    
    public function fromString($str) {
        if (empty($str)) return;
        $pairs = explode(';', $str);
        foreach ($pairs as $pair) {
            $parts = explode('=', trim($pair), 2);
            if (count($parts) == 2) {
                $this->cookies[$parts[0]] = $parts[1];
            }
        }
    }
}

function clear() { system('clear'); }

function timer($seconds, $prefix = "[!] Tunggu") {
    $wait = (int)$seconds;
    $frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'];
    $current = 0;
    while ($wait > 0) {
        $start = microtime(true);
        while ((microtime(true) - $start) < 1) {
            $hours = floor($wait / 3600);
            $minutes = floor(($wait % 3600) / 60);
            $secs = $wait % 60;
            $time_str = sprintf('%02d:%02d:%02d', $hours, $minutes, $secs);
            $spinner = $frames[$current];
            echo PUTIH . $prefix . HIJAU . " $time_str " . PUTIH . $spinner . "\r";
            usleep(100000);
            $current = ($current + 1) % count($frames);
            if ((microtime(true) - $start) >= 1) break;
        }
        $wait--;
    }
    echo str_repeat(" ", 50) . "\r";
}

function get_config() {
    return file_exists(CONFIG_FILE) ? json_decode(file_get_contents(CONFIG_FILE), true) : null;
}

function save_config($config) {
    file_put_contents(CONFIG_FILE, json_encode($config, JSON_PRETTY_PRINT));
}

function get_cookie_from_user() {
    echo PUTIH . "Cookie (copy dari browser, format: key1=value1; key2=value2): " . KUNING;
    $cookie = trim(fgets(STDIN));
    return $cookie;
}

function get_apikey_from_user() {
    echo PUTIH . "API Key bypassallshortlinks: " . KUNING;
    $apikey = trim(fgets(STDIN));
    return $apikey;
}

function http_request($url, $method = 'GET', $data = [], $headers = [], CookieJar &$jar = null) {
    if ($jar === null) {
        $jar = new CookieJar();
    }
    
    $ch = curl_init();
    $options = [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_MAXREDIRS => 10,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_CONNECTTIMEOUT => 30,
        CURLOPT_USERAGENT => 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        CURLOPT_HTTPHEADER => [
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language: id-ID,en;q=0.9',
            'Cache-Control: max-age=0',
            'Upgrade-Insecure-Requests: 1',
        ],
    ];
    
    $cookie_str = $jar->toString();
    if (!empty($cookie_str)) {
        $options[CURLOPT_COOKIE] = $cookie_str;
    }
    
    if (strtoupper($method) === 'POST') {
        $options[CURLOPT_POST] = true;
        $options[CURLOPT_POSTFIELDS] = http_build_query($data);
    }
    
    if (!empty($headers)) {
        $options[CURLOPT_HTTPHEADER] = array_merge($options[CURLOPT_HTTPHEADER], $headers);
    }
    
    curl_setopt_array($ch, $options);
    $response = curl_exec($ch);
    
    if ($response === false) {
        echo MERAH . "[!] cURL error: " . curl_error($ch) . RESET . "\n";
        return null;
    }
    
    $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $body = substr($response, $header_size);
    $header = substr($response, 0, $header_size);
    
    $jar->parseSetCookie($header);
    
    return $body;
}

function solve_turnstile($sitekey, $pageurl, $apikey, $show_progress = false) {
    $url = SOLVER_BASE . "/in.php?key=" . urlencode($apikey) . 
           "&method=turnstile&sitekey=" . urlencode($sitekey) . 
           "&pageurl=" . urlencode($pageurl);
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0');
    $result = curl_exec($ch);
    if (!$result || !str_starts_with($result, 'OK|')) {
        echo MERAH . "[!] Gagal submit Turnstile: $result" . RESET . "\n";
        return null;
    }
    
    $task_id = explode('|', $result)[1];
    if ($show_progress) {
        echo KUNING . "[+] Task ID    : $task_id" . RESET . "\n";
        echo CYAN . "[*] Menunggu Turnstile..." . RESET . "\n";
    }
    
    for ($i = 0; $i < 45; $i++) {
        sleep(2);
        $poll_url = SOLVER_BASE . "/res.php?id=" . urlencode($task_id) . "&key=" . urlencode($apikey);
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $poll_url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        $result = curl_exec($ch);
        if ($result && str_starts_with($result, 'OK|')) {
            $token = explode('|', $result)[1];
            if ($show_progress) {
                echo HIJAU . "[+] Turnstile  : SOLVED ✓" . RESET . "\n";
            }
            return $token;
        }
        if ($show_progress && $i % 5 == 0) {
            echo DIM . "[*] Polling ke- " . ($i+1) . "/45..." . RESET . "\n";
        }
    }
    echo MERAH . "[!] Turnstile timeout." . RESET . "\n";
    return null;
}

function is_logged_in($jar) {
    $urls = [
        BASE_URL . '/dashboard',
        BASE_URL . '/faucet/currency/pol',
    ];
    
    foreach ($urls as $url) {
        $resp = http_request($url, 'GET', [], [], $jar);
        if (!$resp) continue;
        
        $debug_file = 'debug_' . md5($url) . '.html';
        file_put_contents($debug_file, $resp);
        
        if (strpos($resp, 'Logout') !== false || strpos($resp, 'Account') !== false || strpos($resp, 'Withdraw') !== false) {
            return true;
        }
        if (strpos($resp, 'csrf_token_name') !== false && strpos($resp, 'token') !== false) {
            return true;
        }
        if (strlen($resp) < 1000 && (strpos($resp, 'login') !== false || strpos($resp, 'Sign in') !== false)) {
            echo MERAH . "[!] Detected login page from $url" . RESET . "\n";
            return false;
        }
    }
    return false;
}

function get_coins($jar) {
    $html = http_request(BASE_URL, 'GET', [], [], $jar);
    if (!$html) return [];
    preg_match_all('/\/faucet\/currency\/([a-z]+)/', $html, $matches);
    if (!empty($matches[1])) {
        return array_values(array_unique($matches[1]));
    }
    return [];
}

function get_csrf_and_token($jar, $coin) {
    $url = BASE_URL . "/faucet/currency/$coin";
    $headers = ['Referer: ' . BASE_URL];
    $html = http_request($url, 'GET', [], $headers, $jar);
    if (!$html) return ['status' => 'error', 'msg' => 'No response'];
    
    file_put_contents('debug_faucet_' . $coin . '.html', $html);
    
    if (strpos($html, 'Login') !== false && strlen($html) < 500) {
        return ['status' => 'expired'];
    }
    if (strpos($html, 'csrf_token_name') === false || strpos($html, 'token') === false) {
        echo KUNING . "[!] CSRF/Token tidak ditemukan. Cuplikan HTML:\n" . RESET;
        echo substr($html, 0, 500) . "...\n";
        return ['status' => 'error', 'msg' => 'Missing CSRF/Token'];
    }
    
    // ===== REGEX YANG DIPERBAIKI =====
    if (preg_match('/name="csrf_token_name"[^>]*value="([^"]+)"/', $html, $m)) {
        $csrf = $m[1];
    } else {
        if (preg_match('/csrf_token_name"\s*value="([^"]+)"/', $html, $m)) {
            $csrf = $m[1];
        }
    }
    
    if (preg_match('/name="token"[^>]*value="([^"]+)"/', $html, $m)) {
        $token = $m[1];
    } else {
        if (preg_match('/token"\s*value="([^"]+)"/', $html, $m)) {
            $token = $m[1];
        }
    }
    
    if (empty($csrf) || empty($token)) {
        echo KUNING . "[!] CSRF atau Token kosong. Cek debug_faucet_$coin.html" . RESET . "\n";
        return ['status' => 'error', 'msg' => 'Missing CSRF/Token'];
    }
    
    return ['status' => 'ok', 'csrf' => $csrf, 'token' => $token];
}

function claim_faucet($jar, $coin, $apikey) {
    echo CYAN . "[*] Claim      : PROCESSING... (coin: " . strtoupper($coin) . ")" . RESET . "\n";
    
    $data = get_csrf_and_token($jar, $coin);
    if ($data['status'] === 'expired') {
        echo MERAH . "[!] Session expired atau cookie ga valid." . RESET . "\n";
        return 'EXPIRED';
    }
    if ($data['status'] !== 'ok') {
        echo MERAH . "[!] Gagal ambil CSRF/Token: " . $data['msg'] . RESET . "\n";
        return false;
    }
    
    $csrf = $data['csrf'];
    $token = $data['token'];
    echo KUNING . "[+] CSRF Token : $csrf" . RESET . "\n";
    echo KUNING . "[+] Token      : $token" . RESET . "\n";
    
    $sitekey = "0x4AAAAAAAHPLPJjjJUpAitl";
    $pageurl = BASE_URL . "/faucet/currency/$coin";
    $turnstile = solve_turnstile($sitekey, $pageurl, $apikey, true);
    if (!$turnstile) return false;
    
    $post_data = [
        'username_fake_field' => '',
        'csrf_token_name' => $csrf,
        'token' => $token,
        'captcha' => 'turnstile',
        'cf-turnstile-response' => $turnstile
    ];
    
    $url_verify = BASE_URL . "/faucet/verify/$coin";
    $result = http_request($url_verify, 'POST', $post_data, [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: ' . BASE_URL,
        'Referer: ' . BASE_URL . "/faucet/currency/$coin",
    ], $jar);
    
    if (!$result) {
        echo MERAH . "[!] Claim gagal (ga ada respon)." . RESET . "\n";
        return false;
    }
    
    if (strpos($result, 'login') !== false && strlen($result) < 500) {
        echo MERAH . "[!] Session expired setelah claim." . RESET . "\n";
        return 'EXPIRED';
    }
    
    if (strpos($result, 'Good job') !== false || strpos($result, 'success') !== false) {
        echo HIJAU . "[+] Claim      : SUCCESS ✓" . RESET . "\n";
        if (preg_match('/([\d.]+)\s+(\w+)/', $result, $reward)) {
            echo KUNING . "[+] Reward     : " . $reward[1] . " " . $reward[2] . RESET . "\n";
        }
        return true;
    }
    
    if (strpos($result, 'already claimed') !== false || strpos($result, 'wait') !== false) {
        echo KUNING . "[!] Claim      : COOLDOWN ⏳" . RESET . "\n";
        return false;
    }
    
    echo MERAH . "[?] Claim ga jelas." . RESET . "\n";
    file_put_contents('claim_debug_altcryp.html', $result);
    return false;
}

// ========== MAIN ==========
clear();

echo CYAN . "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" . RESET . "\n";
echo BOLD . KUNING . "              🚀 ALTCRYP AUTO BOT (PHP) - FIX V6" . RESET . "\n";
echo CYAN . "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" . RESET . "\n";
echo KUNING . "[!] Bot akan berhenti otomatis setelah 2x gagal berturut-turut." . RESET . "\n";

$config = get_config();
if (!$config) {
    echo KUNING . "[*] Config ga ketemu. Bikin baru..." . RESET . "\n";
    $cookie = get_cookie_from_user();
    $apikey = get_apikey_from_user();
    $config = ['cookie' => $cookie, 'apikey' => $apikey];
    save_config($config);
    echo HIJAU . "[+] Config disimpan di " . CONFIG_FILE . RESET . "\n";
    sleep(1);
}

$cookie = $config['cookie'] ?? '';
$apikey = $config['apikey'] ?? '';

if (empty($apikey)) {
    echo KUNING . "[*] API Key ga ada. Masukin API Key: " . RESET;
    $apikey = get_apikey_from_user();
    $config['apikey'] = $apikey;
    save_config($config);
}

while (true) {
    if (empty($cookie)) {
        echo KUNING . "[*] Cookie kosong. Masukin cookie baru:" . RESET . "\n";
        $cookie = get_cookie_from_user();
        $config['cookie'] = $cookie;
        save_config($config);
    }
    
    $jar = new CookieJar();
    $jar->fromString($cookie);
    
    echo CYAN . "[*] Validasi cookie..." . RESET . "\n";
    
    if (!$jar->get('captcha')) {
        echo KUNING . "[!] Cookie 'captcha' tidak ditemukan. Ini penting!" . RESET . "\n";
        echo KUNING . "[*] Pastikan cookie dari browser sudah include 'captcha=adslab'" . RESET . "\n";
    }
    
    if (is_logged_in($jar)) {
        echo HIJAU . "[+] Cookie valid." . RESET . "\n";
        $updated_cookie = $jar->toString();
        if ($updated_cookie !== $config['cookie']) {
            $config['cookie'] = $updated_cookie;
            save_config($config);
            echo CYAN . "[*] Cookie di-update dari server." . RESET . "\n";
        }
        break;
    } else {
        echo MERAH . "[!] Cookie ga valid atau expired." . RESET . "\n";
        echo KUNING . "[*] Cek file debug_*.html untuk melihat respon server." . RESET . "\n";
        echo KUNING . "[*] Masukin cookie baru:" . RESET . "\n";
        $cookie = get_cookie_from_user();
        $config['cookie'] = $cookie;
        save_config($config);
        continue;
    }
}

$coins = get_coins($jar);
if (empty($coins)) {
    echo MERAH . "[!] Gagal ambil daftar coin. Cek cookie." . RESET . "\n";
    exit(1);
}

echo "\n" . KUNING . "💰 Daftar coin yang tersedia:" . RESET . "\n";
$i = 1;
foreach ($coins as $coin) {
    printf("%s(%2d) %s%-6s%s", PUTIH, $i, HIJAU, strtoupper($coin), RESET);
    if ($i % 4 == 0 || $i == count($coins)) echo "\n";
    $i++;
}
echo "\n" . CYAN . "🎯 Pilih nomor coin: " . RESET;
$choice = trim(fgets(STDIN));
$idx = (int)$choice - 1;
$coin = isset($coins[$idx]) ? $coins[$idx] : $coins[0];
echo HIJAU . "✅ Coin dipilih: " . strtoupper($coin) . RESET . "\n";

$count = 0;
$failures = 0;   // <-- counter gagal berturut-turut

while (true) {
    $count++;
    echo "\n" . CYAN . "┌─[ ROUND $count ]" . RESET . "\n";
    $result = claim_faucet($jar, $coin, $apikey);
    
    $current_cookie = $jar->toString();
    if ($current_cookie !== $config['cookie']) {
        $config['cookie'] = $current_cookie;
        save_config($config);
        echo CYAN . "[*] Cookie state disimpan." . RESET . "\n";
    }
    
    if ($result === 'EXPIRED') {
        // Session expired, minta cookie baru, reset failure
        $failures = 0;
        echo KUNING . "[*] Cookie expired. Masukin cookie baru:" . RESET . "\n";
        $cookie = get_cookie_from_user();
        $config['cookie'] = $cookie;
        save_config($config);
        
        $jar = new CookieJar();
        $jar->fromString($cookie);
        
        if (!is_logged_in($jar)) {
            echo MERAH . "[!] Cookie masih ga valid. Coba lagi." . RESET . "\n";
            continue;
        }
        echo HIJAU . "[+] Cookie baru valid." . RESET . "\n";
        $config['cookie'] = $jar->toString();
        save_config($config);
        continue;
    }
    
    if ($result === true) {
        // Sukses, reset failure
        $failures = 0;
        echo HIJAU . "⏳ Tunggu buat claim berikutnya..." . RESET . "\n";
        timer(CLAIM_INTERVAL, "🔄 Claim berikutnya dalam");
    } else {
        // Gagal (cooldown, error, dll)
        $failures++;
        echo KUNING . "[!] Gagal ke-$failures dari " . MAX_FAILURES . " (maks)." . RESET . "\n";
        if ($failures >= MAX_FAILURES) {
            echo MERAH . "[!] Bot berhenti karena sudah 2x gagal berturut-turut." . RESET . "\n";
            exit(0);
        }
        echo KUNING . "🔄 Coba lagi dalam " . RETRY_INTERVAL . " detik..." . RESET . "\n";
        timer(RETRY_INTERVAL, "🔄 Coba lagi dalam");
    }
}
