<?php // aruble.php
@system("clear");
error_reporting(0);
date_default_timezone_set('Asia/Jakarta');

// ============================================================
//  RICH ANSI HELPERS
// ============================================================
function fg($code) { return "\033[38;5;{$code}m"; }
function bold($s) { return "\033[1m{$s}\033[22m"; }
function dim($s)  { return "\033[2m{$s}\033[22m"; }

function gradient($text, $start = 51, $end = 196) {
    $len = mb_strlen($text, 'UTF-8');
    if ($len <= 1) return fg($start) . $text . "\033[0m";
    $out = '';
    for ($i = 0; $i < $len; $i++) {
        $t = $i / ($len - 1);
        $c = (int)round($start + ($end - $start) * $t);
        $out .= fg($c) . mb_substr($text, $i, 1, 'UTF-8');
    }
    return $out . "\033[0m";
}

function ansiLen($s) {
    $plain = preg_replace('/\033\[[0-9;]*m/', '', $s);
    $width = 0;
    $len   = mb_strlen($plain, 'UTF-8');
    for ($i = 0; $i < $len; $i++) {
        $ch = mb_substr($plain, $i, 1, 'UTF-8');
        $cp = mb_ord($ch, 'UTF-8');
        if (
            ($cp >= 0x1F300 && $cp <= 0x1F9FF) ||
            ($cp >= 0x2600  && $cp <= 0x27BF)  ||
            ($cp >= 0x2B00  && $cp <= 0x2BFF)  ||
            ($cp >= 0x25A0  && $cp <= 0x25FF)  ||
            ($cp >= 0x2580  && $cp <= 0x259F)
        ) {
            $width += 2;
        } else {
            $width += 1;
        }
    }
    return $width;
}
function ansiPad($s, $len) {
    $pad = $len - ansiLen($s);
    return $s . ($pad > 0 ? str_repeat(' ', $pad) : '');
}
function boxLine($content) {
    return fg(51) . "║  " . "\033[0m" . ansiPad($content, 60) . fg(51) . "║" . "\033[0m" . "\n";
}
function boxDivider() {
    return fg(51) . "╠══════════════════════════════════════════════════════════════╣" . "\033[0m" . "\n";
}

function getIPInfo() {
    static $cached = null;
    if ($cached !== null) return $cached;
    $r = @file_get_contents("http://ip-api.com/json");
    if ($r === false) {
        $cached = ['ip' => '?', 'country' => '?', 'isp' => '?'];
        return $cached;
    }
    $j = json_decode($r, true);
    $cached = [
        'ip'      => $j['query']    ?? '?',
        'country' => ($j['country'] ?? '?') . ' / ' . ($j['city'] ?? '?'),
        'isp'     => $j['isp']      ?? '?'
    ];
    return $cached;
}

// ============================================================
//  BANNER
// ============================================================
function displayBanner($stage = 'INIT', $extra = []) {
    $ipInfo = getIPInfo();
    @system("clear");

    echo fg(51) . "╔══════════════════════════════════════════════════════════════╗" . "\033[0m" . "\n";
    echo boxLine(gradient("ARUBLE.NET AUTO CLAIM", 51, 213));
    echo boxLine(dim("─────── SOUU ENGINE ───────"));
    echo boxDivider();

    echo boxLine(fg(213) . bold("NETWORK") . "\033[0m");
    echo boxLine(fg(51) . "├─ IP         : " . "\033[0m" . fg(226) . $ipInfo['ip'] . "\033[0m");
    echo boxLine(fg(51) . "├─ Country    : " . "\033[0m" . fg(226) . $ipInfo['country'] . "\033[0m");
    echo boxLine(fg(51) . "└─ ISP        : " . "\033[0m" . fg(226) . $ipInfo['isp'] . "\033[0m");
    echo boxDivider();

    echo boxLine(fg(213) . bold("SESSION") . "\033[0m");
    echo boxLine(fg(51) . "├─ Stage      : " . "\033[0m" . fg(208) . $stage . "\033[0m");
    echo boxLine(fg(51) . "├─ Email      : " . "\033[0m" . fg(226) . ($extra['email'] ?? '?') . "\033[0m");
    echo boxLine(fg(51) . "└─ Balance    : " . "\033[0m" . fg(46) . ($extra['balance'] ?? '?') . "\033[0m");
    echo boxDivider();

    echo boxLine(fg(213) . bold("LIVE LOG") . "\033[0m");
    $logs = $extra['logs'] ?? [];
    for ($i = 0; $i < 5; $i++) {
        if (isset($logs[$i])) {
            echo boxLine(fg(252) . $logs[$i] . "\033[0m");
        } else {
            echo fg(51) . "║" . str_repeat(' ', 62) . "║" . "\033[0m" . "\n";
        }
    }

    echo fg(51) . "╚══════════════════════════════════════════════════════════════╝" . "\033[0m" . "\n";
    echo "\n   " . gradient("BOT RUNNING", 46, 226) . " " . fg(250) . "• " . date('H:i:s') . "\033[0m" . "\n";
    echo "   " . dim("By Power ") . fg(213) . "@SouuXso" . "\033[0m" . dim(" • ") . fg(46) . "Aruble Edition" . "\033[0m" . "\n\n";
}

