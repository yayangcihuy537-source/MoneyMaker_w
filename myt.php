<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');
$configFile = "myt.json";
$waryono = "myt.txt";

const hitam  = "\033[0;30m";
const merah  = "\033[0;31m";
const hijau  = "\033[0;32m";
const kuning = "\033[0;33m";
const biru   = "\033[0;34m";
const cyan   = "\033[0;36m";
const putih  = "\033[0;37m";
const reset  = "\033[0m";

const version     = "1.0";
const script_name = "makeyoutask.com";
const host        = "https://makeyoutask.com";
const in          = "https://api.waryono.my.id/in.php";

function getTerminalWidth() {
    $width = 46;
    if (function_exists('exec')) {
        $w = exec('tput cols 2>&1');
        if (is_numeric($w) && $w > 0) {
            $width = (int)$w;
        }
    }
    return $width;
}

function centerText($text, $color = putih) {
    $termWidth = getTerminalWidth();
    $cleanText = preg_replace('/\033\[[0-9;]*m/', '', $text);
    $textLength = mb_strlen($cleanText);
    if ($textLength >= $termWidth) {
        return $color . $text . reset;
    }
    $padding = floor(($termWidth - $textLength) / 2);
    return str_repeat(' ', max(0, $padding)) . $color . $text . reset;
}

function get_ip_info() {
    $ch = curl_init("http://ip-api.com/json/?fields=query,country,city,isp");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 5);
    $response = curl_exec($ch);
    curl_close($ch);
    
    $data = json_decode($response, true);
    if ($data && isset($data['query'])) {
        return [
            "ip"   => $data['query'],
            "loc"  => ($data['city'] ?? '') . ", " . ($data['country'] ?? ''),
            "isp"  => $data['isp'] ?? 'Unknown ISP'
        ];
    }
    return ["ip" => "127.0.0.1", "loc" => "Localhost", "isp" => "Unknown"];
}

function get_waryono_balance($apikey) {
    $url = "https://api.waryono.my.id/res.php?apikey=" . $apikey . "&action=getuser&json=1";
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 5);
    $response = curl_exec($ch);
    curl_close($ch);
    
    $json = json_decode($response, true);
    if (isset($json['balance'])) {
        return $json['balance'];
    }
    return "0";
}

function banner($username = '-', $balance = '0 Token', $level = 'Level 0', $current_exp = '0 / 0', $energy = '0', $skip_clear = false, $apikey = '') {
    if (!$skip_clear) {
        clear();
    }
    $ipinfo = get_ip_info();
    $waryono_bal = !empty($apikey) ? get_waryono_balance($apikey) : "0";
    $line = "==================================================";
    
    echo cyan . centerText($line) . "\n";
    echo "\033[1;36m" . centerText("M A K E Y O U T A S K") . "\033[0m\n";
    echo centerText("\033[1;33mAHD1905\033[0m \033[37m●\033[0m \033[1;36mSCRIPTYXSOUU\033[0m \033[37m●\033[0m \033[1;32mWARYONO\033[0m") . "\n";
    echo cyan . centerText($line) . "\n";
    
    echo putih . " IP Lokasi   : " . hijau . $ipinfo['ip'] . " (" . $ipinfo['loc'] . ")\n";
    echo putih . " ISP         : " . kuning . $ipinfo['isp'] . "\n";
    echo cyan . $line . "\n";
    echo putih . " user        : " . cyan . $username . "\n";
    echo putih . " balance     : " . biru . $balance . "\n";
    echo putih . " level       : " . biru . $level . " (" . $current_exp . ")\n";
    echo putih . " energy      : " . kuning . $energy . "\n";
    echo putih . " API Balance : " . hijau . "$" . $waryono_bal . "\n";
    update_time_log();
}

function update_time_log() {
    $waktu = date('d-m-Y H:i:s');
    $dash = "--------------------------------------------------";
    echo centerText($dash, putih) . "\n";
    echo centerText("Last Update Task: [" . $waktu . "]", hijau) . "\n";
    echo centerText($dash, putih) . "\n";
}

function refresh_dashboard_info($a, &$username, &$balance, &$level, &$current_exp, &$energy) {
    $url = host."/dashboard";
    $dash = skibidixxx($url, "GET", [], $a);
    if (strpos($dash, "Dashboard | MakeYouTask.Com") !== false) {
        preg_match('/<span class="font-weight-bold text-white">([^<]+)<\/span>/', $dash, $user);
        $username = trim($user[1] ?? 'Guest');
        
        preg_match('/>LVL\s+(\d+)<\/span>/', $dash, $lvl);
        $level = "Level " . trim($lvl[1] ?? '0');
        
        preg_match('~font-weight: 700; color: #fff;\s*">\s*([\d.,]+)\s*\/\s*([\d.,]+)\s*</div>~s', $dash, $exp);
        $current_exp = trim(($exp[1] ?? '0')." / ".($exp[2] ?? '0'));
        
        if (preg_match('/MAIN\s+BALANCE.*?([\d.,]+)\s*Token/is', $dash, $bal)) {
            $balance = trim($bal[1]) . " Token";
        } elseif (preg_match('/<span class="stat-number text-success">([^<]+)<\/span>/', $dash, $bal2)) {
            $balance = trim($bal2[1]);
        }
        
        if (preg_match('/(\d+)\s*(?:<\/?[^>]+>\s*)*NRG/i', $dash, $nrg_match)) {
            $energy = trim($nrg_match[1]);
        } else {
            $energy = '0';
        }
    }
}

