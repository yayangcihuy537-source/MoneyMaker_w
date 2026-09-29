#!/usr/bin/env php
<?php
/**
 * ═══════════════════════════════════════════════════════════════
 *  THEMAGICDOLLAR.xyz Auto Claim Bot v1.1
 *  - LimeFaucet-style Clean UI
 *  - Turnstile solver via Waryono API
 *  - Apikey di config file (magic_config.json)
 * ═══════════════════════════════════════════════════════════════
 */

error_reporting(0);
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
//  STATE
// ═══════════════════════════════════════════════════════════════
$STATE = [
    'email'         => '-',
    'claims'        => 0,
    'rewards'       => 0.0,
    'currency'      => 'LTC',
    'failures'      => 0,
    'max_failures'  => 5,
    'solve_attempt' => 0,
    'max_solve'     => 3,
    'runtime_start' => time(),
    'max_runtime'   => 3 * 3600,
    'logs'          => [],
    'faucet_status' => 'checking',
    'last_reward'   => '-',
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
}

function fmt_dur(int $s): string {
    return sprintf('%02d:%02d:%02d', floor($s/3600), floor(($s%3600)/60), $s%60);
}

// ═══════════════════════════════════════════════════════════════
//  RENDER
// ═══════════════════════════════════════════════════════════════
function render(): void {
    global $STATE;
    $W=62; $bd=CYN;
    $line=fn(string $c)=>$bd."║".RST.pad_to(" ".$c,$W).$bd."║".RST;
    $top=$bd."╔".str_repeat('═',$W)."╗".RST;
    $mid=$bd."╠".str_repeat('═',$W)."╣".RST;
    $bot=$bd."╚".str_repeat('═',$W)."╝".RST;

    echo "\n".$top."\n";
    echo $line(BOLD.WHT."THEMAGICDOLLAR AUTO CLAIM".RST)."\n";
    echo $line(DIM."─────── SOUU ENGINE ───────".RST)."\n";
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
    echo $line("└─ Attempt  : ".($STATE['solve_attempt']>0
            ? YEL.$STATE['solve_attempt']."/".$STATE['max_solve'].RST
            : DIM."-".RST))."\n";
    echo $mid."\n";

    echo $line(VIO."ACCOUNT".RST)."\n";
    echo $line("├─ Email    : ".$STATE['email'])."\n";
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
    echo "   ".DIM."By Power @SouuXso • TheMagicDollar Edition".RST."\n\n";
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
    return trim((string) fgets(STDIN));
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
        if ($post !== null) {
            curl_setopt($ch, CURLOPT_POST, true);
            if ($json) {
                curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
                curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($post));
            } else {
                curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($post));
            }
        }
        $response = curl_exec($ch);
        if (curl_errno($ch)) slog("Curl: " . curl_error($ch), 'ERR');
        curl_close($ch);
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
        $get_in = $this->in_api($data);
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
            return null;
        }
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
function curl_req($url, $headers = 0, $postData = 0) {
    global $COOKIE_FILE;
    while (true) {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 30);
        curl_setopt($ch, CURLOPT_COOKIEFILE, $COOKIE_FILE);
        curl_setopt($ch, CURLOPT_COOKIEJAR,  $COOKIE_FILE);
        if ($postData) {
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
        }
        if ($headers) curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_HEADER, true);
        $r = curl_exec($ch);
        if (!$r) {
            curl_close($ch);
            slog("Connection error, retry...", 'WARN');
            sleep(2);
            continue;
        }
        $hdr_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
        $hd = substr($r, 0, $hdr_size);
        $bd = substr($r, $hdr_size);
        curl_close($ch);
        if (!$bd) {
            slog("Empty body, retry...", 'WARN');
            sleep(2);
            continue;
        }
        return [$hd, $bd];
    }
}

function headers() {
    return [
        "Host: " . parse_url(host)['host'],
        "user-agent: " . UA,
    ];
}

