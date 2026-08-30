<?php
error_reporting(0);
system('clear');

$cookieFile = __DIR__ . "/cookie.txt";
$configFile = __DIR__ . "/config.json";

// ============================================================
// COLOR
// ============================================================
$R = "\033[0;31m";
$G = "\033[0;32m";
$Y = "\033[0;33m";
$C = "\033[0;36m";
$W = "\033[0;37m";
$RESET = "\033[0m";

// ============================================================
// KONFIGURASI JEDA
// ============================================================
$RUN_DURATION = 10800;  // 3 jam dalam detik
$BREAK_DURATION = 7200; // 120 menit = 7200 detik

// ============================================================
// UI FUNCTIONS
// ============================================================

function print_banner() {
    global $C, $Y, $W, $RESET;
    system('clear');
    echo $C . "========================================================\n";
    echo $C . "║" . $RESET . "                    " . $Y . ":: GainLTC AutoClaim ::" . $RESET . "                     " . $C . "║\n";
    echo $C . "========================================================\n";
    echo $C . "║" . $RESET . " " . $C . "▪ Mode   " . $W . "Auto Claim (Tap-Target Captcha)" . str_repeat(" ", 13) . $C . "║\n";
    echo $C . "║" . $RESET . " " . $C . "▪ Website" . $W . " gainltc.com" . str_repeat(" ", 29) . $C . "║\n";
    echo $C . "========================================================\n";
    echo $C . "--------------------------------------------------------\n\n" . $RESET;
}

function print_box($title, $lines) {
    global $C, $Y, $W, $RESET;
    echo $C . "╔══════════════════════════════════════╗\n";
    echo $C . "║" . $RESET . "         " . $Y . $title . $RESET . "            " . $C . "║\n";
    echo $C . "╚══════════════════════════════════════╝\n";
    foreach ($lines as $line) {
        echo $C . "  " . $line . "\n";
    }
    echo $C . "════════════════════════════════════════\n" . $RESET;
}

function timer($seconds, $label = "⏳ Tunggu") {
    global $Y, $W, $RESET;
    for ($i = $seconds; $i >= 0; $i--) {
        $hours = floor($i / 3600);
        $minutes = floor(($i % 3600) / 60);
        $secs = $i % 60;
        echo "\r" . $Y . $label . ": " . $W . sprintf("%02d:%02d:%02d", $hours, $minutes, $secs) . $RESET . " ";
        flush();
        sleep(1);
    }
    echo "\r" . str_repeat(" ", 60) . "\r";
}

// Hapus cookie lama
@unlink($cookieFile);

// ============================================================
// CONFIG EMAIL & PASSWORD
// ============================================================

print_banner();

$config = [];
if (file_exists($configFile)) {
    $config = json_decode(file_get_contents($configFile), true);
}

if (empty($config['email']) || empty($config['password'])) {
    echo $C . "📧 Email    : " . $W;
    $email = trim(fgets(STDIN));
    echo $C . "🔑 Password : " . $W;
    $password = trim(fgets(STDIN));
    
    file_put_contents($configFile, json_encode([
        "email" => $email,
        "password" => $password
    ], JSON_PRETTY_PRINT));
    
    echo $G . "✅ Berhasil disimpan.\n" . $RESET;
    sleep(2);
    system('clear');
} else {
    $email = $config['email'];
    $password = $config['password'];
}

// ============================================================
// FUNCTION LOGIN
// ============================================================