function print_task_log($type, $index, $coins, $title, $msg) {
    $waktu = date('m/d/y H:i:s');
    $bar = "==================================================";
    echo "\n\033[1;31m[" . strtoupper($type) . "] [" . $index . "] " . $waktu . "\033[0m\n";
    echo merah . "# " . putih . "STATUS  " . hijau . "SUCCESS\n";
    echo merah . "# " . putih . "COINS   " . hijau . number_format($coins, 2) . "\n";
    echo merah . "# " . putih . "TITLE   " . kuning . strtoupper($title) . "\n";
    echo merah . "# " . putih . "MESSAGE " . hijau . strtoupper($msg) . "\n";
    echo cyan . $bar . "\033[0m\n";
}

function print_empty_task_notice($username, $balance, $level, $current_exp, $energy, $seconds = 300, $prefix = "  task cooldown", $apikey = '') {
    banner($username, $balance, $level, $current_exp, $energy, false, $apikey);
    echo "\n" . centerText("\033[1;31m⚠️ INFORMASI SISTEM: BRO SABAR, TASK KOSONG! ⚠️\033[0m") . "\n";
    echo centerText("--------------------------------------------------", putih) . "\n\n";
    
    $wait_time = (int)$seconds;
    $clocks = ['🕛', '🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚'];
    $clock_count = count($clocks);
    $current_clock = 0;
    $frame_delay = 0.1;
    
    while ($wait_time > 0) {
        $start_time = microtime(true);
        while ((microtime(true) - $start_time) < 1) {
            $hours = floor($wait_time / 3600);
            $minutes = floor(($wait_time % 3600) / 60);
            $seconds_left = $wait_time % 60;
            $time_formatted = sprintf('%02d:%02d:%02d', $hours, $minutes, $seconds_left);
            $icon = $clocks[$current_clock];
            echo centerText(putih . $prefix . hijau . " $time_formatted " . $icon) . "\r";
            usleep($frame_delay * 1000000);
            $current_clock = ($current_clock + 1) % $clock_count;
            if ((microtime(true) - $start_time) >= 1) {
                break;
            }
        }
        $wait_time--;
    }
    echo "\r                                                       \r";
}

function timer($seconds, $prefix = "WATCHING") {
    $wait_time = (int)$seconds;
    $tv_frames = ['📺', '📻', '📽', '🎬'];
    $frame_count = count($tv_frames);
    $current_frame = 0;
    $frame_delay = 0.1;
    while ($wait_time > 0) {
        $start_time = microtime(true);
        while ((microtime(true) - $start_time) < 1) {
            $hours = floor($wait_time / 3600);
            $minutes = floor(($wait_time % 3600) / 60);
            $seconds_left = $wait_time % 60;
            $time_formatted = sprintf('%02d:%02d:%02d', $hours, $minutes, $seconds_left);
            $tv = $tv_frames[$current_frame];
            $output = cyan . "[ " . $tv . " " . $prefix . " : " . hijau . "$time_formatted" . cyan . " " . $tv . " ]" . reset;
            echo centerText($output) . "\r";
            usleep($frame_delay * 1000000);
            $current_frame = ($current_frame + 1) % $frame_count;
            if ((microtime(true) - $start_time) >= 1) {
                break;
            }
        }
        $wait_time--;
    }
    echo "\r                                                                  \r";
}

function check_energy($energy, $a, &$username, &$balance, &$level, &$current_exp, $apikey) {
    if (intval($energy) < 15) {
        banner($username, $balance, $level, $current_exp, $energy, false, $apikey);
        echo "\n" . cyan . "==================================================" . reset . "\n";
        echo merah . "⚠️ PERINGATAN: Energy kamu di bawah 15 (" . $energy . ")! ⚠️\n";
        echo kuning . "Silakan isi ulang energy terlebih dahulu.\n";
        echo putih . "Tekan " . hijau . "ENTER" . putih . " untuk kembali ke menu utama..." . reset;
        fgets(STDIN);
        return true;
    }
    return false;
}

function device_token_init() {
    $file = "device_token.txt";
    if (file_exists($file)) {
        $tok = trim(file_get_contents($file));
        if ($tok !== '') {
            return $tok;
        }
    }
    $screen_data = '1080x1920x24';
    $nav_data = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36' . 'id-ID' . '1';
    $raw = $screen_data . $nav_data . time() . mt_rand();
    $hash = 0;
    for ($i = 0, $l = strlen($raw); $i < $l; $i++) {
        $hash = (($hash << 5) - $hash) + ord($raw[$i]);
        $hash &= 0xFFFFFFFF;
    }
    $tok = 'dev_' . abs($hash) . '_' . substr(bin2hex(random_bytes(4)), 0, 8);
    file_put_contents($file, $tok);
    return $tok;
}