// ============================================================
//  STYLED PROMPT BOX
// ============================================================
function promptBox($title, $subtitle = '') {
    $ipInfo = getIPInfo();
    @system("clear");

    echo fg(51) . "╔══════════════════════════════════════════════════════════════╗" . "\033[0m" . "\n";
    echo boxLine(gradient("ARUBLE.NET FIRST SETUP", 51, 213));
    echo boxLine(dim("─────── SOUU ENGINE ───────"));
    echo boxDivider();

    echo boxLine(fg(213) . bold("NETWORK") . "\033[0m");
    echo boxLine(fg(51) . "├─ IP         : " . "\033[0m" . fg(226) . $ipInfo['ip'] . "\033[0m");
    echo boxLine(fg(51) . "└─ ISP        : " . "\033[0m" . fg(226) . $ipInfo['isp'] . "\033[0m");
    echo boxDivider();

    echo boxLine(fg(213) . bold("INPUT REQUIRED") . "\033[0m");
    echo boxLine(fg(51) . "├─ Field      : " . "\033[0m" . fg(226) . $title . "\033[0m");
    if ($subtitle !== '') {
        echo boxLine(fg(51) . "└─ Hint       : " . "\033[0m" . fg(250) . $subtitle . "\033[0m");
    } else {
        echo fg(51) . "║" . str_repeat(' ', 62) . "║" . "\033[0m" . "\n";
    }

    echo fg(51) . "╚══════════════════════════════════════════════════════════════╝" . "\033[0m" . "\n";
    echo "\n   " . gradient("WAITING INPUT", 46, 226) . " " . fg(250) . "• " . date('H:i:s') . "\033[0m" . "\n";
    echo "   " . dim("By Power ") . fg(213) . "@SouuXso" . "\033[0m" . dim(" • ") . fg(46) . "Aruble Edition" . "\033[0m" . "\n\n";
    echo "  " . fg(51) . "┌─[ " . fg(226) . "INPUT " . strtoupper($title) . fg(51) . " ]" . "\033[0m" . "\n";
    echo "  " . fg(51) . "└──> " . "\033[0m";
}

// ============================================================
//  TIMER — single-line refresh (termux-friendly)
// ============================================================
function timer($seconds) {
    date_default_timezone_set('UTC');
    if (!$seconds || !is_numeric($seconds)) $seconds = 5;

    $total = (int)$seconds;
    $start = time();
    $bar_len = 20;

    while (true) {
        $elapsed = time() - $start;
        $left    = $total - $elapsed;
        if ($left < 1) break;

        $pct = min(1, $elapsed / max(1, $total));
        $fill = (int)round($pct * $bar_len);
        if ($fill > $bar_len) $fill = $bar_len;
        $empty = $bar_len - $fill;

        $bar_full  = str_repeat("█", $fill);
        $bar_empty = str_repeat("░", $empty);

        if ($left >= 3600) {
            $time_str = sprintf("%d:%02d Jam", floor($left/3600), floor(($left%3600)/60));
        } elseif ($left >= 60) {
            $time_str = sprintf("%d:%02d Menit", floor($left/60), $left%60);
        } else {
            $time_str = sprintf("%d Detik", $left);
        }

        $pct_str  = str_pad((int)round($pct * 100) . "%", 4, ' ', STR_PAD_LEFT);
        $time_str = str_pad($time_str, 12, ' ', STR_PAD_LEFT);

        $line = fg(226) . "LOADING" . "\033[0m"
              . " " . fg(51) . "[" . "\033[0m"
              . fg(46) . $bar_full . "\033[0m"
              . fg(240) . $bar_empty . "\033[0m"
              . fg(51) . "] " . "\033[0m"
              . fg(250) . $pct_str . "\033[0m"
              . " " . fg(208) . $time_str . "\033[0m";

        echo "\r" . $line . str_repeat(" ", 20);

        sleep(1);
    }

    echo "\r" . str_repeat(" ", 90) . "\r";
}

// ============================================================
//  GLOBAL LOG
// ============================================================
$GLOBALS['_logs'] = [];
$GLOBALS['_stage'] = 'INIT';
$GLOBALS['_email'] = '?';
$GLOBALS['_balance'] = '?';

function pushLog($msg) {
    $GLOBALS['_logs'][] = "[" . date('H:i:s') . "] " . $msg;
    if (count($GLOBALS['_logs']) > 5) array_shift($GLOBALS['_logs']);
}
function refreshBanner() {
    displayBanner($GLOBALS['_stage'], [
        'email'   => $GLOBALS['_email'],
        'balance' => $GLOBALS['_balance'],
        'logs'    => $GLOBALS['_logs']
    ]);
}

