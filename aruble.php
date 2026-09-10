<?php // index.php
@system("clear");
error_reporting(0);

date_default_timezone_set('Asia/Kolkata');

// ===== COLORS =====
$R = "\033[0m";
$B = "\033[1m";
$RED = "\033[1;31m";
$GRN = "\033[1;32m";
$YEL = "\033[1;33m";
$BLU = "\033[1;34m";
$MAG = "\033[1;35m";
$CYN = "\033[1;36m";
$WHT = "\033[1;37m";
$DIM = "\033[2m";

// ===== HEADERS HELPER =====
function head() {
    return [
        'Accept: application/json, text/javascript, */*; q=0.01',
        'x-requested-with: XMLHttpRequest',
        'accept-language: en-GB,en-US;q=0.9,en;q=0.8',
    ];
}

// ===== BANNER =====
function printBanner() {
    $CYN = "\033[1;36m";
    $R = "\033[0m";
    echo $CYN;
    echo " ▄▄▄       ██▀███   █    ██  ▄▄▄▄    ██▓    ▓█████ \n";
    echo "▒████▄    ▓██ ▒ ██▒ ██  ▓██▒▓█████▄ ▓██▒    ▓█   ▀ \n";
    echo "▒██  ▀█▄  ▓██ ░▄█ ▒▓██  ▒██░▒██▒ ▄██▒██░    ▒███   \n";
    echo "░██▄▄▄▄██ ▒██▀▀█▄  ▓▓█  ░██░▒██░█▀  ▒██░    ▒▓█  ▄ \n";
    echo " ▓█   ▓██▒░██▓ ▒██▒▒▒█████▓ ░▓█  ▀█▓░██████▒░▒████▒\n";
    echo " ▒▒   ▓▒█░░ ▒▓ ░▒▓░░▒▓▒ ▒ ▒ ░▒▓███▀▒░ ▒░▓  ░░░ ▒░ ░\n";
    echo "  ▒   ▒▒ ░  ░▒ ░ ▒░░░▒░ ░ ░ ▒░▒   ░ ░ ░ ▒  ░ ░ ░  ░\n";
    echo "  ░   ▒     ░░   ░  ░░░ ░ ░  ░    ░   ░ ░      ░   \n";
    echo "      ░  ░   ░        ░      ░          ░  ░   ░  ░\n";
    echo "                                  ░                \n";
    echo $R;
}

// ===== MAIN MENU =====
function showMenu() {
    global $R, $B, $GRN, $YEL, $CYN, $WHT, $RED;
    @system("clear");
    printBanner();
    echo "\n";
    echo $CYN . "==================================================\n" . $R;
    echo $CYN . "                 " . $WHT . "ARUBLE.NET" . $CYN . "\n" . $R;
    echo $CYN . "==================================================\n" . $R;
    echo $CYN . "             ScriptMaker: " . $YEL . "SouuXso" . $CYN . "\n" . $R;
    echo $CYN . "==================================================\n\n" . $R;

    echo "  " . $GRN . "[1]" . $WHT . " 🚜 Start Farming\n" . $R;
    echo "  " . $GRN . "[2]" . $WHT . " 📧 Config Email\n" . $R;
    echo "  " . $GRN . "[3]" . $WHT . " 🔐 Config Password\n" . $R;
    echo "  " . $GRN . "[4]" . $WHT . " 📱 Config User-Agent\n" . $R;
    echo "  " . $RED . "[0]" . $WHT . " 🚪 Exit\n\n" . $R;

    echo $CYN . "==================================================\n" . $R;
    echo $CYN . "  ➜ " . $WHT . "Pilih menu: " . $YEL;
}

// ===== CONFIG FILES =====
function cfg_set($file, $label) {
    global $R, $CYN, $WHT, $GRN, $YEL;
    $current = file_exists($file) ? file_get_contents($file) : '';
    echo "\n" . $CYN . "  Current " . $label . ": " . $YEL . ($current === '' ? '(kosong)' : $current) . "\n" . $R;
    echo $WHT . "  ➜ Input " . $label . " baru: " . $YEL;
    $v = trim(fgets(STDIN));
    if ($v === '') {
        echo $YEL . "  (kosong, gak disimpan)\n" . $R;
        return;
    }
    file_put_contents($file, $v);
    echo $GRN . "  ✓ " . $label . " tersimpan\n" . $R;
    sleep(1);
}

// ===== SAVE / GET DATA =====
function Save($namadata){
	if(file_exists($namadata)){
		$data = file_get_contents($namadata);
	}else{
		$data = readline("\033[102m\033[1;34m Input ".$namadata."\033[0m\033[1;32m\n ►► \033[1;37m");
		file_put_contents($namadata,$data);
	}
	return $data;
}

// ===== SLOW =====
function slow($text, $delay = 30000) {
    ob_start();
    foreach (str_split($text) as $char) { echo $char; }
    ob_end_flush();
    echo "\r";
}

