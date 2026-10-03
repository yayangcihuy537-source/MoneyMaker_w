<?php
/**
 * FireFaucet — Faucet Only Bot (Hardened)
 *   [1] Start faucet claim
 *   [2] Edit config
 *   [3] Reset
 *   [0] Exit
 * Captcha: hCaptcha only
 */

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');
@ob_implicit_flush(true);
@ob_end_flush();
@ini_set('output_buffering', '0');
@ini_set('implicit_flush', '1');

$configFile = "config.json";

/* ═══════════════════════════════════════════════════
   COLORS
   ═══════════════════════════════════════════════════ */
$yellow = "\033[1;33m";
$green  = "\033[1;32m";
$red    = "\033[1;31m";
$cyan   = "\033[1;36m";
$white  = "\033[1;37m";
$orange = "\033[38;5;208m";
$neonY  = "\033[38;5;226m";
$neonG  = "\033[38;5;46m";
$neonC  = "\033[38;5;51m";
$gray   = "\033[0;90m";
$reset  = "\033[0m";

/* ═══════════════════════════════════════════════════
   CONSTANTS
   ═══════════════════════════════════════════════════ */
const HOST         = "https://firefaucet.win";
const SOLVER_IN    = "https://api.waryono.my.id/in.php";
const SOLVER_OUT   = "https://api.waryono.my.id/res.php";
const HCAPTCHA_KEY = "034eb992-02f4-4cd7-8f90-5dfb05fb21a2";

const TG_GROUP = "https://t.me/+RInZ35ML2GhjM2I1";
const TG_TAG   = "@MoneyMaker_w";

/* ═══════════════════════════════════════════════════
   UI
   ═══════════════════════════════════════════════════ */
function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function timer($sec, $label = "  waiting") {
    global $gray, $cyan, $neonY, $reset;
    if (!is_numeric($sec) || $sec < 1) $sec = 5;
    $end = time() + $sec;
    $frames = ['⣾','⣽','⣻','⢿','⡿','⣟','⣯','⣷'];
    $fc = count($frames); $cf = 0;
    while (($left = $end - time()) > 0) {
        $h = floor($left/3600); $m = floor(($left%3600)/60); $s = $left%60;
        echo "  " . $gray . $label . $reset . " " . $neonY . sprintf('%02d:%02d:%02d', $h,$m,$s) . $reset . " " . $cyan . $frames[$cf] . $reset . "\r";
        usleep(100000);
        $cf = ($cf+1) % $fc;
    }
    echo "\r" . str_repeat(" ", 60) . "\r";
}

function info($tag, $msg)  { global $cyan,$reset; printf("  %s[%s]%s %s\n", $cyan, $tag, $reset, $msg); }
function ok($tag, $msg)    { global $green,$reset; printf("  %s[%s]%s %s%s%s\n", $green, $tag, $reset, $green, $msg, $reset); }
function warn($tag, $msg)  { global $yellow,$reset; printf("  %s[%s]%s %s%s%s\n", $yellow, $tag, $reset, $yellow, $msg, $reset); }
function err($tag, $msg)   { global $red,$reset; printf("  %s[%s]%s %s%s%s\n", $red, $tag, $reset, $red, $msg, $reset); }

function cstrip($s) { return preg_replace('/\033\[[0-9;]*m/', '', (string)$s); }

function lineBox($left, $right, $w = 62) {
    global $gray, $reset;
    $lp = cstrip($left); $rp = cstrip($right);
    $pad = max(0, $w - strlen($lp) - strlen($rp) - 2);
    return $gray . "║" . $reset . " " . $left . str_repeat(" ", $pad) . $right . " " . $gray . "║" . $reset;
}

function lineCenterBox($text, $w = 62) {
    global $gray, $reset;
    $p = cstrip($text); $len = strlen($p);
    $l = (int)floor(($w - $len) / 2);
    $r = $w - $len - $l;
    return $gray . "║" . $reset . str_repeat(" ", max(0, $l)) . $text . str_repeat(" ", max(0, $r)) . $gray . "║" . $reset;
}

