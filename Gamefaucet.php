<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');

$configFile = "config.json";

// GitHub raw URL untuk exec.py
const EXEC_PY_URL = "https://raw.githubusercontent.com/yayangcihuy537-source/MoneyMaker_w/main/exec.py";
const EXEC_PY_LOCAL = "exec.py";

const hitam  = "\033[0;30m";
const merah  = "\033[0;31m";
const hijau  = "\033[0;32m";
const kuning = "\033[0;33m";
const biru   = "\033[0;34m";
const cyan   = "\033[0;36m";
const putih  = "\033[0;37m";
const reset  = "\033[0m";
const bold   = "\033[1m";
const ungu   = "\033[95m";

// Warna khusus koin
const orange_btc = "\033[38;5;214m";
const grey_eth   = "\033[38;5;252m";
const yellow_dog = "\033[38;5;220m";
const grey_ltc   = "\033[38;5;250m";
const green_usdt = "\033[38;5;48m";
const blue_ada   = "\033[38;5;33m";
const blue_xrp   = "\033[38;5;39m";
const orange_bch = "\033[38;5;208m";
const purple_sol = "\033[38;5;135m";
const pink_dot   = "\033[38;5;205m";
const yellow_dai = "\033[38;5;226m";
const orange_xmr = "\033[38;5;202m";
const blue_xtz   = "\033[38;5;27m";
const orange_zec = "\033[38;5;215m";
const white_xlm  = "\033[1;37m";
const red_trx    = "\033[38;5;196m";
const blue_dash  = "\033[38;5;27m";

const version     = "2.0";
const script_name = "gamefaucet.fun";
const host        = "https://gamefaucet.fun";
const in_api      = "https://api.waryono.my.id/in.php";

function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function uf() {
    return md5(uniqid(mt_rand(), true));
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
            echo "\33[1;" . rand(30, 37) . "m🍱 MBG";
            sleep(1);
            echo "\r \r";
            return "ngelek";
        }
    }
}

function getIpAndLocation() {
    $ch = curl_init("http://ip-api.com/json/?fields=query,city,country");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 5);
    $response = curl_exec($ch);
    curl_close($ch);
    
    $data = json_decode($response, true);
    if ($data && isset($data['query'])) {
        return [
            "ip" => $data['query'],
            "location" => $data['city'] . ", " . $data['country']
        ];
    }
    return [
        "ip" => "Unknown IP",
        "location" => "Unknown Location"
    ];
}

function timer($seconds, $prefix = "MENDENGAR PRABOWO PIDATO") {
    $wait_time = (int)$seconds;
    $frames = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘'];
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
    echo "\r                                              \r";
}

function rscaptcha($base64, $apikey) {
    $headers = ["Content-Type: application/json"];
    $body = json_encode([
        "apikey" => $apikey,
        "methods" => "upsidedown_2",
        "image" => $base64,
        "json" => 1
    ]);
    $request = skibidixxx(in_api, "POST", $body, $headers);
    if (strpos($request, "ERROR_") !== false) { 
        return "ERROR_BAD_REQUEST"; 
    }
    $json = json_decode($request, true);
    if (!isset($json["request"])) {
        return "ERROR_BAD_REQUEST";
    }
    $id = $json["request"];
    
    reload:
    timer(2);
    $url = "https://api.waryono.my.id/res.php?apikey=".$apikey."&action=get&id=".$id."&json=1";
    $result = skibidixxx($url, "GET", []);
    if (strpos($result, "WRONG_CAPTCHA_ID") !== false) { return "WRONG_CAPTCHA_ID"; }
    if (strpos($result, "ERROR_SOLVE_PENDING") !== false) { return "ERROR_SOLVE_PENDING"; }
    if (strpos($result, "CAPCHA_NOT_READY") !== false) { goto reload; }
    if (strpos($result, "ERROR_CAPTCHA_UNSOLVABLE") !== false) { return "ERROR_CAPTCHA_UNSOLVABLE"; }
    
    $json = json_decode($result, true);
    if (isset($json["request"])) {
        $res = $json["request"];
        if (preg_match('/x: (\d+), y: (\d+)/', $res, $match)) {
            return ["x" => $match[1], "y" => $match[2]];
        }
    }
    return "ERROR_BAD_REQUEST";
}

