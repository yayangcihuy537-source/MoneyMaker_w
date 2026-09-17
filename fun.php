<?php
/**
 * FreeLTC.fun Faucet Auto-Claim + Captcha OCR Solver
 * HACKER THEME v3.3 — FIXED ENDPOINT
 *
 * Fix dari v3.2:
 *   - Endpoint diperbaiki: /claim/earn → /faucet/earn
 *   - Cookie seeding include device_token
 *   - Handle redirect 303/302 dari /auth/login
 *   - Session detection diperbaiki
 */

declare(strict_types=1);
error_reporting(E_ALL & ~E_DEPRECATED);
ini_set('display_errors', '1');
date_default_timezone_set('Asia/Jakarta');

/* ======================= PATH & CONSTANTS ======================= */

const HOST         = 'https://freeltc.fun';
const SESSION_FILE = __DIR__ . '/session.txt';
const SCRIPT_BY    = 'MoneyMaker_w';
const BRAND        = 'FREELTC HACKER';
const COIN_UNIT    = 'Coins';

const USER_AGENT   = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36';

const CLAIM_DELAY    = 12;
const CAPTCHA_POLL   = 5;
const CAPTCHA_TIMEOUT= 120;
const SLEEP_BETWEEN  = 12;
const MAX_CLAIMS     = 250;

/* ======================= COLORS ======================= */

class C {
    const RESET = "\033[0m"; const BOLD = "\033[1m"; const DIM = "\033[2m";
    const BR_RED = "\033[91m"; const BR_GREEN = "\033[92m"; const BR_YELLOW = "\033[93m";
    const BR_MAGENTA = "\033[95m"; const BR_CYAN = "\033[96m"; const BR_WHITE = "\033[97m";

    const HACK_G = "\033[38;5;46m";
    const HACK_D = "\033[38;5;22m";
    const HACK_Y = "\033[38;5;226m";
    const HACK_R = "\033[38;5;196m";
    const HACK_C = "\033[38;5;51m";
    const HACK_P = "\033[38;5;207m";
    const HACK_M = "\033[38;5;201m";
    const HACK_W = "\033[38;5;231m";
    const HACK_O = "\033[38;5;208m";
}

/* ======================= STATE ======================= */

class State {
    public static array  $cfg = [
        'api_key'        => '',
        'wallet'         => '',
        'manual_cookies' => '',
        'captcha_method' => 'image-to-text',
    ];

    public static string $wallet        = '';
    public static string $status        = 'IDLE';
    public static string $balance       = '0';
    public static int    $claims        = 0;
    public static int    $success       = 0;
    public static int    $failed        = 0;
    public static float  $coins_earned  = 0.0;
    public static int    $captchaSolved = 0;
    public static string $lastReward    = '-';
    public static array  $history       = [];
    public static int    $startTime     = 0;
    public static string $activity      = '';
    public static int    $maxClaims     = 250;
    public static bool   $stopFlag      = false;
    public static string $stopReason    = '';

    public static function addHistory(string $msg, string $tag = 'info'): void {
        $icons = [
            'info'    => C::HACK_C  . 'ℹ' . C::RESET,
            'success' => C::HACK_G  . '✓' . C::RESET,
            'error'   => C::HACK_R  . '✗' . C::RESET,
            'warn'    => C::HACK_Y  . '⚠' . C::RESET,
            'money'   => C::HACK_Y  . '💰' . C::RESET,
            'rocket'  => C::HACK_M  . '🚀' . C::RESET,
            'sleep'   => C::HACK_C  . '⏳' . C::RESET,
            'captcha' => C::HACK_C  . '🤖' . C::RESET,
            'cookie'  => C::HACK_M  . '🍪' . C::RESET,
            'hack'    => C::HACK_G  . '💻' . C::RESET,
            'target'  => C::HACK_R  . '🎯' . C::RESET,
            'stop'    => C::HACK_R  . '⛔' . C::RESET,
        ];
        $icon = $icons[$tag] ?? C::HACK_W . '•' . C::RESET;
        self::$history[] = $icon . ' ' . $msg;
        if (count(self::$history) > 10) array_shift(self::$history);
    }
}

/* ======================= HACKER ANIMATIONS ======================= */

class Hack {
    public static function clear(): void {
        if (stripos(PHP_OS_FAMILY, 'Windows') !== false) {
            system('cls');
        } else {
            echo "\033[2J\033[3J\033[H";
        }
    }

    public static function matrixRain(int $lines = 3, int $width = 60, float $delay = 0.02): void {
        $chars = '!@#$%^&*()_+-={}[]|;:,.<>?/\\0123456789ABCDEF';
        for ($i = 0; $i < $lines; $i++) {
            $line = '';
            for ($j = 0; $j < $width; $j++) {
                $c = $chars[random_int(0, strlen($chars) - 1)];
                $line .= C::HACK_D . $c;
                if ($j > $width - 15) $line .= C::HACK_G;
            }
            echo $line . C::RESET . PHP_EOL;
            usleep((int)($delay * 1000000));
        }
    }

    public static function typing(string $text, float $delay = 0.02, string $color = C::HACK_G): void {
        foreach (str_split($text) as $ch) {
            echo $color . $ch . C::RESET;
            usleep((int)($delay * 1000000));
        }
        echo PHP_EOL;
    }

