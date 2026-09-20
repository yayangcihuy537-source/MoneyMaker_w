<?php
/**
 * EarnSolana.xyz - Auto Faucet Claim (FULL VERSION v3)
 * Fix: daily limit false positive setelah claim sukses
 */

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');

$configFile = "config.json";
$cookieFile = "session/es_cookies.txt";

if (!is_dir('session')) mkdir('session', 0777, true);

const R  = "\033[0;31m";
const G  = "\033[0;32m";
const Y  = "\033[0;33m";
const CY = "\033[0;36m";
const W  = "\033[0;37m";
const X  = "\033[0m";

const HOST   = "https://earnsolana.xyz";
const DEF_UA = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36";

// ==================== UTILITY ====================
function clear(){ (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls','w')); }

function maskEmail($e){
    if (!filter_var($e, FILTER_VALIDATE_EMAIL)) return $e;
    list($u, $d) = explode('@', $e);
    if (strlen($u) <= 4) return substr($u,0,1) . '****@' . $d;
    return substr($u,0,2) . '****' . substr($u,-2) . '@' . $d;
}

function log_msg($m, $t='info'){
    $p = ['success'=>G."✓ ",'error'=>R."✗ ",'warn'=>Y."⚠ ", 'info'=>CY."» "][$t] ?? CY."» ";
    echo $p.$m.X."\n"; flush();
}

function timer($sec, $label="wait"){
    $sec = (int)$sec; if ($sec<1) return;
    $spin = ['⣾','⣽','⣻','⢿','⡿','⣟','⣯','⣷']; $si=0;
    while ($sec>0){
        $t = sprintf("%02d:%02d:%02d", floor($sec/3600), floor(($sec%3600)/60), $sec%60);
        echo "\r\033[K".Y." $label: ".G.$t.W." ".$spin[$si].X;
        $si = ($si+1)%8; sleep(1); $sec--;
    }
    echo "\r\033[K"; flush();
}

function req($url, $method='GET', $data=null, $headers=[]){
    global $cookieFile;
    $ch = curl_init();
    $opts = [
        CURLOPT_URL            => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER         => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT        => 60,
        CURLOPT_HTTPHEADER     => $headers,
        CURLOPT_COOKIEFILE     => $cookieFile,
        CURLOPT_COOKIEJAR      => $cookieFile,
    ];
    if ($method === 'POST'){
        $opts[CURLOPT_POST] = true;
        $opts[CURLOPT_POSTFIELDS] = is_array($data) ? http_build_query($data) : $data;
    }
    curl_setopt_array($ch, $opts);
    $resp = curl_exec($ch);
    if ($resp === false){ @curl_close($ch); return null; }
    $hs   = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $body = substr($resp, $hs);
    @curl_close($ch);
    return $body;
}

// ==================== HTML PARSERS ====================
function get_csrf_from_html($html){
    if (preg_match('/name="csrf_token_name"[^>]*value="([^"]+)"/i', $html, $m)) return $m[1];
    return null;
}

function get_balance($html){
    if (preg_match('/balance-amount">\s*([\d.]+)\s*<span/i', $html, $m)) return (float)$m[1];
    if (preg_match('/Available Balance.*?<h3[^>]*>\s*([\d.]+)/s', $html, $m)) return (float)$m[1];
    return null;
}

function get_total_claims($html){
    if (preg_match('/Total Faucet Claims.*?<h4>(\d+)</s', $html, $m)) return (int)$m[1];
    return null;
}

function get_today_claims($html){
    if (preg_match('/Today Faucet Claims.*?<h4>(\d+)</s', $html, $m)) return (int)$m[1];
    return null;
}

function is_logged_in($html){
    return strpos($html, 'Logout') !== false
        || strpos($html, 'Dashboard | EarnSolana') !== false
        || strpos($html, 'Welcome back') !== false
        || strpos($html, 'profile-banner') !== false;
}

// ==================== FIX: DAILY LIMIT CHECK ====================
// Cuma trigger kalau ada keyword eksplisit. NO heuristic.
function is_daily_limit($html){
    $low = strtolower($html);

    $triggers = [
        'daily limit reached',
        'reached daily limit',
        'reached your daily limit',
        'you have reached the daily limit',
        'daily claim limit reached',
        'daily claim limit',
        'daily claims exhausted',
        'come back tomorrow',
        'try again tomorrow',
        'max claim per day',
        'daily max claim',
        'maximum daily claim',
        'claim limit for today',
    ];

    foreach ($triggers as $t){
        if (strpos($low, $t) !== false) return true;
    }
    return false;
}

function get_daily_limit_info($html){
    $info = ['used'=>null, 'limit'=>null, 'remaining'=>null, 'reset'=>null];
    if (preg_match('/daily claim[s]?[^0-9]*(\d+)\s*\/\s*(\d+)/i', $html, $m)){
        $info['used']  = (int)$m[1];
        $info['limit'] = (int)$m[2];
        $info['remaining'] = $info['limit'] - $info['used'];
    }
    if (preg_match('/reached\s+(\d+)\s+claims?\s+today/i', $html, $m)){
        $info['used'] = (int)$m[1];
    }
    if (preg_match('/reset[s]?\s+in\s+([^<]+)/i', $html, $m)){
        $info['reset'] = trim($m[1]);
    }
    return $info;
}

function get_faucet_form_data($html){
    $data = ['csrf'=>null,'token'=>null,'earn_ticket'=>null,'wallet'=>null];
    if (preg_match('/name="csrf_token_name"[^>]*value="([^"]+)"/i', $html, $m)) $data['csrf'] = $m[1];
    if (preg_match('/name="token"[^>]*value="([^"]+)"/i', $html, $m)) $data['token'] = $m[1];
    if (preg_match('/name="earn_ticket"[^>]*value="([^"]+)"/i', $html, $m)) $data['earn_ticket'] = $m[1];
    if (preg_match('/name="wallet"[^>]*value="([^"]+)"/i', $html, $m)) $data['wallet'] = $m[1];
    return $data;
}

function get_captcha_type($html){
    if (preg_match('/name="captcha"[^>]*value="([^"]+)"/i', $html, $m)) return $m[1];
    return 'turnstile';
}

function get_min_wait($html){
    if (preg_match('/let wait = (\d+)/', $html, $m)) return (int)$m[1];
    return 0;
}

function has_faucet_form($html){
    return strpos($html, 'id="fauform"') !== false
        && strpos($html, 'earn_ticket') !== false;
}

// ==================== FP HASH & DEVICE TOKEN ====================
function gen_fp_hash($ua = DEF_UA){
    $raw = "fp-" . $ua . "360" . "640";
    return hash('sha256', $raw);
}

function gen_device_token(){
    $chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    $rand = '';
    for ($i=0; $i<13; $i++) $rand .= $chars[random_int(0, strlen($chars)-1)];
    $ts = base_convert(time(), 10, 36);
    return 'dev_' . $rand . $ts;
}

// ==================== LOGIN ====================
function do_login($email){
    log_msg("Login: ".maskEmail($email), 'info');

    $h0 = [
        "user-agent:".DEF_UA,
        "accept-language:id-ID",
        "accept:text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "upgrade-insecure-requests:1",
    ];

    $home = req(HOST.'/', 'GET', null, $h0);
    if (!$home){ log_msg("Gagal load /", 'error'); return false; }

    $csrf = get_csrf_from_html($home);
    if (!$csrf){ log_msg("CSRF tidak ketemu di homepage", 'error'); return false; }

    $device_token = gen_device_token();

    $body = [
        'wallet'          => $email,
        'csrf_token_name' => $csrf,
        'device_token'    => $device_token,
    ];

    $h = array_merge($h0, [
        "content-type:application/x-www-form-urlencoded",
        "origin:".HOST,
        "referer:".HOST."/",
        "cache-control:max-age=0",
    ]);

    $resp = req(HOST.'/auth/login', 'POST', $body, $h);
    if (!$resp){ log_msg("Login request gagal", 'error'); return false; }

    $dash = req(HOST.'/dashboard', 'GET', null, $h0);
    if ($dash && is_logged_in($dash)){
        log_msg("Login OK!", 'success');
        return $dash;
    }

    log_msg("Login gagal", 'error');
    return false;
}

// ==================== DASHBOARD ====================
function check_dashboard(){
    $h = ["user-agent:".DEF_UA, "accept-language:id-ID"];
    $dash = req(HOST.'/dashboard', 'GET', null, $h);
    if (!$dash || !is_logged_in($dash)) return null;
    return [
        'html'         => $dash,
        'balance'      => get_balance($dash),
        'total_claims' => get_total_claims($dash),
        'today_claims' => get_today_claims($dash),
    ];
}

// ==================== CLAIM FAUCET ====================
function claim_faucet($email, $max_claims = 250, $wait_between = 60){
    $h0 = [
        "user-agent:".DEF_UA,
        "accept-language:id-ID",
        "accept:text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "upgrade-insecure-requests:1",
    ];

    $total_claimed = 0;
    $consecutive_fail = 0;

    while (true){
        if ($total_claimed >= $max_claims){
            log_msg("Max claim ($max_claims) tercapai. Stop.", 'warn');
            break;
        }

        log_msg("=== Siklus #".($total_claimed+1)."/$max_claims ===", 'info');

        // Step 1: GET /faucet/earn
        $page = req(HOST.'/faucet/earn', 'GET', null, $h0);
        if (!$page){
            log_msg("Gagal load /faucet/earn", 'error');
            $consecutive_fail++;
            if ($consecutive_fail >= 5){ log_msg("5x gagal berturut, stop.", 'error'); break; }
            timer(15, 'Retry'); continue;
        }
        $consecutive_fail = 0;

        // Session check
        if (!is_logged_in($page) && !has_faucet_form($page)){
            log_msg("Session expired, login ulang...", 'warn');
            $dash = do_login($email);
            if (!$dash){ timer(30, 'Retry'); continue; }
            continue;
        }

        // Daily limit check di halaman (SEBELUM claim)
        if (is_daily_limit($page)){
            log_msg("DAILY LIMIT tercapai di halaman faucet!", 'warn');
            $lim = get_daily_limit_info($page);
            if ($lim['used'] !== null || $lim['limit'] !== null){
                log_msg("Daily claim: ".($lim['used'] ?? '?')."/".($lim['limit'] ?? '?'), 'info');
            }
            if ($lim['reset']) log_msg("Reset: ".$lim['reset'], 'info');

            $d = check_dashboard();
            if ($d){
                if ($d['today_claims'] !== null) log_msg("Today claims: ".$d['today_claims'], 'info');
                if ($d['total_claims'] !== null) log_msg("Total claims: ".$d['total_claims'], 'info');
                if ($d['balance'] !== null)      log_msg("Balance: ".$d['balance']." Coins", 'info');
            }
            break;
        }

        // Parse form
        $form = get_faucet_form_data($page);
        if (!$form['csrf'] || !$form['token'] || !$form['earn_ticket']){
            log_msg("Form data tidak lengkap (csrf/token/ticket)", 'error');
            log_msg("csrf=".substr($form['csrf'] ?? 'NULL',0,20)." token=".substr($form['token'] ?? 'NULL',0,20)." ticket=".substr($form['earn_ticket'] ?? 'NULL',0,20), 'debug');
            $consecutive_fail++;
            if ($consecutive_fail >= 5){ log_msg("5x form invalid, stop.", 'error'); break; }
            timer(15, 'Retry'); continue;
        }

        $captcha_type = get_captcha_type($page);
        $wait_sec = get_min_wait($page);
        if ($wait_sec > 0){
            log_msg("Server minta tunggu {$wait_sec}s", 'warn');
            timer($wait_sec + 2, 'Cooldown');
            continue;
        }

        log_msg("Form OK. Token=".substr($form['token'],0,8)."... ticket=".substr($form['earn_ticket'],0,8)."...", 'info');

        // POST /faucet/earn
        $fp_hash = gen_fp_hash();
        $body = [
            'csrf_token_name' => $form['csrf'],
            'token'           => $form['token'],
            'earn_ticket'     => $form['earn_ticket'],
            'fp_hash'         => $fp_hash,
            'confirm_wallet'  => '',
            'wallet'          => $form['wallet'] ?: $email,
            'captcha'         => $captcha_type,
        ];

        $h_post = array_merge($h0, [
            "content-type:application/x-www-form-urlencoded",
            "origin:".HOST,
            "referer:".HOST."/faucet/earn",
            "cache-control:max-age=0",
        ]);

        $resp = req(HOST.'/faucet/earn', 'POST', $body, $h_post);
        if (!$resp){
            log_msg("POST /faucet/earn gagal", 'error');
            $consecutive_fail++;
            if ($consecutive_fail >= 5){ log_msg("5x POST gagal, stop.", 'error'); break; }
            timer(15, 'Retry'); continue;
        }

        // Step 2: Cek hasil claim
        $low = strtolower($resp);
        $is_success = strpos($low, 'success') !== false
            && (strpos($low, 'coins has been added') !== false
                || strpos($low, 'has been added to your account') !== false
                || strpos($low, 'added to your account balance') !== false);

        if ($is_success){
            $total_claimed++;
            $consecutive_fail = 0;

            $reward = 0;
            if (preg_match('/([\d.]+)\s*Coins has been added/i', $resp, $m)) $reward = (float)$m[1];
            log_msg("CLAIM #$total_claimed OK! +".$reward." Coins", 'success');

            // Refresh dashboard
            $d = check_dashboard();
            if ($d){
                if ($d['balance'] !== null)      log_msg("Balance: ".G.$d['balance'].W." Coins", 'info');
                if ($d['today_claims'] !== null) log_msg("Today claims: ".$d['today_claims'], 'info');
                if ($d['total_claims'] !== null) log_msg("Total claims: ".$d['total_claims'], 'info');
            }

            // FIX: HANYA cek daily limit dari response kalau ada keyword EKSPLISIT
            // Ga pakai heuristic "form hilang"
            if (is_daily_limit($resp)){
                log_msg("Daily limit tercapai setelah claim ini (dari response).", 'warn');
                break;
            }

            timer($wait_between + random_int(2,8), 'Next claim');
            continue;
        }

        // FIX: Cek daily limit di response HANYA kalau bukan success
        // (biar ga false positive kalau response = halaman sukses yang redirect)
        if (is_daily_limit($resp)){
            log_msg("DAILY LIMIT tercapai (response).", 'warn');
            break;
        }

        // Gagal claim — kemungkinan cooldown, coba lagi
        log_msg("Claim gagal / response tidak dikenali", 'error');
        $consecutive_fail++;
        if ($consecutive_fail >= 5){ log_msg("5x claim gagal berturut, stop.", 'error'); break; }
        timer(20, 'Retry');
    }

    echo W."-----------------------------------------------\n";
    echo W."Total claimed: ".G.$total_claimed.W." kali (max: $max_claims)\n";
    echo W."-----------------------------------------------\n";

    return ['ok'=>true, 'claimed'=>$total_claimed];
}

// ==================== UI ====================
function bannerMain(){
    echo W."===============================================\n";
    echo Y."   BOT EARNSOLANA.XYZ - Auto Faucet Claim\n";
    echo W."===============================================\n";
}

function saveConfig($f,$d){ file_put_contents($f, json_encode($d, JSON_PRETTY_PRINT)); }

function getConfig($f){
    $d = [];
    if (file_exists($f)) $d = json_decode(file_get_contents($f), true) ?? [];

    $account = $d['account'] ?? [];
    $options = $d['options'] ?? [];

    if (empty($account['email'])){
        clear(); bannerMain();
        echo W."Setup awal\n";
        echo W."-----------------------------------------------\n";
        echo W."Email (FaucetPay): ".Y; $e = trim(fgets(STDIN));
        $account = ['email' => $e];
    }

    if (empty($options)){
        $options = [
            'max_claims'   => 250,
            'wait_between' => 60,
        ];
    }

    $cfg = ['account' => $account, 'options' => $options];
    saveConfig($f, $cfg);
    return $cfg;
}

function editAccount(&$cfg, $f){
    clear(); bannerMain();
    echo W." EDIT AKUN \n\n";
    $a = $cfg['account'];
    echo W."Email baru (Enter = biarkan): ".Y; $e = trim(fgets(STDIN));
    if ($e !== '') $a['email'] = $e;
    $cfg['account'] = $a;
    saveConfig($f, $cfg);
    echo G."\n✓ Config disimpan.\n"; sleep(2);
}

function editOptions(&$cfg, $f){
    clear(); bannerMain();
    echo W." EDIT OPTIONS \n\n";
    $o = $cfg['options'];
    echo W."Max claims (skrg=".$o['max_claims']."): ".Y;
    $mc = trim(fgets(STDIN));
    if ($mc !== '' && is_numeric($mc)) $o['max_claims'] = (int)$mc;

    echo W."Wait between claims detik (skrg=".$o['wait_between']."): ".Y;
    $wb = trim(fgets(STDIN));
    if ($wb !== '' && is_numeric($wb)) $o['wait_between'] = (int)$wb;

    $cfg['options'] = $o;
    saveConfig($f, $cfg);
    echo G."\n✓ Options disimpan.\n"; sleep(2);
}

// ==================== MAIN ====================
$cfg = getConfig($configFile);

while (true){
    clear(); bannerMain();
    echo W."Email : ".CY.maskEmail($cfg['account']['email'] ?? '-')."\n";
    echo W."Max   : ".CY.($cfg['options']['max_claims'] ?? 250)."\n";
    echo W."Wait  : ".CY.($cfg['options']['wait_between'] ?? 60)."s\n";
    echo W."-----------------------------------------------\n";
    echo CY."[1]".W." Cek Status & Daily Limit\n";
    echo CY."[2]".G." Start Auto Claim\n";
    echo CY."[3]".W." Force Login Ulang\n";
    echo CY."[4]".G." Edit Akun\n";
    echo CY."[5]".G." Edit Options\n";
    echo CY."[0]".R." Keluar\n";
    echo W."-----------------------------------------------\n";
    echo W."Pilih: ".Y;
    $c = trim(fgets(STDIN));

    if ($c === '0'){ echo W."\nBye bro!\n"; exit; }
    elseif ($c === '4') editAccount($cfg, $configFile);
    elseif ($c === '5') editOptions($cfg, $configFile);
    elseif (in_array($c, ['1','2','3'])){
        $email = $cfg['account']['email'] ?? '';
        if (empty($email)){ echo R."\nEmail belum diisi!\n"; sleep(2); continue; }

        $h0 = ["user-agent:".DEF_UA, "accept-language:id-ID"];
        $dash = req(HOST.'/dashboard', 'GET', null, $h0);

        $need_login = (!$dash || !is_logged_in($dash)) || $c === '3';
        if ($need_login){
            @unlink($cookieFile);
            $dash = do_login($email);
            if (!$dash){ echo R."\nLogin gagal!\n"; sleep(3); continue; }
        } else {
            log_msg("Session valid ✓", 'success');
        }

        if ($dash && is_logged_in($dash)){
            $bal = get_balance($dash);
            $tot = get_total_claims($dash);
            $tdy = get_today_claims($dash);
            echo W."-----------------------------------------------\n";
            if ($bal !== null) echo W."Balance     : ".G.$bal.W." Coins\n";
            if ($tot !== null) echo W."Total claim : ".CY.$tot.W."\n";
            if ($tdy !== null) echo W."Today claim : ".CY.$tdy.W."\n";
            echo W."-----------------------------------------------\n";
        }

        if ($c === '1'){
            echo "\n".W."Tekan Enter..."; fgets(STDIN);
            continue;
        }

        if ($c === '2'){
            $max  = (int)($cfg['options']['max_claims'] ?? 250);
            $wait = (int)($cfg['options']['wait_between'] ?? 60);
            echo "\n".W."Mode: AUTO CLAIM | max={$max} | wait={$wait}s\n";
            sleep(1);
            claim_faucet($email, $max, $wait);
            echo "\n".W."Tekan Enter..."; fgets(STDIN);
        }
    }
}
