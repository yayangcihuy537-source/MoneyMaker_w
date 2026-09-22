<?php
error_reporting(0);
date_default_timezone_set('Asia/Jakarta');
$configFile = "config.json";
$tod        = "cookies.txt";

const script_name = "limefaucet.com";
const host        = "https://limefaucet.com";
const ref_code    = "F1teymLH6PtKQTy6";
const api_in      = "https://api.waryono.my.id/in.php";
const api_out     = "https://api.waryono.my.id/res.php";
const RUNTIME_MAX = 10800; // 3 jam

const reset  = "\033[0m";
const putih  = "\033[0;37m";
const hijau  = "\033[0;32m";
const kuning = "\033[0;33m";
const merah  = "\033[0;31m";
const cyan   = "\033[0;36m";
const biru   = "\033[0;34m";

$GLOBALS['stats'] = [
    'claims'     => 0,
    'rewards'    => 0.0,
    'start_time' => time(),
    'log'        => []
];
$GLOBALS['acc'] = [
    'uid'     => '?',
    'email'   => '?',
    'balance' => '0.000000'
];
$GLOBALS['hdr_b'] = [];

// ============================================================
//  RICH ANSI HELPERS
// ============================================================
function fg($code) { return "\033[38;5;{$code}m"; }
function bold($s) { return "\033[1m{$s}\033[22m"; }
function dim($s)  { return "\033[2m{$s}\033[22m"; }

function gradient($text, $start = 51, $end = 196) {
    $len = mb_strlen($text, 'UTF-8');
    if ($len <= 1) return fg($start) . $text . reset;
    $out = '';
    for ($i = 0; $i < $len; $i++) {
        $t = $i / ($len - 1);
        $c = (int)round($start + ($end - $start) * $t);
        $out .= fg($c) . mb_substr($text, $i, 1, 'UTF-8');
    }
    return $out . reset;
}

function tagColor($tag) {
    $map = [
        'AUTH'    => fg(46)  . bold('AUTH'),
        'STATUS'  => fg(51)  . bold('STATUS'),
        'CAPTCHA' => fg(213) . bold('CAPTCHA'),
        'CLAIM'   => fg(226) . bold('CLAIM'),
        'WAIT'    => fg(208) . bold('WAIT'),
        'BLOCK'   => fg(196) . bold('BLOCK'),
        'SYSTEM'  => fg(135) . bold('SYSTEM'),
    ];
    $k = trim($tag);
    return $map[$k] ?? fg(250) . bold($k);
}

function tagIcon($tag) {
    $map = [
        'AUTH'    => '●',
        'STATUS'  => '●',
        'CAPTCHA' => '◉',
        'CLAIM'   => '✔',
        'WAIT'    => '◷',
        'BLOCK'   => '✖',
        'SYSTEM'  => '⚙',
    ];
    $k = trim($tag);
    return $map[$k] ?? '•';
}

function ansiLen($s) {
    return mb_strlen(preg_replace('/\033\[[0-9;]*m/', '', $s), 'UTF-8');
}
function ansiPad($s, $len) {
    $pad = $len - ansiLen($s);
    return $s . ($pad > 0 ? str_repeat(' ', $pad) : '');
}

// ============================================================
//  HUMAN JITTER
// ============================================================
function humanDelay($min_ms = 150, $max_ms = 700) {
    usleep(rand($min_ms, $max_ms) * 1000);
}
function humanPause($min_ms = 400, $max_ms = 1200) {
    usleep(rand($min_ms, $max_ms) * 1000);
}

// ============================================================
//  LOGGER
// ============================================================
function addLog($tag, $msg) {
    $GLOBALS['stats']['log'][] = [
        'time' => date('H:i:s'),
        'tag'  => str_pad($tag, 8, ' '),
        'msg'  => $msg
    ];
    if (count($GLOBALS['stats']['log']) > 6) array_shift($GLOBALS['stats']['log']);
}

// ============================================================
//  BANNER
// ============================================================
function boxLine($content) {
    return fg(51) . "║  " . reset . ansiPad($content, 60) . fg(51) . "║" . reset . "\n";
}
function boxDivider() {
    return fg(51) . "╠══════════════════════════════════════════════════════════════╣" . reset . "\n";
}

