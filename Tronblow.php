#!/usr/bin/env php
<?php
/**
 * ═══════════════════════════════════════════════════════════════
 *  TRONBLOW.site Auto Claim Bot v4.1 (Clean UI Edition)
 *  - No animation, static box UI
 *  - Max Claim: 200/day
 *  - Health check: faucet masih bayar atau gak
 *  - Accurate parser: alert-success / alert-error
 *  - STOP kalau "insufficient funds"
 * ═══════════════════════════════════════════════════════════════
 */

if (PHP_VERSION_ID < 80000) {
    fwrite(STDERR, "ERROR: PHP 8.0+ required.\n");
    exit(1);
}

// ═══════════════════════════════════════════════════════════════
//  COLOR + BOX HELPERS
// ═══════════════════════════════════════════════════════════════
const RST = "\033[0m";
const BOLD = "\033[1m";
const DIM  = "\033[2m";
const RED  = "\033[38;5;196m";
const GRN  = "\033[38;5;46m";
const YEL  = "\033[38;5;226m";
const CYN  = "\033[38;5;51m";
const MAG  = "\033[38;5;201m";
const ORG  = "\033[38;5;208m";
const WHT  = "\033[38;5;15m";
const GRY  = "\033[38;5;240m";
const VIO  = "\033[38;5;141m";

function vlen(string $s): int {
    return mb_strlen(preg_replace('/\033\[[0-9;]*m/', '', $s));
}

function pad_to(string $s, int $w): string {
    $len = vlen($s);
    return $s . str_repeat(' ', max(0, $w - $len));
}

// ═══════════════════════════════════════════════════════════════
//  GLOBAL STATE (dipakai untuk render box)
// ═══════════════════════════════════════════════════════════════
$STATE = [
    'email'         => '-',
    'username'      => 'Unknown',
    'balance'       => 0,
    'currency'      => 'SAT',
    'claims'        => 0,
    'rewards'       => 0.0,
    'failures'      => 0,
    'max_failures'  => 5,
    'runtime_start' => time(),
    'max_runtime'   => 3 * 3600,   // 3 jam
    'logs'          => [],         // max 6 entry
    'faucet_status' => 'checking', // checking | ok | suspect | dead
    'last_payment'  => null,
    'daily_count'   => 0,
    'daily_limit'   => 200,
];

function state_log(string $msg, string $level = 'INFO'): void {
    global $STATE;
    $ts = date('H:i:s');
    $tag = '';
    switch (strtoupper($level)) {
        case 'OK':     $tag = GRN  . "◈ OK    " . RST; break;
        case 'ERR':    $tag = RED  . "◈ ERR   " . RST; break;
        case 'WARN':   $tag = YEL  . "◈ WARN  " . RST; break;
        case 'CLAIM':  $tag = MAG  . "⬢ CLAIM " . RST; break;
        case 'SOLVE':  $tag = CYN  . "⬢ SOLVER" . RST; break;
        case 'VERIFY': $tag = VIO  . "◈ VERIFY" . RST; break;
        case 'HEALTH': $tag = ORG  . "◈ HEALTH" . RST; break;
        case 'WAIT':   $tag = YEL  . "⬢ WAIT  " . RST; break;
        default:       $tag = GRY  . "◈ INFO  " . RST; break;
    }
    $STATE['logs'][] = GRY . "[{$ts}] " . RST . $tag . " " . WHT . $msg . RST;
    if (count($STATE['logs']) > 6) {
        array_shift($STATE['logs']);
    }
}

function fmt_duration(int $sec): string {
    $h = floor($sec / 3600);
    $m = floor(($sec % 3600) / 60);
    $s = $sec % 60;
    return sprintf('%02d:%02d:%02d', $h, $m, $s);
}