    public static function bootSequence(): void {
        self::clear();
        echo PHP_EOL;
        self::typing('  > Initializing kernel...', 0.01, C::HACK_G);
        usleep(200000);
        self::typing('  > Loading encryption modules...', 0.01, C::HACK_G);
        usleep(200000);
        self::typing('  > Bypassing TLS handshake...', 0.01, C::HACK_Y);
        usleep(300000);
        self::typing('  > Injecting payload...', 0.01, C::HACK_G);
        usleep(250000);
        echo PHP_EOL;
        self::matrixRain(3, 60, 0.015);
        echo PHP_EOL;
        self::typing('  [SYSTEM READY]', 0.03, C::HACK_C);
        usleep(300000);
        echo PHP_EOL;
    }
}

/* ======================= UI ======================= */

class UI {
    public static function line(int $w = 62, string $c = C::HACK_G): void {
        echo $c . str_repeat('═', $w) . C::RESET . PHP_EOL;
    }

    public static function center(string $t, int $w, string $c = C::RESET): void {
        $v = self::visibleLen($t);
        $pad = max(0, intdiv($w - $v, 2));
        echo str_repeat(' ', $pad) . $c . $t . C::RESET . PHP_EOL;
    }

    public static function visibleLen(string $s): int {
        $s = preg_replace('/\033\[[0-9;]*m/', '', $s);
        $s = preg_replace('/[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]/u', 'XX', $s);
        return mb_strlen($s);
    }

    public static function kv(string $k, string $v, string $c = C::HACK_W): void {
        printf("  %s%-13s%s %s▸%s %s%s%s\n",
            C::HACK_D, $k, C::RESET,
            C::HACK_G, C::RESET,
            $c, $v, C::RESET
        );
    }

    public static function progressBar(int $cur, int $total, int $w = 16): string {
        $total = max(1, $total);
        $cur   = max(0, min($cur, $total));
        $filled = (int)round(($total - $cur) / $total * $w);
        $filled = max(0, min($filled, $w));
        $empty  = $w - $filled;
        return C::HACK_G . str_repeat('█', $filled)
             . C::HACK_D . str_repeat('░', $empty) . C::RESET;
    }

    public static function render(int $remaining = 0, int $totalForBar = 0): void {
        Hack::clear();
        $w = 62;

        self::line($w, C::HACK_G);
        self::center('█▓▒░ 💻 ' . BRAND . ' ░▒▓█', $w, C::BOLD . C::HACK_G);
        self::center('[ TARGET: freeltc.fun ]', $w, C::HACK_D . C::HACK_G);
        self::line($w, C::HACK_G);

        self::kv('ScriptMaker', SCRIPT_BY, C::HACK_M);
        self::kv('Status', '🟢 ' . C::HACK_G . C::BOLD . State::$status . C::RESET);
        self::line($w, C::HACK_D);

        self::kv('WALLET', State::$wallet !== '' ? State::$wallet : '(unknown)', C::HACK_C);
        self::kv('BALANCE', State::$balance . ' ' . COIN_UNIT, C::HACK_Y);
        self::line($w, C::HACK_D);

        $rate = State::$claims > 0 ? (State::$success / State::$claims * 100) : 0;
        $rate_c = $rate >= 90 ? C::HACK_G : ($rate >= 70 ? C::HACK_Y : C::HACK_R);
        $max = State::$maxClaims;

        self::kv('PROGRESS', sprintf('%d / %d claims', State::$claims, $max), C::HACK_W);
        self::kv('SUCCESS', sprintf('%d ✓', State::$success), C::HACK_G);
        self::kv('FAILED', sprintf('%d ✗', State::$failed), C::HACK_R);
        self::kv('RATE', sprintf('%.1f%%', $rate), $rate_c);
        self::kv('COINS EARNED', sprintf('%.2f %s', State::$coins_earned, COIN_UNIT), C::HACK_Y);
        self::kv('CAPTCHA OK', (string)State::$captchaSolved, C::HACK_C);
        self::kv('LAST REWARD', State::$lastReward, C::HACK_G);
        if (State::$activity !== '') {
            self::kv('ACTIVITY', State::$activity, C::HACK_O);
        }

        $bar = self::progressBar($max - State::$claims, $max, 30);
        echo '  ' . C::HACK_D . 'CLAIM ' . C::RESET . $bar
            . ' ' . C::HACK_W . State::$claims . '/' . $max . C::RESET . PHP_EOL;

        self::line($w, C::HACK_D);

        foreach (State::$history as $line) {
            echo '  ' . $line . PHP_EOL;
        }
        self::line($w, C::HACK_D);

        if (State::$stopFlag) {
            echo '  ' . C::HACK_R . C::BOLD . '⛔ STOPPED: ' . State::$stopReason . C::RESET . PHP_EOL;
        } elseif ($remaining > 0) {
            $tb = $totalForBar > 0 ? $totalForBar : $remaining;
            $bar  = self::progressBar($remaining, $tb);
            $time = sprintf('%02d:%02d', intdiv($remaining, 60), $remaining % 60);
            echo '  ' . C::HACK_Y . '⏳ NEXT CLAIM ' . C::RESET
               . $bar . ' ' . C::HACK_W . C::BOLD . $time . C::RESET . PHP_EOL;
        } else {
            echo '  ' . C::HACK_G . '⚡ Ready...' . C::RESET . PHP_EOL;
        }
        self::line($w, C::HACK_G);
    }
}

/* ======================= LOG ======================= */