function banner() {
    $s  = $GLOBALS['stats'];
    $a  = $GLOBALS['acc'];
    $rt = time() - $s['start_time'];
    $rts = sprintf('%02d:%02d:%02d', floor($rt/3600), floor(($rt%3600)/60), $rt%60);

    echo fg(51) . "╔══════════════════════════════════════════════════════════════╗" . reset . "\n";
    echo boxLine(gradient("LIMEFAUCET AUTO CLAIM", 51, 213));
    echo boxLine(dim("─────── SOUU ENGINE ───────"));
    echo boxDivider();

    echo boxLine(fg(213) . bold("CAPTCHA") . reset);
    echo boxLine(fg(51) . "├─ Type     : " . reset . fg(226) . "AC-CAPTCHA" . reset);
    echo boxLine(fg(51) . "└─ Status   : " . reset . fg(46) . "● ACTIVE" . reset);
    echo boxDivider();

    echo boxLine(fg(213) . bold("ACCOUNT") . reset);
    echo boxLine(fg(51) . "├─ ID         : " . reset . fg(226) . $a['uid'] . reset);
    echo boxLine(fg(51) . "├─ Email      : " . reset . fg(226) . $a['email'] . reset);
    echo boxLine(fg(51) . "└─ Balance    : " . reset . fg(46) . "$" . $a['balance'] . reset);
    echo boxDivider();

    echo boxLine(fg(213) . bold("SYSTEM") . reset);
    echo boxLine(fg(51) . "├─ Claims       : " . reset . fg(226) . $s['claims'] . reset);
    echo boxLine(fg(51) . "├─ Rewards      : " . reset . fg(46) . "$" . number_format($s['rewards'], 6) . reset);
    echo boxLine(fg(51) . "└─ Runtime      : " . reset . fg(208) . $rts . " / 03:00:00" . reset);
    echo boxDivider();

    for ($i = 0; $i < 6; $i++) {
        if (isset($s['log'][$i])) {
            $l    = $s['log'][$i];
            $icon = tagIcon($l['tag']);
            $tag  = tagColor($l['tag']);
            $line = dim("[" . $l['time'] . "]") . " " . fg(250) . $icon . reset . " " . $tag . " " . fg(252) . $l['msg'] . reset;
            echo boxLine($line);
        } else {
            echo fg(51) . "║" . str_repeat(' ', 62) . "║" . reset . "\n";
        }
    }

    echo fg(51) . "╚══════════════════════════════════════════════════════════════╝" . reset . "\n";
    echo "\n   " . gradient("BOT RUNNING", 46, 226) . " " . fg(250) . "• " . date('H:i:s') . reset . "\n";
    echo "   " . dim("By Power ") . fg(213) . "@SouuXso" . reset . dim(" • ") . fg(46) . "Lime Limes Edition" . reset . "\n\n";
}

// ============================================================
//  CORE
// ============================================================
function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function skibidixxx($url, $method = 'GET', $data = [], $headers = []) {
    $ch = curl_init();
    $final_headers = [];
    foreach ($headers as $h) $final_headers[] = $h;

    $options = [
        CURLOPT_URL            => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER         => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_SSL_VERIFYHOST => 1,
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_HTTPHEADER     => $final_headers,
        CURLOPT_CONNECTTIMEOUT => 999,
        CURLOPT_TIMEOUT        => 999,
        CURLOPT_COOKIEFILE     => 'cookies.txt',
        CURLOPT_COOKIEJAR      => 'cookies.txt'
    ];
    if (strtoupper($method) === 'POST') {
        $options[CURLOPT_POST] = true;
        $options[CURLOPT_POSTFIELDS] = $data;
    }
    curl_setopt_array($ch, $options);
    $response = curl_exec($ch);
    if ($response) {
        $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
        $body = substr($response, $header_size);
        curl_close($ch);
        return $body;
    } else {
        curl_close($ch);
        return "ERROR_SIGNAL";
    }
}

function timer($seconds, $prefix = "[!] please wait") {
    $wait_time = (int)$seconds;
    if ($wait_time <= 0) $wait_time = 1;
    $frames = ['⣾','⣽','⣻','⢿','⡿','⣟','⣯','⣷'];
    $fc = count($frames);
    $cf = 0;
    while ($wait_time > 0) {
        $start_time = microtime(true);
        while ((microtime(true) - $start_time) < 1) {
            $h = floor($wait_time / 3600);
            $m = floor(($wait_time % 3600) / 60);
            $s = $wait_time % 60;
            $tf = sprintf('%02d:%02d:%02d', $h, $m, $s);
            $sp = $frames[$cf];
            echo fg(250) . $prefix . fg(46) . " $tf " . fg(226) . $sp . "\r";
            usleep(100000);
            $cf = ($cf + 1) % $fc;
            if ((microtime(true) - $start_time) >= 1) break;
        }
        $wait_time--;
    }
    echo "\r                                        \r";
}

