<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');
$configFile = "config.json";
$waryono = "cookies.txt";

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
const in      = "https://api.waryono.my.id/in.php";

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

function banner($username = '-', $balance = '0 Token', $level = 'Level 0', $current_exp = '0 / 0') {
    clear();
    $ipinfo = get_ip_info();
    $line = "==================================================";
    
    echo cyan . centerText($line) . "\n";
    echo "\033[1;36m" . centerText("M A K E Y O U T A S K") . "\033[0m\n";
    echo centerText("\033[1;33mAHD1905\033[0m \033[37m●\033[0m \033[1;36mSCRIPTYXSOUU\033[0m \033[37m●\033[0m \033[1;32mWARYONO\033[0m") . "\n";
    echo cyan . centerText($line) . "\n";
    
    echo putih . " IP Lokasi : " . hijau . $ipinfo['ip'] . " (" . $ipinfo['loc'] . ")\n";
    echo putih . " ISP       : " . kuning . $ipinfo['isp'] . "\n";
    echo cyan . $line . "\n";
    echo putih . " user      : " . cyan . $username . "\n";
    echo putih . " balance   : " . biru . $balance . "\n";
    echo putih . " level     : " . biru . $level . " (" . $current_exp . ")\n";
    update_time_log();
}

function update_time_log() {
    $waktu = date('d-m-Y H:i:s');
    $dash = "--------------------------------------------------";
    echo centerText($dash, putih) . "\n";
    echo centerText("Last Update Task: [" . $waktu . "]", hijau) . "\n";
    echo centerText($dash, putih) . "\n";
}

