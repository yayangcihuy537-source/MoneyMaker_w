<?php
// ============================================================
// 99FAUCET AUTO BOT
// Solver: WARYONO.MY.ID (freesolana.top style)
// ============================================================

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');

define('MERAH',  "\033[0;31m");
define('HIJAU',  "\033[0;32m");
define('BIRU',   "\033[0;34m");
define('KUNING', "\033[0;33m");
define('CYAN',   "\033[0;36m");
define('PUTIH',  "\033[0;37m");
define('RESET',  "\033[0m");
define('DIM',    "\033[2m");
define('BOLD',   "\033[1m");

define('BASE_URL',        'https://99faucet.com');
define('API_IN',          'https://api.waryono.my.id/in.php');
define('API_OUT',         'https://api.waryono.my.id/res.php');
define('CONFIG_FILE',     'config_99.json');
define('SUCCESS_INTERVAL', 20);
define('FAIL_INTERVAL',    11);

// ═══════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════
function clear() { system('clear'); }

function line($text) { echo "\r\033[K" . $text; }

function timer($seconds, $prefix = "[!] Please wait") {
    $wait = (int)$seconds;
    $frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'];
    $fc = count($frames);
    $cf = 0;
    while ($wait > 0) {
        $st = microtime(true);
        while ((microtime(true) - $st) < 1) {
            $h = floor($wait / 3600);
            $m = floor(($wait % 3600) / 60);
            $s = $wait % 60;
            $tf = sprintf('%02d:%02d:%02d', $h, $m, $s);
            echo "\r\033[K" . PUTIH . $prefix . HIJAU . " $tf " . PUTIH . $frames[$cf];
            usleep(100000);
            $cf = ($cf + 1) % $fc;
            if ((microtime(true) - $st) >= 1) break;
        }
        $wait--;
    }
    echo "\r\033[K";
}

// ═══════════════════════════════════════════════════════════
// COOKIE JAR
// ═══════════════════════════════════════════════════════════
class CookieJar {
    private $cookies = [];

    public function set($name, $value) { $this->cookies[$name] = $value; }
    public function get($name) { return $this->cookies[$name] ?? null; }
    public function getAll() { return $this->cookies; }

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
        foreach ($this->cookies as $k => $v) { $str .= "$k=$v; "; }
        return rtrim($str, '; ');
    }

    public function fromString($str) {
        if (empty($str)) return;
        foreach (explode(';', $str) as $pair) {
            $parts = explode('=', trim($pair), 2);
            if (count($parts) == 2) $this->cookies[$parts[0]] = $parts[1];
        }
    }
}

// ═══════════════════════════════════════════════════════════
// HTTP (with CookieJar)
// ═══════════════════════════════════════════════════════════
function http_request($url, $method = 'GET', $data = [], $headers = [], CookieJar &$jar = null, &$finalUrl = null, $follow = true) {
    if ($jar === null) $jar = new CookieJar();

    $ch = curl_init();
    $opts = [
        CURLOPT_URL            => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER         => true,
        CURLOPT_FOLLOWLOCATION => $follow,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT        => 30,
        CURLOPT_CONNECTTIMEOUT => 30,
        CURLOPT_USERAGENT      => 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
    ];

    $cookie_str = $jar->toString();
    if (!empty($cookie_str)) $opts[CURLOPT_COOKIE] = $cookie_str;

    if (strtoupper($method) === 'POST') {
        $opts[CURLOPT_POST] = true;
        $opts[CURLOPT_POSTFIELDS] = http_build_query($data);
    }
    if (!empty($headers)) $opts[CURLOPT_HTTPHEADER] = $headers;

    curl_setopt_array($ch, $opts);
    $response = curl_exec($ch);

    if ($response === false) { curl_close($ch); return null; }

    $hdrSize = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $body    = substr($response, $hdrSize);
    $header  = substr($response, 0, $hdrSize);
    $finalUrl = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);

    $jar->parseSetCookie($header);
    curl_close($ch);
    return $body;
}

