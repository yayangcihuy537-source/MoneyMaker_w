<?php
/**
 * ClaimCrypto.in Auto-Claimer v7
 * PHP CLI — by Kyriel
 *
 * EMAIL-ONLY login:
 *   - Input cuma email
 *   - Device token auto-generate
 *   - csrf & ci_session auto-capture dari login flow
 *   - cf_clearance opsional (kalau CF challenge, paste via arg)
 */

declare(strict_types=1);

// ==================== CONFIG ====================
$config = [
    'base_url'        => 'https://claimcrypto.in',
    'cookie_file'     => __DIR__ . '/cookiesClaimCrypto.txt',
    'config_file'     => __DIR__ . '/config.local.php',   // opsional: {'email':..., 'cf':...}
    'max_fails'       => 5,
    'backoff_rounds'  => 3,
    'backoff_seconds' => 120,
    'claim_delay_min' => 12,
    'claim_delay_max' => 15,
    'timeout'         => 30,
    'retry'           => 2,
    'user_agent'      => 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
];

// Load local override kalau ada
if (file_exists($config['config_file'])) {
    $local = require $config['config_file'];
    if (is_array($local)) $config = array_merge($config, $local);
}

// ==================== ANSI ====================
const C_RESET="\033[0m", C_BOLD="\033[1m", C_DIM="\033[2m";
const C_RED="\033[31m", C_GREEN="\033[32m", C_YELLOW="\033[33m";
const C_BLUE="\033[34m", C_MAGENTA="\033[35m", C_CYAN="\033[36m";
const C_BG_GREEN="\033[42;30m", C_BG_RED="\033[41;97m", C_BG_YELLOW="\033[43;30m";
const C_BG_MAGENTA="\033[45;97m";

function hr(int $w=60): void  { echo C_DIM.str_repeat('─',$w).C_RESET.PHP_EOL; }
function hr2(int $w=60): void { echo C_CYAN.str_repeat('═',$w).C_RESET.PHP_EOL; }
function tstamp(): string { return C_DIM.'['.date('H:i:s').']'.C_RESET; }
function ok(string $m): void    { echo tstamp().' '.C_GREEN.'✅ '.C_RESET.$m.PHP_EOL; }
function err(string $m): void   { echo tstamp().' '.C_RED.'❌ '.C_RESET.$m.PHP_EOL; }
function warn(string $m): void  { echo tstamp().' '.C_YELLOW.'⚠️  '.C_RESET.$m.PHP_EOL; }
function info(string $m): void  { echo tstamp().' '.C_CYAN.'ℹ️  '.C_RESET.$m.PHP_EOL; }
function net(string $m): void   { echo tstamp().' '.C_BLUE.'🌐 '.C_RESET.$m.PHP_EOL; }
function rocket(string $m): void{ echo tstamp().' '.C_MAGENTA.'🚀 '.C_RESET.$m.PHP_EOL; }
function refresh(string $m): void { echo tstamp().' '.C_YELLOW.'🔄 '.C_RESET.$m.PHP_EOL; }

function banner(): void {
    echo PHP_EOL;
    hr2();
    echo C_BOLD.C_GREEN.str_pad('  ⚡  CLAIMCRYPTO AUTO-CLAIMER  ⚡', 60, ' ', STR_PAD_BOTH).C_RESET.PHP_EOL;
    echo C_BOLD.C_GREEN.str_pad('  EMAIL-ONLY LOGIN  •  v7', 60, ' ', STR_PAD_BOTH).C_RESET.PHP_EOL;
    hr2();
    echo PHP_EOL;
}

// ==================== INPUT ====================

function argValue(string $name): ?string {
    global $argv;
    foreach ($argv as $i => $arg) {
        if ($arg === "--$name" && isset($argv[$i+1])) return $argv[$i+1];
        if (preg_match('/^--'.preg_quote($name,'/').'=(.+)$/s', $arg, $m)) return $m[1];
    }
    return null;
}