// ═══════════════════════════════════════════════════════════════
//  RENDER BOX
// ═══════════════════════════════════════════════════════════════
function render_box(): void {
    global $STATE;

    $W = 62;  // lebar dalam
    $bdr = CYN;
    $top    = $bdr . "╔" . str_repeat('═', $W) . "╗" . RST;
    $mid    = $bdr . "╠" . str_repeat('═', $W) . "╣" . RST;
    $bot    = $bdr . "╚" . str_repeat('═', $W) . "╝" . RST;
    $line = function(string $content) use ($bdr, $W) {
        return $bdr . "║" . RST . pad_to(" " . $content, $W) . $bdr . "║" . RST;
    };

    echo "\n";
    echo $top . "\n";
    echo $line(BOLD . WHT . "TRONBLOW AUTO CLAIM" . RST) . "\n";
    echo $line(DIM . "─────── SOUU ENGINE ───────" . RST) . "\n";
    echo $mid . "\n";

    // ── HEALTH ──
    $hs_label = '';
    $hs_color = GRY;
    switch ($STATE['faucet_status']) {
        case 'ok':       $hs_label = 'ONLINE';   $hs_color = GRN; break;
        case 'suspect':  $hs_label = 'SUSPECT';  $hs_color = YEL; break;
        case 'dead':     $hs_label = 'DEAD';     $hs_color = RED; break;
        default:         $hs_label = 'CHECKING'; $hs_color = GRY; break;
    }
    echo $line(VIO . "FAUCET" . RST) . "\n";
    echo $line("├─ Status     : " . $hs_color . $hs_label . RST) . "\n";
    if ($STATE['last_payment']) {
        $age = (int) floor((time() - $STATE['last_payment']) / 60);
        echo $line("├─ Last Pay   : " . DIM . $age . " min ago" . RST) . "\n";
    }
    echo $line("└─ Daily      : " . CYN . $STATE['daily_count'] . RST . " / " . $STATE['daily_limit']) . "\n";
    echo $mid . "\n";

    // ── ACCOUNT ──
    echo $line(VIO . "ACCOUNT" . RST) . "\n";
    echo $line("├─ User       : " . CYN . $STATE['username'] . RST) . "\n";
    echo $line("├─ Email      : " . $STATE['email']) . "\n";
    echo $line("└─ Balance    : " . YEL . $STATE['balance'] . " " . $STATE['currency'] . RST) . "\n";
    echo $mid . "\n";

    // ── SYSTEM ──
    $runtime = time() - $STATE['runtime_start'];
    echo $line(VIO . "SYSTEM" . RST) . "\n";
    echo $line("├─ Claims     : " . GRN . $STATE['claims'] . RST) . "\n";
    echo $line("├─ Rewards    : " . GRN . sprintf('+%.4f', $STATE['rewards']) . RST) . "\n";
    echo $line("├─ Failures   : " . RED . $STATE['failures'] . RST . " / " . $STATE['max_failures']) . "\n";
    echo $line("└─ Runtime    : " . CYN . fmt_duration($runtime) . RST . " / " . DIM . fmt_duration($STATE['max_runtime']) . RST) . "\n";
    echo $mid . "\n";

    // ── LOGS ──
    $logs = $STATE['logs'];
    if (empty($logs)) {
        echo $line(DIM . "─ no activity yet ─" . RST) . "\n";
    } else {
        foreach ($logs as $l) {
            echo $line($l) . "\n";
        }
    }
    echo $bot . "\n";

    // ── FOOTER ──
    echo "\n";
    echo "   " . GRN . "BOT RUNNING" . RST . " " . DIM . "•" . RST . " " . CYN . date('H:i:s') . RST . "\n";
    echo "   " . DIM . "By Power @SouuXso • TronBlow Edition" . RST . "\n\n";
}

function render_box_clear(): void {
    // Pindah kursor ke atas untuk redraw in-place
    // hitung tinggi box: 3 top + 6 header lines + 3 per section (health 4, account 4, system 5) + logs 7 + 3 bottom
    // Simple: hapus layar
    if (PHP_OS_FAMILY === 'Windows') {
        pclose(popen('cls', 'w'));
    } else {
        system('clear');
    }
    render_box();
}

