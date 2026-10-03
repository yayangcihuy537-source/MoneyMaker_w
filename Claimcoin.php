<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');

@ob_implicit_flush(true);
@ob_end_flush();
if (function_exists('gc_enable')) gc_enable();
if (function_exists('ini_set')) {
    @ini_set('output_buffering', '0');
    @ini_set('implicit_flush', '1');
}

$configFile = "config.json";

/* =============== ANSI COLORS =============== */
const RESET  = "\033[0m";
const BOLD   = "\033[1m";
const DIM    = "\033[2m";
const RED    = "\033[1;31m";
const GREEN  = "\033[1;32m";
const YELLOW = "\033[1;33m";
const BLUE   = "\033[1;34m";
const MAGENTA= "\033[1;35m";
const CYAN   = "\033[1;36m";
const WHITE  = "\033[1;37m";
const GRAY   = "\033[0;90m";
const NEON   = "\033[38;5;46m";
const NEON_P = "\033[38;5;201m";
const NEON_C = "\033[38;5;51m";
const NEON_Y = "\033[38;5;226m";

/* =============== CONFIG =============== */
const api_url    = "https://claimcoin.in";
const solver_in  = "https://api.waryono.my.id/in.php";
const solver_out = "https://api.waryono.my.id/res.php";
const SITEKEY_TURNSTILE = "0x4AAAAAAB6ZWSg9eOY7OVRl";
const DEFAULT_UA = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36";

/* =============== LIMITS =============== */
const MAX_SOLVER_RETRY   = 5;
const MAX_CONSEC_ERROR   = 6;
const MAX_CLAIM_PER_RUN  = 200;
const MAX_UNKNOWN_BEFORE_STOP = 3; // 3x unknown beruntun → exit

/* =============== UI HELPERS =============== */

function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function line($left, $right, $lw = 62) {
    $plainL = preg_replace('/\033\[[0-9;]*m/', '', $left);
    $plainR = preg_replace('/\033\[[0-9;]*m/', '', $right);
    $len = strlen($plainL) + strlen($plainR);
    $pad = max(0, $lw - $len - 2);
    return GRAY . "║" . RESET . " " . $left . str_repeat(" ", $pad) . $right . " " . GRAY . "║" . RESET;
}

function lineCenter($text, $lw = 62) {
    $plain = preg_replace('/\033\[[0-9;]*m/', '', $text);
    $len = strlen($plain);
    $left = (int)floor(($lw - $len) / 2);
    $right = $lw - $len - $left;
    return GRAY . "║" . RESET . str_repeat(" ", max(0, $left)) . $text . str_repeat(" ", max(0, $right)) . GRAY . "║" . RESET;
}

function printHeader($title = "CLAIMCOIN.IN — AUTO CLAIM BOT [COOKIE MODE]") {
    echo "\n";
    echo NEON . "  ╔" . str_repeat("═", 60) . "╗" . RESET . "\n";
    echo lineCenter(NEON . BOLD . $title . RESET) . "\n";
    echo lineCenter(GRAY . "ScriptMaker @bgiyannn | Waryono Solver | ClaimCoin" . RESET) . "\n";
    echo NEON . "  ╚" . str_repeat("═", 60) . "╝" . RESET . "\n";
}

function roundHeader($n, $time) {
    $t = "─── ROUND #$n ─── $time ───";
    echo "\n" . CYAN . "  ╭" . str_repeat("─", 55) . "╮" . RESET . "\n";
    echo CYAN . "  │  " . WHITE . BOLD . $t . RESET . "\n";
    echo CYAN . "  ╰" . str_repeat("─", 55) . "╯" . RESET . "\n";
}

function roundFooter() {
    echo CYAN . "  ╰" . str_repeat("─", 55) . "╯" . RESET . "\n";
}

function logInfo($tag, $msg) { printf("  %s[%s]%s %s\n", CYAN, $tag, RESET, $msg); }
function logOk($tag, $msg)   { printf("  %s[%s]%s %s%s%s\n", GREEN, $tag, RESET, GREEN, $msg, RESET); }
function logWarn($tag, $msg) { printf("  %s[%s]%s %s%s%s\n", YELLOW, $tag, RESET, YELLOW, $msg, RESET); }
function logErr($tag, $msg)  { printf("  %s[%s]%s %s%s%s\n", RED, $tag, RESET, RED, $msg, RESET); }

function timer($seconds, $prefix = "  waiting") {
    $wait_time = (int)$seconds;
    if ($wait_time < 1) return;
    $frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'];
    $fc = count($frames);
    $cf = 0;
    while ($wait_time > 0) {
        $start = microtime(true);
        while ((microtime(true) - $start) < 1) {
            $h = floor($wait_time / 3600);
            $m = floor(($wait_time % 3600) / 60);
            $s = $wait_time % 60;
            $tf = sprintf('%02d:%02d:%02d', $h, $m, $s);
            echo "  " . GRAY . $prefix . RESET . " " . NEON_Y . $tf . RESET . " " . CYAN . $frames[$cf] . RESET . "\r";
            usleep(100000);
            $cf = ($cf + 1) % $fc;
            if ((microtime(true) - $start) >= 1) break;
        }
        $wait_time--;
    }
    echo "\r" . str_repeat(" ", 60) . "\r";
}

