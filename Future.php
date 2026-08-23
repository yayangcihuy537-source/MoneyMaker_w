<?php
// ============================================================
// CRYPTOFUTURE AUTO BOT - PHP Version (Cookie Only)
// ALWAYS ASK FOR NEW COOKIE ON EACH RUN
// ============================================================

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');

// ========== WARNA ==========
define('MERAH', "\033[0;31m");
define('HIJAU', "\033[0;32m");
define('KUNING', "\033[0;33m");
define('CYAN', "\033[0;36m");
define('PUTIH', "\033[0;37m");
define('RESET', "\033[0m");
define('BOLD', "\033[1m");

// ========== KONFIGURASI ==========
define('BASE_URL', 'https://cryptofuture.co.in');
define('CONFIG_FILE', 'config_cf.json');
define('CLAIM_INTERVAL', 11);

// ========== COOKIE JAR ==========
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
                    $this->cookies[trim($parts[0])] = trim($parts[1]);
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

// ========== FUNGSI ==========
function clear() {
    system('clear');
}

function timer($seconds, $prefix = "[!] Please wait") {
    $wait = (int)$seconds;
    $frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'];
    $frame_count = count($frames);
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
            $current = ($current + 1) % $frame_count;
            if ((microtime(true) - $start) >= 1) break;
        }
        $wait--;
    }
    echo str_repeat(" ", 50) . "\r";
}

// ===== MODIFIED: ALWAYS ASK FOR NEW COOKIE =====
function get_config() {
    echo PUTIH . "Cookie (dari browser, format: key1=value1; key2=value2): " . KUNING;
    $cookie = trim(fgets(STDIN));
    if (empty($cookie)) {
        echo MERAH . "[!] Cookie tidak boleh kosong." . RESET . "\n";
        exit(1);
    }
    $config = ['cookie' => $cookie];
    // Tetap simpan ke file sebagai backup, tapi gak dipakai otomatis
    file_put_contents(CONFIG_FILE, json_encode($config, JSON_PRETTY_PRINT));
    echo HIJAU . "Config disimpan ke " . CONFIG_FILE . " (backup)\n" . RESET;
    sleep(1);
    return $config;
}

function generate_device_token() {
    return 'dev_' . substr(md5(uniqid(mt_rand(), true)), 0, 15) . time();
}

function generate_smart_token() {
    $data = [
        'ts' => intval(microtime(true) * 1000),
        'cpu' => 8,
        'mem' => 8,
        'w' => 384,
        'h' => 832,
        'touch' => 5,
        'moves' => rand(3, 15)
    ];
    return base64_encode(json_encode($data));
}

function generate_fp_hash() {
    $ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36';
    $raw = 'fp-' . $ua . '384832';
    return hash('sha256', $raw);
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
        CURLOPT_USERAGENT => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
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
        $options[CURLOPT_HTTPHEADER] = $headers;
    }
    
    curl_setopt_array($ch, $options);
    $response = curl_exec($ch);
    
    if ($response === false) {
        curl_close($ch);
        return null;
    }
    
    $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $body = substr($response, $header_size);
    $header = substr($response, 0, $header_size);
    
    $jar->parseSetCookie($header);
    
    curl_close($ch);
    return $body;
}

function is_logged_in($jar) {
    $dash = http_request(BASE_URL . '/dashboard', 'GET', [], [], $jar);
    if ($dash && strpos($dash, 'Dashboard') !== false) {
        return true;
    }
    return false;
}

