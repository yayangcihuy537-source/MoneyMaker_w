#!/usr/bin/env php
<?php
/**
 * ═══════════════════════════════════════════════════════════════
 *  THEMAGICDOLLAR.xyz Auto Claim Bot v1.5 (USDT FIX)
 *  - FIX: coin = USDT (bukan LTC)
 *  - FIX: header lengkap (Origin, Referer, Accept, dll)
 *  - FIX: CURLOPT_ENCODING untuk handle Brotli/gzip
 *  - FIX: parse reward amount & currency dari flash ok
 *  - FIX: login pakai host, bukan refflink
 *  - DEBUG: sitekey + CSRF tampil di panel
 * ═══════════════════════════════════════════════════════════════
 */

error_reporting(E_ALL);
ini_set('display_errors', '1');

if (PHP_VERSION_ID < 80000) { fwrite(STDERR, "PHP 8.0+ required\n"); exit(1); }

// ═══════════════════════════════════════════════════════════════
//  COLORS
// ═══════════════════════════════════════════════════════════════
const RST="\033[0m", BOLD="\033[1m", DIM="\033[2m";
const RED="\033[38;5;196m", GRN="\033[38;5;46m", YEL="\033[38;5;226m";
const CYN="\033[38;5;51m",  MAG="\033[38;5;201m", ORG="\033[38;5;208m";
const WHT="\033[38;5;15m",  GRY="\033[38;5;240m", VIO="\033[38;5;141m";

function vlen(string $s): int { return mb_strlen(preg_replace('/\033\[[0-9;]*m/','',$s)); }
function pad_to(string $s, int $w): string { return $s . str_repeat(' ', max(0, $w - vlen($s))); }

// ═══════════════════════════════════════════════════════════════
//  DEBUG LOGGER (NULL-SAFE)
// ═══════════════════════════════════════════════════════════════
const DEBUG_FILE_NAME = 'magic_debug.txt';
$DEBUG_FP = null;
$DEBUG_PATH = '';

function debug_open(): void {
    global $DEBUG_FP, $DEBUG_PATH;
    $candidates = [
        __DIR__ . '/' . DEBUG_FILE_NAME,
        getcwd() . '/' . DEBUG_FILE_NAME,
        '/sdcard/scupdate/' . DEBUG_FILE_NAME,
        '/sdcard/' . DEBUG_FILE_NAME,
        sys_get_temp_dir() . '/' . DEBUG_FILE_NAME,
    ];
    foreach ($candidates as $path) {
        $fp = @fopen($path, 'w');
        if ($fp !== false) {
            $DEBUG_FP = $fp;
            $DEBUG_PATH = $path;
            fwrite($DEBUG_FP, str_repeat('=', 70)."\n");
            fwrite($DEBUG_FP, "TheMagicDollar Bot v1.5 Debug Log\n");
            fwrite($DEBUG_FP, "Started: ".date('Y-m-d H:i:s')."\n");
            fwrite($DEBUG_FP, "PHP: ".PHP_VERSION."\n");
            fwrite($DEBUG_FP, "Path: {$path}\n");
            fwrite($DEBUG_FP, str_repeat('=', 70)."\n\n");
            fflush($DEBUG_FP);
            return;
        }
    }
    fwrite(STDERR, "warn: debug file gak bisa ditulis, lanjut tanpa debug log\n");
}

function debug_close(): void {
    global $DEBUG_FP;
    if ($DEBUG_FP !== null && is_resource($DEBUG_FP)) {
        @fwrite($DEBUG_FP, "\n".str_repeat('=', 70)."\n");
        @fwrite($DEBUG_FP, "Closed: ".date('Y-m-d H:i:s')."\n");
        @fclose($DEBUG_FP);
    }
    $DEBUG_FP = null;
}

function debug_log(string $tag, string $msg): void {
    global $DEBUG_FP;
    if ($DEBUG_FP === null || !is_resource($DEBUG_FP)) return;
    $ts = date('H:i:s');
    @fwrite($DEBUG_FP, "[{$ts}] [{$tag}] {$msg}\n");
    @fflush($DEBUG_FP);
}

function debug_dump(string $label, $data): void {
    global $DEBUG_FP;
    if ($DEBUG_FP === null || !is_resource($DEBUG_FP)) return;
    @fwrite($DEBUG_FP, "--- {$label} ---\n");
    if (is_array($data) || is_object($data)) {
        @fwrite($DEBUG_FP, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)."\n");
    } else {
        @fwrite($DEBUG_FP, (string)$data."\n");
    }
    @fwrite($DEBUG_FP, "\n");
    @fflush($DEBUG_FP);
}