function shortCookie($c) {
    if (strlen($c) <= 40) return $c;
    return substr($c, 0, 20) . "..." . substr($c, -15);
}

function dump_html($html, $label = "faucet") {
    $fn = "debug_{$label}_" . date("Ymd_His") . ".html";
    @file_put_contents($fn, $html);
    if (file_exists($fn)) {
        logInfo("DEBUG", "HTML dumped → " . GRAY . $fn . RESET . " (" . strlen($html) . " bytes)");
        return $fn;
    }
    return null;
}

/* =============== CONFIG =============== */

function saveConfig($configFile, $data) {
    file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
}

function getConfig($configFile) {
    if (!file_exists($configFile)) {
        echo "\n";
        echo NEON . "  ╔" . str_repeat("═", 60) . "╗" . RESET . "\n";
        echo lineCenter(YELLOW . BOLD . "SETUP AWAL — COOKIE MODE" . RESET) . "\n";
        echo NEON . "  ╚" . str_repeat("═", 60) . "╝" . RESET . "\n\n";

        echo "  " . GRAY . "Cara ambil cookies:" . RESET . "\n";
        echo "  " . GRAY . "  1. Login claimcoin.in di browser" . RESET . "\n";
        echo "  " . GRAY . "  2. F12 → Application → Cookies → https://claimcoin.in" . RESET . "\n";
        echo "  " . GRAY . "  3. Copy semua jadi format: name=value; name=value; ..." . RESET . "\n\n";

        echo "  " . WHITE . "Solver API Key" . GRAY . " : " . RESET; $apikey = trim(fgets(STDIN));
        echo "  " . WHITE . "Cookies       " . GRAY . " : " . RESET; $cookies = trim(fgets(STDIN));
        echo "  " . WHITE . "User-Agent    " . GRAY . " (blank=default): " . RESET; $ua = trim(fgets(STDIN));
        if ($ua === '') $ua = DEFAULT_UA;

        $data = [
            "apikey"     => $apikey,
            "cookies"    => $cookies,
            "user_agent" => $ua
        ];
        saveConfig($configFile, $data);
        echo "\n  " . GREEN . "✓ Config saved → $configFile" . RESET . "\n";
        sleep(1);
        return $data;
    }
    return json_decode(file_get_contents($configFile), true);
}

/* =============== HTTP =============== */

$GLOBALS['cookies_raw'] = "";
$GLOBALS['user_agent']  = DEFAULT_UA;

function wkwk($url, $payload = null, $headers = [], $method = "POST", $redirects = 8, $overrideCookie = null) {
    global $cookies_raw, $user_agent;

    $curl_tries = 0;
    $curl_max = 3;

    while ($curl_tries++ < $curl_max) {
        $ch = curl_init();
        $opts = [
            CURLOPT_URL            => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_FOLLOWLOCATION => false,
            CURLOPT_SSL_VERIFYHOST => 1,
            CURLOPT_SSL_VERIFYPEER => true,
            CURLOPT_HTTPHEADER     => $headers,
            CURLOPT_CONNECTTIMEOUT => 15,
            CURLOPT_TIMEOUT        => 30,
            CURLOPT_LOW_SPEED_LIMIT => 100,
            CURLOPT_LOW_SPEED_TIME  => 20,
            CURLOPT_HEADER         => true,
            CURLOPT_USERAGENT      => $user_agent,
            CURLOPT_ENCODING       => '',
        ];
        $cookieToSend = $overrideCookie !== null ? $overrideCookie : $cookies_raw;
        if ($cookieToSend && strpos($url, 'claimcoin.in') !== false) {
            $opts[CURLOPT_COOKIE] = $cookieToSend;
        }
        if ($method === "POST") {
            $opts[CURLOPT_POST] = true;
            if (is_string($payload)) {
                $opts[CURLOPT_POSTFIELDS] = $payload;
            } else {
                $wantJson = false;
                foreach ($headers as $h) {
                    if (stripos($h, 'content-type:') === 0 && stripos($h, 'json') !== false) {
                        $wantJson = true;
                        break;
                    }
                }
                $opts[CURLOPT_POSTFIELDS] = $wantJson
                    ? json_encode($payload)
                    : http_build_query($payload);
            }
        }
        curl_setopt_array($ch, $opts);
        $response = curl_exec($ch);
        $err = curl_error($ch);
        $code = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
        $hsize = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
        curl_close($ch);

        if ($response === false || $err) {
            if ($curl_tries >= $curl_max) {
                echo "\n  " . RED . "curl err (max retry): $err" . RESET . "\n";
                return ["body" => "", "code" => 0, "headers" => ""];
            }
            echo "\n  " . YELLOW . "curl err: $err" . RESET . ", retry ($curl_tries/$curl_max)...\n";
            sleep(3);
            continue;
        }

        $headers_raw = substr($response, 0, $hsize);
        $body        = substr($response, $hsize);

        if (in_array($code, [301, 302, 303, 307, 308]) && $redirects > 0) {
            if (preg_match('/^location:\s*(.+)$/mi', $headers_raw, $m)) {
                $loc = trim($m[1]);
                if (strpos($loc, 'http') !== 0) {
                    $base = (strpos($url, 'claimcoin.in') !== false) ? api_url : '';
                    $loc = rtrim($base, '/') . '/' . ltrim($loc, '/');
                }
                return wkwk($loc, null, $headers, "GET", $redirects - 1, $overrideCookie);
            }
        }

        return ["body" => $body, "code" => $code, "headers" => $headers_raw];
    }

    return ["body" => "", "code" => 0, "headers" => ""];
}

