<?php
/**
 * CryptoFuture Auto Claim — Endless Loop (Email Only)
 * - Only asks for wallet email.
 * - cf_clearance asked ONLY if CF challenge appears.
 * - No solver, no cap, no daily limit stop.
 * - No file I/O. In-memory cookies only.
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

const UA = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36";

const LOOP_SLEEP_STEP = 5;

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
    $ic = ['i'=>CYN.'›'.RST, 'ok'=>GRN.'✓'.RST, 'er'=>RED.'✗'.RST, 'wr'=>YEL.'!'.RST, 'in'=>BLU.'●'.RST];
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

/* ═══════════ CF DETECT ═══════════ */
function is_cf_challenge($html){
    return stripos($html, 'Just a moment') !== false
        || stripos($html, 'cf-challenge') !== false
        || stripos($html, 'Checking your browser') !== false
        || stripos($html, 'cf_chl_opt') !== false;
}

/* ═══════════ LOGIN ═══════════ */
function login($wallet){
    log_line("login ".$wallet, 'in');
    $r = req(LOGIN);
    if ($r['code'] !== 200) return ['ok'=>false, 'msg'=>"GET login HTTP {$r['code']}", 'cf'=>false];
    $html = $r['body'];

    if (is_cf_challenge($html)) return ['ok'=>false, 'msg'=>'CF challenge', 'cf'=>true];

    $csrf = '';
    foreach ([
        '/name=["\']?csrf_token_name["\']?[^>]*value=["\']([^"\']+)["\']/i',
        '/value=["\']([^"\']+)["\'][^>]*name=["\']?csrf_token_name["\']?/i',
    ] as $p) {
        if (preg_match($p, $html, $m)) { $csrf = $m[1]; break; }
    }
    if ($csrf === '') return ['ok'=>false, 'msg'=>'CSRF not found', 'cf'=>false];

    $device = "dev_".substr(md5(uniqid(mt_rand(), true)), 0, 20);
    $post = http_build_query([
        'wallet' => $wallet,
        'csrf_token_name' => $csrf,
        'device_token' => $device,
    ]);

    $r2 = req(LOGIN, 'POST', $post, ['Origin: '.SITE, 'Referer: '.LOGIN]);
    if ($r2['code'] >= 500) return ['ok'=>false, 'msg'=>"login POST HTTP {$r2['code']}", 'cf'=>false];

    $r3 = req(DASH);
    if (stripos($r3['body'], 'auth/logout') !== false || stripos($r3['body'], 'Logout') !== false)
        return ['ok'=>true, 'msg'=>'login ok', 'cf'=>false];
    return ['ok'=>false, 'msg'=>'cookie not accepted', 'cf'=>false];
}

/* ═══════════ PARSER ═══════════ */
function parse_earn($html){
    $o = ['csrf'=>'','token'=>'','ticket'=>'','wallet'=>'','wait'=>0,'balance'=>null,'has_form'=>false];

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

    return $o;
}

/* ═══════════ BALANCE ═══════════ */
function fetch_balance(){
    $r = req(EARN);
    return parse_earn($r['body'])['balance'];
}

/* ═══════════ CF PROMPT ═══════════ */
function prompt_cf(){
    echo "\n".YEL."  ⚠ Cloudflare challenge detected.".RST."\n";
    echo "  Grab fresh cf_clearance from browser DevTools → Application → Cookies → cryptofuture.co.in\n";
    $cf = ask("  cf_clearance   : ");
    cookie_seed('cf_clearance', $cf);
    return $cf !== '';
}

/* ═══════════ MAIN ═══════════ */
clear_screen();
echo top_plain(54)."\n";
echo CYN.'│'.RST.pad(MAG.BOLD.'  ⚡ CryptoFuture — ENDLESS LOOP ⚡'.RST, 56).CYN.'│'.RST."\n";
echo mid(54)."\n";
echo line(YEL.'◆'.RST.' Input : '.WHT.'Email only')."\n";
echo line(YEL.'◆'.RST.' Mode  : '.WHT.'Loop forever (Ctrl+C to stop)')."\n";
echo line(YEL.'◆'.RST.' Save  : '.GRN.'nothing (memory only)')."\n";
echo bot(54)."\n\n";

$wallet = ask("  Wallet email   : ");
if (!$wallet) { echo RED."wallet kosong\n"; exit(1); }

echo "\n";
log_line("probing /faucet/earn...", 'in');
$r = req(EARN);
$html = $r['body'];