function logmsg(string $msg, string $tag = 'info'): void {
    State::addHistory($msg, $tag);
}

/* ======================= INPUT HELPERS ======================= */

function prompt(string $label, string $default = ''): string {
    $suffix = $default !== '' ? " [" . C::HACK_D . $default . C::RESET . "]" : '';
    fwrite(STDOUT, C::HACK_G . $label . C::RESET . $suffix . C::HACK_G . ' ▸ ' . C::RESET);
    $line = fgets(STDIN);
    if ($line === false) return $default;
    $line = trim($line);
    return $line === '' ? $default : $line;
}

function promptConfirm(string $label, bool $default = true): bool {
    $hint = $default ? '[Y/n]' : '[y/N]';
    fwrite(STDOUT, '  ' . C::HACK_Y . $label . ' ' . $hint . C::HACK_G . ' ▸ ' . C::RESET);
    $line = trim((string)fgets(STDIN));
    if ($line === '') return $default;
    return in_array(strtolower($line), ['y', 'yes', 'ya', '1'], true);
}

/* ======================= SETUP WIZARD ======================= */

function runSetup(): void {
    Hack::clear();
    echo PHP_EOL;
    echo C::HACK_G . '  ╔════════════════════════════════════════════════════════╗' . PHP_EOL;
    echo '  ║' . C::HACK_Y . C::BOLD . '          💻 ' . BRAND . ' — SETUP WIZARD          ' . C::HACK_G . '║' . PHP_EOL;
    echo '  ╚════════════════════════════════════════════════════════╝' . C::RESET . PHP_EOL;
    echo '  ' . C::HACK_D . '  (No log file · session.txt cuma buat cookies+device)' . C::RESET . PHP_EOL . PHP_EOL;

    Hack::typing('  > Initializing setup protocol...', 0.01, C::HACK_D);
    echo PHP_EOL;

    echo C::HACK_Y . '  [1/3] Captcha API Key' . C::RESET . PHP_EOL;
    echo C::HACK_D . '        > api.waryono.my.id' . C::RESET . PHP_EOL;
    do {
        $key = prompt('  API Key');
        if ($key === '') echo '  ' . C::HACK_R . '⚠ Gak boleh kosong.' . C::RESET . PHP_EOL;
    } while ($key === '');
    State::$cfg['api_key'] = $key;
    echo PHP_EOL;

    echo C::HACK_Y . '  [2/3] Wallet (FaucetPay email)' . C::RESET . PHP_EOL;
    echo C::HACK_D . '        > Contoh: wulansukaprabowo@kiwkiw.com' . C::RESET . PHP_EOL;
    do {
        $wallet = prompt('  Wallet');
        if ($wallet === '') echo '  ' . C::HACK_R . '⚠ Wajib diisi.' . C::RESET . PHP_EOL;
    } while ($wallet === '');
    State::$cfg['wallet'] = $wallet;
    echo PHP_EOL;

    echo C::HACK_Y . '  [3/3] Cookies (cf_clearance + ci_session)' . C::RESET . PHP_EOL;
    echo C::HACK_D . '        > Format: cf_clearance=xxx; ci_session=yyy; csrf_cookie_name=zzz' . C::RESET . PHP_EOL;
    do {
        $cookies = prompt('  Cookies');
        if ($cookies === '') echo '  ' . C::HACK_R . '⚠ Wajib diisi.' . C::RESET . PHP_EOL;
    } while ($cookies === '');
    State::$cfg['manual_cookies'] = $cookies;
    echo PHP_EOL;

    echo C::HACK_G . '  ─── Ringkasan ───' . C::RESET . PHP_EOL;
    echo '  ' . C::HACK_D . 'API Key         ' . C::RESET . '▸ ' . C::HACK_W . substr(State::$cfg['api_key'], 0, 12) . '...' . C::RESET . PHP_EOL;
    echo '  ' . C::HACK_D . 'Wallet          ' . C::RESET . '▸ ' . C::HACK_W . State::$cfg['wallet'] . C::RESET . PHP_EOL;
    echo '  ' . C::HACK_D . 'Cookies         ' . C::RESET . '▸ ' . C::HACK_W . substr(State::$cfg['manual_cookies'], 0, 30) . '...' . C::RESET . PHP_EOL;
    echo '  ' . C::HACK_D . 'Claim Delay     ' . C::RESET . '▸ ' . C::HACK_W . CLAIM_DELAY . 's' . C::RESET . PHP_EOL;
    echo '  ' . C::HACK_D . 'Sleep Between   ' . C::RESET . '▸ ' . C::HACK_W . SLEEP_BETWEEN . 's' . C::RESET . PHP_EOL;
    echo '  ' . C::HACK_D . 'Max Claims      ' . C::RESET . '▸ ' . C::HACK_W . MAX_CLAIMS . 'x' . C::RESET . PHP_EOL;
    echo '  ' . C::HACK_D . 'Captcha Poll    ' . C::RESET . '▸ ' . C::HACK_W . CAPTCHA_POLL . 's' . C::RESET . PHP_EOL;
    echo '  ' . C::HACK_D . 'Captcha Timeout ' . C::RESET . '▸ ' . C::HACK_W . CAPTCHA_TIMEOUT . 's' . C::RESET . PHP_EOL;
    echo PHP_EOL;

    if (!promptConfirm('  Lanjut start bot?', true)) {
        echo '  ' . C::HACK_R . 'Batal.' . C::RESET . PHP_EOL;
        exit(0);
    }
    echo PHP_EOL;
}

