<?php
/**
 * OURCOINCASH AUTO CLAIM BOT v5.1
 * ScriptMaker : @bgiyannn
 * Fixed by    : @MoneyMaker_w
 * Solver      : Waryono | Skipcha
 */

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');
$configFile = "OurCoin.json";
$cookieFile = __DIR__ . "/OurCoin.txt";

// ═══════════════ ANSI COLORS ═══════════════
define('RESET',   "\033[0m");
define('BOLD',    "\033[1m");
define('DIM',     "\033[2m");
define('RED',     "\033[1;31m");
define('GREEN',   "\033[1;32m");
define('YELLOW',  "\033[1;33m");
define('CYAN',    "\033[1;36m");
define('WHITE',   "\033[1;37m");
define('GRAY',    "\033[0;90m");
define('NEON',    "\033[38;5;46m");
define('NEON_P',  "\033[38;5;201m");
define('NEON_C',  "\033[38;5;51m");
define('NEON_Y',  "\033[38;5;226m");
define('ORANGE',  "\033[38;5;208m");
define('PURPLE',  "\033[38;5;135m");

const R  = RED; const G  = GREEN; const Y  = YELLOW;
const CY = CYAN; const W  = WHITE; const X  = RESET;

const host    = "https://ourcoincash.xyz";
const SITEKEY = "G46xX4hfCTAnit8a3E6JF8f1IEew2xYomNDcDJ49";
const UA      = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36";
const WARYONO_IN  = "https://api.waryono.my.id/in.php";
const WARYONO_RES = "https://api.waryono.my.id/res.php";
const SKIPCHA_IN  = "https://skipcha.online/in.php";
const SKIPCHA_RES = "https://skipcha.online/res.php";

