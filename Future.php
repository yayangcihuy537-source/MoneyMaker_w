<?php
// ============================================================
// CRYPTOFUTURE AUTO BOT - VERIFICATION CHECK FIXED
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
define('DIM', "\033[2m");

// ========== KONFIGURASI ==========
define('BASE_URL', 'https://cryptofuture.co.in');
define('CONFIG_FILE', 'config_cf.json');
define('MAX_FAILURES', 10);
define('CLAIM_COOLDOWN', 60);

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

// ========== UI ==========
function clear_screen() { system('clear'); }

function box_top($title = '') {
    $len = 58;
    $pad = ($len - strlen($title)) / 2;
    $pad_l = floor($pad);
    $pad_r = ceil($pad);
    return CYAN . "╔" . str_repeat("═", $len) . "╗" . RESET . "\n" .
           CYAN . "║" . str_repeat(" ", $pad_l) . BOLD . KUNING . $title . RESET . str_repeat(" ", $pad_r) . CYAN . "║" . RESET . "\n" .
           CYAN . "╠" . str_repeat("═", $len) . "╣" . RESET;
}

function box_bottom() {
    return CYAN . "╚" . str_repeat("═", 58) . "╝" . RESET;
}

function box_line($left, $right = '') {
    $len = 58;
    $left_len = strlen(preg_replace('/\x1b\[[0-9;]*m/', '', $left));
    $right_len = strlen(preg_replace('/\x1b\[[0-9;]*m/', '', $right));
    $pad = $len - $left_len - $right_len;
    if ($pad < 0) $pad = 0;
    return CYAN . "║" . RESET . " " . $left . str_repeat(" ", $pad) . $right . CYAN . "║" . RESET;
}

function print_banner() {
    clear_screen();
    echo box_top(" CRYPTOFUTURE AUTO BOT ") . "\n";
    echo box_line("  " . CYAN . "▪ Mode     : " . PUTIH . "Auto Claim") . "\n";
    echo box_line("  " . CYAN . "▪ Cooldown : " . PUTIH . CLAIM_COOLDOWN . "s") . "\n";
    echo box_line("  " . CYAN . "▪ Max Fail : " . PUTIH . MAX_FAILURES) . "\n";
    echo box_bottom() . "\n\n";
}

function print_status($attempt, $failures, $total_claimed, $balance = null) {
    echo box_top(" SESSION STATUS ") . "\n";
    echo box_line("  " . CYAN . "Status   : " . HIJAU . "✓ ONLINE") . "\n";
    $bal = ($balance !== null) ? number_format($balance, 0) . " Coins" : "Unknown";
    echo box_line("  " . CYAN . "Balance  : " . PUTIH . $bal) . "\n";
    echo box_line("  " . CYAN . "Attempts : " . PUTIH . $attempt) . "\n";
    $fail_color = ($failures >= MAX_FAILURES) ? MERAH : ($failures > 0 ? KUNING : PUTIH);
    echo box_line("  " . CYAN . "Failures : " . $fail_color . $failures . " / " . MAX_FAILURES) . "\n";
    echo box_line("  " . CYAN . "Claimed  : " . HIJAU . "+" . number_format($total_claimed, 0) . " Coins") . "\n";
    echo box_bottom() . "\n";
}

function print_final($total_claimed, $final_balance, $attempts, $failures, $reason = 'max_failures') {
    clear_screen();
    echo box_top(" EXECUTION FINISHED ") . "\n";
    $reason_text = ($reason == 'max_failures') ? "Max failures reached" : "Manually stopped";
    echo box_line("  " . CYAN . "Status     : " . MERAH . "STOPPED (" . $reason_text . ")") . "\n";
    echo box_line("  " . CYAN . "Attempts   : " . PUTIH . $attempts) . "\n";
    echo box_line("  " . CYAN . "Failures   : " . MERAH . $failures . " / " . MAX_FAILURES) . "\n";
    echo box_line("  " . CYAN . "Claimed    : " . HIJAU . "+" . number_format($total_claimed, 0) . " Coins") . "\n";
    echo box_line("  " . CYAN . "Balance    : " . PUTIH . number_format($final_balance, 0) . " Coins") . "\n";
    echo box_bottom() . "\n";
}

function timer($seconds, $prefix = "⏳ Waiting") {
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
            echo "\r" . PUTIH . $prefix . HIJAU . " $time_str " . PUTIH . $spinner . "   ";
            usleep(100000);
            $current = ($current + 1) % $frame_count;
            if ((microtime(true) - $start) >= 1) break;
        }
        $wait--;
    }
    echo "\r" . str_repeat(" ", 60) . "\r";
}