function base_headers($extra = []) {
    $h = [
        'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        'sec-ch-ua: "Chromium";v="127", "Not)A;Brand";v="99"',
        'sec-ch-ua-mobile: ?1',
        'sec-ch-ua-platform: "Android"',
        'upgrade-insecure-requests: 1',
        'sec-fetch-site: same-origin',
        'sec-fetch-mode: navigate',
        'sec-fetch-dest: document',
        'dnt: 1',
    ];
    return array_merge($h, $extra);
}

function ajax_headers($extra = []) {
    $h = [
        'accept: application/json, text/javascript, */*; q=0.01',
        'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        'x-requested-with: XMLHttpRequest',
        'sec-ch-ua: "Chromium";v="127", "Not)A;Brand";v="99"',
        'sec-ch-ua-mobile: ?1',
        'sec-ch-ua-platform: "Android"',
        'sec-fetch-site: same-origin',
        'sec-fetch-mode: cors',
        'sec-fetch-dest: empty',
        'priority: u=1, i',
    ];
    return array_merge($h, $extra);
}

function detect_cf($html) {
    return (
        strpos($html, 'Just a moment') !== false ||
        strpos($html, 'cf-challenge') !== false ||
        strpos($html, 'challenge-platform') !== false ||
        strpos($html, '_cf_chl_opt') !== false ||
        strpos($html, 'cf-browser-verification') !== false
    );
}

/* =============== BYPASS =============== */

function try_fetch($path, $extraHeaders = [], $label = "") {
    $r = wkwk(api_url . $path, null, base_headers($extraHeaders), "GET");
    if ($r["body"] !== "" && !detect_cf($r["body"])) return $r;

    $r = wkwk(api_url . $path, null, ajax_headers($extraHeaders), "GET");
    if ($r["body"] !== "" && !detect_cf($r["body"])) return $r;

    $r = wkwk(api_url . $path, null, array_merge([
        'accept: */*',
        'x-requested-with: XMLHttpRequest',
    ], $extraHeaders), "GET");
    if ($r["body"] !== "" && !detect_cf($r["body"])) return $r;

    if ($label) logErr("BYPASS", "$label → semua attempt kena CF");
    return null;
}

/* =============== SOLVER =============== */

function parse_solver_response($raw) {
    $raw = trim($raw);
    if ($raw === '') return ['status'=>'error','id'=>'','code'=>'EMPTY_RESPONSE'];

    $j = json_decode($raw, true);
    if (is_array($j)) {
        $req = isset($j['request']) ? trim((string)$j['request']) : '';
        $st  = isset($j['status'])  ? (int)$j['status'] : null;
        if ($st === 0 || (is_string($req) && strpos($req, 'ERROR_') === 0)) {
            return ['status'=>'error','id'=>'','code'=>$req ?: 'UNKNOWN'];
        }
        if ($req !== '' && strpos($req, 'ERROR_') !== 0 && strpos($req, 'CAPCHA_NOT_READY') === false) {
            return ['status'=>'ok','id'=>$req,'code'=>''];
        }
        if (strpos($req, 'CAPCHA_NOT_READY') !== false) {
            return ['status'=>'error','id'=>'','code'=>'CAPCHA_NOT_READY'];
        }
        return ['status'=>'error','id'=>'','code'=>'UNKNOWN_JSON'];
    }

    if (strpos($raw, 'OK|') === 0) {
        $id = trim(substr($raw, 3));
        return ['status'=>'ok','id'=>$id,'code'=>''];
    }
    if (strpos($raw, 'ERROR_') === 0) {
        $parts = explode('|', $raw, 2);
        return ['status'=>'error','id'=>'','code'=>$parts[0]];
    }
    if (strpos($raw, 'CAPCHA_NOT_READY') !== false) {
        return ['status'=>'error','id'=>'','code'=>'CAPCHA_NOT_READY'];
    }
    return ['status'=>'error','id'=>'','code'=>$raw];
}

