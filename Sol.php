<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');
$configFile = "EarnSolona.json";

// ============================================================
//  COLORS
// ============================================================
const merah  = "\033[0;31m";
const hijau  = "\033[0;32m";
const kuning = "\033[0;33m";
const cyan   = "\033[0;36m";
const putih  = "\033[0;37m";
const reset  = "\033[0m";

const script_name = "EarnSolana Auto Claim";
const host        = "https://earnsolana.xyz";
const MAX_CLAIMS  = 750;           // <-- diubah jadi 750
const MAX_FAILURES = 10;
const REFRESH_CLAIMS = 50;
const WAIT_AFTER_CLAIM = 180;       // <-- detik tetap setelah claim

// ============================================================
//  BANNER
// ============================================================
function print_banner() {
    system('clear');
    echo cyan . "========================================================\n";
    echo cyan . "║" . reset . "                " . kuning . ":: EarnSolana Auto Claim ::" . reset . "              " . cyan . "║\n";
    echo cyan . "========================================================\n";
    echo cyan . "║" . reset . " " . cyan . "▪ Mode   " . putih . "Auto Claim (No Captcha)" . str_repeat(" ", 18) . cyan . "║\n";
    echo cyan . "║" . reset . " " . cyan . "▪ Website " . putih . "earnsolana.xyz" . str_repeat(" ", 29) . cyan . "║\n";
    echo cyan . "║" . reset . " " . cyan . "▪ Max     " . putih . MAX_CLAIMS . " claims, " . MAX_FAILURES . " fails stop" . str_repeat(" ", 10) . cyan . "║\n";
    echo cyan . "║" . reset . " " . cyan . "▪ Refresh " . putih . "Every " . REFRESH_CLAIMS . " claims" . str_repeat(" ", 15) . cyan . "║\n";
    echo cyan . "║" . reset . " " . cyan . "▪ Cooldown " . putih . WAIT_AFTER_CLAIM . " seconds fixed" . str_repeat(" ", 15) . cyan . "║\n";
    echo cyan . "║" . reset . " " . cyan . "▪ Maker   " . putih . "MoneyMaker_w" . str_repeat(" ", 29) . cyan . "║\n";
    echo cyan . "========================================================\n";
    echo cyan . "--------------------------------------------------------\n\n" . reset;
}

// ============================================================
//  HTTP
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
        CURLOPT_COOKIEFILE     => $cookiefile,
        CURLOPT_COOKIEJAR      => $cookiefile
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
//  GET BALANCE (with debug)
// ============================================================
function get_balance($headers) {
    $dash = http_request(host . "/dashboard", "GET", [], $headers);
    // Save for debug (optional)
    // file_put_contents("dashboard_debug.html", $dash);
    
    $balance = '0';
    $patterns = [
        '/<strong>\s*([\d,]+)\s*tokens/i',
        '/>([\d,]+)\s*tokens?/i',
        '/Balance:?\s*([\d,]+)/i',
        '/"balance":\s*"([\d,]+)"/i',
        '/<span[^>]*class="[^"]*balance[^"]*"[^>]*>([\d,]+)<\/span>/i',
        '/<h[0-9][^>]*>([\d,]+)<\/h[0-9]>\s*tokens?/i',
    ];
    foreach ($patterns as $pattern) {
        if (preg_match($pattern, $dash, $m)) {
            $balance = trim(str_replace(',', '', $m[1]));
            break;
        }
    }
    return $balance;
}