// ═══════════════════════════════════════════════════════════════
//  CONFIG
// ═══════════════════════════════════════════════════════════════
$CONFIG_FILE  = __DIR__ . "/tronblow_config.json";
$COOKIE_FILE  = __DIR__ . "/cookies_tronblow.txt";
$COUNTER_FILE = __DIR__ . "/tronblow_counter.json";

const DAILY_LIMIT = 200;
const BASE_URL    = 'https://tronblow.site';
const USER_AGENT  = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36';

// ═══════════════════════════════════════════════════════════════
//  IO HELPERS
// ═══════════════════════════════════════════════════════════════
function read_line(string $prompt = ""): string {
    if ($prompt) echo $prompt;
    $line = fgets(STDIN);
    return trim((string) $line);
}

function load_config(): ?array {
    global $CONFIG_FILE;
    if (!file_exists($CONFIG_FILE)) return null;
    $json = @file_get_contents($CONFIG_FILE);
    $cfg  = json_decode((string) $json, true);
    if (is_array($cfg) && !empty($cfg['email'])) {
        $cfg['base_url'] = $cfg['base_url'] ?? BASE_URL;
        $cfg['delay']    = $cfg['delay']    ?? 65;
        $cfg['cookie']   = $cfg['cookie']   ?? '';
        return $cfg;
    }
    return null;
}

function save_config(array $cfg): void {
    global $CONFIG_FILE;
    @file_put_contents($CONFIG_FILE, json_encode($cfg, JSON_PRETTY_PRINT));
}

function load_counter(): array {
    global $COUNTER_FILE;
    $today = date('Y-m-d');
    if (file_exists($COUNTER_FILE)) {
        $d = json_decode((string) file_get_contents($COUNTER_FILE), true);
        if (is_array($d) && ($d['date'] ?? '') === $today) return $d;
    }
    return ['date' => $today, 'count' => 0];
}

function save_counter(array $c): void {
    global $COUNTER_FILE;
    @file_put_contents($COUNTER_FILE, json_encode($c, JSON_PRETTY_PRINT));
}

function increment_counter(): array {
    $c = load_counter();
    $c['count']++;
    save_counter($c);
    return $c;
}

// ═══════════════════════════════════════════════════════════════
//  HTTP
// ═══════════════════════════════════════════════════════════════
function fetch_page(string $url, string $cookie_file): array {
    $ch = curl_init($url);
    $headers = [
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language: en-GB,en;q=0.9',
        'Sec-Ch-Ua: "Chromium";v="127", "Not)A;Brand";v="99"',
        'Sec-Ch-Ua-Mobile: ?1',
        'Sec-Ch-Ua-Platform: "Android"',
        'Sec-Fetch-Dest: document',
        'Sec-Fetch-Mode: navigate',
        'Sec-Fetch-Site: none',
        'Upgrade-Insecure-Requests: 1',
    ];
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT        => 30,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_ENCODING       => '',
        CURLOPT_USERAGENT      => USER_AGENT,
        CURLOPT_HTTPHEADER     => $headers,
        CURLOPT_COOKIEJAR      => $cookie_file,
        CURLOPT_COOKIEFILE     => $cookie_file,
    ]);
    $html = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $err  = curl_error($ch);

    if ($err || $code !== 200 || empty($html)) {
        return ['html' => false, 'http_code' => $code];
    }
    return ['html' => $html, 'http_code' => $code];
}

function submit_claim(string $url, string $cookie_file, string $email, string $csrf, int $answer): array {
    $post = http_build_query([
        'action'      => 'claim',
        'csrf_token'  => $csrf,
        'website'     => '',
        'email'       => $email,
        'math_answer' => $answer,
    ]);

    $ch = curl_init($url);
    $headers = [
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
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
        'Upgrade-Insecure-Requests: 1',
    ];
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => $post,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT        => 30,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_ENCODING       => '',
        CURLOPT_USERAGENT      => USER_AGENT,
        CURLOPT_HTTPHEADER     => $headers,
        CURLOPT_COOKIEJAR      => $cookie_file,
        CURLOPT_COOKIEFILE     => $cookie_file,
    ]);
    $body = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    return ['code' => $code, 'body' => (string) $body];
}