function do_login($email, $password, $cookieFile) {
    global $C, $Y, $G, $R, $W, $RESET;
    
    // GET login page untuk cookie
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => 'https://gainltc.com/login',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_COOKIEJAR => $cookieFile,
        CURLOPT_COOKIEFILE => $cookieFile,
        CURLOPT_HTTPHEADER => [
            'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36',
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'cache-control: max-age=0',
            'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
            'sec-ch-ua-mobile: ?1',
            'sec-ch-ua-platform: "Android"',
            'upgrade-insecure-requests: 1',
            'accept-language: id,en-US;q=0.9,en;q=0.8,pt;q=0.7',
        ],
    ]);
    $response = curl_exec($ch);
    @curl_close($ch);

    // GENERATE CAPTCHA
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => 'https://gainltc.com/api/captcha/generate',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_COOKIEJAR => $cookieFile,
        CURLOPT_COOKIEFILE => $cookieFile,
        CURLOPT_HTTPHEADER => [
            'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36',
            'Accept: application/json, text/plain, */*',
            'content-length: 0',
            'sec-ch-ua-platform: "Android"',
            'x-csrf-token: 02672ff5c721b426b153454827446609c5dfdaf1090145235a8e9438762da39a:1785481205783:e393c4975d59889146d05762d0a92f0210bb0d3aa5a4861fa8b9605d2f10b237',
            'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
            'sec-ch-ua-mobile: ?1',
            'origin: https://gainltc.com',
            'accept-language: id,en-US;q=0.9,en;q=0.8,pt;q=0.7',
        ],
    ]);

    while (true) {
        $response = curl_exec($ch);
        $json = json_decode($response, true);
        if (($json['challenge']['type'] ?? '') === 'tap-target') {
            $token = $json['token'];
            $target = $json['challenge']['target'];
            $tapsRequired = $json['challenge']['tapsRequired'];
            break;
        }
        sleep(1);
    }
    @curl_close($ch);

    // VERIFY CAPTCHA
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => 'https://gainltc.com/api/captcha/verify',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode([
            "token" => $token,
            "answer" => array_fill(0, $tapsRequired, $target),
            "type" => "tap-target"
        ]),
        CURLOPT_COOKIEJAR => $cookieFile,
        CURLOPT_COOKIEFILE => $cookieFile,
        CURLOPT_HTTPHEADER => [
            'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36',
            'Accept: application/json, text/plain, */*',
            'Content-Type: application/json',
            'sec-ch-ua-platform: "Android"',
            'x-csrf-token: 02672ff5c721b426b153454827446609c5dfdaf1090145235a8e9438762da39a:1785481205783:e393c4975d59889146d05762d0a92f0210bb0d3aa5a4861fa8b9605d2f10b237',
            'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
            'sec-ch-ua-mobile: ?1',
            'origin: https://gainltc.com',
            'accept-language: id,en-US;q=0.9,en;q=0.8,pt;q=0.7',
        ],
    ]);
    $response = curl_exec($ch);
    @curl_close($ch);
    $json = json_decode($response, true);

    if (empty($json['success'])) {
        return false;
    }
    $verifiedToken = $json['verifiedToken'];

    // LOGIN
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => 'https://gainltc.com/api/auth/login',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode([
            "email" => $email,
            "password" => $password,
            "captchaToken" => $verifiedToken,
            "rememberMe" => false
        ]),
        CURLOPT_COOKIEJAR => $cookieFile,
        CURLOPT_COOKIEFILE => $cookieFile,
        CURLOPT_HTTPHEADER => [
            'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36',
            'Accept: application/json, text/plain, */*',
            'Content-Type: application/json',
            'sec-ch-ua-platform: "Android"',
            'x-csrf-token: 0b2e5587276a2e1e85b4c3b7fe02c135f72a5d7a0329bd88fd77229347a4d231:1785481514850:ff7d5fb947ecf0365600275f3c17173b59e586365390879bbcbf3dfec6c06433',
            'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
            'sec-ch-ua-mobile: ?1',
            'origin: https://gainltc.com',
            'accept-language: id,en-US;q=0.9,en;q=0.8,pt;q=0.7',
        ],
    ]);
    $response = curl_exec($ch);
    @curl_close($ch);
    $json = json_decode($response, true);

    if (empty($json['success'])) {
        return false;
    }

    return $json['user'];
}

// ============================================================
// FUNCTION CLAIM
// ============================================================

function do_claim($cookieFile) {
    global $C, $Y, $G, $R, $W, $RESET;
    
    // GENERATE CAPTCHA
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => 'https://gainltc.com/api/captcha/generate',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_COOKIEJAR => $cookieFile,
        CURLOPT_COOKIEFILE => $cookieFile,
        CURLOPT_HTTPHEADER => [
            'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36',
            'Accept: application/json, text/plain, */*',
            'content-length: 0',
            'sec-ch-ua-platform: "Android"',
            'x-csrf-token: 02672ff5c721b426b153454827446609c5dfdaf1090145235a8e9438762da39a:1785481205783:e393c4975d59889146d05762d0a92f0210bb0d3aa5a4861fa8b9605d2f10b237',
            'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
            'sec-ch-ua-mobile: ?1',
            'origin: https://gainltc.com',
            'accept-language: id,en-US;q=0.9,en;q=0.8,pt;q=0.7',
        ],
    ]);

    while (true) {
        $response = curl_exec($ch);
        $json = json_decode($response, true);
        if (($json['challenge']['type'] ?? '') === 'tap-target') {
            $token = $json['token'];
            $target = $json['challenge']['target'];
            $tapsRequired = $json['challenge']['tapsRequired'];
            break;
        }
        sleep(1);
    }
    @curl_close($ch);

    // VERIFY CAPTCHA
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => 'https://gainltc.com/api/captcha/verify',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode([
            "token" => $token,
            "answer" => array_fill(0, $tapsRequired, $target),
            "type" => "tap-target"
        ]),
        CURLOPT_COOKIEJAR => $cookieFile,
        CURLOPT_COOKIEFILE => $cookieFile,
        CURLOPT_HTTPHEADER => [
            'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36',
            'Accept: application/json, text/plain, */*',
            'Content-Type: application/json',
            'sec-ch-ua-platform: "Android"',
            'x-csrf-token: 02672ff5c721b426b153454827446609c5dfdaf1090145235a8e9438762da39a:1785481205783:e393c4975d59889146d05762d0a92f0210bb0d3aa5a4861fa8b9605d2f10b237',
            'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
            'sec-ch-ua-mobile: ?1',
            'origin: https://gainltc.com',
            'accept-language: id,en-US;q=0.9,en;q=0.8,pt;q=0.7',
        ],
    ]);
    $response = curl_exec($ch);
    @curl_close($ch);
    $json = json_decode($response, true);

    if (empty($json['success'])) {
        return false;
    }
    $verifiedToken = $json['verifiedToken'];

    // CLAIM
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => 'https://gainltc.com/api/faucet/claim',
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode([
            "captchaToken" => $verifiedToken
        ]),
        CURLOPT_COOKIEJAR => $cookieFile,
        CURLOPT_COOKIEFILE => $cookieFile,
        CURLOPT_HTTPHEADER => [
            'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Safari/605.1.15',
            'Accept: application/json, text/plain, */*',
            'Content-Type: application/json',
            'sec-ch-ua-platform: "macOS"',
            'x-csrf-token: 25bb0ca451421f370a52901df9ac06919f4df9ec4ed2d16c4b37f36649475c07:1785482476166:010d30483b15235b8f229013182d297431a7bd84822a2c496e0caee18cb22ed0',
            'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="150"',
            'sec-ch-ua-mobile: ?0',
            'origin: https://gainltc.com',
            'x-requested-with: mark.via.gp',
            'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        ],
    ]);
    $response = curl_exec($ch);
    @curl_close($ch);
    $json = json_decode($response, true);

    return $json;
}

