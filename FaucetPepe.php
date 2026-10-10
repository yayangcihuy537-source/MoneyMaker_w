<?php

error_reporting(0);
ini_set('display_errors', 0);
date_default_timezone_set('Asia/Jakarta');

$configFile     = "config_pepe.json";
$waryonoFile    = "waryono.txt";
$alljrlwrFile   = "alljrlwr.txt";

$host    = "faucetpepe.xyz";
$apiWary = "https://api.waryono.my.id";
$apiAllj = "https://api.alljrlwr.my.id";

$HCAPTCHA_SITEKEY = "8f60a5ea-4548-47fc-8ba6-9f027142b92a";
$ADSLAB_SITEKEY   = "QzTpYWxuTTo6uviTuyFFkrHVOI171eXA2B2rNq4c";

$hitam  = "\033[0;30m";
$merah  = "\033[0;31m";
$hijau  = "\033[0;32m";
$kuning = "\033[0;33m";
$biru   = "\033[0;34m";
$cyan   = "\033[0;36m";
$putih  = "\033[0;37m";
$reset  = "\033[0m";
$bold   = "\033[1m";
$ungu   = "\033[95m";

$orange_btc = "\033[38;5;214m";
$grey_eth   = "\033[38;5;252m";
$yellow_dog = "\033[38;5;220m";
$grey_ltc   = "\033[38;5;250m";
$green_usdt = "\033[38;5;48m";
$blue_ada   = "\033[38;5;33m";
$blue_xrp   = "\033[38;5;39m";
$orange_bch = "\033[38;5;208m";
$purple_sol = "\033[38;5;135m";
$pink_dot   = "\033[38;5;205m";
$yellow_dai = "\033[38;5;226m";
$orange_xmr = "\033[38;5;202m";
$blue_xtz   = "\033[38;5;27m";
$orange_zec = "\033[38;5;215m";
$white_xlm  = "\033[1;37m";
$red_trx    = "\033[38;5;196m";
$blue_dash  = "\033[38;5;27m";

function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function check_api_balance($provider = "alljrlwr") {
    $api_balance = "N/A";
    if ($provider === "alljrlwr" && file_exists("alljrlwr.txt") && trim(file_get_contents("alljrlwr.txt")) !== "") {
        $key = trim(file_get_contents("alljrlwr.txt"));
        $res = @json_decode(@file_get_contents("https://api.alljrlwr.my.id/res.php?action=userinfo&key=$key&json=1"), true);
        $api_balance = $res["balance"] ?? ($res["data"]["balance"] ?? "Ready");
    } elseif ($provider === "waryono" && file_exists("waryono.txt") && trim(file_get_contents("waryono.txt")) !== "") {
        $key = trim(file_get_contents("waryono.txt"));
        $res = @json_decode(@file_get_contents("https://api.waryono.my.id/balance.php?apikey=$key"), true);
        $api_balance = $res["balance"] ?? "Ready";
    }
    return $api_balance;
}

function skibidixxx($url, $method = 'GET', $data = [], $headers = []) {
    $ch = curl_init();
    $final_headers = [];
    foreach ($headers as $header) {
        $final_headers[] = $header;
    }
    $options = [
        CURLOPT_URL            => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER         => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_SSL_VERIFYHOST => 2,
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_HTTPHEADER     => $final_headers,
        CURLOPT_COOKIEJAR      => 'cookie_pepe.txt',
        CURLOPT_COOKIEFILE     => 'cookie_pepe.txt',
        CURLOPT_CONNECTTIMEOUT => 30,
        CURLOPT_TIMEOUT        => 30
    ];
    if (strtoupper($method) === 'POST') {
        $options[CURLOPT_POST] = true;
        $options[CURLOPT_POSTFIELDS] = $data;
    }
    curl_setopt_array($ch, $options);
    $response = curl_exec($ch);
    $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $body = substr($response, $header_size);
    return $body;
}