/* ═══════════ DOWNLOAD EXEC.PY DARI GITHUB ═══════════ */
function downloadExecPy() {
    if (file_exists(EXEC_PY_LOCAL) && filesize(EXEC_PY_LOCAL) > 100) {
        return true; // udah ada, skip download
    }

    echo putih . "Downloading exec.py from GitHub...\n";
    
    $ch = curl_init(EXEC_PY_URL);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    $content = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($httpCode == 200 && strlen($content) > 100) {
        file_put_contents(EXEC_PY_LOCAL, $content);
        echo hijau . "✔ exec.py downloaded (" . strlen($content) . " bytes)\n";
        return true;
    }

    echo merah . "✖ Gagal download exec.py (HTTP $httpCode)\n";
    return false;
}

/* ═══════════ BYPASS CLOUDFLARE (MODIFIED) ═══════════ */
function bypassCloudflare(&$config, $configFile, $target) {
    echo putih . "Cloudflare! wait.. \n";

    // Auto-download exec.py dari GitHub kalau belum ada
    if (!downloadExecPy()) {
        echo merah . "exec.py tidak tersedia, skip bypass\n";
        return false;
    }

    // Cek Python + Seledroid
    $py_check = shell_exec("python -c \"import seledroid\" 2>&1");
    if (stripos($py_check, 'ModuleNotFoundError') !== false || stripos($py_check, 'No module named') !== false) {
        echo merah . "⚠ Seledroid module belum keinstall!\n";
        echo kuning . "Install dulu: pip install seledroid\n";
        echo kuning . "Atau pastikan APK Seledroid udah keinstall di HP\n";
        return false;
    }

    // Jalankan exec.py
    $python_cmd = "python " . escapeshellarg(EXEC_PY_LOCAL) . " " . escapeshellarg($target) . " 2>/dev/null";
    $output = shell_exec($python_cmd);
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
        echo hijau . "✔ Success Solver Cloudflare! WAF\n";
        echo putih."------------------------------------------\n";
        sleep(2);
        return true;
    } else {
        echo merah . "✖ Error Bypass — output: " . substr($output, 0, 100) . "\n";
        echo putih."------------------------------------------\n";
        return false;
    }
}

function rspayload($html, $x, $y) {
    if (empty($html)) return false;
    $url = "https://api.waryono.my.id/rspayload.php";
    $headers = ["Content-Type: application/json"];
    $data = json_encode(["htmlContent" => $html, "clickX" => (int)$x, "clickY" => (int)$y]);
    $response = skibidixxx($url, "POST", $data, $headers);
    $resJson = json_decode($response, true);
    if (isset($resJson['Payload'])) {
        return ["fingerprint" => $resJson['Payload']];
    }
    return false;
}

function getConfig($configFile) {
    if (!file_exists($configFile)) {
        echo putih . "Masukkan Email Akun: " . kuning;
        $email = trim(fgets(STDIN));
        echo putih . "API Key Waryono: " . kuning;
        $apikey = trim(fgets(STDIN));
        echo putih . "Masukkan Cookie Akun: " . kuning;
        $coki = trim(fgets(STDIN));
        
        $data = ["email" => $email, "apikey" => $apikey, "cookie" => $coki, "earned" => 0, "total_coins" => 0];
        file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
        echo hijau . "Konfigurasi akun berhasil disimpan!\n\n" . reset;
        sleep(2);
        return $data;
    }
    $configData = json_decode(file_get_contents($configFile), true);
    if (!isset($configData['total_coins'])) {
        $configData['total_coins'] = 0;
    }
    return $configData;
}