function debug_marker(string $title = ''): void {
    global $DEBUG_FP;
    if ($DEBUG_FP === null || !is_resource($DEBUG_FP)) return;
    @fwrite($DEBUG_FP, "\n".str_repeat('-', 70)."\n");
    @fwrite($DEBUG_FP, "MARKER ".($title ? "[{$title}] " : "")."@ ".date('Y-m-d H:i:s')."\n");
    @fwrite($DEBUG_FP, str_repeat('-', 70)."\n");
    @fflush($DEBUG_FP);
}

function debug_request(string $method, string $url, $headers = null, $body = null): void {
    debug_log('REQ', "{$method} {$url}");
    if ($headers) debug_dump('REQ-HEADERS', $headers);
    if ($body !== null) debug_dump('REQ-BODY', $body);
}

function debug_response(string $method, string $url, int $status, string $headers, string $body): void {
    global $DEBUG_FP;
    if ($DEBUG_FP === null || !is_resource($DEBUG_FP)) return;
    debug_log('RESP', "{$method} {$url} → HTTP {$status}");
    if ($headers) debug_dump('RESP-HEADERS', trim($headers));
    if ($body !== '') {
        if (strlen($body) > 4000) {
            debug_dump('RESP-BODY (truncated)', substr($body, 0, 4000)."\n... (".strlen($body)." total bytes)");
        } else {
            debug_dump('RESP-BODY', $body);
        }
    }
    @fwrite($DEBUG_FP, "\n");
    @fflush($DEBUG_FP);
}

// ═══════════════════════════════════════════════════════════════
//  STATE
// ═══════════════════════════════════════════════════════════════
$STATE = [
    'email'         => '-',
    'claims'        => 0,
    'rewards'       => 0.0,
    'currency'      => 'USDT',
    'failures'      => 0,
    'max_failures'  => 5,
    'solve_attempt' => 0,
    'max_solve'     => 3,
    'runtime_start' => time(),
    'max_runtime'   => 3 * 3600,
    'logs'          => [],
    'faucet_status' => 'checking',
    'last_reward'   => '-',
    'sitekey'       => '-',
    'csrf_token'    => '-',
];

function slog(string $msg, string $level = 'INFO'): void {
    global $STATE;
    $ts = date('H:i:s');
    $tags = [
        'OK'=>GRN."● OK    ".RST, 'ERR'=>RED."● ERR   ".RST, 'WARN'=>YEL."● WARN  ".RST,
        'INFO'=>GRY."● INFO  ".RST, 'CLAIM'=>MAG."◉ CLAIM ".RST, 'SOLVE'=>CYN."◉ SOLVER".RST,
        'VERIFY'=>VIO."◉ VERIFY".RST, 'CAP'=>YEL."◉ CAPTCHA".RST, 'WAIT'=>ORG."◉ WAIT  ".RST,
        'AUTH'=>GRN."● AUTH  ".RST, 'LOGIN'=>CYN."◉ LOGIN ".RST, 'DEBUG'=>GRY."● DEBUG ".RST,
    ];
    $tag = $tags[strtoupper($level)] ?? $tags['INFO'];
    $STATE['logs'][] = GRY."[{$ts}] ".RST.$tag." ".WHT.$msg.RST;
    if (count($STATE['logs'])>7) array_shift($STATE['logs']);
    debug_log(strtoupper($level), $msg);
}

function fmt_dur(int $s): string {
    return sprintf('%02d:%02d:%02d', floor($s/3600), floor(($s%3600)/60), $s%60);
}