function fixedCooldownTimer($seconds = 15) {
    global $putih, $hijau;
    $wait_time = (int)$seconds;
    $elapsed = 0;
    $frames = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘'];
    $clocks = ['🕛', '🕐', '🕑', '🕒', '肆', '🕔', '🕕', '🕖', '🕗', '🕘', '⑩', '🕚'];
    $frame_count = count($frames);
    $clock_count = count($clocks);
    $current_frame = 0;
    $current_clock = 0;
    
    while ($elapsed < $wait_time) {
        $start_time = microtime(true);
        while ((microtime(true) - $start_time) < 1) {
            $remaining = $wait_time - $elapsed;
            $time_formatted = sprintf('00:00:%02d', $remaining);
            
            $spinner = $frames[$current_frame];
            $clock   = $clocks[$current_clock];
            
            echo "\r\033[K " . $clock . " " . $putih . "MENUNGGU COOLDOWN" . $hijau . " $time_formatted " . $spinner;
            usleep(150000);
            $current_frame = ($current_frame + 1) % $frame_count;
            $current_clock = ($current_clock + 1) % $clock_count;
            if ((microtime(true) - $start_time) >= 1) break;
        }
        $elapsed++;
    }
    echo "\r\033[K";
}

function pollingTimer($seconds, $prefix = "MENYELESAIKAN CAPTCHA") {
    global $putih, $hijau;
    $wait_time = (int)$seconds;
    $elapsed = 0;
    $frames = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘'];
    $clocks = ['🕛', '🕐', '🕑', '🕒', '🕔', '🕕', '🕖', '🕗', '🕘', '🕚'];
    $frame_count = count($frames);
    $clock_count = count($clocks);
    $current_frame = 0;
    $current_clock = 0;
    
    while ($elapsed < $wait_time) {
        $start_time = microtime(true);
        while ((microtime(true) - $start_time) < 1) {
            $hours = floor($elapsed / 3600);
            $minutes = floor(($elapsed % 3600) / 60);
            $seconds_left = $elapsed % 60;
            $time_formatted = sprintf('%02d:%02d:%02d', $hours, $minutes, $seconds_left);
            
            $spinner = $frames[$current_frame];
            $clock   = $clocks[$current_clock];
            
            echo "\r\033[K " . $clock . " " . $putih . $prefix . $hijau . " $time_formatted " . $spinner;
            usleep(150000);
            $current_frame = ($current_frame + 1) % $frame_count;
            $current_clock = ($current_clock + 1) % $clock_count;
            if ((microtime(true) - $start_time) >= 1) break;
        }
        $elapsed++;
    }
    echo "\r\033[K";
}

function getCoinStyle($coin_type) {
    global $orange_btc, $grey_eth, $yellow_dog, $grey_ltc, $green_usdt, $blue_ada, $blue_xrp, $orange_bch, $purple_sol, $pink_dot, $yellow_dai, $orange_xmr, $blue_xtz, $orange_zec, $white_xlm, $red_trx, $blue_dash, $kuning;
    
    $c_lower = strtolower($coin_type);
    switch($c_lower) {
        case 'btc': return ["symbol" => "₿", "color" => $orange_btc];
        case 'eth': return ["symbol" => "Ξ", "color" => $grey_eth];
        case 'doge': return ["symbol" => "Ð", "color" => $yellow_dog];
        case 'ltc': return ["symbol" => "Ł", "color" => $grey_ltc];
        case 'usdt': return ["symbol" => "₮", "color" => $green_usdt];
        case 'ada': return ["symbol" => "₳", "color" => $blue_ada];
        case 'xrp': return ["symbol" => "✕", "color" => $blue_xrp];
        case 'bch': return ["symbol" => "Ƀ", "color" => $orange_bch];
        case 'sol': return ["symbol" => "◎", "color" => $purple_sol];
        case 'dot': return ["symbol" => "●", "color" => $pink_dot];
        case 'dai': return ["symbol" => "◈", "color" => $yellow_dai];
        case 'xmr': return ["symbol" => "ɱ", "color" => $orange_xmr];
        case 'xtz': return ["symbol" => "ꜩ", "color" => $blue_xtz];
        case 'zec': return ["symbol" => "ⓩ", "color" => $orange_zec];
        case 'xlm': return ["symbol" => "🚀", "color" => $white_xlm];
        case 'trx': return ["symbol" => "🔻", "color" => $red_trx];
        case 'dash': return ["symbol" => "💠", "color" => $blue_dash];
        default: return ["symbol" => "🪙", "color" => $kuning];
    }
}

