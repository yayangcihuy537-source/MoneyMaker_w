<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');
$configFile = "OurCoin.json";
$cookieFile = __DIR__ . "/OurCoin.txt";

const hitam  = "\033[0;30m";
const merah  = "\033[0;31m";
const hijau  = "\033[0;32m";
const kuning = "\033[0;33m";
const biru   = "\033[0;34m";
const cyan   = "\033[0;36m";
const putih  = "\033[0;37m";
const reset  = "\033[0m";

const R  = "\033[0;31m";
const G  = "\033[0;32m";
const Y  = "\033[0;33m";
const CY = "\033[0;36m";
const W  = "\033[0;37m";
const X  = "\033[0m";

const script_name = "ourcoincash.xyz";
const host        = "https://ourcoincash.xyz";
const in_url      = "https://api.waryono.my.id/in.php";
const res_url     = "https://api.waryono.my.id/res.php";
const SITEKEY     = "G46xX4hfCTAnit8a3E6JF8f1IEew2xYomNDcDJ49";
const UA          = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36";

// ============================================================
// KONTOL
// ============================================================
function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function timer($seconds, $prefix = "waiting") {
    $wait_time = (int)$seconds;
    if ($wait_time < 1) return;
    $frames = array('⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷');
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
            echo "\r\033[K" . Y . " $prefix: " . G . $time_formatted . W . " " . $spinner . X;
            usleep($frame_delay * 1000000);
            $current_frame = ($current_frame + 1) % $frame_count;
            if ((microtime(true) - $start_time) >= 1) {
                break;
            }
        }
        $wait_time--;
    }
    echo "\r\033[K";
}

function skibidixxx($url, $method = 'GET', $data = array(), $headers = array(), $follow = true) {
    global $cookieFile;
    $ch = curl_init();
    $final_headers = array();
    foreach ($headers as $header) {
        $final_headers[] = $header;
    }
    $options = array(
        CURLOPT_URL            => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER         => true,
        CURLOPT_FOLLOWLOCATION => $follow,
        CURLOPT_SSL_VERIFYHOST => 0,
        CURLOPT_SSL_VERIFYPEER => 0,
        CURLOPT_HTTPHEADER     => $final_headers,
        CURLOPT_CONNECTTIMEOUT => 60,
        CURLOPT_TIMEOUT        => 60,
        CURLOPT_COOKIEFILE     => $cookieFile,
        CURLOPT_COOKIEJAR      => $cookieFile,
        CURLOPT_USERAGENT      => UA
    );
    if (strtoupper($method) === 'POST') {
        $options[CURLOPT_POST] = true;
        if (is_array($data)) {
            $options[CURLOPT_POSTFIELDS] = http_build_query($data);
        } else {
            $options[CURLOPT_POSTFIELDS] = $data;
        }
    }
    curl_setopt_array($ch, $options);
    $response = curl_exec($ch);
    if ($response) {
        $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
        $body = substr($response, $header_size);
        $code = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
        $head = substr($response, 0, $header_size);
        curl_close($ch);
        return array("body" => $body, "code" => $code, "head" => $head);
    } else {
        curl_close($ch);
        echo W . "\nwiwok detok, retry...\n" . X;
        sleep(2);
        return skibidixxx($url, $method, $data, $headers, $follow);
    }
}

function curl_solver($url, $method = 'GET', $data = array(), $headers = array()) {
    $ch = curl_init();
    $options = array(
        CURLOPT_URL            => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT        => 30,
        CURLOPT_CONNECTTIMEOUT => 15
    );
    if (!empty($headers)) $options[CURLOPT_HTTPHEADER] = $headers;
    if (strtoupper($method) === 'POST') {
        $options[CURLOPT_POST] = true;
        $options[CURLOPT_POSTFIELDS] = $data;
    }
    curl_setopt_array($ch, $options);
    $resp = curl_exec($ch);
    curl_close($ch);
    return $resp;
}