// ═══════════════════════════════════════════════════════════
// HTTP (no cookie — buat solver)
// ═══════════════════════════════════════════════════════════
function http_nocookie($url, $method = 'GET', $data = [], $headers = [], $json_body = false) {
    $ch = curl_init();
    $opts = [
        CURLOPT_URL            => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT        => 60,
        CURLOPT_CONNECTTIMEOUT => 30,
    ];
    if (strtoupper($method) === 'POST') {
        $opts[CURLOPT_POST] = true;
        $opts[CURLOPT_POSTFIELDS] = $json_body ? $data : http_build_query($data);
    }
    if (!empty($headers)) $opts[CURLOPT_HTTPHEADER] = $headers;

    curl_setopt_array($ch, $opts);
    $res = curl_exec($ch);
    curl_close($ch);
    return $res;
}

// ═══════════════════════════════════════════════════════════
// WARYONO HCAPTCHA SOLVER (freesolana.top style)
// ═══════════════════════════════════════════════════════════
function solve_hcaptcha($apikey, $sitekey, $pageurl) {
    $attempt = 0;
    while (true) {
        $attempt++;

        // ─── STEP 1: Submit task ───
        $payload = json_encode([
            "apikey"  => $apikey,
            "methods" => "hcaptcha",
            "domain"  => $pageurl,
            "sitekey" => $sitekey,
            "json"    => 1,
        ]);

        $res = http_nocookie(API_IN, 'POST', $payload, [
            "Content-Type: application/json"
        ], true);

        $json = json_decode($res, true);
        $id = $json["request"] ?? null;

        if (!$id || strpos($id, "ERROR_") !== false) {
            $err = $json["request"] ?? "no response";
            echo MERAH . "[!] Submit gagal ($err) — retry #$attempt..." . RESET . "\n";

            // fatal error → stop
            if (is_string($err) && (
                strpos($err, 'ERROR_KEY') !== false ||
                strpos($err, 'ERROR_WRONG') !== false ||
                strpos($err, 'ERROR_ZERO_BALANCE') !== false
            )) {
                echo MERAH . "[💀] API key / saldo bermasalah. Stop." . RESET . "\n";
                return null;
            }
            sleep(3);
            continue;
        }

        echo KUNING . "[+] Task ID    : $id" . RESET . "\n";
        echo CYAN  . "[*] hCaptcha    : WAITING..." . RESET . "\n";

        // ─── STEP 2: Poll ───
        for ($i = 1; $i <= 60; $i++) {
            sleep(5);
            $url = API_OUT . "?apikey=" . urlencode($apikey) . "&id=" . urlencode($id) . "&action=get&json=1";
            $r = http_nocookie($url);

            line(PUTIH . "[*] Polling     : " . ($i * 5) . "s " . HIJAU . "⣾");

            if (strpos($r, "CAPCHA_NOT_READY") !== false) continue;

            $d = json_decode($r, true);
            if ($d && isset($d["request"])
                && strpos($d["request"], "ERROR_") === false
                && $d["request"] !== "CAPCHA_NOT_READY") {
                echo "\r\033[K" . HIJAU . "[+] hCaptcha   : SOLVED ✓" . RESET . "\n";
                return $d["request"];
            }

            // error → break inner, retry outer
            echo "\r\033[K" . MERAH . "[!] Solver error: " . ($d["request"] ?? $r) . RESET . "\n";
            break;
        }

        sleep(3);
    }
}

// ═══════════════════════════════════════════════════════════
// 99FAUCET SPECIFIC
// ═══════════════════════════════════════════════════════════
function get_sitekey($html) {
    if (preg_match('/data-sitekey="([^"]+)"/', $html, $m)) return $m[1];
    if (preg_match('/sitekey:\s*"([^"]+)"/', $html, $m))   return $m[1];
    return null;
}

function is_logged_in($html) {
    return strpos($html, 'Logout') !== false || strpos($html, 'Dashboard') !== false;
}

function generate_uf() {
    return md5(uniqid(mt_rand(), true));
}

function get_config() {
    if (!file_exists(CONFIG_FILE)) return null;
    $cfg = json_decode(file_get_contents(CONFIG_FILE), true);
    if (!isset($cfg['login_method'])) $cfg['login_method'] = 'email';
    return $cfg;
}

