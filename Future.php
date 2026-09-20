<?php
/**
 * CryptoFuture Auto Claim — Loop Mode / No Persistence
 * - Zero file I/O. Cookies live in-memory only.
 * - Auto loop with cooldown.
 * - Detects daily limit → stop.
 * - Caps at MAX_COINS (250).
 * - Auto re-login if session drops.
 */

define("RED","\033[0;31m"); define("GRN","\033[0;32m");
define("YEL","\033[0;33m"); define("BLU","\033[0;34m");
define("MAG","\033[0;35m"); define("CYN","\033[0;36m");
define("WHT","\033[0;37m"); define("RST","\033[0m");
define("BOLD","\033[1m");

const SITE  = "https://cryptofuture.co.in";
const HOME  = SITE . "/";
const LOGIN = SITE . "/auth/login";
const EARN  = SITE . "/faucet/earn";
const DASH  = SITE . "/dashboard";

const SOLVER_IN  = "https://api.waryono.my.id/in.php";
const SOLVER_RES = "https://api.waryono.my.id/res.php";

const UA = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36";

const MAX_COINS = 250.0;   // stop after earning this much in this run
const LOOP_SLEEP_STEP = 5; // check cooldown every N seconds

/* ═══════════ IN-MEMORY COOKIE JAR ═══════════ */
$COOKIES = [];
function cookie_str(){
    global $COOKIES;
    if (!$COOKIES) return '';
    $p = [];
    foreach ($COOKIES as $k => $v) $p[] = "$k=$v";
    return implode('; ', $p);
}
function cookie_absorb($headers){
    global $COOKIES;
    if (preg_match_all('/^set-cookie:\s*([^=]+)=([^;]+)/mi', $headers, $m, PREG_SET_ORDER)) {
        foreach ($m as $c) $COOKIES[trim($c[1])] = trim($c[2]);
    }
}
function cookie_seed($name, $value){
    global $COOKIES;
    if ($value !== '') $COOKIES[$name] = $value;
}

/* ═══════════ UI ═══════════ */
function vlen($s){ return strlen(preg_replace('/\x1b\[[0-9;]*m/','',$s)); }
function pad($s,$w){ return $s . str_repeat(' ', max(0, $w - vlen($s))); }
function line($c,$w=54){ return CYN.'│'.RST.pad('  '.$c,$w).CYN.'│'.RST; }
function mid($w=54){ return CYN.'├'.str_repeat('─',$w+2).'┤'.RST; }
function bot($w=54){ return CYN.'╰'.str_repeat('─',$w+2).'╯'.RST; }
function top_plain($w=54){ return CYN.'╭'.str_repeat('─',$w+2).'╮'.RST; }

function log_line($msg, $tag='i'){
    $ic = ['i'=>CYN.'›'.RST, 'ok'=>GRN.'✓'.RST, 'er'=>RED.'✗'.RST, 'wr'=>YEL.'!'.RST, 'in'=>BLU.'●'.RST, 'bi'=>GRN.'₹'.RST];
    echo WHT.'['.date('H:i:s').']'.RST.' '.($ic[$tag]??'›').' '.$msg."\n"; flush();
}
function ask($p){ echo WHT.$p.RST; return trim(fgets(STDIN)); }
function fmt($s){
    $s=(int)$s; if($s<=0)return '0s';
    if($s>=3600) return floor($s/3600).'h'.floor(($s%3600)/60).'m';
    if($s>=60)   return floor($s/60).'m'.($s%60).'s';
    return $s.'s';
}
function clear_screen(){ echo (strtoupper(substr(PHP_OS,0,3))==='WIN') ? system('cls') : system('clear'); }