function prompt(string $label): string {
    echo C_BOLD.C_YELLOW.$label.' > '.C_RESET;
    $line = fgets(STDIN);
    if ($line === false) { fwrite(STDERR, "Input gagal.\n"); exit(1); }
    return trim($line);
}

// ==================== COOKIE JAR ====================

function writeCookieJar(string $path, array $cookies, string $domain='claimcrypto.in'): void {
    $lines = ["# Netscape HTTP Cookie File", "# auto-generated", ""];
    foreach ($cookies as $name=>$value) {
        $lines[] = implode("\t", [$domain,'TRUE','/','TRUE',0,$name,$value]);
    }
    file_put_contents($path, implode(PHP_EOL,$lines).PHP_EOL);
    @chmod($path, 0600);
}

function readJar(): array {
    global $config;
    $out = [];
    if (!file_exists($config['cookie_file'])) return $out;
    foreach (file($config['cookie_file']) as $line) {
        if ($line === '' || $line[0] === '#') continue;
        $p = preg_split('/\t+/', trim($line));
        if (count($p) >= 7) $out[$p[5]] = $p[6];
    }
    return $out;
}

// ==================== HUMAN DELAY ====================

function humanDelay(int $minMs=800, int $maxMs=2200): void {
    usleep(random_int($minMs,$maxMs)*1000);
}

// ==================== DEVICE TOKEN ====================

function generateDeviceToken(): string {
    $chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    $out = '';
    for ($i=0; $i<20; $i++) $out .= $chars[random_int(0,strlen($chars)-1)];
    return 'dev_'.$out;
}

// ==================== CF EMAIL DECODE ====================

function decodeCfEmail(string $hex): string {
    $raw = @hex2bin($hex); if ($raw === false || strlen($raw) < 2) return '';
    $key = ord($raw[0]); $out = '';
    for ($i=1; $i<strlen($raw); $i++) $out .= chr(ord($raw[$i]) ^ $key);
    return $out;
}

function scrapeEmail(string $html): ?string {
    if (preg_match('/data-cfemail=["\']([0-9a-f]+)["\']/i', $html, $m)) {
        $e = decodeCfEmail($m[1]);
        if ($e && filter_var($e, FILTER_VALIDATE_EMAIL)) return $e;
    }
    if (preg_match('/[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}/i', $html, $m)) return $m[0];
    return null;
}

// ==================== BALANCE SCRAPE ====================

function scrapeBalance(string $html): ?float {
    foreach ([
        '/class=["\']balance-amount["\'][^>]*>\s*([\d,\.]+)/i',
        '/TOTAL\s+BALANCE.*?([\d,\.]+)\s*<span[^>]*>Coins/i',
        '/([\d,\.]+)\s*<span[^>]*class=["\']balance-unit["\'][^>]*>Coins/i',
    ] as $pat) {
        if (preg_match($pat, $html, $m)) return (float) str_replace(',','',$m[1]);
    }
    return null;
}

// ==================== HTTP ====================

function http(string $method, string $url, array $opts=[]): array {
    global $config;
    $attempts = 0; $max = $opts['retry'] ?? $config['retry'];
    start:
    $attempts++;
    $ch = curl_init($url);
    $headers = $opts['headers'] ?? [];
    $headers[] = 'Accept-Language: id-ID,id;q=0.9,en;q=0.8';
    $headers[] = 'sec-ch-ua: "Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"';
    $headers[] = 'sec-ch-ua-mobile: ?1';
    $headers[] = 'sec-ch-ua-platform: "Android"';
    $headers[] = 'Upgrade-Insecure-Requests: 1';
    if (!empty($opts['no_cache'])) {
        $headers[] = 'Cache-Control: no-cache, no-store, max-age=0';
        $headers[] = 'Pragma: no-cache';
    }

    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_MAXREDIRS      => 5,
        CURLOPT_CONNECTTIMEOUT => 10,
        CURLOPT_TIMEOUT        => $config['timeout'],
        CURLOPT_USERAGENT      => $config['user_agent'],
        CURLOPT_COOKIEJAR      => $config['cookie_file'],
        CURLOPT_COOKIEFILE     => $config['cookie_file'],
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_SSL_VERIFYHOST => 2,
        CURLOPT_HTTPHEADER     => $headers,
        CURLOPT_ENCODING       => '',
    ]);

    if (strtoupper($method) === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, is_array($opts['body'] ?? null)
            ? http_build_query($opts['body']) : ($opts['body'] ?? ''));
    }

    $body = curl_exec($ch); $errno = curl_errno($ch); $err = curl_error($ch);
    $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);

    if ($errno !== 0) {
        if ($attempts < $max) { usleep(400000); goto start; }
        throw new RuntimeException("cURL #$errno: $err");
    }
    if ($status >= 500 && $attempts < $max) { usleep(600000); goto start; }
    return ['status'=>$status, 'body'=>$body];
}