// ============================================================
// MAIN LOOP
// ============================================================

$start_time = time();
$claim_count = 0;
$total_earned = 0;
$login_attempt = 0;

while (true) {
    
    // Cek apakah sudah jalan 3 jam
    if (time() - $start_time >= $RUN_DURATION) {
        echo $Y . "\n════════════════════════════════════════\n";
        echo $Y . "  ⏸️  Jeda 2 jam (sudah jalan 3 jam)\n";
        echo $Y . "════════════════════════════════════════\n" . $RESET;
        timer($BREAK_DURATION, "⏳ Jeda");
        $start_time = time();
        continue;
    }
    
    print_banner();
    
    echo $C . "📧 Email    : " . $W . $email . "\n";
    echo $C . "📊 Claims   : " . $W . $claim_count . "\n";
    echo $C . "💰 Earned   : " . $G . number_format($total_earned, 8) . "\n";
    echo $C . "⏱️  Running  : " . $W . gmdate("H:i:s", time() - $start_time) . " / 3:00:00\n";
    echo $C . "════════════════════════════════════════\n" . $RESET;
    
    // Login
    if ($login_attempt == 0) {
        echo $Y . "🔑 Login...\n" . $RESET;
    } else {
        echo $Y . "🔑 Re-login (attempt $login_attempt)...\n" . $RESET;
    }
    
    $user = do_login($email, $password, $cookieFile);
    if (!$user) {
        $login_attempt++;
        echo $R . "❌ Login gagal, coba ulang dalam 10 detik...\n" . $RESET;
        sleep(10);
        continue;
    }
    $login_attempt = 0;
    
    echo $G . "✅ Login berhasil! Balance: " . $user['balance'] . "\n" . $RESET;
    sleep(2);
    
    // Claim loop
    $claim_attempts = 0;
    $max_attempts = 10;
    
    while ($claim_attempts < $max_attempts) {
        
        // Cek jeda 3 jam
        if (time() - $start_time >= $RUN_DURATION) {
            break 2;
        }
        
        $result = do_claim($cookieFile);
        
        if (isset($result['roll'])) {
            $claim_count++;
            $reward = floatval($result['reward']);
            $total_earned += $reward;
            $user['balance'] = $result['newBalance'];
            
            echo $G . "╔══════════════════════════════════════╗\n";
            echo $G . "║          🎲 CLAIM BERHASIL          ║\n";
            echo $G . "╚══════════════════════════════════════╝\n";
            echo $C . "🎲 Roll         : " . $W . $result['roll'] . "\n";
            echo $C . "🎁 Reward       : " . $G . $result['reward'] . "\n";
            echo $C . "💰 New Balance  : " . $G . $result['newBalance'] . "\n";
            echo $C . "📊 Total Claims : " . $W . $claim_count . "\n";
            echo $C . "════════════════════════════════════════\n" . $RESET;
            
            $claim_attempts = 0;
            
            $nextClaimAt = intval($result['nextClaimAt'] / 1000);
            $remaining = max(0, $nextClaimAt - time());
            timer($remaining, "⏳ Next claim");
            
        } else {
            $claim_attempts++;
            $err_msg = $result['error'] ?? 'Unknown error';
            echo $R . "❌ Claim gagal ($claim_attempts/$max_attempts): $err_msg\n" . $RESET;
            
            if ($claim_attempts >= $max_attempts) {
                echo $Y . "⚠️  Terlalu banyak gagal, re-login...\n" . $RESET;
                break;
            }
            
            sleep(5);
        }
    }
}
?>