/* ═══════════ HTTP ═══════════ */
function req($url, $method='GET', $data=null, $headers=[]){
    $ch = curl_init();
    $def = [
        "User-Agent: ".UA,
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language: id-ID,id;q=0.9,en;q=0.8",
        "Upgrade-Insecure-Requests: 1",
        "Referer: ".HOME,
    ];
    if ($method === 'POST') $def[] = "Content-Type: application/x-www-form-urlencoded";
    $cs = cookie_str();
    if ($cs !== '') $def[] = "Cookie: ".$cs;

    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_MAXREDIRS => 5,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_USERAGENT => UA,
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
    if ($resp === false) return ['body'=>'', 'code'=>0, 'headers'=>'', 'error'=>curl_error($ch)];
    $info = curl_getinfo($ch);
    $hs = $info['header_size'];
    $rawHeaders = substr($resp, 0, $hs);
    $body = substr($resp, $hs);
    cookie_absorb($rawHeaders);
    return ['body'=>$body, 'code'=>$info['http_code'], 'headers'=>$rawHeaders, 'error'=>''];
}

/* ═══════════ LOGIN ═══════════ */
function login($wallet){
    log_line("re-login ".$wallet, 'in');
    $r = req(LOGIN);
    if ($r['code'] !== 200) return ['ok'=>false, 'msg'=>"GET login HTTP {$r['code']}"];
    $html = $r['body'];

    $csrf = '';
    foreach ([
        '/name=["\']?csrf_token_name["\']?[^>]*value=["\']([^"\']+)["\']/i',
        '/value=["\']([^"\']+)["\'][^>]*name=["\']?csrf_token_name["\']?/i',
    ] as $p) {
        if (preg_match($p, $html, $m)) { $csrf = $m[1]; break; }
    }
    if ($csrf === '') {
        if (stripos($html, 'Just a moment') !== false) return ['ok'=>false, 'msg'=>'CF challenge'];
        return ['ok'=>false, 'msg'=>'CSRF not found'];
    }

    $device = "dev_".substr(md5(uniqid(mt_rand(), true)), 0, 20);
    $post = http_build_query([
        'wallet' => $wallet,
        'csrf_token_name' => $csrf,
        'device_token' => $device,
    ]);

    $r2 = req(LOGIN, 'POST', $post, ['Origin: '.SITE, 'Referer: '.LOGIN]);
    if ($r2['code'] >= 500) return ['ok'=>false, 'msg'=>"login POST HTTP {$r2['code']}"];

    $r3 = req(DASH);
    if (stripos($r3['body'], 'auth/logout') !== false || stripos($r3['body'], 'Logout') !== false)
        return ['ok'=>true, 'msg'=>'login ok'];
    return ['ok'=>false, 'msg'=>'cookie not accepted'];
}

/* ═══════════ PARSER ═══════════ */
function parse_earn($html){
    $o = ['csrf'=>'','token'=>'','ticket'=>'','wallet'=>'','wait'=>0,'balance'=>null,'antibot'=>[],'has_form'=>false];

    if (preg_match('/<form[^>]+id="fauform"[^>]*>(.*?)<\/form>/si', $html, $fm)) {
        $o['has_form'] = true;
        $in = $fm[1];
        if (preg_match('/name="csrf_token_name"[^>]*value="([^"]*)"/i', $in, $m)) $o['csrf'] = $m[1];
        if (preg_match('/name="token"[^>]*value="([^"]*)"/i', $in, $m)) $o['token'] = $m[1];
        if (preg_match('/name="earn_ticket"[^>]*value="([^"]*)"/i', $in, $m)) $o['ticket'] = $m[1];
        if (preg_match('/name="wallet"[^>]*value="([^"]*)"/i', $in, $m)) $o['wallet'] = html_entity_decode($m[1]);
    }
    if (preg_match('/let\s+wait\s*=\s*(\d+)/i', $html, $m)) $o['wait'] = (int)$m[1];
    if (preg_match('/balance-amount[^>]*>\s*([0-9.,]+)/i', $html, $m)) $o['balance'] = (float)str_replace(',', '', $m[1]);
    elseif (preg_match('/TOTAL BALANCE.*?([0-9.]+)\s*Coins/si', $html, $m)) $o['balance'] = (float)$m[1];

    if (preg_match_all('/<span[^>]*class="antibotlinks"[^>]*>(.*?)<\/span>/si', $html, $all)) {
        foreach ($all[1] as $chunk) {
            if (preg_match_all('/<img[^>]+src=["\']([^"\']+)["\']/i', $chunk, $im))
                foreach ($im[1] as $src) $o['antibot'][] = $src;
            if (preg_match_all('/data:image\/[^;]+;base64,([A-Za-z0-9+\/=]+)/i', $chunk, $bm))
                foreach ($bm[1] as $b64) $o['antibot'][] = $b64;
            $t = trim(strip_tags($chunk));
            if ($t !== '' && strlen($t) < 64) $o['antibot'][] = 'TEXT:'.$t;
        }
    }
    return $o;
}