function lime($apikey, $gambar) {
    $headers = ["Content-Type: application/json"];
    $body = json_encode([
        "apikey"  => $apikey,
        "methods" => "moonptc",
        "base64"  => $gambar,
        "json"    => 1
    ]);
    $request = skibidixxx(api_in, "POST", $body, $headers);

    $json = json_decode($request, true);
    if (!is_array($json)) {
        $snippet = substr(strip_tags($request), 0, 80);
        return "FATAL:BAD_RESPONSE_NOT_JSON (" . trim($snippet) . ")";
    }

    if (($json['status'] ?? 1) === 0 && isset($json['request'])) {
        $r = $json['request'];
        if (strpos($r, "CAPCHA_NOT_READY") !== false) return "ERROR_SOLVE_PENDING";
        if (strpos($r, "ERROR_") !== false)           return $r;
    }

    if (strpos($request, "ERROR_WRONG_METHOD") !== false)                return "FATAL:ERROR_WRONG_METHOD";
    if (strpos($request, "ERROR_KEY_DOES_NOT_EXIST") !== false)          return "FATAL:ERROR_KEY_DOES_NOT_EXIST";
    if (strpos($request, "ERROR_METHOD_NOT_SPECIFIED") !== false)        return "FATAL:ERROR_METHOD_NOT_SPECIFIED";
    if (strpos($request, "ERROR_NO_SUCH_METHOD") !== false)              return "FATAL:ERROR_NO_SUCH_METHOD";
    if (strpos($request, "ERROR_DATABASE_CONNECTION_FAILED") !== false)  return "FATAL:ERROR_DATABASE_CONNECTION_FAILED";
    if (strpos($request, "ERROR_TOO_MANY_REQUESTS") !== false)           return "ERROR_TOO_MANY_REQUESTS";
    if (strpos($request, "ERROR_WRONG_USER_KEY") !== false)              return "FATAL:ERROR_WRONG_USER_KEY";
    if (strpos($request, "ERROR_ZERO_BALANCE") !== false)                return "FATAL:ERROR_ZERO_BALANCE";
    if (strpos($request, "ERROR_BAD_PARAMETERS") !== false)              return "FATAL:ERROR_BAD_PARAMETERS";
    if (strpos($request, "ERROR_EMPTY_IMAGE") !== false)                 return "FATAL:ERROR_EMPTY_IMAGE";
    if (strpos($request, "ERROR_UNKNOWN") !== false)                     return "FATAL:ERROR_UNKNOWN";

    if (!isset($json["request"])) {
        return "FATAL:NO_REQUEST_FIELD (" . substr($request, 0, 80) . ")";
    }

    $id = $json["request"];

    reload:
    timer(2, "  captcha..");
    $url = api_out . "?apikey=".$apikey."&action=get&id=".$id."&json=1";
    $result = skibidixxx($url, "GET", []);

    $jout = json_decode($result, true);
    if (!is_array($jout)) {
        return "FATAL:BAD_RESPONSE_NOT_JSON (" . substr(strip_tags($result), 0, 80) . ")";
    }

    $r = $jout['request'] ?? '';

    if (strpos($r, "CAPCHA_NOT_READY") !== false)          { sleep(2); goto reload; }
    if (strpos($r, "ERROR_BAD_PARAMETERS") !== false)      return "FATAL:ERROR_BAD_PARAMETERS";
    if (strpos($r, "Database connection failed") !== false) return "FATAL:DB_FAIL";
    if (strpos($r, "WRONG_CAPTCHA_ID") !== false)          return "WRONG_CAPTCHA_ID";
    if (strpos($r, "ERROR_SOLVE_PENDING") !== false)       return "ERROR_SOLVE_PENDING";
    if (strpos($r, "ERROR_CAPTCHA_UNSOLVABLE") !== false)  return "ERROR_CAPTCHA_UNSOLVABLE";
    if (strpos($r, "ERROR_BAD_REQUEST") !== false)         return "FATAL:ERROR_BAD_REQUEST";
    if (strpos($r, "INTENAL_SERVER_ERROR") !== false)      return "INTENAL_SERVER_ERROR";
    if (strpos($r, "ERROR_") !== false)                    return $r;

    $arr = explode(':', $r);
    $clean_res = trim(end($arr));
    if (!is_numeric($clean_res)) {
        return "FATAL:BAD_ANSWER ($r)";
    }
    return ["captcha" => (int)$clean_res];
}

