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

const base_url   = "https://btc.tonrevenue.space";
const GIGA_URL   = "https://ad.gigapub.tech/v1/ad";
const GIGA_PROJ  = "5736";
const GIGA_TOKEN = "CEEUHXgZVL184wyaDp6laEchjHQ7RNN3";
const UA_TG      = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.199 Mobile Safari/537.36 Telegram-Android/12.9.1 (Xiaomi M2006C3LG; Android 10; SDK 29; AVERAGE)";

function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function timer($seconds, $prefix = "[!] please wait") {
    $wait_time = (int)$seconds;
    if ($wait_time < 1) return;
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

function getConfig($configFile) {
    if (!file_exists($configFile)) {
        echo putih . "initData (TG) : " . kuning;
        $initData = trim(fgets(STDIN));
        file_put_contents($configFile, json_encode(["initData" => $initData], JSON_PRETTY_PRINT));
        echo hijau . "Konfigurasi disimpan ke $configFile\n\n" . reset;
        sleep(2);
        return ["initData" => $initData];
    }
    return json_decode(file_get_contents($configFile), true);
}

function is_init_error($j) {
    $msg = ($j['detail'] ?? '') . ' ' . ($j['message'] ?? '');
    return (stripos($msg, 'InitData') !== false || stripos($msg, 'session expired') !== false);
}

function refresh_initdata() {
    global $configFile, $initData;
    echo putih . "initData baru: " . kuning;
    $new = trim(fgets(STDIN));
    if ($new === '') return false;
    file_put_contents($configFile, json_encode(["initData" => $new], JSON_PRETTY_PRINT));
    $initData = $new;
    return true;
}

function http_json($url, $payload, $headers, $timeout = 20) {
    $ch = curl_init();
    $opts = [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_SSL_VERIFYHOST => 2,
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_CONNECTTIMEOUT => $timeout,
        CURLOPT_TIMEOUT => $timeout,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($payload),
    ];
    curl_setopt_array($ch, $opts);
    $response = curl_exec($ch);
    curl_close($ch);
    return json_decode($response, true);
}

function tg_headers($extra = []) {
    $h = [
        'user-agent: ' . UA_TG,
        'content-type: application/json',
        'x-requested-with: org.telegram.messenger.web',
        'origin: ' . base_url,
        'referer: ' . base_url . '/tasks',
        'sec-ch-ua: "Not=A?Brand";v="99", "Android WebView";v="151", "Chromium";v="151"',
        'sec-ch-ua-mobile: ?1',
        'sec-ch-ua-platform: "Android"',
        'sec-fetch-site: same-origin',
        'sec-fetch-mode: cors',
        'sec-fetch-dest: empty',
        'accept-language: en,id-ID;q=0.9,id;q=0.8'
    ];
    foreach ($extra as $e) $h[] = $e;
    return $h;
}

function api($path, $extra = []) {
    global $initData;
    for ($try = 0; $try < 2; $try++) {
        $r = http_json(base_url . $path, array_merge(["initData" => $initData], $extra), tg_headers());
        if ($try == 0 && is_init_error($r)) {
            refresh_initdata();
            continue;
        }
        return $r;
    }
    return $r;
}

function giga_call($body) {
    $extra = [
        'authorization: Bearer ' . GIGA_TOKEN,
        'project-id: ' . GIGA_PROJ
    ];
    return http_json(GIGA_URL, $body, tg_headers($extra));
}

function giga_user() {
    global $initData;
    parse_str($initData, $p);
    $u = json_decode($p['user'] ?? '{}', true);
    return ['user' => $u, 'platform' => 'android', 'version' => '9.6', 'start_param' => null];
}

function get_state() {
    $r = api("/api/tasks/ads/state");
    return $r['tasks'] ?? [];
}

function fmt($n) {
    return rtrim(rtrim(number_format((float)$n, 8, '.', ''), '0'), '.');
}

function get_init() {
    for ($try = 0; $try < 2; $try++) {
        $r = http_json(base_url . "/api/init", [
            "initData" => $GLOBALS['initData'],
            "start_param" => null,
            "fingerprint" => "aabbccddeeff00112233445566778899",
            "ua" => UA_TG,
            "screen" => "412x915",
            "lang" => "id",
            "tz" => "Asia/Jakarta",
            "platform" => "Linux armv81",
            "tg_platform" => "android",
            "viewport_width" => 412,
            "viewport_height" => 891,
            "max_touch_points" => 5,
            "device_pixel_ratio" => 2.625
        ], tg_headers());
        if ($try == 0 && is_init_error($r)) {
            refresh_initdata();
            continue;
        }
        return $r;
    }
    return $r;
}

function captcha_answer($ch) {
    $prompt = strtolower(trim(preg_replace('/[^a-zA-Z ]/', '', $ch['prompt'] ?? '')));
    if (preg_match('/the (\w+)/', $prompt, $m)) $want = $m[1];
    else $want = trim(preg_replace('/tap /', '', $prompt));
    foreach (($ch['options'] ?? []) as $o) {
        if (strtolower($o['id'] ?? '') === $want || strtolower($o['label'] ?? '') === $want) {
            return $o['id'];
        }
    }
    return '';
}

function ensure_captcha() {
    for ($try = 0; $try < 3; $try++) {
        $j = get_init();
        $u = $j['user'] ?? [];
        $ch = $u['captcha_challenge'] ?? null;
        if (!$ch) return true;
        $ans = captcha_answer($ch);
        if ($ans === '') {
            echo putih . "[CAPTCHA] " . merah . "jawaban gak ketemu utk '" . ($ch['prompt'] ?? '?') . "'\n";
            return false;
        }
        echo putih . "[CAPTCHA] " . kuning . "solve '" . ($ch['prompt'] ?? '?') . "' -> " . $ans . "...\n";
        $r = api("/api/captcha/verify", ["challenge_id" => $ch['challenge_id'], "answer" => $ans]);
        if (($r['status'] ?? '') == 'success') {
            echo putih . "[CAPTCHA] " . hijau . "OK\n";
            return true;
        }
        echo putih . "[CAPTCHA] " . merah . ($r['detail'] ?? $r['message'] ?? 'gagal') . "\n";
        sleep(2);
    }
    return false;
}

function do_farm() {
    $notified_limit = [];

    while (true) {
        $tasks = get_state();
        if (!$tasks) {
            echo putih . "[STATE] " . merah . "kosong/gagal, coba captcha...\n";
            ensure_captcha();
            $tasks = get_state();
            if (!$tasks) {
                timer(60, "  retry...");
                continue;
            }
        }

        $busy = 0;
        $tried_any = false;
        $claimed = false;
        foreach ($tasks as $t) {
            $prov = $t['provider'] ?? '';
            if (!in_array($prov, ['adexium', 'gigapubs'])) continue;
            $rem = intval($t['remaining_today'] ?? 0);
            $cdl = intval($t['cooldown_left'] ?? 0);
            $cds = intval($t['cooldown_seconds'] ?? 300);
            if ($rem <= 0) {
                if (empty($notified_limit[$prov])) {
                    echo putih . "[" . cyan . $prov . putih . "] " . kuning . "limit hari ini habis, skip\n";
                    $notified_limit[$prov] = true;
                }
                continue;
            }
            if ($cdl > 0) { $busy = max($busy, $cdl); continue; }
            $tried_any = true;

            $st = api("/api/tasks/ads/start", ["provider" => $prov, "interaction" => null]);
            $sid = $st['session_uid'] ?? '';
            if (!$sid) {
                echo putih . "[" . cyan . $prov . putih . "] " . merah . ($st['detail'] ?? $st['message'] ?? 'start gagal') . "\n";
                continue;
            }

            $cfg_status = 'success';
            if ($prov == 'gigapubs') {
                $tg = giga_user();
                giga_call(['method' => 'init', 'args' => ['user' => $tg], 'version' => 'v85', 'seconds' => 9.9]);
                $uniq = mt_rand(100000000, 999999999) . '.' . mt_rand(100000, 999999);
                $any = ['showDone' => true, 'fallPriorityList' => ['rich','rD','t','d','monetag','m1','o1','rB'], 'fallRotationType' => 'priority', 'showCounter' => 0, 'showTryCounter' => 0, 'uniqShowId' => $uniq, 'readyNetsCount' => 4, 'showTag' => null];
                $base = ['user' => $tg, 'placementId' => 'main', 'transactionId' => null, 'version' => 'v85'];
                giga_call(['method' => 'adShowTryStart', 'args' => $base + ['network' => 't', 'rotationType' => 'priority', 'showCounter' => 0, 'anyData' => $any]]);
                sleep(4);
                $any2 = $any; $any2['showDone'] = false; $any2['showTryCounter'] = 1;
                giga_call(['method' => 'adShowed', 'args' => $base + ['network' => 't', 'rotationType' => 'priority', 'showCounter' => 0, 'seconds' => 18.7, 'anyData' => $any2]]);
                $any3 = $any; $any3['showCounter'] = 1; $any3['showTryCounter'] = 2;
                giga_call(['method' => 'adShowTryStart', 'args' => $base + ['network' => 'd', 'rotationType' => 'priority', 'showCounter' => 1, 'anyData' => $any3]]);
                sleep(4);
                $any4 = $any3; $any4['showDone'] = true;
                giga_call(['method' => 'adShowedX', 'args' => $base + ['network' => 'd', 'rotationType' => 'priority', 'showCounter' => 2, 'seconds' => 32.8, 'anyData' => $any4]]);
            }

            $cf = api("/api/tasks/ads/confirm", ["session_uid" => $sid]);
            $status = $cf['status'] ?? '';
            if ($status == 'success' || $status == 'already_confirmed') {
                $amt = $cf['reward_sats'] ?? 0.2;
                $nb  = $cf['new_balance'] ?? '?';
                $used = intval($cf['used_today'] ?? 0);
                $c = intval($cf['cooldown'] ?? $cds);
                echo putih . "[" . cyan . $prov . putih . "] +" . hijau . fmt($amt) . " sat - " . biru . $used . "/" . ($used + intval($cf['remaining_today'] ?? $rem)) . " - balance " . biru . fmt($nb) . " sat\n";
                $busy = max($busy, $c);
                $claimed = true;
                timer(mt_rand(8, 10), "  wait...");
            } elseif ($status == 'pending_postback') {
                echo putih . "[" . cyan . $prov . putih . "] " . kuning . "pending postback\n";
                $busy = max($busy, $cds);
            } else {
                echo putih . "[" . cyan . $prov . putih . "] " . merah . ($cf['detail'] ?? $cf['message'] ?? $status ?? 'gagal') . "\n";
            }
        }

        if ($busy > 0) {
            timer($busy, "  next...");
            continue;
        }
        if (!$tried_any) {
            echo putih . "semua limit hari ini, exit...\n";
            return;
        }
        if ($claimed) {
            timer(5, "  wait...");
            continue;
        }
        timer(20, "  retry...");
    }
}

clear();
$config   = getConfig($configFile);
$initData = $config['initData'];

while (true) {
    clear();
    echo putih . "tonrevenue ad farm | Bypass ADS\n";

    ensure_captcha();
    $ib = get_init();
    if (isset($ib['user'])) {
        $u = $ib['user'];
        $acc = $ib['access'] ?? [];
        echo putih . "balance    : " . biru . fmt($u['balance'] ?? 0) . " sat\n";
        if (!empty($acc['mobile_only_blocked'])) {
            echo putih . "status     : " . merah . "MOBILE ONLY BLOCKED" . "\n";
        } elseif (!empty($u['is_blocked'])) {
            echo putih . "status     : " . merah . "BLOCKED (" . ($u['ban_reason'] ?? '?') . ")\n";
        } else {
            echo putih . "status     : " . hijau . "clean" . putih . " (risk " . ($u['risk_level'] ?? '?') . " " . ($u['risk_score'] ?? '?') . ")\n";
        }
    } else {
        echo putih . "balance    : " . merah . "gagal fetch (" . ($ib['detail'] ?? '?') . ")\n";
    }

    $tasks = get_state();
    if ($tasks) {
        foreach ($tasks as $t) {
            $prov = $t['provider'] ?? '';
            if (!in_array($prov, ['adexium', 'gigapubs'])) continue;
            $used = intval($t['daily_cap'] ?? 0) - intval($t['remaining_today'] ?? 0);
            echo putih . str_pad($prov, 10) . ": " . biru . $used . "/" . ($t['daily_cap'] ?? '?')
               . putih . " | reward " . cyan . ($t['reward_sats'] ?? '?') . " sat"
               . putih . " | cooldown " . cyan . ($t['cooldown_left'] ?? '?') . "s\n";
        }
    } else {
        echo putih . "tasks      : " . merah . "gagal fetch state\n";
    }

    echo "\n";
    echo putih . "  1. " . cyan . "Start Farm" . putih . " (Adexium + GigaPubs)\n";
    echo putih . "  0. " . merah . "Exit\n";
    echo putih . "pilih: " . kuning;
    $opt = trim(fgets(STDIN));
    if ($opt == '1') {
        do_farm();
        echo "\n" . putih . "enter untuk kembali...";
        fgets(STDIN);
    } elseif ($opt == '0') {
        exit;
    }
}