// ═══════════════════════════════════════════════════════════════
//  PARSER
// ═══════════════════════════════════════════════════════════════
function extract_csrf_token(string $html): ?string {
    if (preg_match('/<input\s+type="hidden"\s+name="csrf_token"\s+value="([^"]+)"/i', $html, $m)) {
        return $m[1];
    }
    return null;
}

function extract_math_question(string $html): ?array {
    if (preg_match('/<div\s+class="captcha-q">(.*?)<\/div>/is', $html, $m)) {
        $text = strip_tags($m[1]);
    } else {
        $text = strip_tags($html);
    }
    $text = html_entity_decode($text, ENT_QUOTES | ENT_HTML5, 'UTF-8');
    $text = str_replace(['−','–','—','‐','‑','‒','&minus;'], '-', $text);
    $text = str_replace(['×','&times;'], '*', $text);
    $text = str_replace(['÷','&divide;'], '/', $text);

    if (preg_match('/what\s+is\s+(\d+)\s*([+\-*\/])\s*(\d+)\s*=\s*\?/i', $text, $m)) {
        return ['q1'=>(int)$m[1], 'op'=>$m[2], 'q2'=>(int)$m[3]];
    }
    if (preg_match('/(\d+)\s*([+\-*\/])\s*(\d+)\s*=\s*\?/i', $text, $m)) {
        return ['q1'=>(int)$m[1], 'op'=>$m[2], 'q2'=>(int)$m[3]];
    }
    if (preg_match('/(\d+)\s*([+\-*\/])\s*(\d+)\s*=/i', $text, $m)) {
        return ['q1'=>(int)$m[1], 'op'=>$m[2], 'q2'=>(int)$m[3]];
    }
    return null;
}

function solve_math(array $m): int {
    $a = $m['q1']; $b = $m['q2'];
    switch ($m['op']) {
        case '+': return $a + $b;
        case '-': return $a - $b;
        case '*': return $a * $b;
        case '/': return $b != 0 ? (int)($a / $b) : 0;
        default:  return 0;
    }
}

function extract_endAt(string $html): ?int {
    if (preg_match('/endAt\s*=\s*(\d+)\s*\*\s*1000/', $html, $m)) return (int)($m[1] * 1000);
    if (preg_match('/endAt\s*=\s*(\d+)\s*;?/', $html, $m))          return (int)$m[1];
    return null;
}

// ═══════════════════════════════════════════════════════════════
//  RESPONSE PARSER
// ═══════════════════════════════════════════════════════════════
function parse_alert_message(string $html): array {
    $out = ['success' => null, 'error' => null];

    if (preg_match('/<div[^>]*class="[^"]*alert-success[^"]*"[^>]*>(.*?)<\/div>/is', $html, $m)) {
        $out['success'] = trim(strip_tags($m[1]));
    }
    if (preg_match('/<div[^>]*class="[^"]*alert-error[^"]*"[^>]*>(.*?)<\/div>/is', $html, $m)) {
        $out['error'] = trim(strip_tags($m[1]));
    }
    if ($out['success'] === null && $out['error'] === null) {
        if (preg_match('/<div[^>]*class="[^"]*alert[^"]*"[^>]*>(.*?)<\/div>/is', $html, $m)) {
            $txt = trim(strip_tags($m[1]));
            $low = strtolower($txt);
            if (strpos($low, 'success') !== false || strpos($low, 'sent') !== false) {
                $out['success'] = $txt;
            } else {
                $out['error'] = $txt;
            }
        }
    }
    return $out;
}