/* ======================= HTTP ======================= */

function httpRequest(
    string $url,
    string $method = 'GET',
    array|string|null $data = null,
    array $headers = [],
    bool $followLocation = true
): array {
    $ch = curl_init();
    $defaultHeaders = [
        'User-Agent: ' . USER_AGENT,
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language: id-ID,id;q=0.9,en;q=0.8',
        'Upgrade-Insecure-Requests: 1',
    ];
    $allHeaders = array_merge($defaultHeaders, $headers);

    $opts = [
        CURLOPT_URL            => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER         => true,
        CURLOPT_FOLLOWLOCATION => $followLocation,
        CURLOPT_MAXREDIRS      => 5,
        CURLOPT_TIMEOUT        => 30,
        CURLOPT_CONNECTTIMEOUT => 15,
        CURLOPT_HTTPHEADER     => $allHeaders,
        CURLOPT_COOKIEFILE     => SESSION_FILE,
        CURLOPT_COOKIEJAR      => SESSION_FILE,
        CURLOPT_ENCODING       => '',
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_SSL_VERIFYHOST => 2,
    ];

    if ($method === 'POST') {
        $opts[CURLOPT_POST]       = true;
        $opts[CURLOPT_POSTFIELDS] = is_array($data) ? http_build_query($data) : (string)$data;
    }
    curl_setopt_array($ch, $opts);

    $raw   = curl_exec($ch);
    $err   = curl_error($ch);
    $code  = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $hsize = curl_getinfo($ch, CURLINFO_HEADER_SIZE);

    if ($raw === false) {
        return ['ok' => false, 'code' => 0, 'body' => '', 'error' => $err, 'headers' => ''];
    }
    $head = substr($raw, 0, $hsize);
    $body = substr($raw, $hsize);
    return ['ok' => $code >= 200 && $code < 400, 'code' => $code, 'body' => $body, 'error' => null, 'headers' => $head];
}

function httpJson(string $url, ?array $payload = null, string $method = 'GET'): ?array {
    $ch = curl_init();
    $opts = [
        CURLOPT_URL            => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 60,
        CURLOPT_CONNECTTIMEOUT => 15,
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_HTTPHEADER     => ['Content-Type: application/json', 'Accept: application/json'],
    ];
    if ($method === 'POST' && $payload !== null) {
        $opts[CURLOPT_POST]       = true;
        $opts[CURLOPT_POSTFIELDS] = json_encode($payload);
    }
    curl_setopt_array($ch, $opts);
    $raw = curl_exec($ch);
    if ($raw === false) return null;
    $json = json_decode((string)$raw, true);
    return is_array($json) ? $json : null;
}

/* ======================= SESSION FILE ======================= */

function readSessionFile(): array {
    $result = ['device' => '', 'cookies' => []];
    if (!file_exists(SESSION_FILE)) return $result;

    foreach (file(SESSION_FILE, FILE_IGNORE_NEW_LINES) as $line) {
        if ($line === '') continue;
        if (preg_match('/^#\s*device:\s*(\S+)/i', $line, $m)) {
            $result['device'] = $m[1];
            continue;
        }
        if (str_starts_with($line, '#')) continue;
        $parts = preg_split('/\t/', $line);
        if (count($parts) >= 7) {
            $result['cookies'][$parts[5]] = $parts;
        }
    }
    return $result;
}

function writeSessionFile(string $device, array $cookiePairs): void {
    $expires = time() + 86400 * 30;
    $lines = [];
    $lines[] = '# freeltc session file';
    $lines[] = '# device: ' . $device;
    foreach ($cookiePairs as $name => $value) {
        $lines[] = implode("\t", [
            'freeltc.fun', 'FALSE', '/', 'FALSE', (string)$expires, $name, $value
        ]);
    }
    file_put_contents(SESSION_FILE, implode("\n", $lines) . "\n");
}

function getDeviceToken(): string {
    $sess = readSessionFile();
    if (!empty($sess['device'])) return $sess['device'];
    $random = bin2hex(random_bytes(8)) . base_convert((string)time(), 10, 36);
    $token  = 'dev_' . substr($random, 0, 22);
    writeSessionFile($token, $sess['cookies']);
    return $token;
}

function seedManualCookies(string $manualCookies): void {
    $pairs = [];
    foreach (explode(';', $manualCookies) as $pair) {
        $pair = trim($pair);
        if ($pair === '') continue;
        [$k, $v] = array_pad(explode('=', $pair, 2), 2, '');
        if ($k !== '') $pairs[$k] = $v;
    }

    $sess = readSessionFile();
    $device = $sess['device'];
    if ($device === '') {
        $random = bin2hex(random_bytes(8)) . base_convert((string)time(), 10, 36);
        $device = 'dev_' . substr($random, 0, 22);
    }

    $flat = [];
    foreach ($sess['cookies'] as $name => $parts) {
        $flat[$name] = $parts[6] ?? '';
    }
    foreach ($pairs as $name => $value) {
        $flat[$name] = $value;
    }

    writeSessionFile($device, $flat);
}

function getCookieValue(string $name): ?string {
    $sess = readSessionFile();
    return $sess['cookies'][$name][6] ?? null;
}

/* ======================= PARSERS ======================= */