// ============================================================
//  HELPER: quick GET
// ============================================================
function curl_exec_quick($url, $api) {
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL            => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING       => '',
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_MAXREDIRS      => 5,
        CURLOPT_COOKIEJAR      => 'cookie.txt',
        CURLOPT_COOKIEFILE     => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT        => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER     => [
            'x-requested-with: XMLHttpRequest',
            'User-Agent: ' . $api,
            'sec-ch-ua-full-version: "149.0.7827.197"',
            'referer: https://aruble.net/',
            'accept: */*',
            'accept-language: en-GB,en-US;q=0.9,en;q=0.8',
        ],
    ]);
    $r = curl_exec($ch);
    curl_close($ch);
    return $r;
}

// ============================================================
//  BOT CHECK SIGNAL
// ============================================================
function botCheckSignal($path, $api) {
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL            => 'https://aruble.net/bot-check/signal',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CUSTOMREQUEST  => 'POST',
        CURLOPT_POSTFIELDS     => [
            'mouse'         => rand(8, 25),
            'keyboard'      => rand(0, 4),
            'scroll'        => rand(3, 12),
            'touch'         => rand(2, 8),
            'elapsed'       => rand(20000, 80000),
            'mouse_linear'  => rand(0, 3),
            'direct_clicks' => rand(1, 3),
            'integrity'     => '',
            'path'          => $path,
        ],
        CURLOPT_COOKIEJAR      => 'cookie.txt',
        CURLOPT_COOKIEFILE     => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT        => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER     => [
            'x-requested-with: XMLHttpRequest',
            'User-Agent: ' . $api,
            'sec-ch-ua-full-version: "149.0.7827.197"',
        ],
    ]);
    $response = curl_exec($curl);
    curl_close($curl);
    return $response;
}

