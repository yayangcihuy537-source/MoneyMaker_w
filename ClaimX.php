<?php
/**
 * CLAIMX AUTO CLAIM BOT v8.2
 * Fixed: fetch fail detection + auto re-login + retry
 */

error_reporting(E_ALL & ~E_WARNING & ~E_NOTICE & ~E_DEPRECATED);
date_default_timezone_set('Asia/Jakarta');

// ─── COLOR ───
define('RESET', "\033[0m");
define('RED',   "\033[31m");
define('GREEN', "\033[32m");
define('YELLOW',"\033[33m");
define('CYAN',  "\033[36m");
define('WHITE', "\033[37m");
define('GRAY',  "\033[90m");
define('B_RED',   "\033[1;31m");
define('B_GREEN', "\033[1;32m");
define('B_YELLOW',"\033[1;33m");
define('B_CYAN',  "\033[1;36m");
define('B_WHITE', "\033[1;37m");
define('DIM',     "\033[2m");

// ─── CONFIG ───
const HOST = 'https://claimx.online';
const MAX_DAILY_CLAIMS = 100;
const CONFIG_FILE = 'claimx_config.json';
const COOKIE_FILE = 'claimx_cookie.txt';
const DAILY_FILE  = 'claimx_daily.txt';
const AD_VIEW_SECONDS = 6;
const MIN_CLAIM_DELAY = 3;
const MAX_CLAIM_DELAY = 6;

// ═══════════════ UTILS ═══════════════
function clearScreen() { (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w')); }

function printBanner() {
    clearScreen();
    echo B_CYAN . "==================================================\n";
    echo B_CYAN . "  " . B_WHITE . "ClaimX Auto Claim Bot v8.2" . B_CYAN . "  \n";
    echo B_CYAN . "==================================================\n";
    echo B_CYAN . "  Icon Captcha + Ad-Verify API\n";
    echo B_CYAN . "  Limit: " . MAX_DAILY_CLAIMS . " claim/day\n";
    echo B_CYAN . "  Cooldown server: ~2s\n";
    echo B_CYAN . "==================================================\n\n";
}

function timer($seconds, $prefix = "Waiting") {
    $w = (int)$seconds;
    if ($w <= 0) return;
    $f = ['⣾','⣽','⣻','⢿','⡿','⣟','⣯','⣷'];
    $i = 0;
    while ($w > 0) {
        $tf = sprintf('%02d:%02d:%02d', floor($w/3600), floor(($w%3600)/60), $w%60);
        echo "\r" . B_YELLOW . "  ⏳ {$prefix}: " . B_WHITE . $tf . " " . $f[$i] . "   " . RESET;
        sleep(1); $w--; $i = ($i + 1) % count($f);
    }
    echo "\r" . str_repeat(" ", 60) . "\r";
}

// ═══════════════ HTTP ═══════════════
function req($url, $method = 'GET', $post = null, $extra = []) {
    $ch = curl_init();
    $headers = array_merge([
        'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language: id-ID,id;q=0.9,en;q=0.8',
        'Accept-Encoding: gzip, deflate, br',
        'Connection: keep-alive',
        'Upgrade-Insecure-Requests: 1',
    ], $extra);
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_MAXREDIRS => 10,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_COOKIEFILE => COOKIE_FILE,
        CURLOPT_COOKIEJAR  => COOKIE_FILE,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_CONNECTTIMEOUT => 15,
        CURLOPT_ENCODING => '',
    ]);
    if (strtoupper($method) === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $post);
    }
    $r = curl_exec($ch);
    $errno = curl_errno($ch);
    $errmsg = curl_error($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    $GLOBALS['LAST_REQ'] = [
        'url' => $url,
        'errno' => $errno,
        'errmsg' => $errmsg,
        'code' => $httpCode,
        'len' => is_string($r) ? strlen($r) : 0,
    ];

    if ($errno) return false;
    return $r;
}