/* ═══════════ ANTIBOT ═══════════ */
function solve_antibot($b64, $apikey){
    if (empty($apikey)) return ['ok'=>false, 'msg'=>'apikey kosong'];
    $payload = json_encode(['apikey'=>$apikey, 'methods'=>'antibot', 'main'=>$b64, 'json'=>1]);
    $r = req(SOLVER_IN, 'POST', $payload, ['Content-Type: application/json', 'Referer: '.SOLVER_IN]);
    $j = json_decode($r['body'], true);
    if (!is_array($j) || (int)($j['status']??0) !== 1) return ['ok'=>false, 'msg'=>'submit gagal'];
    $id = $j['request'];

    for ($i = 0; $i < 40; $i++) {
        $q = http_build_query(['apikey'=>$apikey, 'id'=>$id, 'action'=>'get', 'json'=>1]);
        $r2 = req(SOLVER_RES."?".$q);
        $body = trim($r2['body']);
        if (stripos($body, 'OK|') === 0) return ['ok'=>true, 'token'=>substr($body, 3)];
        $j2 = json_decode($body, true);
        if (is_array($j2)) {
            if ((int)($j2['status']??0) === 1) return ['ok'=>true, 'token'=>$j2['request']??''];
            if (($j2['request']??'') === 'CAPCHA_NOT_READY') { echo CYN.'.'.RST; flush(); sleep(3); continue; }
            if (stripos($j2['request']??'', 'ERROR') !== false) return ['ok'=>false, 'msg'=>$j2['request']];
        }
        if (stripos($body, 'CAPCHA_NOT_READY') !== false) { echo CYN.'.'.RST; flush(); sleep(3); continue; }
        sleep(3);
    }
    return ['ok'=>false, 'msg'=>'timeout'];
}

/* ═══════════ DAILY LIMIT DETECTOR ═══════════ */
function is_daily_limit($html){
    $needles = [
        'daily limit', 'daily_limit', 'limit reached',
        'you have reached', 'maximum claim', 'max claim',
        'no more claims', 'come back tomorrow', 'come back later',
        'exceeded', 'too many claim', 'limit for today',
    ];
    $low = strtolower($html);
    foreach ($needles as $n) if (strpos($low, $n) !== false) return true;
    return false;
}

/* ═══════════ BALANCE ═══════════ */
function fetch_balance(){
    $r = req(EARN);
    return parse_earn($r['body'])['balance'];
}

/* ═══════════ BANNER ═══════════ */
function print_banner($wallet, $apikey){
    clear_screen();
    echo top_plain(54)."\n";
    echo CYN.'│'.RST.pad(MAG.BOLD.'  ⚡ CryptoFuture — AUTO LOOP MODE ⚡'.RST, 56).CYN.'│'.RST."\n";
    echo mid(54)."\n";
    echo line(YEL.'◆'.RST.' Wallet  : '.CYN.substr($wallet, 0, 3).str_repeat('*', max(0, strlen($wallet) - 10)).substr($wallet, -7))."\n";
    echo line(YEL.'◆'.RST.' Max     : '.WHT.MAX_COINS.' Coins')."\n";
    echo line(YEL.'◆'.RST.' Session : '.GRN.'in-memory only')."\n";
    echo bot(54)."\n\n";
}

/* ═══════════ MAIN ═══════════ */
clear_screen();
echo top_plain(54)."\n";
echo CYN.'│'.RST.pad(MAG.BOLD.'  ⚡ CryptoFuture — AUTO LOOP ⚡'.RST, 56).CYN.'│'.RST."\n";
echo mid(54)."\n";
echo line(YEL.'◆'.RST.' Mode : '.WHT.'Loop until daily limit / '.MAX_COINS.' Coins')."\n";
echo line(YEL.'◆'.RST.' Save : '.GRN.'nothing (memory only)')."\n";
echo bot(54)."\n\n";