function boxClaim($label, $rows) {
    global $yellow, $white, $green, $cyan, $reset;
    echo $yellow . "  ╔" . str_repeat("═", 58) . "╗" . $reset . "\n";
    echo $yellow . "  ║ " . $white . str_pad("Task: " . $label, 56) . $reset . $yellow . "║" . $reset . "\n";
    foreach ($rows as $k => $v) {
        $plain = cstrip($v);
        $pad = 42 - strlen($plain);
        if ($pad < 0) $pad = 0;
        echo $yellow . "  ║ " . $cyan . str_pad($k . ":", 14) . $reset . $green . $v . str_repeat(" ", $pad) . $reset . $yellow . "║" . $reset . "\n";
    }
    echo $yellow . "  ╚" . str_repeat("═", 58) . "╝" . $reset . "\n";
}

function banner($mode = "FAUCET ONLY") {
    global $orange, $cyan, $gray, $white, $neonY, $neonC, $reset;
    echo "\n";
    echo $orange . "  ╔" . str_repeat("═", 60) . "╗" . $reset . "\n";
    echo lineCenterBox($orange . "\033[1m" . "FIREFAUCET.WIN — AUTO CLAIM BOT" . $reset) . "\n";
    echo lineCenterBox($gray . "Mode: " . $mode . " | Fixed: " . TG_TAG . $reset) . "\n";
    echo lineCenterBox($cyan . "Join: " . $neonC . TG_GROUP . $reset) . "\n";
    echo $orange . "  ╚" . str_repeat("═", 60) . "╝" . $reset . "\n";
}

/* ═══════════════════════════════════════════════════
   CONFIG
   ═══════════════════════════════════════════════════ */
function saveConfig($f, $d) { file_put_contents($f, json_encode($d, JSON_PRETTY_PRINT)); }

function getConfig($f) {
    if (!file_exists($f)) {
        echo "\n  \033[1;33mSetup awal — input config\033[0m\n\n";
        echo "  Solver API Key : "; $ak = trim(fgets(STDIN));
        echo "  Cookies        : "; $ck = trim(fgets(STDIN));
        echo "  User-Agent     : "; $ua = trim(fgets(STDIN));
        if ($ua === '') $ua = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36";

        $d = [
            "apikey"     => $ak,
            "cookies"    => $ck,
            "user_agent" => $ua
        ];
        saveConfig($f, $d);
        echo "\n  \033[1;32m✓ Config saved.\033[0m\n";
        sleep(1);
        return $d;
    }
    return json_decode(file_get_contents($f), true);
}

/* ═══════════════════════════════════════════════════
   HTTP
   ═══════════════════════════════════════════════════ */
function normalize_cookie($raw) {
    $raw = preg_replace('/[\r\n\t]+/', ' ', $raw);
    $parts = array_filter(array_map('trim', explode(';', trim($raw))));
    $clean = [];
    foreach ($parts as $p) {
        if (strpos($p, '=') === false) continue;
        list($k, $v) = explode('=', $p, 2);
        if (trim($k) === '') continue;
        $clean[] = trim($k) . '=' . trim($v);
    }
    return implode('; ', $clean);
}

$GLOBALS['cookies']    = "";
$GLOBALS['user_agent'] = "";
$GLOBALS['apikey']     = "";