// ===== TIMER (ungu progress bar) =====
function timer($timer) {
    date_default_timezone_set('UTC');
    if (!$timer || !is_numeric($timer)) { $timer = 5; }

    $purple = "\033[1;35m";   // ungu terang
    $dim    = "\033[2;35m";   // ungu redup
    $wht    = "\033[1;97m";
    $R      = "\033[0m";

    $total = (int)$timer;
    if ($total < 1) return;
    $end = time() + $total;
    $barLen = 10;

    while (true) {
        $left = $end - time();
        if ($left < 0) $left = 0;

        $h = floor($left / 3600);
        $m = floor(($left % 3600) / 60);
        $s = $left % 60;
        $timeStr = sprintf("%02d:%02d:%02d", $h, $m, $s);

        $elapsed = $total - $left;
        $filled = (int)round(($elapsed / $total) * $barLen);
        if ($filled > $barLen) $filled = $barLen;
        if ($filled < 0) $filled = 0;
        $empty = $barLen - $filled;
        $bar = str_repeat("█", $filled) . str_repeat("░", $empty);

        echo "\r" . $purple . "[⏳ WAIT] " . $wht . "Menunggu " . $purple . "[$timeStr] " . $dim . "[" . $bar . "]" . $R . "   ";

        if ($left < 1) break;
        sleep(1);
    }
    echo "\r" . str_repeat(" ", 80) . "\r";
}

// ===== CLAIM BOX OUTPUT =====
function printClaim($title, $emoji, $rows) {
    global $R, $CYN, $WHT, $GRN, $YEL;
    echo $CYN . "===== " . $WHT . $title . $CYN . " =====\n" . $R;
    foreach ($rows as $r) {
        echo "  " . $r . "\n";
    }
    echo $CYN . "===============\n" . $R;
}

function fmtNext($sec) {
    $sec = (int)$sec;
    if ($sec <= 0) return "∞";
    $m = floor($sec / 60);
    $s = $sec % 60;
    return sprintf("%02d:%02d", $m, $s);
}

// ===== SHARED HELPERS =====
function runAdGate(
    string $api,
    string $placement = 'faucet',
    string $page_path = '/faucet',
    string $check_url = 'https://aruble.net/api/adgate/check?placement=faucet',
    string $ad_url = ''
): array {
    slow("1. Checking AdGate...\r");
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => $check_url, CURLOPT_RETURNTRANSFER => true,
        CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => [
            'x-requested-with: XMLHttpRequest',
            'User-Agent: ' . $api,
            'sec-ch-ua-full-version: "149.0.7827.197"',
        ],
    ]);
    $response = curl_exec($curl); curl_close($curl);
    $data = json_decode($response, true);
    $wait = (int)($data['min_wait'] ?? 0) + 2;
    slow("   → min_wait = {$wait} seconds\r");

    slow("2. Sending interstitial click...\r");
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/api/interstitial/click',
        CURLOPT_RETURNTRANSFER => true, CURLOPT_CUSTOMREQUEST => 'POST',
        CURLOPT_POSTFIELDS => ['ad_index'=>'0','ad_url'=>$ad_url,'page_path'=>$page_path],
        CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => [
            'x-requested-with: XMLHttpRequest', 'User-Agent: ' . $api,
            'sec-ch-ua-full-version: "149.0.7827.197"',
        ],
    ]);
    $response = curl_exec($curl); curl_close($curl);
    $data = json_decode($response, true);
    $click_id = $data['click_id'] ?? null;
    if (!$click_id) { slow("   → ERROR: click_id not received\r"); return $data ?? []; }
    slow("   → click_id = {$click_id}\r");
    slow("3. Waiting {$wait} seconds...\r");
    sleep($wait);

    slow("4. Sending interstitial return...\r");
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/api/interstitial/return',
        CURLOPT_RETURNTRANSFER => true, CURLOPT_CUSTOMREQUEST => 'POST',
        CURLOPT_POSTFIELDS => ['click_id'=>$click_id,'duration'=>$wait],
        CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => [
            'x-requested-with: XMLHttpRequest', 'User-Agent: ' . $api,
            'sec-ch-ua-full-version: "149.0.7827.197"',
        ],
    ]);
    $response = curl_exec($curl); curl_close($curl);

    slow("5. Completing AdGate...\r");
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/api/adgate/complete',
        CURLOPT_RETURNTRANSFER => true, CURLOPT_CUSTOMREQUEST => 'POST',
        CURLOPT_POSTFIELDS => ['placement'=>$placement,'click_id'=>$click_id],
        CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => [
            'x-requested-with: XMLHttpRequest', 'User-Agent: ' . $api,
            'sec-ch-ua-full-version: "149.0.7827.197"',
        ],
    ]);
    $response = curl_exec($curl); curl_close($curl);
    $data = json_decode($response, true);
    slow("Done.\r");
    return $data ?? [];
}