// ============================================================
//  ARUBLE CAPTCHA SOLVER
// ============================================================
function aruble($csrf, $api = null, $path = '/faucet') {
    // BOT CHECK
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL            => 'https://aruble.net/bot-check/signal',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CUSTOMREQUEST  => 'POST',
        CURLOPT_POSTFIELDS     => [
            'mouse' => rand(8,25), 'keyboard' => rand(0,4), 'scroll' => rand(3,12),
            'touch' => rand(2,8), 'elapsed' => rand(20000,80000), 'mouse_linear' => rand(0,3),
            'direct_clicks' => rand(1,3), 'integrity' => '', 'path' => $path,
        ],
        CURLOPT_COOKIEJAR      => 'cookie.txt',
        CURLOPT_COOKIEFILE     => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT        => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER     => [
            'x-requested-with: XMLHttpRequest',
            'User-Agent: ' . $api,
            'sec-ch-ua-full-version: "149.0.7827.197"',
        ],
    ]);
    $res = curl_exec($curl);
    if ($res === false || curl_errno($curl)) { curl_close($curl); return null; }
    curl_close($curl);

    // GET CAPTCHA
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL            => 'https://aruble.net/captcha/challenge',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING       => '',
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_COOKIEJAR      => 'cookie.txt',
        CURLOPT_COOKIEFILE     => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT        => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER     => [
            'x-requested-with: XMLHttpRequest',
            'user-agent: ' . $api,
            'referer: https://aruble.net/',
        ],
    ]);
    $res = curl_exec($curl);
    if ($res === false || curl_errno($curl)) { curl_close($curl); return null; }
    pushLog("CAPTCHA challenge");
    refreshBanner();
    curl_close($curl);

    $data = json_decode($res, true);
    if (isset($data['banned']) && $data['banned'] === true && isset($data['remaining_seconds'])) {
        timer((int)$data['remaining_seconds']);
        return null;
    }
    if (!$data) return null;

    // GATE
    if (!empty($data['gate_required'])) {
        usleep(($data['hold_ms'] ?? 1000) * 1000);

        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL            => 'https://aruble.net/captcha/gate/start',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_ENCODING       => '',
            CURLOPT_POST           => true,
            CURLOPT_POSTFIELDS     => "_csrf_token=$csrf",
            CURLOPT_COOKIEJAR      => 'cookie.txt',
            CURLOPT_COOKIEFILE     => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false,
            CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_TIMEOUT        => 20,
            CURLOPT_CONNECTTIMEOUT => 8,
        ]);
        $response = curl_exec($curl);
        if ($response === false || curl_errno($curl)) { curl_close($curl); return null; }
        pushLog("CAPTCHA gate/start");
        refreshBanner();
        curl_close($curl);

        $gate = json_decode($response, true);
        if (stripos($res, '<title>Redirecting...') !== false || stripos($res, 'Please login') !== false) return null;
        if (empty($gate['success'])) return null;

        usleep($gate['hold_ms'] * 1000);

        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL            => 'https://aruble.net/captcha/gate/complete',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_ENCODING       => '',
            CURLOPT_POST           => true,
            CURLOPT_POSTFIELDS     => http_build_query([
                'gate_key' => $gate['gate_key'], 'moves' => rand(40,60), '_csrf_token' => $csrf
            ]),
            CURLOPT_COOKIEJAR      => 'cookie.txt',
            CURLOPT_COOKIEFILE     => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false,
            CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_TIMEOUT        => 20,
            CURLOPT_CONNECTTIMEOUT => 8,
        ]);
        $response = curl_exec($curl);
        if ($response === false || curl_errno($curl)) { curl_close($curl); return null; }
        curl_close($curl);
        pushLog("CAPTCHA gate/complete");
        refreshBanner();

        $complete = json_decode($response, true);
        if (empty($complete['success'])) return null;

        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL            => 'https://aruble.net/captcha/challenge',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_ENCODING       => '',
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_COOKIEJAR      => 'cookie.txt',
            CURLOPT_COOKIEFILE     => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false,
            CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_TIMEOUT        => 20,
            CURLOPT_CONNECTTIMEOUT => 8,
        ]);
        $res = curl_exec($curl);
        if ($res === false || curl_errno($curl)) { curl_close($curl); return null; }
        pushLog("CAPTCHA re-challenge");
        refreshBanner();
        curl_close($curl);

        $data = json_decode($res, true);
        if (!$data) return null;
    }

    // SOLVE
    $key  = $data['key']  ?? null;
    $type = $data['type'] ?? null;
    if (!$key || !$type) return null;

    $answer = "";
    $solve_time = 0;

    if ($type == "least_repeat") {
        $icons = [];
        foreach ($data['grid'] as $item) $icons[$item['icon']][] = $item['id'];
        asort($icons);
        $answer = $icons[array_key_first($icons)][0];
        $solve_time = rand(20000, 50000);
    } elseif ($type == "slide") {
        $answer = $data['target_pct'] + rand(2, 5);
        $solve_time = rand(4000, 8000);
    } elseif ($type == "icon_order") {
        $map = [];
        foreach ($data['display'] as $item) $map[$item['icon']] = $item['id'];
        $answerArr = [];
        foreach ($data['prompt'] as $icon) $answerArr[] = $map[$icon];
        $answer = json_encode($answerArr);
        $solve_time = rand(20000, 40000);
    } elseif ($type == "drag_dot") {
        $jx = rand(-2, 2); $jy = rand(-2, 2);
        $answer = json_encode([
            "x" => (int)$data['target_x'] + $jx,
            "y" => (int)$data['target_y'] + $jy
        ]);
        $solve_time = rand(5000, 10000);
    } else {
        return null;
    }

    usleep($solve_time);

    // VERIFY + fake human trace
    $trace = [];
    $t = 0;
    $tx = rand(180, 350); $ty = rand(400, 600);
    $ex = rand(500, 800); $ey = rand(150, 320);
    $steps = rand(35, 60);
    for ($i = 0; $i <= $steps; $i++) {
        $p = $i / $steps;
        $e = $p < 0.5 ? 2 * $p * $p : 1 - pow(-2 * $p + 2, 2) / 2;
        $x = $tx + ($ex - $tx) * $e + (rand(-20, 20) / 10);
        $y = $ty + ($ey - $ty) * $e + (rand(-20, 20) / 10);
        $t += rand(6, 22);
        $trace[] = [$t, round($x, 2), round($y, 2)];
    }
    $trace_json = json_encode($trace);

    $post_body = "key=$key"
        . "&answer=" . urlencode($answer)
        . "&trace=" . urlencode($trace_json)
        . "&cf_token=&cf_state=no_widget"
        . "&_csrf_token=$csrf";

    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL            => 'https://aruble.net/captcha/verify',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING       => '',
        CURLOPT_CUSTOMREQUEST  => 'POST',
        CURLOPT_POSTFIELDS     => $post_body,
        CURLOPT_COOKIEJAR      => 'cookie.txt',
        CURLOPT_COOKIEFILE     => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT        => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER     => [
            'x-requested-with: XMLHttpRequest',
            'user-agent: ' . $api,
            'content-type: application/x-www-form-urlencoded; charset=UTF-8',
            'origin: https://aruble.net',
            'referer: https://aruble.net/',
            'accept: */*',
            'accept-language: en-GB,en-US;q=0.9,en;q=0.8',
        ],
    ]);

    $response = curl_exec($curl);
    if ($response === false || curl_errno($curl)) { curl_close($curl); return null; }
    pushLog("CAPTCHA verify");
    refreshBanner();
    curl_close($curl);

    $result = json_decode($response, true);
    if (empty($result['success']) || empty($result['token'])) {
        @file_put_contents('debug_verify.txt',
            "== BODY ==\n$post_body\n\n== RESPONSE ==\n$response\n\n");
        return null;
    }
    return $result['token'];
}

function slow($text, $delay = 30000) {
    echo $text;
}

function clear() {
    if (stripos(PHP_OS, 'WIN') === 0) { pclose(popen('cls', 'w')); } else { passthru('clear'); }
}