// ═══════════════════════════════════════════════════════════════
//  RENDER
// ═══════════════════════════════════════════════════════════════
function render(): void {
    global $STATE, $DEBUG_PATH;
    $W=62; $bd=CYN;
    $line=fn(string $c)=>$bd."║".RST.pad_to(" ".$c,$W).$bd."║".RST;
    $top=$bd."╔".str_repeat('═',$W)."╗".RST;
    $mid=$bd."╠".str_repeat('═',$W)."╣".RST;
    $bot=$bd."╚".str_repeat('═',$W)."╝".RST;

    echo "\n".$top."\n";
    echo $line(BOLD.WHT."THEMAGICDOLLAR AUTO CLAIM".RST)."\n";
    echo $line(DIM."─────── SOUU ENGINE v1.5 ───────".RST)."\n";
    echo $mid."\n";

    $hs_color=GRN; $hs_label='ONLINE';
    if ($STATE['faucet_status']==='suspect')      { $hs_color=YEL; $hs_label='SUSPECT'; }
    elseif ($STATE['faucet_status']==='dead')     { $hs_color=RED; $hs_label='DEAD'; }
    elseif ($STATE['faucet_status']==='checking') { $hs_color=GRY; $hs_label='CHECKING'; }

    echo $line(VIO."FAUCET".RST)."\n";
    echo $line("├─ Host     : ".CYN."themagicdollar.xyz".RST)."\n";
    echo $line("├─ Status   : ".$hs_color.$hs_label.RST)."\n";
    echo $line("└─ Currency : ".CYN.$STATE['currency'].RST)."\n";
    echo $mid."\n";

    echo $line(VIO."CAPTCHA".RST)."\n";
    echo $line("├─ Type     : ".YEL."TURNSTILE".RST)."\n";
    echo $line("├─ Solver   : ".CYN."waryono".RST)."\n";
    $sk = $STATE['sitekey'];
    $sk_disp = ($sk === '-' || $sk === '') ? DIM.'-'.RST : CYN.substr($sk, 0, 28).(strlen($sk)>28?'…':'').RST;
    echo $line("├─ Sitekey  : ".$sk_disp)."\n";
    echo $line("└─ Attempt  : ".($STATE['solve_attempt']>0
            ? YEL.$STATE['solve_attempt']."/".$STATE['max_solve'].RST
            : DIM."-".RST))."\n";
    echo $mid."\n";

    echo $line(VIO."ACCOUNT".RST)."\n";
    echo $line("├─ Email    : ".$STATE['email'])."\n";
    $cs = $STATE['csrf_token'];
    $cs_disp = ($cs === '-' || $cs === '') ? DIM.'-'.RST : GRY.substr($cs, 0, 20).(strlen($cs)>20?'…':'').RST;
    echo $line("├─ CSRF     : ".$cs_disp)."\n";
    echo $line("└─ Last     : ".YEL.$STATE['last_reward'].RST)."\n";
    echo $mid."\n";

    $run=time()-$STATE['runtime_start'];
    echo $line(VIO."SYSTEM".RST)."\n";
    echo $line("├─ Claims   : ".GRN.$STATE['claims'].RST)."\n";
    echo $line("├─ Rewards  : ".GRN.sprintf('+%.8f %s',$STATE['rewards'],$STATE['currency']).RST)."\n";
    echo $line("├─ Failures : ".RED.$STATE['failures'].RST." / ".$STATE['max_failures'])."\n";
    echo $line("└─ Runtime  : ".CYN.fmt_dur($run).RST." / ".DIM.fmt_dur($STATE['max_runtime']).RST)."\n";
    echo $mid."\n";

    $logs=$STATE['logs'];
    if (empty($logs)) {
        echo $line(DIM."─ no activity yet ─".RST)."\n";
    } else {
        foreach ($logs as $l) echo $line($l)."\n";
    }
    echo $bot."\n";
    echo "\n   ".GRN."BOT RUNNING".RST." ".DIM."•".RST." ".CYN.date('H:i:s').RST."\n";
    echo "   ".DIM."By Power @SouuXso • TheMagicDollar Edition".RST."\n";
    if ($DEBUG_PATH) {
        echo "   ".DIM."Debug → ".$DEBUG_PATH.RST."\n\n";
    } else {
        echo "   ".DIM."Debug → (disabled)".RST."\n\n";
    }
}

function clear_render(): void {
    if (PHP_OS_FAMILY==='Windows') pclose(popen('cls','w'));
    else system('clear');
    render();
}

// ═══════════════════════════════════════════════════════════════
//  CONST
// ═══════════════════════════════════════════════════════════════
const host     = "https://themagicdollar.xyz/";
const refflink = "https://themagicdollar.xyz/?r=267";
const WARYONO_API = "https://api.waryono.my.id/";

const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36';

$COOKIE_FILE = __DIR__.'/cookie.txt';
$CONFIG_FILE = __DIR__.'/magic_config.json';

