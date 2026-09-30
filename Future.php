#!/usr/bin/env php
<?php
/**
 * ═══════════════════════════════════════════════════════════════
 *  CryptoFuture Auto Claim — SOUU ENGINE v8.5
 *  FIX: Turnstile detect + auto-solve di faucet claim
 *       Balance scrape 4 fallback regex
 *       Verify login pake /faucet
 * ═══════════════════════════════════════════════════════════════
 */

error_reporting(E_ALL & ~E_DEPRECATED & ~E_USER_DEPRECATED);
ini_set('display_errors', '0');

// ═══════════ COLORS ═══════════
function fg($c){ return "\033[38;5;{$c}m"; }
define("RST", "\033[0m");
define("BOLD", "\033[1m");

// ═══════════ CONFIG ═══════════
const SITE_BASE        = "https://cryptofuture.co.in";
const SITE_HOME        = "https://cryptofuture.co.in/";
const SITE_LOGIN       = "https://cryptofuture.co.in/auth/login";
const SITE_DASHBOARD   = "https://cryptofuture.co.in/dashboard";
const SITE_FAUCET      = "https://cryptofuture.co.in/faucet";
const SITE_VERIFY      = "https://cryptofuture.co.in/faucet/verify";
const SITE_PTC         = "https://cryptofuture.co.in/ptc";
const SITE_PTC_VERIFY  = "https://cryptofuture.co.in/ptc/verify/";

const TURNSTILE_SITEKEY = "0x4AAAAAACCJpcjk1yzJVey2";
const SOLVER_IN  = "https://api.waryono.my.id/in.php";
const SOLVER_OUT = "https://api.waryono.my.id/res.php";

const CONFIG_FILE        = "cryptofuture_config.json";
const DEBUG_FILE         = "debug_verify_response.txt";
const DEBUG_BALANCE_FILE = "debug_balance.html";

const UA_DEFAULT = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36";

const MAX_CLAIMS  = 100;
const CLAIM_CD    = 10;
const RETRY_CD    = 15;
const FAIL_LIMIT  = 5;

// ═══════════ STATE ═══════════
$GLOBALS['_logs']       = [];
$GLOBALS['_stage']      = 'INIT';
$GLOBALS['_email']      = '?';
$GLOBALS['_balance']    = '?';
$GLOBALS['_claims']     = 0;
$GLOBALS['_fails']      = 0;
$GLOBALS['_earned']     = 0.0;
$GLOBALS['_ip']         = '?';
$GLOBALS['_isp']        = '?';
$GLOBALS['_country']    = '?';
$GLOBALS['_startTime']  = time();
$GLOBALS['_mode']       = 'idle';
$GLOBALS['COOKIES']     = [];

// ═══════════ ANSI HELPERS ═══════════
function ansi_len($s){
    $plain = preg_replace('/\x1b\[[0-9;]*m/', '', $s);
    $w = 0;
    $len = mb_strlen($plain, 'UTF-8');
    for ($i = 0; $i < $len; $i++){
        $ch = mb_substr($plain, $i, 1, 'UTF-8');
        $cp = mb_ord($ch, 'UTF-8');
        if (($cp >= 0x1F300 && $cp <= 0x1F9FF) || ($cp >= 0x2600 && $cp <= 0x27BF) ||
            ($cp >= 0x2B00 && $cp <= 0x2BFF) || ($cp >= 0x25A0 && $cp <= 0x25FF) ||
            ($cp >= 0x2580 && $cp <= 0x259F)) {
            $w += 2;
        } else { $w += 1; }
    }
    return $w;
}
function ansi_pad($s, $len){
    $p = $len - ansi_len($s);
    return $s . ($p > 0 ? str_repeat(' ', $p) : '');
}
function gradient($text, $start = 51, $end = 196){
    $len = mb_strlen($text, 'UTF-8');
    if ($len <= 1) return fg($start) . $text . RST;
    $out = '';
    for ($i = 0; $i < $len; $i++){
        $t = $i / max(1, $len - 1);
        $c = (int)round($start + ($end - $start) * $t);
        $out .= fg($c) . mb_substr($text, $i, 1, 'UTF-8');
    }
    return $out . RST;
}
function box_line($c){ return fg(51) . "║  " . RST . ansi_pad($c, 60) . fg(51) . "║" . RST . "\n"; }
function box_div(){  return fg(51) . "╠" . str_repeat("═", 62) . "╣" . RST . "\n"; }

// ═══════════ CLEAR SCREEN ═══════════
function clear_screen(){
    if (PHP_OS_FAMILY === 'Windows') { @system('cls'); }
    else { @system('clear'); }
    echo "\033[3J\033[H\033[2J";
}

// ═══════════ LOG ═══════════
function push_log($msg, $tag = 'i'){
    $icons = ['i' => fg(51)."●".RST, 'ok' => fg(46)."✔".RST, 'er' => fg(196)."✖".RST,
              'wr' => fg(208)."◈".RST, 'in' => fg(213)."◉".RST, 'g' => fg(226)."◆".RST];
    $ts = date('H:i:s');
    $line = fg(250) . "[{$ts}]" . RST . " " . ($icons[$tag] ?? '●') . " " . $msg;
    $GLOBALS['_logs'][] = $line;
    if (count($GLOBALS['_logs']) > 5) array_shift($GLOBALS['_logs']);
}

// ═══════════ IP CHECK ═══════════
function check_ip(){
    if ($GLOBALS['_ip'] !== '?') return;
    $ctx = stream_context_create(['http' => ['timeout' => 5]]);
    $r = @file_get_contents("http://ip-api.com/json", false, $ctx);
    if ($r === false) return;
    $j = json_decode($r, true);
    if (!is_array($j)) return;
    $GLOBALS['_ip']      = $j['query'] ?? '?';
    $GLOBALS['_country'] = ($j['country'] ?? '?') . ' / ' . ($j['city'] ?? '?');
    $GLOBALS['_isp']     = $j['isp'] ?? '?';
}

// ═══════════ TIME HELPERS ═══════════
function fmt_time($s){
    $s = (int)$s; if ($s <= 0) return '0s';
    if ($s >= 3600) return floor($s/3600) . 'h' . floor(($s % 3600) / 60) . 'm';
    if ($s >= 60)   return floor($s/60) . 'm' . ($s % 60) . 's';
    return $s . 's';
}
function fmt_uptime($s){
    $s = (int)$s;
    return sprintf('%02d:%02d:%02d', floor($s/3600), floor(($s%3600)/60), $s%60);
}