// ========== HTTP (with effective URL) ==========
function http_request($url, $method = 'GET', $data = [], $headers = [], CookieJar &$jar = null, &$effective_url = null) {
    if ($jar === null) $jar = new CookieJar();
    
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
    ];
    
    $cookie_str = $jar->toString();
    if (!empty($cookie_str)) $options[CURLOPT_COOKIE] = $cookie_str;
    
    if (strtoupper($method) === 'POST') {
        $options[CURLOPT_POST] = true;
        $options[CURLOPT_POSTFIELDS] = http_build_query($data);
    }
    
    if (!empty($headers)) $options[CURLOPT_HTTPHEADER] = $headers;
    
    curl_setopt_array($ch, $options);
    $response = curl_exec($ch);
    
    if ($response === false) {
        curl_close($ch);
        return null;
    }
    
    $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $body = substr($response, $header_size);
    $header = substr($response, 0, $header_size);
    
    $effective_url = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);
    
    $jar->parseSetCookie($header);
    
    curl_close($ch);
    return $body;
}

// ========== LOGIN ==========
function do_login($jar, $email, $device_token = null) {
    if (!$device_token) {
        $device_token = 'dev_' . bin2hex(random_bytes(8)) . time();
    }
    
    $home = http_request(BASE_URL . '/', 'GET', [], [], $jar);
    if (!$home) return null;
    
    preg_match('/name="csrf_token_name"\s+value="([^"]+)"/', $home, $m);
    $csrf = isset($m[1]) ? $m[1] : '';
    if (empty($csrf)) $csrf = $jar->get('csrf_cookie_name');
    if (empty($csrf)) return null;
    
    $data = [
        'wallet' => $email,
        'csrf_token_name' => $csrf,
        'device_token' => $device_token
    ];
    
    $result = http_request(BASE_URL . '/auth/login', 'POST', $data, [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: ' . BASE_URL,
        'Referer: ' . BASE_URL . '/',
    ], $jar);
    
    if (!$result) return null;
    
    $dash = http_request(BASE_URL . '/dashboard', 'GET', [], [], $jar);
    if ($dash && (strpos($dash, 'Dashboard') !== false || strpos($dash, 'Welcome') !== false)) {
        return true;
    }
    return null;
}

// ========== EARN PAGE (with URL check) ==========
function get_earn_page($jar) {
    $effective_url = null;
    $html = http_request(BASE_URL . '/earn', 'GET', [], [
        'Referer: ' . BASE_URL . '/',
    ], $jar, $effective_url);
    
    if (!$html) {
        file_put_contents('earn_error.txt', 'Empty response');
        return null;
    }
    
    // Save debug
    file_put_contents('earn_debug.html', $html);
    file_put_contents('earn_effective_url.txt', $effective_url);
    
    // Check if we landed on account page (verification required)
    if (strpos($effective_url, '/account') !== false) {
        return 'VERIFY';
    }
    
    // Also check content for "Not Verified" or "Verification Required"
    if (strpos($html, 'Not Verified') !== false || strpos($html, 'Verification Required') !== false) {
        return 'VERIFY';
    }
    
    // Check if we are logged in (if page contains login form, session expired)
    if (strpos($html, 'Login &amp; Start Claiming') !== false || (strpos($html, 'login') !== false && strlen($html) < 2000)) {
        return 'EXPIRED';
    }
    
    // Extract tokens
    $csrf = $token = $earn_ticket = $wallet = '';
    
    preg_match('/name="csrf_token_name"\s+value="([^"]+)"/', $html, $m);
    $csrf = isset($m[1]) ? $m[1] : '';
    
    preg_match('/name="token"\s+value="([^"]+)"/', $html, $m);
    $token = isset($m[1]) ? $m[1] : '';
    
    preg_match('/name="earn_ticket"\s+value="([^"]+)"/', $html, $m);
    $earn_ticket = isset($m[1]) ? $m[1] : '';
    
    preg_match('/name="wallet"\s+value="([^"]+)"/', $html, $m);
    $wallet = isset($m[1]) ? $m[1] : '';
    
    if (empty($csrf) || empty($token) || empty($earn_ticket)) {
        file_put_contents('tokens_missing.txt', "csrf=$csrf, token=$token, earn_ticket=$earn_ticket");
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

// ========== CLAIM ==========
function do_claim($jar, $faucet_data) {
    $csrf = $faucet_data['csrf'];
    $token = $faucet_data['token'];
    $earn_ticket = $faucet_data['earn_ticket'];
    $wallet = $faucet_data['wallet'];
    if (empty($wallet)) $wallet = 'garapanfaucetcrypto@gmail.com';
    
    $fp_hash = generate_fp_hash();
    $smart_token = generate_smart_token();
    
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
        'Referer: ' . BASE_URL . '/',
    ], $jar);
    
    if (!$result) return false;
    
    file_put_contents('claim_debug.html', $result);
    
    if (strpos($result, 'Success!') !== false || strpos($result, '✅') !== false) {
        $balance = extract_balance($result);
        $reward = extract_reward($result);
        if ($balance === null) {
            $balance = get_balance_from_dashboard($jar);
        }
        return ['success' => true, 'reward' => $reward, 'balance' => $balance];
    }
    
    if (preg_match('/Next claim available in:.*?(\d+)m.*?(\d+)s/', $result, $m)) {
        $timer = (int)$m[1] * 60 + (int)$m[2];
        return ['success' => false, 'timer' => $timer];
    }
    if (preg_match('/Next claim available in:.*?(\d+)s/', $result, $m)) {
        return ['success' => false, 'timer' => (int)$m[1]];
    }
    
    return false;
}

