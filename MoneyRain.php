<?php
/**
 * MoneyRain AutoFaucet - FINAL STABLE VERSION
 * Developer: Moneymaker_w
 * Reward: 0.00000250 USDT setiap 5 menit
 */

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');

// ==================== BANNER ====================
$cyan   = "\033[1;36m";
$green  = "\033[1;32m";
$yellow = "\033[1;33m";
$magenta= "\033[1;35m";
$white  = "\033[1;37m";
$reset  = "\033[0m";

echo $cyan . "
 █████╗ ██╗   ██╗████████╗ ██████╗ ███████╗ █████╗ ██╗   ██╗ ██████╗███████╗████████╗
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔════╝██╔══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝
███████║██║   ██║   ██║   ██║   ██║█████╗  ███████║██║   ██║██║     █████╗     ██║
██╔══██║██║   ██║   ██║   ██║   ██║██╔══╝  ██╔══██║██║   ██║██║     ██╔══╝     ██║
██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║     ██║  ██║╚██████╔╝╚██████╗███████╗   ██║
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚══════╝   ╚═╝
";

echo $yellow . "
╔══════════════════════════════════════════════════════════════╗
║      MONEYRAIN AUTO CLAIM                       ║
╠══════════════════════════════════════════════════════════════╣
║  Developer : " . $magenta . "Moneymaker_w" . $yellow . "                                       ║
║  Reward    : " . $green . "0.00000250 USDT / 5 menit" . $yellow . "                           ║
║  Status    : " . $green . "ACTIVE ✅" . $yellow . "                                          ║
╚══════════════════════════════════════════════════════════════╝
" . $reset . "\n";

// ==================== KONFIGURASI ====================
define('BASE_URL', 'https://autofaucet.moneyrain.top');
define('UA', 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36');
define('COOLDOWN', 300);

$COOKIE_FILE = __DIR__ . "/moneyrain_cookies.txt";
$email = '';

// ==================== FUNGSI ====================
function log_msg($msg, $type = 'INFO') {
    $colors = ['SUCCESS'=>"\033[32m",'ERROR'=>"\033[31m",'WARN'=>"\033[33m",'INFO'=>"\033[36m",'RESET'=>"\033[0m"];
    echo $colors[$type] . '[' . date('H:i:s') . '] ' . $msg . $colors['RESET'] . "\n";
}

function get_page($url, $cookie_jar = null) {
    $ch = curl_init($url);
    $options = [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_USERAGENT => UA,
        CURLOPT_ENCODING => '',
        CURLOPT_HTTPHEADER => [
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language: en-US,en;q=0.9',
        ]
    ];
    if ($cookie_jar) {
        $options[CURLOPT_COOKIEJAR] = $cookie_jar;
        $options[CURLOPT_COOKIEFILE] = $cookie_jar;
    }
    curl_setopt_array($ch, $options);
    $html = curl_exec($ch);
    curl_close($ch);
    return $html;
}

function post_form($url, $post_data, $cookie_jar = null) {
    $ch = curl_init($url);
    $options = [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => http_build_query($post_data),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_TIMEOUT => 30,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_USERAGENT => UA,
        CURLOPT_ENCODING => '',
        CURLOPT_HTTPHEADER => [
            'Content-Type: application/x-www-form-urlencoded',
            'Origin: ' . BASE_URL,
            'Referer: ' . $url,
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        ]
    ];
    if ($cookie_jar) {
        $options[CURLOPT_COOKIEJAR] = $cookie_jar;
        $options[CURLOPT_COOKIEFILE] = $cookie_jar;
    }
    curl_setopt_array($ch, $options);
    $response = curl_exec($ch);
    curl_close($ch);
    return $response;
}

function countdown($seconds) {
    for ($i = $seconds; $i > 0; $i--) {
        $mins = floor($i / 60);
        $secs = $i % 60;
        echo "\r\033[33m⏳ Next claim in {$mins}m {$secs}s\033[0m";
        sleep(1);
    }
    echo "\r" . str_repeat(" ", 30) . "\r";
}

function extract_claim_form($html) {
    $result = ['fields' => [], 'action' => ''];
    if (preg_match('/<form[^>]+id="claimForm"[^>]*>(.*?)<\/form>/is', $html, $form_match)) {
        $form_html = $form_match[0];
        if (preg_match('/action="([^"]+)"/', $form_html, $m)) {
            $result['action'] = $m[1];
            if (strpos($result['action'], 'http') !== 0) {
                $result['action'] = BASE_URL . $result['action'];
            }
        } else {
            $result['action'] = BASE_URL . "/claim.php";
        }
        if (preg_match_all('/<input[^>]+name="([^"]+)"[^>]+value="([^"]*)"/i', $form_html, $matches, PREG_SET_ORDER)) {
            foreach ($matches as $m) {
                $result['fields'][$m[1]] = $m[2];
            }
        }
        return $result;
    }
    return null;
}

function is_logged_in($html) {
    return strpos($html, 'Welcome back') !== false || strpos($html, 'Auto-Earning') !== false;
}

function do_login($email) {
    global $COOKIE_FILE;
    log_msg("🔄 Login...", "INFO");
    
    $html = get_page(BASE_URL, $COOKIE_FILE);
    if (!$html || strlen($html) < 100) {
        return false;
    }
    
    if (preg_match('/<form[^>]+action="([^"]+)"/', $html, $m)) {
        $action = $m[1];
        if (strpos($action, 'http') !== 0) $action = BASE_URL . $action;
    } else {
        $action = BASE_URL . "/";
    }
    
    $fields = [];
    if (preg_match_all('/<input[^>]+name="([^"]+)"[^>]+value="([^"]*)"/i', $html, $matches, PREG_SET_ORDER)) {
        foreach ($matches as $m) {
            $fields[$m[1]] = $m[2];
        }
    }
    
    $post_data = $fields;
    $post_data['email'] = $email;
    $response = post_form($action, $post_data, $COOKIE_FILE);
    
    if (is_logged_in($response)) {
        log_msg("✅ Login SUKSES!", "SUCCESS");
        return true;
    }
    log_msg("❌ Login GAGAL!", "ERROR");
    return false;
}

// ==================== MAIN ====================
echo "\n";
$email = readline("\033[36m📧 FaucetPay Email: \033[0m");
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    log_msg("❌ Email tidak valid!", "ERROR");
    exit;
}