// ==================== PARSER ====================

function parseInput(string $html, string $name): ?string {
    $n = preg_quote($name,'/');
    if (preg_match('/<input[^>]*name=["\']'.$n.'["\'][^>]*value=["\']([^"\']*)["\']/i', $html, $m))
        return html_entity_decode($m[1], ENT_QUOTES, 'UTF-8');
    if (preg_match('/<input[^>]*value=["\']([^"\']*)["\'][^>]*name=["\']'.$n.'["\']/i', $html, $m))
        return html_entity_decode($m[1], ENT_QUOTES, 'UTF-8');
    return null;
}

function fakeFpHash(): string {
    return hash('sha256', 'fp-'.php_uname().microtime(true).random_int(1000,9999));
}

function buildSmartToken(int $moves=0): string {
    return base64_encode(json_encode([
        'ts'=>(int)round(microtime(true)*1000),
        'cpu'=>8, 'mem'=>8, 'w'=>384, 'h'=>832, 'touch'=>5, 'moves'=>$moves,
    ], JSON_UNESCAPED_SLASHES));
}

// ==================== LOGIN (EMAIL-ONLY) ====================

/**
 * Fresh login: buang jar lama, GET / buat dapet csrf_cookie_name,
 * POST /auth/login, capture ci_session.
 */
function doLogin(array $config, string $email, string $device, bool $quiet=false): bool {
    if (!$quiet) net('GET / (fresh session)');
    else        refresh('GET / (rejoin)');

    // Reset jar biar bener-bener fresh
    if (file_exists($config['cookie_file'])) @unlink($config['cookie_file']);

    $ts = time();
    humanDelay();
    http('GET', $config['base_url'].'/?_='.$ts, [
        'no_cache' => true,
        'headers' => ['Referer: '.$config['base_url'].'/'],
    ]);

    $jar = readJar();
    $csrf = $jar['csrf_cookie_name'] ?? null;
    if (!$csrf) {
        err('CSRF cookie gak dapet dari GET /');
        return false;
    }
    if (!$quiet) info('CSRF : '.C_DIM.substr($csrf, 0, 16).'...'.C_RESET);

    humanDelay(1500, 3000);
    if (!$quiet) rocket('POST /auth/login');
    else        refresh('POST /auth/login (rejoin)');

    $r = http('POST', $config['base_url'].'/auth/login', [
        'headers' => [
            'Origin: '.$config['base_url'],
            'Referer: '.$config['base_url'].'/?_='.$ts,
            'Content-Type: application/x-www-form-urlencoded',
        ],
        'body' => [
            'wallet'          => $email,
            'csrf_token_name' => $csrf,
            'device_token'    => $device,
        ],
        'no_cache' => true,
    ]);

    $html = $r['body'];

    if (stripos($html, 'Just a moment') !== false) {
        err('Cloudflare challenge. Butuh cf_clearance.');
        return false;
    }

    if (stripos($html, 'Login Success') !== false || stripos($html, 'Welcome back') !== false) {
        if (!$quiet) ok('Login sukses');
        else        refresh('Rejoin sukses');
        return true;
    }

    if (stripos($html, 'Invalid') !== false && stripos($html, 'dashboard') === false) {
        err('Login ditolak (Invalid)');
        return false;
    }

    // Fallback: cek cookie ci_session muncul, berarti login berhasil walau HTML ambigu
    $jar2 = readJar();
    if (!empty($jar2['ci_session'])) {
        if (!$quiet) ok('Login sukses (via cookie)');
        return true;
    }

    if (stripos($html, 'dashboard') !== false) {
        if (!$quiet) warn('Login ambiguous, assume OK');
        return true;
    }

    err('Login gagal status '.$r['status']);
    return false;
}