// ═══════════ BANNER ═══════════
function banner(){
    check_ip();
    clear_screen();

    $elapsed = time() - $GLOBALS['_startTime'];
    $claims  = $GLOBALS['_claims'];
    $maxC    = MAX_CLAIMS;
    $pct     = $maxC > 0 ? min(100, ($claims / $maxC) * 100) : 0;

    $barLen = 20;
    $filled = (int)round(($pct / 100) * $barLen);
    $bar    = str_repeat("█", $filled) . str_repeat("░", $barLen - $filled);

    echo fg(51) . "╔" . str_repeat("═", 62) . "╗" . RST . "\n";
    echo box_line(gradient("CRYPTOFUTURE AUTO CLAIM", 51, 213));
    echo box_line(fg(240) . "─────── SOUU ENGINE v8.5 ───────" . RST);
    echo box_div();

    echo box_line(fg(213) . BOLD . "NETWORK" . RST);
    echo box_line(fg(51) . "├─ IP         : " . RST . fg(226) . $GLOBALS['_ip'] . RST);
    echo box_line(fg(51) . "├─ Country    : " . RST . fg(226) . $GLOBALS['_country'] . RST);
    echo box_line(fg(51) . "└─ ISP        : " . RST . fg(226) . $GLOBALS['_isp'] . RST);
    echo box_div();

    echo box_line(fg(213) . BOLD . "SESSION" . RST);
    echo box_line(fg(51) . "├─ Stage      : " . RST . fg(208) . $GLOBALS['_stage'] . RST);
    echo box_line(fg(51) . "├─ Mode       : " . RST . fg(213) . strtoupper($GLOBALS['_mode']) . RST);
    echo box_line(fg(51) . "├─ Uptime     : " . RST . fg(226) . fmt_uptime($elapsed) . RST);
    echo box_line(fg(51) . "├─ Email      : " . RST . fg(226) . $GLOBALS['_email'] . RST);
    echo box_line(fg(51) . "├─ Balance    : " . RST . fg(46) . $GLOBALS['_balance'] . " Coins" . RST);
    echo box_line(fg(51) . "├─ Claims     : " . RST . fg(226) . "{$claims}/{$maxC}" . RST);
    echo box_line(fg(51) . "├─ Failed     : " . RST . fg(196) . $GLOBALS['_fails'] . RST);
    echo box_line(fg(51) . "└─ Earned     : " . RST . fg(46) . number_format($GLOBALS['_earned'], 4) . " Coins" . RST);
    echo box_div();

    echo box_line(fg(213) . BOLD . "PROGRESS" . RST);
    $pctColor = $pct >= 80 ? 196 : ($pct >= 50 ? 208 : 46);
    echo box_line(fg(51) . "  [" . fg($pctColor) . $bar . fg(51) . "]  " . RST . fg($pctColor) . sprintf("%.1f%%", $pct) . RST);
    echo box_div();

    echo box_line(fg(213) . BOLD . "LIVE LOG" . RST);
    $logs = $GLOBALS['_logs'];
    for ($i = 0; $i < 5; $i++){
        if (isset($logs[$i])) echo box_line(fg(252) . $logs[$i] . RST);
        else echo fg(51) . "║" . str_repeat(" ", 62) . "║" . RST . "\n";
    }

    echo fg(51) . "╚" . str_repeat("═", 62) . "╝" . RST . "\n";
    echo "\n   " . gradient("BOT RUNNING", 46, 226) . " " . fg(250) . "• " . date('H:i:s') . RST
        . " • " . fg(51) . "uptime " . fmt_uptime($elapsed) . RST . "\n";
    echo "   " . fg(240) . "By Power " . RST . fg(213) . "@SouuXso" . RST . fg(240) . " • " . RST
        . fg(46) . "CryptoFuture Edition" . RST . "\n\n";
}

// ═══════════ LIVE TICK ═══════════
function live_tick($seconds, $label = "next", $step = 1){
    $w = (int)$seconds;
    while ($w > 0) {
        $s = min($w, $step);
        sleep($s);
        $w -= $s;

        $elapsed = time() - $GLOBALS['_startTime'];
        $claims  = $GLOBALS['_claims'];
        $pct     = MAX_CLAIMS > 0 ? min(100, ($claims / MAX_CLAIMS) * 100) : 0;

        $line = "  " . fg(51) . "⏳ {$label} " . fmt_time($w) . RST
              . " " . fg(240) . "|" . RST
              . " " . fg(226) . "up " . fmt_uptime($elapsed) . RST
              . " " . fg(240) . "|" . RST
              . " " . fg(46) . "clm {$claims}/" . MAX_CLAIMS . RST
              . " " . fg(213) . sprintf("(%.0f%%)", $pct) . RST;

        echo "\r\033[K" . $line;
        flush();
    }
    echo "\n";
}

// ═══════════ CONFIG ═══════════
function load_config(){
    if (!file_exists(CONFIG_FILE)) return [];
    $j = json_decode(file_get_contents(CONFIG_FILE), true);
    return is_array($j) ? $j : [];
}
function save_config($cfg){
    @file_put_contents(CONFIG_FILE, json_encode($cfg, JSON_PRETTY_PRINT));
    @chmod(CONFIG_FILE, 0600);
}

// ═══════════ COOKIE JAR ═══════════
function cookie_str(){
    if (!$GLOBALS['COOKIES']) return '';
    $p = [];
    foreach ($GLOBALS['COOKIES'] as $k => $v) $p[] = "$k=$v";
    return implode('; ', $p);
}
function cookie_absorb($headers){
    if (preg_match_all('/^set-cookie:\s*([^=]+)=([^;]+)/mi', $headers, $m, PREG_SET_ORDER)) {
        foreach ($m as $c) $GLOBALS['COOKIES'][trim($c[1])] = trim($c[2]);
    }
}