// ═══════════════════════════════════════════════════════════════
//  CONFIG (email + apikey)
// ═══════════════════════════════════════════════════════════════
function load_config(): ?array {
    global $CONFIG_FILE;
    if (!file_exists($CONFIG_FILE)) return null;
    $c = json_decode((string) file_get_contents($CONFIG_FILE), true);
    if (!is_array($c)) return null;
    if (empty($c['email']) || empty($c['apikey'])) return null;
    return $c;
}

function save_config(array $c): void {
    global $CONFIG_FILE;
    @file_put_contents($CONFIG_FILE, json_encode($c, JSON_PRETTY_PRINT));
    @chmod($CONFIG_FILE, 0600);
}

function read_line(string $p = ""): string {
    if ($p) echo $p;
    $l = fgets(STDIN);
    if ($l === false) {
        echo "\n".RED."stdin closed (EOF) — keluar\n".RST;
        exit(0);
    }
    return trim($l);
}

function setup(): array {
    echo "\n".CYN."═══ THEMAGICDOLLAR SETUP ═══".RST."\n\n";
    echo DIM."Register: ".refflink."\n";
    echo DIM."Bot     : https://t.me/Skibidixxx_check_bot\n\n".RST;

    $email = '';
    while (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $email = read_line(YEL."Email: ".RST);
        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            echo RED."  ✗ Email gak valid\n".RST;
        }
    }
    $apikey = '';
    while ($apikey === '') {
        $apikey = read_line(YEL."Waryono API key: ".RST);
        if ($apikey === '') echo RED."  ✗ Kosong\n".RST;
    }
    return ['email' => $email, 'apikey' => $apikey];
}

// ═══════════════════════════════════════════════════════════════
//  SOLVER
// ═══════════════════════════════════════════════════════════════
class Solver {
    public $apikey;
    public $pageurl;
    public $sitekey;
    private $api_url = WARYONO_API;
    private $maxWait = 300;
    private $pollInterval = 5;

    function __construct($apikey) { $this->apikey = $apikey; }

    private function request($url, $post = null, $json = false) {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_ENCODING, '');
        if ($post !== null) {
            curl_setopt($ch, CURLOPT_POST, true);
            if ($json) {
                curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
                curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($post));
                debug_request('SOLVER-POST', $url, ['Content-Type: application/json'], $post);
            } else {
                curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($post));
                debug_request('SOLVER-POST', $url, null, $post);
            }
        } else {
            debug_request('SOLVER-GET', $url, null, null);
        }
        $response = curl_exec($ch);
        if (curl_errno($ch)) {
            slog("Curl: " . curl_error($ch), 'ERR');
            debug_log('SOLVER-ERR', curl_error($ch));
        }
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        debug_response('SOLVER', $url, $code, '', (string)$response);
        return $response;
    }

    private function in_api($data) {
        $data['apikey'] = $this->apikey;
        $res = $this->request($this->api_url . 'in.php', $data, true);
        $json = json_decode($res, true);
        if (is_array($json)) return $json;
        if (strpos((string)$res, 'OK|') === 0) {
            $id = explode('|', $res)[1] ?? '';
            return ['status' => 1, 'request' => $id];
        }
        return ['status' => 0, 'request' => $res];
    }

    private function res_api($id) {
        $url = $this->api_url . 'res.php?apikey=' . urlencode($this->apikey) . '&action=get&id=' . urlencode($id);
        $res = $this->request($url);
        $json = json_decode($res, true);
        if (is_array($json)) return $json;
        if (strpos((string)$res, 'OK|') === 0) {
            $token = explode('|', $res)[1] ?? '';
            return ['status' => 1, 'request' => $token];
        }
        if ($res === 'CAPCHA_NOT_READY') {
            return ['status' => 0, 'request' => 'CAPCHA_NOT_READY'];
        }
        return ['status' => 0, 'request' => $res];
    }

    private function finalResult($data) {
        debug_dump('SOLVER-INPUT', $data);
        $get_in = $this->in_api($data);
        debug_dump('SOLVER-IN-RESP', $get_in);
        if (!$get_in['status']) {
            slog("in_api error: " . ($get_in['request'] ?? 'unknown'), 'ERR');
            return null;
        }
        $id = $get_in['request'];
        slog("Solver task: {$id}", 'SOLVE');
        $startTime = time();
        while ((time() - $startTime) < $this->maxWait) {
            $get_res = $this->res_api($id);
            if (!is_array($get_res)) { slog("Invalid res_api", 'ERR'); return null; }
            $request = $get_res['request'] ?? '';
            if ($request === "CAPCHA_NOT_READY") {
                sleep($this->pollInterval);
                continue;
            }
            if (!empty($get_res['status'])) {
                slog("Solved (" . (time()-$startTime) . "s)", 'OK');
                debug_dump('SOLVER-TOKEN', substr($request, 0, 60).'… ('.strlen($request).' chars)');
                return $request;
            }
            slog("Solver: " . ($get_res['request'] ?? 'unknown'), 'ERR');
            return null;
        }
        slog("Solver timeout", 'ERR');
        return null;
    }

    public function turnstile() {
        if (empty($this->sitekey) || empty($this->pageurl)) {
            slog("sitekey/pageurl kosong", 'ERR');
            debug_log('SOLVER-ERR', "sitekey/pageurl empty");
            return null;
        }
        debug_log('SOLVER', "turnstile domain={$this->pageurl} sitekey={$this->sitekey}");
        return $this->finalResult([
            "methods" => "turnstile",
            "domain"  => $this->pageurl,
            "sitekey" => $this->sitekey,
        ]);
    }
}