function getConfig($configFile) {
    if (!file_exists($configFile)) return null;
    $c = json_decode(file_get_contents($configFile), true);
    if (!isset($c['apikey']) || !isset($c['email'])) return null;
    return $c;
}

function saveConfig($configFile, $data) {
    file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
}

function suki(&$a, &$b, &$c) {
    $ua = "Mozilla/5.0 (Linux; Android 16; 23076RN4BI Build/BP4A.251205.006) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.88 Mobile Safari/537.36";
    $a = [
        "host: limefaucet.com",
        "user-agent: $ua",
        "content-type: application/json",
        "origin: https://limefaucet.com",
        "accept: */*",
        "x-requested-with: Banna.com",
        "referer: https://limefaucet.com/faucet"
    ];
    $b = [
        "host: limefaucet.com",
        "user-agent: $ua",
        "accept: */*",
        "x-requested-with: Banna.com",
        "referer: https://limefaucet.com/dashboard"
    ];
    $c = $a;
}

function refreshAccount() {
    $b = $GLOBALS['hdr_b'];
    humanDelay(120, 350);
    $r = skibidixxx(host."/api/auth/me", "GET", [], $b);
    if (strpos($r, "email") !== false) {
        $q = json_decode($r, true);
        $GLOBALS['acc']['uid']     = $q["user"]["id"]    ?? ($q["id"]    ?? '?');
        $GLOBALS['acc']['email']   = $q["user"]["email"] ?? ($q["email"] ?? '?');
        $GLOBALS['acc']['balance'] = number_format((float)($q["user"]["balance_usd"] ?? ($q["balance_usd"] ?? 0)), 6, '.', '');
        return $q;
    }
    return null;
}

// ============================================================
//  MENU
// ============================================================
function menu() {
    $cfg = getConfig("config.json");
    $ak  = $cfg['apikey'] ?? null;
    $em  = $cfg['email']  ?? null;
    $akDisp = $ak ? substr($ak, 0, 20) . (strlen($ak) > 20 ? '...' : '') : 'belum diset';
    $emDisp = $em ? $em : 'belum diset';

    echo fg(51) . "╔══════════════════════════════════════════════════════════════╗" . reset . "\n";
    echo boxLine(gradient("LIMEFAUCET MENU", 51, 213));
    echo boxDivider();
    echo boxLine(fg(51) . "  API Key : " . reset . fg(226) . $akDisp . reset);
    echo boxLine(fg(51) . "  Email   : " . reset . fg(226) . $emDisp . reset);
    echo boxDivider();
    echo boxLine(fg(46)  . "  [1] " . reset . fg(252) . "Start Farming 3 Hours" . reset);
    echo boxLine(fg(213) . "  [2] " . reset . fg(252) . "Config Apikey" . reset);
    echo boxLine(fg(213) . "  [3] " . reset . fg(252) . "Config Email" . reset);
    echo boxLine(fg(196) . "  [0] " . reset . fg(252) . "Exit" . reset);
    echo fg(51) . "╚══════════════════════════════════════════════════════════════╝" . reset . "\n\n";
    echo fg(51) . "  Pilih >> " . reset;
}

// ============================================================
//  ACTIONS
// ============================================================
function actionConfigApikey($configFile) {
    $cfg = getConfig($configFile) ?? ['apikey' => '', 'email' => ''];
    echo "\n" . fg(213) . "  API Key baru : " . reset;
    $ak = trim(fgets(STDIN));
    if ($ak !== '') $cfg['apikey'] = $ak;
    saveConfig($configFile, $cfg);
    echo fg(46) . "  ✓ apikey disimpan\n" . reset;
    humanPause(500, 900);
}

function actionConfigEmail($configFile) {
    $cfg = getConfig($configFile) ?? ['apikey' => '', 'email' => ''];
    echo "\n" . fg(213) . "  Email baru : " . reset;
    $em = trim(fgets(STDIN));
    if ($em !== '') $cfg['email'] = $em;
    saveConfig($configFile, $cfg);
    echo fg(46) . "  ✓ email disimpan\n" . reset;
    humanPause(500, 900);
}