function fetchDashboard(array $config, bool $quiet=false): ?array {
    if (!$quiet) net('GET /dashboard');
    $r = http('GET', $config['base_url'].'/dashboard?_='.time(), [
        'headers' => ['Referer: '.$config['base_url'].'/'],
        'no_cache' => true,
    ]);
    $html = $r['body'];

    if (stripos($html, 'Just a moment') !== false || stripos($html, 'cf-chl') !== false) {
        err('CF challenge di /dashboard'); return null;
    }
    if (stripos($html, 'Welcome back') === false && stripos($html, 'Dashboard') === false) {
        err('Session invalid di /dashboard'); return null;
    }
    $email = scrapeEmail($html);
    $balance = scrapeBalance($html);
    if (!$quiet) ok('Session valid');
    if ($email && !$quiet) info('Email    : '.$email);
    if ($balance !== null && !$quiet) info('Balance  : '.C_BOLD.C_GREEN.$balance.' Coins'.C_RESET);
    return ['email'=>$email, 'balance'=>$balance];
}

function fetchClaimForm(array $config, bool $quiet=false): ?array {
    humanDelay();
    if (!$quiet) net('GET /earn');
    $url = $config['base_url'].'/earn?_='.time().random_int(100,999);
    $r = http('GET', $url, [
        'headers' => ['Referer: '.$config['base_url'].'/dashboard'],
        'no_cache' => true,
    ]);
    $html = $r['body'];

    foreach (['Daily Limit Reached','completed all claims','check back tomorrow'] as $h) {
        if (stripos($html, $h) !== false) return ['_daily_limit' => true];
    }

    if (preg_match('/let wait = (\d+)/', $html, $m)) {
        $wait = (int) $m[1];
        if ($wait > 0) {
            warn('Cooldown: '.C_BOLD.$wait.'s'.C_RESET);
            for ($i=$wait+2; $i>0; $i--) {
                echo "\r  ".C_DIM."⏳ resume dalam {$i}s...".C_RESET."  ";
                sleep(1);
            }
            echo "\r".str_repeat(' ',40)."\r";
            return fetchClaimForm($config, $quiet);
        }
    }

    if (stripos($html, 'id="fauform"') === false) {
        if (stripos($html, 'Please login') !== false || stripos($html, '/auth/login') !== false) {
            err('Form butuh login');
            return ['_need_login' => true];
        }
        err('Form faucet gak ada');
        return null;
    }

    $csrf   = parseInput($html, 'csrf_token_name');
    $token  = parseInput($html, 'token');
    $ticket = parseInput($html, 'earn_ticket');
    $wallet = parseInput($html, 'wallet');
    $balance = scrapeBalance($html);

    if (!$csrf || !$token || !$ticket) {
        err('Parse gagal'); return null;
    }

    if (!$quiet) {
        ok('Form OK');
        info('Token    : '.C_DIM.$token.C_RESET);
        info('Ticket   : '.C_DIM.substr($ticket,0,16).'...'.C_RESET);
        if ($balance !== null) info('Balance  : '.C_BOLD.C_GREEN.$balance.' Coins'.C_RESET);
    }
    return [
        'csrf_token_name'=>$csrf,
        'token'=>$token,
        'earn_ticket'=>$ticket,
        'wallet'=>$wallet,
        'balance'=>$balance,
    ];
}