// ═══════════════════════════════════════════════════════════════
//  HTTP HELPERS
// ═══════════════════════════════════════════════════════════════
function headers() {
    return [
        "Host: themagicdollar.xyz",
        "User-Agent: " . UA,
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language: en-US,en;q=0.9,id;q=0.8",
        "Origin: https://themagicdollar.xyz",
        "Referer: https://themagicdollar.xyz/",
        "Upgrade-Insecure-Requests: 1",
        "Sec-Fetch-Site: same-origin",
        "Sec-Fetch-Mode: navigate",
        "Sec-Fetch-User: ?1",
        "Sec-Fetch-Dest: document",
    ];
}

function curl_req($url, $headers = 0, $postData = 0) {
    global $COOKIE_FILE;
    $tries = 0;
    while ($tries < 5) {
        $tries++;
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 30);
        curl_setopt($ch, CURLOPT_TIMEOUT, 60);
        curl_setopt($ch, CURLOPT_ENCODING, '');
        curl_setopt($ch, CURLOPT_COOKIEFILE, $COOKIE_FILE);
        curl_setopt($ch, CURLOPT_COOKIEJAR,  $COOKIE_FILE);
        if ($postData) {
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
            if (is_array($headers)) {
                $headers[] = "Content-Type: application/x-www-form-urlencoded";
            } else {
                $headers = ["Content-Type: application/x-www-form-urlencoded"];
            }
        }
        if ($headers) curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_HEADER, true);

        $method = $postData ? 'POST' : 'GET';
        debug_request($method, $url, $headers, $postData ?: null);

        $r = curl_exec($ch);
        if (!$r) {
            $err = curl_error($ch);
            slog("Connection error, retry ({$tries}/5)...", 'WARN');
            debug_log('ERR', "curl_exec false: {$err}");
            sleep(2);
            continue;
        }
        $hdr_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $hd = substr($r, 0, $hdr_size);
        $bd = substr($r, $hdr_size);

        debug_response($method, $url, $code, $hd, $bd);

        if (!$bd) {
            slog("Empty body, retry ({$tries}/5)...", 'WARN');
            sleep(2);
            continue;
        }
        return [$hd, $bd];
    }
    debug_log('ERR', "curl_req gave up after 5 tries");
    return ['', ''];
}

function login(string $email): bool {
    global $STATE;
    $retry = 0;
    while ($retry < 6) {
        $r = curl_req(host, headers())[1];
        if (!preg_match('/name="csrf" value="([^"]+)"/', $r, $m)) {
            slog("Login: CSRF gak ketemu (try ".($retry+1)."/6)", 'WARN');
            debug_log('LOGIN-ERR', "CSRF not found, body_len=".strlen($r));
            $retry++;
            sleep(2);
            continue;
        }
        $csrf = $m[1];
        $STATE['csrf_token'] = $csrf;
        debug_log('LOGIN', "csrf={$csrf}");
        $data = "csrf={$csrf}&action=signin&address=" . urlencode($email);
        $r = curl_req(host, headers(), $data)[1];
        if (preg_match('/<span>Paying <b>([^<]+)<\/b><\/span>/', $r, $m2)) {
            $found = $m2[1];
            $STATE['email'] = $found;
            slog("Login OK: {$found}", 'AUTH');
            return true;
        }
        slog("Login: email gak ketemu (try ".($retry+1)."/6)", 'WARN');
        debug_log('LOGIN-ERR', "email not found in body, len=".strlen($r));
        $retry++;
        sleep(2);
    }
    return false;
}