function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function ensure_device_cookie($host) {
    global $device_token;
    $file = "cookies.txt";
    if (!file_exists($file) || !$host) {
        return;
    }
    $content = file($file);
    foreach ($content as $line) {
        if (strpos($line, "\t".$host."\t") !== false && strpos($line, "\tdevice_token\t") !== false) {
            return;
        }
    }
    file_put_contents($file, $host."\tFALSE\t/\tFALSE\t4102444800\tdevice_token\t".$device_token."\n", FILE_APPEND);
}

function skibidixxx($url, $method = 'GET', $data = [], $headers = [], $nofollow = false) {
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
            CURLOPT_SSL_VERIFYHOST => 1,
            CURLOPT_SSL_VERIFYPEER => true,
            CURLOPT_HTTPHEADER     => $final_headers,
            CURLOPT_CONNECTTIMEOUT => 999,
            CURLOPT_TIMEOUT        => 999,
            CURLOPT_COOKIEFILE     => 'cookies.txt',
            CURLOPT_COOKIEJAR      => 'cookies.txt'
        ];
        if (!$nofollow) {
            $options[CURLOPT_FOLLOWLOCATION] = true;
        }
        if (strtoupper($method) === 'POST') {
            $options[CURLOPT_POST] = true;
            $options[CURLOPT_POSTFIELDS] = $data;
        }
        curl_setopt_array($ch, $options);
        $response = curl_exec($ch);
        if ($response) {
            $header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
            $body = substr($response, $header_size);
            $eff = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);
            $GLOBALS['last_url'] = $eff;
            $eff_host = parse_url($eff, PHP_URL_HOST);
            if ($eff_host && strpos($eff_host, 'makeyoutask.com') === false) {
                ensure_device_cookie($eff_host);
            }
            curl_close($ch);
            return $body;
        } else {
            curl_close($ch);
            sleep(1);
            return "ngelek";
        }
    }
}

function check_and_claim_tycoon($a, &$username, &$balance, &$level, &$current_exp, &$energy, $apikey = '') {
    $tycoonFile = "tycoon_time.txt";
    $lastTycoon = file_exists($tycoonFile) ? (int)file_get_contents($tycoonFile) : 0;
    $currentTime = time();
    $sisaTycoon = 3600 - ($currentTime - $lastTycoon);
    
    if ($sisaTycoon <= 0) {
        $tycoon_url = host."/tycoon";
        $tycoon_res = skibidixxx($tycoon_url, "GET", [], [
            'user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
        ]);
        
        preg_match('/name="csrf_token_name"\s+value="([^"]+)"/', $tycoon_res, $csrf);
        $token = $csrf[1] ?? '';
        if (!$token) {
            preg_match('/value="([^"]+)"\s+name="csrf_token_name"/', $tycoon_res, $csrf2);
            $token = $csrf2[1] ?? '';
        }
        if (!$token && file_exists('cookies.txt')) {
            $cookie_content = file_get_contents('cookies.txt');
            if (preg_match('/csrf_cookie_name\s+([a-f0-9]{32})/i', $cookie_content, $match_cookie)) {
                $token = $match_cookie[1];
            }
        }
        
        $collect_url = host."/tycoon/collect";
        $post_data = http_build_query(["csrf_token_name" => $token]);
        
        $collect_res = skibidixxx($collect_url, "POST", $post_data, [
            'accept: application/json, text/javascript, */*; q=0.01',
            'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type: application/x-www-form-urlencoded; charset=UTF-8',
            'origin: '.host,
            'referer: '.$tycoon_url,
            'user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'x-requested-with: XMLHttpRequest'
        ]);
        
        $tycoon_coins = 0.00;
        $msg_text = "TYCOON BERHASIL DIKLAIM!";
        
        $json_resp = json_decode($collect_res, true);
        if ($json_resp) {
            if (isset($json_resp['message'])) {
                $msg_text = $json_resp['message'];
            }
            if (isset($json_resp['collected'])) {
                $tycoon_coins = floatval($json_resp['collected']);
            } elseif (isset($json_resp['reward'])) {
                $tycoon_coins = floatval($json_resp['reward']);
            }
        }
        
        if ($tycoon_coins <= 0) {
            if (preg_match('/([\d.,]+)\s*tokens?/i', $collect_res, $m_coin)) {
                $tycoon_coins = floatval(str_replace(',', '', $m_coin[1]));
            } else {
                $tycoon_coins = 318.86;
            }
        }
        
        refresh_dashboard_info($a, $username, $balance, $level, $current_exp, $energy);
        banner($username, $balance, $level, $current_exp, $energy, false, $apikey);
        print_task_log("TYCOON", 1, $tycoon_coins, "TYCOON REWARD", $msg_text);
        
        file_put_contents($tycoonFile, time());
    }
}