function claim(array $config, array $form, string $wallet): array {
    humanDelay(1500, 4000);
    $moves = random_int(3, 25);
    rocket('POST /faucet/earn');
    $r = http('POST', $config['base_url'].'/faucet/earn', [
        'headers' => [
            'Origin: '.$config['base_url'],
            'Referer: '.$config['base_url'].'/earn',
            'Content-Type: application/x-www-form-urlencoded',
        ],
        'body' => [
            'csrf_token_name' => $form['csrf_token_name'],
            'token'           => $form['token'],
            'earn_ticket'     => $form['earn_ticket'],
            'fp_hash'         => fakeFpHash(),
            'confirm_wallet'  => '',
            'wallet'          => $form['wallet'] ?: $wallet,
            'smart_token'     => buildSmartToken($moves),
            'captcha'         => 'smartcaptcha',
        ],
        'no_cache' => true,
    ]);
    $html = $r['body'];
    $newBal = scrapeBalance($html);

    if (preg_match('/Success!\s*([\d,\.]+)\s*Coins has been added/i', $html, $m)) {
        return ['ok'=>true, 'reward'=>$m[1], 'balance'=>$newBal, 'hint'=>null, 'stop'=>false];
    }

    foreach (['Daily Limit Reached','completed all claims','check back tomorrow','daily limit'] as $h) {
        if (stripos($html, $h) !== false) {
            return ['ok'=>false, 'reward'=>null, 'balance'=>$newBal, 'hint'=>'daily_limit', 'stop'=>true];
        }
    }

    if (stripos($html, '/auth/login') !== false && stripos($html, 'name="wallet"') !== false) {
        return ['ok'=>false, 'reward'=>null, 'balance'=>$newBal, 'hint'=>'session_dead', 'stop'=>false];
    }

    foreach (['Please Wait','Invalid','Error','expired','captcha','too fast','cooldown'] as $hint) {
        if (stripos($html, $hint) !== false) {
            $isCd = stripos($hint,'wait')!==false || stripos($hint,'cooldown')!==false;
            return ['ok'=>$isCd, 'reward'=>null, 'balance'=>$newBal, 'hint'=>$hint, 'stop'=>false];
        }
    }

    return ['ok'=>false, 'reward'=>null, 'balance'=>$newBal, 'hint'=>'unknown', 'stop'=>false];
}

function fullRefresh(array $config, string $email, string $device): bool {
    refresh('FULL REFRESH — rejoin session');
    hr();

    if (!doLogin($config, $email, $device, true)) {
        err('Re-login gagal saat refresh'); return false;
    }
    humanDelay(800, 1500);

    $d = fetchDashboard($config, true);
    if (!$d) { err('Dashboard gagal saat refresh'); return false; }
    ok('Refresh selesai — session fresh');
    hr();
    return true;
}

// ==================== MAIN ====================

