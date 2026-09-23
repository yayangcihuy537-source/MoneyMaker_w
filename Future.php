<?php
error_reporting(E_ALL & ~E_DEPRECATED & ~E_USER_DEPRECATED);
ini_set('display_errors', '0');

/**
 * CryptoFuture Auto Claim — Endless Loop
 * - Turnstile solver via waryono API
 * - Banner SOUU box style
 * - cf_clearance prompted only if CF challenge appears
 * - In-memory cookies, api key di config file
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

const TURNSTILE_SITEKEY = "0x4AAAAAACCJpcjk1yzJVey2";

const SOLVER_IN  = "https://api.waryono.my.id/in.php";
const SOLVER_OUT = "https://api.waryono.my.id/res.php";

const CONFIG_FILE = "cryptofuture_config.json";

const UA = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36";

const LOOP_SLEEP_STEP = 5;

/* ═══════════ RICH ANSI ═══════════ */
function fg($c){ return "\033[38;5;{$c}m"; }
function ansi_len($s){
    $plain = preg_replace('/\x1b\[[0-9;]*m/','',$s);
    $w = 0;
    $len = mb_strlen($plain, 'UTF-8');
    for ($i=0; $i<$len; $i++){
        $ch = mb_substr($plain,$i,1,'UTF-8');
        $cp = mb_ord($ch, 'UTF-8');
        if (($cp>=0x1F300 && $cp<=0x1F9FF) || ($cp>=0x2600 && $cp<=0x27BF) ||
            ($cp>=0x2B00 && $cp<=0x2BFF) || ($cp>=0x25A0 && $cp<=0x25FF) ||
            ($cp>=0x2580 && $cp<=0x259F)) {
            $w += 2;
        } else { $w += 1; }
    }
    return $w;
}
function ansi_pad($s,$len){ $p = $len - ansi_len($s); return $s . ($p>0 ? str_repeat(' ',$p) : ''); }
function gradient($text,$start=51,$end=196){
    $len = mb_strlen($text,'UTF-8');
    if ($len<=1) return fg($start).$text.RST;
    $out = '';
    for ($i=0; $i<$len; $i++){
        $t = $i/max(1,$len-1);
        $c = (int)round($start + ($end-$start)*$t);
        $out .= fg($c).mb_substr($text,$i,1,'UTF-8');
    }
    return $out.RST;
}
function box_line($c){ return fg(51)."║  ".RST.ansi_pad($c,60).fg(51)."║".RST."\n"; }
function box_div(){ return fg(51)."╠".str_repeat("═",62)."╣".RST."\n"; }

/* ═══════════ GLOBAL STATE ═══════════ */
$GLOBALS['_logs'] = [];
$GLOBALS['_stage'] = 'INIT';
$GLOBALS['_wallet'] = '?';
$GLOBALS['_balance'] = '?';
$GLOBALS['_claims'] = 0;
$GLOBALS['_fails'] = 0;
$GLOBALS['_earned'] = 0.0;
$GLOBALS['_ip'] = '?';
$GLOBALS['_isp'] = '?';
$GLOBALS['_country'] = '?';

function push_log($msg, $tag='i'){
    $icons = ['i'=>fg(51)."●".RST, 'ok'=>fg(46)."✔".RST, 'er'=>fg(196)."✖".RST,
              'wr'=>fg(208)."◈".RST, 'in'=>fg(213)."◉".RST, 'g'=>fg(226)."◆".RST];
    $ts = date('H:i:s');
    $line = fg(250)."[{$ts}]".RST." ".($icons[$tag]??'●')." ".$msg;
    $GLOBALS['_logs'][] = $line;
    if (count($GLOBALS['_logs'])>5) array_shift($GLOBALS['_logs']);
}

/* ═══════════ IP CHECK ═══════════ */
function check_ip(){
    if ($GLOBALS['_ip'] !== '?') return;
    $r = @file_get_contents("http://ip-api.com/json");
    if ($r === false) { $GLOBALS['_ip']='?'; return; }
    $j = json_decode($r, true);
    $GLOBALS['_ip']      = $j['query'] ?? '?';
    $GLOBALS['_country'] = ($j['country'] ?? '?').' / '.($j['city'] ?? '?');
    $GLOBALS['_isp']     = $j['isp'] ?? '?';
}