function extractInput(string $html, string $name): ?string {
    $q = preg_quote($name, '/');
    if (preg_match('/<input[^>]*\bname=["\']' . $q . '["\'][^>]*\bvalue=["\']([^"\']*)["\']/i', $html, $m)) return $m[1];
    if (preg_match('/<input[^>]*\bvalue=["\']([^"\']*)["\'][^>]*\bname=["\']' . $q . '["\']/i', $html, $m)) return $m[1];
    return null;
}

function extractBalance(string $html): ?string {
    if (preg_match('/class="balance-amount"[^>]*>\s*([\d.,]+)/i', $html, $m)) return $m[1];
    if (preg_match('/class="balance-amount">\s*([\d.,]+)/i', $html, $m)) return $m[1];
    return null;
}

function extractCaptchaImage(string $html): ?string {
    if (preg_match('/<div[^>]*class=["\'][^"\']*captcha-box[^"\']*["\'][^>]*>.*?<img[^>]+src=["\']data:image\/(?:png|jpe?g|gif);base64,([A-Za-z0-9+\/=\s]+)["\']/is', $html, $m)) {
        return preg_replace('/\s+/', '', $m[1]);
    }
    if (preg_match('/<img[^>]+src=["\']data:image\/(?:png|jpe?g|gif);base64,([A-Za-z0-9+\/=\s]+)["\'][^>]*>/is', $html, $m)) {
        return preg_replace('/\s+/', '', $m[1]);
    }
    return null;
}

function hasCaptcha(string $html): bool {
    return stripos($html, 'captcha_answer') !== false
        || stripos($html, 'captcha-box') !== false
        || extractCaptchaImage($html) !== null;
}

function extractWallet(string $html): ?string {
    $wallet = extractInput($html, 'wallet');
    if ($wallet && filter_var($wallet, FILTER_VALIDATE_EMAIL)) return $wallet;

    if (preg_match_all('/data-cfemail=["\']([0-9a-f]+)["\']/i', $html, $matches)) {
        foreach ($matches[1] as $hex) {
            $decoded = decodeCfEmail($hex);
            if ($decoded && filter_var($decoded, FILTER_VALIDATE_EMAIL)) return $decoded;
        }
    }

    if (preg_match('/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/', $html, $m)) {
        $found = $m[0];
        if (!str_contains($found, 'example.com') && !str_contains($found, 'faucetpay.io')) return $found;
    }
    return null;
}

function decodeCfEmail(string $hex): ?string {
    if (strlen($hex) < 4 || strlen($hex) % 2 !== 0) return null;
    $bytes = str_split($hex, 2);
    $key = hexdec($bytes[0]);
    $out = '';
    for ($i = 1; $i < count($bytes); $i++) {
        $out .= chr(hexdec($bytes[$i]) ^ $key);
    }
    return $out;
}

function sessionIsValid(string $html): bool {
    if (stripos($html, 'Welcome back') !== false) return true;
    if (stripos($html, 'name="earn_ticket"') !== false) return true;
    if (stripos($html, 'Submit Claim') !== false) return true;
    if (stripos($html, 'name="token"') !== false && stripos($html, 'earn_ticket') !== false) return true;
    if (stripos($html, 'Access Dashboard') !== false) return false;
    if (stripos($html, 'Enter your address to begin') !== false) return false;
    return false;
}

/* ======================= CAPTCHA SOLVER ======================= */

function captchaSubmit(string $base64Image): ?string {
    $payload = [
        'apikey'  => State::$cfg['api_key'],
        'methods' => State::$cfg['captcha_method'],
        'image'   => $base64Image,
        'json'    => 1,
    ];

    logmsg('Captcha: submit ke API', 'captcha');
    UI::render();

    $resp = httpJson('https://api.waryono.my.id/in.php', $payload, 'POST');
    if (!$resp) { logmsg('Captcha: response kosong', 'error'); return null; }

    if (($resp['status'] ?? 0) != 1) {
        $err = $resp['request'] ?? 'unknown';
        logmsg("Captcha: submit gagal ({$err})", 'error');
        return null;
    }

    $id = $resp['request'] ?? null;
    if (!$id) { logmsg('Captcha: request ID kosong', 'error'); return null; }
    return (string)$id;
}

