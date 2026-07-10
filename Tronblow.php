<?php
/**
 * TronBlow.site Faucet Bot
 * v2.1 - No Cookie Input
 * Developer: Moneymaker_w
 */

if (PHP_VERSION_ID < 80000) {
    echo "ERROR: PHP 8.0+ required. You have " . PHP_VERSION . "\n";
    exit(1);
}

// ==================== BANNER ====================
$cyan   = "\033[1;36m";
$green  = "\033[1;32m";
$red    = "\033[1;31m";
$yellow = "\033[1;33m";
$magenta= "\033[1;35m";
$white  = "\033[1;37m";
$reset  = "\033[0m";

echo $cyan . "
████████╗██████╗  ██████╗ ███╗   ██╗██████╗ ██╗      ██████╗ ██╗    ██╗
╚══██╔══╝██╔══██╗██╔═══██╗████╗  ██║██╔══██╗██║     ██╔═══██╗██║    ██║
   ██║   ██████╔╝██║   ██║██╔██╗ ██║██████╔╝██║     ██║   ██║██║ █╗ ██║
   ██║   ██╔══██╗██║   ██║██║╚██╗██║██╔══██╗██║     ██║   ██║██║███╗██║
   ██║   ██║  ██║╚██████╔╝██║ ╚████║██████╔╝███████╗╚██████╔╝╚███╔███╔╝
   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚══════╝ ╚═════╝  ╚══╝╚══╝
" . $reset;

echo $yellow . "
╔══════════════════════════════════════════════════════════════╗
║            TRONBLOW AUTO CLAIM BOT                          ║
╠══════════════════════════════════════════════════════════════╣
║  Developer : " . $green . "Moneymaker_w" . $yellow . "                           ║
║  Version   : 2.1                                             ║
║  Language  : PHP CLI                                         ║
║  Status    : " . $green . "ACTIVE" . $yellow . "                                          ║
╚══════════════════════════════════════════════════════════════╝
" . $reset . "\n";

// ==================== KONFIGURASI ====================
$CONFIG_FILE = __DIR__ . "/tronblow_config.json";
$LAST_RESPONSE_FILE = __DIR__ . "/last_response.html";
$DEBUG_HTML_FILE = __DIR__ . "/debug_tronblow.html";

// ==================== FUNGSI ====================
function log_msg(string $msg, string $type = "INFO"): void {
    $colors = [
        "SUCCESS" => "\033[32m", 
        "ERROR" => "\033[31m", 
        "WARN" => "\033[33m",
        "INPUT" => "\033[36m", 
        "DEBUG" => "\033[35m", 
        "INFO" => "\033[0m"
    ];
    $color = $colors[$type] ?? "\033[0m";
    echo $color . "[" . date("H:i:s") . "] [$type] $msg\033[0m\n";
}

function read_line(string $prompt = ""): string {
    if (!empty($prompt)) echo $prompt;
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

function get_page(string $url, string $cookie_string = ''): string|false {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_ENCODING => '',
        CURLOPT_USERAGENT => 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        CURLOPT_HTTPHEADER => [
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
        ],
        CURLOPT_COOKIE => $cookie_string
    ]);

    $html = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error = curl_error($ch);

    if ($error) {
        log_msg("cURL Error: $error", "ERROR");
        return false;
    }
    if ($http_code !== 200 || empty($html)) {
        log_msg("HTTP $http_code", "ERROR");
        return false;
    }

    return $html;
}

function submit_claim(string $url, string $cookie_string, string $email, array $math_data): array {
    $post_data = http_build_query([
        'action' => 'claim',
        'math_q1' => $math_data['q1'],
        'math_q2' => $math_data['q2'],
        'math_op' => $math_data['op'],
        'email' => $email,
        'math_answer' => $math_data['answer']
    ]);

    $ch = curl_init($url);
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
        CURLOPT_HTTPHEADER => [
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
        ],
        CURLOPT_COOKIE => $cookie_string
    ]);

    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);

    return ['code' => $http_code, 'body' => (string)$response];
}

function normalize_math_text(string $html): string {
    $html = preg_replace('/<script\b[^>]*>.*?<\/script>/is', '', $html);
    $html = preg_replace('/<style\b[^>]*>.*?<\/style>/is', '', $html);

    $text = strip_tags($html);
    $text = html_entity_decode($text, ENT_QUOTES | ENT_HTML5, 'UTF-8');

    $replacements = [
        '−' => '-', '–' => '-', '—' => '-', '‐' => '-', '‑' => '-', '‒' => '-',
        '&minus;' => '-', '&ndash;' => '-', '&mdash;' => '-',
        '×' => '*', '&times;' => '*', '÷' => '/', '&divide;' => '/',
    ];
    foreach ($replacements as $from => $to) {
        $text = str_replace($from, $to, $text);
    }

    $text = preg_replace('/\s+/u', ' ', $text);
    return trim($text);
}

function extract_math_problem(string $html): array|false {
    $text = normalize_math_text($html);

    $patterns = [
        'what_is_equal'    => '/what\s+is\s+(\d+)\s*([+\-*\/])\s*(\d+)\s*=\s*\?/i',
        'what_is'          => '/what\s+is\s+(\d+)\s*([+\-*\/])\s*(\d+)\s*\?/i',
        'number_op_number' => '/(\d+)\s*([+\-*\/])\s*(\d+)\s*=\s*\?/i',
        'equal_no_q'       => '/(\d+)\s*([+\-*\/])\s*(\d+)\s*=/i',
        'solve'            => '/solve[:\s]+(\d+)\s*([+\-*\/])\s*(\d+)/i',
        'math'             => '/math[:\s]+(\d+)\s*([+\-*\/])\s*(\d+)/i',
        'generic'          => '/(\d+)\s*([+\-*\/])\s*(\d+)/i',
    ];

    foreach ($patterns as $name => $pattern) {
        if (preg_match($pattern, $text, $matches)) {
            return solve_math($matches[1], $matches[2], $matches[3]);
        }
    }

    return false;
}

