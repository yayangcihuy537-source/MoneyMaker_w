<?php
/**
 * ClaimCoin.in Auto-Claimer v2.3
 * ────────────────────────────────
 *   ScriptMaker : MoneyMaker_w
 *   Engine      : Smart Captcha Solver (Waryono)
 *
 * v2.3 fixes:
 *   - isCooldownPage() gak lagi cek "Good job" (itu indikator sukses!)
 *   - Cooldown detection murni berdasarkan timer (var wait / countdown)
 *   - Unknown page → coba extract timer dulu sebelum fallback
 *   - $lastBalance di-update tiap claim sukses
 *   - Akumulasi $totalCoins tetap jalan
 */

error_reporting(E_ALL & ~E_WARNING & ~E_NOTICE & ~E_DEPRECATED);
date_default_timezone_set('Asia/Jakarta');

$configFile = __DIR__ . "/config.json";
$cookieFile = __DIR__ . "/cookies.txt";

// ═══════════════════════════════════════════
//  COLOR
// ═══════════════════════════════════════════
const hitam  = "\033[0;30m";
const merah  = "\033[0;31m";
const hijau  = "\033[0;32m";
const kuning = "\033[0;33m";
const biru   = "\033[0;34m";
const cyan   = "\033[0;36m";
const putih  = "\033[0;37m";
const reset  = "\033[0m";
const bold   = "\033[1m";
const dim    = "\033[2m";
const purple = "\033[38;5;135m";
const purpleL= "\033[38;5;177m";
const purpleD= "\033[38;5;93m";
const lavend = "\033[38;5;183m";
const orchid = "\033[38;5;170m";
const gold   = "\033[38;5;220m";
const neon   = "\033[38;5;46m";

// ═══════════════════════════════════════════
//  KONFIG
// ═══════════════════════════════════════════
const host        = "https://claimcoin.in";
const waryono_in  = "https://api.waryono.my.id/in.php";
const waryono_res = "https://api.waryono.my.id/res.php";
const version     = "2.3";
const scriptmaker = "MoneyMaker_w";
const MAX_FAILS   = 5;
const DELAY_MIN   = 12;
const DELAY_MAX   = 16;

// ═══════════════════════════════════════════
//  ANIMATIONS
// ═══════════════════════════════════════════
function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function printLogo() {
    echo purpleL . "
   ██████╗██╗      █████╗ ██╗███╗   ███╗ ██████╗ ██████╗ ██╗███╗   ██╗
  ██╔════╝██║     ██╔══██╗██║████╗ ████║██╔════╝██╔═══██╗██║████╗  ██║
  ██║     ██║     ███████║██║██╔████╔██║██║     ██║   ██║██║██╔██╗ ██║
  ██║     ██║     ██╔══██║██║██║╚██╔╝██║██║     ██║   ██║██║██║╚██╗██║
  ╚██████╗███████╗██║  ██║██║██║ ╚═╝ ██║╚██████╗╚██████╔╝██║██║ ╚████║
   ╚═════╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝
" . reset;
    echo cyan . "       auto claimer • v" . version . " • by kyriel\n" . reset;
    echo orchid . "       ScriptMaker: " . gold . scriptmaker . reset . "\n";
    echo putih . "  ─────────────────────────────────────────────────────────────────\n\n" . reset;
}

function matrixRain($width = 60, $height = 4, $duration = 0.9) {
    $chars = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉ0123456789";
    $charsArr = preg_split('//u', $chars, -1, PREG_SPLIT_NO_EMPTY);
    $start = microtime(true);
    $lines = array_fill(0, $height, array_fill(0, $width, ' '));

    echo "\n";
    for ($i = 0; $i < $height; $i++) echo "\n";

    while ((microtime(true) - $start) < $duration) {
        for ($i = 0; $i < 3; $i++) {
            $col = random_int(0, $width - 1);
            $lines[0][$col] = $charsArr[random_int(0, count($charsArr) - 1)];
        }
        for ($y = $height - 1; $y > 0; $y--) {
            $lines[$y] = $lines[$y - 1];
        }
        $lines[0] = array_fill(0, $width, ' ');

        echo "\033[" . $height . "A";
        foreach ($lines as $y => $row) {
            $color = $y < 1 ? neon : ($y < 2 ? hijau : (dim . hijau));
            echo $color . implode('', $row) . reset . "\n";
        }
        usleep(80000);
    }
}