function solve_captcha($apikey, $method, $sitekey, $action = "", $attempt = 1) {
    if ($attempt > MAX_SOLVER_RETRY) {
        logErr("solver", "retry limit reached (" . MAX_SOLVER_RETRY . "x) — stop");
        return null;
    }

    $headers = ["Content-Type: application/json"];
    $body = [
        "apikey"  => $apikey,
        "methods" => $method,
        "domain"  => "https://claimcoin.in",
        "sitekey" => $sitekey,
        "json"    => 1
    ];
    if ($action !== "") $body["action"] = $action;

    $req = wkwk(solver_in, $body, $headers);
    $parsed = parse_solver_response($req["body"]);

    if ($parsed['status'] === 'error') {
        $errCode = $parsed['code'];
        $fatal = [
            "ERROR_WRONG_USER_KEY","ERROR_KEY_DOES_NOT_EXIST","ERROR_ZERO_BALANCE",
            "ERROR_WRONG_METHOD","ERROR_METHOD_NOT_SPECIFIED","ERROR_NO_SUCH_METHOD",
            "ERROR_BAD_PARAMETERS","ERROR_EMPTY_IMAGE","ERROR_DATABASE_CONNECTION_FAILED","ERROR_UNKNOWN"
        ];
        if (in_array($errCode, $fatal)) {
            logErr("solver", $errCode);
            if ($errCode === "ERROR_KEY_DOES_NOT_EXIST") logInfo("solver", "apikey kosong / ga kekirim");
            elseif ($errCode === "ERROR_WRONG_USER_KEY") logInfo("solver", "apikey salah, regen di bot waryono");
            elseif ($errCode === "ERROR_ZERO_BALANCE") logInfo("solver", "saldo habis, topup dulu");
            return null;
        }
        if ($errCode === "ERROR_TOO_MANY_REQUESTS") {
            logWarn("solver", "TOO_MANY_REQUESTS, retry (" . $attempt . "/" . MAX_SOLVER_RETRY . ")");
            sleep(3);
            return solve_captcha($apikey, $method, $sitekey, $action, $attempt + 1);
        }
        logWarn("solver", "err: $errCode, retry (" . $attempt . "/" . MAX_SOLVER_RETRY . ")");
        sleep(3);
        return solve_captcha($apikey, $method, $sitekey, $action, $attempt + 1);
    }

    $id = $parsed['id'];
    if (!$id) {
        logErr("solver", "no id in response");
        sleep(3);
        return solve_captcha($apikey, $method, $sitekey, $action, $attempt + 1);
    }

    logInfo("solver", "task id = " . CYAN . $id . RESET);

    $poll = 0;
    while ($poll++ < 40) {
        timer(5, "  poll $poll ");
        $res = wkwk(solver_out . "?apikey=" . urlencode($apikey) . "&action=get&id=" . urlencode($id) . "&json=1", null, [], "GET");
        $p = parse_solver_response($res["body"]);

        if ($p['status'] === 'error') {
            $e = $p['code'];
            if ($e === "CAPCHA_NOT_READY" || $e === "CAPTCHA_NOT_READY") continue;
            if ($e === "ERROR_CAPTCHA_UNSOLVABLE") {
                logWarn("solver", "UNSOLVABLE, retry (" . $attempt . "/" . MAX_SOLVER_RETRY . ")");
                sleep(1);
                return solve_captcha($apikey, $method, $sitekey, $action, $attempt + 1);
            }
            if (in_array($e, ["WRONG_CAPTCHA_ID","ERROR_SOLVE_PENDING","ERROR_BAD_REQUEST","INTENAL_SERVER_ERROR","INTERNAL_SERVER_ERROR"])) {
                logWarn("solver", "$e, retry (" . $attempt . "/" . MAX_SOLVER_RETRY . ")");
                sleep(1);
                return solve_captcha($apikey, $method, $sitekey, $action, $attempt + 1);
            }
            if (in_array($e, ["ERROR_BAD_PARAMETERS","ERROR_WRONG_USER_KEY","ERROR_KEY_DOES_NOT_EXIST","ERROR_ZERO_BALANCE"])) {
                logErr("solver", "fatal: $e");
                return null;
            }
            logWarn("solver", "poll err: $e, retry (" . $attempt . "/" . MAX_SOLVER_RETRY . ")");
            sleep(1);
            return solve_captcha($apikey, $method, $sitekey, $action, $attempt + 1);
        }
        if ($p['id']) return $p['id'];
    }
    logErr("solver", "poll timeout");
    return null;
}