// ═══════════ HTTP ═══════════
function req($url, $method = 'GET', $data = null, $headers = [], $binary = false){
    $ch = curl_init();
    $def = [
        "User-Agent: " . UA_DEFAULT,
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language: id-ID,id;q=0.9,en;q=0.8",
        "Upgrade-Insecure-Requests: 1",
        "Referer: " . SITE_HOME,
        "sec-ch-ua: \"Chromium\";v=\"127\", \"Not)A;Brand\";v=\"99\"",
        "sec-ch-ua-mobile: ?1",
        "sec-ch-ua-platform: \"Android\"",
    ];
    if ($method === 'POST') $def[] = "Content-Type: application/x-www-form-urlencoded";
    $cs = cookie_str();
    if ($cs !== '') $def[] = "Cookie: " . $cs;

    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER => !$binary,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_MAXREDIRS => 5,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_CONNECTTIMEOUT => 15,
        CURLOPT_ENCODING => "",
        CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_2TLS,
        CURLOPT_HTTPHEADER => array_merge($def, $headers),
    ]);
    if ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        if ($data !== null) curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    }

    $resp = curl_exec($ch);
    if ($resp === false){
        $err = curl_error($ch);
        curl_close($ch);
        return ['body' => '', 'code' => 0, 'headers' => '', 'error' => $err];
    }
    $info = curl_getinfo($ch);
    curl_close($ch);

    if ($binary){
        return ['body' => $resp, 'code' => $info['http_code'], 'headers' => '', 'error' => ''];
    }
    $hs   = $info['header_size'];
    $raw  = substr($resp, 0, $hs);
    $body = substr($resp, $hs);
    cookie_absorb($raw);
    return ['body' => $body, 'code' => $info['http_code'], 'headers' => $raw, 'error' => ''];
}

// ═══════════ CF DETECT ═══════════
function is_cf_challenge($html){
    return stripos($html, 'Just a moment') !== false
        || stripos($html, 'cf-challenge') !== false
        || stripos($html, 'Checking your browser') !== false
        || stripos($html, 'cf_chl_opt') !== false;
}

// ═══════════ TURNSTILE SOLVER ═══════════
function solve_turnstile($apikey, $domain, $sitekey, $action = '', $cdata = ''){
    push_log("solving turnstile...", 'in');
    $body = json_encode([
        "apikey"  => $apikey,
        "methods" => "turnstile",
        "domain"  => $domain,
        "sitekey" => $sitekey,
        "action"  => $action,
        "cdata"   => $cdata,
    ]);
    $r = req(SOLVER_IN, 'POST', $body, ["Content-Type: application/json"]);
    if (!$r['body']){
        push_log("solver in: empty response", 'er');
        return null;
    }
    $j = json_decode($r['body'], true);

    if (is_array($j) && isset($j['request'])) {
        if (($j['status'] ?? 1) === 0) {
            push_log("solver err: " . $j['request'], 'er');
            return null;
        }
        $id = $j['request'];
    } elseif (preg_match('/OK\|(\S+)/', $r['body'], $m)) {
        $id = $m[1];
    } else {
        push_log("solver in: " . substr($r['body'], 0, 60), 'er');
        return null;
    }

    push_log("job id $id, polling...", 'in');
    for ($i = 0; $i < 40; $i++) {
        sleep(2);
        $url = SOLVER_OUT . "?apikey=" . $apikey . "&action=get&id=" . $id . "&json=1";
        $r2 = req($url, 'GET');
        $raw = trim($r2['body']);

        if (strpos($raw, "CAPCHA_NOT_READY") !== false) continue;
        if (strpos($raw, "ERROR_") !== false) {
            push_log("solver: " . substr($raw, 0, 60), 'er');
            return null;
        }
        if (preg_match('/^OK\|(.+)$/', $raw, $m)) {
            return $m[1];
        }
        $j2 = json_decode($raw, true);
        if (is_array($j2) && isset($j2['request'])) {
            $v = $j2['request'];
            if (strpos($v, "answer:") === 0) return substr($v, 7);
            if (strpos($v, "CAPCHA") !== false) continue;
            if (strpos($v, "ERROR_") !== false) {
                push_log("solver: $v", 'er');
                return null;
            }
            if (strlen($v) > 30) return $v;
        }
    }
    push_log("solver timeout", 'er');
    return null;
}

// ═══════════ SCRAPERS ═══════════
function extract_csrf($html){
    if (preg_match('/name="csrf_token_name"[^>]*value="([^"]+)"/i', $html, $m)) return $m[1];
    if (preg_match('/<meta[^>]+name=["\']csrf-token["\'][^>]+content=["\']([^"\']+)/i', $html, $m)) return $m[1];
    return '';
}

function parse_earn($html){
    $o = [
        'csrf'         => '',
        'claim_token'  => '',
        'wait'         => 0,
        'balance'      => null,
        'has_form'     => false,
        'has_turnstile'=> false,
        'turnstile_sitekey' => TURNSTILE_SITEKEY,
    ];

    if (preg_match('/<form[^>]+id="fauform"[^>]*>(.*?)<\/form>/si', $html, $fm)) {
        $o['has_form'] = true;
        $in = $fm[1];
        if (preg_match('/name="csrf_token_name"[^>]*value="([^"]*)"/i', $in, $m)) $o['csrf']        = $m[1];
        if (preg_match('/name="claim_token"[^>]*value="([^"]*)"/i', $in, $m))     $o['claim_token'] = $m[1];

        // ── Detect Turnstile di dalam form ──
        if (stripos($in, 'cf-turnstile') !== false
            || stripos($in, 'cf-turnstile-response') !== false) {
            $o['has_turnstile'] = true;
            if (preg_match('/data-sitekey=["\']([^"\']+)["\']/i', $in, $m)) {
                $o['turnstile_sitekey'] = $m[1];
            }
        }
    }

    // Fallback: cek Turnstile di seluruh halaman
    if (!$o['has_turnstile'] && stripos($html, 'cf-turnstile') !== false) {
        $o['has_turnstile'] = true;
        if (preg_match('/data-sitekey=["\']([^"\']+)["\']/i', $html, $m)) {
            $o['turnstile_sitekey'] = $m[1];
        }
    }

    if (preg_match('/(?:let|var|const)\s+wait\s*=\s*(\d+)/i', $html, $m)) {
        $o['wait'] = (int)$m[1];
    }

    $o['balance'] = scrape_balance($html);

    return $o;
}