// ============================================================
// KONTOL
// ============================================================
function solve_adslab($apikey) {
    $headers = array("Content-Type: application/json");
    $body = json_encode(array(
        "apikey"  => $apikey,
        "methods" => "adslab",
        "domain"  => "ourcoincash.xyz",
        "sitekey" => SITEKEY,
        "json"    => 1
    ));
    $request = curl_solver(in_url, "POST", $body, $headers);
    $json = json_decode($request, true);

    if (!isset($json['status']) || $json['status'] != 1) {
        $err = isset($json['request']) ? $json['request'] : 'submit failed';
        echo W . "[CAPTCHA] " . R . $err . X . "\n";
        return false;
    }

    $id = $json["request"];
    echo W . "[CAPTCHA] task: " . CY . $id . W . " waiting" . X;

    $tries = 0;
    while ($tries < 40) {
        sleep(3);
        $url = res_url . "?apikey=" . $apikey . "&action=get&id=" . $id . "&json=1";
        $result = curl_solver($url, "GET");
        $res = json_decode($result, true);

        if (!isset($res['status'])) { echo W . "."; $tries++; continue; }
        if ($res['status'] == 1) {
            $token = $res['request'];
            if (preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i', $token)) {
                echo " " . G . "OK" . X . "\n";
                return $token;
            }
            echo "\n" . W . "[CAPTCHA] " . R . "invalid token: " . $token . X . "\n";
            return false;
        }

        $msg = isset($res['request']) ? $res['request'] : '';
        if ($msg === 'CAPCHA_NOT_READY') { echo W . "."; $tries++; continue; }
        if ($msg === 'ERROR_CAPTCHA_UNSOLVABLE') {
            echo "\r\033[K";
            return false;
        }

        echo "\n" . W . "[CAPTCHA] " . R . $msg . X . "\n";
        return false;
    }
    echo "\r\033[K";
    return false;
}

// ============================================================
// KONTOL
// ============================================================
function solve_adslab_login($apikey) {
    $headers = array("Content-Type: application/json");
    $body = json_encode(array(
        "apikey"  => $apikey,
        "methods" => "adslab",
        "domain"  => "ourcoincash.xyz",
        "sitekey" => SITEKEY,
        "json"    => 1
    ));
    $request = curl_solver(in_url, "POST", $body, $headers);
    $json = json_decode($request, true);

    if (!isset($json['status']) || $json['status'] != 1) {
        $err = isset($json['request']) ? $json['request'] : 'submit failed';
        echo "\r\033[K" . W . "[LOGIN] " . R . "solving gagal: " . $err . X . "\n";
        return false;
    }

    $id = $json["request"];

    $cycleDuration = 3;
    $maxTotal      = 120;

    $mh = curl_multi_init();
    $ch = null;
    $cycleStart = time();
    $startTotal = time();
    $frames = array('⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷');
    $fi = 0;

    echo "\033[?25l";

    while (true) {
        if (time() - $startTotal > $maxTotal) {
            if ($ch) { curl_multi_remove_handle($mh, $ch); curl_close($ch); }
            curl_multi_close($mh);
            echo "\033[?25h";
            echo "\r\033[K" . W . "[LOGIN] " . R . "solving timeout" . X . "\n";
            return false;
        }

        $elapsed   = time() - $cycleStart;
        $remaining = $cycleDuration - $elapsed;
        if ($remaining < 0) $remaining = 0;

        $time_str = sprintf('%02d:%02d:%02d', floor($remaining/3600), floor(($remaining%3600)/60), $remaining%60);

        $isZero = ($remaining <= 0);
        $blinkOn = true;
        if ($isZero) {
            $blinkOn = (int)(microtime(true) * 6) % 2 === 0;
        }

        if ($blinkOn) {
            echo "\r" . W . "[LOGIN] " . CY . "solving adsLab captcha " . Y . $time_str . " " . CY . $frames[$fi] . X;
        } else {
            echo "\r" . str_repeat(" ", 60) . "\r";
        }
        flush();
        $fi = ($fi + 1) % 8;

        if ($remaining == 0 && $ch === null) {
            $url = res_url . "?apikey=" . $apikey . "&action=get&id=" . $id . "&json=1";
            $ch = curl_init();
            curl_setopt($ch, CURLOPT_URL, $url);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_TIMEOUT, 10);
            curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
            curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
            curl_multi_add_handle($mh, $ch);
        }

        curl_multi_exec($mh, $running);

        while ($info = curl_multi_info_read($mh)) {
            if ($ch && $info['handle'] === $ch) {
                $result = curl_multi_getcontent($ch);
                curl_multi_remove_handle($mh, $ch);
                curl_close($ch);
                $ch = null;

                $res = json_decode($result, true);
                if (isset($res['status']) && $res['status'] == 1) {
                    $token = $res['request'];
                    curl_multi_close($mh);
                    echo "\033[?25h";
                    if (preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i', $token)) {
                        echo "\r\033[K" . W . "[LOGIN] " . G . "✓ sukses" . X . "\n";
                        return $token;
                    }
                    echo "\r\033[K" . W . "[LOGIN] " . R . "invalid token" . X . "\n";
                    return false;
                }

                $cycleStart = time();
            }
        }

        usleep(100000);
    }
}