/* =============== HTML PARSER (ROBUST) =============== */

function extract_csrf($html) {
    if (preg_match('/name="csrf_token_name"\s+value="([^"]+)"/i', $html, $m)) return $m[1];
    if (preg_match('/name="csrf_token_name"\s+id="[^"]*"\s+value="([^"]+)"/i', $html, $m)) return $m[1];
    if (preg_match('/"csrf_token_name"\s*:\s*"([^"]+)"/i', $html, $m)) return $m[1];
    return null;
}

function extract_sitekey($html) {
    if (preg_match('/data-sitekey="([^"]+)"/i', $html, $m)) return $m[1];
    if (preg_match('/sitekey["\']?\s*[:=]\s*["\']([^"\']+)["\']/i', $html, $m)) return $m[1];
    return SITEKEY_TURNSTILE;
}

/**
 * parse_faucet_state — multi-pattern.
 * Return:
 *   ["ready" => true,  "wait" => 0,        "pattern" => "..."]
 *   ["ready" => false, "wait" => N,        "pattern" => "..."]
 *   ["ready" => false, "wait" => -1,       "unauthed" => true]
 *   ["ready" => false, "wait" => 0,        "unknown" => true]   <- parser gagal baca
 */
function parse_faucet_state($html) {
    if ($html === '' || $html === null) {
        return ["ready" => false, "wait" => 0, "unknown" => true, "reason" => "empty_body"];
    }

    // 1. siap? beberapa variasi marker
    $ready_markers = [
        'cc-countdown-ready',
        'countdown-ready',
        '>READY<',
        '>Ready<',
        'class="cc-countdown cc-countdown-ready"',
        'Next Claim',
    ];
    // cek marker yang bener (yang utama cc-countdown-ready)
    if (strpos($html, 'cc-countdown-ready') !== false) {
        return ["ready" => true, "wait" => 0, "pattern" => "cc-countdown-ready"];
    }

    // 2. countdown minute:second (format 1) — dengan <b> tags
    if (preg_match('/<b[^>]*id=["\']minute["\'][^>]*>(\d+)<\/b>\s*[:.]\s*<b[^>]*id=["\']second["\'][^>]*>(\d+)<\/b>/i', $html, $m)) {
        $wait = ((int)$m[1]) * 60 + (int)$m[2];
        return ["ready" => false, "wait" => $wait, "pattern" => "b minute/second"];
    }

    // 3. countdown dengan id tapi tanpa <b>
    if (preg_match('/id=["\']minute["\'][^>]*>(\d+)<[^>]*>.*?id=["\']second["\'][^>]*>(\d+)/is', $html, $m)) {
        $wait = ((int)$m[1]) * 60 + (int)$m[2];
        return ["ready" => false, "wait" => $wait, "pattern" => "id minute/second"];
    }

    // 4. "wait=NN" di script JS
    if (preg_match('/var\s+wait\s*=\s*(\d+)\s*-\s*1/i', $html, $m)) {
        return ["ready" => false, "wait" => (int)$m[1], "pattern" => "var wait"];
    }

    // 5. countdown dari data-attribute
    if (preg_match('/data-countdown=["\'](\d+)["\']/i', $html, $m)) {
        return ["ready" => false, "wait" => (int)$m[1], "pattern" => "data-countdown"];
    }

    // 6. login page
    if (strpos($html, 'cc-auth-body') !== false || strpos($html, 'name="password"') !== false) {
        return ["ready" => false, "wait" => -1, "unauthed" => true];
    }

    // fallback: UNKNOWN
    return ["ready" => false, "wait" => 0, "unknown" => true, "reason" => "no_pattern_matched"];
}

function parse_reward($html) {
    if (preg_match("/'([\d.]+)\s*tokens has been added to your balance'/i", $html, $m)) return $m[1];
    if (preg_match('/Good job!.*?([\d.]+)\s*tokens/i', $html, $m)) return $m[1];
    if (preg_match('/([\d.]+)\s*tokens has been added/i', $html, $m)) return $m[1];
    return null;
}

function parse_balance($html) {
    if (preg_match('/Available Balance<\/span>\s*<h3>([\d.,]+)\s*tokens?<\/h3>/i', $html, $m)) return $m[1];
    if (preg_match('/Available Balance.*?([\d.,]+)\s*tokens?/si', $html, $m)) return $m[1];
    if (preg_match('/balance[^0-9]{1,20}([\d.,]+)\s*tokens?/i', $html, $m)) return $m[1];
    return null;
}

function is_limit_reached($html) {
    $needles = [
        'reached the daily limit','you have reached the daily limit','daily faucet limit reached',
        'you have reached your limit','faucet daily limit reached','daily claim limit reached',
        'no more claims today','come back tomorrow','limit for today has been reached',
        'you reached your daily','exceeded your daily','exceeded the daily','daily limit exceeded',
        'out of tokens for today','faucet is empty for today',
    ];
    foreach ($needles as $n) if (stripos($html, $n) !== false) return true;
    return false;
}