/**
 * Scrape balance — 4 fallback regex
 */
function scrape_balance($html) {
    if (!$html) return null;

    // P1: exact — "Balance: <strong>N Coins</strong>"
    if (preg_match('/Balance:\s*<strong[^>]*>([\d,\.]+)\s*Coins/i', $html, $m)) {
        return (float)str_replace(',', '', $m[1]);
    }
    // P2: strong manapun + "N Coins"
    if (preg_match('/<strong[^>]*>([\d,\.]+)\s*Coins<\/strong>/i', $html, $m)) {
        return (float)str_replace(',', '', $m[1]);
    }
    // P3: any tag + "N Coins"
    if (preg_match_all('/>([\d,\.]+)\s*Coins\b/i', $html, $mm)) {
        $best = 0;
        foreach ($mm[1] as $v) {
            $n = (float)str_replace(',', '', $v);
            if ($n > $best) $best = $n;
        }
        if ($best > 0) return $best;
    }
    // P4: raw "N Coins"
    if (preg_match('/([\d,\.]+)\s*Coins\b/i', $html, $m)) {
        return (float)str_replace(',', '', $m[1]);
    }
    return null;
}

function fetch_balance_from_faucet(){
    $r = req(SITE_FAUCET);
    $bal = scrape_balance($r['body']);
    if ($bal === null) {
        @file_put_contents(DEBUG_BALANCE_FILE,
            "TIME  : " . date('Y-m-d H:i:s') . "\n" .
            "URL   : " . SITE_FAUCET . "\n" .
            "LEN   : " . strlen($r['body']) . "\n" .
            "SNIP  :\n" . substr($r['body'], 0, 3000) . "\n\n",
            FILE_APPEND);
        return null;
    }
    $GLOBALS['_balance'] = number_format((float)$bal, 0);
    return $bal;
}

function is_login_page($html) {
    if (stripos($html, 'cf-chl-') !== false) return false;
    if (stripos($html, 'Just a moment') !== false) return false;
    if (stripos($html, 'name="password"') !== false && stripos($html, 'fauform') === false) return true;
    if (preg_match('/<form[^>]*action=["\'][^"\']*(?:login|auth|signin)[^"\']*["\']/i', $html)) return true;
    return false;
}

// ═══════════ GENERATORS ═══════════
function gen_device_token(){
    $chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    $s = '';
    for ($i = 0; $i < 20; $i++) $s .= $chars[random_int(0, strlen($chars) - 1)];
    return 'dev_' . $s;
}

// ═══════════ SESSION CHECK ═══════════
function check_session(){
    $tryUrls = [SITE_FAUCET, SITE_DASHBOARD, SITE_HOME];
    $lastHttp = 0;
    foreach ($tryUrls as $url) {
        $r = req($url);
        $httpCode = (int)($r['code'] ?? 0);
        $body = $r['body'];
        $lastHttp = $httpCode;
        if ($httpCode === 404 || $httpCode === 0) continue;

        $info = parse_earn($body);
        $bal = $info['balance'];

        if ($bal !== null) $GLOBALS['_balance'] = number_format((float)$bal, 0);

        if (!empty($info['claim_token']) || !empty($info['has_form'])) {
            return ['ok' => true, 'balance' => $bal, 'http' => $httpCode];
        }
        if (is_login_page($body))
            return ['ok' => false, 'reason' => 'session_expired', 'http' => $httpCode];

        if ($httpCode >= 200 && $httpCode < 400) {
            if ($bal !== null || stripos($body, 'logout') !== false
                || stripos($body, 'Faucet') !== false) {
                return ['ok' => true, 'balance' => $bal, 'http' => $httpCode];
            }
        }
    }
    return ['ok' => false, 'reason' => 'unknown_' . $lastHttp, 'http' => $lastHttp];
}

// ═══════════ EMAIL LOGIN ═══════════
function login_with_email($email, $apikey){
    push_log("opening homepage...", 'in');
    banner();

    $r1 = req(SITE_HOME);
    $html = $r1['body'];

    if (is_cf_challenge($html)) {
        push_log("CF challenge at homepage — retry...", 'wr');
        sleep(3);
        $r1 = req(SITE_HOME);
        $html = $r1['body'];
        if (is_cf_challenge($html)) {
            return ['ok' => false, 'msg' => 'CF challenge - bot blocked by Cloudflare'];
        }
    }

    $csrf = extract_csrf($html);
    if ($csrf === '') {
        $csrf = $GLOBALS['COOKIES']['csrf_cookie_name'] ?? '';
    }
    if ($csrf === '') {
        return ['ok' => false, 'msg' => 'CSRF not found'];
    }
    push_log("csrf: " . substr($csrf, 0, 12) . "...", 'ok');
    banner();

    push_log("opening login page...", 'in');
    banner();
    $r2 = req(SITE_LOGIN);
    $loginHtml = $r2['body'];

    if (is_cf_challenge($loginHtml)) {
        return ['ok' => false, 'msg' => 'CF challenge at /login'];
    }

    $csrf2 = extract_csrf($loginHtml);
    if ($csrf2 !== '') $csrf = $csrf2;

    $loginSitekey = TURNSTILE_SITEKEY;
    if (preg_match('/data-sitekey="([^"]+)"/i', $loginHtml, $m)) {
        $loginSitekey = $m[1];
    }
    $hasTurnstile = stripos($loginHtml, 'cf-turnstile') !== false;

    $tsToken = '';
    if ($hasTurnstile && $apikey) {
        push_log("login page: turnstile required", 'wr');
        banner();
        $tsToken = solve_turnstile($apikey, SITE_HOME, $loginSitekey);
        if (!$tsToken) {
            return ['ok' => false, 'msg' => 'turnstile solve fail'];
        }
        push_log("turnstile solved", 'ok');
        banner();
    } elseif ($hasTurnstile && !$apikey) {
        return ['ok' => false, 'msg' => 'turnstile required but apikey missing'];
    }

    $device = gen_device_token();
    $postData = [
        'wallet'          => $email,
        'csrf_token_name' => $csrf,
        'device_token'    => $device,
    ];
    if ($tsToken) {
        $postData['cf-turnstile-response'] = $tsToken;
    }

    $post = http_build_query($postData);
    push_log("posting login...", 'in');
    banner();

    $r3 = req(SITE_LOGIN, 'POST', $post, [
        'Origin: ' . SITE_BASE,
        'Referer: ' . SITE_LOGIN,
    ]);

    $httpCode = (int)($r3['code'] ?? 0);
    $respBody = $r3['body'];

    if ($httpCode >= 400) {
        return ['ok' => false, 'msg' => "HTTP {$httpCode}"];
    }
    if (is_login_page($respBody)) {
        return ['ok' => false, 'msg' => 'still on login page (turnstile rejected)'];
    }

    push_log("verifying session...", 'in');
    banner();
    sleep(2);

    // ── FIX: verify pake /faucet (ada balance), bukan /dashboard ──
    $r4 = req(SITE_FAUCET);
    $faucetHtml = $r4['body'];

    if (is_login_page($faucetHtml)) {
        return ['ok' => false, 'msg' => 'login rejected (redirected to login)'];
    }

    $loginOk = stripos($faucetHtml, 'fauform') !== false
            || stripos($faucetHtml, 'auth/logout') !== false
            || stripos($faucetHtml, 'Logout') !== false
            || stripos($faucetHtml, 'Balance:') !== false
            || stripos($faucetHtml, 'Faucet') !== false;

    if (!$loginOk) {
        return ['ok' => false, 'msg' => 'login rejected (no faucet markers)'];
    }

    $bal = scrape_balance($faucetHtml);
    if ($bal !== null) {
        $GLOBALS['_balance'] = number_format((float)$bal, 0);
        push_log("balance: " . $GLOBALS['_balance'] . " Coins", 'ok');
    }
    banner();

    return ['ok' => true];
}