// ============================================================
// KONTOL
// ============================================================
function getConfig($configFile) {
    $data = array();
    if (file_exists($configFile)) {
        $data = json_decode(file_get_contents($configFile), true);
        if (!$data) $data = array();
    }

    $apikey   = isset($data['apikey'])   ? $data['apikey']   : '';
    $email    = isset($data['email'])    ? $data['email']    : '';
    $password = isset($data['password']) ? $data['password'] : '';

    if (empty($apikey) || empty($email) || empty($password)) {
        clear();
        echo W . "===============================================\n";
        echo Y . "     OURCOINCASH.XYZ BY @bgiyannn\n";
        echo W . "===============================================\n";

        if (empty($apikey)) {
            echo W . "API Key Skibidixxx   : " . Y;
            $apikey = trim(fgets(STDIN));
        } else {
            echo W . "API Key Skibidixxx   : " . G . $apikey . "\n" . X;
        }

        if (empty($email)) {
            echo W . "Email  : " . Y;
            $email = trim(fgets(STDIN));
        } else {
            echo W . "Email  : " . G . $email . "\n" . X;
        }

        if (empty($password)) {
            echo W . "Password. : " . Y;
            $password = trim(fgets(STDIN));
        } else {
            echo W . "Password. : " . G . $password . "\n" . X;
        }

        $data = array(
            "apikey"   => $apikey,
            "email"    => $email,
            "password" => $password
        );
        file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
        echo G . "\n[CONFIG] disimpan ke $configFile\n\n" . X;
        sleep(2);
    }

    return $data;
}

// ============================================================
// KONTOL
// ============================================================
function parse_csrf($html) {
    if (preg_match('/name="csrf_token_name"\s+id="[^"]*"\s+value="([^"]+)"/', $html, $m)) return $m[1];
    if (preg_match('/name="csrf_token_name"\s+value="([^"]+)"/', $html, $m)) return $m[1];
    if (preg_match('/name="csrf_token_name" value="([^"]+)"/', $html, $m)) return $m[1];
    return null;
}

function parse_token($html) {
    if (preg_match('/name="token"\s+value="([^"]+)"/', $html, $m)) return $m[1];
    if (preg_match('/name="token" value="([^"]+)"/', $html, $m)) return $m[1];
    return null;
}

function parse_balance($html) {
    if (preg_match('/class="acc-amount"[^>]*>\s*<i[^>]*><\/i>\s*([\d,\.]+)/i', $html, $m)) {
        return (float)str_replace(',', '', $m[1]);
    }
    if (preg_match('/Balance.*?([\d,]{4,}\.\d{2})/s', $html, $m)) {
        return (float)str_replace(',', '', $m[1]);
    }
    return null;
}

function parse_faucet_status($html) {
    $status = "UNKNOWN";
    if (preg_match('/<h4 class="lh-1 mb-1">\s*([A-Z]+)\s*<\/h4>/', $html, $m)) {
        $status = trim($m[1]);
    }
    $reward = null;
    if (preg_match('/id="faucetRewardValue">\s*([\d,\.]+)\s*</', $html, $m)) {
        $reward = (int)str_replace(',', '', $m[1]);
    }
    $claimsLeft = null;
    if (preg_match('/([\d,]+)\/[\d,]+\s*<\/h4>\s*<h6[^>]*>claims left/', $html, $m)) {
        $claimsLeft = (int)str_replace(',', '', $m[1]);
    }
    return array(
        "status"      => $status,
        "reward"      => $reward,
        "claims_left" => $claimsLeft
    );
}

// ============================================================
// KONTOL
// ============================================================
function base_headers($referer = '') {
    $h = array(
        'host: ourcoincash.xyz',
        'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
        'sec-ch-ua-platform: "Android"',
        'sec-ch-ua-mobile: ?1',
        'upgrade-insecure-requests: 1',
        'user-agent: ' . UA,
        'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'sec-fetch-site: same-origin',
        'sec-fetch-mode: navigate',
        'sec-fetch-user: ?1',
        'sec-fetch-dest: document',
        'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
    );
    if ($referer) $h[] = 'referer: ' . $referer;
    return $h;
}