function banner($earned = "0", $total_coins = "0", $coin_type = "COINS") {
    global $putih, $cyan, $kuning, $hijau, $bold, $ungu, $reset;
    $earned_text = $earned . " Successful Claims";
    $clean_coins = rtrim(rtrim(number_format((float)$total_coins, 8, '.', ''), '0'), '.');
    if ($clean_coins == "" || $clean_coins == ".") $clean_coins = "0";
    
    $style = getCoinStyle($coin_type);
    $coins_text = $clean_coins . " " . strtoupper($coin_type);
    $time_text  = date('d-m-Y H:i:s');
    
    $bal_alljrlwr = check_api_balance("alljrlwr");
    $bal_waryono  = check_api_balance("waryono");

    echo $cyan . "  ==========================================\n";
    echo $cyan . "             " . $bold . $putih . "F A U C E T   P E P E" . $cyan . "\n";
    echo $cyan . "  ==========================================\n" . $reset;
    echo $bold . $ungu . "  Script by AHD1905 Supported by ScriptyXSouu\n" . $reset;
    echo $cyan . "  ┌────────────────────────────────────────┐\n";
    echo $cyan . "  │ ⏰ Waktu      : " . $kuning . str_pad($time_text, 26, ' ', STR_PAD_RIGHT) . $cyan . " │\n";
    echo $cyan . "  │ 💵 AllJrLwr   : " . $hijau . str_pad($bal_alljrlwr, 26, ' ', STR_PAD_RIGHT) . $cyan . " │\n";
    echo $cyan . "  │ 💶 Waryono    : " . $hijau . str_pad($bal_waryono, 26, ' ', STR_PAD_RIGHT) . $cyan . " │\n";
    echo $cyan . "  │ 💰 Total Claim: " . $hijau . $bold . str_pad($earned_text, 26, ' ', STR_PAD_RIGHT) . $cyan . " │\n";
    echo $cyan . "  │ " . $style["color"] . $style["symbol"] . $cyan . " Total Coin  : " . $style["color"] . $bold . str_pad($coins_text, 26, ' ', STR_PAD_RIGHT) . $cyan . " │\n";
    echo $cyan . "  └────────────────────────────────────────┘\n" . $reset;
    echo $putih . "  ------------------------------------------\n";
}

function solveHcaptchaWaryono($waryonoKey, $sitekey) {
    global $apiWary, $host, $hijau, $merah, $putih;
    $body = json_encode([
        "apikey"  => $waryonoKey,
        "methods" => "hcaptcha",
        "domain"  => $host,
        "sitekey" => $sitekey,
        "json"    => 1
    ]);

    $headers = ["Content-Type: application/json", "Accept: application/json"];
    echo $putih . "[📤] Menyelesaikan Captcha 🪧\n";
    $request = skibidixxx($apiWary . "/in.php", "POST", $body, $headers);
    
    $json = json_decode($request, true);
    if (!isset($json["request"]) || (isset($json["status"]) && $json["status"] !== 1)) {
        echo $merah . "[📥] Captcha Unsolved ⚠️\n";
        return "";
    }

    $taskId = $json["request"];

    for ($attempt = 1; $attempt <= 60; $attempt++) {
        pollingTimer(3, "MENUNGGU HCAPTCHA WARYONO");
        $pollUrl = $apiWary . "/res.php?" . http_build_query([
            'apikey' => $waryonoKey, 
            'action' => 'get',
            'id'     => $taskId, 
            'json'   => 1
        ]);
        
        $pollResponse = skibidixxx($pollUrl, 'GET', [], ["Accept: application/json"]);
        $pollData = json_decode($pollResponse, true);
        $status = $pollData['status'] ?? 0;
        $msg = $pollData['request'] ?? '';

        if ($status == 1 || $status === "1") {
            echo $hijau . "[📥] Captcha Solved 🤝\n";
            return $msg;
        }
    }
    echo $merah . "[📥] Captcha Unsolved ⚠️\n";
    return "";
}

