<?php
// ============================================================
// 99FAUCET AUTO BOT - PHP + Login Choice
// STOP jika redirect ke shortlink (tanpa auto solve)
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
define('DIM', "\033[2m");
define('BOLD', "\033[1m");

// ========== KONFIGURASI ==========
define('BASE_URL', 'https://99faucet.com');
define('SOLVER_BASE', 'https://bypassallshortlinks.space');
define('CONFIG_FILE', 'config_99.json');
define('SUCCESS_INTERVAL', 20);
define('FAIL_INTERVAL', 11);

// ========== COOKIE JAR CLASS ==========
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

function get_config() {
    if (file_exists(CONFIG_FILE)) {
        $config = json_decode(file_get_contents(CONFIG_FILE), true);
        if (!isset($config['login_method'])) {
            $config['login_method'] = 'email';
        }
        return $config;
    }
    return null;
}

function save_config($config) {
    file_put_contents(CONFIG_FILE, json_encode($config, JSON_PRETTY_PRINT));
}

function get_login_choice() {
    clear();
    echo CYAN . "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" . RESET . "\n";
    echo BOLD . KUNING . "              🍪 99FAUCET AUTO BOT" . RESET . "\n";
    echo CYAN . "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" . RESET . "\n";
    echo PUTIH . "Pilih metode login:\n";
    echo HIJAU . "  [1] " . PUTIH . "Pakai Cookie (langsung jalan)\n";
    echo HIJAU . "  [2] " . PUTIH . "Pakai Email + Password (auto login)\n";
    echo PUTIH . "Pilihan (1/2): " . KUNING;
    $choice = trim(fgets(STDIN));
    echo RESET;
    
    if ($choice == '2') {
        echo PUTIH . "Email: " . KUNING;
        $email = trim(fgets(STDIN));
        echo PUTIH . "Password: " . KUNING;
        system('stty -echo');
        $password = trim(fgets(STDIN));
        system('stty echo');
        echo "\n";
        echo PUTIH . "API Key bypassallshortlinks: " . KUNING;
        $apikey = trim(fgets(STDIN));
        echo RESET;
        return [
            'method' => 'email',
            'email' => $email,
            'password' => $password,
            'apikey' => $apikey,
            'cookie' => ''
        ];
    } else {
        echo PUTIH . "Cookie (dari browser): " . KUNING;
        $cookie = trim(fgets(STDIN));
        echo PUTIH . "API Key bypassallshortlinks: " . KUNING;
        $apikey = trim(fgets(STDIN));
        echo RESET;
        return [
            'method' => 'cookie',
            'email' => '',
            'password' => '',
            'apikey' => $apikey,
            'cookie' => $cookie
        ];
    }
}

function generate_uf() {
    return md5(uniqid(mt_rand(), true));
}

function http_request($url, $method = 'GET', $data = [], $headers = [], CookieJar &$jar = null, &$finalUrl = null) {
    if ($jar === null) {
        $jar = new CookieJar();
    }
    
    $ch = curl_init();
    $options = [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER => true,
        CURLOPT_FOLLOWLOCATION => true,
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
    
    $finalUrl = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);
    
    $jar->parseSetCookie($header);
    
    curl_close($ch);
    return $body;
}

function solve_hcaptcha($sitekey, $pageurl, $apikey, $show_progress = false) {
    $url = SOLVER_BASE . "/in.php?key=" . urlencode($apikey) . 
           "&method=hcaptcha&sitekey=" . urlencode($sitekey) . 
           "&pageurl=" . urlencode($pageurl);
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');
    $result = curl_exec($ch);
    curl_close($ch);
    
    if (!$result || !str_starts_with($result, 'OK|')) {
        echo MERAH . "[!] Gagal submit hCaptcha: $result" . RESET . "\n";
        return null;
    }
    
    $task_id = explode('|', $result)[1];
    if ($show_progress) {
        echo KUNING . "[+] Task ID    : $task_id" . RESET . "\n";
        echo CYAN . "[*] hCaptcha    : WAITING..." . RESET . "\n";
    }
    
    for ($i = 0; $i < 45; $i++) {
        sleep(2);
        $poll_url = SOLVER_BASE . "/res.php?id=" . urlencode($task_id) . "&key=" . urlencode($apikey);
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $poll_url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        $result = curl_exec($ch);
        curl_close($ch);
        
        if ($result && str_starts_with($result, 'OK|')) {
            $token = explode('|', $result)[1];
            if ($show_progress) {
                echo HIJAU . "[+] hCaptcha   : SOLVED ✓" . RESET . "\n";
            }
            return $token;
        }
        if ($show_progress && $i % 5 == 0) {
            echo DIM . "[*] Polling     : " . ($i+1) . "/45..." . RESET . "\n";
        }
    }
    echo MERAH . "[!] hCaptcha timeout." . RESET . "\n";
    return null;
}