function save_config($cfg) {
    file_put_contents(CONFIG_FILE, json_encode($cfg, JSON_PRETTY_PRINT));
}

function get_login_choice() {
    clear();
    echo CYAN . "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" . RESET . "\n";
    echo BOLD . KUNING . "              🍪 99FAUCET AUTO BOT" . RESET . "\n";
    echo CYAN . "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" . RESET . "\n";
    echo DIM . PUTIH . "              Solver: WARYONO.MY.ID" . RESET . "\n";
    echo CYAN . "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" . RESET . "\n";
    echo PUTIH . "Pilih metode login:\n";
    echo HIJAU . "  [1] " . PUTIH . "Pakai Cookie\n";
    echo HIJAU . "  [2] " . PUTIH . "Pakai Email + Password\n";
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
        echo "\n" . PUTIH . "API Key waryono: " . KUNING;
        $apikey = trim(fgets(STDIN));
        echo RESET;
        return [
            'login_method' => 'email',
            'email'        => $email,
            'password'     => $password,
            'apikey'       => $apikey,
            'cookie'       => ''
        ];
    } else {
        echo PUTIH . "Cookie: " . KUNING;
        $cookie = trim(fgets(STDIN));
        echo PUTIH . "API Key waryono: " . KUNING;
        $apikey = trim(fgets(STDIN));
        echo RESET;
        return [
            'login_method' => 'cookie',
            'email'        => '',
            'password'     => '',
            'apikey'       => $apikey,
            'cookie'       => $cookie
        ];
    }
}

