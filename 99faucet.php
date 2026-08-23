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
const bg_hitam  = "\033[40m";
const bg_merah  = "\033[41m";
const bg_hijau  = "\033[42m";
const bg_kuning = "\033[43m";
const bg_biru   = "\033[44m";
const bg_ungu   = "\033[45m";
const bg_cyan   = "\033[46m";
const bg_putih  = "\033[47m";

const version     = "1.0";
const script_name = "99faucet.com";
const host        = "https://99faucet.com";
const api_in      = "https://api.waryono.my.id/in.php";

function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function uf() {
    return md5(uniqid(mt_rand(), true));
}

function zone() {
    return date_default_timezone_get();
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

function slider($app_id, $public_key, $version, $reff, $apikey) {
    $headers = ["Content-Type: application/json"];
    $body = json_encode([
        "apikey"     => $apikey,
        "app_id"     => $app_id,
        "methods"    => "rslider",
        "public_key" => $public_key,
        "version"    => $version,
        "referer"    => $reff,
        "json"       => 1
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
    $id = $json["request"];
    reload:
    timer(3);
    $url = "https://api.waryono.my.id/res.php?apikey=".$apikey."&id=".$id."&json=1";
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
    $res = $json["request"];
    preg_match('/rs_token:(\d+),rs_res:([^,]+)/', $res, $match);
    return [
        "rs_token" => $match[1], 
        "rs_res"   => $match[2]
    ];
}

function bypassCloudflare(&$config, $configFile, $target) {
    echo putih . "Cloudflare! wait.. ";
    $python_cmd = "python exec.py " . $target ." 2>/dev/null";
    $output = exec($python_cmd);
    $data_bypass = json_decode($output, true);
    if (isset($data_bypass['cf_clearance']) && !empty($data_bypass['cf_clearance'])) {
        $full_new_cf = $data_bypass['cf_clearance'];
        $new_ua = $data_bypass['user_agent'];
        $old_cookie = $config['cookie'];
        if (strpos($full_new_cf, '=') !== false) {
            $new_token_value = explode('=', $full_new_cf)[1];
        } else {
            $new_token_value = $full_new_cf;
        }
        $pattern = '/cf_clearance=[^;]+/';
        $replacement = "cf_clearance=" . $new_token_value;
        if (preg_match($pattern, $old_cookie)) {
            $new_cookie_str = preg_replace($pattern, $replacement, $old_cookie);
        } else {
            $new_cookie_str = rtrim($old_cookie, "; ") . "; " . $replacement;
        }
        $config['cookie'] = $new_cookie_str;
        $config['user_agent'] = $new_ua;
        file_put_contents($configFile, json_encode($config, JSON_PRETTY_PRINT));
        echo hijau . "Success Solver Cloudflare! WAF\n";
        echo putih."------------------------------------------------------\n";
        sleep(2);
        return true;
    } else {
        echo merah . "Error Bypass\n";
        echo putih."------------------------------------------------------\n";
        return false;
    }
}

function getConfig($configFile) {
    if (!file_exists($configFile)) {
        echo putih . "API Key: " . kuning;
        $apikey = trim(fgets(STDIN));
        echo putih . "Cookie: " . kuning;
        $coki = trim(fgets(STDIN));
        $data = ["apikey" => $apikey, "cookie" => $coki];
        file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
        echo hijau . "disimpan ke $configFile\n\n" . reset;
        sleep(3);
        return $data;
    }
    return json_decode(file_get_contents($configFile), true);
}

function banner() {
    echo putih  . "-----------------------------------------------------\n";
    echo cyan   . hijau .script_name.putih." Rscap Slider + Seledroid (opsional)\n";
    echo putih  . "-----------------------------------------------------\n\n";
}

login:
clear();
banner();

$config = getConfig($configFile);
$apikey = $config['apikey'];
$coki   = $config['cookie'];
$ua     = $config['user_agent'] ?? "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36";

dash:
clear();
banner();

$a = [
    "host: 99faucet.com",
    "user-agent: " . $ua,
    "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
    "referer: ".host."/faucet/pepe",
    "cookie: " . $coki
];

$url = host."/dashboard";
$dash = skibidixxx($url, "GET", [], $a);

if ($dash == "ngelek" || strpos($dash, "Just a moment") !== false) {
    bypassCloudflare($config, $configFile, $url);
    $coki = $config['cookie'];
    $ua   = $config['user_agent'];
    goto dash;
}

if (strpos($dash, "Dashboard | 99Faucet") !== false) {
    preg_match_all('/<a href="https:\/\/99faucet\.com\/faucet\/([^"]+)" class="">/', $dash, $matches);
    $currencies = $matches[1];
    usort($currencies, function($a, $b) {
        return strlen($a) - strlen($b);
    });
    $columns = 4;
    $total = count($currencies);
    for ($i = 0; $i < $total; $i++) {
        $num = $i + 1;
        $currency = strtoupper($currencies[$i]);
        echo putih."(" . str_pad($num, 2, ' ', STR_PAD_LEFT) . ") ".hijau . str_pad($currency, 6, ' ') . "".putih;
        if (($i + 1) % $columns == 0 || $i == $total - 1) {
            echo "\n";
        }
    }
    echo putih."chosee: ".merah;
    $handle = fopen("php://stdin", "r");
    $input = trim(fgets($handle));
    fclose($handle);
    if (!is_numeric($input)) {
        echo putih."Invalid input! Please enter a number.\n";
        sleep(2);
        goto dash;
    }
    $input = (int)$input;
    if ($input < 1 || $input > count($currencies)) {
        echo putih."Invalid selection! Please choose between 1-" . count($currencies) . "\n";
        sleep(4);
        goto dash;
    }
    $selectedCurrency = $currencies[$input-1];
    $coin = strtolower($selectedCurrency);
    echo putih."chosee: ".hijau .$coin. "\n\n";

    reload:
    while(true){
        // Header untuk GET faucet
        $a_faucet = [
            "host: 99faucet.com",
            "user-agent: " . $ua,
            "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
            "referer: ".host."/dashboard",
            "cookie: " . $coki
        ];

        // Header untuk POST claim (referer disesuaikan dengan coin)
        $c_post = [
            "host: 99faucet.com",
            "origin: ".host,
            "content-type: application/x-www-form-urlencoded",
            "user-agent: " . $ua,
            "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
            "referer: " . host . "/faucet/" . $coin,
            "cookie: " . $coki
        ];

        $url_faucet = host."/faucet/".$coin;
        $faucet = skibidixxx($url_faucet, "GET", [], $a_faucet);

        if ($faucet == "ngelek" || strpos($faucet, "Just a moment") !== false) {
            bypassCloudflare($config, $configFile, $url_faucet);
            $coki = $config['cookie'];
            $ua   = $config['user_agent'];
            goto reload;
        }

        // ===== DETEKSI SHORTLINK PAKE TOKEN =====
        // Cek apakah ada input name="token" atau id="token"
        if (strpos($faucet, 'name="token"') === false && strpos($faucet, 'id="token"') === false) {
            echo putih."------------------------------------------------------\n";
            echo kuning."⚠️  Halaman tidak memiliki token claim (shortlink terdeteksi).\n";
            echo putih."Selesaikan minimal 1 shortlinks, lalu tekan Enter untuk reload...";
            trim(fgets(STDIN));
            // Setelah user selesai, reload halaman faucet
            goto reload;
        }

        // Ambil token
        if (preg_match('/name="token"\s+value="([^"]+)"/', $faucet, $token_match)) {
            $token = $token_match[1];
        } else {
            // fallback
            $token = explode('"', explode('<input type="hidden" name="token" value="', $faucet)[1])[0];
        }

        $app_id = "1044";
        $public_key = "ws1WNm5E0xjtnezLT8r9";
        $version = "v5";
        $reff = "https://99faucet.com/";

        $bypass = slider($app_id, $public_key, $version, $reff, $apikey);
        if (is_array($bypass)) {
        
            $data = http_build_query([
                "ci_csrf_token" => "",
                "token" => $token,
                "currency" => $coin,
                "captcha" => "rscaptchav37",
                "rscaptcha_token" => $bypass["rs_token"],
                "rscaptcha_response" => $bypass["rs_res"],
                "uf" => uf(),
                "utt" => "Asia/Jakarta",
                "ls" => "id,en-US,en,ms,ru"
            ]);
            timer(5);
            $url_verify = host."/faucet/verify";
            $claim = skibidixxx($url_verify, "POST", $data, $c_post);
            
            if (strpos($claim, "Good job!") !== false) {
                $msg = explode("'", explode("text: '", $claim)[1])[0];
                $timer_wait = explode(' -', explode('let wait = ', $claim)[1])[0];
                echo hijau.$msg."\n";
                timer($timer_wait);
            } elseif (strpos($claim, "Invalid") !== false){
                echo "Invalid captcha or invalid claim!\n";
                goto reload;
            } elseif (strpos($claim, "The faucet does not have sufficient funds") !== false) {
                echo putih."------------------------------------------------------\n";
                echo kuning."The faucet does not have sufficient funds.\n";
                echo putih."enter to menu..";
                trim(fgets(STDIN));
                goto dash;
            } else {
                echo merah."Error tidak tahu gua anjay!";
                sleep(1.8);
                echo "\r                                  \r";
                goto reload;
            }

        } elseif (in_array($bypass, ["WRONG_CAPTCHA_ID", "ERROR_CAPTCHA_UNSOLVABLE", "ERROR_TOO_MANY_REQUESTS", "ERROR_SOLVE_PENDING", "INTENAL_SERVER_ERROR"])) {
            goto reload;
        } else {
            echo putih . "Error: " . merah . " Tidak di ketahui!! coba lagi...\n";
            goto reload;
        }
    }
} else {
    echo putih."Hiii Login again ....!\n";
    @unlink($configFile);
    sleep(4);
    goto login;
}