function get_faucet_data($jar) {
    // Gunakan /earn karena dari trace
    $html = http_request(BASE_URL . '/earn', 'GET', [], [], $jar);
    if (!$html) {
        $html = http_request(BASE_URL . '/faucet/earn', 'GET', [], [], $jar);
    }
    if (!$html) return null;
    
    // Ekstrak dengan regex sederhana
    $csrf = '';
    $token = '';
    $earn_ticket = '';
    $wallet = '';
    
    // Cari dengan pattern yang lebih aman
    if (preg_match('/name="csrf_token_name"\s+value="([^"]+)"/', $html, $m)) {
        $csrf = $m[1];
    } else if (preg_match('/csrf_token_name"\s*value="([^"]+)"/', $html, $m)) {
        $csrf = $m[1];
    }
    
    if (preg_match('/name="token"\s+value="([^"]+)"/', $html, $m)) {
        $token = $m[1];
    } else if (preg_match('/token"\s*value="([^"]+)"/', $html, $m)) {
        $token = $m[1];
    }
    
    if (preg_match('/name="earn_ticket"\s+value="([^"]+)"/', $html, $m)) {
        $earn_ticket = $m[1];
    } else if (preg_match('/earn_ticket"\s*value="([^"]+)"/', $html, $m)) {
        $earn_ticket = $m[1];
    }
    
    if (preg_match('/name="wallet"\s+value="([^"]+)"/', $html, $m)) {
        $wallet = $m[1];
    } else if (preg_match('/wallet"\s*value="([^"]+)"/', $html, $m)) {
        $wallet = $m[1];
    }
    
    // Jika masih kosong, coba dari hidden input di form
    if (empty($csrf) || empty($token) || empty($earn_ticket)) {
        preg_match('/<form[^>]*>.*?csrf_token_name.*?value="([^"]+)"/s', $html, $m);
        if (!empty($m[1])) $csrf = $m[1];
        preg_match('/<form[^>]*>.*?token.*?value="([^"]+)"/s', $html, $m);
        if (!empty($m[1])) $token = $m[1];
        preg_match('/<form[^>]*>.*?earn_ticket.*?value="([^"]+)"/s', $html, $m);
        if (!empty($m[1])) $earn_ticket = $m[1];
        preg_match('/<form[^>]*>.*?wallet.*?value="([^"]+)"/s', $html, $m);
        if (!empty($m[1])) $wallet = $m[1];
    }
    
    // Cek redirect ke login
    if (strpos($html, 'login') !== false && strlen($html) < 500) {
        return 'EXPIRED';
    }
    
    if (empty($csrf) || empty($token) || empty($earn_ticket)) {
        return null;
    }
    
    return [
        'csrf' => $csrf,
        'token' => $token,
        'earn_ticket' => $earn_ticket,
        'wallet' => $wallet,
        'html' => $html
    ];
}

function extract_timer($html) {
    if (preg_match('/Next claim available in:\s*<span[^>]*>(\d+)<\/span>m\s*<span[^>]*>(\d+)<\/span>s/', $html, $m)) {
        return (int)$m[1] * 60 + (int)$m[2];
    }
    if (preg_match('/Next claim available in:\s*<span[^>]*>(\d+)<\/span>s/', $html, $m)) {
        return (int)$m[1];
    }
    if (preg_match('/id="minute">(\d+)/', $html, $min) && preg_match('/id="second">(\d+)/', $html, $sec)) {
        return (int)$min[1] * 60 + (int)$sec[1];
    }
    return 0;
}

function extract_reward($html) {
    if (preg_match('/(\d+)\s*Coins\s*has been added/', $html, $m)) {
        return (int)$m[1];
    }
    if (preg_match('/\+\s*(\d+)\s*Coins/', $html, $m)) {
        return (int)$m[1];
    }
    return 10;
}

function extract_balance($html) {
    if (preg_match('/balance-amount[^>]*>.*?(\d+)\s*<span/', $html, $m)) {
        return (int)$m[1];
    }
    if (preg_match('/TOTAL BALANCE.*?(\d+)\s*Coins/', $html, $m)) {
        return (int)$m[1];
    }
    return null;
}

