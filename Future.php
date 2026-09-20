<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');
$configFile = "config.json";
$tod = "cookies.txt";

const hitam  = "\033[0;30m";
const merah  = "\033[0;31m";
const hijau  = "\033[0;32m";
const kuning = "\033[0;33m";
const biru   = "\033[0;34m";
const cyan   = "\033[0;36m";
const putih  = "\033[0;37m";
const reset  = "\033[0m";

const bg_hitam  = "\033[40m";
const bg_merah  = "\033[41m";
const bg_hijau  = "\033[42m";
const bg_kuning = "\033[43m";
const bg_biru   = "\033[44m";
const bg_ungu   = "\033[45m";
const bg_cyan   = "\033[46m";
const bg_putih  = "\033[47m";

const script_name = "limefaucet.com";
const host        = "https://limefaucet.com";
const ref_code    = "TN04h4nLzInrMZ0R";
const api_in      = "https://api.waryono.my.id/in.php";
const api_out     = "https://api.waryono.my.id/res.php";

function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function uf() {
    return md5(uniqid(mt_rand(), true));
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
        CURLOPT_SSL_VERIFYHOST => 1,
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_HTTPHEADER     => $final_headers,
        CURLOPT_CONNECTTIMEOUT => 999,
        CURLOPT_TIMEOUT        => 999,
        CURLOPT_COOKIEFILE     => 'cookies.txt',
        CURLOPT_COOKIEJAR      => 'cookies.txt'
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
        return "ERROR_SIGNAL";
    }
}

function timer($seconds, $prefix = "[!] please wait") {
    $wait_time = (int)$seconds;
    if ($wait_time <= 0) { $wait_time = 1; }
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
    echo "\r                                        \r";
}

function lime($apikey, $gambar) {
    $headers = ["Content-Type: application/json"];
    $body = json_encode([
        "apikey"  => $apikey,
        "methods" => "moonptc",
        "base64"  => $gambar,
        "json"    => 1
    ]);
    $request = skibidixxx(api_in, "POST", $body, $headers);
    if (strpos($request, "ERROR_WRONG_METHOD") !== false) { echo putih."Error: ".merah."ERROR_WRONG_METHOD\n"; exit; }
    if (strpos($request, "ERROR_KEY_DOES_NOT_EXIST") !== false) { echo putih."Error: ".merah."ERROR_KEY_DOES_NOT_EXIST\n"; exit; }
    if (strpos($request, "ERROR_METHOD_NOT_SPECIFIED") !== false) { echo putih."Error: ".merah."ERROR_METHOD_NOT_SPECIFIED\n"; exit; }
    if (strpos($request, "ERROR_NO_SUCH_METHOD") !== false) { echo putih."Error: ".merah."ERROR_NO_SUCH_METHOD\n"; exit; }
    if (strpos($request, "ERROR_DATABASE_CONNECTION_FAILED") !== false) { echo putih."Error: ".merah."ERROR_DATABASE_CONNECTION_FAILED\n"; exit; }
    if (strpos($request, "ERROR_TOO_MANY_REQUESTS") !== false) { echo putih."Error: ".merah."ERROR_TOO_MANY_REQUESTS"; sleep(1.8); echo "\r                                               \r"; return "ERROR_TOO_MANY_REQUESTS"; }
    if (strpos($request, "ERROR_WRONG_USER_KEY") !== false) { echo putih."Error: ".merah."ERROR_WRONG_USER_KEY\n"; exit; }
    if (strpos($request, "ERROR_ZERO_BALANCE") !== false) { echo putih."Error: ".merah."ERROR_ZERO_BALANCE\n"; exit; }
    if (strpos($request, "ERROR_BAD_PARAMETERS") !== false) { echo putih."Error: ".merah."ERROR_BAD_PARAMETERS\n"; exit; }
    if (strpos($request, "ERROR_EMPTY_IMAGE") !== false) { echo putih."Error: ".merah."ERROR_EMPTY_IMAGE\n"; exit; }
    if (strpos($request, "ERROR_UNKNOWN") !== false) { echo putih."Error: ".merah."ERROR_UNKNOWN\n"; exit; }
    $json = json_decode($request, true);
    if (!isset($json["request"])) {
        echo putih."Error: ".merah."Response tidak dikenal: ".$request."\n"; exit;
    }
    $id = $json["request"];
    reload:
    timer(2, "  captcha..");
    $url = api_out . "?apikey=".$apikey."&action=get&id=".$id."&json=1";
    $result = skibidixxx($url, "GET", []);
    if (strpos($result, "ERROR_BAD_PARAMETERS") !== false) { echo putih."Error: ".merah."ERROR_BAD_PARAMETERS\n"; exit; }
    if (strpos($result, "Database connection failed") !== false) { echo putih."Error: ".merah."Database connection failed\n"; exit; }
    if (strpos($result, "WRONG_CAPTCHA_ID") !== false) { echo putih."Error: ".merah."WRONG_CAPTCHA_ID"; sleep(1.8); echo "\r                                               \r"; return "WRONG_CAPTCHA_ID"; }
    if (strpos($result, "ERROR_SOLVE_PENDING") !== false) { echo putih."Error: ".merah."ERROR_SOLVE_PENDING"; sleep(1.8); echo "\r                                               \r"; return "ERROR_SOLVE_PENDING"; }
    if (strpos($result, "CAPCHA_NOT_READY") !== false) { echo putih."Error: ".merah."CAPCHA_NOT_READY"; sleep(1.8); echo "\r                                               \r"; goto reload; }
    if (strpos($result, "ERROR_CAPTCHA_UNSOLVABLE") !== false) { echo putih."Error: ".merah."ERROR_CAPTCHA_UNSOLVABLE"; sleep(1.8); echo "\r                                               \r"; return "ERROR_CAPTCHA_UNSOLVABLE"; }
    if (strpos($result, "ERROR_BAD_REQUEST") !== false) { echo "Error: ".merah."ERROR_BAD_REQUEST\n"; exit; }
    if (strpos($result, "INTENAL_SERVER_ERROR") !== false) { echo "Errro: ".merah."INTENAL_SERVER_ERROR"; sleep(1.8); echo "\r                                               \r"; return "INTENAL_SERVER_ERROR"; }
    $json = json_decode($result, true);
    $res = $json["request"] ?? '';
    $arr = explode(':', $res);
    $clean_res = end($arr);
    if (!is_numeric(trim($clean_res))) {
        echo putih."Error: ".merah."Jawaban tidak valid: ".$res."\n";
        return "BAD_ANSWER";
    }
    return ["captcha" => trim($clean_res)];
}