function Save($namadata) {
    if (file_exists($namadata)) {
        $data = file_get_contents($namadata);
    } else {
        $label = ucfirst($namadata);
        $hint = '';
        if ($namadata === 'Email')      $hint = 'email akun aruble lo';
        if ($namadata === 'Password')   $hint = 'password akun aruble lo';
        if ($namadata === 'user-agent') $hint = 'paste user-agent browser lo';

        promptBox($label, $hint);
        $data = trim(fgets(STDIN));

        if ($data === '') {
            echo "\n  " . fg(196) . "x kosong, coba lagi" . "\033[0m\n";
            usleep(800000);
            return Save($namadata);
        }

        file_put_contents($namadata, $data);
        echo "\n  " . fg(46) . "v tersimpan" . "\033[0m\n";
        usleep(600000);
    }
    return $data;
}

// ============================================================
//  MAIN
// ============================================================
$email = Save("Email");
$pass  = Save("Password");
$api   = Save("user-agent");

$GLOBALS['_email'] = $email;

displayBanner('INIT', ['email' => $email, 'balance' => '?']);
sleep(2);

// ============================================================
//  LOGIN
// ============================================================
login:
@unlink("cookie.txt");

pushLog("AUTH fetching base...");
refreshBanner();

$curl = curl_init();
curl_setopt_array($curl, [
    CURLOPT_URL            => 'https://aruble.net',
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_ENCODING       => '',
    CURLOPT_FOLLOWLOCATION => true,
    CURLOPT_MAXREDIRS      => 5,
    CURLOPT_COOKIEJAR      => 'cookie.txt',
    CURLOPT_COOKIEFILE     => 'cookie.txt',
    CURLOPT_SSL_VERIFYPEER => false,
    CURLOPT_SSL_VERIFYHOST => false,
    CURLOPT_TIMEOUT        => 30,
    CURLOPT_CONNECTTIMEOUT => 8,
    CURLOPT_HTTPHEADER     => [
        'User-Agent: ' . $api,
        'cache-control: max-age=0',
        'sec-ch-ua: "Chromium";v="146", "Not-A.Brand";v="24", "Android WebView";v="146"',
        'sec-ch-ua-mobile: ?1',
        'sec-ch-ua-platform: "Android"',
        'upgrade-insecure-requests: 1',
        'x-requested-with: XMLHttpRequest',
        'sec-fetch-site: none',
        'sec-fetch-mode: navigate',
        'sec-fetch-user: ?1',
        'sec-fetch-dest: document',
        'accept-language: en-GB,en-US;q=0.9,en;q=0.8',
        'priority: u=0, i',
    ],
]);
$res = curl_exec($curl);
curl_close($curl);

$csrf = explode('">', explode('<meta name="csrf-token" content="', $res)[1] ?? '')[0] ?? null;
if (!$csrf) {
    $snippet = substr(strip_tags($res), 0, 80);
    pushLog("FAIL csrf not found: " . $snippet);
    refreshBanner();
    sleep(3);
    goto login;
}

$token = aruble($csrf, $api, '/login');

if (!$token) {
    pushLog("FAIL captcha login fail, retry");
    refreshBanner();
    sleep(3);
    goto login;
}

$curl = curl_init();
curl_setopt_array($curl, [
    CURLOPT_URL            => 'https://aruble.net/api/auth/login',
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_ENCODING       => '',
    CURLOPT_CUSTOMREQUEST  => 'POST',
    CURLOPT_POSTFIELDS     => "_csrf_token=$csrf&email=$email&password=$pass&captcha_token=$token&remember_me=1&device_fingerprint=0d2be167b01027c02ec8e88326aaa91d26c20f1794b4c221d905fa603846c7c3",
    CURLOPT_COOKIEJAR      => 'cookie.txt',
    CURLOPT_COOKIEFILE     => 'cookie.txt',
    CURLOPT_SSL_VERIFYPEER => false,
    CURLOPT_SSL_VERIFYHOST => false,
    CURLOPT_TIMEOUT        => 30,
    CURLOPT_CONNECTTIMEOUT => 8,
    CURLOPT_HTTPHEADER     => [
        'User-Agent: ' . $api,
        'sec-ch-ua-platform: "Android"',
        'x-requested-with: XMLHttpRequest',
        'sec-ch-ua: "Chromium";v="146", "Not-A.Brand";v="24", "Android WebView";v="146"',
        'content-type: application/x-www-form-urlencoded; charset=UTF-8',
        'sec-ch-ua-mobile: ?1',
        'origin: https://aruble.net',
        'sec-fetch-site: same-origin',
        'sec-fetch-mode: cors',
        'sec-fetch-dest: empty',
        'referer: https://aruble.net/',
        'accept-language: en-GB,en-US;q=0.9,en;q=0.8',
        'priority: u=1, i',
    ],
]);
$response = curl_exec($curl);
curl_close($curl);

$data = json_decode($response, true);
if ($data && ($data['success'] ?? false)) {
    pushLog("AUTH login OK");
    refreshBanner();
    sleep(2);
    goto challenge;
} else {
    $msg = $data['message'] ?? 'unknown';
    pushLog("FAIL login: $msg, retry");
    refreshBanner();
    sleep(3);
    goto login;
}

// ============================================================
//  CHALLENGE
// ============================================================
challenge:

$GLOBALS['_stage'] = 'CHALLENGE';