function captchaPoll(string $requestId): ?string {
    $timeout  = CAPTCHA_TIMEOUT;
    $pollInt  = CAPTCHA_POLL;
    $deadline = time() + $timeout;
    $tries    = 0;
    $started  = time();

    $waitKeywords = [
        'not_ready', 'not ready', 'wait', 'processing', 'pending',
        'capcha_not_ready', 'captcha_not_ready', 'in_progress',
        'progress', 'loading', 'queue', 'try_again', 'try again',
    ];
    $invalidKeywords = [
        'error_wrong_id', 'wrong_id', 'invalid_id', 'not_found',
        'not found', 'error_captcha_unsolvable', 'unsolvable',
        'invalid_apikey', 'invalid apikey', 'invalid_key',
    ];

    while (time() < $deadline) {
        $tries++;
        $elapsed = time() - $started;
        State::$activity = sprintf('Polling captcha (%ds) #%d', $elapsed, $tries);
        UI::render();

        $url = 'https://api.waryono.my.id/res.php?' . http_build_query([
            'apikey' => State::$cfg['api_key'],
            'id'     => $requestId,
            'action' => 'get',
            'json'   => 1,
        ]);

        $resp = httpJson($url, null, 'GET');
        if ($resp === null) { sleep($pollInt); continue; }

        $status  = (int)($resp['status'] ?? 0);
        $reqRaw  = (string)($resp['request'] ?? '');
        $reqLow  = strtolower($reqRaw);

        if ($status === 1 && $reqRaw !== '') return $reqRaw;

        $isWaiting = false;
        foreach ($waitKeywords as $kw) {
            if (str_contains($reqLow, $kw)) { $isWaiting = true; break; }
        }
        if ($isWaiting) {
            State::$activity = sprintf('Captcha processing (%ds) #%d', $elapsed, $tries);
            UI::render();
            sleep($pollInt);
            continue;
        }

        $isInvalid = false;
        foreach ($invalidKeywords as $kw) {
            if (str_contains($reqLow, $kw)) { $isInvalid = true; break; }
        }
        if ($isInvalid) { logmsg('Captcha: request invalid', 'error'); return null; }

        if ($status === 0) {
            State::$activity = sprintf('Captcha pending (%ds) #%d', $elapsed, $tries);
            UI::render();
            sleep($pollInt);
            continue;
        }

        logmsg('Captcha poll error', 'error');
        return null;
    }

    logmsg("Captcha: timeout {$elapsed}s", 'error');
    return null;
}

function isValidTextAnswer(string $ans): bool {
    $ans = trim($ans);
    if (preg_match('/^x\s*[:=]\s*\d+/i', $ans)) return false;
    if (preg_match('/^\d+\s*[,;]\s*\d+$/', $ans)) return false;
    $clean = str_replace(' ', '', $ans);
    if (!preg_match('/^[A-Za-z0-9]{3,8}$/', $clean)) return false;
    return true;
}

function solveCaptcha(string $base64Image): ?string {
    State::$activity = 'Submit captcha';
    UI::render();

    $id = captchaSubmit($base64Image);
    if (!$id) { State::$activity = ''; return null; }

    $answer = captchaPoll($id);
    State::$activity = '';

    if ($answer === null) { UI::render(); return null; }

    $clean = strtoupper(preg_replace('/[^A-Za-z0-9]/', '', $answer));

    if (!isValidTextAnswer($clean)) {
        logmsg("Captcha: jawaban invalid: '{$clean}'", 'warn');
        UI::render();
        return null;
    }

    State::$captchaSolved++;
    logmsg("✓ Captcha solved: {$clean}", 'success');
    UI::render();
    return $clean;
}

/* ======================= FLOW ======================= */

/**
 * Fix: endpoint bener = /faucet/earn (bukan /claim/earn)
 */
function bootstrapSession(): array {
    logmsg('Verifying session...', 'cookie');
    UI::render();

    $r = httpRequest(HOST . '/faucet/earn');  // ✅ FIX
    if (!$r['ok']) {
        return ['ok' => false, 'wallet' => null, 'html' => null, 'error' => 'HTTP ' . $r['code']];
    }
    if ($r['code'] === 403) {
        return ['ok' => false, 'wallet' => null, 'html' => null, 'error' => 'CF cookie expired (403)'];
    }
    if ($r['code'] === 404) {
        return ['ok' => false, 'wallet' => null, 'html' => null, 'error' => 'Endpoint not found (404) — cek URL'];
    }

    $html = $r['body'];

    if (!sessionIsValid($html)) {
        return ['ok' => false, 'wallet' => null, 'html' => $html, 'error' => 'Session invalid / belum login'];
    }

    $wallet = extractWallet($html);
    return ['ok' => true, 'wallet' => $wallet, 'html' => $html, 'error' => null];
}

function getClaimParams(string $wallet): array {
    logmsg('Opening earn page', 'info');
    UI::render();

    $r = httpRequest(HOST . '/faucet/earn');  // ✅ FIX
    if (!$r['ok']) return ['ok' => false];

    $html   = $r['body'];
    $csrf   = extractInput($html, 'csrf_token_name') ?: getCookieValue('csrf_cookie_name');
    $token  = extractInput($html, 'token');
    $ticket = extractInput($html, 'earn_ticket');
    $bal    = extractBalance($html);
    $hasCap = hasCaptcha($html);
    $capImg = $hasCap ? extractCaptchaImage($html) : null;

    $freshWallet = extractWallet($html);
    if ($freshWallet && $freshWallet !== $wallet) $wallet = $freshWallet;

    if ($bal) {
        State::$balance = $bal;
    }

    if (!$token || !$ticket) {
        logmsg('token / earn_ticket gak ketemu', 'error');
        UI::render();
        return ['ok' => false];
    }

    return [
        'ok'            => true,
        'csrf'          => $csrf,
        'token'         => $token,
        'ticket'        => $ticket,
        'balance'       => $bal,
        'captcha_image' => $capImg,
        'wallet'        => $wallet,
    ];
}