function solveAdslabAlljrlwr($alljrlwrKey, $sitekey) {
    global $apiAllj, $host, $hijau, $merah, $putih;
    
    $postData = [
        'key'     => $alljrlwrKey,
        'method'  => 'adslab',
        'sitekey' => $sitekey,
        'domain'  => 'https://' . $host,
        'subid'   => 'widget_user',
        'json'    => 1
    ];

    echo $putih . "[📤] Menyelesaikan Captcha 🪧\n";
    $request = skibidixxx($apiAllj . '/in.php', 'POST', http_build_query($postData), [
        'Content-Type: application/x-www-form-urlencoded'
    ]);
    
    $json = json_decode($request, true);
    if (!isset($json["status"]) || $json["status"] !== 'OK') {
        echo $merah . "[📥] Captcha Unsolved ⚠️\n";
        return "";
    }

    $taskId = $json["request"];

    for ($attempt = 1; $attempt <= 60; $attempt++) {
        pollingTimer(4, "MENUNGGU ADSLAB ALLJRLWR");
        $pollUrl = $apiAllj . '/res.php?' . http_build_query([
            'key'    => $alljrlwrKey,
            'action' => 'get',
            'id'     => $taskId,
            'json'   => 1
        ]);
        
        $pollResponse = skibidixxx($pollUrl, 'GET', []);
        $pollData = json_decode($pollResponse, true);
        $status = $pollData['status'] ?? '';

        if ($status === 'OK') {
            echo $hijau . "[📥] Captcha Solved 🤝\n";
            return $pollData['result'] ?? '';
        } elseif ($status === 'CAPCHA_NOT_READY') {
            continue;
        } elseif (strpos($status, 'ERROR_') === 0) {
            echo $merah . "[📥] Captcha Unsolved ⚠️\n";
            return "";
        }
    }
    echo $merah . "[📥] Captcha Unsolved ⚠️\n";
    return "";
}

function solveAdslabWaryono($waryonoKey, $sitekey) {
    global $apiWary, $host, $hijau, $merah, $putih;
    $body = json_encode([
        "apikey"  => $waryonoKey,
        "methods" => "adslab",
        "domain"  => $host,
        "sitekey" => $sitekey,
        "subid"   => "widget_user",
        "json"    => 1
    ]);

    $headers = ["Content-Type: application/json", "Accept: application/json"];
    echo $putih . "[📤] Menyelesaikan Captcha 🪧\n";
    $request = skibidixxx($apiWary . "/in.php", "POST", $body, $headers);
    
    $json = json_decode($request, true);
    if (!isset($json["request"]) || (isset($json["status"]) && $json["status"] !== 1)) {
        echo $merah . "[📥] Captcha Unsolved ⚠️\n";
        return "";
    }

    $taskId = $json["request"];

    for ($attempt = 1; $attempt <= 60; $attempt++) {
        pollingTimer(3, "MENUNGGU ADSLAB WARYONO");
        $pollUrl = $apiWary . "/res.php?" . http_build_query([
            'apikey' => $waryonoKey, 
            'action' => 'get',
            'id'     => $taskId, 
            'json'   => 1
        ]);
        
        $pollResponse = skibidixxx($pollUrl, 'GET', [], ["Accept: application/json"]);
        $pollData = json_decode($pollResponse, true);
        $status = $pollData['status'] ?? 0;
        $msg = $pollData['request'] ?? '';

        if ($status == 1 || $status === "1") {
            echo $hijau . "[📥] Captcha Solved 🤝\n";
            return $msg;
        }
    }
    echo $merah . "[📥] Captcha Unsolved ⚠️\n";
    return "";
}

