<?php

clear();

// ======================= BANNER =======================
$blue   = "\033[1;34m";
$cyan   = "\033[1;36m";
$green  = "\033[1;32m";
$yellow = "\033[1;33m";
$white  = "\033[1;37m";
$reset  = "\033[0m";

echo $cyan . "
███████╗███████╗██╗   ██╗ ██████╗ ██████╗ ██████╗  █████╗
██╔════╝██╔════╝╚██╗ ██╔╝██╔═══██╗██╔══██╗██╔══██╗██╔══██╗
█████╗  █████╗   ╚████╔╝ ██║   ██║██████╔╝██████╔╝███████║
██╔══╝  ██╔══╝    ╚██╔╝  ██║   ██║██╔══██╗██╔══██╗██╔══██║
██║     ███████╗   ██║   ╚██████╔╝██║  ██║██║  ██║██║  ██║
╚═╝     ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
" . $reset;

echo $blue . "┌────────────────────────────────────────────────────┐\n";
echo $blue . "│" . $yellow . "                FEYORRA AUTO CLAIM                " . $blue . "│\n";
echo $blue . "├────────────────────────────────────────────────────┤\n";
echo $blue . "│" . $white . " Developer : " . $green . "@MoneyMaker_w                  " . $blue . "│\n";
echo $blue . "│" . $white . " Version   : " . $green . "1.0                            " . $blue . "│\n";
echo $blue . "│" . $white . " Nonapikey  : " . $green . "SERING CEK SCRIPT KARENA ADA TUGAS PTC / often check the script because there is a PTC assignment                         " . $blue . "│\n";
echo $blue . "└────────────────────────────────────────────────────┘" . $reset . "\n\n";

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');
$configFile = "config.json";
$cookieFile = "cookies.txt";

const hitam  = "\033[0;30m";
const merah  = "\033[0;31m";
const hijau  = "\033[0;32m";
const kuning = "\033[0;33m";
const biru   = "\033[0;34m";
const cyan   = "\033[0;36m";
const putih  = "\033[0;37m";
const reset  = "\033[0m";

const version     = "1.0";
const script_name = "feyorra";
const host        = "https://feyorra.top";

function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function cookieStringToNetscape($cookieStr, $domain = 'feyorra.top', $path = '/') {
    $lines = [];
    $pairs = explode(';', $cookieStr);
    foreach ($pairs as $pair) {
        $pair = trim($pair);
        if (empty($pair)) continue;
        $kv = explode('=', $pair, 2);
        $name  = trim($kv[0]);
        $value = isset($kv[1]) ? trim($kv[1]) : '';
        $lines[] = "$domain\tFALSE\t$path\tFALSE\t0\t$name\t$value";
    }
    return implode("\n", $lines);
}

function skibidixxx($url, $method = 'GET', $data = [], $headers = []) {
    global $cookieFile;
    while (true) {
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
            CURLOPT_COOKIEFILE     => $cookieFile,
            CURLOPT_COOKIEJAR      => $cookieFile
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
            echo "\33[1;" . rand(30, 37) . "mwiwok detok";
            sleep(1);
            echo "\r \r";
            return "ngelek";
        }
    }
}

function timer($seconds, $prefix = "[!] please wait") {
    $wait_time = (int)$seconds;
    $frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'];
    $frame_count = count($frames);
    $current_frame = 0;
    $frame_delay = 0.1;
    while ($wait_time > 0) {
        $start_time = microtime(true);
        while ((microtime(true) - $start_time) < 1) {
            $hours = floor($wait_time / 3600);
            $minutes = floor(($wait_time % 3600) / 60);
            $seconds_left = $wait_time % 60;
            $time_formatted = sprintf('%02d:%02d:%02d', $hours, $minutes, $seconds_left);
            $spinner = $frames[$current_frame];
            echo putih . $prefix . hijau . " $time_formatted " . putih . $spinner . "\r";
            usleep($frame_delay * 1000000);
            $current_frame = ($current_frame + 1) % $frame_count;
            if ((microtime(true) - $start_time) >= 1) break;
        }
        $wait_time--;
    }
    echo "\r                                     \r";
}