function main(): void {
    global $config;
    banner();

    // ---- Input ----
    hr();

    // Email
    $email = argValue('email') ?: (getenv('CC_EMAIL') ?: ($config['email'] ?? null));
    if (!$email) {
        $email = prompt('📧 Email / wallet address');
    }
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        err('Email gak valid: '.$email); exit(1);
    }

    // cf_clearance opsional
    $cf = argValue('cf') ?: (getenv('CC_CF') ?: ($config['cf'] ?? null));
    if (!$cf) {
        echo C_DIM.'🛡️  cf_clearance (opsional, enter buat skip — cuma perlu kalau kena CF challenge)'.C_RESET.PHP_EOL;
        $cf = prompt('cf_clearance');
    }

    info('Panjang email    : '.strlen($email));
    if ($cf) info('cf_clearance     : '.C_DIM.substr($cf, 0, 20).'...'.C_RESET);

    // Preload jar dengan cf_clearance kalau ada
    if ($cf) {
        writeCookieJar($config['cookie_file'], ['cf_clearance' => $cf]);
        info('cf_clearance di-preload ke jar');
    }

    hr();

    // ---- Login ----
    $device = generateDeviceToken();
    info('Email    : '.C_BOLD.$email.C_RESET);
    info('Device   : '.C_BOLD.$device.C_RESET);
    info('Delay    : '.C_BOLD.$config['claim_delay_min'].'-'.$config['claim_delay_max'].'s'.C_RESET);
    info('Mode     : '.C_BOLD.'Email-only login'.C_RESET);
    hr();
    PHP_EOL;

    $loginFail = 0;
    while (!doLogin($config, $email, $device)) {
        $loginFail++;
        if ($loginFail >= 3) {
            err('Login gagal 3x. Stop.'); exit(1);
        }
        warn("Retry login ($loginFail/3)...");
        sleep(3);
    }

    $dash = fetchDashboard($config);
    if (!$dash) {
        err('Verifikasi awal gagal. Kemungkinan butuh cf_clearance.');
        exit(1);
    }
    $scrapedEmail = $dash['email'] ?? $email;
    PHP_EOL;

    // ---- Claim loop ----
    $fail = 0;
    $backoffRound = 0;
    $total = 0;
    $totalCoins = 0.0;
    $sessionCheck = 0;
    $needRefresh = false;

    while (true) {
        hr2();
        echo C_BG_GREEN.'  AUTO-CLAIMER ACTIVE  '.C_RESET.'  '.
             C_DIM.'sukses: '.C_RESET.C_BOLD.$total.C_RESET.
             C_DIM.'  |  gagal: '.C_RESET.C_BOLD.$fail.'/'.$config['max_fails'].C_RESET.
             C_DIM.'  |  backoff: '.C_RESET.C_BOLD.$backoffRound.'/'.$config['backoff_rounds'].C_RESET.
             PHP_EOL;
        hr2();

        if ($needRefresh) {
            if (!fullRefresh($config, $email, $device)) {
                err('Full refresh gagal. Stop.'); break;
            }
            $needRefresh = false;
            $fail = 0;
        }

        $form = fetchClaimForm($config);

        // ═══ DAILY LIMIT ═══
        if (is_array($form) && !empty($form['_daily_limit'])) {
            echo PHP_EOL;
            hr2();
            echo C_BG_YELLOW.'  🎯 DAILY LIMIT REACHED '.C_RESET.PHP_EOL;
            hr2();
            warn('Lu udah nge-klaim semua jatah hari ini, Bos.');
            info('Server bilang: '.C_BOLD.'"check back tomorrow"'.C_RESET);
            info('Total sukses sesi ini: '.C_BOLD.C_GREEN.$total.' klaim'.C_RESET.
                 ' ('.$totalCoins.' Coins)'.C_RESET);
            echo PHP_EOL;
            info('Saran: jalanin lagi besok pagi (reset server ~07:00 WIB).');
            hr2();
            break;
        }

        if (is_array($form) && !empty($form['_need_login'])) {
            warn('Session expired — rejoin...');
            if (!fullRefresh($config, $email, $device)) {
                err('Rejoin gagal. Stop.'); break;
            }
            continue;
        }

        if (!$form) {
            $fail++;
            err("Gagal ambil form ($fail/{$config['max_fails']})");
            if ($fail >= $config['max_fails']) {
                $backoffRound++;
                if ($backoffRound > $config['backoff_rounds']) {
                    err('Backoff habis. Stop.'); break;
                }
                warn('Backoff round '.$backoffRound.' — tidur '.$config['backoff_seconds'].'s');
                hr();
                for ($i=$config['backoff_seconds']; $i>0; $i--) {
                    echo "\r  ".C_DIM."😴 backoff: {$i}s...".C_RESET."  ";
                    sleep(1);
                }
                echo "\r".str_repeat(' ',60)."\r";
                $fail = 0;
                $needRefresh = true;
                hr();
                continue;
            }
            sleep(3);
            continue;
        }

        $res = claim($config, $form, $scrapedEmail);

        // ═══ DAILY LIMIT via claim ═══
        if (!empty($res['stop']) && $res['hint'] === 'daily_limit') {
            echo PHP_EOL;
            hr2();
            echo C_BG_YELLOW.'  🎯 DAILY LIMIT REACHED '.C_RESET.PHP_EOL;
            hr2();
            warn('Lu udah nge-klaim semua jatah hari ini, Bos.');
            info('Server bilang: '.C_BOLD.'"check back tomorrow"'.C_RESET);
            if ($res['balance'] !== null) {
                info('Balance akhir: '.C_BOLD.C_GREEN.$res['balance'].' Coins'.C_RESET);
            }
            info('Total sukses sesi ini: '.C_BOLD.C_GREEN.$total.' klaim'.C_RESET.
                 ' ('.$totalCoins.' Coins)'.C_RESET);
            echo PHP_EOL;
            echo C_BG_MAGENTA.' 📢 WULAN SUKA PRABOWO '.C_RESET.'  — share di grup '.C_BOLD.'ScriptyXSouu'.C_RESET.' 😂'.PHP_EOL;
            hr2();
            break;
        }

        if ($res['ok']) {
            $total++;
            if ($res['reward']) $totalCoins += (float) $res['reward'];
            echo tstamp().' '.C_BG_GREEN.' 💰 CLAIM SUKSES '.C_RESET.
                 ' +'.C_BOLD.C_GREEN.($res['reward'] ?? '?').' Coins'.C_RESET.PHP_EOL;
            info('Total sukses : '.C_BOLD.$total.C_RESET.' klaim');
            if ($res['balance'] !== null)
                info('Balance baru : '.C_BOLD.C_GREEN.$res['balance'].' Coins'.C_RESET);
            if ($totalCoins > 0)
                info('Akumulasi    : '.C_BOLD.C_GREEN.$totalCoins.' Coins'.C_RESET.' (session ini)');

            $fail = 0;
            $backoffRound = 0;
            $sessionCheck++;

            $delay = random_int($config['claim_delay_min'], $config['claim_delay_max']);
            echo tstamp().' '.C_DIM."💤 Delay human: {$delay}s...".C_RESET.PHP_EOL;
            sleep($delay);

            if ($sessionCheck % 4 === 0) {
                hr();
                refresh('Preventif refresh setiap 4 klaim sukses');
                if (!fullRefresh($config, $email, $device)) {
                    err('Refresh preventif gagal');
                    $needRefresh = true;
                }
            }
        } else {
            $fail++;
            $hint = $res['hint'] ?? 'unknown';

            if ($hint === 'session_dead') {
                warn('Session mati — rejoin...');
                if (!fullRefresh($config, $email, $device)) {
                    err('Rejoin gagal. Stop.'); break;
                }
                $fail = 0;
                continue;
            }

            err("Claim gagal (hint: $hint) [$fail/{$config['max_fails']}]");

            hr();
            refresh('Fail terdeteksi → refresh + rejoin sebelum retry');
            if (!fullRefresh($config, $email, $device)) {
                err('Refresh setelah fail gagal. Coba backoff...');
                $needRefresh = true;
            } else {
                $fail = 0;
            }

            if ($fail >= $config['max_fails']) {
                $backoffRound++;
                if ($backoffRound > $config['backoff_rounds']) {
                    warn('Backoff habis — kemungkinan cap harian');
                    break;
                }
                warn('Backoff round '.$backoffRound.' — tidur '.$config['backoff_seconds'].'s');
                hr();
                for ($i=$config['backoff_seconds']; $i>0; $i--) {
                    echo "\r  ".C_DIM."😴 backoff: {$i}s...".C_RESET."  ";
                    sleep(1);
                }
                echo "\r".str_repeat(' ',60)."\r";
                $fail = 0;
                hr();
            }
        }
    }

    echo PHP_EOL;
    hr2();
    echo C_BOLD.C_GREEN.str_pad(' 🏁 SELESAI ', 60, ' ', STR_PAD_BOTH).C_RESET.PHP_EOL;
    hr2();
    info('Total klaim sukses : '.C_BOLD.$total.C_RESET);
    info('Total Coins        : '.C_BOLD.C_GREEN.$totalCoins.C_RESET);
    hr2();
}

try { main(); }
catch (Throwable $e) { err('FATAL: '.$e->getMessage()); exit(1); }