function submitClaim(string $wallet, string $csrf, string $token, string $ticket, ?string $captchaAnswer = null): array {
    $payload = [
        'csrf_token_name' => $csrf,
        'token'           => $token,
        'earn_ticket'     => $ticket,
        'confirm_wallet'  => '',
        'wallet'          => $wallet,
    ];
    if ($captchaAnswer !== null) $payload['captcha_answer'] = $captchaAnswer;

    logmsg('Submit claim' . ($captchaAnswer ? ' (captcha)' : ''));
    UI::render();

    $r = httpRequest(
        HOST . '/faucet/earn',  // ✅ FIX
        'POST',
        $payload,
        ['Content-Type: application/x-www-form-urlencoded', 'Origin: ' . HOST, 'Referer: ' . HOST . '/faucet/earn']
    );

    if (!$r['ok']) {
        return ['success' => false, 'error' => true, 'error_msg' => 'HTTP ' . $r['code'], 'captcha_error' => false, 'coins' => 0.0];
    }

    $body = $r['body'];
    $success = (stripos($body, 'has been added') !== false)
            || (stripos($body, "icon: 'success'") !== false)
            || (stripos($body, 'Success!') !== false);

    $error = null;
    if (preg_match("/icon:\s*'error'[^}]*html:\s*'([^']+)'/i", $body, $m)) {
        $error = strip_tags($m[1]);
    }

    $captchaError = $error && (
        stripos($error, 'captcha') !== false ||
        stripos($error, 'verification') !== false
    );

    $coins = 0.0;
    if ($success) {
        if (preg_match('/([\d.,]+)\s*Coins?\s*has been added/i', $body, $m)) {
            $coins = (float)str_replace(',', '', $m[1]);
        } elseif (preg_match('/([\d.,]+)\s*Coins?/i', $body, $m)) {
            $coins = (float)str_replace(',', '', $m[1]);
        }
    }

    return [
        'success'       => $success,
        'error'         => !$success && $error !== null,
        'error_msg'     => $error,
        'captcha_error' => $captchaError,
        'coins'         => $coins,
    ];
}

/* ======================= COUNTDOWN ======================= */

function countdown(int $seconds, ?int $totalForBar = null): void {
    $total = $totalForBar ?? $seconds;
    for ($i = $seconds; $i > 0; $i--) {
        if (State::$stopFlag) return;
        UI::render($i, $total);
        sleep(1);
    }
    UI::render(0, $total);
}

/* ======================= FINAL REPORT ======================= */

function showReport(): void {
    $runtime = time() - State::$startTime;
    $rh = intdiv($runtime, 3600);
    $rm = intdiv($runtime % 3600, 60);
    $rs = $runtime % 60;
    $rate = State::$claims > 0 ? (State::$success / State::$claims * 100) : 0;

    Hack::clear();
    echo PHP_EOL;
    echo C::HACK_G . C::BOLD;
    echo '  ╔════════════════════════════════════════════════════════╗' . PHP_EOL;
    echo '  ║          █▀▀ █ █▄░█ ▄▀█ █░░   █▀█ █▀ █▀▀ █▀█          ║' . PHP_EOL;
    echo '  ║          █▀░ █ █░▀█ █▀█ █▄▄   █▀▄ █▄ █▀░ █▀▄          ║' . PHP_EOL;
    echo '  ╚════════════════════════════════════════════════════════╝' . C::RESET . PHP_EOL;
    echo PHP_EOL;

    printf("  %s⛔ Stop reason    %s▸ %s%s%s\n", C::HACK_D, C::RESET, C::HACK_R, State::$stopReason, C::RESET);
    printf("  %s⏱  Runtime        %s▸ %s%02dh %02dm %02ds%s\n", C::HACK_D, C::RESET, C::HACK_C, $rh, $rm, $rs, C::RESET);
    printf("  %s👤 Wallet         %s▸ %s%s%s\n", C::HACK_D, C::RESET, C::HACK_C, State::$wallet, C::RESET);
    printf("  %s💰 Balance        %s▸ %s%s %s%s\n", C::HACK_D, C::RESET, C::HACK_Y, State::$balance, COIN_UNIT, C::RESET);
    echo PHP_EOL;

    echo '  ' . C::HACK_G . '───────────────── STATISTIK ─────────────────' . C::RESET . PHP_EOL;
    printf("  %s📊 Total claims   %s▸ %s%d / %d%s\n", C::HACK_D, C::RESET, C::HACK_W, State::$claims, State::$maxClaims, C::RESET);
    printf("  %s✓  Success        %s▸ %s%d%s\n", C::HACK_D, C::RESET, C::HACK_G, State::$success, C::RESET);
    printf("  %s✗  Failed         %s▸ %s%d%s\n", C::HACK_D, C::RESET, C::HACK_R, State::$failed, C::RESET);
    printf("  %s%%  Success rate   %s▸ %s%.2f%%%s\n", C::HACK_D, C::RESET, ($rate >= 90 ? C::HACK_G : ($rate >= 70 ? C::HACK_Y : C::HACK_R)), $rate, C::RESET);
    printf("  %s🤖 Captcha solved %s▸ %s%d%s\n", C::HACK_D, C::RESET, C::HACK_C, State::$captchaSolved, C::RESET);
    echo PHP_EOL;

    echo '  ' . C::HACK_Y . '───────────────── EARNINGS ─────────────────' . C::RESET . PHP_EOL;
    printf("  %s💎 Total earned   %s▸ %s%.2f %s%s\n", C::HACK_D, C::RESET, C::HACK_G, State::$coins_earned, COIN_UNIT, C::RESET);
    printf("  %s🎁 Last reward    %s▸ %s%s%s\n", C::HACK_D, C::RESET, C::HACK_G, State::$lastReward, C::RESET);
    if (State::$success > 0) {
        $avg = State::$coins_earned / State::$success;
        printf("  %s📈 Avg per claim  %s▸ %s%.2f %s%s\n", C::HACK_D, C::RESET, C::HACK_C, $avg, COIN_UNIT, C::RESET);
    }
    if ($runtime > 0 && State::$coins_earned > 0) {
        $perHour = State::$coins_earned / ($runtime / 3600);
        $perDay  = $perHour * 24;
        printf("  %s⏰ Rate / hour    %s▸ %s%.2f %s%s\n", C::HACK_D, C::RESET, C::HACK_C, $perHour, COIN_UNIT, C::RESET);
        printf("  %s🌙 Projected 24h  %s▸ %s%.2f %s%s\n", C::HACK_D, C::RESET, C::HACK_M, $perDay, COIN_UNIT, C::RESET);
    }
    echo PHP_EOL;

    echo C::HACK_G . str_repeat('═', 62) . C::RESET . PHP_EOL;
    echo '  ' . C::HACK_D . 'Session end · no log · no state file' . C::RESET . PHP_EOL;
    echo C::HACK_G . str_repeat('═', 62) . C::RESET . PHP_EOL;
    echo PHP_EOL;
}