/* ═══════════ BANNER ═══════════ */
function banner(){
    check_ip();
    echo "\033[2J\033[H"; // clear + home

    echo fg(51)."╔".str_repeat("═",62)."╗".RST."\n";
    echo box_line(gradient("CRYPTOFUTURE AUTO CLAIM", 51, 213));
    echo box_line(fg(240)."─────── SOUU ENGINE ───────".RST);
    echo box_div();

    echo box_line(fg(213).BOLD."NETWORK".RST);
    echo box_line(fg(51)."├─ IP         : ".RST.fg(226).$GLOBALS['_ip'].RST);
    echo box_line(fg(51)."├─ Country    : ".RST.fg(226).$GLOBALS['_country'].RST);
    echo box_line(fg(51)."└─ ISP        : ".RST.fg(226).$GLOBALS['_isp'].RST);
    echo box_div();

    echo box_line(fg(213).BOLD."SESSION".RST);
    echo box_line(fg(51)."├─ Stage      : ".RST.fg(208).$GLOBALS['_stage'].RST);
    echo box_line(fg(51)."├─ Wallet     : ".RST.fg(226).$GLOBALS['_wallet'].RST);
    echo box_line(fg(51)."├─ Balance    : ".RST.fg(46).$GLOBALS['_balance'].RST);
    echo box_line(fg(51)."├─ Claims     : ".RST.fg(226).$GLOBALS['_claims'].RST);
    echo box_line(fg(51)."├─ Failed     : ".RST.fg(196).$GLOBALS['_fails'].RST);
    echo box_line(fg(51)."└─ Earned     : ".RST.fg(46).number_format($GLOBALS['_earned'], 4).RST);
    echo box_div();

    echo box_line(fg(213).BOLD."LIVE LOG".RST);
    $logs = $GLOBALS['_logs'];
    for ($i=0; $i<5; $i++){
        if (isset($logs[$i])) echo box_line(fg(252).$logs[$i].RST);
        else echo fg(51)."║".str_repeat(" ",62)."║".RST."\n";
    }

    echo fg(51)."╚".str_repeat("═",62)."╝".RST."\n";
    echo "\n   ".gradient("BOT RUNNING", 46, 226)." ".fg(250)."• ".date('H:i:s').RST."\n";
    echo "   ".fg(240)."By Power ".RST.fg(213)."@SouuXso".RST.fg(240)." • ".RST.fg(46)."CryptoFuture Edition".RST."\n\n";
}

/* ═══════════ CONFIG ═══════════ */
function load_config(){
    if (!file_exists(CONFIG_FILE)) return [];
    $j = json_decode(file_get_contents(CONFIG_FILE), true);
    return is_array($j) ? $j : [];
}
function save_config($cfg){
    file_put_contents(CONFIG_FILE, json_encode($cfg, JSON_PRETTY_PRINT));
}

/* ═══════════ IN-MEMORY COOKIE JAR ═══════════ */
$GLOBALS['COOKIES'] = [];
function cookie_str(){
    if (!$GLOBALS['COOKIES']) return '';
    $p = [];
    foreach ($GLOBALS['COOKIES'] as $k=>$v) $p[] = "$k=$v";
    return implode('; ', $p);
}
function cookie_absorb($headers){
    if (preg_match_all('/^set-cookie:\s*([^=]+)=([^;]+)/mi', $headers, $m, PREG_SET_ORDER)) {
        foreach ($m as $c) $GLOBALS['COOKIES'][trim($c[1])] = trim($c[2]);
    }
}
function cookie_seed($name, $value){
    if ($value !== '') $GLOBALS['COOKIES'][$name] = $value;
}

/* ═══════════ HTTP ═══════════ */
function req($url, $method='GET', $data=null, $headers=[], $binary=false){
    $ch = curl_init();
    $def = [
        "User-Agent: ".UA,
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language: id-ID,id;q=0.9,en;q=0.8",
        "Upgrade-Insecure-Requests: 1",
        "Referer: ".HOME,
        "sec-ch-ua: \"Chromium\";v=\"127\", \"Not)A;Brand\";v=\"99\"",
        "sec-ch-ua-mobile: ?1",
        "sec-ch-ua-platform: \"Android\"",
    ];
    if ($method === 'POST') $def[] = "Content-Type: application/x-www-form-urlencoded";
    $cs = cookie_str();
    if ($cs !== '') $def[] = "Cookie: ".$cs;

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
        return ['body'=>'', 'code'=>0, 'headers'=>'', 'error'=>$err];
    }
    $info = curl_getinfo($ch);
    if ($binary){
        return ['body'=>$resp, 'code'=>$info['http_code'], 'headers'=>'', 'error'=>''];
    }
    $hs = $info['header_size'];
    $raw = substr($resp, 0, $hs);
    $body = substr($resp, $hs);
    cookie_absorb($raw);
    return ['body'=>$body, 'code'=>$info['http_code'], 'headers'=>$raw, 'error'=>''];
}

/* ═══════════ CF DETECT ═══════════ */
function is_cf_challenge($html){
    return stripos($html, 'Just a moment') !== false
        || stripos($html, 'cf-challenge') !== false
        || stripos($html, 'Checking your browser') !== false
        || stripos($html, 'cf_chl_opt') !== false;
}