/* =============== BALANCE =============== */

function fetch_balance() {
    logInfo("BALANCE", "GET /dashboard ...");
    $r = try_fetch("/dashboard", ['referer: ' . api_url . '/faucet'], "/dashboard");
    if ($r === null) return ["ok" => false, "reason" => "cf", "balance" => null];
    if (strpos($r["body"], 'cc-auth-body') !== false || strpos($r["body"], 'name="password"') !== false) {
        return ["ok" => false, "reason" => "unauthed", "balance" => null];
    }
    $bal = parse_balance($r["body"]);
    if ($bal === null) {
        // dashboard accessed, tapi balance ga keparse
        return ["ok" => true, "reason" => "ok", "balance" => null, "balance_missing" => true];
    }
    return ["ok" => true, "reason" => "ok", "balance" => $bal];
}

/* =============== CLAIM =============== */

function post_verify_with_bypass($payload) {
    logInfo("POST", "/faucet/verify (ajax)");
    $r = wkwk(api_url . "/faucet/verify", $payload, ajax_headers([
        'content-type: application/x-www-form-urlencoded; charset=UTF-8',
        'origin: ' . api_url,
        'referer: ' . api_url . '/faucet',
    ]), "POST");
    if (!detect_cf($r["body"])) return $r;

    $r = wkwk(api_url . "/faucet/verify", $payload, [
        'accept: */*',
        'content-type: application/x-www-form-urlencoded',
        'origin: ' . api_url,
        'referer: ' . api_url . '/faucet',
        'x-requested-with: XMLHttpRequest',
    ], "POST");
    if (!detect_cf($r["body"])) return $r;

    $r = wkwk(api_url . "/faucet/verify", $payload, [
        'content-type: application/x-www-form-urlencoded',
        'x-requested-with: XMLHttpRequest',
    ], "POST");
    if (!detect_cf($r["body"])) return $r;

    $r = wkwk(api_url . "/faucet/verify", $payload, [
        'content-type: application/x-www-form-urlencoded',
        'accept: application/json, text/plain, */*',
        'origin: ' . api_url,
        'x-requested-with: XMLHttpRequest',
    ], "POST");
    return $r;
}

function claim_once($apikey) {
    logInfo("GET", "/faucet");
    $r = try_fetch("/faucet", ['referer: ' . api_url . '/dashboard'], "/faucet");
    if ($r === null) return ["state" => "cf"];

    $html = $r["body"];

    if (strpos($html, 'cc-auth-body') !== false || strpos($html, 'name="password"') !== false) {
        logErr("FAUCET", "session expired");
        return ["state" => "unauthed"];
    }

    $st = parse_faucet_state($html);

    if (!empty($st["unauthed"])) return ["state" => "unauthed"];

    // UNKNOWN state: parser gagal baca
    if (!empty($st["unknown"])) {
        logWarn("FAUCET", "parser tidak mengenali HTML (reason: " . ($st["reason"] ?? "?") . ")");
        $fn = dump_html($html, "faucet_unknown");
        if ($fn) logInfo("FAUCET", "coba buka file ini buat cek struktur terbaru");
        return ["state" => "unknown"];
    }

    if (!$st["ready"]) {
        if ($st["wait"] > 0) {
            $w = max(3, (int)$st["wait"]);
            logWarn("FAUCET", "COOLDOWN | next in " . $w . "s (pattern: " . ($st["pattern"] ?? "?") . ")");
            echo "  " . GRAY . "Cooldown: " . RESET . NEON_Y . sprintf("%02d:%02d", floor($w/60), $w%60) . RESET . "\n";
            timer($w + 2, "  waiting ");
            return ["state" => "notready"];
        }
        if (is_limit_reached($html)) {
            logWarn("FAUCET", "Daily limit reached");
            return ["state" => "limit"];
        }
        // fallback di bawah ini harusnya ga kena lagi (udah ada unknown handler)
        logWarn("FAUCET", "not ready, wait 10s (fallback)");
        timer(12, "  waiting ");
        return ["state" => "notready"];
    }

    $csrf = extract_csrf($html);
    if (!$csrf && preg_match('/csrf_cookie_name=([a-f0-9]{32})/i', $r["headers"], $m)) $csrf = $m[1];
    if (!$csrf) {
        logErr("FAUCET", "csrf not found");
        dump_html($html, "faucet_nocsrf");
        return ["state" => "error"];
    }
    $sitekey = extract_sitekey($html);

    logOk("FAUCET", "status: READY" . (isset($st["pattern"]) ? " (pattern: " . $st["pattern"] . ")" : ""));
    logInfo("FAUCET", "csrf   : " . GRAY . substr($csrf, 0, 16) . "..." . RESET);
    logInfo("FAUCET", "sitekey: " . GRAY . $sitekey . RESET);
    logInfo("FAUCET", "method : " . CYAN . "turnstile" . RESET);

    $token = solve_captcha($apikey, "turnstile", $sitekey, "faucet");
    if (!$token) { logErr("CAPTCHA", "failed"); return ["state" => "error"]; }

    $payload = http_build_query([
        "csrf_token_name"       => $csrf,
        "captcha"               => "turnstile",
        "cf-turnstile-response" => $token
    ]);

    $res = post_verify_with_bypass($payload);
    $rbody = $res["body"];

    if (detect_cf($rbody)) {
        logErr("CLAIM", "CF challenge di verify (gagal semua attempt)");
        return ["state" => "cf"];
    }

    if (is_limit_reached($rbody)) {
        return ["state" => "limit"];
    }

    $reward = parse_reward($rbody);
    if ($reward !== null) {
        return ["state" => "claimed", "reward" => $reward];
    }

    $st2 = parse_faucet_state($rbody);
    if (!$st2["ready"] && $st2["wait"] > 0) {
        return ["state" => "notready", "wait" => $st2["wait"]];
    }
    if ($st2["ready"]) {
        return ["state" => "claimed", "reward" => "?"];
    }

    logErr("CLAIM", "unknown response");
    dump_html($rbody, "verify_unknown");
    return ["state" => "error"];
}

