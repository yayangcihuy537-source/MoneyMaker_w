<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');
$configFile = "config.json";
$waryono = "cookies.txt"; // masih dipake buat cookie jar

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
const script_name = "claimtrx.com";
const host        = "https://claimtrx.com";

function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
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
            if ((microtime(true) - $start_time) >= 1) {
                break;
            }
        }
        $wait_time--;
    }
    echo "\r                                     \r";
}

function getConfig($configFile) {
    if (!file_exists($configFile)) {
        echo putih . "API Key   : " . kuning;
        $apikey = trim(fgets(STDIN));
        echo putih . "Cookie    : " . kuning;
        $coki = trim(fgets(STDIN));
        $data = [
            "apikey"   => $apikey,
            "coki" => $coki
        ];
        file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
        echo hijau . "Konfigurasi disimpan ke $configFile\n\n" . reset;
        sleep(3);
        return $data;
    }
    return json_decode(file_get_contents($configFile), true);
}

// Fungsi cloud dan ocr sudah dihapus (tidak dipakai)

function allhwaders(&$a, &$b, &$coki){
	$a = [
		"host: claimtrx.com",
		"user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36",
		"accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
		"sec-fetch-site: same-origin",
		"sec-fetch-mode: navigate",
		"sec-fetch-user: ?1",
		"sec-fetch-dest: document",
		"referer: https://claimtrx.com/",
		"accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
		"cookie: ".$coki
	];

	$b = [
		"host: claimtrx.com",
		"origin: https://claimtrx.com",
		"content-type: application/x-www-form-urlencoded",
		"user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36",
		"accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
		"referer: https://claimtrx.com/login",
		"accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
		"cookie: ".$coki
	];
}

home:
clear();
$config   = getConfig($configFile);
$apikey   = $config['apikey']; // masih disimpan, mungkin dipakai nanti
$coki    = $config['coki'];

clear();

allhwaders($a,$b,$coki);
$url  = host."/dashboard";
$dash = skibidixxx($url, "GET", [], $a);
if (strpos($dash, "Dashboard") !== false) {
    preg_match('/Balance.*?font-18">([^<]+)<\/h2>/s', $dash, $res);
    $balance = $res[1] ?? '';

    echo putih."Account balance ".cyan.$balance."\n\n";

	fc:
	while(true){
    $url    = host."/faucet";
    $faucet = skibidixxx($url, "GET", [], $a);
    
    // ===== HAPUS PENGE CEKAN SHORTLINK & PTC =====
    // Kita abaikan pesan itu, kita tetap lanjut
    // Tapi tetap kita cek apakah ada tombol claim atau form

    if (strpos($faucet, "READY") !== false) {
		preg_match('/id="token" value="([^"]+)"/', $faucet, $matches_csrf);
		$csrf = $matches_csrf[1] ?? '';
		preg_match('/name="token" value="([^"]+)"/', $faucet, $matches_token);
		$token = $matches_token[1] ?? '';
		preg_match('/class="form-control border border-dark mb-3" name="([^"]+)"/', $faucet, $matches);
		$border = $matches[1] ?? '';

		// ===== BYPASS CAPTCHA =====
		// Kita kirim captcha kosong atau nilai dummy
		// Bisa juga kita coba tanpa field captcha, tapi kita kirim field kosong
		$text = ''; // kosong, atau coba "dummy"
		
		$data = http_build_query([
			"csrf_token_name" => $csrf,
			"token" => $token,
			$border => $text // <-- captcha field dikosongkan
		]);
		
		$url = host."/faucet/verify";
		$claim = skibidixxx($url, "POST", $data, $b);
		
		if (preg_match("/title: '([^']+)'/", $claim, $win)) {
		    $timer_val = explode(' -', explode('var wait = ', $claim)[1])[0];
		    echo putih."[Success] ".hijau.$win[1] . "\n";
		    timer($timer_val, "  next...");
		} elseif (preg_match('/alert-danger">.*?<\/i>\s*([^<]+)/s', $claim, $fail)) {
		    echo putih."[Failed] " .merah. trim($fail[1]);
		    sleep(1);
		    echo "\r                                         \r";
		    goto fc;
		} else {
		    echo "Error: Respon zonk atau limit, Cuki!\n";
		    // coba lagi
		    timer(10, "  retry...");
		}

    } else {
    	$timer_val = explode(' -', explode('var wait = ', $faucet)[1])[0];
    	timer($timer_val, "  next...");
    	goto fc;
    }

}

} else {
    clear();
    echo putih."login required!...\n";
    sleep(2);
    @unlink($waryono); @unlink($configFile);
    goto home;
}