function refresh_dashboard_info($a, &$username, &$balance, &$level, &$current_exp) {
    $url = host."/dashboard";
    $dash = skibidixxx($url, "GET", [], $a);
    if (strpos($dash, "Dashboard | MakeYouTask.Com") !== false) {
        preg_match('/<span class="font-weight-bold text-white">([^<]+)<\/span>/', $dash, $user);
        $username = trim($user[1] ?? 'Guest');
        preg_match('/>LVL\s+(\d+)<\/span>/', $dash, $lvl);
        $level = "Level " . trim($lvl[1] ?? '0');
        preg_match('~font-weight: 700; color: #fff;">\s*([\d.,]+)\s*\/\s*([\d.,]+)\s*</div>~s', $dash, $exp);
        $current_exp = trim(($exp[1] ?? '0')." / ".($exp[2] ?? '0'));
        preg_match('/<span class="stat-number text-success">([^<]+)<\/span>/', $dash, $bal);
        $balance = trim($bal[1] ?? '0 Token');
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

function print_empty_task_notice($username, $balance, $level, $current_exp, $seconds = 300, $prefix = "  PTC cooldown") {
    banner($username, $balance, $level, $current_exp);
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

function timer_silent($seconds) {
    $wait_time = (int)$seconds;
    while ($wait_time > 0) {
        $start_time = microtime(true);
        while ((microtime(true) - $start_time) < 1) {
            usleep(100000);
            if ((microtime(true) - $start_time) >= 1) {
                break;
            }
        }
        $wait_time--;
    }
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

function smm_claim_headers($claim_url, $referer) {
    $origin = preg_replace('~^(https?://[^/]+).*$~', '$1', $claim_url);
    $headers = [
        'sec-ch-ua: "Not;A=Brand";v="8", "Chromium";v="127", "Google Chrome";v="127"',
        'sec-ch-ua-platform: "Android"',
        'x-requested-with: XMLHttpRequest',
        'user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        'accept: application/json, text/javascript, q=0.01',
        'content-type: application/x-www-form-urlencoded; charset=UTF-8',
        'sec-ch-ua-mobile: ?1',
        'origin: '.$origin,
        'sec-fetch-site: same-origin',
        'sec-fetch-mode: cors',
        'sec-fetch-dest: empty'
    ];
    if ($referer) {
        $headers[] = 'referer: '.$referer;
    }
    $headers[] = 'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7';
    return $headers;
}

function blog_headers($referer, $is_post = false) {
    $origin = preg_replace('~^(https?://[^/]+).*$~', '$1', $referer);
    $headers = [
        'sec-ch-ua: "Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"',
        'sec-ch-ua-mobile: ?1',
        'sec-ch-ua-platform: "Android"',
        'upgrade-insecure-requests: 1',
        'user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7',
        'sec-fetch-site: same-origin',
        'sec-fetch-mode: navigate',
        'sec-fetch-user: ?1',
        'sec-fetch-dest: document',
        'accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
    ];
    if ($is_post) {
        array_unshift($headers, 'cache-control: max-age=0');
        array_unshift($headers, 'content-type: application/x-www-form-urlencoded');
        array_unshift($headers, 'origin: '.$origin);
    }
    if ($referer) {
        $headers[] = 'referer: '.$referer;
    }
    return $headers;
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
            CURLOPT_COOKIEFILE => 'cookies.txt',
            CURLOPT_COOKIEJAR => 'cookies.txt'
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

function check_and_claim_tycoon($a, &$username, &$balance, &$level, &$current_exp) {
    $tycoonFile = "tycoon_time.txt";
    $lastTycoon = file_exists($tycoonFile) ? (int)file_get_contents($tycoonFile) : 0;
    $currentTime = time();
    $sisaTycoon = 3600 - ($currentTime - $lastTycoon);
    
    if ($sisaTycoon <= 0) {
        $tycoon_url = host."/tycoon";
        $tycoon_res = skibidixxx($tycoon_url, "GET", [], $a);
        refresh_dashboard_info($a, $username, $balance, $level, $current_exp);
        banner($username, $balance, $level, $current_exp);
        if (strpos($tycoon_res, "tycoon") !== false || strpos($tycoon_res, "success") !== false || strpos($tycoon_res, "claim") !== false) {
            print_task_log("TYCOON", 1, 318.86, "Tycoon Reward", "Halaman tycoon berhasil diakses dan diklaim!");
        } else {
            echo putih."[TYCOON] ".kuning."Akses halaman tycoon selesai.\n";
        }
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

$device_token = device_token_init();
allsuki($a,$b,$c,$d);

refresh_dashboard_info($a, $username, $balance, $level, $current_exp);
banner($username, $balance, $level, $current_exp);

	menu_misi:
	echo "\n";
	echo centerText("┌──────────────────────────────────────────┐", cyan) . "\n";
	echo centerText("│             PILIHAN MODE MISI            │", cyan) . "\n";
	echo centerText("├──────────────────────────────────────────┤", cyan) . "\n";
	echo centerText("│ 1. Watch Earn Only                       │", putih) . "\n";
	echo centerText("│ 2. Tycoon + Short Earn Only              │", putih) . "\n";
	echo centerText("│ 3. Mode 1+2 Loops                        │", putih) . "\n";
	echo centerText("│ 4. Mode 2+1 Loops                        │", putih) . "\n";
	echo centerText("│ 5. Perbarui CONFIG                       │", putih) . "\n";
	echo centerText("│ 0. Exit                                  │", putih) . "\n";
	echo centerText("└──────────────────────────────────────────┘", cyan) . "\n";
	echo centerText("Pilih [1/2/3/4/5/0] : ", putih);
	$pilihan = trim(fgets(STDIN));
	
	if ($pilihan === '0') {
		echo merah."Keluar...\n".reset;
		exit;
	}
	if ($pilihan === '5') {
		@unlink($configFile);
		@unlink($waryono);
		echo hijau."CONFIG lama dihapus. Masukkan data baru:\n".reset;
		goto home;
	}
	if ($pilihan === '1') {
		$mission_mode = 'watch_only';
	} elseif ($pilihan === '2') {
		$mission_mode = 'tycoon_ptc_only';
	} elseif ($pilihan === '3') {
		$mission_mode = 'mode1_2';
	} elseif ($pilihan === '4') {
		$mission_mode = 'mode2_1';
	} else {
		echo merah."Pilihan tidak valid!\n".reset;
		sleep(1);
		goto menu_misi;
	}

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
    	        refresh_dashboard_info($a, $username, $balance, $level, $current_exp);
    	        banner($username, $balance, $level, $current_exp);
    	        sleep(2);
    	    } else {
    	        sleep(2);
    	        goto menu_misi;
    	    }
    	} else {
    	    goto ulang;
        }
	}

	if ($mission_mode === 'tycoon_ptc_only') {
		goto ptc;
	} elseif ($mission_mode === 'mode2_1') {
		goto ptc;
	} elseif ($mission_mode === 'watch_only') {
		goto reload;
	} elseif ($mission_mode === 'mode1_2') {
		goto reload;
	}

	reload:
	smm_get:
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
	    if (strpos($watch, "There are no videos available for you right now") !== false) {
	        refresh_dashboard_info($a, $username, $balance, $level, $current_exp);
	        print_empty_task_notice($username, $balance, $level, $current_exp, 10, "  cooldown");
	        if ($mission_mode === 'mode1_2') {
	            goto ptc;
	        } else {
	            goto home;
	        }
	    }
	    if (strpos($watch, "You must wait at least") !== false) {
	        preg_match('~at least <strong>(\d+)\s*minutes?</strong>~i', $watch, $mnt);
	        $menit = intval($mnt[1] ?? 5);
	        refresh_dashboard_info($a, $username, $balance, $level, $current_exp);
	        print_empty_task_notice($username, $balance, $level, $current_exp, $menit * 60, "  cooldown");
	        goto smm_get;
	    }
	    sleep(5);
	    goto smm_get;
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
	    sleep(5);
	    goto smm_get;
	}

	$watched = 0;
	$task_counter = 1;
	while (true) {
	    timer_silent($required);
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
	    if ($status == 'success') {
	        refresh_dashboard_info($a, $username, $balance, $level, $current_exp);
	        banner($username, $balance, $level, $current_exp);
	        print_task_log("SURF ADS", $task_counter++, 320.50, "WATCH & EARN STREAM", $pesan);
	    }
	    if (($cp[1] ?? 'false') == 'true') {
	        break;
	    }
	    if (($rf[1] ?? 'false') == 'true' || $done) {
	        break;
	    }
	}
	goto smm_get;

	ptc:
	$ptc_counter = 1;
	youtube:
	check_and_claim_tycoon($a, $username, $balance, $level, $current_exp);
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
	        goto youtube;
	    }
	    timer_silent($wait);

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
	            refresh_dashboard_info($a, $username, $balance, $level, $current_exp);
	            banner($username, $balance, $level, $current_exp);
	            print_task_log("SURF ADS", $ptc_counter++, 325.00, "YOUTUBE PTC TASK", $pesan);
	            goto youtube;

	        } elseif (preg_match("/Swal\.fire\('[^']+',\s*'([^']+)',\s*'success'\)/s", $claim, $msg)) {
	            refresh_dashboard_info($a, $username, $balance, $level, $current_exp);
	            banner($username, $balance, $level, $current_exp);
	            print_task_log("SURF ADS", $ptc_counter++, 325.00, "YOUTUBE PTC TASK", trim($msg[1]));
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
	check_and_claim_tycoon($a, $username, $balance, $level, $current_exp);
	$url = host."/ptc/index/window";
	$ptc = skibidixxx($url, "GET", [], $a);
	preg_match_all('/wmv-url="([^"]+)"\s*wmv-sec="(\d+)"/', $ptc, $res);
	$url_view = $res[1][0] ?? '';
	$detik    = $res[2][0] ?? 0;
	if ($url_view) {
		$go = skibidixxx($url_view, "GET", [], $a);
		timer_silent($detik);
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
		        refresh_dashboard_info($a, $username, $balance, $level, $current_exp);
		        banner($username, $balance, $level, $current_exp);
		        print_task_log("SURF ADS", $ptc_counter++, 328.00, "WINDOW PTC TASK", $pesan);
		        goto kopet;

		    } elseif (preg_match("/Swal\.fire\('[^']+',\s*'([^']+)',\s*'success'\)/", $claim, $msg)) {
		        refresh_dashboard_info($a, $username, $balance, $level, $current_exp);
		        banner($username, $balance, $level, $current_exp);
		        print_task_log("SURF ADS", $ptc_counter++, 328.00, "WINDOW PTC TASK", $msg[1]);
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
	check_and_claim_tycoon($a, $username, $balance, $level, $current_exp);
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
		timer_silent($wait);

		nyawit:
		$bypass = cloud($apikey, $sitekey);
		if (is_array($bypass)) {
			$data = http_build_query([
				  "captcha" => "turnstile",
				  "cf-turnstile-response" => $bypass["turnstile"],
				  "csrf_token_name" => $token
			]);
		    $claim = skibidixxx($action, "POST", $data, $b);
		    if (preg_match("/Swal\.fire\('[^']+',\s*'([^']+)',\s*'success'\)/s", $claim, $msg)) {
		        $pesan = str_replace(['<br>', '<br/>', '<br />'], ' ', $msg[1]);
		        refresh_dashboard_info($a, $username, $balance, $level, $current_exp);
		        banner($username, $balance, $level, $current_exp);
		        print_task_log("SURF ADS", $ptc_counter++, 330.00, "IFRAME PTC TASK", trim($pesan));
		        goto coli;

		    } else {
		        goto coli;
		    }
		} else {
			goto nyawit;
	    }
	} else {
	    refresh_dashboard_info($a, $username, $balance, $level, $current_exp);
	    print_empty_task_notice($username, $balance, $level, $current_exp, 300, "  PTC cooldown");
	    
	    if ($mission_mode === 'tycoon_ptc_only') {
	        goto ptc;
	    } elseif ($mission_mode === 'mode2_1') {
	        goto reload;
	    } else {
	        goto ptc;
	    }
	}






#Created by AHD1905 