function req($url, $post = null, $extraHeaders = [], $method = null) {
    global $cookies, $user_agent, $gray, $reset;

    $m = $method ?: ($post !== null ? "POST" : "GET");
    $maxTries = 3;
    $tries = 0;
    $lastErr = "";

    while ($tries++ < $maxTries) {
        $ch = curl_init();
        $headers = array_merge([
            'User-Agent: ' . $user_agent,
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer: ' . HOST . '/',
            'Connection: keep-alive',
        ], $extraHeaders);

        $opts = [
            CURLOPT_URL            => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_SSL_VERIFYPEER => true,
            CURLOPT_SSL_VERIFYHOST => 2,
            CURLOPT_CONNECTTIMEOUT => 20,
            CURLOPT_TIMEOUT        => 45,
            CURLOPT_COOKIE         => normalize_cookie($cookies),
            CURLOPT_COOKIEFILE     => 'cookie.txt',
            CURLOPT_COOKIEJAR      => 'cookie.txt',
            CURLOPT_HTTPHEADER     => $headers,
            CURLOPT_HEADER         => true,
            CURLOPT_ENCODING       => '',
            CURLOPT_IPRESOLVE      => CURL_IPRESOLVE_V4,
            CURLOPT_TCP_KEEPALIVE  => 1,
        ];
        if ($m === "POST") {
            $opts[CURLOPT_POST] = true;
            $opts[CURLOPT_POSTFIELDS] = is_string($post) ? $post : http_build_query($post);
        }
        curl_setopt_array($ch, $opts);
        $response = curl_exec($ch);
        $err = curl_error($ch);
        $code = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
        $hsize = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
        curl_close($ch);

        if ($response === false || $err) {
            $lastErr = $err;
            $retryable = (
                stripos($err, 'Connection reset') !== false ||
                stripos($err, 'timed out') !== false ||
                stripos($err, 'Operation was aborted') !== false ||
                stripos($err, 'Empty reply') !== false ||
                stripos($err, 'Recv failure') !== false ||
                stripos($err, 'Send failure') !== false ||
                stripos($err, 'SSL') !== false ||
                stripos($err, 'handshake') !== false ||
                stripos($err, 'resolve') !== false
            );

            if ($retryable && $tries < $maxTries) {
                echo "  " . $gray . "connection error, retry $tries/$maxTries: " . substr($err, 0, 60) . $reset . "\n";
                sleep(3);
                continue;
            }

            echo "  " . $gray . "curl fatal: " . substr($err, 0, 100) . $reset . "\n";
            return ["body" => "", "code" => 0, "headers" => "", "err" => $err];
        }

        return [
            "body"    => substr($response, $hsize),
            "code"    => $code,
            "headers" => substr($response, 0, $hsize),
            "err"     => ""
        ];
    }
    return ["body" => "", "code" => 0, "headers" => "", "err" => "max retries: $lastErr"];
}

/* ═══════════════════════════════════════════════════
   PAGE DETECTORS — multi-marker
   ═══════════════════════════════════════════════════ */

/**
 * Deteksi halaman redirect ke login — multi marker.
 * Cek title, meta refresh, HTTP 30x body, dll.
 */
function isRedirecting($html, $headers = "") {
    // 1. title redirect (case-insensitive, spasi fleksibel)
    if (preg_match('/<title>\s*Redirecting[^<]*<\/title>/i', $html)) return true;

    // 2. meta refresh ke login/root
    if (preg_match('/<meta[^>]*http-equiv=["\']?refresh["\']?[^>]*url=\s*["\']?\/?(?:login|auth)/i', $html)) return true;

    // 3. body cuma berisi "Redirecting..." / "Redirect"
    $plain = trim(strip_tags($html));
    if (strlen($plain) < 60 && preg_match('/^redirecting/i', $plain)) return true;

    // 4. header Location ke /login
    if ($headers && preg_match('/^location:\s*\/?(?:login|auth)/mi', $headers)) return true;

    return false;
}

/**
 * Deteksi halaman login — multi marker.
 */
function isLoginPage($html) {
    $markers = [
        'au-page-login',
        'au-form',
        'au-title-solo',
        'Welcome back',
    ];
    foreach ($markers as $mk) {
        if (stripos($html, $mk) !== false) return true;
    }
    // form login punya username + password
    if (strpos($html, 'name="username"') !== false && strpos($html, 'name="password"') !== false) return true;
    return false;
}

/* ═══════════════════════════════════════════════════
   PARSER — multi-pattern, tolerant
   ═══════════════════════════════════════════════════ */

function extractSidebarCsrf($html) {
    if (preg_match('/name="csrf_token_sidebar"\s+value="([^"]+)"/i', $html, $m)) return $m[1];
    if (preg_match('/name="csrf_token"\s+value="([^"]+)"/i', $html, $m)) return $m[1];
    if (preg_match('/<input[^>]*value="([^"]+)"[^>]*name="csrf_token(?:_sidebar)?"/i', $html, $m)) return $m[1];
    if (preg_match('/"csrf_token"\s*:\s*"([^"]+)"/i', $html, $m)) return $m[1];
    if (preg_match('/<meta[^>]*name="csrf-token"[^>]*content="([^"]+)"/i', $html, $m)) return $m[1];
    return null;
}