function post_headers($referer = '') {
    $h = array(
        'host: ourcoincash.xyz',
        'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
        'sec-ch-ua-platform: "Android"',
        'sec-ch-ua-mobile: ?1',
        'origin: https://ourcoincash.xyz',
        'content-type: application/x-www-form-urlencoded',
        'upgrade-insecure-requests: 1',
        'user-agent: ' . UA,
        'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'sec-fetch-site: same-origin',
        'sec-fetch-mode: navigate',
        'sec-fetch-user: ?1',
        'sec-fetch-dest: document',
        'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
    );
    if ($referer) $h[] = 'referer: ' . $referer;
    return $h;
}

// ============================================================
// KONTOL
// ============================================================
function is_session_valid() {
    global $cookieFile;
    if (!file_exists($cookieFile) || filesize($cookieFile) == 0) return false;
    $r = skibidixxx(host . "/dashboard", 'GET', array(), base_headers(host . "/"));
    return (strpos($r['body'], 'Logout') !== false);
}

// ============================================================
// KONTOL
// ============================================================
function maskEmail($email) {
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) return $email;
    list($user, $domain) = explode('@', $email);
    $len = strlen($user);
    if ($len <= 4) return substr($user, 0, 1) . '****' . '@' . $domain;
    return substr($user, 0, 2) . '****' . substr($user, -2) . '@' . $domain;
}

// ============================================================
// KONTOL
// ============================================================
function do_login($email, $password, $apikey) {
    $masked = maskEmail($email);

    echo W . "[LOGIN] " . CY . "user: " . W . $masked . X . "\n";

    $r = skibidixxx(host . "/login", 'GET', array(), base_headers(host . "/"));

    if ($r['code'] != 200) {
        echo W . "[LOGIN] " . R . "gagal akses halaman login" . X . "\n";
        return false;
    }

    $csrf = parse_csrf($r['body']);
    if (!$csrf) {
        echo W . "[LOGIN] " . R . "csrf tidak ditemukan!" . X . "\n";
        return false;
    }

    $captcha = solve_adslab_login($apikey);
    if (!$captcha) {
        return false;
    }

    $payload = array(
        "email"              => $email,
        "password"           => $password,
        "captcha"            => "adslabpro",
        "csrf_token_name"    => $csrf,
        "alcaptcha-response" => $captcha
    );
    $r2 = skibidixxx(host . "/auth/login", 'POST', $payload, post_headers(host . "/login"), false);

    if ($r2['code'] == 303 && strpos($r2['head'], '/dashboard') !== false) {
        skibidixxx(host . "/dashboard", 'GET', array(), base_headers(host . "/login"));
        return true;
    }
    if (strpos($r2['body'], 'Logout') !== false) {
        return true;
    }

    echo W . "[LOGIN] " . R . "✗ gagal" . X . "\n";
    return false;
}

// ============================================================
// KONTOL
// ============================================================
function get_balance() {
    $r = skibidixxx(host . "/dashboard", 'GET', array(), base_headers(host . "/"));
    if (strpos($r['body'], 'Logout') === false) return null;
    return parse_balance($r['body']);
}

// ============================================================
// KONTOL
// ============================================================
function claim_faucet($apikey) {
    $r = skibidixxx(host . "/faucet", 'GET', array(), base_headers(host . "/dashboard"));

    if (strpos($r['body'], 'Logout') === false) {
        return array("ok" => false, "error" => "session_invalid");
    }

    $info = parse_faucet_status($r['body']);
    echo W . "[FAUCET] " . CY . "status: " . Y . $info['status']
       . W . " | reward: " . Y . $info['reward']
       . W . " | claims left: " . Y . $info['claims_left'] . X . "\n";

    if ($info['status'] !== 'READY') {
        if (preg_match('/<h4 class="lh-1 mb-1">(\d+)<\/h4>\s*<h6 class="mb-0">minutes/', $r['body'], $m)) {
            return array("ok" => false, "cooldown" => (int)$m[1] * 60);
        }
        return array("ok" => false, "cooldown" => 0);
    }

    $csrf  = parse_csrf($r['body']);
    $token = parse_token($r['body']);
    if (!$csrf || !$token) {
        return array("ok" => false, "error" => "no_csrf_token");
    }

    echo W . "[FAUCET] " . CY . "solving adsLab captcha..." . X . "\n";
    $captcha = solve_adslab($apikey);
    if (!$captcha) {
        return array("ok" => false, "error" => "captcha_failed");
    }

    $payload = array(
        "csrf_token_name"    => $csrf,
        "token"              => $token,
        "captcha"            => "adslabpro",
        "alcaptcha-response" => $captcha
    );
    $r2 = skibidixxx(host . "/faucet/verify", 'POST', $payload, post_headers(host . "/faucet"), false);

    if ($r2['code'] == 303) {
        return array("ok" => true);
    }
    if ($r2['code'] == 200) {
        return array("ok" => false, "error" => "http_200_response");
    }
    return array("ok" => false, "error" => "unknown_response_" . $r2['code']);
}