function get_sitekey($html) {
    preg_match('/data-sitekey="([^"]+)"/', $html, $match);
    if (!empty($match[1])) return $match[1];
    preg_match('/sitekey:\s*"([^"]+)"/', $html, $match);
    if (!empty($match[1])) return $match[1];
    return null;
}

function is_logged_in($html) {
    if (strpos($html, 'Logout') !== false || strpos($html, 'Dashboard') !== false) {
        return true;
    }
    return false;
}

function login(CookieJar &$jar, $email, $password, $apikey) {
    echo CYAN . "[*] Login via email..." . RESET . "\n";
    
    $home = http_request(BASE_URL, 'GET', [], [], $jar);
    if (!$home) {
        echo MERAH . "[!] Gagal akses homepage." . RESET . "\n";
        return false;
    }
    
    if (!$jar->get('uf')) {
        $jar->set('uf', generate_uf());
    }
    
    $sitekey = get_sitekey($home);
    if (!$sitekey) {
        echo MERAH . "[!] Gagal ambil sitekey." . RESET . "\n";
        return false;
    }
    echo KUNING . "[+] Sitekey    : $sitekey" . RESET . "\n";
    
    $captcha = solve_hcaptcha($sitekey, BASE_URL, $apikey, true);
    if (!$captcha) return false;
    
    $data = [
        'email' => $email,
        'captcha' => 'hcaptcha',
        'g-recaptcha-response' => '',
        'h-captcha-response' => $captcha,
        'captcha_choosen' => '',
        'uf' => $jar->get('uf'),
        'utt' => 'Asia/Jakarta',
        'ls' => 'id-ID'
    ];
    
    http_request(BASE_URL . "/auth/login", 'POST', $data, [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: ' . BASE_URL,
        'Referer: ' . BASE_URL . '/',
    ], $jar);
    
    $dash = http_request(BASE_URL . "/dashboard", 'GET', [], [], $jar);
    if ($dash && is_logged_in($dash)) {
        echo HIJAU . "[+] Login sukses!" . RESET . "\n";
        return true;
    }
    
    echo MERAH . "[!] Login gagal." . RESET . "\n";
    return false;
}

function get_coins(CookieJar &$jar) {
    $result = http_request(BASE_URL . "/dashboard", 'GET', [], [], $jar);
    if (!$result) return [];
    preg_match_all('/\/faucet\/([a-z]+)/', $result, $matches);
    if (!empty($matches[1])) {
        $coins = array_values(array_unique($matches[1]));
        sort($coins);
        return $coins;
    }
    return [];
}

// ===== CEK SHORTLINK TANPA AUTO SOLVE =====
function get_faucet_page(CookieJar &$jar, $coin, &$finalUrl = null) {
    $url = BASE_URL . "/faucet/$coin";
    $result = http_request($url, 'GET', [], [], $jar, $finalUrl);
    if (!$result) return null;
    
    // Jika redirect ke /links/... atau halaman berisi shortlink, stop
    if ($finalUrl && strpos($finalUrl, '/links/') !== false) {
        return ['status' => 'shortlink', 'url' => $finalUrl];
    }
    if (strpos($result, 'Shortlinks') !== false || strpos($result, 'Click To Visit') !== false) {
        return ['status' => 'shortlink', 'url' => $url];
    }
    
    preg_match('/name="token"\s+value="([^"]+)"/', $result, $token_match);
    $token = isset($token_match[1]) ? $token_match[1] : null;
    
    preg_match('/id="minute">(\d+)/', $result, $min);
    preg_match('/id="second">(\d+)/', $result, $sec);
    $wait = 0;
    if (!empty($min) && !empty($sec)) {
        $wait = (int)$min[1] * 60 + (int)$sec[1];
    }
    
    $sitekey = get_sitekey($result);
    
    return ['status' => 'ok', 'token' => $token, 'html' => $result, 'wait_time' => $wait, 'sitekey' => $sitekey];
}

function wait_for_cooldown(CookieJar &$jar, $coin) {
    echo KUNING . "[*] Cek cooldown..." . RESET . "\n";
    $max_wait = 600;
    $total = 0;
    while ($total < $max_wait) {
        $page = get_faucet_page($jar, $coin);
        if (!$page) break;
        if ($page['status'] === 'shortlink') {
            echo MERAH . "[!] Redirect ke shortlink terdeteksi. Bot berhenti." . RESET . "\n";
            return 'SHORTLINK';
        }
        $wait = $page['wait_time'] ?? 0;
        if ($wait <= 0) {
            echo HIJAU . "[+] Cooldown selesai." . RESET . "\n";
            return true;
        }
        $min = floor($wait / 60);
        $sec = $wait % 60;
        echo KUNING . "[!] Cooldown " . sprintf("%02d:%02d", $min, $sec) . " - menunggu..." . RESET . "\r";
        sleep(2);
        $total += 2;
    }
    return false;
}