/* ======================= MAIN ======================= */

function main(): void {
    Hack::bootSequence();
    runSetup();

    State::$claims        = 0;
    State::$success       = 0;
    State::$failed        = 0;
    State::$coins_earned  = 0.0;
    State::$captchaSolved = 0;
    State::$maxClaims     = MAX_CLAIMS;
    State::$startTime     = time();
    State::$wallet        = State::$cfg['wallet'];

    seedManualCookies(State::$cfg['manual_cookies']);
    logmsg('Session file ready', 'cookie');

    State::$status = 'VERIFYING';
    UI::render();
    $boot = bootstrapSession();
    if (!$boot['ok']) {
        logmsg('Session invalid: ' . $boot['error'], 'error');
        UI::render();
        echo PHP_EOL . C::HACK_Y . '  ⚠ ' . $boot['error'] . C::RESET . PHP_EOL;
        echo C::HACK_D . '  Tips: cek cookies & wallet di setup wizard.' . C::RESET . PHP_EOL;
        exit(3);
    }

    $wallet = $boot['wallet'] ?? '';
    if ($wallet) {
        State::$wallet = $wallet;
        logmsg('Wallet: ' . $wallet, 'success');
    }

    State::$status = 'RUNNING';
    logmsg('Target: ' . MAX_CLAIMS . ' claims', 'target');
    UI::render();

    $consecutiveFails = 0;

    while (!State::$stopFlag) {
        if (State::$claims >= State::$maxClaims) {
            State::$stopFlag = true;
            State::$stopReason = 'Max claims tercapai (' . State::$maxClaims . 'x)';
            logmsg('Target tercapai! Auto-stop', 'stop');
            UI::render();
            break;
        }

        State::$status = sprintf('CLAIM %d/%d', State::$claims + 1, State::$maxClaims);

        $params = getClaimParams($wallet);
        if (!$params['ok']) {
            $consecutiveFails++;
            State::$failed++;
            State::$claims++;

            if ($consecutiveFails >= 3) {
                logmsg("Gagal {$consecutiveFails}x — auto-stop", 'stop');
                State::$stopFlag = true;
                State::$stopReason = 'Gagal fetch params 3x berturut';
                UI::render();
                break;
            }
            logmsg('Retry param 30s', 'warn');
            UI::render();
            countdown(30, 30);
            continue;
        }
        $consecutiveFails = 0;

        if (!empty($params['wallet']) && $params['wallet'] !== $wallet) {
            $wallet = $params['wallet'];
            State::$wallet = $wallet;
        }

        $captchaAnswer = null;
        if (!empty($params['captcha_image'])) {
            $captchaAnswer = solveCaptcha($params['captcha_image']);
            if ($captchaAnswer === null) {
                logmsg('Gagal solve captcha', 'error');
                State::$failed++;
                State::$claims++;
                UI::render();
                countdown(SLEEP_BETWEEN, SLEEP_BETWEEN);
                continue;
            }
        }

        $result = submitClaim(
            $wallet,
            $params['csrf'],
            $params['token'],
            $params['ticket'],
            $captchaAnswer
        );

        State::$claims++;

        if ($result['captcha_error']) {
            logmsg('Captcha salah, retry', 'warn');
            State::$failed++;
            UI::render();
            sleep(3);
            continue;
        }

        if ($result['success']) {
            $coins = $result['coins'] ?? 0.0;
            State::$success++;
            if ($coins > 0) {
                State::$coins_earned += $coins;
                State::$lastReward = sprintf('🎁 +%.2f %s', $coins, COIN_UNIT);
                logmsg(sprintf('✓ CLAIM #%d · +%.2f %s', State::$success, $coins, COIN_UNIT), 'money');
            } else {
                State::$lastReward = '🎁 Claimed (amount n/a)';
                logmsg(sprintf('✓ CLAIM #%d berhasil', State::$success), 'success');
            }
            UI::render();
            countdown(SLEEP_BETWEEN, SLEEP_BETWEEN);
        } else {
            $errMsg = $result['error_msg'] ?? 'Unknown error';
            State::$failed++;

            logmsg('✗ ERROR: ' . $errMsg, 'error');
            UI::render();

            State::$stopFlag = true;
            State::$stopReason = 'Claim error: ' . $errMsg;
            break;
        }
    }

    showReport();
}

main();