// ========== HELPERS ==========
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
    $ua = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36';
    $raw = 'fp-' . $ua . '384832';
    return hash('sha256', $raw);
}

function extract_balance($html) {
    $dom = new DOMDocument();
    @$dom->loadHTML($html);
    $xpath = new DOMXPath($dom);
    $nodes = $xpath->query("//*[contains(@class, 'balance-amount')]");
    if ($nodes->length > 0) {
        $text = trim($nodes->item(0)->textContent);
        if (preg_match('/([\d,]+)/', $text, $m)) {
            return (int) str_replace(',', '', $m[1]);
        }
    }
    if (preg_match_all('/(\d{2,})\s*Coins?/i', $html, $matches)) {
        $candidates = array_map('intval', $matches[1]);
        if (!empty($candidates)) return max($candidates);
    }
    return null;
}

function extract_reward($html) {
    if (preg_match('/Success!?\s*(\d+)\s*Coins?/i', $html, $m)) {
        return (int)$m[1];
    }
    if (preg_match('/has been added.*?(\d+)\s*Coins?/i', $html, $m)) {
        return (int)$m[1];
    }
    return 10;
}

function get_balance_from_dashboard($jar) {
    $html = http_request(BASE_URL . '/dashboard', 'GET', [], [], $jar);
    if ($html) return extract_balance($html);
    return null;
}

// ========== MAIN ==========
print_banner();

echo box_top(" SETUP ") . "\n";
echo box_line("  " . PUTIH . "Masukkan email FaucetPay") . "\n";
echo box_bottom() . "\n\n";
echo PUTIH . "Email: " . KUNING;
$email = trim(fgets(STDIN));
if (empty($email)) {
    echo MERAH . "\n[!] Email tidak boleh kosong.\n" . RESET;
    exit(1);
}

$device_token = '';
if (file_exists(CONFIG_FILE)) {
    $config = json_decode(file_get_contents(CONFIG_FILE), true);
    if ($config && isset($config['device_token'])) {
        $device_token = $config['device_token'];
    }
}
if (empty($device_token)) {
    $device_token = 'dev_' . bin2hex(random_bytes(8)) . time();
}

$jar = new CookieJar();

print_banner();
echo box_top(" LOGIN ") . "\n";
echo box_line("  " . CYAN . "⏳ Logging in as " . PUTIH . $email) . "\n";
echo box_bottom() . "\n";

if (!do_login($jar, $email, $device_token)) {
    echo box_top(" ERROR ") . "\n";
    echo box_line("  " . MERAH . "✗ Login failed! Check email or device token.") . "\n";
    echo box_bottom() . "\n";
    exit(1);
}

echo box_top(" LOGIN ") . "\n";
echo box_line("  " . HIJAU . "✓ Login successful!") . "\n";
echo box_bottom() . "\n";

$config = ['email' => $email, 'device_token' => $device_token];
file_put_contents(CONFIG_FILE, json_encode($config, JSON_PRETTY_PRINT));

sleep(1);

$attempts = 0;
$failures = 0;
$total_claimed = 0;
$balance = null;