function loadingBar($label = "LOADING", $duration = 1.2) {
    $frames = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'];
    $start = microtime(true);
    $i = 0;
    $barLen = 30;
    while ((microtime(true) - $start) < $duration) {
        $progress = (microtime(true) - $start) / $duration;
        $filled = (int)($barLen * $progress);
        $bar = str_repeat('█', $filled) . str_repeat('░', $barLen - $filled);
        $frame = $frames[$i % count($frames)];
        $hex = '';
        for ($h = 0; $h < 4; $h++) $hex .= dechex(random_int(0, 15));
        $pct = (int)($progress * 100);
        echo "\r" . purple . "  ┃" . reset . " " . orchid . $frame . reset . " "
            . lavend . str_pad($label, 24) . reset
            . " " . purple . "[" . $bar . "]" . reset
            . " " . purpleD . sprintf("%3d%%", $pct) . reset
            . " " . dim . "0x" . strtoupper($hex) . reset;
        usleep(60000);
        $i++;
    }
    echo "\r" . str_repeat(' ', 110) . "\r";
}

function scanLine($label = "SCANNING", $steps = 45) {
    for ($i = 0; $i <= $steps; $i++) {
        $bar = str_repeat('█', $i) . str_repeat('░', $steps - $i);
        $noise = '';
        for ($n = 0; $n < 16; $n++) $noise .= random_int(0, 1);
        echo "\r" . purple . "  ┃" . reset . " " . lavend . $label . reset
            . " " . purpleL . $bar . reset
            . " " . purpleD . "[" . $noise . "]" . reset;
        usleep(30000);
    }
    echo "\n";
}

function hackingBoot() {
    clear();
    printLogo();
    echo purpleL . "  ⚡ SYSTEM BOOT SEQUENCE" . reset . "\n\n";

    $steps = [
        ["Initializing kernel module...", 90000],
        ["Loading smart captcha engine...", 80000],
        ["Connecting to Waryono solver API...", 100000],
        ["Bypassing anti-bot detection...", 90000],
        ["Generating device fingerprint...", 80000],
        ["Injecting stealth headers...", 80000],
        ["Loading session cookies...", 90000],
    ];
    foreach ($steps as $s) {
        echo hijau . "[✓]" . reset . " " . $s[0];
        usleep($s[1]);
        echo "\n";
    }
    echo gold . "[⚡]" . reset . "   Node status: " . hijau . "SECURE" . reset . "\n";
    echo purpleL . "[★]" . reset . "   System ready. Welcome, Operative." . reset . "\n";

    matrixRain(60, 4, 0.9);
    echo "\n";
    usleep(250000);
}

function line($w = 65) { echo putih . "  " . str_repeat("─", $w) . "\n" . reset; }

function info($m) { echo putih . "  [i] " . cyan . $m . "\n" . reset; }
function ok($m)   { echo putih . "  [✓] " . hijau . $m . "\n" . reset; }
function err($m)  { echo putih . "  [✗] " . merah . $m . "\n" . reset; }
function warn($m) { echo putih . "  [!] " . kuning . $m . "\n" . reset; }
function step($m) { echo putih . "  [>] " . biru . $m . "\n" . reset; }
function dbg($m)  { echo putih . "  [.] " . dim . $m . reset . "\n"; }