function getConfig($configFile) {
    if (!file_exists($configFile)) {
        echo putih . "API Key: " . kuning;
        $apikey = trim(fgets(STDIN));
        echo putih . "Email: " . kuning;
        $email = trim(fgets(STDIN));
        $data = [
            "apikey"   => $apikey,
            "email"    => $email
        ];
        file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
        echo hijau . "disimpan ke $configFile\n\n" . reset;
        sleep(3);
        return $data;
    }
    return json_decode(file_get_contents($configFile), true);
}

function banner() {
    echo putih  . "---------------------------------------------------\n";
    echo putih. "Script Name : " . hijau . script_name."\n";
    echo putih  . "---------------------------------------------------\n";
}

function suki(&$a, &$b, &$c) {
    $a = [
        "host: limefaucet.com",
        "user-agent: Mozilla/5.0 (Linux; Android 16; 23076RN4BI Build/BP4A.251205.006) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.88 Mobile Safari/537.36",
        "content-type: application/json",
        "origin: https://limefaucet.com",
        "accept: */*",
        "x-requested-with: Banna.com",
        "referer: https://limefaucet.com/faucet"
    ];

    $b = [
        "host: limefaucet.com",
        "user-agent: Mozilla/5.0 (Linux; Android 16; 23076RN4BI Build/BP4A.251205.006) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.88 Mobile Safari/537.36",
        "accept: */*",
        "x-requested-with: Banna.com",
        "referer: https://limefaucet.com/dashboard"
    ];

    $c = [
        "host: limefaucet.com",
        "user-agent: Mozilla/5.0 (Linux; Android 16; 23076RN4BI Build/BP4A.251205.006) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.88 Mobile Safari/537.36",
        "content-type: application/json",
        "origin: https://limefaucet.com",
        "accept: */*",
        "x-requested-with: Banna.com",
        "referer: https://limefaucet.com/faucet"
    ];
}

home:
clear();
banner();

$config   = getConfig($configFile);
$apikey   = $config['apikey'];
$email    = $config['email'];

clear();
banner();

suki($a, $b, $c);