while (true) {
    $attempts++;
    print_banner();
    print_status($attempts, $failures, $total_claimed, $balance);
    
    echo box_top(" CLAIMING ") . "\n";
    echo box_line("  " . CYAN . "⏳ Fetching earn page...") . "\n";
    echo box_bottom() . "\n";
    
    $faucet_data = get_earn_page($jar);
    if ($faucet_data === 'VERIFY') {
        echo box_top(" VERIFICATION REQUIRED ") . "\n";
        echo box_line("  " . MERAH . "✗ Your account is NOT VERIFIED.") . "\n";
        echo box_line("  " . KUNING . "⚠ Please verify via Telegram:") . "\n";
        echo box_line("  " . PUTIH . "https://t.me/cryptofuturefaucet_bot?start=verify_1101") . "\n";
        echo box_line("  " . KUNING . "After verification, run the script again.") . "\n";
        echo box_bottom() . "\n";
        exit(1);
    }
    
    if ($faucet_data === 'EXPIRED') {
        echo box_top(" SESSION EXPIRED ") . "\n";
        echo box_line("  " . MERAH . "✗ Session expired, re-login...") . "\n";
        echo box_bottom() . "\n";
        if (!do_login($jar, $email, $device_token)) {
            echo box_top(" ERROR ") . "\n";
            echo box_line("  " . MERAH . "✗ Re-login failed. Exiting.") . "\n";
            echo box_bottom() . "\n";
            break;
        }
        continue;
    }
    
    if (!$faucet_data) {
        echo box_top(" ERROR ") . "\n";
        echo box_line("  " . MERAH . "✗ Failed to get earn page. Check earn_debug.html") . "\n";
        echo box_bottom() . "\n";
        $failures++;
        if ($failures >= MAX_FAILURES) {
            print_final($total_claimed, ($balance !== null) ? $balance : 0, $attempts, $failures);
            echo PUTIH . "Press Enter to exit...";
            fgets(STDIN);
            exit(0);
        }
        timer(5, "🔄 Retry in");
        continue;
    }
    
    $result = do_claim($jar, $faucet_data);
    
    if ($result === false) {
        echo box_top(" CLAIM RESULT ") . "\n";
        echo box_line("  " . MERAH . "✗ FAILED (unknown)") . "\n";
        echo box_bottom() . "\n";
        $failures++;
        if ($failures >= MAX_FAILURES) {
            print_final($total_claimed, ($balance !== null) ? $balance : 0, $attempts, $failures);
            echo PUTIH . "Press Enter to exit...";
            fgets(STDIN);
            exit(0);
        }
        timer(5, "🔄 Retry in");
        continue;
    }
    
    if ($result['success']) {
        $reward = $result['reward'];
        if ($result['balance'] !== null) {
            $balance = $result['balance'];
        } else {
            $dash_balance = get_balance_from_dashboard($jar);
            if ($dash_balance !== null) $balance = $dash_balance;
            else $balance = ($balance !== null) ? $balance + $reward : $reward;
        }
        $total_claimed += $reward;
        $failures = 0;
        
        print_banner();
        print_status($attempts, $failures, $total_claimed, $balance);
        echo box_top(" CLAIM RESULT ") . "\n";
        echo box_line("  " . HIJAU . "✓ SUCCESS" . "  +" . number_format($reward, 0) . " Coins") . "\n";
        if ($balance !== null) {
            echo box_line("  " . CYAN . "Balance : " . PUTIH . number_format($balance, 0) . " Coins") . "\n";
        }
        echo box_line("  " . KUNING . "⏳ Next claim in " . CLAIM_COOLDOWN . "s") . "\n";
        echo box_bottom() . "\n";
        timer(CLAIM_COOLDOWN, "🔄 Next claim in");
        
    } else {
        $timer_val = isset($result['timer']) ? $result['timer'] : 0;
        if ($timer_val > 0) {
            echo box_top(" COOLDOWN ") . "\n";
            echo box_line("  " . KUNING . "⏳ Cooldown " . $timer_val . " seconds") . "\n";
            echo box_bottom() . "\n";
            timer($timer_val + 2, "⏳ Cooldown");
        } else {
            echo box_top(" CLAIM RESULT ") . "\n";
            echo box_line("  " . MERAH . "✗ FAILED") . "\n";
            echo box_bottom() . "\n";
            $failures++;
            if ($failures >= MAX_FAILURES) {
                print_final($total_claimed, ($balance !== null) ? $balance : 0, $attempts, $failures);
                echo PUTIH . "Press Enter to exit...";
                fgets(STDIN);
                exit(0);
            }
            timer(5, "🔄 Retry in");
        }
    }
}

print_final($total_claimed, ($balance !== null) ? $balance : 0, $attempts, $failures);
echo PUTIH . "Press Enter to exit...";
fgets(STDIN);
exit(0);