function botCheckSignal($path, $api) {
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/bot-check/signal',
        CURLOPT_RETURNTRANSFER => true, CURLOPT_CUSTOMREQUEST => 'POST',
        CURLOPT_POSTFIELDS => [
            'mouse'=>rand(8,25),'keyboard'=>rand(0,4),'scroll'=>rand(3,12),
            'touch'=>rand(2,8),'elapsed'=>rand(20000,80000),'mouse_linear'=>rand(0,3),
            'direct_clicks'=>rand(1,3),'integrity'=>'','path'=>$path,
        ],
        CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => [
            'x-requested-with: XMLHttpRequest', 'User-Agent: ' . $api,
            'sec-ch-ua-full-version: "149.0.7827.197"',
        ],
    ]);
    $response = curl_exec($curl); curl_close($curl);
    return $response;
}

function aruble($csrf, $api = null, $path = '/faucet') {
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/bot-check/signal',
        CURLOPT_RETURNTRANSFER => true, CURLOPT_CUSTOMREQUEST => 'POST',
        CURLOPT_POSTFIELDS => [
            'mouse'=>rand(8,25),'keyboard'=>rand(0,4),'scroll'=>rand(3,12),
            'touch'=>rand(2,8),'elapsed'=>rand(20000,80000),'mouse_linear'=>rand(0,3),
            'direct_clicks'=>rand(1,3),'integrity'=>'','path'=>$path,
        ],
        CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => [
            'x-requested-with: XMLHttpRequest', 'User-Agent: ' . $api,
            'sec-ch-ua-full-version: "149.0.7827.197"',
        ],
    ]);
    $res = curl_exec($curl);
    if ($res === false || curl_errno($curl)) { curl_close($curl); return null; }
    curl_close($curl);

    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/captcha/challenge',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
        CURLOPT_HTTPHEADER => ['x-requested-with: XMLHttpRequest', 'user-agent: ' . $api],
    ]);
    $res = curl_exec($curl);
    if ($res === false || curl_errno($curl)) { curl_close($curl); return null; }
    slow("Result  challenge\r"); curl_close($curl);

    $data = json_decode($res, true);
    if (!$data) return null;

    if (!empty($data['gate_required'])) {
        usleep(($data['hold_ms'] ?? 1000) * 1000);
        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://aruble.net/captcha/gate/start',
            CURLOPT_RETURNTRANSFER => true, CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => "_csrf_token=$csrf",
            CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
        ]);
        $response = curl_exec($curl);
        if ($response === false || curl_errno($curl)) { curl_close($curl); return null; }
        slow("Result  gate/start\r"); curl_close($curl);
        $gate = json_decode($response, true);
        if (empty($gate['success'])) return null;

        usleep($gate['hold_ms'] * 1000);
        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://aruble.net/captcha/gate/complete',
            CURLOPT_RETURNTRANSFER => true, CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => http_build_query([
                'gate_key' => $gate['gate_key'], 'moves' => rand(40,60), '_csrf_token' => $csrf
            ]),
            CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
        ]);
        $response = curl_exec($curl);
        if ($response === false || curl_errno($curl)) { curl_close($curl); return null; }
        curl_close($curl);
        slow("Result  gate/complete\r");
        $complete = json_decode($response, true);
        if (empty($complete['success'])) return null;

        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://aruble.net/captcha/challenge',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
        ]);
        $res = curl_exec($curl);
        if ($res === false || curl_errno($curl)) { curl_close($curl); return null; }
        slow("Result  captcha/challenge\r"); curl_close($curl);
        $data = json_decode($res, true);
        if (!$data) return null;
    }

    $key = $data['key'] ?? null;
    $type = $data['type'] ?? null;
    if (!$key || !$type) return null;

    $answer = ""; $solve_time = 0;

    if ($type == "least_repeat") {
        $icons = [];
        foreach ($data['grid'] as $item) { $icons[$item['icon']][] = $item['id']; }
        asort($icons);
        $answer = $icons[array_key_first($icons)][0];
        $solve_time = rand(20000, 50000);
    } elseif ($type == "slide") {
        $target = $data['target_pct'];
        $answer = $target + rand(2, 5);
        $solve_time = rand(4000, 8000);
    } elseif ($type == "icon_order") {
        $map = [];
        foreach ($data['display'] as $item) { $map[$item['icon']] = $item['id']; }
        $answerArr = [];
        foreach ($data['prompt'] as $icon) { $answerArr[] = $map[$icon]; }
        $answer = json_encode($answerArr);
        $solve_time = rand(20000, 40000);
    } elseif ($type == "drag_dot") {
        $answer = json_encode(["x"=>$data['target_x'],"y"=>$data['target_y']]);
        $solve_time = rand(5000, 10000);
    } else { return null; }

    usleep($solve_time);

    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/captcha/verify',
        CURLOPT_RETURNTRANSFER => true, CURLOPT_CUSTOMREQUEST => 'POST',
        CURLOPT_POSTFIELDS => "key=$key&answer=" . urlencode($answer) . "&_csrf_token=$csrf",
        CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
    ]);
    $response = curl_exec($curl);
    if ($response === false || curl_errno($curl)) { curl_close($curl); return null; }
    slow("Result  captcha/verify\r"); curl_close($curl);

    $result = json_decode($response, true);
    if (empty($result['success']) || empty($result['token'])) return null;
    slow("Result  $answer\r");
    return $result['token'];
}