$test = curl_exec_quick('https://aruble.net/dashboard', $api);
$pre_len   = strlen($test);
$has_login = stripos($test, 'Please login') !== false ? 'Y' : 'N';
$has_cf    = stripos($test, 'Just a moment') !== false ? 'Y' : 'N';
$has_redir = stripos($test, '<title>Redirecting') !== false ? 'Y' : 'N';
$has_csrf  = stripos($test, '<meta name="csrf-token"') !== false ? 'Y' : 'N';
pushLog("pre: len={$pre_len} log={$has_login} cf={$has_cf} rdr={$has_redir} csrf={$has_csrf}");
refreshBanner();
sleep(1);

while (true) {
    pushLog("challenge fetch...");
    refreshBanner();

    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL            => 'https://aruble.net/challenge',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING       => '',
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_MAXREDIRS      => 5,
        CURLOPT_COOKIEJAR      => 'cookie.txt',
        CURLOPT_COOKIEFILE     => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT        => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER     => [
            'x-requested-with: XMLHttpRequest',
            'User-Agent: ' . $api,
            'sec-ch-ua-full-version: "149.0.7827.197"',
            'referer: https://aruble.net/',
        ],
    ]);

    $res = curl_exec($curl);
    $http_code = curl_getinfo($curl, CURLINFO_HTTP_CODE);
    curl_close($curl);
    sleep(rand(2, 5));

    $csrf  = explode('">', explode('<meta name="csrf-token" content="', $res)[1] ?? '')[0] ?? null;
    $title = explode('</title>', explode('<title>', $res)[1] ?? '')[0] ?? '';

    $has_login2 = stripos($res, 'Please login') !== false ? 'Y' : 'N';
    $has_cf2    = stripos($res, 'Just a moment') !== false ? 'Y' : 'N';
    $has_claim  = preg_match('/onclick="claimChallenge\((\d+),\s*this\)"/i', $res) ? 'Y' : 'N';
    $has_remain = preg_match('/"remaining_seconds"\s*:\s*(\d+)/', $res) ? 'Y' : 'N';
    $len        = strlen($res);

    pushLog("ch http={$http_code} len={$len} csrf=" . ($csrf ? 'Y' : 'N') . " log={$has_login2} cf={$has_cf2} c={$has_claim} r={$has_remain} t=" . substr($title, 0, 20));
    refreshBanner();

    if ($csrf === null) continue;

    if ($title == "Just a moment...") {
        pushLog("CF challenge, sleep 300");
        refreshBanner();
        sleep(300);
        continue;
    }

    if (stripos($res, '<title>Redirecting...</title>') !== false || stripos($res, 'Please login') !== false) goto login;

    if (preg_match('/"remaining_seconds"\s*:\s*(\d+)/', $res, $m)) goto Daily;

    if (!preg_match('/onclick="claimChallenge\((\d+),\s*this\)"/i', $res, $m)) {
        pushLog("no claim button, goto Daily");
        refreshBanner();
        goto Daily;
    }

    $claimid = $m[1];

    botCheckSignal('/challenge', $api);
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL            => 'https://aruble.net/challenge/claim',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING       => '',
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => http_build_query([
            'challenge_id' => $claimid, '_csrf_token' => $csrf
        ]),
        CURLOPT_COOKIEJAR      => 'cookie.txt',
        CURLOPT_COOKIEFILE     => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT        => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER     => [
            'User-Agent: ' . $api,
            'Accept: application/json, text/javascript, */*; q=0.01',
            'sec-ch-ua-platform: "Android"',
            'x-requested-with: XMLHttpRequest',
            'content-type: application/x-www-form-urlencoded; charset=UTF-8',
            'origin: https://aruble.net',
            'referer: https://aruble.net/challenge',
            'accept-language: en-GB,en-US;q=0.9,en;q=0.8',
        ],
    ]);
    $res = curl_exec($curl);
    curl_close($curl);
    $data = json_decode($res, true);

    if (isset($data['message']) && $data['message'] === "Invalid session. Please go back and try again.") goto login;
    if (isset($data['message']) && $data['message'] === "Please login") goto login;

    if ($data && ($data['success'] ?? false)) {
        $challenge = $data['challenge_name'];
        $reward = $data['reward'];
        pushLog("CHALLENGE {$challenge} +{$reward}");
        refreshBanner();
    }
}

// ============ DAILY ============
Daily:

while (true) {
    $GLOBALS['_stage'] = 'DAILY';
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/daily-bonus',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => '',
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_COOKIEJAR => 'cookie.txt',
        CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => [
            'x-requested-with: XMLHttpRequest',
            'User-Agent: ' . $api,
            'sec-ch-ua-full-version: "149.0.7827.197"',
        ],
    ]);
    $res = curl_exec($curl);
    curl_close($curl);

    $csrf = explode('">', explode('<meta name="csrf-token" content="', $res)[1] ?? '')[0] ?? null;
    $title = explode('</title>', explode('<title>', $res)[1] ?? '')[0] ?? '';
    if ($title == "Just a moment...") { sleep(300); continue; }
    if ($csrf === null) continue;

    if (stripos($res, '<title>Redirecting...</title>') !== false || stripos($res, 'Please login') !== false) goto login;
    if (preg_match('/"remaining_seconds"\s*:\s*(\d+)/', $res, $m)) goto login;
    if (strpos($res, 'Come Back Later') !== false) goto Spin;

    $token = aruble($csrf, $api, '/daily-bonus');
    if (!$token) continue;

    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/daily-bonus/claim',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => '',
        CURLOPT_CUSTOMREQUEST => 'POST',
        CURLOPT_POSTFIELDS => "captcha_token=$token&_csrf_token=$csrf",
        CURLOPT_COOKIEJAR => 'cookie.txt',
        CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => [
            'User-Agent: ' . $api,
            'x-requested-with: XMLHttpRequest',
            'content-type: application/x-www-form-urlencoded; charset=UTF-8',
            'origin: https://aruble.net',
            'referer: https://aruble.net/daily-bonus',
        ],
    ]);
    $res = curl_exec($curl);
    curl_close($curl);
    $data = json_decode($res, true);

    if ($data && ($data['success'] ?? false) === false) {
        $message = $data['message'] ?? '';
        if (strpos($message, 'You need 10 more faucet claims today before collecting your bonus') !== false) goto Spin;
    }
    if (isset($data['message']) && $data['message'] === "Invalid session. Please go back and try again.") goto login;
    if (isset($data['message']) && $data['message'] === "Please login") goto login;

    if ($data && ($data['success'] ?? false)) {
        $amount = $data['amount']; $streak = $data['streak'];
        $balance = $data['balance_after']; $symbol = $data['symbol'];
        $GLOBALS['_balance'] = $balance;
        pushLog("DAILY +{$amount} {$symbol} streak {$streak}");
        refreshBanner();
    }
    goto Spin;
}

// ============ SPIN ============
Spin:

while (true) {
    $GLOBALS['_stage'] = 'SPIN';
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/spin',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => '',
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_COOKIEJAR => 'cookie.txt',
        CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => [
            'x-requested-with: XMLHttpRequest',
            'User-Agent: ' . $api,
            'sec-ch-ua-full-version: "149.0.7827.197"',
        ],
    ]);
    $res = curl_exec($curl);
    curl_close($curl);

    $csrf = explode('">', explode('<meta name="csrf-token" content="', $res)[1] ?? '')[0] ?? null;
    $title = explode('</title>', explode('<title>', $res)[1] ?? '')[0] ?? '';
    if ($title == "Just a moment...") { sleep(300); continue; }
    if ($csrf === null) continue;

    if (stripos($res, '<title>Redirecting...</title>') !== false || stripos($res, 'Please login') !== false) goto login;
    if (preg_match('/"remaining_seconds"\s*:\s*(\d+)/', $res, $m)) goto login;
    if (strpos($res, 'No Spins Available') !== false) goto faucet;

    $token = aruble($csrf, $api, '/spin');
    if (!$token) continue;

    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/spin/claim',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => '',
        CURLOPT_CUSTOMREQUEST => 'POST',
        CURLOPT_POSTFIELDS => "captcha_token=$token&_csrf_token=$csrf",
        CURLOPT_COOKIEJAR => 'cookie.txt',
        CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => [
            'User-Agent: ' . $api,
            'x-requested-with: XMLHttpRequest',
            'content-type: application/x-www-form-urlencoded; charset=UTF-8',
            'origin: https://aruble.net',
            'referer: https://aruble.net/spin',
        ],
    ]);
    $res = curl_exec($curl);
    curl_close($curl);
    $data = json_decode($res, true);

    if (($data['success'] ?? true) === false && str_contains($data['message'] ?? '', 'Lucky Wheel is currently under maintenance')) goto faucet;
    if (isset($data['message']) && $data['message'] === "Invalid session. Please go back and try again.") goto login;
    if (isset($data['message']) && $data['message'] === "Please login") goto login;

    if ($data && ($data['success'] ?? false)) {
        $reward = $data['reward']; $label = $data['label'];
        $balance = $data['new_balance']; $spinsLeft = $data['spins_left'];
        $GLOBALS['_balance'] = $balance;
        pushLog("SPIN {$label} +{$reward} left {$spinsLeft}");
        refreshBanner();
    }
}

// ============ FAUCET ============
faucet:

while (true) {
    $GLOBALS['_stage'] = 'FAUCET';
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/faucet',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => '',
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_COOKIEJAR => 'cookie.txt',
        CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => [
            'x-requested-with: XMLHttpRequest',
            'User-Agent: ' . $api,
            'sec-ch-ua-full-version: "149.0.7827.197"',
        ],
    ]);
    $res = curl_exec($curl);
    curl_close($curl);
    sleep(rand(2, 5));

    $csrf = explode('">', explode('<meta name="csrf-token" content="', $res)[1] ?? '')[0] ?? null;
    $title = explode('</title>', explode('<title>', $res)[1] ?? '')[0] ?? '';
    if ($title == "Just a moment...") { sleep(300); continue; }
    if ($csrf === null) continue;

    if (stripos($res, '<title>Redirecting...</title>') !== false || stripos($res, 'Please login') !== false) goto login;
    if (preg_match('/"remaining_seconds"\s*:\s*(\d+)/', $res, $m)) goto login;

    if (preg_match('/globalCooldown\s*:\s*(\d+)/', $res, $m)) {
        $cooldownF = $m[1];
        if ($cooldownF > 0) { timer($cooldownF + rand(5, 15)); continue; }
    }

    $token = aruble($csrf, $api, '/faucet');
    if (!$token) continue;

    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/faucet/claim',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => '',
        CURLOPT_CUSTOMREQUEST => 'POST',
        CURLOPT_POSTFIELDS => "dest=account&wc_id=0&captcha_token=$token&fp=0d2be167b01027c02ec8e88326aaa91d26c20f1794b4c221d905fa603846c7c3&_csrf_token=$csrf",
        CURLOPT_COOKIEJAR => 'cookie.txt',
        CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => [
            'User-Agent: ' . $api,
            'Accept: application/json, text/javascript, */*; q=0.01',
            'sec-ch-ua-platform: "Android"',
            'x-requested-with: XMLHttpRequest',
            'content-type: application/x-www-form-urlencoded; charset=UTF-8',
            'origin: https://aruble.net',
            'referer: https://aruble.net/faucet',
        ],
    ]);
    $res = curl_exec($curl);
    curl_close($curl);
    $data = json_decode($res, true);

    if ($data && ($data['success'] ?? false) === false) {
        $msg = $data['message'] ?? '';
        if (strpos($msg, 'daily limit') !== false) {
            pushLog("FAUCET daily limit, wait");
            refreshBanner();
            timer(1800);
            goto roll;
        }
    }
    if (isset($data['message']) && $data['message'] === "Invalid session. Please go back and try again.") goto login;
    if (isset($data['message']) && $data['message'] === "Please login") goto login;

    if ($data && ($data['success'] ?? false)) {
        $amount = $data['amount']; $symbol = $data['symbol'];
        $balance = $data['balance_after'];
        $today = $data['claims_today']; $max = $data['claims_max'];
        $GLOBALS['_balance'] = $balance;
        pushLog("FAUCET +{$amount} {$symbol} {$today}/{$max}");
        refreshBanner();
        timer(300);
        goto roll;
    }
}

// ============ ROLL ============
roll:

while (true) {
    $GLOBALS['_stage'] = 'ROLL';
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/bonus-roll',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => '',
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_COOKIEJAR => 'cookie.txt',
        CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => [
            'x-requested-with: XMLHttpRequest',
            'User-Agent: ' . $api,
            'sec-ch-ua-full-version: "149.0.7827.197"',
        ],
    ]);
    $res = curl_exec($curl);
    curl_close($curl);

    $csrf = explode('">', explode('<meta name="csrf-token" content="', $res)[1] ?? '')[0] ?? null;
    $title = explode('</title>', explode('<title>', $res)[1] ?? '')[0] ?? '';
    if ($title == "Just a moment...") { sleep(300); continue; }
    if ($csrf === null) continue;

    if (stripos($res, '<title>Redirecting...</title>') !== false || stripos($res, 'Please login') !== false) goto login;
    if (preg_match('/"remaining_seconds"\s*:\s*(\d+)/', $res, $m)) goto login;

    if (stripos($res, 'On Cooldown') !== false) { timer(60); goto faucet; }

    $token = aruble($csrf, $api, '/bonus-roll');
    if (!$token) continue;

    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/bonus-roll/claim',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_ENCODING => '',
        CURLOPT_CUSTOMREQUEST => 'POST',
        CURLOPT_POSTFIELDS => "captcha_token=$token&_csrf_token=$csrf",
        CURLOPT_COOKIEJAR => 'cookie.txt',
        CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => [
            'User-Agent: ' . $api,
            'x-requested-with: XMLHttpRequest',
            'content-type: application/x-www-form-urlencoded; charset=UTF-8',
            'origin: https://aruble.net',
            'referer: https://aruble.net/bonus-roll',
        ],
    ]);
    $res = curl_exec($curl);
    curl_close($curl);
    $data = json_decode($res, true);

    if (isset($data['message']) && $data['message'] === "The Bonus Roll is currently under maintenance.") goto faucet;
    if (isset($data['message']) && $data['message'] === "Invalid session. Please go back and try again.") goto login;
    if (isset($data['message']) && $data['message'] === "Please login") goto login;

    if ($data && ($data['success'] ?? false)) {
        $drawn = $data['number_drawn']; $reward = $data['reward'];
        $label = strip_tags($data['label']); $balance = $data['new_token_balance'];
        $GLOBALS['_balance'] = $balance;
        pushLog("ROLL #{$drawn} {$label} +{$reward}");
        refreshBanner();
        timer(60);
        goto faucet;
    }
}