function timer($seconds, $prefix = "wait") {
    $wait = (int)$seconds;
    if ($wait <= 0) return;
    $frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'];
    $fc = count($frames);
    $cf = 0;
    while ($wait > 0) {
        $start = microtime(true);
        while ((microtime(true) - $start) < 1) {
            $h = floor($wait / 3600);
            $m = floor(($wait % 3600) / 60);
            $s = $wait % 60;
            $t = sprintf('%02d:%02d:%02d', $h, $m, $s);
            echo putih . "  ⏳ " . cyan . "$prefix" . putih . " : " . hijau . "$t " . putih . $frames[$cf] . "\r";
            usleep(100000);
            $cf = ($cf + 1) % $fc;
            if ((microtime(true) - $start) >= 1) break;
        }
        $wait--;
    }
    echo "\r                                                                  \r";
}

// ═══════════════════════════════════════════
//  HEADERS
// ═══════════════════════════════════════════
function headersGet() {
    return [
        "host: claimcoin.in",
        "upgrade-insecure-requests: 1",
        "user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
        "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "sec-ch-ua: \"Chromium\";v=\"127\", \"Not)A;Brand\";v=\"99\", \"Microsoft Edge Simulate\";v=\"127\", \"Lemur\";v=\"127\"",
        "sec-ch-ua-mobile: ?1",
        "sec-ch-ua-platform: \"Android\"",
        "sec-fetch-site: same-origin",
        "sec-fetch-mode: navigate",
        "sec-fetch-dest: document",
    ];
}

function headersPost($referer) {
    return [
        "host: claimcoin.in",
        "origin: " . host,
        "content-type: application/x-www-form-urlencoded",
        "upgrade-insecure-requests: 1",
        "user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
        "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "referer: $referer",
        "accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "sec-ch-ua: \"Chromium\";v=\"127\", \"Not)A;Brand\";v=\"99\", \"Microsoft Edge Simulate\";v=\"127\", \"Lemur\";v=\"127\"",
        "sec-ch-ua-mobile: ?1",
        "sec-ch-ua-platform: \"Android\"",
        "sec-fetch-site: same-origin",
        "sec-fetch-mode: navigate",
        "sec-fetch-dest: document",
    ];
}

// ═══════════════════════════════════════════
//  HTTP
// ═══════════════════════════════════════════
function req($url, $method = 'GET', $data = [], $headers = [], $isJson = false) {
    global $cookieFile;
    $ch = curl_init();
    $options = [
        CURLOPT_URL            => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER         => false,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_MAXREDIRS      => 5,
        CURLOPT_SSL_VERIFYHOST => 2,
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_HTTPHEADER     => $headers,
        CURLOPT_CONNECTTIMEOUT => 30,
        CURLOPT_TIMEOUT        => 60,
        CURLOPT_ENCODING       => '',
    ];
    if (!$isJson) {
        $options[CURLOPT_COOKIEFILE] = $cookieFile;
        $options[CURLOPT_COOKIEJAR]  = $cookieFile;
    }
    if (strtoupper($method) === 'POST') {
        $options[CURLOPT_POST] = true;
        $options[CURLOPT_POSTFIELDS] = $isJson && is_array($data) ? json_encode($data) : $data;
    }
    curl_setopt_array($ch, $options);
    $body = curl_exec($ch);
    $errno = curl_errno($ch);
    $err = curl_error($ch);
    $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $finalUrl = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);
    curl_close($ch);

    if ($errno !== 0) {
        err("cURL #$errno: $err");
        return ['body'=>false, 'status'=>0, 'url'=>$url];
    }
    return ['body'=>$body, 'status'=>$status, 'url'=>$finalUrl];
}