if (is_cf_challenge($html)) {
    if (!prompt_cf()) { echo RED."  no cf_clearance, exit\n"; exit(1); }
    $r = req(EARN);
    $html = $r['body'];
    if (is_cf_challenge($html)) { echo RED."  still CF, exit\n"; exit(1); }
}

if (strpos($html, 'id="fauform"') === false) {
    $lr = login($wallet);
    if (!$lr['ok']) {
        if (!empty($lr['cf'])) {
            if (!prompt_cf()) { echo RED."  exit\n"; exit(1); }
            $lr = login($wallet);
        }
        if (!$lr['ok']) { log_line("login gagal: ".$lr['msg'], 'er'); exit(1); }
    }
    log_line("login ok", 'ok');
}

/* Stats */
$sessionStart = time();
$earned = 0.0;
$claims = 0;
$fails  = 0;
$balNow = null;

/* ═══════════ LOOP ═══════════ */
$round = 0;
while (true) {
    $round++;
    echo "\n".MAG."  ┌─ Round #".$round." ─────────────────────────────".RST."\n";

    $r = req(EARN);
    $html = $r['body'];

    /* CF mid-run */
    if (is_cf_challenge($html)) {
        log_line("CF challenge — butuh cf_clearance baru", 'wr');
        if (!prompt_cf()) { log_line("abort", 'er'); break; }
        continue;
    }

    /* Session drop */
    if (strpos($html, 'id="fauform"') === false
        && (stripos($html, 'auth/login') !== false || stripos($html, 'Sign in') !== false)) {
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

    $info = parse_earn($html);
    if ($info['balance'] !== null) $balNow = $info['balance'];

    /* Cooldown */
    if ($info['wait'] > 0) {
        $w = $info['wait'];
        log_line("cooldown ".fmt($w)." (bal: ".number_format((float)$balNow, 4).")", 'wr');
        echo CYN."  ⏳ waiting".RST;
        while ($w > 0) { $c = min($w, LOOP_SLEEP_STEP); sleep($c); $w -= $c; echo CYN.".".RST; flush(); }
        echo "\n";
        continue;
    }

    /* No form & no wait */
    if (!$info['has_form']) {
        log_line("no form & no wait — unknown", 'er');
        $fails++;
        sleep(15);
        continue;
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

    $success = false;
    $amount  = 0.0;

    if ($r2['code'] === 200) {
        if (preg_match("/Swal\.fire\(\{[^}]*html:\s*'([^']+)'/i", $respHtml, $m)) {
            $msg = strip_tags($m[1]);
            if (preg_match('/([0-9.]+)\s+Coins/i', $msg, $am)) { $amount = (float)$am[1]; $success = true; }
            if (stripos($msg, 'success') !== false) $success = true;
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
        if ($delta > 0) { $success = true; $amount = $delta; $balNow = $balAfter; }
    }

    if ($success) {
        $claims++;
        $earned += $amount;
        if ($balNow !== null) $balNow += $amount;
        log_line("✓ +".number_format($amount, 4)." | total: ".number_format($earned, 4)." | bal: ".number_format((float)$balNow, 4), 'ok');
    } else {
        $fails++;
        log_line("✗ fail (HTTP ".$r2['code'].")", 'er');
    }

    $cd = $success ? 65 : rand(20, 40);
    echo CYN."  ⏳ next in ".fmt($cd).RST;
    $w = $cd;
    while ($w > 0) { $c = min($w, LOOP_SLEEP_STEP); sleep($c); $w -= $c; echo CYN.".".RST; flush(); }
    echo "\n";
}

/* ═══════════ SUMMARY ═══════════ */
$uptime = time() - $sessionStart;
echo "\n".CYN.'╭'.str_repeat('─',56).'╮'.RST."\n";
echo CYN.'│'.RST.pad(MAG.BOLD.'  FINAL SUMMARY'.RST, 56).CYN.'│'.RST."\n";
echo mid(54)."\n";
echo line('Claims  : '.GRN.BOLD.$claims.RST.'    Failed : '.RED.$fails)."\n";
echo line('Earned  : '.GRN.BOLD.'+'.number_format($earned, 4).' Coins'.RST)."\n";
if ($balNow !== null) echo line('Balance : '.GRN.number_format((float)$balNow, 4).' Coins')."\n";
echo line('Uptime  : '.fmt($uptime))."\n";
echo bot(54)."\n\n";

echo WHT.'  ~ session flushed from memory'.RST."\n";
exit(0);