function getBalanceFromHome($html) {
    if (preg_match('/<div[^>]*color:\s*#00a8ff[^>]*>\s*<b>([\d.,]+)<\/b>/i', $html, $m)) return $m[1];
    if (preg_match('/acp-balance-value[^>]*>\s*([\d.,]+)/i', $html, $m)) return $m[1];
    if (preg_match('/id="acp[_-]?balance"[^>]*>\s*([\d.,]+)/i', $html, $m)) return $m[1];
    if (preg_match('/\bACP\b[^0-9]{0,40}([\d.,]+)/i', $html, $m)) return $m[1];
    if (preg_match('/(?:Balance|balance)[^0-9]{0,40}([\d.,]{2,})/i', $html, $m)) return $m[1];
    return null;
}

function getUsernameFromHome($html) {
    if (preg_match('/<span class="username-text">([^<]+)<\/span>/i', $html, $m)) return trim($m[1]);
    if (preg_match('/<div class="hub-username">([^<]+)<\/div>/i', $html, $m)) return trim($m[1]);
    if (preg_match('/class="welcome[^"]*"[^>]*>([^<]{2,32})</i', $html, $m)) return trim($m[1]);
    return null;
}

function getFuelFromHome($html) {
    if (preg_match('/autoclaim-fuel-total">\s*([\d,]+)/i', $html, $m)) return $m[1];
    if (preg_match('/fuel[^0-9]{0,40}([\d,]+)/i', $html, $m)) return $m[1];
    return null;
}

function detectProvider($html) {
    if (preg_match('/value="hcaptcha"/i', $html)) return "hcaptcha";
    if (preg_match('/value="turnstile"/i', $html)) return "turnstile";
    if (preg_match('/value="recaptcha"/i', $html)) return "recaptcha";
    if (preg_match('/selected-captcha["\']?\s*[=:]\s*["\']?hcaptcha/i', $html)) return "hcaptcha";
    if (preg_match('/selected-captcha["\']?\s*[=:]\s*["\']?turnstile/i', $html)) return "turnstile";
    if (preg_match('/selected-captcha["\']?\s*[=:]\s*["\']?recaptcha/i', $html)) return "recaptcha";
    if (stripos($html, 'hCaptcha') !== false) return "hcaptcha";
    if (stripos($html, 'Turnstile') !== false) return "turnstile";
    if (stripos($html, 'reCAPTCHA') !== false) return "recaptcha";
    return null;
}

/**
 * Extract cooldown.
 *   Return int  (>=0) kalau berhasil
 *   Return null      kalau TIDAK dikenali (caller harus skip)
 */
function extractCooldown($html) {
    // cek dulu apakah ada tombol claim aktif → artinya READY (wait 0)
    $readyMarkers = [
        'faucet-claim-btn',
        'Claim My ACP',
        'claim-button',
        'faucet-btn-text',
    ];
    $hasReady = false;
    foreach ($readyMarkers as $mk) {
        if (stripos($html, $mk) !== false) { $hasReady = true; break; }
    }

    // 1. startCountdown('#faucet-countdown', parseInt('123'))
    if (preg_match("/startCountdown\('#faucet-countdown',\s*parseInt\('(\d+)'\)/i", $html, $m)) return (int)$m[1];
    // 2. startCountdown("#...", 123)
    if (preg_match('/startCountdown\(["\'][^"\']*["\'],\s*(\d+)/i', $html, $m)) return (int)$m[1];
    // 3. data-countdown
    if (preg_match('/data-countdown=["\'](\d+)["\']/i', $html, $m)) return (int)$m[1];
    // 4. data-wait
    if (preg_match('/data-wait=["\'](\d+)["\']/i', $html, $m)) return (int)$m[1];
    // 5. var timer/wait/seconds
    if (preg_match('/var\s+(?:timer|wait|seconds)\s*=\s*(\d+)/i', $html, $m)) return (int)$m[1];
    // 6. "wait": 123
    if (preg_match('/"wait"\s*:\s*(\d+)/i', $html, $m)) return (int)$m[1];
    // 7. "cooldown": 123
    if (preg_match('/"(?:cooldown|cooldown_seconds)"\s*:\s*(\d+)/i', $html, $m)) return (int)$m[1];
    // 8. generik: angka 2-5 digit deket 'countdown'/'wait'
    if (preg_match('/(?:countdown|wait)[^0-9]{0,40}(\d{2,5})/i', $html, $m)) return (int)$m[1];

    // kalau ga nemu countdown tapi ADA tombol claim → ready (wait 0)
    if ($hasReady) return 0;

    // bener-bener ga bisa dibaca
    return null;
}

