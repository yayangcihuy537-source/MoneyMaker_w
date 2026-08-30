<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');
$configFile = "MoonPtc.json";

// ============================================================
//  COLORS
// ============================================================
const merah  = "\033[0;31m";
const hijau  = "\033[0;32m";
const kuning = "\033[0;33m";
const cyan   = "\033[0;36m";
const putih  = "\033[0;37m";
const reset  = "\033[0m";

const script_name = "MoonPTC Auto Claim";
const host        = "https://moonptc.com";
const MAX_CLAIMS  = 5000;
const MAX_FAILURES = 5;

// ---- Jeda otomatis ----
const PAUSE_INTERVAL = 7200;   // 2 jam dalam detik
const PAUSE_DURATION = 4320;   // 1,2 jam = 72 menit

function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function print_banner() {
    clear();
    echo cyan . "========================================================\n";
    echo cyan . "║" . reset . "                " . kuning . ":: MoonPTC Auto Claim ::" . reset . "                 " . cyan . "║\n";
    echo cyan . "========================================================\n";
    echo cyan . "║" . reset . " " . cyan . "▪ Mode   " . putih . "Auto Claim (Rotation Captcha)" . str_repeat(" ", 18) . cyan . "║\n";
    echo cyan . "║" . reset . " " . cyan . "▪ Website " . putih . "moonptc.com" . str_repeat(" ", 29) . cyan . "║\n";
    echo cyan . "║" . reset . " " . cyan . "▪ Max     " . putih . MAX_CLAIMS . " claims, " . MAX_FAILURES . " fails stop" . str_repeat(" ", 10) . cyan . "║\n";
    echo cyan . "║" . reset . " " . cyan . "▪ Jeda    " . putih . "2 jam jalan → 1,2 jam pause" . str_repeat(" ", 13) . cyan . "║\n";
    echo cyan . "========================================================\n";
    echo cyan . "--------------------------------------------------------\n\n" . reset;
}

// ============================================================
//  TIMER
// ============================================================
function timer($seconds) {
    $wait_time = (int)$seconds;
    if ($wait_time <= 0) $wait_time = 5;
    $frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'];
    $current_frame = 0;
    while ($wait_time > 0) {
        $hours = floor($wait_time / 3600);
        $minutes = floor(($wait_time % 3600) / 60);
        $seconds_left = $wait_time % 60;
        $time_formatted = sprintf('%02d:%02d:%02d', $hours, $minutes, $seconds_left);
        $spinner = $frames[$current_frame];
        echo "\r" . kuning . "cooldown... " . putih . $time_formatted . " " . $spinner . "   " . reset;
        sleep(1);
        $wait_time--;
        $current_frame = ($current_frame + 1) % count($frames);
    }
    echo "\r" . str_repeat(" ", 40) . "\r";
}

// ============================================================
//  HTTP HELPER
// ============================================================
function http_request($url, $method = 'GET', $data = [], $headers = [], $cookiefile = 'cookies.txt') {
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
        CURLOPT_MAXREDIRS      => 10,
        CURLOPT_SSL_VERIFYHOST => 1,
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_HTTPHEADER     => $final_headers,
        CURLOPT_CONNECTTIMEOUT => 30,
        CURLOPT_TIMEOUT        => 30,
        CURLOPT_COOKIEFILE     => 'cookies.txt',
        CURLOPT_COOKIEJAR      => 'cookies.txt'
    ];
    if (strtoupper($method) === 'POST') {
        $options[CURLOPT_POST] = true;
        $options[CURLOPT_POSTFIELDS] = $data;
    }
    curl_setopt_array($ch, $options);
    $response = curl_exec($ch);
    if ($response === false) {
        curl_close($ch);
        return "ERROR_SIGNAL";
    }
    $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $body = substr($response, $header_size);
    curl_close($ch);
    return $body;
}

// ============================================================
//  CONFIG
// ============================================================
function getConfig($configFile) {
    if (!file_exists($configFile)) {
        print_banner();
        echo putih . "Email: " . kuning;
        $email = trim(fgets(STDIN));
        echo putih . "User-Agent: " . kuning;
        $ua = trim(fgets(STDIN));
        $data = ["email" => $email, "ua" => $ua];
        file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
        echo hijau . "Saved.\n\n" . reset;
        sleep(1);
        return $data;
    }
    return json_decode(file_get_contents($configFile), true);
}

// ============================================================
//  GET BALANCE
// ============================================================
function get_balance($headers) {
    $dash = http_request(host . "/api/balance", "GET", [], $headers);
    $data = json_decode($dash, true);
    return $data['balance'] ?? '0';
}