// ═══════════════════════════════════════════
//  WARYONO SOLVER
// ═══════════════════════════════════════════
function solveTurnstile($apikey, $sitekey, $domain = host, $action = "login") {
    step("Request turnstile token ke Waryono...");
    dbg("Sitekey : " . $sitekey);
    $payload = [
        "apikey"  => $apikey,
        "methods" => "turnstile",
        "domain"  => $domain,
        "sitekey" => $sitekey,
        "action"  => $action,
        "json"    => 1,
    ];
    $r = req(waryono_in, "POST", $payload, ["Content-Type: application/json"], true);
    if (!$r['body']) { err("Gagal kirim task ke Waryono"); return null; }
    $j = json_decode($r['body'], true);

    if (!$j && strpos($r['body'], "OK|") !== false) {
        $j = ["status"=>1, "request"=>explode("|", $r['body'], 2)[1]];
    }
    if (!is_array($j)) { err("Response Waryono invalid: " . substr($r['body'], 0, 100)); return null; }

    if (($j['status'] ?? 0) != 1) {
        $errcode = $j['request'] ?? $r['body'];
        err("Waryono reject: " . $errcode);
        if (strpos($errcode, "ERROR_KEY_DOES_NOT_EXIST") !== false) err("=> Cek API key lu");
        if (strpos($errcode, "ERROR_ZERO_BALANCE") !== false) err("=> Saldo Waryono lu abis");
        return null;
    }

    $taskId = $j['request'];
    ok("Task ID : " . $taskId);
    step("Polling token...");

    $start = time();
    $maxWait = 120;
    while (time() - $start < $maxWait) {
        timer(5, "solver");
        $url = waryono_res . "?apikey=" . urlencode($apikey) . "&id=" . urlencode($taskId) . "&action=get&json=1";
        $r2 = req($url, "GET");
        if (!$r2['body']) continue;
        $j2 = json_decode($r2['body'], true);
        if (!$j2 && strpos($r2['body'], "OK|") !== false) {
            $tok = explode("|", $r2['body'], 2)[1];
            ok("Token diterima");
            return $tok;
        }
        if (is_array($j2)) {
            if (($j2['status'] ?? 0) == 1 && !empty($j2['request'])) {
                ok("Token diterima");
                return $j2['request'];
            }
            $req = strtoupper($j2['request'] ?? "");
            if (strpos($req, "NOT_READY") !== false) continue;
            if (strpos($req, "ERROR") !== false) {
                err("Solver error: " . $req);
                return null;
            }
        }
    }
    err("Timeout nunggu token (max {$maxWait}s)");
    return null;
}

// ═══════════════════════════════════════════
//  PARSER
// ═══════════════════════════════════════════
function parseCsrf($html) {
    if (preg_match('/<input[^>]*name=["\']csrf_token_name["\'][^>]*value=["\']([^"\']+)["\']/i', $html, $m))
        return $m[1];
    if (preg_match('/<input[^>]*value=["\']([^"\']+)["\'][^>]*name=["\']csrf_token_name["\']/i', $html, $m))
        return $m[1];
    if (preg_match('/<input[^>]*id=["\']token["\'][^>]*value=["\']([^"\']+)["\']/i', $html, $m))
        return $m[1];
    if (preg_match('/<input[^>]*value=["\']([^"\']+)["\'][^>]*id=["\']token["\']/i', $html, $m))
        return $m[1];
    return null;
}

function parseSitekey($html) {
    if (preg_match('/data-sitekey=["\']([^"\']+)["\']/i', $html, $m)) return $m[1];
    if (preg_match('/sitekey["\']?\s*[:=]\s*["\'](0x[0-9A-Za-z_-]+)["\']/', $html, $m)) return $m[1];
    return null;
}

function parseBalance($html) {
    if (preg_match('/Available\s+Balance.*?<h2>\s*([\d,\.]+)\s*CCP/i', $html, $m))
        return (float)str_replace(',', '', $m[1]);
    if (preg_match('/([\d,\.]+)\s*CCP/i', $html, $m))
        return (float)str_replace(',', '', $m[1]);
    return null;
}

function parseWait($html) {
    if (preg_match('/var\s+wait\s*=\s*(\d+)\s*-\s*1/i', $html, $m)) return max(0, (int)$m[1] - 1);
    if (preg_match('/var\s+wait\s*=\s*(\d+)/i', $html, $m)) return (int)$m[1];
    if (preg_match('/id="second"[^>]*>\s*(\d+)/i', $html, $m)) return (int)$m[1];
    return 0;
}