/* ═══════════════════════════════════════════════════
   SOLVER (hCaptcha only)
   ═══════════════════════════════════════════════════ */
function parseSolverResp($raw) {
    $raw = trim($raw);
    if ($raw === '') return ['status'=>'error','id'=>'','code'=>'EMPTY'];
    $j = json_decode($raw, true);
    if (is_array($j)) {
        $req = isset($j['request']) ? trim((string)$j['request']) : '';
        $st  = isset($j['status']) ? (int)$j['status'] : null;
        if ($st === 0 || (is_string($req) && strpos($req, 'ERROR_') === 0)) {
            return ['status'=>'error','id'=>'','code'=>$req ?: 'UNKNOWN'];
        }
        if ($req !== '' && strpos($req, 'ERROR_') !== 0 && strpos($req, 'CAPCHA_NOT_READY') === false) {
            return ['status'=>'ok','id'=>$req,'code'=>''];
        }
        if (strpos($req, 'CAPCHA_NOT_READY') !== false) {
            return ['status'=>'error','id'=>'','code'=>'NOT_READY'];
        }
        return ['status'=>'error','id'=>'','code'=>'UNKNOWN'];
    }
    if (strpos($raw, 'OK|') === 0) return ['status'=>'ok','id'=>trim(substr($raw,3)),'code'=>''];
    if (strpos($raw, 'ERROR_') === 0) {
        $p = explode('|', $raw, 2);
        return ['status'=>'error','id'=>'','code'=>$p[0]];
    }
    return ['status'=>'error','id'=>'','code'=>$raw];
}

function solveHcaptcha($sitekey, $pageurl = "https://firefaucet.win/faucet/") {
    global $apikey;

    $body = [
        "apikey"  => $apikey,
        "methods" => "hcaptcha",
        "domain"  => "https://firefaucet.win",
        "sitekey" => $sitekey,
        "json"    => 1,
        "pageurl" => $pageurl
    ];

    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL            => SOLVER_IN,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => json_encode($body),
        CURLOPT_HTTPHEADER     => ["Content-Type: application/json"],
        CURLOPT_TIMEOUT        => 30,
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_SSL_VERIFYHOST => 2,
        CURLOPT_IPRESOLVE      => CURL_IPRESOLVE_V4,
    ]);
    $resp = curl_exec($ch);
    curl_close($ch);

    $parsed = parseSolverResp($resp);
    if ($parsed['status'] === 'error') {
        err("solver", $parsed['code']);
        return ["token" => false, "attempts" => 0];
    }
    $id = $parsed['id'];
    info("solver", "task $id (hcaptcha)");

    $attempts = 0;
    $errCount = 0;
    while ($attempts < 30) {
        $attempts++;
        sleep(3);
        $pollUrl = SOLVER_OUT . "?apikey=" . urlencode($apikey) . "&action=get&id=" . urlencode($id) . "&json=1";
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL            => $pollUrl,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT        => 30,
            CURLOPT_SSL_VERIFYPEER => true,
            CURLOPT_SSL_VERIFYHOST => 2,
            CURLOPT_IPRESOLVE      => CURL_IPRESOLVE_V4,
        ]);
        $poll = curl_exec($ch);
        curl_close($ch);

        $p = parseSolverResp($poll);
        if ($p['status'] === 'ok' && $p['id']) {
            return ["token" => $p['id'], "attempts" => $attempts];
        }
        if ($p['code'] === 'NOT_READY' || $p['code'] === 'CAPCHA_NOT_READY') {
            echo "\r  " . $GLOBALS['gray'] . "processing ($attempts)..." . $GLOBALS['reset'];
            continue;
        }
        $errCount++;
        if ($errCount >= 5) {
            err("solver", "5 errors in row: " . $p['code']);
            return ["token" => false, "attempts" => $attempts];
        }
    }
    err("solver", "max attempts");
    return ["token" => false, "attempts" => $attempts];
}

