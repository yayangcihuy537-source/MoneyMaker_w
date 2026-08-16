<?php
/**
 * TronBlow.site Auto Claim Bot v3.2
 * Fix: hapus curl_close, tambah banner sukses keren
 */

if (PHP_VERSION_ID < 80000) {
    echo "ERROR: PHP 8.0+ required.\n";
    exit(1);
}

// ==================== WARNA ANSI ====================
$green   = "\033[1;32m";
$cyan    = "\033[1;36m";
$yellow  = "\033[1;33m";
$magenta = "\033[1;35m";
$white   = "\033[1;37m";
$bold    = "\033[1m";
$reset   = "\033[0m";

// ==================== BANNER ====================
echo $green . "
╭──────────────────────────────────────────────────────────────╮
│                                                              │
│   ████████╗██████╗  ██████╗ ███╗   ██╗                      │
│   ╚══██╔══╝██╔══██╗██╔═══██╗████╗  ██║                      │
│      ██║   ██████╔╝██║   ██║██╔██╗ ██║                      │
│      ██║   ██╔══██╗██║   ██║██║╚██╗██║                      │
│      ██║   ██║  ██║╚██████╔╝██║ ╚████║                      │
│      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝                      │
│                                                              │
│              " . $cyan . "TRONBLOW // AUTO CLAIM" . $green . "                │
│                                                              │
│   " . $white . "┌─ SYSTEM ─────────────────────────────────────────┐" . $green . " │
│   " . $white . "│ " . $green . "● BOT STATUS   : ONLINE" . $white . "                      │" . $green . " │
│   " . $white . "│ " . $cyan . "⚡ CLAIM MODE   : AUTOMATIC" . $white . "                   │" . $green . " │
│   " . $white . "│ " . $yellow . "💰 REWARD      : 1000 SATOSHI" . $white . "                 │" . $green . " │
│   " . $white . "│ " . $magenta . "⏱ INTERVAL     : 60 SECONDS" . $white . "                 │" . $green . " │
│   " . $white . "└───────────────────────────────────────────────────┘" . $green . " │
│                                                              │
│             " . $yellow . ">>> INITIALIZING CLAIM ENGINE..." . $green . "             │
│                                                              │
╰──────────────────────────────────────────────────────────────╯
" . $reset . "\n";

// ==================== KONFIGURASI ====================
$CONFIG_FILE = __DIR__ . "/tronblow_config.json";
$COOKIE_FILE = __DIR__ . "/cookies_tronblow.txt";

// ==================== FUNGSI ====================
function log_msg(string $msg, string $type = "INFO"): void {
    $colors = [
        "SUCCESS" => "\033[32m",
        "ERROR"   => "\033[31m",
        "WARN"    => "\033[33m",
        "INPUT"   => "\033[36m",
        "DEBUG"   => "\033[35m",
        "INFO"    => "\033[0m"
    ];
    $color = $colors[$type] ?? "\033[0m";
    echo $color . "[" . date("H:i:s") . "] [$type] $msg\033[0m\n";
}

function read_line(string $prompt = ""): string {
    if ($prompt) echo $prompt;
    $handle = fopen("php://stdin", "r");
    $line = fgets($handle);
    fclose($handle);
    return trim($line);
}

function load_config(): ?array {
    global $CONFIG_FILE;
    if (file_exists($CONFIG_FILE)) {
        $json = file_get_contents($CONFIG_FILE);
        $config = json_decode($json, true);
        if (is_array($config) && !empty($config['email'])) {
            if (!isset($config['base_url'])) $config['base_url'] = 'https://tronblow.site';
            if (!isset($config['delay']))    $config['delay']    = 65;
            if (!isset($config['cookie']))   $config['cookie']   = '';
            return $config;
        }
    }
    return null;
}

function save_config(array $config): void {
    global $CONFIG_FILE;
    file_put_contents($CONFIG_FILE, json_encode($config, JSON_PRETTY_PRINT));
    log_msg("Config saved!", "SUCCESS");
}