function parseRewardAmount($str) {
    if (preg_match('/([\d,]+(?:\.\d+)?)\s*CCP/i', $str, $m))
        return (float)str_replace(',', '', $m[1]);
    return 0.0;
}

function isLoginPage($html) {
    if (preg_match('/<input[^>]*type=["\']password["\']/i', $html)) return true;
    if (preg_match('/<title>\s*Login/i', $html)) return true;
    return false;
}

function isLoggedIn($html) {
    return (stripos($html, 'User Dashboard') !== false)
        || (stripos($html, 'Available Balance') !== false)
        || (stripos($html, 'Total Earned') !== false);
}

/**
 * FIX v2.3: Cooldown murni based on timer, BUKAN "Good job"
 * (Good job itu indikator SUKSES di claim(), bukan cooldown)
 */
function isCooldownPage($html) {
    // Timer JavaScript
    if (preg_match('/var\s+wait\s*=\s*\d+/i', $html)) return true;
    // Countdown element
    if (preg_match('/id=["\']second["\'][^>]*>\s*\d+/i', $html)) return true;
    if (preg_match('/id=["\']minute["\'][^>]*>\s*\d+/i', $html)) return true;
    // Halaman "Please Wait" tanpa form
    if (stripos($html, 'Please Wait') !== false && stripos($html, '/faucet/verify') === false) return true;
    return false;
}

// ═══════════════════════════════════════════
//  CONFIG
// ═══════════════════════════════════════════
function getConfig($configFile) {
    if (!file_exists($configFile)) {
        clear();
        printLogo();
        echo kuning . "  [Setup Pertama]\n\n" . reset;
        echo putih . "  Email       : " . kuning;
        $email = trim(fgets(STDIN));
        echo putih . "  Password    : " . kuning;
        $password = trim(fgets(STDIN));
        echo putih . "  Waryono Key : " . kuning;
        $apikey = trim(fgets(STDIN));
        $data = ["email"=>$email, "password"=>$password, "apikey"=>$apikey];
        file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
        echo hijau . "\n  ✓ Config tersimpan\n" . reset;
        sleep(2);
        return $data;
    }
    $cfg = json_decode(file_get_contents($configFile), true);
    if (!is_array($cfg) || empty($cfg['email']) || empty($cfg['password']) || empty($cfg['apikey'])) {
        @unlink($configFile);
        return getConfig($configFile);
    }
    return $cfg;
}

// ═══════════════════════════════════════════
//  LOGIN
// ═══════════════════════════════════════════
function login($email, $password, $apikey) {
    step("GET /login — scrape csrf + sitekey");
    $r = req(host . "/login", "GET", [], headersGet());
    if (!$r['body']) { err("Gagal GET /login"); return false; }

    $csrf = parseCsrf($r['body']);
    $sitekey = parseSitekey($r['body']);
    if (!$csrf) {
        err("CSRF gak ketemu di login page");
        dbg("Snippet: " . substr(preg_replace('/\s+/', ' ', strip_tags($r['body'])), 0, 200));
        return false;
    }
    if (!$sitekey) {
        warn("Sitekey turnstile gak ketemu, pakai default");
        $sitekey = "0x4AAAAAAB6ZWSg9eOY7OVRl";
    }
    info("CSRF    : " . dim . substr($csrf, 0, 16) . "..." . reset);
    info("Sitekey : " . $sitekey);

    $turnstileToken = solveTurnstile($apikey, $sitekey);
    if (!$turnstileToken) { err("Gagal solve turnstile"); return false; }

    step("POST /auth/login");
    $data = http_build_query([
        "csrf_token_name"       => $csrf,
        "email"                 => $email,
        "password"              => $password,
        "captcha"               => "turnstile",
        "cf-turnstile-response" => $turnstileToken,
    ]);
    $r2 = req(host . "/auth/login", "POST", $data, headersPost(host . "/login"));
    if (!$r2['body']) { err("Gagal POST login"); return false; }

    if (isLoggedIn($r2['body']) || stripos($r2['body'], 'Dashboard | ClaimCoin') !== false) {
        ok("Login sukses");
        return true;
    }
    if (isLoginPage($r2['body'])) {
        if (preg_match('/alert-danger">.*?<\/i>\s*([^<]+)/s', $r2['body'], $m))
            err("Login ditolak: " . trim($m[1]));
        else
            err("Login ditolak (masih di halaman login)");
        return false;
    }
    if (strpos($r2['url'], '/dashboard') !== false) {
        ok("Login sukses (redirect)");
        return true;
    }
    warn("Response login ambigu, cek dashboard...");
    return true;
}

