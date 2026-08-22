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
const script_name = "feyorra";
const host        = "https://feyorra.top";

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
        echo putih . "Cookie    : " . kuning;
        $coki = trim(fgets(STDIN));
        // API Key tidak dipakai lagi, tapi kita simpan kosong
        $data = [
            "apikey"   => "",
            "coki" => $coki
        ];
        file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
        echo hijau . "Konfigurasi disimpan ke $configFile\n\n" . reset;
        sleep(3);
        return $data;
    }
    return json_decode(file_get_contents($configFile), true);
}

// Fungsi ocr dihapus total

function allhwaders(&$a, &$b, &$c, $coki){
	$a = [
		"host: feyorra.top",
		"user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36",
		"accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
		"sec-fetch-site: same-origin",
		"sec-fetch-mode: navigate",
		"sec-fetch-user: ?1",
		"sec-fetch-dest: document",
		"referer: https://feyorra.top/",
		"accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
		"cookie: ".$coki
	];

	$b = [
		"host: feyorra.top",
		"origin: https://feyorra.top",
		"content-type: application/x-www-form-urlencoded",
		"user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36",
		"accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,q=0.8,application/signed-exchange;v=b3;q=0.7",
		"referer: https://feyorra.top/login",
		"accept-language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
		"cookie: ".$coki
	];

	$c = [
		"host: feyorra.top",
		"user-agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36",
		"accept: image/avif,image/webp,image/apng,image/svg+xml,image,q=0.8",
		"sec-fetch-dest: image",
		"referer: https://feyorra.top/faucet",
		"cookie: ".$coki
	];
}

home:
clear();
$config   = getConfig($configFile);
$coki    = $config['coki'];

clear();

allhwaders($a,$b,$c,$coki);
$url  = host."/dashboard";
$dash = skibidixxx($url, "GET", [], $a);
if (strpos($dash, "Dashboard") !== false) {
    $balance = explode("</p>", explode("<p>", $dash)[1])[0];
    echo putih."Account balance ".cyan.$balance."\n\n";

	fc:
	while(true){
    $url    = host."/faucet";
    $faucet = skibidixxx($url, "GET", [], $a);
    
    // ===== HAPUS PENGE CEKAN SHORTLINK & PTC =====
    // Kita abaikan semua pesan misi, kita lanjut aja
    // Cuma kita tetap cek apakah ada tombol claim (Ready To Claim)

    if (strpos($faucet, "Ready To Claim") !== false) {
		preg_match('/id="token" value="([^"]+)"/', $faucet, $matches_csrf);
		$csrf = $matches_csrf[1] ?? '';
		preg_match('/name="token" value="([^"]+)"/', $faucet, $matches_token);
		$token = $matches_token[1] ?? '';
		preg_match('/class="form-control border border-dark mb-3" name="([^"]+)"/', $faucet, $matches);
		$border = $matches[1] ?? '';

		// ===== BYPASS CAPTCHA =====
		// Kita kirim captcha kosong (atau dummy)
		$text = ''; // kosong
		
		$data = http_build_query([
			"csrf_token_name" => $csrf,
			"token" => $token,
			$border => $text
		]);
		
		$url = host."/faucet/verify";
		$claim = skibidixxx($url, "POST", $data, $b);
		
		if (preg_match("/title: '([^']+)'/", $claim, $win)) {
		    $timer_val = explode(' -', explode('let wait = ', $claim)[1])[0];
		    echo putih."[Success] ".hijau.$win[1] . "\n";
		    timer($timer_val, "  next");
		} elseif (preg_match('/alert-danger">.*?<\/i>\s*([^<]+)/s', $claim, $fail)) {
		    echo putih."[Failed] " .merah. trim($fail[1]) . "\n";
		    // coba lagi setelah timer kecil
		    timer(10, "  retry...");
		} else {
		    echo "Error: Respon zonk atau limit, Cuki!\n";
		    timer(10, "  retry...");
		}

    } else {
    	// Jika belum ready, ambil timer dari halaman
    	if (preg_match('/let wait = (\d+)/', $faucet, $mt)) {
    	    $timer_val = $mt[1];
    	} else {
    	    $timer_val = 60; // default
    	}
    	timer($timer_val, "  next");
    	goto fc;
    }

}

} else {
    clear();
    echo putih."login required!...\n";
    @unlink($configFile);
    sleep(3);
    goto home;
}