function tmr(int $seconds) {
    $spinner = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'];
    $end = microtime(true) + $seconds;
    $i = 0;
    while (($remaining = $end - microtime(true)) > 0) {
        $remaining = (int)$remaining;
        $h = intdiv($remaining, 3600);
        $m = intdiv($remaining % 3600, 60);
        $s = $remaining % 60;
        printf("\r   " . ORG . "%s" . RST . " %02d:%02d:%02d", $spinner[$i % count($spinner)], $h, $m, $s);
        $i++;
        usleep(50000);
    }
    echo "\r                              \r";
}

// ═══════════════════════════════════════════════════════════════
//  MAIN
// ═══════════════════════════════════════════════════════════════
debug_open();

clear_render();

$config = load_config();
if ($config) {
    echo GRN."  ✓ Config found\n".RST;
    echo DIM."    Email  : {$config['email']}\n".RST;
    echo DIM."    APIKey : ".substr($config['apikey'], 0, 12)."...\n\n".RST;
    $ans = read_line(YEL."  Use saved? (y/n): ".RST);
    if (strtolower($ans) === 'n') $config = setup();
    else save_config($config);
} else {
    $config = setup();
    save_config($config);
}

debug_log('CONFIG', "email={$config['email']} apikey=".substr($config['apikey'], 0, 12)."…");

$solver = new Solver($config['apikey']);
$STATE['email'] = $config['email'];

clear_render();
slog("Bot starting...", 'INFO');
clear_render();

$maxretry = 5;
$retry    = 0;
$showemail = false;
$round     = 0;