// ═══════════════════════════════════════════
//  DASHBOARD
// ═══════════════════════════════════════════
function checkDashboard() {
    $r = req(host . "/dashboard", "GET", [], headersGet());
    if (!$r['body']) return null;
    if (!isLoggedIn($r['body'])) return false;
    $username = null;
    if (preg_match('/key="t-henry">([^<]+)</i', $r['body'], $m)) $username = trim($m[1]);
    return [
        'balance' => parseBalance($r['body']),
        'username'=> $username,
    ];
}

// ═══════════════════════════════════════════
//  FAUCET
// ═══════════════════════════════════════════
function getFaucet() {
    $r = req(host . "/faucet", "GET", [], headersGet());
    if (!$r['body']) return ['state'=>'error'];

    // Redirect ke halaman lain = cooldown
    $finalUrl = $r['url'] ?? host . '/faucet';
    if (strpos($finalUrl, '/faucet') === false) {
        return ['state'=>'cooldown', 'wait'=>30, 'msg'=>'redirected'];
    }

    if (isLoginPage($r['body'])) return ['state'=>'need_login'];

    // Cooldown page (timer-based aja)
    if (isCooldownPage($r['body'])) {
        $wait = parseWait($r['body']);
        return ['state'=>'cooldown', 'wait'=>max($wait, 10)];
    }

    // Form marker
    $hasVerifyForm = stripos($r['body'], '/faucet/verify') !== false;
    $hasCollectBtn = stripos($r['body'], 'Collect your reward') !== false;

    if (!$hasVerifyForm && !$hasCollectBtn) {
        // Fallback: cek kalau ada timer tersembunyi / status
        $wait = parseWait($r['body']);
        if ($wait > 0) {
            return ['state'=>'cooldown', 'wait'=>$wait, 'msg'=>'fallback_timer'];
        }

        // Debug info
        $title = '(no title)';
        if (preg_match('/<title>([^<]*)<\/title>/i', $r['body'], $tm)) $title = trim($tm[1]);
        dbg("Unknown page: len=" . strlen($r['body']) . " | title=" . $title);

        // Kalau body sangat pendek, itu error server
        if (strlen($r['body']) < 500) {
            return ['state'=>'cooldown', 'wait'=>20, 'msg'=>'short_body'];
        }

        return ['state'=>'cooldown', 'wait'=>30, 'msg'=>'unknown_page'];
    }

    $csrf = parseCsrf($r['body']);
    if (!$csrf) {
        return ['state'=>'cooldown', 'wait'=>15, 'msg'=>'csrf_parse_fail'];
    }

    return [
        'state'   => 'ready',
        'csrf'    => $csrf,
        'balance' => parseBalance($r['body']),
    ];
}