/* ═══════════ TURNSTILE SOLVER ═══════════ */
function solve_turnstile($apikey, $domain, $sitekey, $action='', $cdata=''){
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
            push_log("solver err: ".$j['request'], 'er');
            return null;
        }
        $id = $j['request'];
    } elseif (preg_match('/OK\|(\S+)/', $r['body'], $m)) {
        $id = $m[1];
    } else {
        push_log("solver in: ".substr($r['body'],0,60), 'er');
        return null;
    }

    push_log("job id $id, polling...", 'in');
    for ($i=0; $i<40; $i++) {
        sleep(2);
        $url = SOLVER_OUT."?apikey=".$apikey."&action=get&id=".$id."&json=1";
        $r2 = req($url, 'GET');
        $raw = trim($r2['body']);

        if (strpos($raw, "CAPCHA_NOT_READY") !== false) continue;
        if (strpos($raw, "ERROR_") !== false) {
            push_log("solver: ".substr($raw,0,60), 'er');
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

/* ═══════════ CF PROMPT ═══════════ */
function prompt_cf(){
    echo "\n".YEL."  ⚠ Cloudflare challenge detected.".RST."\n";
    echo "  Grab cf_clearance from browser DevTools → Application → Cookies → cryptofuture.co.in\n";
    echo WHT."  cf_clearance   : ".RST;
    $cf = trim(fgets(STDIN));
    cookie_seed('cf_clearance', $cf);
    return $cf !== '';
}

/* ═══════════ LOGIN ═══════════ */
function login($wallet, $apikey){
    push_log("login $wallet", 'in');
    $r = req(LOGIN);
    if ($r['code'] !== 200) return ['ok'=>false, 'msg'=>"GET login HTTP {$r['code']}", 'cf'=>false];
    $html = $r['body'];

    if (is_cf_challenge($html)) return ['ok'=>false, 'msg'=>'CF challenge', 'cf'=>true];

    $csrf = '';
    if (preg_match('/name="csrf_token_name"\s+value="([^"]+)"/i', $html, $m)) $csrf = $m[1];
    if ($csrf === '' && preg_match('/name="csrf_token_name"\s+id="[^"]*"\s+value="([^"]+)"/i', $html, $m)) $csrf = $m[1];
    if ($csrf === '') return ['ok'=>false, 'msg'=>'CSRF not found', 'cf'=>false];

    $ts_token = solve_turnstile($apikey, HOME, TURNSTILE_SITEKEY, '', '');
    if (!$ts_token) return ['ok'=>false, 'msg'=>'turnstile solve fail', 'cf'=>false];

    $device = "dev_".substr(md5(uniqid(mt_rand(), true)), 0, 12).base_convert(time(), 10, 36);
    $post = http_build_query([
        'wallet'                => $wallet,
        'csrf_token_name'       => $csrf,
        'device_token'          => $device,
        'cf-turnstile-response' => $ts_token,
    ]);

    $r2 = req(LOGIN, 'POST', $post, ['Origin: '.SITE, 'Referer: '.HOME]);
    if ($r2['code'] >= 500) return ['ok'=>false, 'msg'=>"login POST HTTP {$r2['code']}", 'cf'=>false];

    $r3 = req(DASH);
    if (stripos($r3['body'], 'auth/logout') !== false
        || stripos($r3['body'], 'Logout') !== false
        || stripos($r3['body'], 'Dashboard') !== false) {
        return ['ok'=>true, 'msg'=>'login ok', 'cf'=>false];
    }
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

function fetch_balance(){
    $r = req(EARN);
    return parse_earn($r['body'])['balance'];
}

function fmt_time($s){
    $s = (int)$s; if ($s<=0) return '0s';
    if ($s >= 3600) return floor($s/3600).'h'.floor(($s%3600)/60).'m';
    if ($s >= 60)   return floor($s/60).'m'.($s%60).'s';
    return $s.'s';
}

function wait_bar($seconds, $prefix="next"){
    $w = (int)$seconds;
    echo fg(51)."  ⏳ {$prefix} ".fmt_time($w)."".RST;
    while ($w > 0) {
        $c = min($w, LOOP_SLEEP_STEP);
        sleep($c);
        $w -= $c;
        echo fg(51).".".RST; flush();
    }
    echo "\n";
}

/* ═══════════ MAIN ═══════════ */
banner();

$cfg = load_config();
$apikey = $cfg['apikey'] ?? '';

if (!$apikey) {
    echo fg(213)."\n  INPUT REQUIRED\n".RST;
    echo fg(51)."  ┌─[ ".fg(226)."SOLVER APIKEY (waryono)".fg(51)." ]".RST."\n";
    echo fg(51)."  └──> ".RST;
    $apikey = trim(fgets(STDIN));
    if (!$apikey) { echo RED."apikey kosong\n"; exit(1); }
    $cfg['apikey'] = $apikey;
    save_config($cfg);
    echo fg(46)."  ✓ tersimpan\n".RST;
    sleep(1);
    banner();
}

echo fg(213)."\n  INPUT REQUIRED\n".RST;
echo fg(51)."  ┌─[ ".fg(226)."FAUCETPAY EMAIL".fg(51)." ]".RST."\n";
echo fg(51)."  └──> ".RST;
$wallet = trim(fgets(STDIN));
if (!$wallet) { echo RED."wallet kosong\n"; exit(1); }

$GLOBALS['_wallet'] = $wallet;

/* Init CF + login */
push_log("probing /faucet/earn...", 'in');
banner();

$r = req(EARN);
$html = $r['body'];

if (is_cf_challenge($html)) {
    if (!prompt_cf()) { echo RED."no cf_clearance, exit\n"; exit(1); }
    $r = req(EARN);
    $html = $r['body'];
    if (is_cf_challenge($html)) { echo RED."still CF, exit\n"; exit(1); }
}

if (strpos($html, 'id="fauform"') === false) {
    $lr = login($wallet, $apikey);
    if (!$lr['ok']) {
        if (!empty($lr['cf'])) {
            if (!prompt_cf()) { echo RED."exit\n"; exit(1); }
            $lr = login($wallet, $apikey);
        }
        if (!$lr['ok']) { push_log("login gagal: ".$lr['msg'], 'er'); banner(); exit(1); }
    }
    push_log("login ok", 'ok');
    banner();
}

$sessionStart = time();
$round = 0;

/* ═══════════ LOOP ═══════════ */
while (true) {
    $round++;
    $GLOBALS['_stage'] = "ROUND #{$round}";

    $r = req(EARN);
    $html = $r['body'];

    if (is_cf_challenge($html)) {
        push_log("CF challenge — butuh cf_clearance baru", 'wr');
        banner();
        if (!prompt_cf()) { push_log("abort", 'er'); banner(); break; }
        continue;
    }

    if (strpos($html, 'id="fauform"') === false
        && (stripos($html, 'auth/login') !== false || stripos($html, 'Sign in') !== false)) {
        push_log("session drop — re-login", 'wr');
        banner();
        $lr = login($wallet, $apikey);
        if (!$lr['ok']) {
            push_log("re-login gagal: ".$lr['msg']." — tunggu 60s", 'er');
            banner();
            sleep(60);
            continue;
        }
        push_log("re-login ok", 'ok');
        banner();
        continue;
    }

    $info = parse_earn($html);
    if ($info['balance'] !== null) $GLOBALS['_balance'] = number_format((float)$info['balance'], 4);

    if ($info['wait'] > 0) {
        push_log("cooldown ".fmt_time($info['wait'])." | bal: ".$GLOBALS['_balance'], 'wr');
        banner();
        wait_bar($info['wait'], "cooldown");
        continue;
    }

    if (!$info['has_form']) {
        push_log("no form & no wait — unknown", 'er');
        $GLOBALS['_fails']++;
        banner();
        sleep(15);
        continue;
    }

    // POST claim
    sleep(rand(2,4));
    $smart = base64_encode(json_encode([
        'ts' => (int)(microtime(true) * 1000),
        'cpu' => 8, 'mem' => 8, 'w' => 384, 'h' => 832,
        'touch' => 5, 'moves' => rand(0,3),
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
    $amount = 0.0;

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

    if (!$success && ($r2['code'] === 500 || stripos($respHtml, 'Database Error') !== false)) {
        push_log("HTTP 500 / DB err — re-check balance", 'wr');
        banner();
        sleep(2);
        $balAfter = fetch_balance();
        $delta = (float)$balAfter - (float)$info['balance'];
        if ($delta > 0) { $success = true; $amount = $delta; }
    }

    if ($success) {
        $GLOBALS['_claims']++;
        $GLOBALS['_earned'] += $amount;
        if ($amount > 0) {
            $GLOBALS['_balance'] = number_format((float)$info['balance'] + $amount, 4);
        }
        push_log("+".number_format($amount, 4)." | total: ".number_format($GLOBALS['_earned'],4)." | bal: ".$GLOBALS['_balance'], 'ok');
    } else {
        $GLOBALS['_fails']++;
        push_log("fail (HTTP ".$r2['code'].")", 'er');
    }
    banner();

    $cd = $success ? 65 : rand(20, 40);
    wait_bar($cd);
}

/* ═══════════ SUMMARY ═══════════ */
$uptime = time() - $sessionStart;
$GLOBALS['_stage'] = 'DONE';
push_log("done | claims=".$GLOBALS['_claims']." fails=".$GLOBALS['_fails']." earned=".number_format($GLOBALS['_earned'],4), 'g');
banner();
echo fg(250)."  ~ session flushed\n".RST;
exit(0);