/* ═══════════════════════════════════════════════════
   CHECK BALANCE
   ═══════════════════════════════════════════════════ */
function checkBalance() {
    info("CHECK", "GET / (verify cookie + balance)");
    $r = req(HOST . "/");
    $html = $r["body"];

    if ($html === "") {
        return ["ok"=>false, "reason"=>"error", "detail"=>$r["err"] ?: "empty response"];
    }
    if (isRedirecting($html, $r["headers"])) {
        return ["ok"=>false, "reason"=>"expired", "detail"=>"server redirect ke login"];
    }
    if (isLoginPage($html)) {
        return ["ok"=>false, "reason"=>"expired", "detail"=>"login page (cookie mati)"];
    }
    if (stripos($html, 'Just a moment') !== false || stripos($html, 'challenge-platform') !== false) {
        return ["ok"=>false, "reason"=>"cf", "detail"=>"Cloudflare challenge"];
    }

    $csrf = extractSidebarCsrf($html);
    if (!$csrf) {
        $loggedInMarkers = [
            'logout', '/logout', 'username-text', 'hub-username',
            'acp-balance', 'side-nav-btns'
        ];
        $looksLoggedIn = false;
        foreach ($loggedInMarkers as $mk) {
            if (stripos($html, $mk) !== false) { $looksLoggedIn = true; break; }
        }
        if ($looksLoggedIn) {
            return ["ok"=>false, "reason"=>"csrf_missing",
                    "detail"=>"csrf token tidak ketemu di HTML (tapi kelihatan logged-in). "
                            . "Format HTML mungkin berubah."];
        }
        return ["ok"=>false, "reason"=>"expired",
                "detail"=>"bukan halaman logged-in (csrf & marker absen)"];
    }

    return [
        "ok"     => true,
        "reason" => "ok",
        "user"   => getUsernameFromHome($html),
        "acp"    => getBalanceFromHome($html),
        "fuel"   => getFuelFromHome($html),
        "csrf"   => $csrf,
    ];
}

function printBalanceBox($b) {
    global $cyan, $white, $neonY, $orange, $reset;
    echo "\n";
    echo "\033[38;5;46m" . "  ╔" . str_repeat("═", 60) . "╗" . $reset . "\n";
    echo lineCenterBox("\033[38;5;46m\033[1m" . "✓ SESSION VALID" . $reset) . "\n";
    echo "\033[38;5;46m" . "  ╠" . str_repeat("═", 60) . "╣" . $reset . "\n";
    echo lineBox($white . "User   " . $reset . " : " . $cyan . ($b['user'] ?: "?") . $reset, "") . "\n";
    echo lineBox($white . "ACP    " . $reset . " : " . $neonY . ($b['acp'] ?: "?") . $reset, "") . "\n";
    echo lineBox($white . "Fuel   " . $reset . " : " . $orange . ($b['fuel'] ?: "?") . $reset, "") . "\n";
    echo "\033[38;5;46m" . "  ╚" . str_repeat("═", 60) . "╝" . $reset . "\n";
}

/* ═══════════════════════════════════════════════════
   FAUCET CLAIM
   ═══════════════════════════════════════════════════ */