while (true) {
    $round++;
    if ((time() - $STATE['runtime_start']) >= $STATE['max_runtime']) {
        slog("Max runtime reached", 'WARN'); break;
    }
    if ($retry >= $maxretry) {
        slog("Max retry reached", 'ERR'); break;
    }
    if ($STATE['failures'] >= $STATE['max_failures']) {
        slog("Max failures reached", 'ERR'); break;
    }

    debug_marker("ROUND #{$round}");

    $resp = curl_req(host, headers());
    $r = $resp[1] ?? '';
    if ($r === '') {
        slog("Empty home page, retry...", 'WARN');
        debug_log('ERR', "home page empty");
        clear_render(); sleep(3); continue;
    }

    preg_match('/data-wait="([^"]+)"/', $r, $mw);
    $tmr_wait = $mw[1] ?? 0;

    preg_match('/<span>Paying <b>([^<]+)<\/b><\/span>/', $r, $me);
    $email = $me[1] ?? '';

    if (!$email) {
        debug_log('EMAIL', "not found on page, attempting login");
        if (!login($config['email'])) {
            slog("Login failed 6x", 'ERR');
            clear_render();
            break;
        }
        clear_render();
        continue;
    }

    if (!$showemail) {
        $STATE['email'] = $email;
        slog("Email: {$email}", 'OK');
        $showemail = true;
        clear_render();
    }

    if (preg_match('/Next claim/i', $r) && is_numeric($tmr_wait) && $tmr_wait > 0) {
        slog("Cooldown {$tmr_wait}s", 'WAIT');
        debug_log('COOLDOWN', "{$tmr_wait}s");
        clear_render();
        tmr((int)$tmr_wait);
        clear_render();
        continue;
    }

    if (!preg_match('/name="csrf" value="([^"]+)"/', $r, $mc)) {
        slog("CSRF gak ketemu, retry...", 'WARN');
        debug_log('CSRF', "not found on main page, body_len=".strlen($r));
        clear_render(); sleep(3); continue;
    }
    $csrf = $mc[1];
    $STATE['csrf_token'] = $csrf;
    debug_log('CSRF-MAIN', $csrf);

    // Ambil coin dari halaman (biasanya USDT)
    preg_match('/name="coin" value="([^"]+)"/', $r, $mcoin);
    $coin = $mcoin[1] ?? 'USDT';
    debug_log('COIN', "using {$coin}");

    $data = "csrf={$csrf}&coin={$coin}";
    debug_log('CLAIM-STEP1', "posting to claim.php with coin={$coin}");
    $r = curl_req(host . 'claim.php', headers(), $data)[1];
    tmr(5);

    if (!preg_match('/name="csrf" value="([^"]+)"/', $r, $mc2)) {
        slog("CSRF (captcha) gak ketemu", 'WARN');
        debug_log('CSRF-CAPTCHA', "not found, body_len=".strlen($r));
        debug_dump('CLAIM-BODY-SNIPPET', substr($r, 0, 1500));
        clear_render(); sleep(3); continue;
    }
    $csrf = $mc2[1];
    $STATE['csrf_token'] = $csrf;
    debug_log('CSRF-CAPTCHA', $csrf);

    preg_match('/data-sitekey="([^"]+)"/', $r, $ms);
    $sitekey = $ms[1] ?? '';

    if (!$sitekey) {
        debug_log('SITEKEY', "primary pattern failed, trying alt");
        if (preg_match('/cf-turnstile[^>]*data-sitekey="([^"]+)"/i', $r, $ms2)) {
            $sitekey = $ms2[1];
            debug_log('SITEKEY-ALT', "found: {$sitekey}");
        } elseif (preg_match('/sitekey["\']?\s*[:=]\s*["\']([^"\']+)["\']/i', $r, $ms3)) {
            $sitekey = $ms3[1];
            debug_log('SITEKEY-ALT2', "found: {$sitekey}");
        }
    }

    if (!$sitekey) {
        slog("Captcha gak ketemu", 'ERR');
        debug_log('SITEKEY', "NOT FOUND — dumping captcha body");
        debug_dump('CAPTCHA-BODY', substr($r, 0, 3000));
        $retry++;
        clear_render(); sleep(3); continue;
    }

    $STATE['sitekey'] = $sitekey;
    debug_log('SITEKEY', $sitekey);
    slog("Sitekey: ".substr($sitekey, 0, 30)."…", 'CAP');
    clear_render();

    $solver->pageurl = host;
    $solver->sitekey = $sitekey;

    $cap = null;
    $STATE['solve_attempt'] = 0;
    while ($STATE['solve_attempt'] < $STATE['max_solve']) {
        $STATE['solve_attempt']++;
        slog("Solving ({$STATE['solve_attempt']}/{$STATE['max_solve']})...", 'SOLVE');
        clear_render();
        $cap = $solver->turnstile();
        clear_render();
        if ($cap) break;
        slog("Solve failed, retry...", 'WARN');
        clear_render();
        sleep(2);
    }

    if (!$cap) {
        slog("All solve failed", 'ERR');
        debug_log('SOLVE', "all attempts failed");
        $STATE['failures']++; $retry++;
        clear_render(); sleep(5); continue;
    }

    slog("Verifying captcha...", 'VERIFY');
    clear_render();

    $data = "csrf={$csrf}&cf-turnstile-response=" . $cap;
    debug_log('VERIFY', "posting captcha token, len=".strlen($cap));
    $r = curl_req(host . 'captcha.php?ts=1', headers(), $data)[1];

    if (preg_match('/<div class="flash ok">([^<]+)<\/div>/', $r, $mok)) {
        $msg = trim($mok[1]);
        $STATE['claims']++;
        $STATE['last_reward'] = $msg;
        $STATE['failures'] = 0;
        $retry = 0;

        // Parse reward amount & currency
        if (preg_match('/Sent ([\d.]+) (\w+) to your FaucetPay account/', $msg, $mr)) {
            $STATE['rewards'] += (float)$mr[1];
            $STATE['currency'] = $mr[2];
        }

        slog("Claimed: {$msg}", 'OK');
        debug_log('CLAIM-OK', $msg);
        clear_render();
    } else {
        $STATE['failures']++;
        $retry++;
        slog("Claim rejected", 'ERR');
        debug_log('CLAIM-FAIL', "no flash ok in response, body_len=".strlen($r));
        debug_dump('CLAIM-FAIL-SNIPPET', substr($r, 0, 1500));
        clear_render();
    }

    sleep(3);
}

clear_render();
echo "\n".CYN."  ◉ Bot stopped.\n".RST;
echo DIM."  Claims: {$STATE['claims']}  |  Failures: {$STATE['failures']}  |  Rewards: ".sprintf('%.8f',$STATE['rewards'])." {$STATE['currency']}\n\n".RST;
if ($DEBUG_PATH) echo DIM."  Debug log: ".$DEBUG_PATH."\n\n".RST;

debug_log('STOP', "claims={$STATE['claims']} failures={$STATE['failures']} rewards={$STATE['rewards']}");
debug_close();