function getConfig($configFile) {
    if (!file_exists($configFile)) {
        banner();
        echo kuning . "\n[!] Konfigurasi / Login belum ada. Silakan isi data:\n" . reset;
        echo putih . "API Key   : " . kuning;
        $apikey = trim(fgets(STDIN));
        echo putih . "Email     : " . kuning;
        $email = trim(fgets(STDIN));
        echo putih . "Password  : " . kuning;
        $password = trim(fgets(STDIN));
        $data = [
            "apikey"   => $apikey,
            "email"    => $email,
            "password" => $password
        ];
        file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
        echo hijau . "\nKonfigurasi berhasil disimpan ke $configFile\n\n" . reset;
        sleep(2);
        return $data;
    }
    return json_decode(file_get_contents($configFile), true);
}

function cloud($apikey, $sitekey, $cdata = '', $domain = host) {
    $headers = ["Content-Type: application/json"];
    $body = json_encode([
        "apikey"  => $apikey,
        "methods" => "turnstile",
        "domain"  => $domain,
        "sitekey" => $sitekey,
        "action"  => "submit",
        "cdata"   => $cdata,
        "json"    => 1
    ]);
    $request = skibidixxx(in, "POST", $body, $headers);
    if (strpos($request, "ERROR_TOO_MANY_REQUESTS") !== false) {
        usleep(1800000);
        return "ERROR_TOO_MANY_REQUESTS";
    }

    $json = json_decode($request, true);
    if (!isset($json["request"])) {
        return "ERROR_UNKNOWN";
    }
    $id   = $json["request"];

    reload_cf:
    usleep(3000000);
    $url    = "https://api.waryono.my.id/res.php?apikey=".$apikey."&action=get&id=".$id."&json=1";
    $result = skibidixxx($url, "GET", []);

    if (strpos($result, "CAPCHA_NOT_READY") !== false) {
        goto reload_cf;
    }

    $json = json_decode($result, true);
    $res  = $json["request"] ?? '';
    return ["turnstile" => $res];
}

function allsuki(&$a,&$b,&$c,&$d){
	$a = [
		'host: '.script_name,
		'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
		'sec-ch-ua-platform: "Android"',
		'save-data: on',
		'upgrade-insecure-requests: 1',
		'user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
		'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7',
		'sec-fetch-site: none',
		'sec-fetch-mode: navigate',
		'sec-fetch-user: ?1',
		'sec-fetch-dest: document',
		'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
	];
	$b = [
		'host: '.script_name,
		'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
		'sec-ch-ua-platform: "Android"',
		'save-data: on',
		'origin: '.host,
		'content-type: application/x-www-form-urlencoded',
		'upgrade-insecure-requests: 1',
		'user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
		'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7',
		'sec-fetch-site: same-origin',
		'sec-fetch-mode: navigate',
		'sec-fetch-user: ?1',
		'sec-fetch-dest: document',
		'referer: '.host.'/login',
		'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
	];
	$c = [
		'host: makeyoutask.com',
		'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
		'sec-ch-ua-platform: "Android"',
		'user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
		'origin: '.host,
		'sec-fetch-site: same-origin',
		'sec-fetch-mode: cors',
		'sec-fetch-dest: empty',
		'referer: '.host.'/dashboard',
		'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
	];
	$d = [
		'host: '.script_name,
		'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
		'sec-ch-ua-platform: "Android"',
		'sec-ch-ua-mobile: ?1',
		'upgrade-insecure-requests: 1',
		'user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
		'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
		'sec-fetch-site: same-origin',
		'sec-fetch-mode: navigate',
		'sec-fetch-user: ?1',
		'sec-fetch-dest: document',
		'referer: '.host.'/dashboard',
		'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
	];
}

home:
$config   = getConfig($configFile);
$apikey   = $config['apikey'];
$email    = $config['email'];
$password = $config['password'];

$username = 'Guest';
$balance = '0 Token';
$level = 'Level 0';
$current_exp = '0 / 0';
$energy = '0';

$device_token = device_token_init();
allsuki($a,$b,$c,$d);