function claim_faucet(CookieJar &$jar, $coin, $apikey) {
    echo CYAN . "[*] Claim      : PROCESSING... (coin: " . strtoupper($coin) . ")" . RESET . "\n";
    
    $finalUrl = null;
    $page = get_faucet_page($jar, $coin, $finalUrl);
    if (!$page) {
        echo MERAH . "[!] Gagal ambil halaman faucet." . RESET . "\n";
        return false;
    }
    
    if ($page['status'] === 'shortlink') {
        echo MERAH . "[!] Redirect ke shortlinks: " . $page['url'] . RESET . "\n";
        echo MERAH . "[!] Bot berhenti karena membutuhkan shortlink manual." . RESET . "\n";
        return 'SHORTLINK';
    }
    
    $cooldown = wait_for_cooldown($jar, $coin);
    if ($cooldown === 'SHORTLINK') {
        return 'SHORTLINK';
    }
    if (!$cooldown) {
        echo MERAH . "[!] Gagal menunggu cooldown." . RESET . "\n";
        return false;
    }
    
    $page = get_faucet_page($jar, $coin);
    if (!$page || $page['status'] === 'shortlink') {
        echo MERAH . "[!] Halaman faucet tidak valid atau shortlink." . RESET . "\n";
        return 'SHORTLINK';
    }
    
    $token = $page['token'];
    $sitekey = $page['sitekey'];
    echo KUNING . "[+] Token      : $token" . RESET . "\n";
    echo KUNING . "[+] Sitekey    : " . substr($sitekey, 0, 16) . "****" . RESET . "\n";
    
    $url = BASE_URL . "/faucet/$coin";
    $captcha = solve_hcaptcha($sitekey, $url, $apikey, true);
    if (!$captcha) return false;
    
    $data = [
        'ci_csrf_token' => '',
        'token' => $token,
        'currency' => $coin,
        'captcha' => 'hcaptcha',
        'g-recaptcha-response' => '',
        'h-captcha-response' => $captcha,
        'uf' => $jar->get('uf'),
        'utt' => 'Asia/Jakarta',
        'ls' => 'id-ID'
    ];
    
    $result = http_request(BASE_URL . "/faucet/verify", 'POST', $data, [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: ' . BASE_URL,
        'Referer: ' . BASE_URL . "/faucet/$coin",
    ], $jar);
    
    if (!$result) {
        echo MERAH . "[!] Gagal claim (no response)." . RESET . "\n";
        return false;
    }
    
    if (strpos($result, 'Swal.fire') !== false && strpos($result, 'Good job') !== false) {
        echo HIJAU . "[+] Claim      : SUCCESS ✓" . RESET . "\n";
        preg_match('/text:\s*[\'"]?([\d.]+)\s+(\w+)/', $result, $reward);
        if (!empty($reward)) {
            echo KUNING . "[+] Reward     : " . $reward[1] . " " . $reward[2] . RESET . "\n";
        }
        return true;
    }
    
    preg_match('/id="minute">(\d+)/', $result, $min);
    preg_match('/id="second">(\d+)/', $result, $sec);
    if (!empty($min) && !empty($sec)) {
        $wait = (int)$min[1] * 60 + (int)$sec[1];
        if ($wait > 0) {
            echo KUNING . "[!] Cooldown $wait detik." . RESET . "\n";
            return false;
        }
    }
    
    if (strpos($result, 'has been sent') !== false || strpos($result, 'success') !== false) {
        echo HIJAU . "[+] Claim      : SUCCESS ✓" . RESET . "\n";
        return true;
    }
    
    if (strpos($result, 'login') !== false && strlen($result) < 500) {
        echo MERAH . "[!] Session expired." . RESET . "\n";
        return "EXPIRED";
    }
    
    echo MERAH . "[?] Claim tidak jelas." . RESET . "\n";
    file_put_contents("claim_debug_99.html", $result);
    return false;
}

// ========== MAIN ==========
$config = get_config();

if ($config && isset($config['login_method'])) {
    echo CYAN . "Config ditemukan. Login method terakhir: " . $config['login_method'] . RESET . "\n";
    echo PUTIH . "Gunakan config yang ada? (y/n): " . KUNING;
    $use_config = trim(fgets(STDIN));
    if (strtolower($use_config) === 'y') {
        $login_data = [
            'method' => $config['login_method'],
            'email' => $config['email'] ?? '',
            'password' => $config['password'] ?? '',
            'apikey' => $config['apikey'] ?? '',
            'cookie' => $config['cookie'] ?? ''
        ];
    } else {
        $login_data = get_login_choice();
    }
} else {
    $login_data = get_login_choice();
}

save_config($login_data);