// ============================================================
//  GET USERNAME
// ============================================================
function get_username($headers) {
    $dash = http_request(host . "/api/user", "GET", [], $headers);
    $data = json_decode($dash, true);
    return $data['username'] ?? 'Unknown';
}

// ============================================================
//  LOGIN
// ============================================================
function login($email, $ua, &$headers) {
    $login_headers = [
        "host: moonptc.com",
        "user-agent: " . $ua,
        "x-requested-with: XMLHttpRequest",
        "sec-ch-ua: \"Chromium\";v=\"146\", \"Not-A.Brand\";v=\"24\", \"Android WebView\";v=\"146\"",
        "sec-ch-ua-mobile: ?1",
        "sec-ch-ua-platform: \"Android\"",
        "content-type: application/json",
        "origin: https://moonptc.com",
        "referer: https://moonptc.com/",
        "accept-language: en-GB,en-US;q=0.9,en;q=0.8",
    ];
    $data = json_encode(["email" => $email]);
    $res = http_request(host . "/api/auth/email-login", "POST", $data, $login_headers);
    $result = json_decode($res, true);
    if (($result['ok'] ?? false) === true) {
        return true;
    }
    return false;
}

// ============================================================
//  VARIANT ID => ANSWER (FULL MAPPING)
// ============================================================
$answers = [
    21 => '25', 19 => '87', 88 => '332', 34 => '304',
    26 => '214', 28 => '153', 29 => '119', 9  => '62',
    79 => '271', 8  => '87', 4  => '218', 61 => '151',
    24 => '278', 96 => '89', 85 => '95', 87 => '32',
    75 => '62', 35 => '271', 83 => '152', 45 => '302',
    32 => '29', 43 => '30', 33 => '328', 57 => '273',
    52 => '89', 73 => '123', 72 => '154', 70 => '212',
    63 => '87', 47 => '242', 30 => '90', 18 => '117',
    48 => '213', 25 => '249', 60 => '178', 46 => '269',
    67 => '300', 10 => '34', 12 => '308',
    22 => '167',
];

// ============================================================
//  MAIN
// ============================================================
print_banner();

$config = getConfig($configFile);
$email = $config['email'];
$ua = $config['ua'];

$headers = [
    "host: moonptc.com",
    "user-agent: " . $ua,
    "x-requested-with: XMLHttpRequest",
    "sec-ch-ua: \"Chromium\";v=\"146\", \"Not-A.Brand\";v=\"24\", \"Android WebView\";v=\"146\"",
    "sec-ch-ua-mobile: ?1",
    "sec-ch-ua-platform: \"Android\"",
    "content-type: application/json",
    "origin: https://moonptc.com",
    "referer: https://moonptc.com/faucet",
    "accept-language: en-GB,en-US;q=0.9,en;q=0.8",
];

// Login
if (!login($email, $ua, $headers)) {
    echo merah . "[FAILED] Login failed. Check email.\n";
    exit;
}
echo hijau . "[SUCCESS] Logged in.\n\n";

$username = get_username($headers);
$balance = get_balance($headers);

$claims_done = 0;
$failures = 0;
$unknown_retries = 0;

$start_time = time(); // waktu mulai untuk pengecekan jeda

echo putih . "User: " . cyan . $username . "\n";
echo putih . "Starting...\n\n";