function banner($email = "Active Account", $earned = "0", $total_coins = "0", $coin_type = "COINS") {
    $earned_text = $earned . " Successful Claims";
    $clean_coins = rtrim(rtrim(number_format($total_coins, 8, '.', ''), '0'), '.');
    if ($clean_coins == "" || $clean_coins == ".") $clean_coins = "0";
    
    $c_lower = strtolower($coin_type);
    
    switch($c_lower) {
        case 'btc': $symbol = "₿"; $c_color = orange_btc; break;
        case 'eth': $symbol = "Ξ"; $c_color = grey_eth; break;
        case 'doge': $symbol = "Ð"; $c_color = yellow_dog; break;
        case 'ltc': $symbol = "Ł"; $c_color = grey_ltc; break;
        case 'usdt': $symbol = "₮"; $c_color = green_usdt; break;
        case 'ada': $symbol = "₳"; $c_color = blue_ada; break;
        case 'xrp': $symbol = "✕"; $c_color = blue_xrp; break;
        case 'bch': $symbol = "Ƀ"; $c_color = orange_bch; break;
        case 'sol': $symbol = "◎"; $c_color = purple_sol; break;
        case 'dot': $symbol = "●"; $c_color = pink_dot; break;
        case 'dai': $symbol = "◈"; $c_color = yellow_dai; break;
        case 'xmr': $symbol = "ɱ"; $c_color = orange_xmr; break;
        case 'xtz': $symbol = "ꜩ"; $c_color = blue_xtz; break;
        case 'zec': $symbol = "ⓩ"; $c_color = orange_zec; break;
        case 'xlm': $symbol = "🚀"; $c_color = white_xlm; break;
        case 'trx': $symbol = "🔻"; $c_color = red_trx; break;
        case 'dash': $symbol = "💠"; $c_color = blue_dash; break;
        default: $symbol = "🪙"; $c_color = kuning; break;
    }

    $coins_text  = $clean_coins . " " . strtoupper($coin_type);
    $time_text   = date('d-m-Y H:i:s');
    $geo_info    = getIpAndLocation();
    $ip_text     = $geo_info['query'] ?? $geo_info['ip'];
    $loc_text    = $geo_info['location'];

    echo cyan . "  ==========================================\n";
    echo cyan . "           " . bold . putih . "G A M E   F A U C E T" . cyan . "\n";
    echo cyan . "  ==========================================\n" . reset;
    echo bold . ungu . "  Created by AHD1905 supported by ScriptyXSouu\n" . reset;
    echo cyan . "  ┌────────────────────────────────────────┐\n";
    echo cyan . "  │ 📧 Akun       : " . putih . str_pad($email, 27, ' ', STR_PAD_RIGHT) . cyan . " │\n";
    echo cyan . "  │ ⏰ Waktu      : " . kuning . str_pad($time_text, 27, ' ', STR_PAD_RIGHT) . cyan . " │\n";
    echo cyan . "  │ 🌐 IP         : " . putih . str_pad($ip_text, 27, ' ', STR_PAD_RIGHT) . cyan . " │\n";
    echo cyan . "  │ 📍 Lokasi     : " . putih . str_pad($loc_text, 27, ' ', STR_PAD_RIGHT) . cyan . " │\n";
    echo cyan . "  │ 💰 Total Claim: " . hijau . bold . str_pad($earned_text, 27, ' ', STR_PAD_RIGHT) . cyan . " │\n";
    echo cyan . "  │ " . $c_color . $symbol . cyan . " Total Coin : " . $c_color . bold . str_pad($coins_text, 27, ' ', STR_PAD_RIGHT) . cyan . " │\n";
    echo cyan . "  └────────────────────────────────────────┘\n" . reset;
    echo putih . "  ------------------------------------------\n\n";
}

/* ═══════════ MAIN ENTRY ═══════════ */

login:
clear();
banner("Not Logged In", "0", "0", "COINS");

// Auto-download exec.py dari GitHub di awal
downloadExecPy();

$config = getConfig($configFile);
$accountEmail = $config['email'] ?? "Active Account";
$totalEarned  = $config['earned'] ?? 0;
$totalCoins   = $config['total_coins'] ?? 0;
$apikey       = $config['apikey'];
$coki         = $config['cookie'];
$ua           = $config['user_agent'] ?? "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36";

dash:
$a = [
    "host: ".script_name,
    "user-agent: " . $ua,
    "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
    "referer: ".host."/faucet/pepe",
    "cookie: " . $coki
];

$url = host."/dashboard";
$dash = skibidixxx($url, "GET", [], $a);