// ═══════════ FAUCET CLAIM (v8.5 — Turnstile detect + solve) ═══════════
function attempt_faucet_claim($apikey){
    $r    = req(SITE_FAUCET);
    $html = $r['body'];

    if (is_cf_challenge($html)) return ['status' => 'cf'];
    if (is_login_page($html))  return ['status' => 'session_invalid'];

    $info = parse_earn($html);
    if ($info['balance'] !== null) {
        $GLOBALS['_balance'] = number_format((float)$info['balance'], 0);
    }

    if ($info['wait'] > 0)     return ['status' => 'cooldown', 'wait' => (int)$info['wait']];
    if (!$info['has_form'])    return ['status' => 'error', 'msg' => 'no fauform'];
    if ($info['claim_token'] === '') return ['status' => 'error', 'msg' => 'claim_token missing'];

    sleep(rand(2, 4));

    $postData = [
        'csrf_token_name' => $info['csrf'],
        'claim_token'     => $info['claim_token'],
    ];

    // ── FIX v8.5: Solve Turnstile kalo muncul ──
    if (!empty($info['has_turnstile'])) {
        push_log("turnstile DETECTED — solving...", 'wr');
        banner();
        $ts_token = solve_turnstile($apikey, SITE_HOME, $info['turnstile_sitekey']);
        if (!$ts_token) {
            push_log("turnstile solve FAIL — skip round", 'er');
            banner();
            return ['status' => 'error', 'msg' => 'turnstile solve fail'];
        }
        $postData['cf-turnstile-response'] = $ts_token;
        push_log("turnstile SOLVED (" . strlen($ts_token) . "c)", 'ok');
        banner();
    }

    $post = http_build_query($postData);
    $r2 = req(SITE_VERIFY, 'POST', $post, ['Origin: ' . SITE_BASE, 'Referer: ' . SITE_FAUCET]);
    $respHtml = (string)($r2['body'] ?? '');
    $httpCode = (int)($r2['code'] ?? 0);

    @file_put_contents(DEBUG_FILE,
        str_repeat('═', 60) . "\n" .
        "TIME   : " . date('Y-m-d H:i:s') . "\n" .
        "HTTP   : {$httpCode}\n" .
        "TURNSTILE: " . (!empty($info['has_turnstile']) ? 'YES (' . strlen($postData['cf-turnstile-response'] ?? '') . 'c)' : 'no') . "\n" .
        "CLAIM  : csrf=" . substr($info['csrf'], 0, 12) . " token=" . substr($info['claim_token'], 0, 12) . "\n" .
        "BODY (5000):\n" . substr($respHtml, 0, 5000) . "\n\n",
        FILE_APPEND);

    $success = false;
    $amount  = 0.0;

    if ($httpCode === 200 && $respHtml !== '') {
        // P1: Swal success + amount
        if (preg_match("/Swal\.fire\s*\(\s*\{.*?icon:\s*['\"]success['\"].*?html:\s*['\"]([^'\"]*\d+[^'\"]*Coins?[^'\"]*)['\"]/is", $respHtml, $m)) {
            if (preg_match('/([\d\.,]+)\s*Coins?/i', $m[1], $am)) {
                $amount = (float)str_replace(',', '', $am[1]);
                $success = true;
            }
        }
        // P2: Swal success tanpa amount (cari amount manapun)
        if (!$success && preg_match("/Swal\.fire\s*\(\s*\{.*?icon:\s*['\"]success['\"]/is", $respHtml)) {
            if (preg_match("/html:\s*['\"]([^'\"]*\d+[^'\"]*Coins?[^'\"]*)['\"]/is", $respHtml, $m)) {
                if (preg_match('/([\d\.,]+)\s*Coins?/i', $m[1], $am)) {
                    $amount = (float)str_replace(',', '', $am[1]);
                }
            }
            $success = true;
        }
        // P3: plain text
        if (!$success && preg_match('/([\d\.,]+)\s+Coins?\s+has been added/i', $respHtml, $m)) {
            $amount = (float)str_replace(',', '', $m[1]);
            $success = true;
        }
        // P4: balance delta
        if (!$success) {
            sleep(1);
            $balAfter = fetch_balance_from_faucet();
            if ($balAfter !== null && $info['balance'] !== null) {
                $delta = (float)$balAfter - (float)$info['balance'];
                if ($delta > 0) { $success = true; $amount = $delta; }
            }
        }
        // Extract error msg kalo gagal
        if (!$success) {
            $errMsg = '';
            if (preg_match("/Swal\.fire\s*\(\s*\{.*?html:\s*['\"]([^'\"]+)['\"]/is", $respHtml, $m)) {
                $errMsg = strip_tags($m[1]);
            } elseif (preg_match("/Swal\.fire\s*\(\s*\{.*?title:\s*['\"]([^'\"]+)['\"]/is", $respHtml, $m)) {
                $errMsg = $m[1];
            }
            if ($errMsg !== '') {
                return ['status' => 'fail', 'http' => $httpCode, 'msg' => substr(trim($errMsg), 0, 80)];
            }
        }
    }

    if ($success) return ['status' => 'success', 'amount' => $amount];
    return ['status' => 'fail', 'http' => $httpCode];
}