function is_fatal_error(string $msg): bool {
    $s = strtolower($msg);
    $keys = [
        'insufficient fund', 'does not have sufficient', 'payment failed',
        'faucet is empty', 'out of funds', 'no funds', 'balance is empty',
        'not enough balance',
    ];
    foreach ($keys as $k) {
        if (strpos($s, $k) !== false) return true;
    }
    return false;
}

function check_faucet_health(string $html, int $max_age_min = 30): array {
    $out = ['ok' => true, 'last_payment' => null, 'age_min' => null, 'reason' => ''];
    if (preg_match_all('/(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})/', $html, $matches)) {
        $ts = array_map('strtotime', $matches[1]);
        sort($ts);
        $latest = end($ts);
        $out['last_payment'] = $latest;
        $age_sec = time() - $latest;
        $age_min = (int) floor($age_sec / 60);
        $out['age_min'] = $age_min;
        if ($age_min > $max_age_min) {
            $out['ok'] = false;
            $out['reason'] = "Last payment {$age_min} menit lalu (threshold {$max_age_min}m)";
        }
    } else {
        $out['ok'] = false;
        $out['reason'] = 'Gak ada entry di Live Payment Proof';
    }
    return $out;
}

function check_response(string $html): array {
    $alerts = parse_alert_message($html);

    if ($alerts['success'] !== null) {
        return ['status' => 'success', 'msg' => $alerts['success']];
    }
    if ($alerts['error'] !== null) {
        $msg = $alerts['error'];
        if (is_fatal_error($msg)) {
            return ['status' => 'fatal', 'msg' => $msg];
        }
        $low = strtolower($msg);
        if (strpos($low, 'math') !== false || strpos($low, 'captcha') !== false
            || strpos($low, 'wrong') !== false || strpos($low, 'incorrect') !== false
            || strpos($low, 'invalid') !== false) {
            return ['status' => 'wrong', 'msg' => $msg];
        }
        return ['status' => 'error', 'msg' => $msg];
    }

    $low = strtolower($html);
    foreach (['banned', 'blocked', 'vpn not allowed', 'proxy not allowed'] as $kw) {
        if (strpos($low, $kw) !== false) return ['status' => 'banned', 'msg' => "Keyword: $kw"];
    }
    foreach (['please wait', 'try again later', 'countdown', 'one claim'] as $kw) {
        if (strpos($low, $kw) !== false) return ['status' => 'wait', 'msg' => "Cooldown: $kw"];
    }
    return ['status' => 'unknown', 'msg' => 'Unclear response'];
}

// ═══════════════════════════════════════════════════════════════
//  SETUP
// ═══════════════════════════════════════════════════════════════
function interactive_setup(): array {
    echo "\n" . CYN . "═══ FIRST TIME SETUP ═══" . RST . "\n\n";
    $email = '';
    while (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $email = read_line(YEL . "FaucetPay Email: " . RST);
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            echo RED . "  ✗ Email gak valid, coba lagi.\n" . RST;
        }
    }
    return [
        'email'    => $email,
        'base_url' => BASE_URL,
        'delay'    => 65,
        'cookie'   => '',
    ];
}

// ═══════════════════════════════════════════════════════════════
//  MAIN
// ═══════════════════════════════════════════════════════════════
render_box_clear();
echo CYN . "  ◈ TRONBLOW AUTO CLAIM ENGINE v4.1 (Clean)\n" . RST;
echo DIM . "  ─── Souu Engine ───\n\n" . RST;

// Load config
$config = load_config();
if ($config) {
    echo GRN . "  ✓ Config found\n" . RST;
    echo DIM . "    Email : {$config['email']}\n" . RST;
    echo DIM . "    Delay : {$config['delay']}s\n" . RST;
    echo DIM . "    URL   : {$config['base_url']}\n\n" . RST;
    $ans = read_line(YEL . "  Use saved? (y/n): " . RST);
    if (strtolower($ans) === 'n') {
        $config = interactive_setup();
    }
} else {
    $config = interactive_setup();
}
save_config($config);