function claim($csrf) {
    $data = http_build_query(["csrf_token_name" => $csrf]);
    $r = req(host . "/faucet/verify", "POST", $data, headersPost(host . "/faucet"));
    if (!$r['body']) return ['ok'=>false, 'hint'=>'no_response'];

    $html = $r['body'];

    if (preg_match("/Swal\.fire\('Good job!',\s*'([^']+)'/", $html, $m)) {
        $amount = parseRewardAmount($m[1]);
        return ['ok'=>true, 'reward'=>$amount, 'balance'=>parseBalance($html)];
    }
    if (preg_match("/([\d,]+(?:\.\d+)?)\s*CCP has been added to your balance/i", $html, $m)) {
        return ['ok'=>true, 'reward'=>(float)str_replace(',', '', $m[1]), 'balance'=>parseBalance($html)];
    }

    foreach (['Daily Limit','daily limit','come back tomorrow','no more claims','already claimed'] as $h) {
        if (stripos($html, $h) !== false) return ['ok'=>false, 'hint'=>'daily_limit', 'stop'=>true];
    }

    if (isLoginPage($html)) return ['ok'=>false, 'hint'=>'session_dead'];

    $wait = parseWait($html);
    if ($wait > 0 && stripos($html, '/faucet/verify') === false)
        return ['ok'=>false, 'hint'=>'cooldown', 'wait'=>$wait];

    foreach (['Invalid','Error','expired','captcha','too fast'] as $h) {
        if (stripos($html, $h) !== false) return ['ok'=>false, 'hint'=>$h];
    }

    return ['ok'=>false, 'hint'=>'unknown'];
}