function stepFaucet() {
    info("FAUCET", "GET /faucet/");
    $r = req(HOST . "/faucet/");
    $html = $r["body"];

    if ($html === "") { err("FAUCET", "response kosong: " . $r["err"]); return "error"; }
    if (isRedirecting($html, $r["headers"])) { err("FAUCET", "redirect ke login"); return "expired"; }
    if (isLoginPage($html)) { err("FAUCET", "login page — cookie mati"); return "expired"; }
    if (strpos($html, 'Daily Limit Reached') !== false) {
        warn("FAUCET", "daily limit reached");
        return "limit";
    }

    $csrf = extractSidebarCsrf($html);
    if (!$csrf) { warn("FAUCET", "csrf not found"); return "skip"; }

    // ==== cooldown handling — null = skip, bukan assume ready ====
    $wait = extractCooldown($html);
    if ($wait === null) {
        warn("FAUCET", "cooldown pattern tidak dikenali — skip round (aman)");
        return "skip";
    }
    if ($wait > 0) {
        info("FAUCET", "cooldown $wait s");
        timer($wait, "  cooldown ");
        return "cooldown";
    }

    $provider = detectProvider($html);
    if (!$provider) { warn("FAUCET", "no captcha found"); return "skip"; }

    if ($provider !== "hcaptcha") {
        warn("FAUCET", "server minta '$provider' — skip (hcaptcha only)");
        return "skip";
    }

    info("FAUCET", "solving hCaptcha");
    $sol = solveHcaptcha(HCAPTCHA_KEY, HOST . "/faucet/");
    if (!$sol['token']) { err("FAUCET", "solve failed"); return "skip"; }

    $post = [
        'csrf_token'           => $csrf,
        'selected-captcha'     => 'hcaptcha',
        'g-recaptcha-response' => $sol['token'],
        'h-captcha-response'   => $sol['token']
    ];

    info("FAUCET", "POST /faucet/");
    $r2 = req(HOST . "/faucet/", $post, [
        'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
        'Origin: ' . HOST,
        'Referer: ' . HOST . '/faucet/',
    ]);

    if ($r2["body"] === "") {
        err("FAUCET", "POST kosong: " . $r2["err"]);
        return "error";
    }

    $data = json_decode($r2["body"], true);
    if (!is_array($data)) {
        warn("FAUCET", "response bukan JSON: " . substr($r2["body"], 0, 100));
        return "skip";
    }

    if (empty($data['ok'])) {
        $msg = $data['message'] ?? 'unknown';
        warn("FAUCET", "claim fail: $msg");
        if (stripos($msg, 'daily limit') !== false) return "limit";
        return "skip";
    }

    $reward = $data['reward'] ?? 0;
    $wait2  = $data['wait'] ?? 0;
    $fuel   = $data['fuel_won'] ?? 0;
    $today  = $data['claimed_today'] ?? 0;
    $total  = $data['claimed_total'] ?? 0;
    $limit  = $data['daily_claim_limit'] ?? 0;
    $limR   = !empty($data['daily_limit_reached']);

    $rb = req(HOST . "/");
    $balance = getBalanceFromHome($rb["body"]) ?? '?';

    boxClaim("FAUCET CLAIM", [
        "Captcha" => "hcaptcha (attempts: " . $sol['attempts'] . ")",
        "Reward"  => "$reward ACP",
        "Fuel"    => $fuel,
        "Balance" => $balance,
        "Claimed" => "$today / $limit",
        "Total"   => $total,
        "Wait"    => $wait2 . " sec",
        "Time"    => date("h:i:s A"),
    ]);

    if ($limR) return "limit";
    return "ok";
}

/* ═══════════════════════════════════════════════════
   MENU
   ═══════════════════════════════════════════════════ */
function shortCookie($c) {
    if (strlen($c) <= 40) return $c;
    return substr($c, 0, 20) . "..." . substr($c, -15);
}

function mainMenu($cookiePreview) {
    global $white, $cyan, $gray, $orange, $reset;
    echo "\n";
    echo "  " . $white . "Cookie" . $reset . " : " . $cyan . $cookiePreview . $reset . "\n";
    echo "  " . $gray . str_repeat("─", 58) . $reset . "\n";
    echo "    " . $orange . "[1]" . $reset . " Start faucet claim\n";
    echo "    " . $orange . "[2]" . $reset . " Edit config\n";
    echo "    " . $orange . "[3]" . $reset . " Reset config\n";
    echo "    " . $gray . "[0]" . $reset . " Exit\n";
    echo "  " . $gray . ">> " . $reset;
    $in = fgets(STDIN);
    if ($in === false) return "0";
    return trim($in);
}

/* ═══════════════════════════════════════════════════
   MAIN
   ═══════════════════════════════════════════════════ */