function fetch_page(string $url, string $cookie_file): array {
    $ch = curl_init($url);
    $headers = [
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language: en-GB,en;q=0.9',
        'Sec-Ch-Ua: "Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile: ?1',
        'Sec-Ch-Ua-Platform: "Android"',
        'Sec-Fetch-Dest: document',
        'Sec-Fetch-Mode: navigate',
        'Sec-Fetch-Site: none',
        'Sec-Fetch-User: ?1',
        'Upgrade-Insecure-Requests: 1'
    ];
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_ENCODING => '',
        CURLOPT_USERAGENT => 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_COOKIEJAR => $cookie_file,
        CURLOPT_COOKIEFILE => $cookie_file,
    ]);

    $html = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error = curl_error($ch);
    // curl_close sudah tidak perlu di PHP 8.0+

    if ($error) {
        log_msg("cURL Error: $error", "ERROR");
        return ['html' => false, 'http_code' => 0];
    }
    if ($http_code !== 200 || empty($html)) {
        log_msg("HTTP $http_code", "ERROR");
        return ['html' => false, 'http_code' => $http_code];
    }
    return ['html' => $html, 'http_code' => $http_code];
}

function submit_claim(string $url, string $cookie_file, string $email, string $csrf_token, int $math_answer): array {
    $post_data = http_build_query([
        'action'      => 'claim',
        'csrf_token'  => $csrf_token,
        'website'     => '',
        'email'       => $email,
        'math_answer' => $math_answer
    ]);

    $ch = curl_init($url);
    $headers = [
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language: en-GB,en;q=0.9',
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: ' . $url,
        'Referer: ' . $url . '/',
        'Sec-Ch-Ua: "Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile: ?1',
        'Sec-Ch-Ua-Platform: "Android"',
        'Sec-Fetch-Dest: document',
        'Sec-Fetch-Mode: navigate',
        'Sec-Fetch-Site: same-origin',
        'Sec-Fetch-User: ?1',
        'Upgrade-Insecure-Requests: 1'
    ];
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => $post_data,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_ENCODING => '',
        CURLOPT_USERAGENT => 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_COOKIEJAR => $cookie_file,
        CURLOPT_COOKIEFILE => $cookie_file,
    ]);

    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    // curl_close sudah tidak perlu di PHP 8.0+

    return ['code' => $http_code, 'body' => (string)$response];
}

function extract_csrf_token(string $html): ?string {
    if (preg_match('/<input\s+type="hidden"\s+name="csrf_token"\s+value="([^"]+)"/i', $html, $m)) {
        return $m[1];
    }
    return null;
}

function extract_math_question(string $html): ?array {
    if (preg_match('/<div\s+class="captcha-q">(.*?)<\/div>/is', $html, $m)) {
        $text = strip_tags($m[1]);
        $text = html_entity_decode($text, ENT_QUOTES | ENT_HTML5, 'UTF-8');
        $text = trim($text);
    } else {
        $text = strip_tags($html);
        $text = html_entity_decode($text, ENT_QUOTES | ENT_HTML5, 'UTF-8');
    }

    $text = str_replace(['−', '–', '—', '‐', '‑', '‒', '&minus;'], '-', $text);
    $text = str_replace(['×', '&times;'], '*', $text);
    $text = str_replace(['÷', '&divide;'], '/', $text);

    if (preg_match('/what\s+is\s+(\d+)\s*([+\-*\/])\s*(\d+)\s*=\s*\?/i', $text, $m)) {
        return ['q1' => (int)$m[1], 'op' => $m[2], 'q2' => (int)$m[3]];
    }
    if (preg_match('/(\d+)\s*([+\-*\/])\s*(\d+)\s*=\s*\?/i', $text, $m)) {
        return ['q1' => (int)$m[1], 'op' => $m[2], 'q2' => (int)$m[3]];
    }
    if (preg_match('/(\d+)\s*([+\-*\/])\s*(\d+)\s*=/i', $text, $m)) {
        return ['q1' => (int)$m[1], 'op' => $m[2], 'q2' => (int)$m[3]];
    }
    return null;
}

function solve_math(array $math): int {
    $n1 = $math['q1'];
    $n2 = $math['q2'];
    switch ($math['op']) {
        case '+': return $n1 + $n2;
        case '-': return $n1 - $n2;
        case '*': return $n1 * $n2;
        case '/': return $n2 != 0 ? (int)($n1 / $n2) : 0;
        default: return 0;
    }
}

function extract_endAt(string $html): ?int {
    if (preg_match('/var\s+endAt\s*=\s*(\d+)\s*\*\s*1000/', $html, $m)) {
        return (int)($m[1] * 1000);
    }
    if (preg_match('/endAt\s*=\s*(\d+)\s*\*\s*1000/', $html, $m)) {
        return (int)($m[1] * 1000);
    }
    if (preg_match('/endAt\s*=\s*(\d+)\s*;?/', $html, $m)) {
        return (int)$m[1];
    }
    return null;
}