log_msg("🚀 Bot Started — Reward akan masuk ke FaucetPay setiap 5 menit", "SUCCESS");
log_msg("💡 Tekan Ctrl+C untuk berhenti", "WARN");
echo "\n";

if (!do_login($email)) {
    log_msg("❌ Login gagal!", "ERROR");
    exit;
}
echo "\n";

log_msg("━━━ AUTO CLAIM LOOP ━━━", "INFO");
log_msg("⏳ Claim setiap 5 menit, auto-relogin jika session expired", "INFO");
echo "\n";

$cycle = 0;
while (true) {
    $cycle++;
    log_msg("━━━ CYCLE #$cycle ━━━", "INFO");

    $html = get_page(BASE_URL . "/claim.php", $COOKIE_FILE);
    
    if (!$html || strlen($html) < 100 || strpos($html, 'START EARNING NOW') !== false) {
        log_msg("⚠️ Session expired, relogin...", "WARN");
        if (!do_login($email)) {
            sleep(30);
            continue;
        }
        $html = get_page(BASE_URL . "/claim.php", $COOKIE_FILE);
        if (!$html || strlen($html) < 100) {
            sleep(30);
            continue;
        }
    }
    
    $form = extract_claim_form($html);
    if (!$form) {
        log_msg("❌ Form tidak ditemukan!", "ERROR");
        sleep(30);
        continue;
    }

    $post_data = $form['fields'];
    $post_data['device_viewport_width'] = '390';
    $post_data['device_screen_width'] = '390';
    $post_data['device_touch_points'] = '1';
    $post_data['device_hover'] = '0';
    $post_data['device_fine_pointer'] = '0';
    $post_data['device_platform'] = 'Android';
    $post_data['device_mobile_hint'] = '1';

    $response = post_form($form['action'], $post_data, $COOKIE_FILE);
    file_put_contents("claim_response.html", $response);

    if (strpos($response, 'Claimed') !== false || strpos($response, 'alert-success') !== false) {
        log_msg("✅ Claim BERHASIL! 0.00000250 USDT sent to FaucetPay", "SUCCESS");
    } else {
        log_msg("⏳ Cooldown atau belum siap", "WARN");
    }

    countdown(COOLDOWN);
    echo "\n";
}