clear();

if (function_exists('pcntl_signal')) {
    pcntl_signal(SIGINT, function() {
        echo "\n\n  \033[1;33mInterrupted. Bye.\033[0m\n";
        exit(0);
    });
    pcntl_async_signals(true);
}

$config = getConfig($configFile);

while (true) {
    $apikey     = $config['apikey'];
    $cookies    = $config['cookies'] ?? "";
    $user_agent = $config['user_agent'] ?? "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36";

    $GLOBALS['apikey']     = $apikey;
    $GLOBALS['cookies']    = $cookies;
    $GLOBALS['user_agent'] = $user_agent;

    clear();
    banner();
    $choice = mainMenu(shortCookie($cookies));

    if ($choice === "0") {
        echo "\n  \033[1;33mBye bos.\033[0m\n";
        exit(0);
    }
    if ($choice === "2") {
        @unlink($configFile);
        $config = getConfig($configFile);
        continue;
    }
    if ($choice === "3") {
        @unlink($configFile);
        @unlink('cookie.txt');
        echo "\n  \033[1;32m✓ Config & cookie dihapus.\033[0m\n";
        sleep(1);
        $config = getConfig($configFile);
        continue;
    }

    // ============ [1] START ============
    clear();
    banner("FAUCET CLAIM RUNNING");

    $check = checkBalance();
    if (!$check["ok"]) {
        switch ($check["reason"]) {
            case "expired":
                err("CHECK", "cookie expired — " . $check["detail"]);
                break;
            case "cf":
                err("CHECK", "Cloudflare challenge — " . $check["detail"]);
                break;
            case "csrf_missing":
                warn("CHECK", "HTML berubah: " . $check["detail"]);
                break;
            default:
                err("CHECK", "gagal konek: " . $check["detail"]);
        }
        echo "\n  Tekan ENTER untuk balik ke menu...";
        fgets(STDIN);
        continue;
    }
    ok("CHECK", "cookie valid");
    printBalanceBox($check);

    echo "\n";
    echo $orange . "  ══════════════════════════════════════════════════════════" . $reset . "\n";
    echo $orange . "   AUTO CLAIM STARTING — hCaptcha" . $reset . "\n";
    echo $orange . "  ══════════════════════════════════════════════════════════" . $reset . "\n";

    $round = 0;
    $consecError = 0;

    while (true) {
        $round++;
        echo "\n" . $cyan . "  ╭─────── ROUND #$round ─── " . date("H:i:s") . " ───────╮" . $reset . "\n";

        $r = stepFaucet();

        if ($r === "expired") {
            echo $cyan . "  ╰─────────────────────────────────────────╯" . $reset . "\n";
            err("MAIN", "cookie expired — update di menu [2]");
            echo "\n  Tekan ENTER untuk balik ke menu...";
            fgets(STDIN);
            break;
        }
        if ($r === "limit") {
            echo $cyan . "  ╰─────────────────────────────────────────╯" . $reset . "\n";
            warn("MAIN", "daily limit reached. Balik ke menu.");
            echo "\n  Tekan ENTER untuk balik ke menu...";
            fgets(STDIN);
            break;
        }
        if ($r === "ok") {
            $consecError = 0;
            $rb = req(HOST . "/faucet/");
            $waitNext = extractCooldown($rb["body"]);
            if ($waitNext === null || $waitNext < 30) $waitNext = 1800;
            echo $cyan . "  ╰─────────────────────────────────────────╯" . $reset . "\n";
            timer($waitNext + mt_rand(2, 5), "  next claim ");
            continue;
        }
        if ($r === "cooldown") {
            echo $cyan . "  ╰─────────────────────────────────────────╯" . $reset . "\n";
            continue;
        }
        if ($r === "skip" || $r === "error") {
            $consecError++;
            echo $cyan . "  ╰─────────────────────────────────────────╯" . $reset . "\n";
            if ($consecError >= 6) {
                err("MAIN", "6 error beruntun. Balik ke menu.");
                echo "\n  Tekan ENTER untuk balik ke menu...";
                fgets(STDIN);
                break;
            }
            timer(15, "  retry ");
        }
    }
}