if (!file_exists($COOKIE_FILE)) touch($COOKIE_FILE);

// Update state
$STATE['email'] = $config['email'];
$STATE['daily_count'] = load_counter()['count'];
$STATE['runtime_start'] = time();

render_box_clear();

$cycle = 0;
while (true) {
    // Cek daily limit
    $counter = load_counter();
    $STATE['daily_count'] = $counter['count'];
    if ($counter['count'] >= DAILY_LIMIT) {
        state_log("Daily limit reached ({$counter['count']}/" . DAILY_LIMIT . ")", 'WARN');
        render_box_clear();
        $secs = strtotime("tomorrow 00:00 UTC") - time();
        while ($secs > 0) {
            sleep(min(60, $secs));
            $secs = strtotime("tomorrow 00:00 UTC") - time();
        }
        continue;
    }

    // Cek max runtime
    if ((time() - $STATE['runtime_start']) >= $STATE['max_runtime']) {
        state_log("Max runtime reached, exiting", 'WARN');
        render_box_clear();
        break;
    }

    // Cek max failures
    if ($STATE['failures'] >= $STATE['max_failures']) {
        state_log("Max failures reached, exiting", 'ERR');
        render_box_clear();
        break;
    }

    $cycle++;
    state_log("Cycle #$cycle starting...", 'INFO');
    render_box_clear();

    // Fetch homepage
    $result = fetch_page($config['base_url'], $COOKIE_FILE);
    if (!$result['html']) {
        state_log("Fetch failed (HTTP {$result['http_code']})", 'ERR');
        $STATE['failures']++;
        render_box_clear();
        sleep(30);
        continue;
    }
    $html = $result['html'];

    // ─── HEALTH CHECK ───
    state_log("Checking faucet health...", 'HEALTH');
    render_box_clear();
    $health = check_faucet_health($html, 30);
    $STATE['faucet_status'] = $health['ok'] ? 'ok' : 'suspect';
    $STATE['last_payment']  = $health['last_payment'];

    if (!$health['ok']) {
        state_log("SUSPECT: {$health['reason']}", 'WARN');
        render_box_clear();

        // Pre-check: apakah ada alert fatal di homepage?
        $pre = parse_alert_message($html);
        if ($pre['error'] && is_fatal_error($pre['error'])) {
            $STATE['faucet_status'] = 'dead';
            state_log("FATAL: {$pre['error']}", 'ERR');
            render_box_clear();
            echo "\n" . RED . "  ╔══════════════════════════════════════════════════════╗\n" . RST;
            echo RED   . "  ║  ❌ FAUCET SUDAH TIDAK BISA BAYAR                    ║\n" . RST;
            echo RED   . "  ║  Bot dihentikan otomatis.                            ║\n" . RST;
            echo RED   . "  ╚══════════════════════════════════════════════════════╝\n\n" . RST;
            break;
        }

        // Tanya user
        echo "\n" . YEL . "  ⚠ Faucet kelihatan gak bayar (" . ($health['age_min'] ?? '?') . " menit).\n" . RST;
        $ans = read_line(YEL . "  Lanjut claim? (y/n): " . RST);
        if (strtolower($ans) !== 'y') {
            state_log("Stopped by user", 'WARN');
            render_box_clear();
            break;
        }
    }

    // ─── CLOUDFLARE check ───
    $low = strtolower($html);
    if (strpos($low, 'cf-browser-verification') !== false
        || strpos($low, 'challenge-platform') !== false
        || strpos($low, 'just a moment') !== false) {
        state_log("Cloudflare challenge — clearing cookies", 'WARN');
        render_box_clear();
        @unlink($COOKIE_FILE);
        touch($COOKIE_FILE);
        sleep(60);
        continue;
    }

    // ─── CSRF ───
    $csrf = extract_csrf_token($html);
    if (!$csrf) {
        state_log("CSRF token not found", 'ERR');
        $STATE['failures']++;
        render_box_clear();
        sleep(30);
        continue;
    }

    // ─── MATH ───
    $math = extract_math_question($html);
    if (!$math) {
        state_log("Math question not found", 'ERR');
        $STATE['failures']++;
        render_box_clear();
        sleep(30);
        continue;
    }
    $answer = solve_math($math);
    state_log("Math: {$math['q1']} {$math['op']} {$math['q2']} = $answer", 'VERIFY');
    render_box_clear();

    // ─── SUBMIT ───
    state_log("Claiming 1000 SAT...", 'CLAIM');
    render_box_clear();

    $submit = submit_claim($config['base_url'], $COOKIE_FILE, $config['email'], $csrf, $answer);
    $status = check_response($submit['body']);
    $wait_seconds = $config['delay'];

    switch ($status['status']) {
        case 'success':
            $counter = increment_counter();
            $STATE['daily_count'] = $counter['count'];
            $STATE['claims']++;
            $STATE['rewards'] += 0.00001; // 1000 sat = 0.00001 TRX
            $STATE['failures'] = 0;
            state_log("✓ CLAIMED: {$status['msg']}", 'OK');

            $endAt = extract_endAt($submit['body']);
            if ($endAt) {
                $wait_ms = $endAt - (int)(microtime(true) * 1000);
                if ($wait_ms > 0) $wait_seconds = (int) ceil($wait_ms / 1000);
            }
            render_box_clear();
            break;

        case 'fatal':
            $STATE['faucet_status'] = 'dead';
            state_log("FATAL: {$status['msg']}", 'ERR');
            render_box_clear();
            echo "\n" . RED . "  ╔══════════════════════════════════════════════════════╗\n" . RST;
            echo RED   . "  ║  ❌ FAUCET SUDAH TIDAK BISA BAYAR                    ║\n" . RST;
            echo RED   . "  ║  " . str_pad("  " . substr($status['msg'], 0, 46), 52) . "  ║\n" . RST;
            echo RED   . "  ║  Bot dihentikan otomatis.                            ║\n" . RST;
            echo RED   . "  ╚══════════════════════════════════════════════════════╝\n\n" . RST;
            exit(2);

        case 'wait':
        case 'already':
            state_log("⏳ {$status['msg']}", 'WAIT');
            $endAt = extract_endAt($submit['body']);
            if ($endAt) {
                $wait_ms = $endAt - (int)(microtime(true) * 1000);
                if ($wait_ms > 0) $wait_seconds = (int) ceil($wait_ms / 1000);
            }
            render_box_clear();
            break;

        case 'wrong':
            state_log("Math wrong: {$status['msg']}", 'ERR');
            $STATE['failures']++;
            render_box_clear();
            sleep(5);
            continue 2;

        case 'error':
            state_log("Error: {$status['msg']}", 'ERR');
            $STATE['failures']++;
            render_box_clear();
            sleep(15);
            continue 2;

        case 'banned':
            state_log("BANNED: {$status['msg']}", 'ERR');
            render_box_clear();
            exit(1);

        default:
            state_log("Unknown: {$status['msg']}", 'WARN');
            $endAt = extract_endAt($submit['body']);
            if ($endAt) {
                $wait_ms = $endAt - (int)(microtime(true) * 1000);
                if ($wait_ms > 0) $wait_seconds = (int) ceil($wait_ms / 1000);
            }
            render_box_clear();
            break;
    }

    // Wait
    if ($wait_seconds > 0) {
        state_log("Next claim in {$wait_seconds}s", 'WAIT');
        render_box_clear();
        sleep($wait_seconds);
    }
}

// Final
render_box_clear();
echo "\n" . CYN . "  ◈ Bot stopped.\n" . RST;
echo DIM . "  Claims: {$STATE['claims']}  |  Failures: {$STATE['failures']}\n\n" . RST;