function login(CookieJar &$jar, $email, $password, $apikey) {
    echo CYAN . "[*] Login via email..." . RESET . "\n";

    $home = http_request(BASE_URL, 'GET', [], [], $jar);
    if (!$home) { echo MERAH . "[!] Gagal akses homepage." . RESET . "\n"; return false; }

    if (!$jar->get('uf')) $jar->set('uf', generate_uf());

    $sitekey = get_sitekey($home);
    if (!$sitekey) { echo MERAH . "[!] Gagal ambil sitekey login." . RESET . "\n"; return false; }
    echo KUNING . "[+] Sitekey    : $sitekey" . RESET . "\n";

    $captcha = solve_hcaptcha($apikey, $sitekey, BASE_URL);
    if (!$captcha) return false;

    $data = [
        'email'                 => $email,
        'password'              => $password,
        'captcha'               => 'hcaptcha',
        'g-recaptcha-response'  => $captcha,   // <-- FIX: isi token
        'h-captcha-response'    => $captcha,
        'captcha_choosen'       => '',
        'uf'                    => $jar->get('uf'),
        'utt'                   => 'Asia/Jakarta',
        'ls'                    => 'id-ID'
    ];

    http_request(BASE_URL . "/auth/login", 'POST', $data, [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: '  . BASE_URL,
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

function is_shortlink_page($html) {
    if (strpos($html, 'name="token"') !== false || strpos($html, 'id="token"') !== false) return false;
    if (strpos($html, 'Click To Visit') !== false) return true;
    return false;
}

function get_faucet_page(CookieJar &$jar, $coin, &$finalUrl = null) {
    $url = BASE_URL . "/faucet/$coin";
    $result = http_request($url, 'GET', [], [], $jar, $finalUrl);
    if (!$result) return null;

    if ($finalUrl && strpos($finalUrl, '/links/') !== false) {
        return ['status' => 'shortlink', 'url' => $finalUrl];
    }
    if (is_shortlink_page($result)) {
        return ['status' => 'shortlink', 'url' => $url];
    }

    preg_match('/name="token"\s+value="([^"]+)"/', $result, $tm);
    $token = $tm[1] ?? null;

    preg_match('/id="minute">(\d+)/', $result, $min);
    preg_match('/id="second">(\d+)/', $result, $sec);
    $wait = 0;
    if (!empty($min) && !empty($sec)) $wait = (int)$min[1] * 60 + (int)$sec[1];

    $sitekey = get_sitekey($result);

    return ['status' => 'ok', 'token' => $token, 'html' => $result, 'wait_time' => $wait, 'sitekey' => $sitekey];
}

function wait_for_cooldown(CookieJar &$jar, $coin) {
    echo KUNING . "[*] Cek cooldown..." . RESET . "\n";
    $max = 600; $total = 0;
    while ($total < $max) {
        $page = get_faucet_page($jar, $coin);
        if (!$page) break;
        if ($page['status'] === 'shortlink') return 'SHORTLINK';

        $wait = $page['wait_time'] ?? 0;
        if ($wait <= 0) { echo HIJAU . "[+] Cooldown selesai." . RESET . "\n"; return true; }

        $m = floor($wait / 60); $s = $wait % 60;
        echo "\r\033[K" . KUNING . "[!] Cooldown " . sprintf("%02d:%02d", $m, $s) . " - menunggu..." . RESET;
        sleep(2); $total += 2;
    }
    return false;
}

function claim_faucet(CookieJar &$jar, $coin, $apikey) {
    echo CYAN . "[*] Claim      : PROCESSING... (coin: " . strtoupper($coin) . ")" . RESET . "\n";

    $finalUrl = null;
    $page = get_faucet_page($jar, $coin, $finalUrl);
    if (!$page) { echo MERAH . "[!] Gagal ambil halaman faucet." . RESET . "\n"; return false; }
    if ($page['status'] === 'shortlink') return 'SHORTLINK';

    $cd = wait_for_cooldown($jar, $coin);
    if ($cd === 'SHORTLINK') return 'SHORTLINK';
    if (!$cd) { echo MERAH . "[!] Gagal menunggu cooldown." . RESET . "\n"; return false; }

    $page = get_faucet_page($jar, $coin);
    if (!$page || $page['status'] === 'shortlink') return 'SHORTLINK';

    $token   = $page['token'];
    $sitekey = $page['sitekey'];

    if (!$token || !$sitekey) {
        echo MERAH . "[!] Token / sitekey kosong." . RESET . "\n";
        return false;
    }

    echo KUNING . "[+] Token      : $token" . RESET . "\n";
    echo KUNING . "[+] Sitekey    : " . substr($sitekey, 0, 16) . "****" . RESET . "\n";

    $url = BASE_URL . "/faucet/$coin";
    $captcha = solve_hcaptcha($apikey, $sitekey, $url);
    if (!$captcha) return false;

    $data = [
        'ci_csrf_token'         => '',
        'token'                 => $token,
        'currency'              => $coin,
        'captcha'               => 'hcaptcha',
        'g-recaptcha-response'  => $captcha,   // <-- FIX
        'h-captcha-response'    => $captcha,
        'uf'                    => $jar->get('uf'),
        'utt'                   => 'Asia/Jakarta',
        'ls'                    => 'id-ID'
    ];

    $result = http_request(BASE_URL . "/faucet/verify", 'POST', $data, [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: '  . BASE_URL,
        'Referer: ' . $url,
    ], $jar);

    if (!$result) { echo MERAH . "[!] Gagal claim (no response)." . RESET . "\n"; return false; }

    // ─── Success check ───
    if (strpos($result, 'Swal.fire') !== false && strpos($result, 'Good job') !== false) {
        echo HIJAU . "[+] Claim      : SUCCESS ✓" . RESET . "\n";
        if (preg_match('/text:\s*[\'"]?([\d.]+)\s+(\w+)/', $result, $r)) {
            echo KUNING . "[+] Reward     : " . $r[1] . " " . $r[2] . RESET . "\n";
        }
        return true;
    }

    // ─── Cooldown / error check ───
    preg_match('/id="minute">(\d+)/', $result, $min);
    preg_match('/id="second">(\d+)/', $result, $sec);
    if (!empty($min) && !empty($sec)) {
        $wait = (int)$min[1] * 60 + (int)$sec[1];
        if ($wait > 0) { echo KUNING . "[!] Cooldown $wait detik." . RESET . "\n"; return false; }
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

// ═══════════════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════════════
$config = get_config();

if ($config && isset($config['login_method'])) {
    echo CYAN . "Config ditemukan. Login method terakhir: " . $config['login_method'] . RESET . "\n";
    echo PUTIH . "Gunakan config yang ada? (y/n): " . KUNING;
    $use = trim(fgets(STDIN));
    if (strtolower($use) === 'y') {
        $login_data = [
            'login_method' => $config['login_method'],
            'email'        => $config['email']    ?? '',
            'password'     => $config['password'] ?? '',
            'apikey'       => $config['apikey']   ?? '',
            'cookie'       => $config['cookie']   ?? ''
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
echo KUNING . "[*] Login method: " . $login_data['login_method'] . RESET . "\n";
echo KUNING . "[*] Solver      : WARYONO.MY.ID" . RESET . "\n";

$jar = new CookieJar();

// ─── AUTH ───
if ($login_data['login_method'] === 'cookie') {
    if (empty($login_data['cookie'])) { echo MERAH . "[!] Cookie kosong!" . RESET . "\n"; exit(1); }
    $jar->fromString($login_data['cookie']);
    echo HIJAU . "[+] Cookie loaded." . RESET . "\n";

    $dash = http_request(BASE_URL . "/dashboard", 'GET', [], [], $jar);
    if ($dash && is_logged_in($dash)) {
        echo HIJAU . "[+] Session aktif dengan cookie!" . RESET . "\n";
    } else {
        echo MERAH . "[!] Cookie tidak valid / expired." . RESET . "\n";
        exit(1);
    }
} else {
    $dash = http_request(BASE_URL . "/dashboard", 'GET', [], [], $jar);
    if ($dash && is_logged_in($dash)) {
        echo HIJAU . "[+] Session aktif!" . RESET . "\n";
    } else {
        echo KUNING . "[*] Session tidak aktif, mencoba login..." . RESET . "\n";
        if (!login($jar, $login_data['email'], $login_data['password'], $login_data['apikey'])) {
            echo MERAH . "[!] Login gagal. Cek config." . RESET . "\n";
            exit(1);
        }
        $login_data['cookie'] = $jar->toString();
        save_config($login_data);
        echo HIJAU . "[+] Cookie disimpan." . RESET . "\n";
    }
}

// ─── COIN PICKER ───
$coins = get_coins($jar);
if (empty($coins)) { echo MERAH . "[!] Gagal ambil daftar coin." . RESET . "\n"; exit(1); }

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
    $emoji = $emoji_map[$coin] ?? '🪙';
    printf("%s(%2d) %s %s%-6s%s", PUTIH, $i, $emoji, HIJAU, strtoupper($coin), RESET);
    if ($i % 4 == 0 || $i == count($coins)) echo "\n";
    $i++;
}
echo "\n" . CYAN . "🎯 Pilih nomor coin: " . RESET;
$choice = trim(fgets(STDIN));
$idx = (int)$choice - 1;
$coin = $coins[$idx] ?? $coins[0];
echo HIJAU . "✅ Coin dipilih: " . strtoupper($coin) . RESET . "\n";

// ─── LOOP ───
$count = 0;
while (true) {
    $count++;
    echo "\n" . CYAN . "┌─[ ROUND $count ]" . RESET . "\n";

    $result = claim_faucet($jar, $coin, $login_data['apikey']);

    if ($result === "EXPIRED") {
        echo KUNING . "[*] Session expired. Mencoba refresh..." . RESET . "\n";
        if ($login_data['login_method'] === 'email') {
            if (login($jar, $login_data['email'], $login_data['password'], $login_data['apikey'])) {
                $login_data['cookie'] = $jar->toString();
                save_config($login_data);
                echo HIJAU . "[+] Session refresh sukses!" . RESET . "\n";
                continue;
            }
        } else {
            echo MERAH . "[!] Cookie expired. Update cookie di config." . RESET . "\n";
            break;
        }
    }

    if ($result === 'SHORTLINK') {
        echo MERAH . "[!] Shortlink terdeteksi! Bot berhenti." . RESET . "\n";
        echo KUNING . "[*] Selesaikan shortlink manual di browser." . RESET . "\n";
        echo PUTIH  . "Halaman: " . BASE_URL . "/links/" . $coin . RESET . "\n";
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