// ═══════════ WATCH ADS (PTC) ═══════════
function attempt_watch_claim(){
    $r1 = req(SITE_PTC);
    $html = $r1['body'];
    $httpP = (int)($r1['code'] ?? 0);

    if ($httpP === 404) return ['status' => 'error', 'msg' => '/ptc 404'];
    if (is_login_page($html)) return ['status' => 'session_invalid'];
    if (preg_match('/no ads? (available|left)|all ads? (watched|completed)/i', $html)) {
        return ['status' => 'error', 'msg' => 'no ads available'];
    }

    $adLinks = [];
    if (preg_match_all("#location\.href='https://cryptofuture\.co\.in/(ptc/(?:window|iframe)/(\d+))'#i", $html, $m, PREG_SET_ORDER)) {
        foreach ($m as $row) {
            $adLinks[] = ['url' => SITE_BASE . '/' . $row[1], 'id' => $row[2], 'type' => strpos($row[1], 'window') !== false ? 'window' : 'iframe'];
        }
    }
    if (empty($adLinks)) return ['status' => 'error', 'msg' => 'no ad links found'];

    $ad = $adLinks[0];
    $viewUrl = $ad['url'];
    $adId = $ad['id'];

    push_log("opening ad #{$adId} ({$ad['type']})", 'in');
    banner();

    $r2 = req($viewUrl, 'GET', null, ['Referer: ' . SITE_PTC]);
    $viewHtml = $r2['body'];

    if (is_login_page($viewHtml)) return ['status' => 'session_invalid'];

    $csrf = '';
    if (preg_match('/name="csrf_token_name"[^>]*value="([^"]+)"/i', $viewHtml, $m)) {
        $csrf = $m[1];
    }
    if ($csrf === '') $csrf = $GLOBALS['COOKIES']['csrf_cookie_name'] ?? '';
    if ($csrf === '') return ['status' => 'error', 'msg' => 'CSRF not found on view page'];

    $timer = 10;
    if (preg_match('/(?:var|let|const)\s+timer\s*=\s*(\d+)/i', $viewHtml, $m)) {
        $timer = (int)$m[1];
    }

    push_log("watching {$timer}s...", 'i');
    banner();

    $wait = $timer + rand(1, 3);
    live_tick($wait, "ad #{$adId}");

    $verifyUrl = SITE_PTC_VERIFY . $adId;
    $post = http_build_query(['csrf_token_name' => $csrf]);
    $h = ['Origin: ' . SITE_BASE, 'Referer: ' . $viewUrl];

    $r3 = req($verifyUrl, 'POST', $post, $h);
    $respHtml = (string)($r3['body'] ?? '');
    $httpCode = (int)($r3['code'] ?? 0);

    $success = false;
    $amount = 0.0;

    if (preg_match("/Swal\.fire\s*\(\s*\{.*?html\s*:\s*['\"]([^'\"]*\d+[^'\"]*Coins?[^'\"]*)['\"]/is", $respHtml, $m)) {
        if (preg_match('/([\d\.,]+)\s*Coins?/i', $m[1], $am)) {
            $amount = (float)str_replace(',', '', $am[1]);
            $success = true;
        }
    }
    if (!$success && preg_match('/([\d\.,]+)\s+Coins?\s+has been added/i', $respHtml, $m)) {
        $amount = (float)str_replace(',', '', $m[1]);
        $success = true;
    }
    if (!$success) {
        sleep(1);
        $r4 = req(SITE_PTC);
        if (preg_match("/Swal\.fire\s*\(\s*\{.*?html\s*:\s*['\"]([^'\"]*\d+[^'\"]*Coins?[^'\"]*)['\"]/is", $r4['body'], $m)) {
            if (preg_match('/([\d\.,]+)\s*Coins?/i', $m[1], $am)) {
                $amount = (float)str_replace(',', '', $am[1]);
                $success = true;
            }
        }
    }

    if ($success) return ['status' => 'success', 'amount' => $amount];
    return ['status' => 'fail', 'http' => $httpCode];
}

// ═══════════ MENU ═══════════
function menu_ui($cfg){
    $apikey_set = !empty($cfg['apikey']);
    $email_set  = !empty($cfg['email']);

    echo fg(51) . "╔" . str_repeat("═", 62) . "╗" . RST . "\n";
    echo box_line(fg(213) . BOLD . "MENU" . RST);
    echo box_div();
    echo box_line(fg(46) . "  1" . RST . ". Start Faucet Claim");
    echo box_line(fg(46) . "  2" . RST . ". Start Watch Ads Claim");
    echo box_line(fg(226) . "  3" . RST . ". Login/Relogin via Email  " . ($email_set ? fg(46) . "[" . $GLOBALS['_email'] . "]" . RST : fg(196) . "[not logged]" . RST));
    echo box_line(fg(226) . "  4" . RST . ". Set Waryono API Key  " . ($apikey_set ? fg(46) . "[set]" . RST : fg(196) . "[missing]" . RST));
    echo box_line(fg(226) . "  5" . RST . ". Change Email");
    echo box_line(fg(213) . "  6" . RST . ". Refresh Balance");
    echo fg(51) . "╚" . str_repeat("═", 62) . "╝" . RST . "\n";
    echo "\n  " . fg(51) . "›" . RST . " Choose: ";
    return trim(fgets(STDIN));
}