if ($dash == "ngelek" || strpos($dash, "Just a moment") !== false) {
    bypassCloudflare($config, $configFile, $url);
    $config = getConfig($configFile);
    $coki = $config['cookie'];
    $ua   = $config['user_agent'];
    goto dash;
}

if (strpos($dash, "Dashboard | GameFaucet") !== false) {
    clear();
    banner($accountEmail, $totalEarned, $totalCoins, "COINS");

    preg_match_all('/<a href="https:\/\/gamefaucet\.fun\/faucet\/([^"]+)" class="">/', $dash, $matches);
    $currencies = $matches[1];
    usort($currencies, function($a, $b) {
        return strlen($a) - strlen($b);
    });
    
    $columns = 2;
    $total = count($currencies);
    
    echo " " . bold . putih . "📌 PILIH MATA UANG FAUCET:" . reset . "\n";
    echo cyan . "  ------------------------------------------" . reset . "\n";

    $coin_styles = [
        'ltc'  => ["\033[38;5;250m", "Ł"],
        'dgb'  => ["\033[38;5;33m",  "🔵"],
        'sol'  => ["\033[38;5;135m", "◎"],
        'pol'  => ["\033[38;5;99m",  "💜"],
        'fey'  => ["\033[38;5;208m", "🟠"],
        'usdt' => ["\033[38;5;48m",  "₮"],
        'doge' => ["\033[38;5;220m", "Ð"],
        'pepe' => ["\033[38;5;118m", "🐸"],
        'trx'  => ["\033[38;5;196m", "🔻"],
        'bch'  => ["\033[38;5;214m", "Ƀ"],
        'dash' => ["\033[38;5;27m",  "💠"],
        'zec'  => ["\033[38;5;221m", "ⓩ"]
    ];

    for ($i = 0; $i < $total; $i++) {
        $num = $i + 1;
        $curr_raw = strtolower($currencies[$i]);
        $currency = strtoupper($currencies[$i]);
        
        $color = $coin_styles[$curr_raw][0] ?? "\033[97m";
        $symbol_icon = $coin_styles[$curr_raw][1] ?? "🪙";
        
        $formatted_num = str_pad($num, 2, ' ', STR_PAD_LEFT);
        $formatted_curr = str_pad($currency, 6, ' ');
        
        echo " " . cyan . "[" . hijau . $formatted_num . cyan . "] " . $symbol_icon . " " . $color . bold . $formatted_curr . reset . "  ";
        if (($i + 1) % $columns == 0 || $i == $total - 1) {
            echo "\n";
        }
    }
    echo cyan . "  ------------------------------------------" . reset . "\n";
    echo putih . " chosee: " . merah;

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
    $memek = strtolower($selectedCurrency);

    clear();
    banner($accountEmail, $totalEarned, $totalCoins, $memek);

    reload:
    while(true){
        $a = [
            "host: ".script_name,
            "user-agent: " . $ua,
            "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
            "referer: ".host."/dashboard",
            "cookie: " . $coki
        ];
        $b = [
            "host: rscaptcha.com",
            "user-agent: " . $ua,
            "accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "referer: ".host."/",
            "accept-language: id,en-US;q=0.9,en;q=0.8,ms;q=0.7,ru;q=0.6",
            "priority: i"
        ];
        $c = [
            "host: ".script_name,
            "origin: ".host,
            "content-type: application/x-www-form-urlencoded",
            "user-agent: " . $ua,
            "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
            "referer: ".host."/faucet/".$memek,
            "cookie: " . $coki
        ];

        $url = host."/faucet/".$memek;
        $faucet = skibidixxx($url, "GET", [], $a);

        if ($faucet == "ngelek" || strpos($faucet, "Just a moment") !== false) {
            bypassCloudflare($config, $configFile, $url);
            $config = getConfig($configFile);
            $coki = $config['cookie'];
            $ua   = $config['user_agent'];
            goto reload;
        }

        if (strpos($faucet, "Shortlinks | GameFaucet") !== false) {
   	        echo putih."------------------------------------------\n";
            echo kuning."You Need to Complete Atleast 1 Shortlinks!\n";
            echo putih."enter to reload..";
            trim(fgets(STDIN));
            goto reload;
        }
        
        if (strpos($faucet, 'rscaptcha_token') === false || strpos($faucet, 'rscaptcha_img') === false) {
            sleep(2);
            goto reload;
        }

        $rs_token = explode('"', explode('<input type="hidden" name="rscaptcha_token" value="', $faucet)[1])[0];
        $token = explode('"', explode('<input type="hidden" name="token" value="', $faucet)[1])[0];
        $rsimage = explode('"', explode('<img class="captcha-image" id="rscaptcha_img" src="', $faucet)[1])[0];

        $rsdownload = base64_encode(skibidixxx($rsimage, "GET", [], $b));
        $bypass = rscaptcha($rsdownload, $apikey);
        
        if (is_array($bypass)) {
            $x = $bypass["x"];
            $y = $bypass["y"];
        } elseif (in_array($bypass, ["WRONG_CAPTCHA_ID", "ERROR_CAPTCHA_UNSOLVABLE", "ERROR_TOO_MANY_REQUESTS", "ERROR_SOLVE_PENDING", "INTENAL_SERVER_ERROR"])) {
            goto reload;
        } else {
            echo putih . "Status: " . merah . " Gagal memproses captcha, mengulang...\n";
            sleep(3);
            echo "\033[1A\033[2K";
            goto reload;
        }

        $payload = rspayload($faucet, $x, $y);
        if (!$payload) {
            echo merah . "Status: Gagal membuat fingerprint!\n";
            sleep(3);
            echo "\033[1A\033[2K";
            goto reload;
        }

        $data = http_build_query([
            "ci_csrf_token" => "",
            "token" => $token,
            "currency" => $memek,
            "user_website" => "",
            "bh_gesture" => rand(1,10),
            "bh_dwell" => rand(1000,9000),
            "bh_interacted" => rand(1,10),
            "captcha" => "rscaptcha",
            "rscaptcha_token" => $rs_token,
            "rscaptcha_response" => $payload["fingerprint"],
            "uf" => uf(),
            "utt" => "Asia/Jakarta",
            "ls" => "id-ID,id,en-US,en"
        ]);
        
        $url = host."/faucet/verify";
        $claim = skibidixxx($url, "POST", $data, $c);
        if (strpos($claim, "Good job!") !== false) {
            $msg = explode("'", explode("text: '", $claim)[1])[0];
            $timer = explode(' -', explode('let wait = ', $claim)[1])[0];
            
            $rewardCoins = 0.0;
            if (preg_match('/([\d\.]+)\s*(satoshi|satoshis|tokens|coin|coins|pepe|LTC|DOGE|SOL|TRX|BCH|DASH|ZEC)?/i', $msg, $coinMatch)) {
                $rewardCoins = (float)$coinMatch[1];
            }

            $totalEarned++;
            $totalCoins += $rewardCoins;
            
            $config['earned'] = $totalEarned;
            $config['total_coins'] = $totalCoins;
            file_put_contents($configFile, json_encode($config, JSON_PRETTY_PRINT));

            echo putih . " " . hijau . $msg . "\n";
            sleep(3);
            echo "\033[1A\033[2K";
            
            clear();
            banner($accountEmail, $totalEarned, $totalCoins, $memek);
            
            timer($timer);
            clear();
            banner($accountEmail, $totalEarned, $totalCoins, $memek);

        } elseif (strpos($claim, "Invalid") !== false){
            echo putih . "Status: " . kuning . "Captcha/Klaim tidak valid, mengulang...\n";
            sleep(3);
            echo "\033[1A\033[2K";
            goto reload;

        } elseif (strpos($claim, "The faucet does not have sufficient funds") !== false) {
            echo putih."------------------------------------------\n";
            echo kuning." The faucet does not have sufficient funds.\n";
            echo putih."enter to menu..";
            trim(fgets(STDIN));
            goto dash;
        } else {
            echo putih . "KOPERASI MERAH PUTIH";
            sleep(1.8);
            echo "\033[1A\033[2K";
            goto reload;
        }
    }
} else {
    echo putih."SILAHKAN DAFTAR TERMUL\n";
    @unlink($configFile);
    sleep(3);
    goto login;
}