$home = skibidixxx(host."/api/auth/me", "GET", [], $b);
if (strpos($home, "email") !== false) {
    $q = json_decode($home, true);
    $uid = $q["user"]["id"] ?? ($q["id"] ?? '?');
    $uemail = $q["user"]["email"] ?? ($q["email"] ?? $email);
    $ubal = $q["user"]["balance_usd"] ?? ($q["balance_usd"] ?? '0');

    echo putih . "ID       " . biru . $uid . "\n";
    echo putih . "Email    " . biru . $uemail . "\n";

    asu:
    $info = skibidixxx(host."/api/faucet/info", "GET", [], $b);
    $i = json_decode($info, true);

    $remaining = (int)($i['time_remaining_seconds'] ?? 0);
    if ($remaining > 0) {
        timer($remaining, "  wait..");
        goto asu;
    }

    $generate = skibidixxx(host."/api/faucet/ac-captcha/challenge", "POST", "{}", $a);
    $d = json_decode($generate, true);

    if (isset($d['session_id']) && isset($d['challenge']['image'])) {
        $sid    = $d['session_id'];
        $gambar = $d['challenge']['image'];

        if (strpos($gambar, "data:image/gif;base64,") === false) {
            timer(5, "  retry..");
            goto asu;
        }

        $anti = lime($apikey, $gambar);
        if (is_array($anti)) {
            $asw = (int)$anti["captcha"];

            $payload = json_encode([
                "session_id" => $sid,
                "candidate_index" => $asw
            ]);

            $veri = skibidixxx(host."/api/faucet/ac-captcha/verify", "POST", $payload, $a);
            $v = json_decode($veri, true);

            if (($v['ok'] ?? false) === true && isset($v['token'])) {
                $verifiedToken = $v['token'];
                $data = json_encode(["captcha_token" => $verifiedToken]);
                $claim = skibidixxx(host."/api/faucet/claim", "POST", $data, $a);
                $cl = json_decode($claim, true);

                if (isset($cl['roll_number'])) {
                    echo putih . "[SUCCESS] " . hijau . "roll ".$cl['roll_number'].putih." reward ".hijau."$".$cl['reward_usd']."\n";
                    timer(180, "  next claim");
                    goto asu;
                } else {
                    timer(5, "  retry..");
                    goto asu;
                }

            } elseif (($v['error'] ?? '') === 'too_fast') {
                $retry_ms = $v['retry_after_ms'] ?? 250;
                sleep(ceil($retry_ms / 1000));
                goto asu;
            } elseif (($v['error'] ?? '') === 'wrong') {
                timer(2, "  new challenge..");
                goto asu;
            } elseif (($v['error'] ?? '') === 'blocked' || isset($v['locked_until'])) {
                $until = (float)($v['locked_until'] ?? 0);
                $secs = ceil(($until - round(microtime(true) * 1000)) / 1000);
                if ($secs < 1) $secs = 60;
                timer(min($secs, 900), "  blocked wait..");
                goto asu;
            } else {
                timer(5, "  retry..");
                goto asu;
            }

        } elseif (is_string($anti) && in_array($anti, ["WRONG_CAPTCHA_ID", "ERROR_CAPTCHA_UNSOLVABLE", "ERROR_TOO_MANY_REQUESTS", "ERROR_SOLVE_PENDING", "INTENAL_SERVER_ERROR", "BAD_ANSWER"])) {
            timer(3, "  retry..");
            goto asu;
        } else {
            timer(5, "  retry..");
            goto asu;
        }

    } elseif (isset($d['error']) && $d['error'] === 'blocked') {
        timer(60, "  blocked wait..");
        goto asu;
    } elseif (isset($d['locked_until'])) {
        $until = (float)$d['locked_until'];
        $secs = ceil(($until - round(microtime(true) * 1000)) / 1000);
        if ($secs < 1) $secs = 60;
        timer(min($secs, 900), "  locked wait..");
        goto asu;
    } else {
        timer(5, "  retry..");
        goto asu;
    }

} else {
    @unlink($tod);
    echo putih . "login required!...\n";

    $data = json_encode(["email" => $email, "referral_code" => ref_code]);
    $p = skibidixxx(host."/api/auth/login", "POST", $data, $a);

    if (strpos($p, "email") !== false) {
        $j = json_decode($p, true);
        $uid = $j["user"]["id"] ?? '?';
        $uemail = $j["user"]["email"] ?? $email;
        echo putih . "login success.. > ID: " . hijau . $uid . putih . " | " . hijau . $uemail . "\n";
        sleep(3);
        goto home;
    } else {
        echo kuning . "Login Failed!, try again.. or check web!\n";
        @unlink($tod);
        @unlink($configFile);
        exit;
    }
}