function menu_login(&$cfg){
    $savedEmail = $cfg['email'] ?? '';
    if ($savedEmail !== '') {
        echo "\n" . fg(213) . BOLD . "─── LOGIN VIA EMAIL ───" . RST . "\n";
        echo fg(240) . "Saved: {$savedEmail}" . RST . "\n";
        echo fg(51) . "  Use saved? (y/n) [y]: " . RST;
        $ans = strtolower(trim(fgets(STDIN)));
        if ($ans === '' || $ans === 'y') {
            $email = $savedEmail;
        } else {
            echo fg(51) . "  Email: " . RST;
            $email = trim(fgets(STDIN));
        }
    } else {
        echo "\n" . fg(213) . BOLD . "─── LOGIN VIA EMAIL ───" . RST . "\n";
        echo fg(51) . "  Email: " . RST;
        $email = trim(fgets(STDIN));
    }

    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        push_log("invalid email", 'er');
        sleep(2);
        return;
    }

    $apikey = $cfg['apikey'] ?? '';
    if (!$apikey) {
        push_log("apikey missing (menu 4) — turnstile gak bisa di-solve", 'er');
        sleep(2);
        return;
    }

    $cfg['email'] = $email;
    $GLOBALS['_email'] = $email;
    save_config($cfg);

    $GLOBALS['COOKIES'] = [];
    push_log("logging in as {$email}...", 'in');
    banner();

    $res = login_with_email($email, $apikey);

    if ($res['ok']) {
        $cfg['cookies'] = $GLOBALS['COOKIES'];
        save_config($cfg);
        push_log("login OK | bal: " . $GLOBALS['_balance'] . " Coins", 'ok');
        banner();
    } else {
        push_log("login FAIL: " . ($res['msg'] ?? '?'), 'er');
        banner();
    }
    sleep(2);
}

function menu_set_apikey(&$cfg){
    echo "\n" . fg(213) . BOLD . "─── WARYONO API KEY ───" . RST . "\n";
    echo fg(240) . "Get from https://waryono.my.id" . RST . "\n\n";
    echo fg(51) . "  Key: " . RST;
    $k = trim(fgets(STDIN));
    if ($k === '') { push_log("empty — cancelled", 'wr'); return; }
    $cfg['apikey'] = $k;
    save_config($cfg);
    push_log("apikey saved", 'ok');
    sleep(1);
}

function menu_change_email(&$cfg){
    echo "\n" . fg(213) . BOLD . "─── CHANGE EMAIL ───" . RST . "\n";
    echo fg(51) . "  New email: " . RST;
    $e = trim(fgets(STDIN));
    if (!filter_var($e, FILTER_VALIDATE_EMAIL)) {
        push_log("invalid email", 'er');
        sleep(2);
        return;
    }
    $cfg['email'] = $e;
    $GLOBALS['_email'] = $e;
    save_config($cfg);
    push_log("email updated: {$e}", 'ok');
    sleep(1);
}

function menu_refresh_balance(){
    push_log("refreshing balance...", 'in');
    banner();
    $bal = fetch_balance_from_faucet();
    if ($bal !== null) {
        push_log("balance: " . $GLOBALS['_balance'] . " Coins", 'ok');
    } else {
        push_log("balance not detected — cek debug_balance.html", 'er');
    }
    sleep(2);
}

// ═══════════ BOT LOOPS ═══════════
function run_faucet($apikey, &$cfg){
    $GLOBALS['_mode'] = 'faucet';

    push_log("probing /faucet...", 'in');
    banner();
    $r = req(SITE_FAUCET);
    $html = $r['body'];

    if (is_cf_challenge($html)) {
        push_log("CF challenge — try relogin", 'wr');
        banner();
        return;
    }

    if (strpos($html, 'id="fauform"') === false) {
        if (!empty($cfg['email'])) {
            push_log("session expired — auto relogin...", 'wr');
            banner();
            $res = login_with_email($cfg['email'], $apikey);
            if ($res['ok']) {
                $cfg['cookies'] = $GLOBALS['COOKIES'];
                save_config($cfg);
                push_log("relogin OK", 'ok');
                banner();
                sleep(1);
                $r = req(SITE_FAUCET);
                $html = $r['body'];
            } else {
                push_log("relogin FAIL: " . ($res['msg'] ?? '?'), 'er');
                banner();
                sleep(2);
                return;
            }
        }
        if (strpos($html, 'id="fauform"') === false) {
            push_log("still no fauform — abort", 'er');
            banner();
            sleep(2);
            return;
        }
    }

    $bal = scrape_balance($html);
    if ($bal !== null) {
        $GLOBALS['_balance'] = number_format((float)$bal, 0);
    }

    push_log("faucet page OK | bal: " . $GLOBALS['_balance'], 'ok');
    banner();

    $round = 0;
    while (true) {
        if ($GLOBALS['_claims'] >= MAX_CLAIMS) {
            $GLOBALS['_stage'] = 'LIMIT';
            push_log("max claims reached", 'g');
            banner();
            break;
        }
        if ($GLOBALS['_fails'] >= FAIL_LIMIT) {
            $GLOBALS['_stage'] = 'FAIL LIMIT';
            push_log("fail limit reached", 'er');
            banner();
            break;
        }

        $round++;
        $GLOBALS['_stage'] = "ROUND #{$round}";
        banner();

        $res = attempt_faucet_claim($apikey);
        $st = $res['status'];

        if ($st === 'success') {
            $amt = (float)$res['amount'];
            $GLOBALS['_claims']++;
            $GLOBALS['_fails'] = 0;
            $GLOBALS['_earned'] += $amt;
            if ($amt > 0) {
                $cur = (float)str_replace(',', '', $GLOBALS['_balance']);
                $GLOBALS['_balance'] = number_format($cur + $amt, 0);
            }
            push_log("+" . number_format($amt, 4) . " | bal: " . $GLOBALS['_balance'], 'ok');
            banner();
            live_tick(CLAIM_CD, "next");
        } elseif ($st === 'cooldown') {
            $w = (int)$res['wait'];
            push_log("cooldown " . fmt_time($w), 'wr');
            banner();
            live_tick($w, "cooldown");
        } elseif ($st === 'cf') {
            push_log("CF challenge — abort", 'wr');
            banner();
            break;
        } elseif ($st === 'session_invalid') {
            $GLOBALS['_fails']++;
            push_log("session expired — auto relogin...", 'er');
            banner();
            if (!empty($cfg['email'])) {
                $res2 = login_with_email($cfg['email'], $apikey);
                if ($res2['ok']) {
                    $cfg['cookies'] = $GLOBALS['COOKIES'];
                    save_config($cfg);
                    $GLOBALS['_fails'] = 0;
                    push_log("relogin OK", 'ok');
                    banner();
                    sleep(1);
                    continue;
                }
            }
            live_tick(RETRY_CD, "retry");
        } else {
            $GLOBALS['_fails']++;
            $err = $res['msg'] ?? ('HTTP ' . ($res['http'] ?? '?'));
            push_log("fail: " . substr($err, 0, 60), 'er');
            banner();
            live_tick(RETRY_CD, "retry");
        }
    }

    $GLOBALS['_stage'] = 'DONE';
    banner();
}