// ============================================================
// KONTOL
// ============================================================
clear();
$config   = getConfig($configFile);
$apikey   = $config['apikey'];
$email    = $config['email'];
$password = $config['password'];

clear();
echo W . "===============================================\n";
echo Y . "                 Ourcoincash.xyz\n";
echo W . "===============================================\n";

// 
if (is_session_valid()) {
    $loggedIn = true;
} else {
    $loggedIn = do_login($email, $password, $apikey);
}

if (!$loggedIn) {
    echo W . "[!] " . R . "login gagal, keluar." . X . "\n";
    exit;
}

// 
$balance = get_balance();
if ($balance === null) {
    echo W . "[!] " . R . "gagal ambil balance. session mungkin gak valid." . X . "\n";
    echo W . "[!] " . Y . "coba login ulang..." . X . "\n";
    if (!do_login($email, $password, $apikey)) {
        echo W . "[!] " . R . "login gagal, keluar." . X . "\n";
        exit;
    }
    $balance = get_balance();
    if ($balance === null) {
        echo W . "[!] " . R . "masih gagal, keluar." . X . "\n";
        exit;
    }
}

// 
echo "\n";
echo W . "Email    : " . CY . maskEmail($email) . X . "\n";
echo W . "Balance  : " . G . number_format($balance, 2) . " coins" . X . "\n\n";

// 
while (true) {
    echo W . "-----------------------------------------------\n";

    $before = get_balance();
    if ($before === null) {
        echo W . "[!] " . Y . "session hilang, re-login..." . X . "\n";
        if (!do_login($email, $password, $apikey)) {
            echo W . "[!] " . R . "re-login gagal, keluar." . X . "\n";
            exit;
        }
        sleep(2);
        continue;
    }

    $result = claim_faucet($apikey);

    if (isset($result['ok']) && $result['ok'] === true) {
        sleep(3);
        $after = get_balance();
        $diff  = $after - $before;

        if ($diff > 0) {
            echo W . "[CLAIM] " . G . "✓ +" . number_format($diff, 2) . " coins"
               . W . " | balance: " . G . number_format($after, 2) . X . "\n";
            timer(5, "  waiting");
        } else {
            echo W . "[CLAIM] " . Y . "⚠ response OK tapi balance gak berubah ("
               . number_format($before, 2) . " -> " . number_format($after, 2) . ")" . X . "\n";
            echo W . "        kemungkinan captcha ditolak server. retry 5s..." . X . "\n";
            sleep(5);
        }
    }
    elseif (isset($result['cooldown'])) {
        if ($result['cooldown'] <= 0) {
            timer(5, "  waiting");
        } else {
            echo W . "[COOLDOWN] " . Y . sprintf('%02d:%02d', floor($result['cooldown']/60), $result['cooldown']%60) . X . "\n";
            timer($result['cooldown'], "  waiting");
        }
    }
    else {
        $err = isset($result['error']) ? $result['error'] : 'unknown';

        if ($err === 'captcha_failed' || $err === 'unknown_response_200') {
            echo W . "-----------------------------------------------\n";
            continue;
        }

        echo W . "[CLAIM] " . R . "✗ gagal: " . $err . X . "\n";

        if ($err === 'session_invalid') {
            echo W . "[!] " . Y . "session hilang, re-login..." . X . "\n";
            if (!do_login($email, $password, $apikey)) {
                echo W . "[!] " . R . "re-login gagal, keluar." . X . "\n";
                exit;
            }
        } else {
            sleep(5);
        }
    }
}