while ($claims_done < MAX_CLAIMS && $failures < MAX_FAILURES) {
    
    // ===== GET FAUCET STATUS =====
    $res = http_request(host . "/api/faucet/status", "GET", [], $headers);
    $data = json_decode($res, true);
    
    if (isset($data['error']) && $data['error'] === 'unauthorized') {
        echo kuning . "[!] Session expired. Re-logging...\n";
        if (!login($email, $ua, $headers)) {
            echo merah . "[FAILED] Re-login failed.\n";
            exit;
        }
        $unknown_retries = 0;
        continue;
    }
    
    // Check cooldown
    if (($data['canClaim'] ?? true) === false) {
        $remaining = $data['remainingSeconds'] ?? 0;
        if ($remaining > 0) {
            timer($remaining);
            // Setelah timer selesai, cek jeda
            if (time() - $start_time >= PAUSE_INTERVAL) {
                echo kuning . "\n[PAUSE] Running for 2 hours. Taking 1.2 hours break...\n";
                timer(PAUSE_DURATION);
                $start_time = time();
            }
            continue;
        }
    }
    
    // ===== GENERATE ROTATION CAPTCHA =====
    $gen_headers = $headers;
    $gen_headers[] = "content-type: application/json";
    $gen_headers[] = "referer: https://moonptc.com/faucet";
    $gen_res = http_request(host . "/api/captcha-rotation/generate", "POST", '{}', $gen_headers);
    $gen_data = json_decode($gen_res, true);
    
    if (empty($gen_data['success'])) {
        echo merah . "[ERROR] Failed to generate captcha.\n";
        $failures++;
        timer(10);
        // Cek jeda setelah timer
        if (time() - $start_time >= PAUSE_INTERVAL) {
            echo kuning . "\n[PAUSE] Running for 2 hours. Taking 1.2 hours break...\n";
            timer(PAUSE_DURATION);
            $start_time = time();
        }
        continue;
    }
    
    $token = $gen_data['token'] ?? null;
    $variantId = $gen_data['challenge']['variantId'] ?? null;
    if (!$token || $variantId === null) {
        echo merah . "[ERROR] Invalid captcha response.\n";
        $failures++;
        timer(10);
        if (time() - $start_time >= PAUSE_INTERVAL) {
            echo kuning . "\n[PAUSE] Running for 2 hours. Taking 1.2 hours break...\n";
            timer(PAUSE_DURATION);
            $start_time = time();
        }
        continue;
    }
    
    // ===== FIND ANSWER =====
    if (!array_key_exists($variantId, $answers)) {
        $unknown_retries++;
        if ($unknown_retries >= 3) {
            $failures++;
            $unknown_retries = 0;
            echo merah . "[FAILED] Unknown variant: $variantId\n";
        }
        timer(10);
        if (time() - $start_time >= PAUSE_INTERVAL) {
            echo kuning . "\n[PAUSE] Running for 2 hours. Taking 1.2 hours break...\n";
            timer(PAUSE_DURATION);
            $start_time = time();
        }
        continue;
    }
    $answer = [$answers[$variantId]];
    $unknown_retries = 0;
    
    // ===== VERIFY CAPTCHA =====
    $verify_headers = $headers;
    $verify_headers[] = "content-type: application/json";
    $verify_headers[] = "referer: https://moonptc.com/faucet";
    $verify_payload = json_encode([
        'token' => $token,
        'answer' => $answer,
        'type' => 'rotation'
    ]);
    $verify_res = http_request(host . "/api/captcha-rotation/verify", "POST", $verify_payload, $verify_headers);
    $verify_data = json_decode($verify_res, true);
    
    if (empty($verify_data['success']) || empty($verify_data['verifiedToken'])) {
        echo merah . "[ERROR] Captcha verification failed.\n";
        $failures++;
        timer(10);
        if (time() - $start_time >= PAUSE_INTERVAL) {
            echo kuning . "\n[PAUSE] Running for 2 hours. Taking 1.2 hours break...\n";
            timer(PAUSE_DURATION);
            $start_time = time();
        }
        continue;
    }
    
    $verifiedToken = $verify_data['verifiedToken'];
    
    // ===== CLAIM FAUCET =====
    $claim_headers = $headers;
    $claim_headers[] = "content-type: application/json";
    $claim_headers[] = "referer: https://moonptc.com/faucet";
    $claim_payload = json_encode(['captchaToken' => $verifiedToken]);
    $claim_res = http_request(host . "/api/faucet/claim", "POST", $claim_payload, $claim_headers);
    $claim_data = json_decode($claim_res, true);
    
    if (($claim_data['ok'] ?? false) === true) {
        $claims_done++;
        $failures = 0;
        $reward = $claim_data['finalReward'] ?? 0;
        $balance = $claim_data['newBalance'] ?? $balance;
        $roll = $claim_data['roll'] ?? 0;
        
        $emoji = ['🔥', '⚡️', '⭐', '💎', '🚀', '💰', '🎯', '🏆'];
        $rand = $emoji[array_rand($emoji)];
        echo hijau . "[SUCCESS] Roll: {$roll}{$rand} | +{$reward}⚡️ Coins | Balance: {$balance}⭐\n";
        
        $remaining = $claim_data['remainingSeconds'] ?? 10;
        if ($remaining > 0) {
            timer($remaining);
        } else {
            timer(10);
        }
    } else {
        $failures++;
        $msg = $claim_data['message'] ?? 'Unknown error';
        echo merah . "[FAILED] ($failures/$MAX_FAILURES) $msg\n";
        timer(10);
    }
    
    // ---- Cek jeda otomatis setelah satu siklus selesai ----
    if (time() - $start_time >= PAUSE_INTERVAL) {
        echo kuning . "\n[PAUSE] Running for 2 hours. Taking 1.2 hours break...\n";
        timer(PAUSE_DURATION);
        $start_time = time(); // reset timer
    }
}

if ($claims_done >= MAX_CLAIMS) {
    echo hijau . "\n[✓] Done! " . MAX_CLAIMS . " claims completed.\n";
} else {
    echo merah . "\n[✗] Stopped after " . MAX_FAILURES . " failures.\n";
}
$balance = get_balance($headers);
echo putih . "Final Balance: " . hijau . $balance . " Coins\n";