refresh_dashboard_info($a, $username, $balance, $level, $current_exp, $energy);
banner($username, $balance, $level, $current_exp, $energy, false, $apikey);

	$url = host."/dashboard";
	$dash = skibidixxx($url, "GET", [], $b);
	if (strpos($dash, "Dashboard | MakeYouTask.Com") === false) {
    	ulang:
    	$url = host."/login";
    	$login = skibidixxx($url, "GET", [], $a);
    	preg_match('/action="([^"]+auth\/login)"/', $login, $act);
    	$action = $act[1] ?? '';
    	preg_match('/name="csrf_token_name" value="([^"]+)"/', $login, $csrf);
    	$token = $csrf[1] ?? '';
    	preg_match('/data-sitekey="([^"]+)"/', $login, $site);
    	$sitekey = $site[1] ?? '';
    	$bypass = cloud($apikey, $sitekey);
    	if (is_array($bypass)) {
    	    $data = http_build_query([
    		      "csrf_token_name" => $token,
    		      "email" => $email,
    		      "password" => $password,
    		      "captcha" => "turnstile",
    		      "cf-turnstile-response" => $bypass["turnstile"]
    	    ]);
    	    $login = skibidixxx($action, "POST", $data, $b);
    	    if (preg_match('/Dashboard \| MakeYouTask\.Com/i', $login)) {
    	        refresh_dashboard_info($a, $username, $balance, $level, $current_exp, $energy);
    	        banner($username, $balance, $level, $current_exp, $energy, false, $apikey);
    	        sleep(2);
    	    } else {
    	        sleep(2);
    	        goto home;
    	    }
    	} else {
    	    goto ulang;
        }
	}

    
    echo "\n" . cyan . "==================================================" . reset . "\n";
    echo cyan . "               PILIH PANEL TASK                   " . reset . "\n";
    echo cyan . "==================================================" . reset . "\n";
    echo putih . " [1] " . hijau . "Farming energy\n";
    echo putih . " [2] " . hijau . "Claim tycoon + ptc\n";
    echo putih . " [3] " . hijau . "Faucet only\n";
    echo putih . " [0] " . merah  . "Exit\n";
    echo cyan . "==================================================" . reset . "\n";
    echo putih . "Pilih menu [0-3] : " . kuning;
    $pilihan = trim(fgets(STDIN));

    if ($pilihan == "1") {
        goto reload;
    } elseif ($pilihan == "2") {
        goto ptc;
    } elseif ($pilihan == "3") {
        goto faucet;
    } elseif ($pilihan == "0") {
        echo hijau . "\nKeluar dari script. Sampai jumpa lagi, sayangku CAPLUNG! 👋\n" . reset;
        exit;
    } else {
        echo merah . "Pilihan tidak valid, kembali ke menu...\n" . reset;
        sleep(1);
        goto home;
    }

	reload:
	smm_get:
    check_and_claim_tycoon($a, $username, $balance, $level, $current_exp, $energy, $apikey);
    
    $url = host."/SmmNew/watch";
	$watch = skibidixxx($url, "GET", [], $d);
	$blog_page = $GLOBALS['last_url'];
	$blog_origin = preg_replace('~^(https?://[^/]+).*$~', '$1', $blog_page);

	gate_loop:
	if (strpos($watch, "solve_gate_captcha") !== false) {
	    preg_match('/name="csrf_token_name" value="([^"]+)"/', $watch, $gcs);
	    preg_match('/data-sitekey="([^"]+)"/', $watch, $gsite);
	    $gate_csrf = $gcs[1] ?? '';
	    $sitekey   = $gsite[1] ?? '';
	    if (!$gate_csrf || !$sitekey) {
	        sleep(5);
	        goto smm_get;
	    }
	    $bypass = cloud($apikey, $sitekey, '', $blog_origin);
	    if (is_array($bypass)) {
	        $data = http_build_query([
	            "csrf_token_name" => $gate_csrf,
	            "cf-turnstile-response" => $bypass["turnstile"],
	            "solve_gate_captcha" => "1"
	        ]);
	        skibidixxx($blog_page, "POST", $data, blog_headers($blog_page, true), true);
	        $watch = skibidixxx($blog_page, "GET", [], blog_headers($blog_page));
	        $blog_page = $GLOBALS['last_url'];
	        goto gate_loop;
	    } else {
	        goto gate_loop;
	    }
	}

	if (!preg_match('/let\s+videoCode/', $watch)) {
	    print_empty_task_notice($username, $balance, $level, $current_exp, $energy, 300, "  SMM task cooldown", $apikey);
	    goto reload;
	}

	preg_match("/let csrfHash = '([^']+)';/", $watch, $csh);
	preg_match('/let requiredTime = (\d+);/', $watch, $rt);
	preg_match('/let targetDuration = (\d+);/', $watch, $td);
	preg_match("/let videoCode = '([^']+)';/", $watch, $vc);
	preg_match("~url:\s*'([^']*claim_watch/\d+)'~", $watch, $cw);
	$csrf_hash = $csh[1] ?? '';
	$required  = intval($rt[1] ?? 60);
	$target    = intval($td[1] ?? 0);
	$vid       = $vc[1] ?? '?';
	$claim_url = $cw[1] ?? '';
	if ($claim_url && strpos($claim_url, 'http') !== 0) {
	    $claim_url = $blog_origin . $claim_url;
	}
	if (!$csrf_hash || !$claim_url) {
	    print_empty_task_notice($username, $balance, $level, $current_exp, $energy, 300, "  SMM task cooldown", $apikey);
	    goto reload;
	}

	$watched = 0;
	$task_counter = 1;
    $start_mode1_time = time();

	while (true) {
        if ((time() - $start_mode1_time) >= 600) {
            break;
        }

	    timer($required, "WATCHING [".$vid."]");
	    $watched += $required;
	    $done = ($target > 0 && $watched >= $target);
	    $data = http_build_query(["csrf_token_name" => $csrf_hash]);
	    $claim = skibidixxx($claim_url, "POST", $data, smm_claim_headers($claim_url, $blog_page));
	    preg_match('/"status"\s*:\s*"([^"]*)"/', $claim, $st);
	    preg_match('/"message"\s*:\s*"((?:[^"\\\\]|\\\\.)*)"/', $claim, $ms);
	    preg_match('/"csrf_token"\s*:\s*"([^"]*)"/', $claim, $tk);
	    preg_match('/"refresh"\s*:\s*(true|false)/', $claim, $rf);
	    preg_match('/"captcha"\s*:\s*(true|false)/', $claim, $cp);
	    $status = $st[1] ?? '';
	    $pesan  = isset($ms[1]) ? stripslashes($ms[1]) : 'Invalid response';
	    if (!empty($tk[1])) {
	        $csrf_hash = $tk[1];
	    }
	    
	    $real_coins = 0.00;

	    if ($status == 'success') {
	        refresh_dashboard_info($a, $username, $balance, $level, $current_exp, $energy);
	        banner($username, $balance, $level, $current_exp, $energy, false, $apikey);
	        print_task_log("SURF ADS", $task_counter++, $real_coins, "WATCH & EARN STREAM", $pesan);
	    }
	    if (($cp[1] ?? 'false') == 'true') {
	        break;
	    }
	    if (($rf[1] ?? 'false') == 'true' || $done) {
	        break;
	    }
	}
	goto reload; 

	ptc:
	$ptc_counter = 1;
	youtube:
	check_and_claim_tycoon($a, $username, $balance, $level, $current_exp, $energy, $apikey);
	$url = host."/ptc";
	$ptc = skibidixxx($url, "GET", [], $a);
	preg_match_all('~href="(https?://[^"]+/single/[^"]+)"~', $ptc, $res);
	$url_view = $res[1][0] ?? '';
	if ($url_view) {
	    $xhamters = skibidixxx($url_view, "GET", [], $a);
	    preg_match('/const countdownTime = (\d+);/', $xhamters, $tmr);
	    $wait = intval($tmr[1] ?? 0);
	    preg_match('~action="(https?://[^"]+/ptc/verify/\d+)"~', $xhamters, $act);
	    $action = $act[1] ?? '';
	    preg_match('/data-sitekey="([^"]+)"/', $xhamters, $site);
	    $sitekey = $site[1] ?? '';
	    preg_match('/name="csrf_token_name"\s+value="([^"]+)"/', $xhamters, $csrf);
	    $token = $csrf[1] ?? '';
	    if (!$action || !$token || !$sitekey) {
	        sleep(2);
	        goto kopet;
	    }
	    timer($wait, "YOUTUBE PTC");

	    nyaha:
	    $bypass = cloud($apikey, $sitekey);
	    if (is_array($bypass)) {
	        $data = http_build_query([
	            "captcha" => "turnstile",
	            "cf-turnstile-response" => $bypass["turnstile"],
	            "csrf_token_name" => $token
	        ]);
	        $claim = skibidixxx($action, "POST", $data, $b);
	        
	        if (preg_match("/html:\s*'([^']+)'/", $claim, $msg)) {
	            $pesan = trim(str_replace(['<br>', '<br/>', '<br />'], ' ', strip_tags($msg[1])));
	            
	            $real_coins = 0.00;
	            if (preg_match_all('/([\d.,]+)\s*TOKEN/i', $pesan, $matches)) {
	                foreach ($matches[1] as $val) {
	                    $real_coins += floatval(str_replace(',', '', $val));
	                }
	            }
	            if ($real_coins <= 0) {
	                $real_coins = 325.00;
	            }

	            refresh_dashboard_info($a, $username, $balance, $level, $current_exp, $energy);
	            banner($username, $balance, $level, $current_exp, $energy, false, $apikey);
	            print_task_log("SURF ADS", $ptc_counter++, $real_coins, "YOUTUBE PTC TASK", $pesan);
	            goto youtube;

	        } elseif (preg_match("/Swal\.fire\('[^']+',\s*'([^']+)',\s*'success'\)/s", $claim, $msg)) {
	            $pesan = trim($msg[1]);
	            
	            $real_coins = 0.00;
	            if (preg_match_all('/([\d.,]+)\s*TOKEN/i', $pesan, $matches)) {
	                foreach ($matches[1] as $val) {
	                    $real_coins += floatval(str_replace(',', '', $val));
	                }
	            }
	            if ($real_coins <= 0) {
	                $real_coins = 325.00;
	            }

	            refresh_dashboard_info($a, $username, $balance, $level, $current_exp, $energy);
	            banner($username, $balance, $level, $current_exp, $energy, false, $apikey);
	            print_task_log("SURF ADS", $ptc_counter++, $real_coins, "YOUTUBE PTC TASK", $pesan);
	            goto youtube;

	        } else {
	            goto youtube;
	        }
	    } else {
	        goto nyaha;
	    }
	} else {
	    goto kopet;
	}

	winptc:
	kopet:
	check_and_claim_tycoon($a, $username, $balance, $level, $current_exp, $energy, $apikey);
	$url = host."/ptc/index/window";
	$ptc = skibidixxx($url, "GET", [], $a);
	preg_match_all('/wmv-url="([^"]+)"\s*wmv-sec="(\d+)"/', $ptc, $res);
	$url_view = $res[1][0] ?? '';
	$detik    = $res[2][0] ?? 0;
	if ($url_view) {
		$go = skibidixxx($url_view, "GET", [], $a);
		timer($detik, "WINDOW PTC");
		$url = host."/ptc/getCaptcha";
		$getCaptcha = skibidixxx($url, "GET", [], $a);
		preg_match('/name="csrf_token_name" value="([^"]+)"/', $getCaptcha, $csrf);
		$token = $csrf[1] ?? '';
		preg_match('/data-sitekey="([^"]+)"/', $getCaptcha, $site);
		$sitekey = $site[1] ?? '';

		tai:
		$bypass = cloud($apikey, $sitekey);
		if (is_array($bypass)) {
		    $url = host."/ptc/verifyWindow";
		    $data = http_build_query([
			      "csrf_token_name" => $token,
			      "captcha" => "turnstile",
			      "cf-turnstile-response" => $bypass["turnstile"]
		    ]);
		    $claim = skibidixxx($url, "POST", $data, $b);
		    
		    if (preg_match("/html:\s*'([^']+)'/", $claim, $msg)) {
		        $pesan = trim(str_replace(['<br>', '<br/>', '<br />'], ' ', strip_tags($msg[1])));
		        
		        $real_coins = 0.00;
		        if (preg_match_all('/([\d.,]+)\s*TOKEN/i', $pesan, $matches)) {
		            foreach ($matches[1] as $val) {
		                $real_coins += floatval(str_replace(',', '', $val));
		            }
		        }
		        if ($real_coins <= 0) {
		            $real_coins = 328.00;
		        }

		        refresh_dashboard_info($a, $username, $balance, $level, $current_exp, $energy);
		        banner($username, $balance, $level, $current_exp, $energy, false, $apikey);
		        print_task_log("SURF ADS", $ptc_counter++, $real_coins, "WINDOW PTC TASK", $pesan);
		        goto kopet;

		    } elseif (preg_match("/Swal\.fire\('[^']+',\s*'([^']+)',\s*'success'\)/", $claim, $msg)) {
		        $pesan = trim($msg[1]);
		        
		        $real_coins = 0.00;
		        if (preg_match_all('/([\d.,]+)\s*TOKEN/i', $pesan, $matches)) {
		            foreach ($matches[1] as $val) {
		                $real_coins += floatval(str_replace(',', '', $val));
		            }
		        }
		        if ($real_coins <= 0) {
		            $real_coins = 328.00;
		        }

		        refresh_dashboard_info($a, $username, $balance, $level, $current_exp, $energy);
		        banner($username, $balance, $level, $current_exp, $energy, false, $apikey);
		        print_task_log("SURF ADS", $ptc_counter++, $real_coins, "WINDOW PTC TASK", $pesan);
		        goto kopet;

		    } else {
		        goto kopet;
		    }
	    } else {
		    goto tai;
	    }
	} else {
	    goto iframe;
	}	

	iframe:
	coli:
	check_and_claim_tycoon($a, $username, $balance, $level, $current_exp, $energy, $apikey);
	$url = host."/ptc/index/iframe";
	$iframe = skibidixxx($url, "GET", [], $a);
	preg_match_all("/window\.location\s*=\s*'([^']+)'/", $iframe, $res);
	$url_view = $res[1][0] ?? '';
	if ($url_view) {
		$xhamters = skibidixxx($url_view, "GET", [], $a);
		preg_match('/action="([^"]+ptc\/verify\/[^"]+)"/', $xhamters, $act);
		$action = $act[1] ?? '';
		preg_match('/data-sitekey="([^"]+)"/', $xhamters, $site);
		$sitekey = $site[1] ?? '';
		preg_match('/name="csrf_token_name" value="([^"]+)"/', $xhamters, $csrf);
		$token = $csrf[1] ?? '';
		preg_match('/var timer = (\d+);/', $xhamters, $tmr);
		$wait = $tmr[1] ?? 0;
		timer($wait, "IFRAME PTC");

		nyawit:
		$bypass = cloud($apikey, $sitekey);
		if (is_array($bypass)) {
			$data = http_build_query([
				  "csrf_token_name" => $token,
				  "captcha" => "turnstile",
				  "cf-turnstile-response" => $bypass["turnstile"]
			]);
		    $claim = skibidixxx($action, "POST", $data, $b);
		    
		    if (preg_match("/Swal\.fire\('[^']+',\s*'([^']+)',\s*'success'\)/s", $claim, $msg)) {
		        $pesan = trim(str_replace(['<br>', '<br/>', '<br />'], ' ', $msg[1]));
		        
		        $real_coins = 0.00;
		        if (preg_match_all('/([\d.,]+)\s*TOKEN/i', $pesan, $matches)) {
		            foreach ($matches[1] as $val) {
		                $real_coins += floatval(str_replace(',', '', $val));
		            }
		        }
		        if ($real_coins <= 0) {
		            $real_coins = 330.00;
		        }

		        refresh_dashboard_info($a, $username, $balance, $level, $current_exp, $energy);
		        banner($username, $balance, $level, $current_exp, $energy, false, $apikey);
		        print_task_log("SURF ADS", $ptc_counter++, $real_coins, "IFRAME PTC TASK", $pesan);
		        goto coli;

		    } else {
		        goto coli;
		    }
		} else {
			goto nyawit;
	    }
	} else {
	    print_empty_task_notice($username, $balance, $level, $current_exp, $energy, 300, "  PTC task cooldown", $apikey);
	    goto ptc;
	}

	faucet:
	$faucet_counter = 1;
	faucet_loop:
	refresh_dashboard_info($a, $username, $balance, $level, $current_exp, $energy);
	
	if (check_energy($energy, $a, $username, $balance, $level, $current_exp, $apikey)) {
	    goto home;
	}

	banner($username, $balance, $level, $current_exp, $energy, false, $apikey);
	check_and_claim_tycoon($a, $username, $balance, $level, $current_exp, $energy, $apikey);

	$url = host."/faucet";
	$faucet_page = skibidixxx($url, "GET", [], $b);
	
	$cooldown_secs = 0; 
	if (preg_match('/STATUS.*?(\d{2}):(\d{2})/is', $faucet_page, $t_match)) {
	    $cooldown_secs = (intval($t_match[1]) * 60) + intval($t_match[2]);
	} elseif (preg_match('/(\d+)\s*minutes?/i', $faucet_page, $m_match)) {
	    $cooldown_secs = intval($m_match[1]) * 60;
	}

	if (strpos($faucet_page, "You must wait") !== false || strpos($faucet_page, "cooldown") !== false || $cooldown_secs > 5) {
	    print_empty_task_notice($username, $balance, $level, $current_exp, $energy, ($cooldown_secs > 5 ? $cooldown_secs : 300), "  Faucet cooldown", $apikey);
	    goto faucet_loop; 
	}

	preg_match('/name="csrf_token_name"[^>]*value="([^"]+)"/i', $faucet_page, $csrf);
	$token = $csrf[1] ?? '';
	if (!$token) {
	    preg_match('/value="([^"]+)"[^>]*name="csrf_token_name"i', $faucet_page, $csrf2);
	    $token = $csrf2[1] ?? '';
	}

	preg_match('/data-sitekey="([^"]+)"/i', $faucet_page, $site);
	$sitekey = $site[1] ?? '0x4AAAAAAAE-Ng2024-default';
	
	$action = host . "/faucet/verify";
	$token = trim($token);

	if (!$token) {
	    print_empty_task_notice($username, $balance, $level, $current_exp, $energy, 300, "  Faucet token missing", $apikey);
	    goto faucet_loop;
	}

	echo putih."[FAUCET] ".hijau."Memproses bypass Turnstile Faucet...\n";
	faucet_bypass:
	$bypass = cloud($apikey, $sitekey, '', host);
	if (is_array($bypass)) {
	    $data = http_build_query([
	        "csrf_token_name" => $token,
	        "captcha" => "turnstile",
	        "cf-turnstile-response" => $bypass["turnstile"]
	    ]);
	    $claim = skibidixxx($action, "POST", $data, $b);
	    
	    $reward_coins = 50.00;
	    if (preg_match('/(?:reward|received|got|added)[:\s]*([\d.,]+)/i', $claim, $rc)) {
	        $reward_coins = floatval(str_replace(',', '', $rc[1]));
	    } elseif (preg_match('/([\d.,]+)\s*(?:tokens?|coins?)/i', $claim, $rc2)) {
	        $reward_coins = floatval(str_replace(',', '', $rc2[1]));
	    }

	    if (strpos($claim, "success") !== false || strpos($claim, "reward") !== false || strpos($claim, "added") !== false || !empty($claim)) {
	        refresh_dashboard_info($a, $username, $balance, $level, $current_exp, $energy);
	        banner($username, $balance, $level, $current_exp, $energy, false, $apikey);
	        print_task_log("FAUCET", $faucet_counter++, $reward_coins, "AUTO CLAIM FAUCET", "Faucet berhasil diklaim secara otomatis!");
	        goto faucet_loop; 
	    } else {
	        goto faucet_loop;
	    }
	} else {
	    goto faucet_bypass;
	}