clear();
echo CYAN . "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" . RESET . "\n";
echo BOLD . KUNING . "              🍪 99FAUCET AUTO BOT" . RESET . "\n";
echo CYAN . "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" . RESET . "\n";
echo KUNING . "[*] Login method: " . $login_data['method'] . RESET . "\n";

$jar = new CookieJar();

if ($login_data['method'] === 'cookie') {
    if (!empty($login_data['cookie'])) {
        $jar->fromString($login_data['cookie']);
        echo HIJAU . "[+] Cookie loaded." . RESET . "\n";
    } else {
        echo MERAH . "[!] Cookie kosong!" . RESET . "\n";
        exit(1);
    }
    
    $dash = http_request(BASE_URL . "/dashboard", 'GET', [], [], $jar);
    if ($dash && is_logged_in($dash)) {
        echo HIJAU . "[+] Session aktif dengan cookie!" . RESET . "\n";
    } else {
        echo MERAH . "[!] Cookie tidak valid atau expired." . RESET . "\n";
        exit(1);
    }
} else {
    $email = $login_data['email'];
    $password = $login_data['password'];
    $apikey = $login_data['apikey'];
    
    $dash = http_request(BASE_URL . "/dashboard", 'GET', [], [], $jar);
    if ($dash && is_logged_in($dash)) {
        echo HIJAU . "[+] Session aktif!" . RESET . "\n";
    } else {
        echo KUNING . "[*] Session tidak aktif, mencoba login..." . RESET . "\n";
        if (!login($jar, $email, $password, $apikey)) {
            echo MERAH . "[!] Login gagal. Cek config." . RESET . "\n";
            exit(1);
        }
        $login_data['cookie'] = $jar->toString();
        save_config($login_data);
        echo HIJAU . "[+] Cookie disimpan." . RESET . "\n";
    }
}

$coins = get_coins($jar);
if (empty($coins)) {
    echo MERAH . "[!] Gagal ambil daftar coin." . RESET . "\n";
    exit(1);
}

echo "\n" . KUNING . "💰 Daftar coin yang tersedia:" . RESET . "\n";
$emoji_map = [
    'ltc' => '🪙', 'dgb' => '💎', 'trx' => '🔥', 'bch' => '💵',
    'bnb' => '🟡', 'sol' => '☀️', 'xrp' => '💧', 'pol' => '🟣',
    'ada' => '🔵', 'ton' => '💎', 'xlm' => '🌟', 'eth' => '♦️',
    'usdt' => '💵', 'dash' => '🟠', 'doge' => '🐕', 'usdc' => '💵',
    'pepe' => '🐸', 'trump' => '🇺🇸'
];
$i = 1;
foreach ($coins as $coin) {
    $emoji = isset($emoji_map[$coin]) ? $emoji_map[$coin] : '🪙';
    printf("%s(%2d) %s %s%-6s%s", PUTIH, $i, $emoji, HIJAU, strtoupper($coin), RESET);
    if ($i % 4 == 0 || $i == count($coins)) echo "\n";
    $i++;
}
echo "\n" . CYAN . "🎯 Pilih nomor coin: " . RESET;
$choice = trim(fgets(STDIN));
$idx = (int)$choice - 1;
$coin = isset($coins[$idx]) ? $coins[$idx] : $coins[0];
echo HIJAU . "✅ Coin dipilih: " . strtoupper($coin) . RESET . "\n";

$count = 0;
while (true) {
    $count++;
    echo "\n" . CYAN . "┌─[ ROUND $count ]" . RESET . "\n";
    $result = claim_faucet($jar, $coin, $login_data['apikey']);
    
    if ($result === "EXPIRED") {
        echo KUNING . "[*] Session expired. Mencoba refresh..." . RESET . "\n";
        if ($login_data['method'] === 'email') {
            if (login($jar, $login_data['email'], $login_data['password'], $login_data['apikey'])) {
                $login_data['cookie'] = $jar->toString();
                save_config($login_data);
                echo HIJAU . "[+] Session refresh sukses!" . RESET . "\n";
                continue;
            }
        } else {
            echo MERAH . "[!] Cookie expired. Harap update cookie di config." . RESET . "\n";
            break;
        }
    }
    
    if ($result === 'SHORTLINK') {
        echo MERAH . "[!] Shortlink terdeteksi. Bot berhenti." . RESET . "\n";
        break;
    }
    
    if ($result) {
        echo HIJAU . "⏳ Next claim in " . SUCCESS_INTERVAL . "s..." . RESET . "\n";
        timer(SUCCESS_INTERVAL, "🔄 Next claim in");
    } else {
        echo KUNING . "🔄 Retry in " . FAIL_INTERVAL . "s..." . RESET . "\n";
        timer(FAIL_INTERVAL, "🔄 Retry in");
    }
}