function run_watch(&$cfg, $apikey){
    $GLOBALS['_mode'] = 'watch';

    push_log("probing /ptc...", 'in');
    banner();
    $r = req(SITE_PTC);
    if (is_cf_challenge($r['body'])) {
        push_log("CF challenge — abort", 'er');
        banner();
        return;
    }
    if (is_login_page($r['body'])) {
        if (!empty($cfg['email'])) {
            push_log("session expired — auto relogin...", 'wr');
            banner();
            $res = login_with_email($cfg['email'], $apikey);
            if ($res['ok']) {
                $cfg['cookies'] = $GLOBALS['COOKIES'];
                save_config($cfg);
                push_log("relogin OK", 'ok');
                banner();
                sleep(1);
            } else {
                push_log("relogin FAIL", 'er');
                banner();
                sleep(2);
                return;
            }
        } else {
            push_log("not logged in — login first", 'er');
            banner();
            sleep(2);
            return;
        }
    }

    fetch_balance_from_faucet();

    push_log("/ptc OK | bal: " . $GLOBALS['_balance'], 'ok');
    banner();

    $round = 0;
    while (true) {
        if ($GLOBALS['_claims'] >= MAX_CLAIMS) {
            $GLOBALS['_stage'] = 'LIMIT';
            push_log("max claims reached", 'g');
            banner();
            break;
        }
        if ($GLOBALS['_fails'] >= FAIL_LIMIT) {
            $GLOBALS['_stage'] = 'FAIL LIMIT';
            push_log("fail limit reached", 'er');
            banner();
            break;
        }

        $round++;
        $GLOBALS['_stage'] = "ROUND #{$round}";
        banner();

        $res = attempt_watch_claim();
        $st = $res['status'];

        if ($st === 'success') {
            $amt = (float)$res['amount'];
            $GLOBALS['_claims']++;
            $GLOBALS['_fails'] = 0;
            $GLOBALS['_earned'] += $amt;
            if ($amt > 0) {
                $cur = (float)str_replace(',', '', $GLOBALS['_balance']);
                $GLOBALS['_balance'] = number_format($cur + $amt, 0);
            }
            push_log("+" . number_format($amt, 4) . " | bal: " . $GLOBALS['_balance'], 'ok');
            banner();
            live_tick(15, "next");
        } elseif ($st === 'session_invalid') {
            $GLOBALS['_fails']++;
            push_log("session expired — relogin...", 'er');
            banner();
            if (!empty($cfg['email'])) {
                $res2 = login_with_email($cfg['email'], $apikey);
                if ($res2['ok']) {
                    $cfg['cookies'] = $GLOBALS['COOKIES'];
                    save_config($cfg);
                    $GLOBALS['_fails'] = 0;
                    push_log("relogin OK", 'ok');
                    banner();
                    sleep(1);
                    continue;
                }
            }
            live_tick(RETRY_CD, "retry");
        } else {
            $GLOBALS['_fails']++;
            $err = $res['msg'] ?? '?';
            push_log("fail: " . substr($err, 0, 60), 'er');
            banner();
            live_tick(RETRY_CD, "retry");
        }
    }

    $GLOBALS['_stage'] = 'DONE';
    banner();
}

// ═══════════ MAIN ═══════════
if (function_exists('pcntl_signal')) {
    pcntl_async_signals(true);
    pcntl_signal(SIGINT, function () {
        echo "\n\n" . fg(226) . "[!] SIGINT — keluar aman" . RST . "\n";
        exit(0);
    });
}

$cfg = load_config();
if (!empty($cfg['email'])) $GLOBALS['_email'] = $cfg['email'];
if (!empty($cfg['cookies']) && is_array($cfg['cookies'])) {
    $GLOBALS['COOKIES'] = $cfg['cookies'];
}

while (true) {
    banner();
    $ch = menu_ui($cfg);

    switch ($ch) {
        case '1':
            $apikey = $cfg['apikey'] ?? '';
            if (!$apikey) { push_log("set apikey dulu (menu 4)", 'wr'); sleep(2); break; }
            if (empty($cfg['email'])) { push_log("login via email dulu (menu 3)", 'wr'); sleep(2); break; }
            if (empty($GLOBALS['COOKIES'])) {
                push_log("no cookies — auto login...", 'wr');
                banner();
                $res = login_with_email($cfg['email'], $apikey);
                if ($res['ok']) {
                    $cfg['cookies'] = $GLOBALS['COOKIES'];
                    save_config($cfg);
                } else {
                    push_log("login fail: " . ($res['msg'] ?? '?'), 'er');
                    sleep(2);
                    break;
                }
            }
            run_faucet($apikey, $cfg);
            break;

        case '2':
            $apikey = $cfg['apikey'] ?? '';
            if (empty($cfg['email'])) { push_log("login via email dulu (menu 3)", 'wr'); sleep(2); break; }
            if (empty($GLOBALS['COOKIES'])) {
                push_log("no cookies — auto login...", 'wr');
                banner();
                $res = login_with_email($cfg['email'], $apikey);
                if ($res['ok']) {
                    $cfg['cookies'] = $GLOBALS['COOKIES'];
                    save_config($cfg);
                } else {
                    push_log("login fail: " . ($res['msg'] ?? '?'), 'er');
                    sleep(2);
                    break;
                }
            }
            run_watch($cfg, $apikey);
            break;

        case '3': menu_login($cfg); break;
        case '4': menu_set_apikey($cfg); break;
        case '5': menu_change_email($cfg); break;
        case '6': menu_refresh_balance(); break;

        default:
            push_log("invalid choice", 'wr');
            sleep(1);
    }
}