// ============================================================
//  TIMER (fixed 12 seconds)
// ============================================================
function timer($seconds) {
    $wait_time = (int)$seconds;
    if ($wait_time <= 0) $wait_time = WAIT_AFTER_CLAIM; // fallback
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
//  LOGIN
// ============================================================
function login($email, $password, &$headers) {
    $login_page = http_request(host . "/login", "GET", [], $headers);
    preg_match('/name="csrf_token_name"\s*value="([^"]+)"/i', $login_page, $tok);
    $csrf = $tok[1] ?? '';
    if (!$csrf) return false;
    $post_data = http_build_query([
        "csrf_token_name" => $csrf,
        "email" => $email,
        "password" => $password
    ]);
    $login_headers = [
        "host: earnsolana.xyz",
        "content-type: application/x-www-form-urlencoded",
        "user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36",
        "origin: https://earnsolana.xyz",
        "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
        "referer: https://earnsolana.xyz/login"
    ];
    $login_res = http_request(host . "/auth/login", "POST", $post_data, $login_headers);
    if (strpos($login_res, 'Dashboard') !== false || strpos($login_res, 'faucet') !== false) {
        return true;
    }
    return false;
}

// ============================================================
//  MAIN
// ============================================================
print_banner();

// ---- Config Y/N ----
if (file_exists($configFile)) {
    echo putih . "Use saved config? (y/n): " . kuning;
    $use_saved = trim(fgets(STDIN));
    if (strtolower($use_saved) === 'y') {
        $config = json_decode(file_get_contents($configFile), true);
        $email = $config['email'] ?? '';
        $password = $config['password'] ?? '';
        echo hijau . "Loaded saved credentials.\n\n" . reset;
    } else {
        // ask for new credentials
        echo putih . "Email: " . kuning;
        $email = trim(fgets(STDIN));
        echo putih . "Password: " . kuning;
        $password = trim(fgets(STDIN));
        $config = ["email" => $email, "password" => $password];
        file_put_contents($configFile, json_encode($config, JSON_PRETTY_PRINT));
        echo hijau . "Saved.\n\n" . reset;
        sleep(1);
    }
} else {
    // no config file, ask
    echo putih . "Email: " . kuning;
    $email = trim(fgets(STDIN));
    echo putih . "Password: " . kuning;
    $password = trim(fgets(STDIN));
    $config = ["email" => $email, "password" => $password];
    file_put_contents($configFile, json_encode($config, JSON_PRETTY_PRINT));
    echo hijau . "Saved.\n\n" . reset;
    sleep(1);
}

$headers = [
    "host: earnsolana.xyz",
    "upgrade-insecure-requests: 1",
    "user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36",
    "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
    "referer: https://earnsolana.xyz/"
];

// Login
$faucet = http_request(host . "/faucet", "GET", [], $headers);
if (strpos($faucet, 'READY') === false && strpos($faucet, 'Next Claim') === false) {
    echo merah . "[!] Logging in...\n";
    if (!login($email, $password, $headers)) {
        echo merah . "[FAILED] Login failed.\n";
        exit;
    }
    echo hijau . "[SUCCESS] Logged in.\n\n";
    $faucet = http_request(host . "/faucet", "GET", [], $headers);
}

$username = 'Unknown';
if (preg_match('/key="t-henry">([^<]+)</i', $faucet, $u)) $username = trim($u[1]);
elseif (preg_match('/Welcome back,\s*([^<]+)/i', $faucet, $u2)) $username = trim($u2[1]);

$balance = get_balance($headers);
$claims_done = 0;
$failures = 0;
$unknown_retries = 0;
$last_refresh = 0;

echo putih . "User: " . cyan . $username . "\n";
echo putih . "Balance: " . hijau . $balance . " tokens\n";
echo putih . "Starting... (max " . MAX_CLAIMS . " claims, fixed cooldown " . WAIT_AFTER_CLAIM . "s)\n\n";

while ($claims_done < MAX_CLAIMS && $failures < MAX_FAILURES) {
    
    // Auto refresh
    if ($claims_done > 0 && $claims_done % REFRESH_CLAIMS == 0 && $claims_done != $last_refresh) {
        echo kuning . "\n[!] Refreshing session...\n";
        if (!login($email, $password, $headers)) {
            echo merah . "[FAILED] Re-login failed.\n";
            sleep(5);
            continue;
        }
        $last_refresh = $claims_done;
        $balance = get_balance($headers);
        echo putih . "Balance: " . hijau . $balance . " tokens\n\n";
        $unknown_retries = 0;
        sleep(2);
    }
    
    // Fetch faucet page
    $faucet = http_request(host . "/faucet", "GET", [], $headers);
    
    // Check locked
    if (strpos($faucet, "Locked") !== false) {
        echo merah . "[!] Account locked. Exiting.\n";
        exit;
    }
    if (preg_match('/(?<![0-9])[01]\/250/', $faucet)) {
        echo kuning . "[INFO] Daily limit reached.\n";
        exit;
    }
    
    // Extract CSRF and all hidden inputs
    preg_match('/name="csrf_token_name"\s*id="token"\s*value="([^"]+)"/i', $faucet, $tok);
    $csrf_token = $tok[1] ?? '';
    if (!$csrf_token) {
        echo kuning . "[!] CSRF missing. Re-logging...\n";
        if (login($email, $password, $headers)) {
            $balance = get_balance($headers);
            echo putih . "Balance: " . $balance . " tokens\n";
            $unknown_retries = 0;
            sleep(2);
            continue;
        }
        timer(WAIT_AFTER_CLAIM);
        continue;
    }
    
    // Extract all hidden inputs
    preg_match_all('/<input type="hidden" name="([^"]+)" value="([^"]+)"/i', $faucet, $hidden_matches);
    $post_data = ["csrf_token_name" => $csrf_token];
    for ($i = 0; $i < count($hidden_matches[1]); $i++) {
        $name = $hidden_matches[1][$i];
        $value = $hidden_matches[2][$i];
        if ($name !== 'csrf_token_name') {
            $post_data[$name] = $value;
        }
    }
    
    if (strpos($faucet, "READY") !== false || strpos($faucet, 'btn btn-primary btn-lg claim-button') !== false) {
        $unknown_retries = 0;
        
        echo cyan . "[*] Claiming... (" . ($claims_done+1) . "/" . MAX_CLAIMS . ")\n";
        
        $post_encoded = http_build_query($post_data);
        $claim_headers = $headers;
        $claim_headers[] = "content-type: application/x-www-form-urlencoded";
        $claim_headers[] = "origin: https://earnsolana.xyz";
        $claim_headers[] = "referer: https://earnsolana.xyz/faucet";
        
        $claim_res = http_request(host . "/faucet/verify", "POST", $post_encoded, $claim_headers);
        // Debug (optional) – comment out to reduce clutter
        // file_put_contents("claim_debug_" . time() . ".html", $claim_res);
        
        $success = false;
        if (strpos($claim_res, 'Claim Successful!') !== false || 
            strpos($claim_res, 'alert-success') !== false) {
            $success = true;
        }
        
        $old_balance = $balance;
        $new_balance = get_balance($headers);
        
        if ($success || $new_balance > $old_balance) {
            $claims_done++;
            $failures = 0;
            $unknown_retries = 0;
            $balance = $new_balance > $old_balance ? $new_balance : get_balance($headers);
            
            // Extract reward
            $reward = '0.00000200 SOL';
            if (preg_match('/<strong>([\d.]+)\s*SOL<\/strong>/i', $claim_res, $r)) {
                $reward = $r[1] . ' SOL';
            } elseif (preg_match('/<strong>([\d.]+)\s*Tokens?<\/strong>/i', $claim_res, $r)) {
                $reward = $r[1] . ' Tokens';
            }
            
            echo hijau . "[SUCCESS] Claimed " . $reward . " (" . $claims_done . "/" . MAX_CLAIMS . ") | Balance: " . $balance . " tokens\n";
            // === FIXED 12 SECONDS WAIT ===
            timer(WAIT_AFTER_CLAIM);
        } 
        elseif (strpos($claim_res, 'alert-danger') !== false || strpos($claim_res, 'Failed') !== false) {
            $failures++;
            $unknown_retries = 0;
            echo merah . "[FAILED] (" . $failures . "/" . MAX_FAILURES . ")\n";
            if (preg_match('/<div[^>]*class="[^"]*alert-danger[^"]*"[^>]*>(.*?)<\/div>/s', $claim_res, $err)) {
                echo "  " . trim(strip_tags($err[1])) . "\n";
            }
            $balance = get_balance($headers);
            echo "  Current balance: " . $balance . " tokens\n";
            // === FIXED 12 SECONDS WAIT ===
            timer(WAIT_AFTER_CLAIM);
        }
        else {
            // Unknown – treat as cooldown
            $unknown_retries++;
            echo kuning . "[?] Unknown response (attempt $unknown_retries/2). Re-logging...\n";
            if ($unknown_retries >= 2) {
                if (login($email, $password, $headers)) {
                    $unknown_retries = 0;
                    $balance = get_balance($headers);
                    echo putih . "Balance: " . $balance . " tokens\n";
                    sleep(2);
                    continue;
                } else {
                    $failures++;
                    $unknown_retries = 0;
                }
            }
            // === FIXED 12 SECONDS WAIT ===
            timer(WAIT_AFTER_CLAIM);
            continue;
        }
    } else {
        // Not ready – just wait fixed 12 seconds
        echo kuning . "[!] Not ready yet, waiting " . WAIT_AFTER_CLAIM . "s...\n";
        timer(WAIT_AFTER_CLAIM);
    }
}

if ($claims_done >= MAX_CLAIMS) {
    echo hijau . "\n[✓] Done! " . MAX_CLAIMS . " claims completed.\n";
} else {
    echo merah . "\n[✗] Stopped after " . $failures . " failures.\n";
}
$balance = get_balance($headers);
echo putih . "Final Balance: " . hijau . $balance . " tokens\n";