$wallet = ask("  Wallet email   : ");
if (!$wallet) { echo RED."wallet kosong\n"; exit(1); }

$apikey = ask("  Waryono apikey : ");
if (!$apikey) { echo RED."apikey kosong\n"; exit(1); }

$cfc = ask("  cf_clearance   : ");
cookie_seed('cf_clearance', $cfc);

echo "\n";

/* Ensure logged in */
$r = req(EARN);
if (strpos($r['body'], 'id="fauform"') === false) {
    $lr = login($wallet);
    if (!$lr['ok']) { log_line("login gagal: ".$lr['msg'], 'er'); exit(1); }
    log_line("login ok", 'ok');
}

/* Init stats */
$sessionStart = time();
$earned = 0.0;
$claims = 0;
$fails  = 0;
$balNow = null;
$dailyLimitHit = false;

print_banner($wallet, $apikey);

/* ═══════════ LOOP ═══════════ */
$round = 0;
while (true) {
    $round++;

    /* Cap check */
    if ($earned >= MAX_COINS) {
        log_line("cap tercapai (".number_format($earned, 4)." Coins ≥ ".MAX_COINS.") — stop", 'ok');
        break;
    }

    echo "\n".MAG."  ┌─ Round #".$round." ─────────────────────────────".RST."\n";

    /* Fetch /earn */
    $r = req(EARN);
    $html = $r['body'];

    /* Session check */
    if (strpos($html, 'id="fauform"') === false) {
        if (stripos($html, 'auth/login') !== false || stripos($html, 'Sign in') !== false || stripos($html, 'Logout') === false) {
            log_line("session drop — re-login", 'wr');
            $lr = login($wallet);
            if (!$lr['ok']) {
                log_line("re-login gagal: ".$lr['msg']." — tunggu 60s", 'er');
                sleep(60);
                continue;
            }
            log_line("re-login ok", 'ok');
            continue;
        }
    }

    $info = parse_earn($html);
    if ($info['balance'] !== null) $balNow = $info['balance'];

    /* Daily limit in GET? */
    if (is_daily_limit($html)) {
        log_line("DAILY LIMIT terdeteksi di GET — stop", 'er');
        $dailyLimitHit = true;
        break;
    }

    /* Cooldown */
    if ($info['wait'] > 0) {
        $w = $info['wait'];
        log_line("cooldown ".fmt($w)." (bal: ".number_format((float)$balNow, 4).")", 'wr');
        echo CYN."  ⏳ waiting".RST;
        while ($w > 0) {
            $chunk = min($w, LOOP_SLEEP_STEP);
            sleep($chunk);
            $w -= $chunk;
            echo CYN.".".RST; flush();
        }
        echo "\n";
        continue;
    }

    /* Form present but no wait → claimable */
    if (!$info['has_form']) {
        log_line("no form & no wait — unknown state", 'er');
        $fails++;
        sleep(15);
        continue;
    }

    /* Antibot */
    if (!empty($info['antibot'])) {
        log_line("antibot: ".count($info['antibot']), 'in');
        $abOk = true;
        foreach ($info['antibot'] as $src) {
            if (strpos($src, 'TEXT:') === 0) continue;
            $b64 = $src;
            if (!preg_match('#^[A-Za-z0-9+/=]+$#', $src)) {
                if (strpos($src, 'http') !== 0) $src = SITE . (strpos($src, '/') === 0 ? '' : '/') . $src;
                $img = req($src);
                if (empty($img['body'])) continue;
                $b64 = base64_encode($img['body']);
            }
            echo CYN."  ◇ solving".RST;
            $sol = solve_antibot($b64, $apikey);
            echo "\n";
            if (!$sol['ok']) { log_line("antibot fail: ".$sol['msg'], 'er'); $abOk = false; break; }
        }
        if (!$abOk) { $fails++; sleep(rand(20, 40)); continue; }
    }

    /* POST */
    sleep(rand(2, 4));
    $smart = base64_encode(json_encode([
        'ts' => (int)(microtime(true) * 1000),
        'cpu' => 8, 'mem' => 8, 'w' => 384, 'h' => 832,
        'touch' => 5, 'moves' => rand(0, 3),
    ]));
    $fp = hash('sha256', UA.'384x832');
    $post = http_build_query([
        'csrf_token_name' => $info['csrf'],
        'token'           => $info['token'],
        'earn_ticket'     => $info['ticket'],
        'fp_hash'         => $fp,
        'confirm_wallet'  => '',
        'wallet'          => $info['wallet'],
        'smart_token'     => $smart,
        'captcha'         => 'smartcaptcha',
    ]);

    $r2 = req(EARN, 'POST', $post, ['Origin: '.SITE, 'Referer: '.EARN]);
    $respHtml = $r2['body'];

    /* Result detection */
    $success = false;
    $amount  = 0.0;

    if ($r2['code'] === 200) {
        if (preg_match("/Swal\.fire\(\{[^}]*html:\s*'([^']+)'/i", $respHtml, $m)) {
            $msg = strip_tags($m[1]);
            if (preg_match('/([0-9.]+)\s+Coins/i', $msg, $am)) { $amount = (float)$am[1]; $success = true; }
            if (stripos($msg, 'success') !== false) $success = true;
            if (is_daily_limit($msg)) { $dailyLimitHit = true; }
        }
        if (!$success && preg_match('/Success!.*?([0-9.]+)\s+Coins/i', $respHtml, $m)) {
            $amount = (float)$m[1]; $success = true;
        }
    }

    /* 500 / DB error → re-check balance */
    if (!$success && ($r2['code'] === 500 || stripos($respHtml, 'Database Error') !== false)) {
        log_line("HTTP 500 / DB err — re-check balance", 'wr');
        sleep(2);
        $balAfter = fetch_balance();
        $delta = (float)$balAfter - (float)$balNow;
        if ($delta > 0) {
            $success = true;
            $amount = $delta;
            $balNow = $balAfter;
        }
    }

    /* Daily limit via response body */
    if (!$success && is_daily_limit($respHtml)) $dailyLimitHit = true;

    /* Report */
    if ($success) {
        $claims++;
        $earned += $amount;
        if ($balNow !== null) $balNow += $amount;
        log_line("✓ +".number_format($amount, 4)." | total: ".number_format($earned, 4)." | bal: ".number_format((float)$balNow, 4), 'ok');
    } else {
        $fails++;
        log_line("✗ fail (HTTP ".$r2['code'].")", 'er');
    }

    /* Stop conditions */
    if ($dailyLimitHit) {
        log_line("DAILY LIMIT reached — stop", 'er');
        break;
    }
    if ($earned >= MAX_COINS) {
        log_line("cap ".MAX_COINS." tercapai — stop", 'ok');
        break;
    }

    /* Cooldown before next */
    $cd = $success ? 65 : rand(20, 40);
    echo CYN."  ⏳ next in ".fmt($cd).RST;
    $w = $cd;
    while ($w > 0) {
        $chunk = min($w, LOOP_SLEEP_STEP);
        sleep($chunk);
        $w -= $chunk;
        echo CYN.".".RST; flush();
    }
    echo "\n";
}

/* ═══════════ SUMMARY ═══════════ */
$uptime = time() - $sessionStart;
echo "\n".CYN.'╭'.str_repeat('─',56).'╮'.RST."\n";
echo CYN.'│'.RST.pad(MAG.BOLD.'  FINAL SUMMARY'.RST, 56).CYN.'│'.RST."\n";
echo mid(54)."\n";
echo line('Status  : '.($dailyLimitHit ? RED.'Daily limit'.RST : GRN.'Cap reached / done'.RST))."\n";
echo line('Claims  : '.GRN.BOLD.$claims.RST.'    Failed : '.RED.$fails)."\n";
echo line('Earned  : '.GRN.BOLD.'+'.number_format($earned, 4).' Coins'.RST)."\n";
if ($balNow !== null) echo line('Balance : '.GRN.number_format((float)$balNow, 4).' Coins')."\n";
echo line('Uptime  : '.fmt($uptime))."\n";
echo bot(54)."\n\n";

echo WHT.'  ~ session flushed from memory'.RST."\n";
exit(0);