function reqNoFollow($url, $post = null, $extra = []) {
    $ch = curl_init();
    $headers = array_merge([
        'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        'Accept: */*',
        'Accept-Language: id-ID,id;q=0.9,en;q=0.8',
        'Accept-Encoding: gzip, deflate, br',
        'Connection: keep-alive',
        'X-Requested-With: XMLHttpRequest',
    ], $extra);
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_COOKIEFILE => COOKIE_FILE,
        CURLOPT_COOKIEJAR  => COOKIE_FILE,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_CONNECTTIMEOUT => 15,
        CURLOPT_ENCODING => '',
    ]);
    if ($post !== null) {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $post);
    }
    $r = curl_exec($ch);
    $errno = curl_errno($ch);
    curl_close($ch);
    return $errno ? false : $r;
}

// ═══════════════ PARSERS ═══════════════
function parseCSRF($html) {
    if (preg_match('/<input[^>]*name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']/i', $html, $m)) return $m[1];
    if (preg_match('/csrf_token\s*[:=]\s*["\']([^"\']+)["\']/i', $html, $m)) return $m[1];
    return null;
}

function parseIconCaptcha($html) {
    $target = null;
    $choices = [];

    // Target icon
    if (preg_match_all('/<div[^>]*class=["\'][^"\']*border-warning[^"\']*["\'][^>]*>\s*<i[^>]*class=["\']([^"\']+)["\'][^>]*>\s*<\/i>/si', $html, $ms)) {
        foreach ($ms[1] as $cls) {
            if (preg_match('/\bbi-[a-z0-9\-]+/i', $cls, $ic)) {
                $target = $ic[0];
                break;
            }
        }
    }

    if (!$target) {
        if (preg_match('/<div[^>]*class=["\'][^"\']*text-warning[^"\']*["\'][^>]*>\s*<i[^>]*class=["\']([^"\']+)["\'][^>]*>\s*<\/i>/si', $html, $m)) {
            if (preg_match('/\bbi-[a-z0-9\-]+/i', $m[1], $ic)) {
                $target = $ic[0];
            }
        }
    }

    // Choices
    if (preg_match_all('/<button[^>]*data-key=["\']([^"\']+)["\'][^>]*>(.*?)<\/button>/si', $html, $ms, PREG_SET_ORDER)) {
        foreach ($ms as $m) {
            $key = $m[1];
            $inner = $m[2];
            if (preg_match('/<i[^>]*class=["\']([^"\']*bi-[a-z0-9\-]+[^"\']*)["\']/i', $inner, $ic)) {
                if (preg_match('/\bbi-[a-z0-9\-]+/i', $ic[1], $only)) {
                    $choices[] = ['key' => $key, 'icon' => $only[0]];
                }
            }
        }
    }

    return [$target, $choices];
}

function matchIcon($target, $choices) {
    if (!$target || empty($choices)) return null;

    $targetIcon = null;
    if (preg_match('/\bbi-[a-z0-9\-]+/i', $target, $m)) {
        $targetIcon = $m[0];
    } else {
        $targetIcon = $target;
    }

    foreach ($choices as $c) {
        if (strcasecmp($targetIcon, $c['icon']) === 0) return $c['key'];
    }

    $targetPart = preg_replace('/^bi-/', '', $targetIcon);
    foreach ($choices as $c) {
        $choicePart = preg_replace('/^bi-/', '', $c['icon']);
        if (strcasecmp($targetPart, $choicePart) === 0) return $c['key'];
    }

    return null;
}

// ═══════════════ DAILY ═══════════════
function getDailyCount() {
    if (file_exists(DAILY_FILE)) {
        $d = json_decode(file_get_contents(DAILY_FILE), true);
        if (($d['date'] ?? '') === date('Y-m-d')) return (int)$d['count'];
    }
    return 0;
}
function updateDailyCount($c) {
    file_put_contents(DAILY_FILE, json_encode(['date'=>date('Y-m-d'), 'count'=>$c]));
}
function resetDailyIfNeeded() {
    if (file_exists(DAILY_FILE)) {
        $d = json_decode(file_get_contents(DAILY_FILE), true);
        if (($d['date'] ?? '') !== date('Y-m-d')) { updateDailyCount(0); return true; }
    }
    return false;
}

function getBalance() {
    $html = req(HOST . '/dashboard');
    if (!$html) return '0.00000000';
    $pats = [
        '/Earnings Balance.*?<h3[^>]*class="[^"]*fs-4[^"]*"[^>]*>([0-9.]+)/si',
        '/Earnings Balance<\/p>\s*<h3[^>]*>([0-9.]+)/si',
        '/balance[^>]*>([0-9.]+)/si',
    ];
    foreach ($pats as $p) if (preg_match($p, $html, $m)) return trim($m[1]);
    return '0.00000000';
}

function checkDailyLimit($html) {
    return strpos($html, 'Daily Limit Reached') !== false
        || strpos($html, 'You have completed all') !== false
        || strpos($html, 'Upgrade Membership') !== false;
}

function isLoginPage($html) {
    return strpos($html, 'FaucetPay Email Address') !== false
        && strpos($html, 'Enter Faucet Portal') !== false;
}

function isCooldownPage($html) {
    return strpos($html, 'countdownClock') !== false
        || strpos($html, 'Faucet Cooling Down') !== false;
}

function isReadyToClaim($html) {
    return strpos($html, 'id="faucetForm"') !== false;
}

function parseCooldownSeconds($html) {
    if (preg_match('/id="countdownClock"[^>]*data-seconds=["\']?(\d+)/i', $html, $m)) {
        return (int)$m[1];
    }
    return 0;
}

// ═══════════════ LOGIN ═══════════════
function doLogin($email, $password) {
    echo B_CYAN . "  [LOGIN] Attempting login...\n" . RESET;

    if (file_exists(COOKIE_FILE)) @unlink(COOKIE_FILE);

    $html = false;
    for ($i = 1; $i <= 3; $i++) {
        $html = req(HOST . '/login');
        if ($html && strlen($html) > 500) break;
        echo "  " . B_YELLOW . "[retry $i/3] fetch /login gagal, tunggu 5s..." . RESET . "\n";
        sleep(5);
    }

    if (!$html || strlen($html) < 500) {
        echo B_RED . "  [ERROR] Gagal fetch /login\n" . RESET;
        return false;
    }

    $csrf = parseCSRF($html);
    if (!$csrf) { echo B_RED . "  [ERROR] CSRF login ga ketemu\n" . RESET; return false; }

    list($target, $choices) = parseIconCaptcha($html);
    if (!$target) { echo B_RED . "  [ERROR] Target icon login ga ketemu\n" . RESET; return false; }
    if (empty($choices)) { echo B_RED . "  [ERROR] Choices login kosong\n" . RESET; return false; }

    $key = matchIcon($target, $choices);
    if (!$key) {
        echo B_RED . "  [ERROR] Ikon login ga match\n" . RESET;
        echo "  " . DIM . "  target: {$target}\n";
        foreach ($choices as $c) echo "  " . DIM . "  choice: {$c['key']} = {$c['icon']}\n" . RESET;
        return false;
    }

    echo B_CYAN . "  [LOGIN] {$target} → {$key}\n" . RESET;

    $post = http_build_query([
        'csrf_token' => $csrf,
        'email' => $email,
        'password' => $password,
        'icon_captcha_selected' => $key
    ]);
    $r = req(HOST . '/login', 'POST', $post, [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: ' . HOST,
        'Referer: ' . HOST . '/login',
    ]);
    if ($r === false) { echo B_RED . "  [ERROR] POST login gagal\n" . RESET; return false; }

    if (strpos($r, 'Welcome back') !== false || strpos($r, 'Dashboard') !== false) {
        echo B_GREEN . "  [SUCCESS] Login OK\n" . RESET;
        return true;
    }
    echo B_RED . "  [ERROR] Login reject\n" . RESET;
    return false;
}

// ═══════════════ AD-TOKEN ═══════════════
function fetchAdToken($csrf) {
    $body = 'csrf_token=' . urlencode($csrf);
    $r = reqNoFollow(HOST . '/faucet/verify-ad', $body, [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: ' . HOST,
        'Referer: ' . HOST . '/faucet',
    ]);

    if ($r === false) return ['ok'=>false, 'raw'=>'curl failed'];

    $j = json_decode($r, true);
    if (is_array($j) && !empty($j['success']) && !empty($j['token'])) {
        return ['ok'=>true, 'token'=>$j['token'], 'raw'=>$r];
    }

    return ['ok'=>false, 'token'=>null, 'raw'=>$r];
}

// ═══════════════ CLAIM ═══════════════
function claimFaucet(&$info) {
    // ── Fetch /faucet dengan retry 3x ──
    $html = false;
    for ($try = 1; $try <= 3; $try++) {
        $html = req(HOST . '/faucet');
        if ($html && strlen($html) > 500) break;

        $dbg = $GLOBALS['LAST_REQ'] ?? [];
        echo "  " . B_YELLOW . "[fetch] try {$try}/3 gagal | "
             . "errno=" . ($dbg['errno'] ?? '?') . " code=" . ($dbg['code'] ?? '?')
             . " len=" . ($dbg['len'] ?? '?')
             . " msg=" . substr($dbg['errmsg'] ?? '-', 0, 60) . RESET . "\n";

        if ($try < 3) sleep(rand(3, 5));
    }

    if (!$html || strlen($html) < 500) {
        $dbg = $GLOBALS['LAST_REQ'] ?? [];
        $code = (int)($dbg['code'] ?? 0);
        if ($code == 0 || $code >= 500) {
            echo B_RED . "  [NETWORK] server gak respon / 5xx → tunggu 30s" . RESET . "\n";
            return ['cooldown' => 30];
        }
        // HTTP 200 tapi body kosong → kemungkinan cookie expired / Cloudflare
        if ($code == 200 && ($dbg['len'] ?? 0) < 500) {
            echo B_RED . "  [FETCH] response kosong → re-login attempt" . RESET . "\n";
            return 'session_invalid';
        }
        return 'fetch_fail';
    }

    if (isLoginPage($html)) return 'session_invalid';
    if (checkDailyLimit($html)) return 'limit_reached';

    // Cooldown state?
    if (!isReadyToClaim($html)) {
        if (isCooldownPage($html)) {
            $s = parseCooldownSeconds($html);
            if ($s > 0) return ['cooldown' => $s];
            return ['cooldown' => 3];
        }
        return 'no_form';
    }

    $csrf = parseCSRF($html);
    if (!$csrf) return 'no_csrf';

    echo B_CYAN . "  [FAUCET] Processing...\n" . RESET;

    // ── Ad view ──
    for ($i = AD_VIEW_SECONDS; $i > 0; $i--) {
        echo "\r  " . B_CYAN . "[AD] Viewing sponsored ad: " . B_WHITE . "{$i}s" . RESET . "   ";
        sleep(1);
    }
    echo "\r" . str_repeat(' ', 50) . "\r";

    // ── Fetch ad-token ──
    echo B_CYAN . "  [AD] Requesting verify-ad token...\n" . RESET;
    $tokRes = fetchAdToken($csrf);

    if (!$tokRes['ok'] && stripos($tokRes['raw'], 'at least 5 seconds') !== false) {
        echo "  " . B_YELLOW . "[AD] Server minta 5s+, tunggu 4s lagi..." . RESET . "\n";
        sleep(4);
        $tokRes = fetchAdToken($csrf);
    }

    if (!$tokRes['ok']) {
        echo B_RED . "  [AD] token gagal | " . substr($tokRes['raw'], 0, 120) . "\n" . RESET;
        return 'ad_token_fail';
    }

    $token = $tokRes['token'];
    echo B_CYAN . "  [AD] token: " . substr($token, 0, 16) . "...\n" . RESET;

    // ── Icon captcha ──
    $postArr = [
        'csrf_token' => $csrf,
        'ad_verification_token' => $token,
    ];

    list($target, $choices) = parseIconCaptcha($html);
    if ($target && !empty($choices)) {
        $key = matchIcon($target, $choices);
        if ($key) {
            echo B_CYAN . "  [CAPTCHA] {$target} → {$key}\n" . RESET;
            $postArr['icon_captcha_selected'] = $key;
        } else {
            echo B_YELLOW . "  [CAPTCHA] ikon ga match, skip round" . RESET . "\n";
            return 'captcha_skip';
        }
    } else {
        echo B_CYAN . "  [CAPTCHA] kosong di page, skip" . RESET . "\n";
    }

    // ── POST /faucet/claim ──
    $r = req(HOST . '/faucet/claim', 'POST', http_build_query($postArr), [
        'Content-Type: application/x-www-form-urlencoded',
        'Origin: ' . HOST,
        'Referer: ' . HOST . '/faucet',
    ]);
    if ($r === false) return 'fetch_fail';

    if (isLoginPage($r)) return 'session_invalid';
    if (checkDailyLimit($r)) return 'limit_reached';

    // ── Parse result ──
    $amount = null;
    if (preg_match('/Claim successful!\s*Received\s*\+?([0-9.]+)\s*USDT/i', $r, $m)) {
        $amount = $m[1];
    } elseif (preg_match('/alert-success[^>]*>([^<]*?Received[^<]*?)</i', $r, $m)) {
        if (preg_match('/([0-9.]+)/', $m[1], $n)) $amount = $n[1];
    }

    if ($amount) {
        echo B_GREEN . "  [SUCCESS] +{$amount} USDT\n" . RESET;
        $info = ['amount' => $amount];
        return true;
    }

    if (preg_match('/alert-(?:danger|warning)[^>]*>([^<]+)</i', $r, $m)) {
        $err = trim($m[1]);
        echo B_RED . "  [SERVER] {$err}\n" . RESET;

        if (stripos($err, 'adblock') !== false) return ['cooldown' => rand(30, 45)];
        if (stripos($err, 'wait') !== false || stripos($err, 'cooldown') !== false) {
            $cd = 3;
            if (preg_match('/(\d+)\s*second/i', $err, $s)) $cd = (int)$s[1];
            return ['cooldown' => $cd];
        }
        if (stripos($err, 'captcha') !== false || stripos($err, 'verification') !== false || stripos($err, 'token') !== false) {
            return 'captcha_skip';
        }
    }

    if (strlen($r) < 100) return 'fetch_fail';

    file_put_contents("claim_fail.html", $r);
    echo B_RED . "  [ERROR] Claim unknown → claim_fail.html\n" . RESET;
    return 'unknown';
}

// ═══════════════ FARMING ═══════════════
function startFarming($email, $password) {
    if (!doLogin($email, $password)) return;

    $balance = getBalance();
    $dailyCount = getDailyCount();
    echo B_CYAN . "  [BALANCE] " . B_WHITE . $balance . " USDT\n" . RESET;
    echo B_CYAN . "  [DAILY] " . B_WHITE . $dailyCount . "/" . MAX_DAILY_CLAIMS . "\n" . RESET;
    echo B_CYAN . "  [START] Bot jalan...\n\n" . RESET;

    $claims = 0; $failures = 0; $skips = 0;
    $maxFailures = 15;
    $sessionInvalidCount = 0;

    while (true) {
        if (resetDailyIfNeeded()) $dailyCount = 0;

        $round = $claims + $failures + $skips + 1;
        echo "\n" . B_CYAN . "  ╔══ ROUND #{$round} ─ " . date('H:i:s') . " ═══╗" . RESET . "\n";

        if ($dailyCount >= MAX_DAILY_CLAIMS) {
            echo "  " . B_RED . "[LIMIT] Habis kuota harian, tunggu reset." . RESET . "\n";
            timer(strtotime('tomorrow 00:00:00') - time());
            continue;
        }

        $info = [];
        $res = claimFaucet($info);

        if ($res === 'limit_reached') {
            echo "  " . B_RED . "[LIMIT] Daily limit reached." . RESET . "\n";
            break;
        }
        elseif ($res === 'session_invalid') {
            $sessionInvalidCount++;
            echo "  " . B_YELLOW . "[!] Session expired ({$sessionInvalidCount}x), re-login..." . RESET . "\n";
            sleep(5);

            if (!doLogin($email, $password)) {
                echo "  " . B_RED . "[STOP] Re-login gagal." . RESET . "\n";
                if ($sessionInvalidCount >= 3) break;
                sleep(30);
                continue;
            }
            $sessionInvalidCount = 0;
            $balance = getBalance();
            echo B_CYAN . "  [BALANCE] " . B_WHITE . $balance . " USDT\n" . RESET;
            sleep(5);
            continue;
        }
        elseif ($res === 'captcha_skip') {
            $skips++;
            echo "  " . B_YELLOW . "skip round" . RESET . "\n";
            sleep(rand(3, 6));
        }
        elseif ($res === 'no_form' || $res === 'no_csrf') {
            echo "  " . B_YELLOW . "form kosong, tunggu 5s" . RESET . "\n";
            sleep(5);
        }
        elseif ($res === 'fetch_fail') {
            $failures++;
            echo "  " . B_RED . "fetch fail ({$failures}/{$maxFailures})" . RESET . "\n";
            if ($failures >= $maxFailures) { echo "  " . B_RED . "[STOP] Gagal terus." . RESET . "\n"; break; }
            sleep(10);
        }
        elseif ($res === 'ad_token_fail') {
            $failures++;
            echo "  " . B_RED . "ad token fail ({$failures}/{$maxFailures})" . RESET . "\n";
            if ($failures >= $maxFailures) { echo "  " . B_RED . "[STOP] Gagal terus." . RESET . "\n"; break; }
            sleep(8);
        }
        elseif (is_array($res) && isset($res['cooldown'])) {
            $cd = max(1, (int)$res['cooldown']);
            echo "  " . B_YELLOW . "cooldown {$cd}s" . RESET . "\n";
            timer($cd, "Cooldown");
        }
        elseif ($res === true) {
            $claims++; $dailyCount++;
            updateDailyCount($dailyCount);
            $failures = 0;
            $balance = getBalance();
            echo B_CYAN . "  [BALANCE] " . B_WHITE . $balance . " USDT\n" . RESET;
            echo B_CYAN . "  [DAILY] " . B_WHITE . $dailyCount . "/" . MAX_DAILY_CLAIMS . "\n" . RESET;
            echo B_GREEN . "  [TOTAL] {$claims} success" . RESET . "\n";

            $waitS = rand(MIN_CLAIM_DELAY, MAX_CLAIM_DELAY);
            sleep($waitS);
        }
        else {
            $failures++;
            echo B_RED . "  [FAIL] {$failures}/{$maxFailures}" . RESET . "\n";
            if ($failures >= $maxFailures) { echo "  " . B_RED . "[STOP] Gagal terus." . RESET . "\n"; break; }
            sleep(rand(5, 10));
        }

        echo B_CYAN . "  ╚═══════════════════════════════════════╝" . RESET . "\n";
    }

    $balance = getBalance();
    echo "\n" . B_CYAN . "  [FINAL] " . B_WHITE . $balance . " USDT | ";
    echo $claims . " success / " . $skips . " skip / " . $failures . " fail" . RESET . "\n";
}

// ═══════════════ MENU ═══════════════
function printMenu() {
    printBanner();
    echo B_CYAN . "  [1] " . B_GREEN . "Start Farming\n";
    echo B_CYAN . "  [2] " . B_YELLOW . "Config Email & Password\n";
    echo B_CYAN . "  [0] " . B_RED . "Exit\n";
    echo B_CYAN . "==================================================\n";
    echo B_WHITE . "  Pilih: " . RESET;
}

function configEmailPassword() {
    clearScreen();
    printBanner();
    echo B_CYAN . "  ── Konfigurasi Akun ──\n\n";
    echo B_WHITE . "Email: " . RESET;
    $e = trim(fgets(STDIN));
    echo B_WHITE . "Password: " . RESET;
    $p = trim(fgets(STDIN));
    file_put_contents(CONFIG_FILE, json_encode(['email'=>$e, 'password'=>$p], JSON_PRETTY_PRINT));
    echo B_GREEN . "\n  ✅ Config disimpan!\n" . RESET;
    echo B_WHITE . "\n  Tekan Enter untuk kembali...\n" . RESET;
    fgets(STDIN);
}

// ═══════════════ MAIN ═══════════════
printBanner();

if (!file_exists(CONFIG_FILE)) {
    echo "  " . B_YELLOW . "[!] Config belum ada, isi dulu.\n" . RESET;
    echo "  " . DIM . "Enter untuk lanjut..." . RESET;
    fgets(STDIN);
    configEmailPassword();
}

$cfg = json_decode(file_get_contents(CONFIG_FILE), true);
$email = $cfg['email'] ?? '';
$password = $cfg['password'] ?? '';

while (true) {
    printMenu();
    $choice = trim(fgets(STDIN));

    switch ($choice) {
        case '1':
            startFarming($email, $password);
            echo "\n  " . DIM . "Enter untuk kembali..." . RESET;
            fgets(STDIN);
            break;
        case '2':
            configEmailPassword();
            $cfg = json_decode(file_get_contents(CONFIG_FILE), true);
            $email = $cfg['email'] ?? '';
            $password = $cfg['password'] ?? '';
            break;
        case '0':
            echo "\n" . B_GREEN . "  Bye." . RESET . "\n";
            exit(0);
        default:
            echo "\n  " . B_RED . "salah pilihan." . RESET . "\n";
            echo "  " . DIM . "Enter..." . RESET;
            fgets(STDIN);
    }
}