function check_response(string $html): array {
    $lower = strtolower($html);
    $patterns = [
        'success' => ['success','claimed','reward','sent','received','balance','congratulations'],
        'wait'    => ['wait','countdown','timer','please wait','try again later','time remaining'],
        'wrong'   => ['wrong','incorrect','invalid','error','failed','captcha','try again'],
        'already' => ['already','recently','one claim','per day','limit','maximum'],
        'banned'  => ['banned','blocked','suspicious','bot detected','vpn','proxy']
    ];
    foreach ($patterns as $status => $keywords) {
        foreach ($keywords as $kw) {
            if (strpos($lower, $kw) !== false) {
                return ['status' => $status, 'msg' => ucfirst($status) . " (keyword: '$kw')"];
            }
        }
    }
    return ['status' => 'unknown', 'msg' => 'Unclear response'];
}

function countdown_seconds(int $seconds): void {
    global $yellow, $reset, $green;
    for ($i = $seconds; $i > 0; $i--) {
        echo "\r" . $yellow . "[" . date("H:i:s") . "] [WAIT] Next claim in {$i}s..." . $reset;
        sleep(1);
    }
    echo "\r" . $green . "[" . date("H:i:s") . "] [INFO] Claiming now!          " . $reset . "\n";
}

// ==================== BANNER SUKSES KEREN ====================
function print_success_banner(string $email, string $reward = "1000 SATOSHI TRX"): void {
    global $green, $cyan, $yellow, $white, $reset, $bold;

    // Rapikan email (maks 30 karakter)
    $email_short = strlen($email) > 30 ? substr($email, 0, 27) . '...' : $email;
    $email_padded = str_pad($email_short, 30);
    $reward_padded = str_pad($reward, 30);

    echo "\n" . $green . $bold .
         "╭──────────────────────────────────────────────────────────╮\n" .
         "│                                                          │\n" .
         "│              ✓ CLAIM COMPLETED                           │\n" .
         "│                                                          │\n" .
         "│   STATUS   : " . $white . "SUCCESS" . $green . "                                │\n" .
         "│   REWARD   : " . $yellow . $reward_padded . $green . "                    │\n" .
         "│   ACCOUNT  : " . $white . $email_padded . $green . "                    │\n" .
         "│                                                          │\n" .
         "│              " . $cyan . "WAITING FOR NEXT CYCLE..." . $green . "              │\n" .
         "│                                                          │\n" .
         "╰──────────────────────────────────────────────────────────╯" .
         $reset . "\n";
}

// ==================== INTERACTIVE SETUP ====================
function interactive_setup(): array {
    global $green, $cyan, $reset;
    echo "\n" . $green . "╔════════════════════════════════════════════════╗" . $reset . "\n";
    echo $green . "║     TRONBLOW FAUCET BOT v3.2                  ║" . $reset . "\n";
    echo $green . "║     Developer: ScriptyXSouu                    ║" . $reset . "\n";
    echo $green . "╚════════════════════════════════════════════════╝" . $reset . "\n\n";

    $config = [];
    echo $cyan . "[1/2] Enter your FaucetPay email:" . $reset . "\n";
    $config['email'] = read_line("Email: ");
    while (empty($config['email']) || !filter_var($config['email'], FILTER_VALIDATE_EMAIL)) {
        log_msg("Invalid email!", "WARN");
        $config['email'] = read_line("Email: ");
    }

    $config['base_url'] = "https://tronblow.site";
    $config['delay'] = 65;
    $config['cookie'] = '';

    echo "\n" . $green . "Config saved!" . $reset . "\n";
    return $config;
}

// ==================== MAIN ====================
$config = load_config();
if ($config) {
    echo "\n";
    log_msg("Saved config found!", "SUCCESS");
    echo "  Email: {$config['email']}\n";
    echo "  URL:   {$config['base_url']}\n";
    echo "  Delay: {$config['delay']}s\n\n";
    $use = read_line("\033[36mUse saved? (y/n/reconfig): \033[0m");
    if ($use === 'n' || $use === 'reconfig') {
        $config = interactive_setup();
    }
} else {
    $config = interactive_setup();
}