// ═══════════════════════════════════════════
//  MAIN
// ═══════════════════════════════════════════
function main() {
    global $configFile, $cookieFile;

    if (!file_exists($cookieFile)) {
        file_put_contents($cookieFile, "");
        @chmod($cookieFile, 0600);
    }

    $config = getConfig($configFile);
    $email    = $config['email'];
    $password = $config['password'];
    $apikey   = $config['apikey'];

    hackingBoot();
    loadingBar("Loading core modules", 1.0);
    scanLine("Fetching account state", 45);

    clear();
    printLogo();

    // STEP 1: Cek session
    step("Cek session /dashboard...");
    $dash = checkDashboard();

    $needLogin = false;
    if ($dash === false || $dash === null) {
        warn("Belum login. Coba login pakai email+password...");
        $needLogin = true;
    } else {
        ok("Session valid");
        info("User    : " . bold . ($dash['username'] ?? '-') . reset);
        if ($dash['balance'] !== null) info("Balance : " . bold . $dash['balance'] . " CCP" . reset);
    }

    // STEP 2: Login kalau perlu
    if ($needLogin) {
        line();
        if (!login($email, $password, $apikey)) {
            err("Login gagal. Cek config atau captcha.");
            exit(1);
        }
        $dash = checkDashboard();
        if ($dash === false || $dash === null) {
            err("Gagal akses dashboard setelah login.");
            exit(1);
        }
        info("User    : " . bold . ($dash['username'] ?? '-') . reset);
        if ($dash['balance'] !== null) info("Balance : " . bold . $dash['balance'] . " CCP" . reset);
    }

    line();
    echo "\n";

    // STEP 3: Loop claim
    $fail = 0;
    $total = 0;
    $totalCoins = 0.0;
    $lastBalance = $dash['balance'] ?? null;
    $needRelogin = false;

    while (true) {
        line();
        echo putih . "  " . bold . hijau . " AUTO-CLAIMER " . reset
            . putih . "  sukses: " . hijau . $total . reset
            . putih . "  |  akumulasi: " . gold . sprintf("%.4f", $totalCoins) . " CCP" . reset
            . putih . "  |  gagal: " . merah . "$fail/" . MAX_FAILS . reset . "\n";
        line();

        if ($needRelogin) {
            warn("Re-login karena session expired...");
            if (!login($email, $password, $apikey)) {
                err("Re-login gagal. Stop.");
                break;
            }
            $needRelogin = false;
            $fail = 0;
        }

        $state = getFaucet();

        if ($state['state'] === 'need_login') {
            warn("Session expired, coba re-login...");
            $needRelogin = true;
            continue;
        }

        if ($state['state'] === 'cooldown') {
            $wait = $state['wait'] ?? 10;
            $msg = $state['msg'] ?? '';
            if ($msg) dbg("Cooldown reason: " . $msg);
            timer($wait, "cooldown");
            continue;
        }

        if ($state['state'] !== 'ready' || empty($state['csrf'])) {
            $fail++;
            err("State invalid ({$state['state']}) [$fail/" . MAX_FAILS . "]");
            if ($fail >= MAX_FAILS) { warn("Gagal " . MAX_FAILS . "x. Stop."); break; }
            sleep(3);
            continue;
        }

        if (!empty($state['balance'])) $lastBalance = $state['balance'];

        info("CSRF    : " . dim . substr($state['csrf'], 0, 16) . "..." . reset);
        if ($lastBalance !== null) info("Balance : " . bold . $lastBalance . " CCP" . reset);

        $res = claim($state['csrf']);

        if ($res['ok']) {
            $total++;
            $reward = (float)($res['reward'] ?? 0);
            if ($reward > 0) $totalCoins += $reward;

            // Update balance dari response claim
            if (!empty($res['balance'])) $lastBalance = $res['balance'];

            echo putih . "  " . bold . hijau . " 💰 SUKSES " . reset
                . hijau . " +" . ($reward > 0 ? sprintf("%.4f", $reward) : "?") . " CCP" . reset . "\n";
            info("Total sukses : " . bold . $total . reset . " klaim");
            if ($totalCoins > 0)
                info("Akumulasi    : " . bold . gold . sprintf("%.4f", $totalCoins) . " CCP" . reset . " (session ini)");
            if ($lastBalance !== null)
                info("Balance baru : " . bold . $lastBalance . " CCP" . reset);

            $fail = 0;

            $delay = random_int(DELAY_MIN, DELAY_MAX);
            echo "\n";
            timer($delay, "delay");
            echo "\n";
            continue;
        }

        if (!empty($res['stop']) && ($res['hint'] ?? '') === 'daily_limit') {
            echo "\n"; line();
            echo putih . "  " . bold . kuning . " 🎯 DAILY LIMIT REACHED " . reset . "\n";
            line();
            warn("Jatah hari ini abis.");
            if ($lastBalance !== null) info("Balance akhir : " . bold . $lastBalance . " CCP" . reset);
            info("Total sukses  : " . bold . $total . reset);
            info("Total akumulasi : " . bold . gold . sprintf("%.4f", $totalCoins) . " CCP" . reset);
            echo "\n  " . purpleL . "👑 ScriptMaker: " . gold . scriptmaker . reset . "\n";
            break;
        }

        if (($res['hint'] ?? '') === 'session_dead') {
            warn("Session mati, re-login...");
            $needRelogin = true;
            continue;
        }

        if (($res['hint'] ?? '') === 'cooldown') {
            $wait = $res['wait'] ?? 10;
            warn("Server cooldown: {$wait}s");
            timer($wait, "cooldown");
            $fail = 0;
            continue;
        }

        $fail++;
        $hint = $res['hint'] ?? 'unknown';
        err("Claim gagal (hint: $hint) [$fail/" . MAX_FAILS . "]");

        if ($fail >= MAX_FAILS) { warn("Gagal " . MAX_FAILS . "x. Stop."); break; }
        sleep(3);
    }

    echo "\n"; line();
    echo putih . "  " . bold . hijau . " 🏁 SELESAI " . reset . "\n";
    line();
    info("Total klaim sukses : " . bold . $total . reset);
    info("Total CCP          : " . bold . gold . sprintf("%.4f", $totalCoins) . " CCP" . reset);
    if ($lastBalance !== null) info("Balance terakhir   : " . bold . $lastBalance . " CCP" . reset);
    echo "\n  " . purpleL . "👑 ScriptMaker: " . gold . scriptmaker . reset . "\n";
    line();
}

try { main(); }
catch (Throwable $e) {
    echo merah . "\n  [FATAL] " . $e->getMessage() . "\n" . reset;
    exit(1);
}