function getConfig($configFile) {
    if (file_exists($configFile)) {
        $config = json_decode(file_get_contents($configFile), true);
        if (isset($config['email']) && isset($config['password'])) return $config;
    }
    echo putih . "Email     : " . kuning;
    $email = trim(fgets(STDIN));
    echo putih . "Password  : " . kuning;
    $password = trim(fgets(STDIN));
    $data = ["email" => $email, "password" => $password];
    file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
    echo hijau . "Konfigurasi disimpan ke $configFile\n\n" . reset;
    sleep(2);
    return $data;
}

function initCookie($cookieFile) {
    if (file_exists($cookieFile)) return;
    echo putih . "Masukkan cookie string :\n" . kuning;
    $cookieStr = trim(fgets(STDIN));
    if (stripos($cookieStr, 'Cookie:') === 0) {
        $cookieStr = trim(substr($cookieStr, 7));
    }
    $netscapeContent = cookieStringToNetscape($cookieStr);
    file_put_contents($cookieFile, $netscapeContent);
    echo hijau . "Cookie disimpan (format Netscape).\n" . reset;
    sleep(2);
}

function validateCookie($a) {
    $url = host . "/dashboard";
    $dash = skibidixxx($url, "GET", [], $a);
    return (strpos($dash, "Dashboard") !== false);
}

function allhwaders(&$a, &$b, &$c){
    $a = [
        "host: feyorra.top",
        "user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36",
        "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
        "sec-fetch-site: same-origin",
        "sec-fetch-mode: navigate",
        "sec-fetch-user: ?1",
        "sec-fetch-dest: document",
        "referer: https://feyorra.top/",
        "accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
    ];
    $b = [
        "host: feyorra.top",
        "origin: https://feyorra.top",
        "content-type: application/x-www-form-urlencoded",
        "user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36",
        "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
        "referer: https://feyorra.top/login",
        "accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
    ];
    $c = [
        "host: feyorra.top",
        "user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
        "accept: image/avif,image/webp,image/apng,image/svg+xml,image,q=0.8",
        "sec-fetch-dest: image",
        "referer: https://feyorra.top/faucet"
    ];
}

// ================= MAIN =================
home:
$config = getConfig($configFile);
$email    = $config['email'];
$password = $config['password'];

initCookie($cookieFile);
allhwaders($a, $b, $c);

if (!validateCookie($a)) {
    echo merah . "Cookie tidak valid / kadaluarsa.\n" . reset;
    @unlink($cookieFile);
    sleep(2);
    goto home;
}

$dash = skibidixxx(host . "/dashboard", "GET", [], $a);
if (strpos($dash, "Dashboard") !== false) {
    $balance = explode("</p>", explode("<p>", $dash)[1])[0];
    echo putih . "Account balance " . cyan . $balance . "\n\n";
} else {
    echo merah . "Gagal mengambil dashboard.\n" . reset;
    exit;
}

fc:
while (true) {
    $faucet = skibidixxx(host . "/faucet", "GET", [], $a);
    if (strpos($faucet, "Daily limit") !== false || strpos($faucet, "limit") !== false) {
        echo merah . "Daily Limit reached!\n";
        exit;
    }
    if (strpos($faucet, "complete shortlink") !== false) {
        echo merah . "Selesaikan Misi Shortlink!\n";
        exit;
    }
    if (strpos($faucet, "Complete all ptc ads for continue Faucet claiming.") !== false) {
        echo merah . "Selesaikan Misi (Complete all ptc ads)\n";
        exit;
    }
    if (strpos($faucet, "Ready To Claim") !== false) {
        preg_match('/id="token" value="([^"]+)"/', $faucet, $m);
        $csrf = $m[1];
        preg_match('/name="token" value="([^"]+)"/', $faucet, $m);
        $token = $m[1];

        $data = http_build_query([
            "csrf_token_name" => $csrf,
            "token" => $token
        ]);
        $claim = skibidixxx(host . "/faucet/verify", "POST", $data, $b);
        if (preg_match("/title: '([^']+)'/", $claim, $win)) {
            $wait = explode(' -', explode('let wait = ', $claim)[1])[0];
            echo putih . "[Success] " . hijau . $win[1] . "\n";
            timer($wait, "  next");
        } elseif (preg_match('/alert-danger">.*?<\/i>\s*([^<]+)/s', $claim, $fail)) {
            echo putih . "[Failed] " . merah . trim($fail[1]) . "\n";
        } else {
            echo "Error: Respon zonk atau limit!\n";
        }
    } else {
        $wait = explode(' -', explode('let wait = ', $faucet)[1])[0];
        timer($wait, "  next");
        goto fc;
    }
}