/* =============== MENU =============== */

function mainMenu($cookiePreview, $solverName = "WARYONO") {
    echo "\n";
    echo "  " . WHITE . BOLD . "Solver" . RESET . " : " . CYAN . $solverName . RESET . "\n";
    echo "  " . WHITE . BOLD . "Cookie" . RESET . " : " . CYAN . $cookiePreview . RESET . "\n";
    echo "  " . WHITE . BOLD . "Mode  " . RESET . " : " . CYAN . "COOKIE + BYPASS" . RESET . "\n";
    echo "  " . GRAY . str_repeat("─", 58) . RESET . "\n";
    echo "    " . NEON . "[1]" . RESET . " Lanjut\n";
    echo "    " . NEON . "[2]" . RESET . " Edit config\n";
    echo "    " . NEON . "[3]" . RESET . " Reset\n";
    echo "  " . GRAY . ">> " . RESET;
    return trim(fgets(STDIN));
}

/* =============== MAIN =============== */

clear();

if (function_exists('pcntl_signal')) {
    pcntl_signal(SIGINT, function() {
        echo "\n\n  " . YELLOW . "Interrupted. Bye." . RESET . "\n";
        exit(0);
    });
    pcntl_async_signals(true);
}

$config = getConfig($configFile);

while (true) {
    $apikey     = $config['apikey'];
    $cookies    = $config['cookies'] ?? "";
    $user_agent = $config['user_agent'] ?? DEFAULT_UA;

    $GLOBALS['cookies_raw'] = $cookies;
    $GLOBALS['user_agent']  = $user_agent;

    printHeader();
    $choice = mainMenu(shortCookie($cookies));

    if ($choice === "2") {
        @unlink($configFile);
        $config = getConfig($configFile);
        continue;
    }
    if ($choice === "3") {
        @unlink($configFile);
        @unlink('cookies.txt');
        echo "\n  " . GREEN . "✓ Config & cookies dihapus." . RESET . "\n";
        sleep(1);
        clear();
        $config = getConfig($configFile);
        continue;
    }

    clear();
    printHeader();

    echo "\n  " . WHITE . BOLD . "Solver" . RESET . " : " . CYAN . "WARYONO" . RESET . "\n";
    echo "  " . WHITE . BOLD . "Cookie" . RESET . " : " . CYAN . shortCookie($cookies) . RESET . "\n\n";

    logInfo("START", "cek balance dulu sebelum faucet");
    $balRes = fetch_balance();

    if (!$balRes["ok"]) {
        if ($balRes["reason"] === "cf") {
            echo "\n  " . RED . "✗ Cloudflare challenge di /dashboard — semua bypass gagal." . RESET . "\n";
            echo "  " . GRAY . "Update cookie dengan yang fresh dari browser." . RESET . "\n";
        } elseif ($balRes["reason"] === "unauthed") {
            echo "\n  " . RED . "✗ ci_session expired. Login ulang di browser, copy cookie baru." . RESET . "\n";
        } else {
            echo "\n  " . RED . "✗ Unknown error." . RESET . "\n";
        }
        echo "\n  " . GRAY . "Tekan ENTER untuk balik ke menu..." . RESET;
        fgets(STDIN);
        clear();
        continue;
    }

    $balance = $balRes["balance"];
    $balMissing = !empty($balRes["balance_missing"]);

    echo "\n";
    echo NEON . "  ╔" . str_repeat("═", 60) . "╗" . RESET . "\n";
    echo lineCenter(GREEN . BOLD . "✓ SESSION VALID" . RESET) . "\n";
    echo NEON . "  ╠" . str_repeat("═", 60) . "╣" . RESET . "\n";
    echo line(WHITE . "Mode    " . RESET . " : " . CYAN . "COOKIE + BYPASS" . RESET, "") . "\n";
    echo line(WHITE . "Solver  " . RESET . " : " . CYAN . "WARYONO" . RESET, "") . "\n";
    echo line(WHITE . "Cookie  " . RESET . " : " . GRAY . shortCookie($cookies) . RESET, "") . "\n";

    if ($balMissing) {
        echo line(WHITE . "Balance " . RESET . " : " . YELLOW . "not parsed (layout beda?)" . RESET, "") . "\n";
    } else {
        echo line(WHITE . "Balance " . RESET . " : " . NEON_Y . ($balance !== null ? number_format((float)str_replace(',', '', $balance), 2) . " tokens" : "?") . RESET, "") . "\n";
    }
    echo NEON . "  ╚" . str_repeat("═", 60) . "╝" . RESET . "\n\n";

    $total_claims = 0;
    $consecutive_errors = 0;
    $consecutive_unknown = 0;
    $round = 0;

    while (true) {
        if ($total_claims >= MAX_CLAIM_PER_RUN) {
            logWarn("MAIN", "cap " . MAX_CLAIM_PER_RUN . " claims tercapai, exit.");
            break;
        }

        $round++;
        roundHeader($round, date("H:i:s"));

        $r = claim_once($apikey);

        switch ($r["state"]) {
            case "claimed":
                $total_claims++;
                $consecutive_unknown = 0;
                $rewardStr = ($r["reward"] === "?" ? "?" : number_format((float)$r["reward"], 4));
                $b = fetch_balance();
                $balStr = ($b["ok"] && $b["balance"] !== null) ? number_format((float)str_replace(',', '', $b["balance"]), 2) . " tokens" : "(not parsed)";
                echo "\n";
                logOk("CLAIM", "✓ +$rewardStr tokens | balance: $balStr");
                logInfo("TOTAL", "claims: " . GREEN . $total_claims . RESET);
                roundFooter();
                $consecutive_errors = 0;
                timer(mt_rand(2, 4), "  cooldown ");
                break;

            case "notready":
                roundFooter();
                $consecutive_errors = 0;
                $consecutive_unknown = 0;
                break;

            case "unknown":
                roundFooter();
                $consecutive_unknown++;
                logWarn("MAIN", "unknown state (x$consecutive_unknown/" . MAX_UNKNOWN_BEFORE_STOP . ")");
                if ($consecutive_unknown >= MAX_UNKNOWN_BEFORE_STOP) {
                    logWarn("MAIN", "HTML berubah / parser ga nyampe. Balik ke menu.");
                    echo "  " . GRAY . "Cek file debug_faucet_unknown_*.html di folder ini." . RESET . "\n";
                    echo "  " . GRAY . "Tekan ENTER untuk balik ke menu..." . RESET;
                    fgets(STDIN);
                    clear();
                    continue 3;
                }
                timer(10, "  retry ");
                break;

            case "limit":
                roundFooter();
                echo "\n";
                logWarn("MAIN", "──────────────────────────────────────");
                logWarn("MAIN", "DAILY LIMIT REACHED — STOP");
                logWarn("MAIN", "Total claims session ini: " . YELLOW . $total_claims . RESET);
                logWarn("MAIN", "Coba lagi besok, atau kembali ke menu.");
                logWarn("MAIN", "──────────────────────────────────────");
                echo "\n  " . GRAY . "Tekan ENTER untuk balik ke menu..." . RESET;
                fgets(STDIN);
                clear();
                continue 3;

            case "unauthed":
                roundFooter();
                echo "\n";
                logErr("MAIN", "ci_session expired — update cookie");
                echo "  " . GRAY . "Balik ke menu..." . RESET . "\n";
                sleep(3);
                continue 3;

            case "cf":
                roundFooter();
                echo "\n";
                logErr("MAIN", "cf challenge — update cookie");
                echo "  " . GRAY . "Balik ke menu..." . RESET . "\n";
                sleep(3);
                continue 3;

            case "error":
            default:
                roundFooter();
                $consecutive_errors++;
                logErr("MAIN", "error (x$consecutive_errors/" . MAX_CONSEC_ERROR . "), retry 15s");
                if ($consecutive_errors >= MAX_CONSEC_ERROR) {
                    logWarn("MAIN", "terlalu banyak error beruntun, balik ke menu");
                    $consecutive_errors = 0;
                    continue 3;
                } else {
                    timer(15, "  retry ");
                }
                break;
        }
    }
}