if (empty($config['email']) || empty($config['base_url'])) {
    log_msg("Invalid configuration!", "ERROR");
    exit(1);
}
if (!isset($config['delay'])) $config['delay'] = 65;
if (!isset($config['cookie'])) $config['cookie'] = '';

if (!file_exists($COOKIE_FILE)) {
    touch($COOKIE_FILE);
}

echo "\n┌────────────────────────────────────────┐\n";
echo "│         CURRENT CONFIGURATION          │\n";
echo "├────────────────────────────────────────┤\n";
echo "│ Email: " . str_pad(substr($config['email'], 0, 25), 26) . "│\n";
echo "│ URL:   " . str_pad($config['base_url'], 26) . "│\n";
echo "│ Delay: " . str_pad($config['delay'] . "s", 26) . "│\n";
echo "└────────────────────────────────────────┘\n\n";

log_msg("=== BOT STARTED ===", "SUCCESS");
log_msg("Press Ctrl+C to stop", "WARN");
echo "\n";

$cycle = 0;
while (true) {
    $cycle++;
    log_msg("========== CYCLE #$cycle ==========", "INFO");

    $result = fetch_page($config['base_url'], $COOKIE_FILE);
    if (!$result['html']) {
        log_msg("Failed to fetch page. Retry in 30s...", "ERROR");
        countdown_seconds(30);
        continue;
    }
    $html = $result['html'];

    $lower = strtolower($html);
    if (strpos($lower, 'cf-browser-verification') !== false ||
        strpos($lower, 'challenge-platform') !== false ||
        strpos($lower, 'just a moment') !== false) {
        log_msg("Cloudflare challenge detected! Clearing cookies and retrying...", "WARN");
        unlink($COOKIE_FILE);
        touch($COOKIE_FILE);
        countdown_seconds(60);
        continue;
    }

    $csrf = extract_csrf_token($html);
    if (!$csrf) {
        log_msg("CSRF token not found! Retry in 30s...", "ERROR");
        countdown_seconds(30);
        continue;
    }
    log_msg("CSRF: " . substr($csrf, 0, 10) . "...", "DEBUG");

    $math = extract_math_question($html);
    if (!$math) {
        log_msg("Could not extract math question. Retry in 30s...", "ERROR");
        countdown_seconds(30);
        continue;
    }
    $answer = solve_math($math);
    log_msg("Math: {$math['q1']} {$math['op']} {$math['q2']} = $answer", "SUCCESS");

    $submit = submit_claim($config['base_url'], $COOKIE_FILE, $config['email'], $csrf, $answer);
    log_msg("HTTP Status: {$submit['code']}", "INFO");

    $status = check_response($submit['body']);
    $wait_seconds = $config['delay'];

    switch ($status['status']) {
        case 'success':
            // Tampilkan banner keren, hilangkan log sukses yang berisik
            print_success_banner($config['email']);
            $endAt = extract_endAt($submit['body']);
            if ($endAt) {
                $now = time() * 1000;
                $wait_ms = $endAt - $now;
                if ($wait_ms > 0) $wait_seconds = (int)ceil($wait_ms / 1000);
            }
            break;
        case 'wait':
        case 'already':
            log_msg("⏳ Cooldown active. Waiting for server timer.", "WARN");
            $endAt = extract_endAt($submit['body']);
            if ($endAt) {
                $now = time() * 1000;
                $wait_ms = $endAt - $now;
                if ($wait_ms > 0) $wait_seconds = (int)ceil($wait_ms / 1000);
            }
            break;
        case 'wrong':
            log_msg("❌ Math answer wrong! Retrying with new page...", "ERROR");
            countdown_seconds(10);
            continue 2;
        case 'banned':
            log_msg("🚫 ACCOUNT BANNED! Exiting...", "ERROR");
            exit(1);
        default:
            log_msg("❓ Unknown response: {$status['msg']}", "WARN");
            $endAt = extract_endAt($submit['body']);
            if ($endAt) {
                $now = time() * 1000;
                $wait_ms = $endAt - $now;
                if ($wait_ms > 0) $wait_seconds = (int)ceil($wait_ms / 1000);
            }
    }

    if ($wait_seconds > 0) {
        countdown_seconds($wait_seconds);
    } else {
        log_msg("No timer found, using default delay {$config['delay']}s", "WARN");
        countdown_seconds($config['delay']);
    }
}