$botMode = 1; 
while (true) {
    clear();
    echo $cyan . "  ==========================================\n";
    echo $cyan . "             " . $bold . $putih . "PANEL KONFIGURASI BOT" . $cyan . "\n";
    echo $cyan . "  ==========================================\n" . $reset;
    echo $merah . $bold . "  [!] Gunakan 2 apikey sekaligus kalo tidak mending tidur!!!\n      Alljrlwr Hcaptcha stroke dan Waryono Adslab Stroke!!!!\n" . $reset;
    echo $cyan . "  ------------------------------------------\n" . $reset;
    echo $putih . "  [1] Run 2 apikey\n";
    echo $putih . "  [2] Run full waryono\n";
    echo $putih . "  [3] Apikey Alljrlwr\n";
    echo $putih . "  [4] Apikey Waryono\n";
    echo $putih . "  [5] Akun FaucetPay\n";
    echo $putih . "  [6] Hapus Config\n";
    echo $putih . "  [0] Exit\n";
    echo $cyan . "  ------------------------------------------\n" . $reset;
    echo $putih . "  Pilih opsi [0-6]: " . $kuning;
    $opt = trim(fgets(STDIN));

    if ($opt === "1") {
        $botMode = 1;
        break;
    } elseif ($opt === "2") {
        $botMode = 2;
        break;
    } elseif ($opt === "3") {
        echo $putih . "  Masukkan API Key AllJrLwr baru: " . $kuning;
        $k = trim(fgets(STDIN));
        file_put_contents($alljrlwrFile, $k);
        echo $hijau . "  [+] API Key AllJrLwr berhasil disimpan!\n" . $reset;
        sleep(1.5);
    } elseif ($opt === "4") {
        echo $putih . "  Masukkan API Key Waryono baru: " . $kuning;
        $k = trim(fgets(STDIN));
        file_put_contents($waryonoFile, $k);
        echo $hijau . "  [+] API Key Waryono berhasil disimpan!\n" . $reset;
        sleep(1.5);
    } elseif ($opt === "5") {
        echo $putih . "  Masukkan Email FaucetPay baru: " . $kuning;
        $e = trim(fgets(STDIN));
        $conf = file_exists($configFile) ? json_decode(file_get_contents($configFile), true) : [];
        $conf['email'] = $e;
        file_put_contents($configFile, json_encode($conf, JSON_PRETTY_PRINT));
        echo $hijau . "  [+] Akun FaucetPay berhasil diperbarui!\n" . $reset;
        sleep(1.5);
    } elseif ($opt === "6") {
        @unlink($configFile);
        @unlink($waryonoFile);
        @unlink($alljrlwrFile);
        @unlink("cookie_pepe.txt");
        echo $hijau . "  [+] Berhasil menghapus seluruh data konfigurasi & koin!\n" . $reset;
        sleep(1.5);
    } elseif ($opt === "0") {
        echo $kuning . "  Keluar dari bot. Sampai jumpa!\n" . $reset;
        exit;
    }
}

function getApiKey($file, $promptName) {
    global $putih, $kuning;
    if (file_exists($file)) {
        $apikey = trim(file_get_contents($file));
        if (!empty($apikey)) return $apikey;
    }
    echo $putih . "Masukkan API Key $promptName: " . $kuning;
    $apikey = trim(fgets(STDIN));
    file_put_contents($file, $apikey);
    return $apikey;
}

$apikeyWaryono  = getApiKey($waryonoFile, "Waryono");
$apikeyAlljrlwr = ($botMode == 1) ? getApiKey($alljrlwrFile, "AllJrLwr") : "";