function solve_math(string $q1, string $op, string $q2): array {
    $n1 = (int)$q1; $n2 = (int)$q2;
    $answer = match($op) {
        '+' => $n1 + $n2, '-' => $n1 - $n2,
        '*' => $n1 * $n2, '/' => $n2 !== 0 ? $n1 / $n2 : 0,
        default => 0
    };
    return ['q1' => $q1, 'q2' => $q2, 'op' => $op, 'answer' => $answer];
}

function check_response(string $html): array {
    $lower = strtolower($html);
    $patterns = [
        'success' => ['success','claimed','reward','sent','received','balance','get reward','congratulations'],
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
    return ['status' => 'unknown', 'msg' => 'Response unclear'];
}

function countdown(int $seconds): void {
    global $cyan, $reset, $green, $yellow;
    for ($i = $seconds; $i > 0; $i--) {
        echo "\r" . $yellow . "[" . date("H:i:s") . "] [WAIT] Next claim in {$i}s..." . $reset;
        sleep(1);
    }
    echo "\r" . $green . "[" . date("H:i:s") . "] [INFO] Claiming now!          " . $reset . "\n";
}

// ==================== MAIN ====================
$config = load_config();
if ($config) {
    echo "\n";
    log_msg("Saved config found!", "SUCCESS");
    echo "  Email: {$config['email']}\n  URL:   {$config['base_url']}\n  Delay: {$config['delay']}s\n\n";
    $use = read_line("\033[36mUse saved? (y/n/reconfig): \033[0m");
    if ($use === 'n' || $use === 'reconfig') $config = interactive_setup();
} else {
    $config = interactive_setup();
}

if (empty($config['email']) || empty($config['base_url'])) {
    log_msg("Invalid configuration!", "ERROR");
    exit(1);
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

    log_msg("[1/3] Fetching page...", "INFO");
    $html = get_page($config['base_url'], $config['cookie'] ?? '');
    if (!$html) { 
        log_msg("Failed to fetch page. Retry in 30s...", "ERROR");
        countdown(30); 
        continue; 
    }

    if (strlen($html) < 1000) {
        log_msg("Page too short (" . strlen($html) . " chars)", "WARN");
        countdown(30); 
        continue;
    }

    $lower_html = strtolower($html);
    if (strpos($lower_html, 'cf-browser-verification') !== false ||
        strpos($lower_html, 'challenge-platform') !== false ||
        strpos($lower_html, 'just a moment') !== false) {
        log_msg("Cloudflare challenge! Cookie expired.", "ERROR");
        countdown(60); 
        continue;
    }

    log_msg("[2/3] Solving math problem...", "INFO");
    $math = extract_math_problem($html);
    if (!$math) {
        log_msg("Could not find math. Waiting...", "ERROR");
        countdown($config['delay']);
        continue;
    }

    log_msg("Math: {$math['q1']} {$math['op']} {$math['q2']} = {$math['answer']}", "SUCCESS");

    log_msg("[3/3] Submitting claim...", "INFO");
    $result = submit_claim($config['base_url'], $config['cookie'] ?? '', $config['email'], $math);

    log_msg("HTTP Status: {$result['code']}", "INFO");

    $status = check_response($result['body']);
    switch ($status['status']) {
        case 'success': 
            log_msg("✅ CLAIM SUCCESS! Reward added to balance.", "SUCCESS"); 
            break;
        case 'wait': 
            log_msg("⏳ Please wait before next claim.", "WARN"); 
            break;
        case 'already': 
            log_msg("⚠️ Already claimed recently. Try again later.", "WARN"); 
            break;
        case 'wrong': 
            log_msg("❌ Math answer wrong! Retrying...", "ERROR"); 
            break;
        case 'banned': 
            log_msg("🚫 ACCOUNT BANNED! Exiting...", "ERROR"); 
            exit(1);
        default: 
            log_msg("❓ Unknown response: {$status['msg']}", "WARN");
    }

    file_put_contents($LAST_RESPONSE_FILE, $result['body']);
    countdown($config['delay']);
}

function interactive_setup(): array {
    global $green, $cyan, $yellow, $reset;
    
    echo "\n" . $green . "╔════════════════════════════════════════════════╗" . $reset . "\n";
    echo $green . "║     TRONBLOW FAUCET BOT v2.1                  ║" . $reset . "\n";
    echo $green . "║     Developer: Moneymaker_w                    ║" . $reset . "\n";
    echo $green . "╚════════════════════════════════════════════════╝" . $reset . "\n\n";

    $config = [];
    echo $cyan . "[1/1] Enter your FaucetPay email:" . $reset . "\n";
    $config['email'] = read_line("Email: ");
    while (empty($config['email']) || !filter_var($config['email'], FILTER_VALIDATE_EMAIL)) {
        log_msg("Invalid email!", "WARN");
        $config['email'] = read_line("Email: ");
    }

    // Tidak ada input cookie lagi
    $config['cookie'] = ''; // kosongkan
    $config['base_url'] = "https://tronblow.site";
    $config['delay'] = 65;

    echo "\n" . $green . "Config saved! (Cookie not required)" . $reset . "\n";
    return $config;
}