function curl($url, $post = 0, $httpheader = 0, $proxy = 0) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 30);
    curl_setopt($ch, CURLOPT_TIMEOUT, 60);
    if ($post) { curl_setopt($ch, CURLOPT_POST, true); curl_setopt($ch, CURLOPT_POSTFIELDS, $post); }
    if ($httpheader) { curl_setopt($ch, CURLOPT_HTTPHEADER, $httpheader); }
    if ($proxy) { curl_setopt($ch, CURLOPT_HTTPPROXYTUNNEL, true); curl_setopt($ch, CURLOPT_PROXY, $proxy); }
    curl_setopt($ch, CURLOPT_HEADER, true);
    $response = curl_exec($ch);
    $httpcode = curl_getinfo($ch);
    if (!$httpcode) return "Curl Error: " . curl_error($ch);
    else {
        $header = substr($response, 0, curl_getinfo($ch, CURLINFO_HEADER_SIZE));
        $body = substr($response, curl_getinfo($ch, CURLINFO_HEADER_SIZE));
        curl_close($ch);
        return array($header, $body);
    }
}

function get($url) { return curl($url, null, head())[1]; }
function post($url, $data) { return curl($url, $data, head())[1]; }

// ===== FARMING FUNCTION =====
function startFarming() {
    global $R, $CYN, $WHT, $GRN, $YEL, $RED;

    $email = Save("Email");
    $pass = Save("Password");
    $api = Save("user-agent");

    @system("clear");
    printBanner();
    echo "\n" . $CYN . "  🚜 Starting farming...\n" . $R;
    sleep(1);

    $yellow = "\033[1;33m";
    $reset = "\033[0m";

    login:
    unlink("cookie.txt");
    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net',
        CURLOPT_RETURNTRANSFER => true, CURLOPT_ENCODING => '',
        CURLOPT_MAXREDIRS => 10, CURLOPT_TIMEOUT => 30,
        CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
        CURLOPT_CUSTOMREQUEST => 'GET',
        CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_HTTPHEADER => [
            'User-Agent: '.$api, 'cache-control: max-age=0',
            'sec-ch-ua: "Chromium";v="146", "Not-A.Brand";v="24", "Android WebView";v="146"',
            'sec-ch-ua-mobile: ?1', 'sec-ch-ua-platform: "Android"',
            'upgrade-insecure-requests: 1', 'x-requested-with: XMLHttpRequest',
            'sec-fetch-site: none', 'sec-fetch-mode: navigate',
            'sec-fetch-user: ?1', 'sec-fetch-dest: document',
            'accept-language: en-GB,en-US;q=0.9,en;q=0.8', 'priority: u=0, i',
        ],
    ]);
    $res = curl_exec($curl);
    $csrf = explode('">', explode('<meta name="csrf-token" content="', $res)[1])[0];
    $token = aruble($csrf, $api, '/login');
    if (!$token) { goto login; }

    $curl = curl_init();
    curl_setopt_array($curl, [
        CURLOPT_URL => 'https://aruble.net/api/auth/login',
        CURLOPT_RETURNTRANSFER => true, CURLOPT_ENCODING => '',
        CURLOPT_MAXREDIRS => 10, CURLOPT_TIMEOUT => 30,
        CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
        CURLOPT_CUSTOMREQUEST => 'POST',
        CURLOPT_POSTFIELDS => "_csrf_token=$csrf&email=$email&password=$pass&captcha_token=$token&remember_me=1&device_fingerprint=0d2be167b01027c02ec8e88326aaa91d26c20f1794b4c221d905fa603846c7c3",
        CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
        CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_HTTPHEADER => [
            'User-Agent: '.$api, 'sec-ch-ua-platform: "Android"',
            'x-requested-with: XMLHttpRequest',
            'sec-ch-ua: "Chromium";v="146", "Not-A.Brand";v="24", "Android WebView";v="146"',
            'content-type: application/x-www-form-urlencoded; charset=UTF-8',
            'sec-ch-ua-mobile: ?1', 'origin: https://aruble.net',
            'sec-fetch-site: same-origin', 'sec-fetch-mode: cors',
            'sec-fetch-dest: empty', 'referer: https://aruble.net/',
            'accept-language: en-GB,en-US;q=0.9,en;q=0.8', 'priority: u=1, i',
        ],
    ]);
    $response = curl_exec($curl);
    $data = json_decode($response, true);
    if ($data && ($data['success'] ?? false)) {
        $message = $data['message'];
        slow("✓ Login: $message\r");
        sleep(2);
    }

    challenge:
    while (true) {
        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://aruble.net/challenge',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
            CURLOPT_HTTPHEADER => [
                'x-requested-with: XMLHttpRequest', 'User-Agent: '.$api,
                'sec-ch-ua-full-version: "149.0.7827.197"',
            ],
        ]);
        $res = curl_exec($curl);
        sleep(rand(2,5));
        $csrf = explode('">', explode('<meta name="csrf-token" content="', $res)[1])[0];
        $title = explode('</title>', explode('<title>', $res)[1])[0];
        if ($title == "Just a moment...") { slow("answer $title\r"); sleep(300); continue; }
        if (stripos($res, '<title>Redirecting...</title>') !== false || stripos($res, 'Please login') !== false) { goto login; }
        if (preg_match('/"remaining_seconds"\s*:\s*(\d+)/', $res, $m)) { goto login; }
        if (!preg_match('/onclick="claimChallenge\((\d+),\s*this\)"/i', $res, $m)) { goto Daily; }
        $claimid = $m[1];

        botCheckSignal('/challenge', $api);
        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://aruble.net/challenge/claim',
            CURLOPT_RETURNTRANSFER => true, CURLOPT_ENCODING => '',
            CURLOPT_MAXREDIRS => 10, CURLOPT_TIMEOUT => 20,
            CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1, CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => http_build_query(['challenge_id'=>$claimid,'_csrf_token'=>$csrf]),
            CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_CONNECTTIMEOUT => 8,
            CURLOPT_HTTPHEADER => [
                'User-Agent: '.$api, 'Accept: application/json, text/javascript, */*; q=0.01',
                'sec-ch-ua-platform: "Android"', 'x-requested-with: XMLHttpRequest',
                'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
                'content-type: application/x-www-form-urlencoded; charset=UTF-8',
                'sec-ch-ua-mobile: ?1', 'origin: https://aruble.net',
                'sec-fetch-site: same-origin', 'sec-fetch-mode: cors',
                'sec-fetch-dest: empty', 'referer: https://aruble.net/challenge',
                'accept-language: en-GB,en-US;q=0.9,en;q=0.8', 'priority: u=1, i',
            ],
        ]);
        $res = curl_exec($curl);
        curl_close($curl);
        $data = json_decode($res, true);
        if (isset($data['message']) && $data['message'] === "Invalid session. Please go back and try again.") { goto login; }
        if (isset($data['message']) && $data['message'] === "Please login") { goto login; }
        if ($data && ($data['success'] ?? false)) {
            printClaim("CHALLENGE", "🎁", [
                "⏰ " . date("h:i:s A"),
                "🎁 Challenge : " . ($data['challenge_name'] ?? '?'),
                "💰 Reward    : +" . ($data['reward'] ?? '?') . " Coins",
                "✅ " . ($data['message'] ?? ''),
            ]);
        }
    }

    Daily:
    while (true) {
        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://aruble.net/daily-bonus',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
            CURLOPT_HTTPHEADER => [
                'x-requested-with: XMLHttpRequest', 'User-Agent: '.$api,
                'sec-ch-ua-full-version: "149.0.7827.197"',
            ],
        ]);
        $res = curl_exec($curl);
        $csrf = explode('">', explode('<meta name="csrf-token" content="', $res)[1])[0];
        $title = explode('</title>', explode('<title>', $res)[1])[0];
        if ($title == "Just a moment...") { slow("answer $title\r"); sleep(300); continue; }
        if (stripos($res, '<title>Redirecting...</title>') !== false || stripos($res, 'Please login') !== false) { goto login; }
        if (preg_match('/"remaining_seconds"\s*:\s*(\d+)/', $res, $m)) { goto login; }
        if (strpos($res, 'Come Back Later') !== false) { goto Spin; }
        $token = aruble($csrf, $api, '/daily-bonus');
        if (!$token) continue;

        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://aruble.net/daily-bonus/claim',
            CURLOPT_RETURNTRANSFER => true, CURLOPT_ENCODING => '',
            CURLOPT_MAXREDIRS => 10, CURLOPT_TIMEOUT => 20,
            CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
            CURLOPT_CUSTOMREQUEST => 'POST',
            CURLOPT_POSTFIELDS => "captcha_token=$token&_csrf_token=$csrf",
            CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_CONNECTTIMEOUT => 8,
            CURLOPT_HTTPHEADER => [
                'User-Agent: '.$api, 'sec-ch-ua-platform: "Android"',
                'x-requested-with: XMLHttpRequest',
                'sec-ch-ua: "Chromium";v="146", "Not-A.Brand";v="24", "Android WebView";v="146"',
                'content-type: application/x-www-form-urlencoded; charset=UTF-8',
                'sec-ch-ua-mobile: ?1', 'origin: https://aruble.net',
                'sec-fetch-site: same-origin', 'sec-fetch-mode: cors',
                'sec-fetch-dest: empty', 'referer: https://aruble.net/daily-bonus',
                'accept-language: en-GB,en-US;q=0.9,en;q=0.8', 'priority: u=1, i',
            ],
        ]);
        $res = curl_exec($curl);
        $data = json_decode($res, true);
        if ($data && ($data['success'] ?? false) === false) {
            $message = $data['message'] ?? '';
            if (strpos($message, 'You need 10 more faucet claims today before collecting your bonus') !== false) { goto Spin; }
        }
        if (isset($data['message']) && $data['message'] === "Invalid session. Please go back and try again.") { goto login; }
        if (isset($data['message']) && $data['message'] === "Please login") { goto login; }
        if ($data && ($data['success'] ?? false)) {
            printClaim("DAILY BONUS", "🎁", [
                "⏰ " . date("h:i:s A"),
                ($data['icon'] ?? '🎁') . " Reward  : +" . ($data['amount'] ?? '?') . " " . ($data['symbol'] ?? ''),
                "🔥 Streak  : " . ($data['streak'] ?? '?'),
                "💰 Balance : " . ($data['balance_after'] ?? '?'),
                "🎯 Next    : " . ($data['next_reward'] ?? '?') . " " . ($data['symbol'] ?? ''),
            ]);
        }
        goto Spin;
    }

    Spin:
    while (true) {
        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://aruble.net/spin',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
            CURLOPT_HTTPHEADER => [
                'x-requested-with: XMLHttpRequest', 'User-Agent: '.$api,
                'sec-ch-ua-full-version: "149.0.7827.197"',
            ],
        ]);
        $res = curl_exec($curl);
        $csrf = explode('">', explode('<meta name="csrf-token" content="', $res)[1])[0];
        $title = explode('</title>', explode('<title>', $res)[1])[0];
        if ($title == "Just a moment...") { slow("answer $title\r"); sleep(300); continue; }
        if (stripos($res, '<title>Redirecting...</title>') !== false || stripos($res, 'Please login') !== false) { goto login; }
        if (preg_match('/"remaining_seconds"\s*:\s*(\d+)/', $res, $m)) { goto login; }
        if (strpos($res, 'No Spins Available') !== false) { goto faucet; }

        $token = aruble($csrf, $api, '/spin');
        if (!$token) continue;

        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://aruble.net/spin/claim',
            CURLOPT_RETURNTRANSFER => true, CURLOPT_ENCODING => '',
            CURLOPT_MAXREDIRS => 10, CURLOPT_TIMEOUT => 20,
            CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
            CURLOPT_CUSTOMREQUEST => 'POST',
            CURLOPT_POSTFIELDS => "captcha_token=$token&_csrf_token=$csrf",
            CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_CONNECTTIMEOUT => 8,
            CURLOPT_HTTPHEADER => [
                'User-Agent: '.$api, 'sec-ch-ua-platform: "Android"',
                'x-requested-with: XMLHttpRequest',
                'sec-ch-ua: "Chromium";v="146", "Not-A.Brand";v="24", "Android WebView";v="146"',
                'content-type: application/x-www-form-urlencoded; charset=UTF-8',
                'sec-ch-ua-mobile: ?1', 'origin: https://aruble.net',
                'sec-fetch-site: same-origin', 'sec-fetch-mode: cors',
                'sec-fetch-dest: empty', 'referer: https://aruble.net/spin',
                'accept-language: en-GB,en-US;q=0.9,en;q=0.8', 'priority: u=1, i',
            ],
        ]);
        $res = curl_exec($curl);
        $data = json_decode($res, true);
        if (isset($data['message']) && $data['message'] === "Invalid session. Please go back and try again.") { goto login; }
        if (isset($data['message']) && $data['message'] === "Please login") { goto login; }
        if ($data && ($data['success'] ?? false)) {
            printClaim("SPIN", ($data['icon'] ?? '🎰'), [
                "⏰ " . date("h:i:s A"),
                ($data['icon'] ?? '🎰') . " Label    : " . ($data['label'] ?? '?'),
                "🎁 Reward  : +" . ($data['reward'] ?? '?') . " COINS",
                "💰 Balance : " . ($data['new_balance'] ?? '?'),
                "🎯 Spins   : " . ($data['spins_left'] ?? '?'),
                "⏳ Next    : " . fmtNext($data['next_spin_in'] ?? 0),
            ]);
        }
    }

    faucet:
    while (true) {
        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://aruble.net/faucet',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
            CURLOPT_HTTPHEADER => [
                'x-requested-with: XMLHttpRequest', 'User-Agent: '.$api,
                'sec-ch-ua-full-version: "149.0.7827.197"',
            ],
        ]);
        $res = curl_exec($curl);
        sleep(rand(2,5));
        $csrf = explode('">', explode('<meta name="csrf-token" content="', $res)[1])[0];
        $title = explode('</title>', explode('<title>', $res)[1])[0];
        if ($title == "Just a moment...") { slow("answer $title\r"); sleep(300); continue; }
        if (stripos($res, '<title>Redirecting...</title>') !== false || stripos($res, 'Please login') !== false) { goto login; }
        if (preg_match('/"remaining_seconds"\s*:\s*(\d+)/', $res, $m)) { goto login; }
        if (preg_match('/globalCooldown\s*:\s*(\d+)/', $res, $m)) {
            $cooldownF = $m[1];
            if ($cooldownF > 0) { timer($cooldownF + rand(5,15)); continue; }
        }

        $result = runAdGate(
            $api, 'faucet', '/faucet',
            'https://aruble.net/api/adgate/check?placement=faucet',
            'https://cdn.bmcdn6.com/p/6aa08666932548d934c3873f/?source=...'
        );
        if (empty($result)) { slow("Result empty → Retrying...\r"); sleep(2); continue; }
        $token = aruble($csrf, $api, '/faucet');
        if (!$token) continue;

        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://aruble.net/faucet/claim',
            CURLOPT_RETURNTRANSFER => true, CURLOPT_ENCODING => '',
            CURLOPT_MAXREDIRS => 10, CURLOPT_TIMEOUT => 20,
            CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
            CURLOPT_CUSTOMREQUEST => 'POST',
            CURLOPT_POSTFIELDS => "dest=account&wc_id=0&captcha_token=$token&fp=0d2be167b01027c02ec8e88326aaa91d26c20f1794b4c221d905fa603846c7c3&_csrf_token=$csrf",
            CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_CONNECTTIMEOUT => 8,
            CURLOPT_HTTPHEADER => [
                'User-Agent: '.$api, 'Accept: application/json, text/javascript, */*; q=0.01',
                'sec-ch-ua-platform: "Android"', 'x-requested-with: XMLHttpRequest',
                'sec-ch-ua: "Chromium";v="146", "Not-A.Brand";v="24", "Android WebView";v="146"',
                'content-type: application/x-www-form-urlencoded; charset=UTF-8',
                'sec-ch-ua-mobile: ?1', 'origin: https://aruble.net',
                'sec-fetch-site: same-origin', 'sec-fetch-mode: cors',
                'sec-fetch-dest: empty', 'referer: https://aruble.net/faucet',
                'accept-language: en-GB,en-US;q=0.9,en;q=0.8', 'priority: u=1, i',
            ],
        ]);
        $res = curl_exec($curl);
        $data = json_decode($res, true);
        if ($data && ($data['success'] ?? false) === false) {
            $msg = $data['message'] ?? '';
            if (strpos($msg, 'daily limit') !== false) {
                echo $RED . "🚫 " . $msg . "\n" . $R;
                exit;
            }
        }
        if (isset($data['message']) && $data['message'] === "Invalid session. Please go back and try again.") { goto login; }
        if (isset($data['message']) && $data['message'] === "Please login") { goto login; }
        if ($data && ($data['success'] ?? false)) {
            printClaim("CLAIM", "🎁", [
                "⏰ " . date("h:i:s A"),
                "🎁 Reward : +" . ($data['amount'] ?? '?') . " " . ($data['symbol'] ?? ''),
                "💰 Balance: " . ($data['balance_after'] ?? '?'),
                "📊 Claim  : " . ($data['claims_today'] ?? '?') . "/" . ($data['claims_max'] ?? '?'),
                "⏳ Next   : " . fmtNext($data['next_claim_in'] ?? 0),
            ]);
            goto auto;
        }
    }

    auto:
    while (true) {
        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://aruble.net/auto',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
            CURLOPT_HTTPHEADER => [
                'x-requested-with: XMLHttpRequest', 'User-Agent: '.$api,
                'sec-ch-ua-full-version: "149.0.7827.197"',
            ],
        ]);
        $res = curl_exec($curl);
        $csrf = explode('">', explode('<meta name="csrf-token" content="', $res)[1])[0];
        $statNext = explode('s</div>', explode('<div class="mining-stat-value" id="statNext">', $res)[1])[0];
        $title = explode('</title>', explode('<title>', $res)[1])[0];
        if ($title == "Just a moment...") { slow("answer $title\r"); sleep(300); continue; }
        if (stripos($res, '<title>Redirecting...</title>') !== false || stripos($res, 'Please login') !== false) { goto login; }
        if (preg_match('/"remaining_seconds"\s*:\s*(\d+)/', $res, $m)) { goto login; }

        botCheckSignal('/auto', $api);
        preg_match('/currentEnergy\s*:\s*(\d+)/', $res, $energy);
        preg_match('/energyCost\s*:\s*(\d+)/', $res, $cost);
        $currentEnergy = $energy[1] ?? 0;
        $energyCost = $cost[1] ?? 10;
        if ($currentEnergy < $energyCost) { goto roll; }

        timer($statNext);

        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://aruble.net/auto/burn',
            CURLOPT_RETURNTRANSFER => true, CURLOPT_ENCODING => '',
            CURLOPT_MAXREDIRS => 10, CURLOPT_TIMEOUT => 20,
            CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
            CURLOPT_CUSTOMREQUEST => 'POST',
            CURLOPT_POSTFIELDS => "_csrf_token=$csrf",
            CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_CONNECTTIMEOUT => 8,
            CURLOPT_HTTPHEADER => [
                'User-Agent: '.$api, 'sec-ch-ua-platform: "Android"',
                'x-requested-with: XMLHttpRequest',
                'sec-ch-ua: "Chromium";v="146", "Not-A.Brand";v="24", "Android WebView";v="146"',
                'content-type: application/x-www-form-urlencoded; charset=UTF-8',
                'sec-ch-ua-mobile: ?1', 'origin: https://aruble.net',
                'sec-fetch-site: same-origin', 'sec-fetch-mode: cors',
                'sec-fetch-dest: empty', 'referer: https://aruble.net/auto',
                'accept-language: en-GB,en-US;q=0.9,en;q=0.8', 'priority: u=1, i',
            ],
        ]);
        $res = curl_exec($curl);
        $data = json_decode($res, true);
        if (isset($data['message']) && $data['message'] === "Invalid session. Please go back and try again.") { goto login; }
        if (isset($data['message']) && $data['message'] === "Please login") { goto login; }
        if ($data && ($data['success'] ?? false)) {
            printClaim("AUTO MINING", "⛏️", [
                "⏰ " . date("h:i:s A"),
                "⚡ Energy : -" . ($data['energy_spent'] ?? '?'),
                ($data['coin_icon'] ?? '💰') . " Reward : +" . ($data['coins_earned'] ?? '?') . " " . ($data['coin_symbol'] ?? ''),
                "💰 Balance: " . ($data['balance_after'] ?? '?'),
                "⚡ After  : " . ($data['energy_after'] ?? '?'),
                "📈 Mult   : x" . ($data['multiplier'] ?? '1') . " | 🎁 " . ($data['bonus_pct'] ?? '0') . "%",
            ]);
        }
    }

    roll:
    while (true) {
        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://aruble.net/bonus-roll',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_TIMEOUT => 20, CURLOPT_CONNECTTIMEOUT => 8,
            CURLOPT_HTTPHEADER => [
                'x-requested-with: XMLHttpRequest', 'User-Agent: '.$api,
                'sec-ch-ua-full-version: "149.0.7827.197"',
            ],
        ]);
        $res = curl_exec($curl);
        $csrf = explode('">', explode('<meta name="csrf-token" content="', $res)[1])[0];
        $title = explode('</title>', explode('<title>', $res)[1])[0];
        if ($title == "Just a moment...") { slow("answer $title\r"); sleep(300); continue; }
        if (stripos($res, '<title>Redirecting...</title>') !== false || stripos($res, 'Please login') !== false) { goto login; }
        if (preg_match('/"remaining_seconds"\s*:\s*(\d+)/', $res, $m)) { goto login; }
        if (stripos($res, 'On Cooldown') !== false) { timer(60); goto faucet; }

        $token = aruble($csrf, $api, '/bonus-roll');
        if (!$token) continue;

        $curl = curl_init();
        curl_setopt_array($curl, [
            CURLOPT_URL => 'https://aruble.net/bonus-roll/claim',
            CURLOPT_RETURNTRANSFER => true, CURLOPT_ENCODING => '',
            CURLOPT_MAXREDIRS => 10, CURLOPT_TIMEOUT => 20,
            CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
            CURLOPT_CUSTOMREQUEST => 'POST',
            CURLOPT_POSTFIELDS => "captcha_token=$token&_csrf_token=$csrf",
            CURLOPT_COOKIEJAR => 'cookie.txt', CURLOPT_COOKIEFILE => 'cookie.txt',
            CURLOPT_SSL_VERIFYPEER => false, CURLOPT_SSL_VERIFYHOST => false,
            CURLOPT_CONNECTTIMEOUT => 8,
            CURLOPT_HTTPHEADER => [
                'User-Agent: '.$api, 'sec-ch-ua-platform: "Android"',
                'x-requested-with: XMLHttpRequest',
                'sec-ch-ua: "Chromium";v="146", "Not-A.Brand";v="24", "Android WebView";v="146"',
                'content-type: application/x-www-form-urlencoded; charset=UTF-8',
                'sec-ch-ua-mobile: ?1', 'origin: https://aruble.net',
                'sec-fetch-site: same-origin', 'sec-fetch-mode: cors',
                'sec-fetch-dest: empty', 'referer: https://aruble.net/bonus-roll',
                'accept-language: en-GB,en-US;q=0.9,en;q=0.8', 'priority: u=1, i',
            ],
        ]);
        $res = curl_exec($curl);
        $data = json_decode($res, true);
        if (isset($data['message']) && $data['message'] === "Invalid session. Please go back and try again.") { goto login; }
        if (isset($data['message']) && $data['message'] === "Please login") { goto login; }
        if ($data && ($data['success'] ?? false)) {
            printClaim("BONUS ROLL", "🎲", [
                "⏰ " . date("h:i:s A"),
                "🎲 Drawn  : " . ($data['number_drawn'] ?? '?'),
                "🏆 Label  : " . strip_tags($data['label'] ?? '?'),
                "⚡ Reward : +" . ($data['reward'] ?? '?'),
                "💰 Balance: " . ($data['new_token_balance'] ?? '?'),
                "⏳ Next   : " . fmtNext($data['next_roll_in'] ?? 0),
            ]);
            timer(60);
            goto faucet;
        }
    }
}

// ===== MAIN LOOP =====
while (true) {
    showMenu();
    $opt = trim(fgets(STDIN));
    switch ($opt) {
        case '1':
            startFarming();
            break;
        case '2':
            cfg_set('Email', '📧 Email');
            break;
        case '3':
            cfg_set('Password', '🔐 Password');
            break;
        case '4':
            cfg_set('user-agent', '📱 User-Agent');
            break;
        case '0':
            @system("clear");
            echo "\n\033[1;33m  👋 Bye bos...\033[0m\n\n";
            exit;
        default:
            echo "\n\033[1;31m  ✗ Pilihan gak ada, coba lagi...\033[0m\n";
            sleep(1);
    }
}