function doLogin($apikeyWaryono, $HCAPTCHA_SITEKey, $configFile) {
    global $putih, $kuning, $merah, $hijau;
    $ua = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Mobile Safari/537.36";
    
    $email = "";
    $earned = 0;
    $total_coins = 0;
    if (file_exists($configFile)) {
        $existingConfig = json_decode(file_get_contents($configFile), true);
        if (!empty($existingConfig['email'])) {
            $email = $existingConfig['email'];
        }
        $earned = $existingConfig['earned'] ?? 0;
        $total_coins = $existingConfig['total_coins'] ?? 0;
    }

    if (empty($email)) {
        echo $putih . "Masukkan Email FaucetPay Anda: " . $kuning;
        $email = trim(fgets(STDIN));
    }
    
    skibidixxx("https://faucetpepe.xyz/", "GET", [], [
        "user-agent: " . $ua,
        "accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    ]);

    echo $putih . "[🔒] Proses Login!\n";
    $hcap_token = "";
    while (empty($hcap_token)) {
        $hcap_token = solveHcaptchaWaryono($apikeyWaryono, $HCAPTCHA_SITEKey);
        if (empty($hcap_token)) {
            echo $merah . "[🔏] Login Gagal!!! ❌️\n" . $reset;
            sleep(3);
        }
    }
    
    $login_data = http_build_query([
        "email" => $email,
        "captcha" => "hcaptcha",
        "h-captcha-response" => $hcap_token,
        "g-recaptcha-response" => $hcap_token,
        "uf" => md5($email),
        "utt" => "Asia/Jakarta",
        "ls" => "en-US,en;q=0.9"
    ]);
    
    list($login_res, , $l_code) = skibidixxx("https://faucetpepe.xyz/auth/login", "POST", $login_data, [
        "Content-Type: application/x-www-form-urlencoded",
        "Origin: https://faucetpepe.xyz",
        "Referer: https://faucetpepe.xyz/",
        "User-Agent: " . $ua
    ]);

    if (strpos($login_res, "does not exist") !== false || strpos($login_res, "invalid email") !== false || strpos($login_res, "not registered") !== false) {
        echo $merah . "[📧] Akun Tidak Valid ⛔️\n" . $reset;
        exit;
    }
    
    echo $hijau . "[🔓] Login Berhasil! ✅️\n" . $reset;
    $configData = ["email" => $email, "earned" => $earned, "total_coins" => $total_coins];
    file_put_contents($configFile, json_encode($configData, JSON_PRETTY_PRINT));
    sleep(2);
}

if (!file_exists($configFile) || !file_exists("cookie_pepe.txt")) {
    doLogin($apikeyWaryono, $HCAPTCHA_SITEKEY, $configFile);
}

$ua = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Mobile Safari/537.36";
clear();
$configData = json_decode(file_get_contents($configFile), true);
$totalEarned = $configData['earned'] ?? 0;
$totalCoins = $configData['total_coins'] ?? 0;
banner($totalEarned, $totalCoins, "COINS");

$dash_page = skibidixxx("https://faucetpepe.xyz/dashboard", "GET", [], [
    "user-agent: " . $ua,
    "accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
]);

if (strpos($dash_page, 'Enter Your FaucetPay Email') !== false || strpos($dash_page, 'action="https://faucetpepe.xyz/auth/login"') !== false) {
    if (file_exists("cookie_pepe.txt")) unlink("cookie_pepe.txt");
    doLogin($apikeyWaryono, $HCAPTCHA_SITEKEY, $configFile);
    $dash_page = skibidixxx("https://faucetpepe.xyz/dashboard", "GET", [], ["user-agent: " . $ua]);
}

preg_match_all('/href="[^"]*\/faucet\/([a-zA-Z0-9]+)"/i', $dash_page, $matches);
$foundCoins = array_unique($matches[1]);

$configData = json_decode(file_get_contents($configFile), true);
$selectedCoin = $configData['coin'] ?? '';

if (empty($selectedCoin) || !in_array(strtolower($selectedCoin), array_map('strtolower', $foundCoins))) {
    if (!empty($foundCoins)) {
        clear();
        banner($totalEarned, $totalCoins, "COINS");
        echo "\n" . $cyan . "  ==========================================\n";
        echo "          " . $bold . $putih . "PILIHAN KOIN FAUCET" . $cyan . "\n";
        echo "  ==========================================\n" . $reset;
        
        $coinList = array_values($foundCoins);
        $total = count($coinList);
        $columns = 3;
        
        for ($i = 0; $i < $total; $i++) {
            $num = $i + 1;
            $c_name = strtoupper($coinList[$i]);
            $style = getCoinStyle($c_name);
            
            echo " " . $cyan . "[" . $hijau . str_pad($num, 2, '0', STR_PAD_LEFT) . $cyan . "] " . $style["color"] . $style["symbol"] . " " . $bold . str_pad($c_name, 5) . $reset . " ";
            
            if (($i + 1) % $columns == 0 || $i == $total - 1) {
                echo "\n";
            }
        }
        echo $cyan . "  ------------------------------------------\n" . $reset;
        echo $putih . "  Pilih nomor koin: " . $kuning;
        $choice = trim(fgets(STDIN));
        $selectedIndex = intval($choice) - 1;
        if (isset($coinList[$selectedIndex])) {
            $selectedCoin = strtolower($coinList[$selectedIndex]);
        } else {
            $selectedCoin = strtolower($coinList[0]);
        }
    } else {
        $selectedCoin = "usdt";
    }
    $configData['coin'] = $selectedCoin;
    file_put_contents($configFile, json_encode($configData, JSON_PRETTY_PRINT));
}

$totalEarned = $configData['earned'] ?? 0;
$totalCoins = $configData['total_coins'] ?? 0;
echo "\n[+] Bot aktif menggunakan koin: " . strtoupper($selectedCoin) . "\n";
sleep(2);

loop_start:
$configData = json_decode(file_get_contents($configFile), true);
$totalEarned = $configData['earned'] ?? 0;
$totalCoins = $configData['total_coins'] ?? 0;

clear();
banner($totalEarned, $totalCoins, $selectedCoin);

$targetUrl = "https://faucetpepe.xyz/faucet/" . $selectedCoin;

$headers = [
    "host: faucetpepe.xyz",
    "user-agent: " . $ua,
    "accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "referer: https://faucetpepe.xyz/dashboard"
];

$faucet_page = skibidixxx($targetUrl, "GET", [], $headers);

if (strpos($faucet_page, 'Enter Your FaucetPay Email') !== false || strpos($faucet_page, 'action="https://faucetpepe.xyz/auth/login"') !== false) {
    if (file_exists("cookie_pepe.txt")) unlink("cookie_pepe.txt");
    doLogin($apikeyWaryono, $HCAPTCHA_SITEKEY, $configFile);
    goto loop_start;
}

if (strpos($faucet_page, 'Insufficient funds') !== false || strpos($faucet_page, 'empty') !== false || strpos($faucet_page, 'Faucet is empty') !== false) {
    echo $merah . "[💴] Saldo Faucet Habis Bos!. Tolong ganti yang lain!!🗿\n" . $reset;
    sleep(5);
    goto loop_start;
}

$token = "";
if (preg_match('/<input[^>]+name="token"\s+value="([^"]+)"/i', $faucet_page, $m)) {
    $token = $m[1];
} elseif (preg_match('/<input[^>]+value="([^"]+)"[^>]+name="token"/i', $faucet_page, $m)) {
    $token = $m[1];
} elseif (preg_match('/token["\']?\s*:\s*["\']([a-zA-Z0-9_-]+)["\']/i', $faucet_page, $m)) {
    $token = $m[1];
}

if (empty($token)) {
    echo $merah . "[💴] Saldo Faucet Habis Bos!. Tolong ganti yang lain!!🗿\n" . $reset;
    sleep(5);
    goto loop_start;
}

if ($botMode == 1) {
    $captcha_token = solveAdslabAlljrlwr($apikeyAlljrlwr, $ADSLAB_SITEKEY);
} else {
    $captcha_token = solveAdslabWaryono($apikeyWaryono, $ADSLAB_SITEKEY);
}

if (empty($captcha_token)) {
    echo $merah . "[❌️] Claim Gagal🥊\n" . $reset;
    sleep(5);
    goto loop_start;
}

$post_data = http_build_query([
    "token" => $token,
    "currency" => $selectedCoin,
    "captcha" => "alcaptcha",
    "alcaptcha-response" => $captcha_token,
    "uf" => md5($configData['email']),
    "utt" => "Asia/Jakarta",
    "ls" => "en-US,en;q=0.9"
]);

$post_headers = [
    "host: faucetpepe.xyz",
    "origin: https://faucetpepe.xyz",
    "content-type: application/x-www-form-urlencoded",
    "user-agent: " . $ua,
    "referer: $targetUrl"
];

$claim_res = skibidixxx("https://faucetpepe.xyz/faucet/verify", "POST", $post_data, $post_headers);

if (strpos($claim_res, "Good job!") !== false || strpos($claim_res, "successfully") !== false || strpos($claim_res, "Sent To Your Account") !== false) {
    
    $is_error = false;
    $error_keywords = ["Please wait", "cooldown", "Invalid", "expired"];
    foreach ($error_keywords as $keyword) {
        if (strpos($claim_res, $keyword) !== false) {
            $is_error = true;
            break;
        }
    }

    if (!$is_error) {
        $rewardCoins = 0.00015;
        if (preg_match('/([\d\.]+)\s*(?:Usdt|satoshis|tokens|coin|coins|pepe|LTC|DOGE|SOL|TRX|BCH|DASH|ZEC|[a-zA-Z]+)?\s*&\s*\d+\s*PTS/i', $claim_res, $coinMatch)) {
            if (isset($coinMatch[1]) && is_numeric($coinMatch[1])) {
                $rewardCoins = (float)$coinMatch[1];
            }
        } elseif (preg_match('/([\d\.]+)\s*(?:Usdt|USD|satoshis|tokens|coin|coins)/i', $claim_res, $coinMatch)) {
            if (isset($coinMatch[1]) && is_numeric($coinMatch[1])) {
                $rewardCoins = (float)$coinMatch[1];
            }
        }

        $totalEarned++;
        $totalCoins += $rewardCoins;
        
        $configData['earned'] = $totalEarned;
        $configData['total_coins'] = $totalCoins;
        file_put_contents($configFile, json_encode($configData, JSON_PRETTY_PRINT));
        
        clear();
        banner($totalEarned, $totalCoins, $selectedCoin);
        echo $hijau . "[✅️] Claim Sukses (" . $rewardCoins . " " . strtoupper($selectedCoin) . ") 🎉\n" . $reset;
    } else {
        echo $merah . "[❌️] Claim Gagal🥊\n" . $reset;
    }
} else {
    if (strpos($claim_res, "Shortlinks") !== false || strpos($claim_res, "Shortlink") !== false || strpos($claim_res, "Complete Atleast") !== false || strpos($claim_res, "links/") !== false) {
        echo "\n" . $kuning . $bold . "  ⚠️ Jangan malas selesaikan shortlink ⚠️\n" . $reset;
        echo $putih . "  Tekan " . $kuning . "[ENTER]" . $putih . " untuk melanjutkan bot setelah selesai... " . $reset;
        fgets(STDIN);
    } else {
        echo $merah . "[❌️] Claim Gagal🥊\n" . $reset;
    }
}

fixedCooldownTimer(15);
goto loop_start;
