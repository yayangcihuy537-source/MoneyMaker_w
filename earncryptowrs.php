<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');
$configFile = "config.json";

const hitam  = "\033[0;30m";
const merah  = "\033[0;31m";
const hijau  = "\033[0;32m";
const kuning = "\033[0;33m";
const biru   = "\033[0;34m";
const cyan   = "\033[0;36m";
const putih  = "\033[0;37m";
const reset  = "\033[0m";

const script_name = "earncryptowrs";
const host        = "https://earncryptowrs.in";

function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function SmartToken($moves = []) {
    $data = [
        'ts'    => round(microtime(true) * 1000),
        'cpu'   => 4,
        'mem'   => 8,
        'w'     => 1920,
        'h'     => 1080,
        'touch' => 0,
        'moves' => $moves
    ];
    return base64_encode(json_encode($data));
}

function skibidixxx($url, $method = 'GET', $data = [], $headers = []) {
    while (true) {
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
            CURLOPT_SSL_VERIFYHOST => 1,
            CURLOPT_SSL_VERIFYPEER => true,
            CURLOPT_HTTPHEADER     => $final_headers,
            CURLOPT_CONNECTTIMEOUT => 999,
            CURLOPT_TIMEOUT        => 999
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
    if ($wait_time < 1) $wait_time = 1;
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
    if (!file_exists($configFile)) {
        echo putih . "Cookie: " . kuning;
        $coki = trim(fgets(STDIN));
        $data = ["cookie" => $coki];
        file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
        echo hijau . "disimpan ke $configFile\n\n" . reset;
        sleep(3);
        return $data;
    }
    return json_decode(file_get_contents($configFile), true);
}

function banner() {
    system("clear");
    $cyan   = "\033[1;36m";
    $green  = "\033[1;32m";
    $yellow = "\033[1;33m";
    $white  = "\033[1;37m";
    $reset  = "\033[0m";

    echo $cyan . "
███████╗ █████╗ ██████╗ ███╗   ██╗ ██████╗██████╗ ██╗   ██╗██████╗ ████████╗ ██████╗
██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗
█████╗  ███████║██████╔╝██╔██╗ ██║██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██║   ██║
██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██║   ██║
███████╗██║  ██║██║  ██║██║ ╚████║╚██████╗██║  ██║   ██║   ██║        ██║   ╚██████╔╝
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝
";
    echo $green . "                EARNCRYPTOWRS AUTO CLAIM\n";
    echo $yellow . "=============================================================\n";
    echo $white  . " Developer : @MoneyMaker_w\n";
    echo $white  . " Language  : PHP CLI\n";
    echo $white  . " Version   : 4.0 (Cookie manual)\n";
    echo $yellow . "=============================================================\n\n";
    echo $reset;
}

// ==================== HEADERS ====================
function getHeaders($coki) {
    return [
        "host: earncryptowrs.in",
        "save-data: on",
        "upgrade-insecure-requests: 1",
        "user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36",
        "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
        "sec-fetch-site: same-origin",
        "sec-fetch-mode: navigate",
        "sec-fetch-user: ?1",
        "sec-fetch-dest: document",
        "referer: https://earncryptowrs.in/",
        "accept-language: id,en-US;q=0.9,en;q=0.8,ms;q=0.7,ru;q=0.6",
        "cookie: " . $coki
    ];
}

function postHeaders($coki) {
    return [
        "host: earncryptowrs.in",
        "save-data: on",
        "origin: https://earncryptowrs.in",
        "content-type: application/x-www-form-urlencoded",
        "upgrade-insecure-requests: 1",
        "user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36",
        "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
        "sec-fetch-site: same-origin",
        "sec-fetch-mode: navigate",
        "sec-fetch-user: ?1",
        "sec-fetch-dest: document",
        "referer: https://earncryptowrs.in/",
        "accept-language: id,en-US;q=0.9,en;q=0.8,ms;q=0.7,ru;q=0.6",
        "cookie: " . $coki
    ];
}

// ==================== DETEKSI RESPONS ====================
function detectClaimResponse($html) {
    // 1. Cari alert di HTML
    if (preg_match('/<div[^>]*class="[^"]*alert[^"]*"[^>]*>(.*?)<\/div>/is', $html, $m)) {
        $alert_html = $m[1];
        $alert_text = strip_tags($alert_html);
        $alert_text = trim($alert_text);
        
        // Cek apakah alert-success
        if (strpos($m[0], 'alert-success') !== false) {
            return ['status' => 'success', 'message' => $alert_text];
        }
        // Cek apakah alert-danger atau alert-warning
        if (strpos($m[0], 'alert-danger') !== false || strpos($m[0], 'alert-warning') !== false) {
            return ['status' => 'error', 'message' => $alert_text];
        }
        // Jika alert biasa, cek isinya
        if (stripos($alert_text, 'success') !== false || stripos($alert_text, 'claimed') !== false || stripos($alert_text, 'reward') !== false) {
            return ['status' => 'success', 'message' => $alert_text];
        }
        if (stripos($alert_text, 'error') !== false || stripos($alert_text, 'failed') !== false || stripos($alert_text, 'banned') !== false || stripos($alert_text, 'limit') !== false) {
            return ['status' => 'error', 'message' => $alert_text];
        }
        // Jika ada alert tapi tidak jelas, anggap error
        return ['status' => 'error', 'message' => $alert_text];
    }

    // 2. Coba parse JSON
    $json = json_decode($html, true);
    if ($json !== null) {
        if (isset($json['status']) && $json['status'] === 'success') {
            return ['status' => 'success', 'message' => $json['message'] ?? 'Claim berhasil'];
        }
        if (isset($json['status']) && $json['status'] === 'error') {
            return ['status' => 'error', 'message' => $json['message'] ?? 'Terjadi error'];
        }
        if (isset($json['success']) && $json['success'] === true) {
            return ['status' => 'success', 'message' => $json['message'] ?? 'Claim berhasil'];
        }
        if (isset($json['error'])) {
            return ['status' => 'error', 'message' => $json['error']];
        }
    }

    // 3. HTML response: cari pola Swal.fire
    if (preg_match("/Swal\.fire\(\{.*?icon:\s*'success'.*?html:\s*'([^']+)'/s", $html, $m)) {
        return ['status' => 'success', 'message' => $m[1]];
    }
    if (preg_match("/Swal\.fire\(\{.*?icon:\s*'error'.*?html:\s*'([^']+)'/s", $html, $m)) {
        return ['status' => 'error', 'message' => $m[1]];
    }

    // 4. Cari kata kunci umum
    if (stripos($html, 'success') !== false || stripos($html, 'claimed') !== false || stripos($html, 'reward') !== false) {
        return ['status' => 'success', 'message' => 'Claim berhasil (deteksi kata kunci)'];
    }
    if (stripos($html, 'error') !== false || stripos($html, 'failed') !== false || stripos($html, 'limit') !== false || stripos($html, 'banned') !== false) {
        return ['status' => 'error', 'message' => 'Terjadi error (deteksi kata kunci)'];
    }

    // Jika tidak ada pola, kembalikan null (unknown)
    return null;
}

// ==================== MAIN ====================
menu:
clear();
banner();

$config = getConfig($configFile);
$coki   = $config['cookie'];

$url = host . "/dashboard";
$dash = skibidixxx($url, "GET", [], getHeaders($coki));
preg_match('/ID:\s*(\d+)/s', $dash, $m);
$userid = $m[1] ?? '';

if (empty($userid)) {
    echo putih . "Cookie expired.. input new please..\n";
    @unlink($configFile);
    sleep(2);
    goto menu;
}

echo putih . "Your UserId " . cyan . $userid . "\n";

// Ambil daftar currency
$earn = skibidixxx($url, "GET", [], getHeaders($coki));
preg_match_all('/href="https:\/\/earncryptowrs\.in\/faucet\/currency\/([a-zA-Z]+)"\s*\n\s*class="dropdown-item"/', $earn, $matches);
$currencies = $matches[1];
usort($currencies, function($a, $b) {
    return strlen($a) - strlen($b);
});

echo putih . "Available currencies:\n";
$counter = 1;
foreach ($currencies as $currency) {
    $paddedCurrency = str_pad(strtoupper($currency), 5, " ", STR_PAD_RIGHT);
    echo putih . "(" . hijau . $counter . putih . ") " . cyan . $paddedCurrency . "   ";
    if ($counter % 4 == 0) echo "\n";
    $counter++;
}
echo "\n";
echo putih . "-------------------------------------------------------\n";
echo putih . "chosee: " . merah;
$input = trim(fgets(STDIN));

if (!is_numeric($input) || $input < 1 || $input > count($currencies)) {
    echo merah . "invalid chosee\n";
    sleep(1);
    goto menu;
}

$selectedIndex = (int)$input - 1;
$selectedCurrency = $currencies[$selectedIndex];
$pilih = strtolower($selectedCurrency);
echo putih . "selected " . cyan . $pilih . "\n\n";

// ==================== LOOP CLAIM ====================
while (true) {
    $url_faucet = host . "/faucet/currency/" . $pilih;
    $faucet = skibidixxx($url_faucet, "GET", [], getHeaders($coki));

    // Cek limit di halaman faucet (jika ada alert)
    $check = detectClaimResponse($faucet);
    if ($check && $check['status'] === 'error') {
        if (stripos($check['message'], 'limit') !== false || stripos($check['message'], 'banned') !== false) {
            echo merah . "❌ " . $check['message'] . "\n";
            exit;
        }
    }

    // Ambil CSRF, token, wallet, action
    preg_match('/name="csrf_token_name" id="token" value="([^"]+)"/', $faucet, $r_csrf);
    $csrf = $r_csrf[1] ?? '';
    preg_match('/<form[^>]*id="fauform"[^>]*action="([^"]+)"/is', $faucet, $m);
    $url_verify = $m[1] ?? host . "/faucet/verify";
    preg_match('/name="token" value="([^"]+)"/', $faucet, $r_token);
    $token = $r_token[1] ?? '';
    preg_match('/name="wallet".*?value="([^"]+)"/', $faucet, $r_wallet);
    $wallet = $r_wallet[1] ?? '';

    // Hidden inputs
    $hidden = [];
    if (preg_match_all('/<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"[^>]*>/i', $faucet, $matches)) {
        for ($i = 0; $i < count($matches[0]); $i++) {
            $hidden[$matches[1][$i]] = $matches[2][$i];
        }
    }
    unset($hidden['csrf_token_name']);
    unset($hidden['token']);
    unset($hidden['wallet']);

    $post_data = array_merge($hidden, [
        'csrf_token_name' => $csrf,
        'token' => $token,
        'wallet' => $wallet,
        'smart_token' => SmartToken(),
    ]);

    $data = http_build_query($post_data);
    $claim = skibidixxx($url_verify, "POST", $data, postHeaders($coki));
    file_put_contents("claim_debug.html", $claim);

    // Deteksi respons
    $result = detectClaimResponse($claim);

    if ($result !== null) {
        if ($result['status'] === 'success') {
            echo hijau . "✅ " . $result['message'] . "\n";
            // Cek cooldown
            if (preg_match('/var wait = (\d+) -/', $claim, $regex_wait)) {
                $wait = $regex_wait[1];
                timer($wait, "  menunggu...");
            } else {
                timer(10, "  menunggu 10 detik...");
            }
        } else {
            echo merah . "❌ " . $result['message'] . "\n";
            if (stripos($result['message'], 'limit') !== false || stripos($result['message'], 'banned') !== false) {
                echo merah . "Daily limit atau banned. Exiting...\n";
                exit;
            }
            sleep(5);
        }
    } else {
        // Unknown response, coba cek apakah ada indikasi sukses/gagal
        if (strpos($claim, 'limit') !== false || strpos($claim, 'banned') !== false) {
            echo merah . "Daily limit atau banned. Exiting...\n";
            exit;
        }
        echo kuning . "⚠️ Unknown response. Coba lagi...\n";
        echo "Preview: " . substr($claim, 0, 200) . "\n";
        sleep(5);
    }
}