// ═══════════════ UTILS ═══════════════
function clear() { (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w')); }

function countdown($seconds, $prefix = "waiting") {
    $wt = (int)$seconds; if ($wt < 1) return;
    while ($wt > 0) {
        $t = sprintf('%02d:%02d:%02d', floor($wt/3600), floor(($wt%3600)/60), $wt%60);
        echo "\r  " . Y . $prefix . ": " . G . $t . RESET . "   ";
        sleep(1);
        $wt--;
    }
    echo "\r" . str_repeat(' ', 50) . "\r";
}

function req($url, $method='GET', $data=array(), $headers=array(), $follow=true) {
    global $cookieFile;
    $ch = curl_init();
    $opts = array(
        CURLOPT_URL => $url, CURLOPT_RETURNTRANSFER => true, CURLOPT_HEADER => true,
        CURLOPT_FOLLOWLOCATION => $follow,
        CURLOPT_SSL_VERIFYHOST => 0, CURLOPT_SSL_VERIFYPEER => 0,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_CONNECTTIMEOUT => 60, CURLOPT_TIMEOUT => 60,
        CURLOPT_COOKIEFILE => $cookieFile, CURLOPT_COOKIEJAR => $cookieFile,
        CURLOPT_USERAGENT => UA
    );
    if (strtoupper($method) === 'POST') {
        $opts[CURLOPT_POST] = true;
        $opts[CURLOPT_POSTFIELDS] = is_array($data) ? http_build_query($data) : $data;
    }
    curl_setopt_array($ch, $opts);
    $r = curl_exec($ch);
    if ($r) {
        $hs = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
        $out = array(
            'body' => substr($r, $hs),
            'code' => curl_getinfo($ch, CURLINFO_RESPONSE_CODE),
            'head' => substr($r, 0, $hs),
            'url'  => curl_getinfo($ch, CURLINFO_EFFECTIVE_URL)
        );
        curl_close($ch);
        return $out;
    }
    curl_close($ch);
    echo W . "\nnetwork err, retry...\n" . X; sleep(2);
    return req($url, $method, $data, $headers, $follow);
}

function curl_solver($url, $method='GET', $data=array(), $headers=array()) {
    $ch = curl_init();
    $opts = array(
        CURLOPT_URL => $url, CURLOPT_RETURNTRANSFER => true, CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 30, CURLOPT_CONNECTTIMEOUT => 15
    );
    if (!empty($headers)) $opts[CURLOPT_HTTPHEADER] = $headers;
    if (strtoupper($method) === 'POST') {
        $opts[CURLOPT_POST] = true;
        $opts[CURLOPT_POSTFIELDS] = $data;
    }
    curl_setopt_array($ch, $opts);
    $r = curl_exec($ch); curl_close($ch);
    return $r;
}

// ═══════════════ SOLVERS ═══════════════
function solver_submit_waryono($apikey, $method='adslab') {
    $body = json_encode(array(
        "apikey" => $apikey, "methods" => $method,
        "domain" => "ourcoincash.xyz", "sitekey" => SITEKEY,
        "subid" => "widget_user", "json" => 1
    ));
    $r = curl_solver(WARYONO_IN, "POST", $body, array("Content-Type: application/json"));
    $j = json_decode($r, true);
    if (!isset($j['status']) || $j['status'] != 1) return array('ok'=>false,'msg'=>$j['request']??'submit failed');
    return array('ok'=>true, 'id'=>$j['request']);
}

function solver_poll_waryono($apikey, $id) {
    $url = WARYONO_RES . "?apikey=".urlencode($apikey)."&action=get&id=".urlencode($id)."&json=1";
    $j = json_decode(curl_solver($url), true);
    if (!isset($j['status'])) return array('status'=>'pending');
    if ($j['status'] == 1) return array('status'=>'ready','token'=>$j['request']);
    if (($j['request']??'') === 'CAPCHA_NOT_READY') return array('status'=>'pending');
    return array('status'=>'error','msg'=>$j['request']??'unknown');
}

function solver_submit_skipcha($apikey) {
    $url = SKIPCHA_IN . "?" . http_build_query(array("key"=>$apikey,"method"=>"adslab","json"=>1));
    $body = json_encode(array("pageurl"=>host, "sitekey"=>SITEKEY, "subid"=>"widget_user"));
    $r = curl_solver($url, "POST", $body, array("Content-Type: application/json"));
    $j = json_decode($r, true);
    if (!isset($j['status']) || $j['status'] != 1) return array('ok'=>false,'msg'=>$j['request']??'submit failed');
    return array('ok'=>true, 'id'=>$j['request']);
}

function solver_poll_skipcha($apikey, $id) {
    $url = SKIPCHA_RES . "?" . http_build_query(array("key"=>$apikey,"action"=>"get","id"=>$id,"json"=>1));
    $j = json_decode(curl_solver($url), true);
    if (!isset($j['status'])) return array('status'=>'pending');
    if ($j['status'] == 1) return array('status'=>'ready','token'=>$j['request']);
    if (($j['request']??'') === 'CAPCHA_NOT_READY') return array('status'=>'pending');
    return array('status'=>'error','msg'=>$j['request']??'unknown');
}

function solve($apikey, $solver, $label='CAPTCHA') {
    if ($solver === 'skipcha') {
        $s = solver_submit_skipcha($apikey);
    } else {
        $s = solver_submit_waryono($apikey, 'adslab');
        if (!$s['ok'] && stripos($s['msg'], 'ERROR_NO_SUCH_METHOD') !== false) {
            $s = solver_submit_waryono($apikey, 'adslabpro');
        }
    }
    if (!$s['ok']) { echo W . "[$label] " . R . $s['msg'] . X . "\n"; return false; }

    $id = $s['id'];
    echo W . "[$label] task: " . CY . $id . W . " waiting" . X;

    for ($i = 0; $i < 40; $i++) {
        sleep(3);
        $r = ($solver === 'skipcha') ? solver_poll_skipcha($apikey, $id) : solver_poll_waryono($apikey, $id);
        if ($r['status'] === 'ready') {
            if (!empty($r['token']) && stripos($r['token'], 'ERROR') !== 0) {
                echo " " . G . "OK" . X . "\n";
                return $r['token'];
            }
            echo "\n" . W . "[$label] " . R . "invalid token" . X . "\n"; return false;
        }
        if ($r['status'] === 'pending') { echo W . "."; continue; }
        echo "\r\033[K" . W . "[$label] " . R . $r['msg'] . X . "\n"; return false;
    }
    echo "\r\033[K"; return false;
}

// ═══════════════ PARSERS ═══════════════
function get_csrf($html) {
    if (preg_match('/name=["\']csrf_token_name["\'][^>]*value=["\']([^"\']+)["\']/i', $html, $m)) return $m[1];
    if (preg_match('/value=["\']([^"\']+)["\'][^>]*name=["\']csrf_token_name["\']/i', $html, $m)) return $m[1];
    return null;
}
function get_token($html) {
    if (preg_match('/name=["\']token["\'][^>]*value=["\']([^"\']+)["\']/i', $html, $m)) return $m[1];
    return null;
}
function detect_captcha_field($html) {
    if (preg_match_all('/<(?:input|textarea)\b[^>]*name=["\']([^"\']*(?:captcha|adslab|alc)[^"\']*)["\']/i', $html, $m)) return $m[1][0];
    return null;
}
function mask_email($e) {
    if (!filter_var($e, FILTER_VALIDATE_EMAIL)) return $e;
    list($u, $d) = explode('@', $e);
    $l = strlen($u);
    return ($l <= 4 ? substr($u,0,1).'****' : substr($u,0,2).'****'.substr($u,-2)) . '@' . $d;
}
function parse_balance($html) {
    if (preg_match('/class="acc-amount"[^>]*>\s*<i[^>]*><\/i>\s*([\d,\.]+)/i', $html, $m))
        return (float)str_replace(',', '', $m[1]);
    if (preg_match('/Balance.*?([\d,]{4,}\.\d{2})/s', $html, $m))
        return (float)str_replace(',', '', $m[1]);
    return null;
}
function parse_faucet_status($html) {
    $st = "UNKNOWN"; $rw = null; $cl = null;
    if (preg_match('/<h4 class="lh-1 mb-1">\s*([A-Z]+)\s*<\/h4>/', $html, $m)) $st = trim($m[1]);
    if (preg_match('/id="faucetRewardValue">\s*([\d,\.]+)\s*</', $html, $m)) $rw = (int)str_replace(',','',$m[1]);
    if (preg_match('/([\d,]+)\/[\d,]+\s*<\/h4>\s*<h6[^>]*>claims left/', $html, $m)) $cl = (int)str_replace(',','',$m[1]);
    return array('status'=>$st, 'reward'=>$rw, 'claims_left'=>$cl);
}

// ═══════════════ HEADERS ═══════════════
function base_headers($ref='') {
    $h = array(
        'host: ourcoincash.xyz',
        'upgrade-insecure-requests: 1',
        'user-agent: ' . UA,
        'accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'sec-fetch-site: same-origin', 'sec-fetch-mode: navigate',
        'sec-fetch-user: ?1', 'sec-fetch-dest: document',
        'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
    );
    if ($ref) $h[] = 'referer: ' . $ref;
    return $h;
}
function post_headers($ref='') {
    $h = array(
        'host: ourcoincash.xyz',
        'origin: https://ourcoincash.xyz',
        'content-type: application/x-www-form-urlencoded',
        'upgrade-insecure-requests: 1',
        'user-agent: ' . UA,
        'accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'sec-fetch-site: same-origin', 'sec-fetch-mode: navigate',
        'sec-fetch-user: ?1', 'sec-fetch-dest: document',
        'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
    );
    if ($ref) $h[] = 'referer: ' . $ref;
    return $h;
}

// ═══════════════ CONFIG ═══════════════
function get_config($f) {
    $d = file_exists($f) ? json_decode(file_get_contents($f), true) : array();
    if (!is_array($d)) $d = array();
    if (isset($d['apikey']) && !isset($d['apikey_waryono'])) {
        $d['apikey_waryono'] = $d['apikey']; unset($d['apikey']);
    }
    $s = $d['solver'] ?? ''; $aw = $d['apikey_waryono'] ?? '';
    $as = $d['apikey_skipcha'] ?? ''; $em = $d['email'] ?? ''; $pw = $d['password'] ?? '';

    if (empty($s) || empty($em) || empty($pw)) {
        clear();
        echo "\n" . NEON_C . "  ⚙  SETUP WIZARD" . RESET . "\n";
        echo NEON_C . "  " . str_repeat('─', 50) . RESET . "\n\n";
        if (empty($s)) {
            echo WHITE . "  Pilih Solver:\n";
            echo "    " . NEON . "[1]" . WHITE . " Waryono\n";
            echo "    " . NEON . "[2]" . WHITE . " Skipcha\n";
            echo WHITE . "  >> " . NEON_Y;
            $s = (trim(fgets(STDIN)) === '2') ? 'skipcha' : 'waryono';
        }
        if ($s === 'skipcha' && empty($as)) { echo WHITE . "  API Key Skipcha : " . NEON_Y; $as = trim(fgets(STDIN)); }
        elseif ($s === 'waryono' && empty($aw)) { echo WHITE . "  API Key Waryono : " . NEON_Y; $aw = trim(fgets(STDIN)); }
        if (empty($em)) { echo WHITE . "  Email           : " . NEON_Y; $em = trim(fgets(STDIN)); }
        if (empty($pw)) { echo WHITE . "  Password        : " . NEON_Y; $pw = trim(fgets(STDIN)); }

        $d = array('solver'=>$s,'apikey_waryono'=>$aw,'apikey_skipcha'=>$as,'email'=>$em,'password'=>$pw);
        file_put_contents($f, json_encode($d, JSON_PRETTY_PRINT));
        echo "\n" . NEON . "  [✓] Config disimpan ke $f" . RESET . "\n\n";
        sleep(2);
    }
    return $d;
}

// ═══════════════ LOGIN ═══════════════
function do_login($email, $password, $apikey, $solver) {
    echo W . "[LOGIN] " . CY . "user: " . W . mask_email($email) . W . " | solver: " . CY . strtoupper($solver) . X . "\n";

    $r = req(host . "/login", 'GET', array(), base_headers(host . "/"));
    if ($r['code'] != 200) { echo W . "[LOGIN] " . R . "GET /login HTTP " . $r['code'] . X . "\n"; return false; }

    $csrf = get_csrf($r['body']);
    if (!$csrf) { echo W . "[LOGIN] " . R . "csrf tidak ditemukan!" . X . "\n"; return false; }
    $captchaField = detect_captcha_field($r['body']);
    echo W . "[LOGIN] " . CY . "csrf: " . substr($csrf,0,15) . "... | captcha field: " . ($captchaField ?: "(default)") . X . "\n";

    $cap = solve($apikey, $solver, 'LOGIN');
    if (!$cap) { echo W . "[LOGIN] " . R . "solving gagal" . X . "\n"; return false; }
    echo W . "[LOGIN] " . G . "token len: " . strlen($cap) . X . "\n";

    $r2 = req(host . "/login", 'GET', array(), base_headers(host . "/"));
    $csrf2 = get_csrf($r2['body']);
    if ($csrf2) $csrf = $csrf2;
    if ($captchaField === null) $captchaField = detect_captcha_field($r2['body']);
    if ($captchaField === null) $captchaField = 'alcaptcha-response';

    $payload = array(
        "email"            => $email,
        "password"         => $password,
        "captcha"          => "adslabpro",
        "csrf_token_name"  => $csrf,
        $captchaField      => $cap
    );

    $r3 = req(host . "/auth/login", 'POST', $payload, post_headers(host . "/login"), false);
    $location = '';
    if (preg_match('/location:\s*([^\r\n]+)/i', $r3['head'], $lm)) $location = trim($lm[1]);

    if (strpos($location, 'dashboard') !== false || strpos($r3['body'], 'Logout') !== false) {
        echo W . "[LOGIN] " . G . "✓ sukses" . X . "\n";
        req(host . "/dashboard", 'GET', array(), base_headers(host . "/login"));
        return true;
    }

    echo W . "[LOGIN] " . R . "✗ gagal (HTTP " . $r3['code'] . ")" . X . "\n";
    if ($location) {
        $fl = req($location, 'GET', array(), base_headers(host . "/login"), false);
        if (preg_match('/<div[^>]*class=["\'][^"\']*alert-danger[^"\']*["\'][^>]*>(.*?)<\/div>/is', $fl['body'], $m)) {
            echo W . "[ERROR] " . R . trim(preg_replace('/\s+/',' ',strip_tags($m[1]))) . X . "\n";
        }
        file_put_contents("login_fail.html", $fl['body']);
    }
    return false;
}

// ═══════════════ CLAIM ═══════════════
function claim($apikey, $solver) {
    $r = req(host . "/faucet", 'GET', array(), base_headers(host . "/dashboard"));
    if (strpos($r['body'], 'Logout') === false) return array("ok"=>false,"error"=>"session_invalid");

    $info = parse_faucet_status($r['body']);
    echo W . "[FAUCET] " . CY . "status: " . Y . $info['status']
       . W . " | reward: " . Y . ($info['reward']??'-')
       . W . " | left: " . Y . ($info['claims_left']??'-') . X . "\n";

    if ($info['status'] !== 'READY') {
        if (preg_match('/<h4 class="lh-1 mb-1">(\d+)<\/h4>\s*<h6 class="mb-0">minutes/', $r['body'], $m)) {
            return array("ok"=>false, "cooldown"=>(int)$m[1]*60);
        }
        return array("ok"=>false, "cooldown"=>0);
    }

    $csrf = get_csrf($r['body']);
    $token = get_token($r['body']);
    if (!$csrf || !$token) return array("ok"=>false, "error"=>"no_csrf_or_token");

    $cap = solve($apikey, $solver, 'FAUCET');
    if (!$cap) return array("ok"=>false, "error"=>"captcha_failed");

    $captchaField = detect_captcha_field($r['body']) ?: 'alcaptcha-response';

    $payload = array(
        "csrf_token_name" => $csrf,
        "token"           => $token,
        "captcha"         => "adslabpro",
        $captchaField     => $cap
    );

    echo W . "[FAUCET] " . CY . "submit field: " . $captchaField . " | token len: " . strlen($cap) . X . "\n";

    $r2 = req(host . "/faucet/verify", 'POST', $payload, post_headers(host . "/faucet"), false);

    // DEBUG: save response buat inspeksi kalau gagal
    $loc = '';
    if (preg_match('/location:\s*([^\r\n]+)/i', $r2['head'], $lm)) $loc = trim($lm[1]);

    if ($r2['code'] == 303 || $r2['code'] == 302) {
        return array("ok"=>true, "redirect"=>$loc);
    }
    if ($r2['code'] == 200) {
        if (stripos($r2['body'], 'success') !== false || stripos($r2['body'], 'Good job') !== false)
            return array("ok"=>true);
        // Kalau ada alert-danger
        if (preg_match('/<div[^>]*class=["\'][^"\']*alert-danger[^"\']*["\'][^>]*>(.*?)<\/div>/is', $r2['body'], $m)) {
            $msg = trim(preg_replace('/\s+/',' ',strip_tags($m[1])));
            file_put_contents("faucet_fail.html", $r2['body']);
            return array("ok"=>false, "error"=>"server: " . $msg);
        }
        file_put_contents("faucet_fail.html", $r2['body']);
        return array("ok"=>false, "error"=>"http_200_no_success");
    }
    file_put_contents("faucet_fail.html", $r2['body']);
    return array("ok"=>false, "error"=>"http_".$r2['code']);
}

// ═══════════════ MAIN ═══════════════
clear();
$cfg = get_config($configFile);
$solver = $cfg['solver'];

clear();
echo "\n" . NEON_C . "
  ╔══════════════════════════════════════════════════════════╗
  ║             OURCOINCASH — AUTO CLAIM BOT v5.1            ║
  ║        ScriptMaker @bgiyannn | Fixed @MoneyMaker_w       ║
  ╚══════════════════════════════════════════════════════════╝
" . RESET . "\n";

echo W . "  Solver : " . CY . strtoupper($solver) . X . "\n";
echo W . "  Email  : " . CY . mask_email($cfg['email']) . X . "\n";
echo W . "  " . str_repeat('─', 58) . X . "\n";
echo G . "    [1]" . W . " Lanjut " . CY . strtoupper($solver) . "\n";
$other = ($solver==='waryono') ? 'SKIPCHA' : 'WARYONO';
echo G . "    [2]" . W . " Ganti ke " . CY . $other . "\n";
echo G . "    [3]" . W . " Edit config\n";
echo G . "    [4]" . W . " Reset\n";
echo W . "  >> " . Y;
$menu = trim(fgets(STDIN));

if ($menu === '2') {
    $cfg['solver'] = ($solver==='waryono') ? 'skipcha' : 'waryono';
    $kn = 'apikey_' . $cfg['solver'];
    if (empty($cfg[$kn])) { echo W . "API Key " . CY . $cfg['solver'] . W . ": " . Y; $cfg[$kn] = trim(fgets(STDIN)); }
    file_put_contents($configFile, json_encode($cfg, JSON_PRETTY_PRINT));
    echo G . "→ " . strtoupper($cfg['solver']) . "\n" . X; sleep(1);
} elseif ($menu === '3') {
    echo W . "Email (enter skip): " . Y; $e=trim(fgets(STDIN)); if($e)$cfg['email']=$e;
    echo W . "Password (enter skip): " . Y; $p=trim(fgets(STDIN)); if($p)$cfg['password']=$p;
    $kn = 'apikey_'.$cfg['solver'];
    echo W . "API Key (enter skip): " . Y; $k=trim(fgets(STDIN)); if($k)$cfg[$kn]=$k;
    file_put_contents($configFile, json_encode($cfg, JSON_PRETTY_PRINT));
    echo G . "saved.\n" . X; sleep(1);
} elseif ($menu === '4') {
    @unlink($configFile); @unlink($cookieFile);
    echo Y . "reset. Jalankan ulang.\n" . X; exit;
}

$cfg = json_decode(file_get_contents($configFile), true);
$apikey = $cfg['apikey_' . $cfg['solver']] ?? '';
$solver = $cfg['solver'];

clear();
echo W . "Solver : " . CY . strtoupper($solver) . X . "\n\n";

if (!do_login($cfg['email'], $cfg['password'], $apikey, $solver)) {
    echo W . "[!] " . R . "login gagal." . X . "\n";
    exit;
}

$bal = parse_balance(req(host . "/dashboard", 'GET', array(), base_headers(host . "/"))['body']);
if ($bal === null) { echo W . "[!] " . R . "gagal ambil balance." . X . "\n"; exit; }

echo "\n";
echo G . "╔══════════════════════════════════════════════════════════╗\n";
echo G . "║  ✓ LOGIN SUCCESS                                          ║\n";
echo G . "╠══════════════════════════════════════════════════════════╣\n";
echo G . "║" . W . "  Email          : " . str_pad(mask_email($cfg['email']), 39) . G . "║\n";
echo G . "║" . W . "  Solver         : " . str_pad(strtoupper($solver), 39) . G . "║\n";
echo G . "║" . W . "  Balance        : " . str_pad(number_format($bal, 2) . " coins", 39) . G . "║\n";
echo G . "╚══════════════════════════════════════════════════════════╝\n" . X;
echo "\n";

$round = 0;
while (true) {
    $round++;
    echo "\n" . NEON_P . "╭─── ROUND #$round ─── " . date("H:i:s") . " ───╮" . X . "\n";

    $before = parse_balance(req(host . "/dashboard", 'GET', array(), base_headers(host . "/"))['body']);
    if ($before === null) {
        echo W . "[!] " . Y . "session hilang, re-login..." . X . "\n";
        if (!do_login($cfg['email'], $cfg['password'], $apikey, $solver)) { exit; }
        continue;
    }

    $res = claim($apikey, $solver);

    if (!empty($res['ok'])) {
        sleep(3);
        $after = parse_balance(req(host . "/dashboard", 'GET', array(), base_headers(host . "/"))['body']);
        $diff = $after - $before;
        if ($diff > 0) {
            echo W . "[CLAIM] " . G . "✓ +" . number_format($diff, 2) . " coins | balance: " . G . number_format($after, 2) . X . "\n";
            countdown(5, "Next claim");
        } else {
            echo W . "[CLAIM] " . Y . "⚠ server OK tapi balance gak berubah" . X . "\n";
            echo W . "[CLAIM] " . DIM . "kemungkinan: captcha token ditolak server (cek faucet_fail.html)" . X . "\n";
            countdown(5, "Retry");
        }
    } elseif (isset($res['cooldown'])) {
        if ($res['cooldown'] <= 0) {
            countdown(5, "Waiting");
        } else {
            echo W . "[COOLDOWN] " . Y . sprintf('%02d:%02d', floor($res['cooldown']/60), $res['cooldown']%60) . X . "\n";
            countdown($res['cooldown'], "Cooldown");
        }
    } else {
        $err = $res['error'] ?? 'unknown';
        if ($err === 'captcha_failed') {
            echo W . "[CLAIM] " . Y . "captcha gagal, retry" . X . "\n";
            echo NEON . "╰─────────────────────────────────────╯" . X . "\n";
            continue;
        }
        echo W . "[CLAIM] " . R . "✗ gagal: " . $err . X . "\n";
        if ($err === 'session_invalid') {
            if (!do_login($cfg['email'], $cfg['password'], $apikey, $solver)) exit;
        } else {
            countdown(5, "Retry");
        }
    }
    echo NEON . "╰─────────────────────────────────────╯" . X . "\n";
}