function claim_faucet($jar, $faucet_data) {
    $csrf = $faucet_data['csrf'];
    $token = $faucet_data['token'];
    $earn_ticket = $faucet_data['earn_ticket'];
    $wallet = $faucet_data['wallet'];
    
    if (empty($wallet)) {
        $wallet = 'garapanfaucetcrypto@gmail.com';
    }
    
    $smart_token = generate_smart_token();
    $fp_hash = generate_fp_hash();
    
    $data = [
        'csrf_token_name' => $csrf,
        'token' => $token,
        'earn_ticket' => $earn_ticket,
        'fp_hash' => $fp_hash,
        'confirm_wallet' => '',
        'wallet' => $wallet,
        'smart_token' => $smart_token,
        'captcha' => 'smartcaptcha'
    ];
    
    $result = http_request(BASE_URL . '/faucet/earn', 'POST', $data, [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: ' . BASE_URL,
        'Referer: ' . BASE_URL . '/earn',
    ], $jar);
    
    if (!$result) {
        echo MERAH . "[!] Gagal claim (no response)." . RESET . "\n";
        return false;
    }
    
    $html = $result;
    
    // Cek sukses
    if (strpos($html, 'Success') !== false || strpos($html, 'coins has been added') !== false) {
        $reward = extract_reward($html);
        echo HIJAU . "[+] Claim sukses! +$reward Coins" . RESET . "\n";
        $balance = extract_balance($html);
        if ($balance !== null) {
            echo HIJAU . "[+] Balance sekarang: $balance Coins" . RESET . "\n";
        }
        return true;
    }
    
    // Cek cooldown
    $timer = extract_timer($html);
    if ($timer > 0) {
        echo KUNING . "[⏳] Cooldown $timer detik." . RESET . "\n";
        return $timer;
    }
    
    // Cek "Failed!" retry
    if (strpos($html, 'Failed!') !== false || strpos($html, 'Please try again') !== false) {
        echo KUNING . "[!] Got Failed, refresh form..." . RESET . "\n";
        return false;
    }
    
    echo MERAH . "[?] Claim tidak jelas." . RESET . "\n";
    file_put_contents('claim_debug_cf.html', $html);
    return false;
}

// ========== MAIN ==========
clear();

echo CYAN . "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" . RESET . "\n";
echo BOLD . KUNING . "              🍪 CryptoFuture AUTO BOT" . RESET . "\n";
echo CYAN . "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" . RESET . "\n";

// ALWAYS ask for cookie
$config = get_config();
$cookie_str = $config['cookie'] ?? '';

if (empty($cookie_str)) {
    echo MERAH . "[!] Cookie tidak ditemukan." . RESET . "\n";
    exit(1);
}

$jar = new CookieJar();
$jar->fromString($cookie_str);

// Cek session
if (!is_logged_in($jar)) {
    echo MERAH . "[!] Cookie tidak valid atau expired." . RESET . "\n";
    echo KUNING . "[*] Ambil cookie baru dari browser dan jalankan ulang." . RESET . "\n";
    exit(1);
}
echo HIJAU . "[+] Session aktif!" . RESET . "\n";

// Simpan cookie terbaru (opsional)
$config['cookie'] = $jar->toString();
file_put_contents(CONFIG_FILE, json_encode($config, JSON_PRETTY_PRINT));

// Ambil data faucet
$faucet_data = get_faucet_data($jar);
if (!$faucet_data || $faucet_data === 'EXPIRED') {
    echo MERAH . "[!] Gagal ambil data faucet." . RESET . "\n";
    if ($faucet_data === 'EXPIRED') {
        echo KUNING . "[*] Cookie mungkin perlu refresh. Ambil cookie baru." . RESET . "\n";
    }
    exit(1);
}

echo KUNING . "[+] CSRF       : " . $faucet_data['csrf'] . RESET . "\n";
echo KUNING . "[+] Token      : " . $faucet_data['token'] . RESET . "\n";
echo KUNING . "[+] Earn Ticket: " . $faucet_data['earn_ticket'] . RESET . "\n";

$count = 0;
while (true) {
    $count++;
    echo "\n" . CYAN . "┌─[ ROUND $count ]" . RESET . "\n";
    
    $faucet_data = get_faucet_data($jar);
    if (!$faucet_data) {
        echo MERAH . "[!] Gagal refresh data faucet." . RESET . "\n";
        sleep(5);
        continue;
    }
    if ($faucet_data === 'EXPIRED') {
        echo MERAH . "[!] Session expired. Ambil cookie baru." . RESET . "\n";
        break;
    }
    
    $result = claim_faucet($jar, $faucet_data);
    if ($result === true) {
        echo HIJAU . "⏳ Next claim in " . CLAIM_INTERVAL . "s..." . RESET . "\n";
        timer(CLAIM_INTERVAL, "🔄 Next claim in");
    } elseif (is_int($result) && $result > 0) {
        echo KUNING . "⏳ Cooldown $result detik..." . RESET . "\n";
        timer($result + 2, "🔄 Cooldown");
    } else {
        echo KUNING . "🔄 Retry in 5s..." . RESET . "\n";
        timer(5, "🔄 Retry in");
    }
}