function login(string $email): bool {
    global $STATE;
    $retry = 0;
    while ($retry < 6) {
        $r = curl_req(refflink, headers())[1];
        if (!preg_match('/name="csrf" value="([^"]+)"/', $r, $m)) { $retry++; continue; }
        $csrf = $m[1];
        $data = "csrf={$csrf}&action=signin&address=" . urlencode($email);
        $r = curl_req(refflink, headers(), $data)[1];
        if (preg_match('/<span>Paying <b>([^<]+)<\/b><\/span>/', $r, $m2)) {
            $found = $m2[1];
            $STATE['email'] = $found;
            slog("Login OK: {$found}", 'AUTH');
            return true;
        }
        $retry++;
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
clear_render();

$config = load_config();
if ($config) {
    echo GRN."  ✓ Config found\n".RST;
    echo DIM."    Email  : {$config['email']}\n".RST;
    echo DIM."    APIKey : ".substr($config['apikey'], 0, 12)."...\n\n".RST;
    $ans = read_line(YEL."  Use saved? (y/n): ".RST);
    if (strtolower($ans) === 'n') $config = setup();
    else save_config($config); // safety
} else {
    $config = setup();
    save_config($config);
}

$solver = new Solver($config['apikey']);
$STATE['email'] = $config['email'];

clear_render();
slog("Bot starting...", 'INFO');
clear_render();

$maxretry = 5;
$retry    = 0;
$showemail = false;

while (true) {
    if ((time() - $STATE['runtime_start']) >= $STATE['max_runtime']) {
        slog("Max runtime reached", 'WARN'); break;
    }
    if ($retry >= $maxretry) {
        slog("Max retry reached", 'ERR'); break;
    }
    if ($STATE['failures'] >= $STATE['max_failures']) {
        slog("Max failures reached", 'ERR'); break;
    }

    $r = curl_req(host, headers())[1];

    preg_match('/data-wait="([^"]+)"/', $r, $mw);
    $tmr_wait = $mw[1] ?? 0;

    preg_match('/<span>Paying <b>([^<]+)<\/b><\/span>/', $r, $me);
    $email = $me[1] ?? '';

    if (!$email) {
        if (!login($config['email'])) {
            slog("Login failed 5x", 'ERR');
            clear_render();
            exit(1);
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
        clear_render();
        tmr((int)$tmr_wait);
        clear_render();
        continue;
    }

    if (!preg_match('/name="csrf" value="([^"]+)"/', $r, $mc)) {
        slog("CSRF gak ketemu, retry...", 'WARN');
        clear_render(); sleep(3); continue;
    }
    $csrf = $mc[1];
    $data = "csrf={$csrf}&coin=LTC";
    $r = curl_req(host . 'claim.php', headers(), $data)[1];
    tmr(5);

    if (!preg_match('/name="csrf" value="([^"]+)"/', $r, $mc2)) {
        slog("CSRF (captcha) gak ketemu", 'WARN');
        clear_render(); sleep(3); continue;
    }
    $csrf = $mc2[1];

    preg_match('/data-sitekey="([^"]+)"/', $r, $ms);
    $sitekey = $ms[1] ?? '';

    if (!$sitekey) {
        slog("Captcha gak ketemu", 'ERR');
        $retry++; clear_render(); sleep(3); continue;
    }

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
        clear_render(); sleep(2);
    }

    if (!$cap) {
        slog("All solve failed", 'ERR');
        $STATE['failures']++; $retry++;
        clear_render(); sleep(5); continue;
    }

    slog("Verifying captcha...", 'VERIFY');
    clear_render();

    $data = "csrf={$csrf}&cf-turnstile-response=" . $cap;
    $r = curl_req(host . 'captcha.php?ts=1', headers(), $data)[1];

    if (preg_match('/<div class="flash ok">([^<]+)<\/div>/', $r, $mok)) {
        $msg = trim($mok[1]);
        $STATE['claims']++;
        $STATE['last_reward'] = $msg;
        $STATE['failures'] = 0;
        $retry = 0;
        slog("Claimed: {$msg}", 'OK');
        clear_render();
    } else {
        $STATE['failures']++;
        $retry++;
        slog("Claim rejected", 'ERR');
        clear_render();
    }

    sleep(3);
}

clear_render();
echo "\n".CYN."  ◉ Bot stopped.\n".RST;
echo DIM."  Claims: {$STATE['claims']}  |  Failures: {$STATE['failures']}  |  Rewards: ".sprintf('%.8f',$STATE['rewards'])." {$STATE['currency']}\n\n".RST;