// ============================================================
//  FARM
// ============================================================
function actionFarm($configFile, $apikey, $email) {
    global $tod;

    $GLOBALS['stats'] = [
        'claims'     => 0,
        'rewards'    => 0.0,
        'start_time' => time(),
        'log'        => []
    ];

    clear();
    suki($a, $b, $c);
    $GLOBALS['hdr_b'] = $b;

    humanDelay(200, 500);
    $home = skibidixxx(host."/api/auth/me", "GET", [], $b);

    if (strpos($home, "email") !== false) {
        $q = json_decode($home, true);
        $GLOBALS['acc']['uid']     = $q["user"]["id"]    ?? ($q["id"]    ?? '?');
        $GLOBALS['acc']['email']   = $q["user"]["email"] ?? ($q["email"] ?? $email);
        $GLOBALS['acc']['balance'] = number_format((float)($q["user"]["balance_usd"] ?? ($q["balance_usd"] ?? 0)), 6, '.', '');

        addLog("AUTH", "Session OK");
        clear();
        banner();

        asu:
        if ((time() - $GLOBALS['stats']['start_time']) >= RUNTIME_MAX) {
            addLog("SYSTEM", "3 hour limit reached, exiting");
            clear();
            banner();
            echo fg(226) . "\n  ⏱  Farming selesai. Tekan Enter buat balik ke menu..." . reset;
            fgets(STDIN);
            return;
        }

        humanDelay(150, 400);
        $info = skibidixxx(host."/api/faucet/info", "GET", [], $b);
        $i = json_decode($info, true);

        $remaining = (int)($i['time_remaining_seconds'] ?? 0);
        if ($remaining > 0) {
            addLog("WAIT", "Next claim in " . gmdate("i:s", $remaining));
            clear();
            banner();
            timer($remaining, "  wait..");
            goto asu;
        }

        addLog("STATUS", "Faucet available");
        clear();
        banner();

        humanDelay(250, 600);
        $generate = skibidixxx(host."/api/faucet/ac-captcha/challenge", "POST", "{}", $a);
        $d = json_decode($generate, true);

        if (isset($d['session_id']) && isset($d['challenge']['image'])) {
            $sid    = $d['session_id'];
            $gambar = $d['challenge']['image'];

            addLog("CAPTCHA", "Challenge received");
            clear();
            banner();

            if (strpos($gambar, "data:image/gif;base64,") === false) {
                addLog("CAPTCHA", "Bad image, retry");
                humanPause(2000, 3500);
                goto asu;
            }

            humanPause(600, 1400);

            $anti = lime($apikey, $gambar);
            if (is_array($anti)) {
                $asw = (int)$anti["captcha"];

                humanPause(300, 900);

                $payload = json_encode(["session_id" => $sid, "candidate_index" => $asw]);
                $veri = skibidixxx(host."/api/faucet/ac-captcha/verify", "POST", $payload, $a);
                $v = json_decode($veri, true);

                if (($v['ok'] ?? false) === true && isset($v['token'])) {
                    addLog("CAPTCHA", "Verified (#$asw)");
                    clear();
                    banner();

                    humanPause(400, 1000);

                    $data  = json_encode(["captcha_token" => $v['token']]);
                    $claim = skibidixxx(host."/api/faucet/claim", "POST", $data, $a);
                    $cl    = json_decode($claim, true);

                    if (isset($cl['roll_number'])) {
                        $GLOBALS['stats']['claims']++;
                        $GLOBALS['stats']['rewards'] += (float)($cl['reward_usd'] ?? 0);
                        addLog("CLAIM", "Roll #" . $cl['roll_number'] . " -> $" . $cl['reward_usd']);
                        refreshAccount();
                        clear();
                        banner();
                        timer(180, "  next claim");
                        goto asu;
                    } else {
                        addLog("CLAIM", "No roll in response");
                        humanPause(2000, 4000);
                        goto asu;
                    }

                } elseif (($v['error'] ?? '') === 'too_fast') {
                    $retry_ms = $v['retry_after_ms'] ?? 250;
                    sleep(ceil($retry_ms / 1000));
                    goto asu;
                } elseif (($v['error'] ?? '') === 'wrong') {
                    addLog("CAPTCHA", "Wrong, new challenge");
                    humanPause(1500, 3000);
                    goto asu;
                } elseif (($v['error'] ?? '') === 'blocked' || isset($v['locked_until'])) {
                    $until = (float)($v['locked_until'] ?? 0);
                    $secs = ceil(($until - round(microtime(true) * 1000)) / 1000);
                    if ($secs < 1) $secs = 60;
                    addLog("BLOCK", "Locked " . $secs . "s");
                    clear();
                    banner();
                    timer(min($secs, 900), "  blocked wait..");
                    goto asu;
                } else {
                    humanPause(3000, 5000);
                    goto asu;
                }

            } elseif (is_string($anti)) {
                if (strpos($anti, "FATAL:") === 0) {
                    addLog("SYSTEM", "Fatal: " . substr($anti, 6));
                    clear();
                    banner();
                    echo fg(196) . "\n  ✖ Fatal error. Cek apikey lo. Tekan Enter..." . reset;
                    fgets(STDIN);
                    return;
                }
                humanPause(2000, 4000);
                goto asu;
            } else {
                humanPause(2000, 4000);
                goto asu;
            }

        } elseif (isset($d['error']) && $d['error'] === 'blocked') {
            addLog("BLOCK", "Faucet blocked");
            timer(60, "  blocked wait..");
            goto asu;
        } elseif (isset($d['locked_until'])) {
            $until = (float)$d['locked_until'];
            $secs = ceil(($until - round(microtime(true) * 1000)) / 1000);
            if ($secs < 1) $secs = 60;
            addLog("BLOCK", "Locked " . $secs . "s");
            timer(min($secs, 900), "  locked wait..");
            goto asu;
        } else {
            humanPause(2000, 4000);
            goto asu;
        }

    } else {
        @unlink($tod);
        addLog("AUTH", "Login required");
        clear();
        banner();

        humanDelay(300, 700);
        $data = json_encode(["email" => $email, "referral_code" => ref_code]);
        $p = skibidixxx(host."/api/auth/login", "POST", $data, $a);

        if (strpos($p, "email") !== false) {
            $j = json_decode($p, true);
            $uid = $j["user"]["id"] ?? '?';
            addLog("AUTH", "Login OK ($uid)");
            humanPause(1500, 2500);

            // refresh ke /me untuk isi acc
            $me = skibidixxx(host."/api/auth/me", "GET", [], $b);
            if (strpos($me, "email") !== false) {
                $q = json_decode($me, true);
                $GLOBALS['acc']['uid']     = $q["user"]["id"]    ?? ($q["id"]    ?? $uid);
                $GLOBALS['acc']['email']   = $q["user"]["email"] ?? ($q["email"] ?? $email);
                $GLOBALS['acc']['balance'] = number_format((float)($q["user"]["balance_usd"] ?? ($q["balance_usd"] ?? 0)), 6, '.', '');
            }

            clear();
            banner();
            goto asu;

        } else {
            addLog("AUTH", "Login FAILED");
            clear();
            banner();
            @unlink($tod);
            echo fg(196) . "\n  ✖ Login gagal. Cek email. Tekan Enter..." . reset;
            fgets(STDIN);
            return;
        }
    }
}

// ============================================================
//  MAIN LOOP
// ============================================================
$first = true;
while (true) {
    clear();
    if ($first) {
        echo "\n";
        $first = false;
    }
    menu();
    $opt = trim(fgets(STDIN));

    switch ($opt) {
        case '1':
            $cfg = getConfig($configFile);
            if (!$cfg || empty($cfg['apikey']) || empty($cfg['email'])) {
                clear();
                echo fg(196) . "\n  ✖ Config belum lengkap. Set apikey & email dulu (menu 2 & 3).\n" . reset;
                echo fg(250) . "  Tekan Enter..." . reset;
                fgets(STDIN);
                break;
            }
            actionFarm($configFile, $cfg['apikey'], $cfg['email']);
            break;

        case '2':
            actionConfigApikey($configFile);
            break;

        case '3':
            actionConfigEmail($configFile);
            break;

        case '0':
            clear();
            echo fg(213) . "\n  bye boss 👋\n\n" . reset;
            exit;

        default:
            echo fg(196) . "\n  ✖ Pilihan gak valid.\n" . reset;
            humanPause(600, 1000);
            break;
    }
}
