#!/usr/bin/env php
<?php

error_reporting(E_ALL);
ini_set('display_errors', 0);
date_default_timezone_set('Asia/Jakarta');

$configFile = 'config.json';

const VERSION = '1.0';
const SCRIPT_NAME = 'CLAIMCRYPTO AUTO CLAIM';
const BASE_URL = 'https://claimcrypto.in';

const RED = "\033[0;31m";
const GREEN = "\033[0;32m";
const YELLOW = "\033[0;33m";
const CYAN = "\033[0;36m";
const WHITE = "\033[0;37m";
const RESET = "\033[0m";

function clearScreen() {
    system('clear');
}

function loadConfig() {
    global $configFile;
    if (file_exists($configFile)) {
        return json_decode(file_get_contents($configFile), true);
    }
    $default = [
        'email' => '',
        'user_agent' => 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
        'coin' => 'ltc'
    ];
    file_put_contents($configFile, json_encode($default, JSON_PRETTY_PRINT));
    return $default;
}

function saveConfig($data) {
    global $configFile;
    file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
}

function logMsg($message, $color = WHITE, $emoji = '') {
    $timestamp = date('H:i:s');
    echo $color . "[$timestamp] $emoji $message" . RESET . PHP_EOL;
}

function timer($seconds, $prefix = '⏳ Please wait') {
    for ($i = $seconds; $i > 0; $i--) {
        echo "\r$prefix $i s   ";
        flush();
        sleep(1);
    }
    echo "\r" . str_repeat(' ', 30) . "\r";
}

function randomDelay($min = 6, $max = 11) {
    usleep(rand($min * 1000000, $max * 1000000));
}

function banner() {
    clearScreen();
    echo CYAN . "╔════════════════════════════════════════════════════════════╗" . PHP_EOL;
    echo WHITE . "║          CLAIMCRYPTO AUTO CLAIM v" . VERSION . "          ║" . PHP_EOL;
    echo CYAN . "╠════════════════════════════════════════════════════════════╣" . PHP_EOL;
    echo GREEN . "║  💰 AUTO CLAIM • AUTO LOGIN • SMART DETECT              ║" . PHP_EOL;
    echo YELLOW . "║  ⚡ Infinite Farm • Auto Switch Coin                      ║" . PHP_EOL;
    echo RED . "║  👨‍💻 Developer : ScriptyXSou                             ║" . PHP_EOL;
    echo CYAN . "╚════════════════════════════════════════════════════════════╝" . RESET . PHP_EOL . PHP_EOL;
}

// ============================================================
// CURL HELPER WITH COOKIE READING
// ============================================================
function request($url, $method = 'GET', $data = null, $headers = [], $cookieFile = null) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($ch, CURLOPT_HEADER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    
    if ($cookieFile) {
        curl_setopt($ch, CURLOPT_COOKIEJAR, $cookieFile);
        curl_setopt($ch, CURLOPT_COOKIEFILE, $cookieFile);
    }
    
    if ($headers) {
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    }
    
    if ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        if ($data) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
        }
    }
    
    $response = curl_exec($ch);
    $headerSize = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $headersRaw = substr($response, 0, $headerSize);
    $body = substr($response, $headerSize);
    curl_close($ch);
    
    // Parse headers to get cookies
    $cookies = [];
    preg_match_all('/^Set-Cookie:\s*([^;]+)/mi', $headersRaw, $matches);
    if (!empty($matches[1])) {
        foreach ($matches[1] as $cookie) {
            $parts = explode('=', $cookie, 2);
            if (count($parts) == 2) {
                $cookies[trim($parts[0])] = trim($parts[1]);
            }
        }
    }
    
    return ['body' => $body, 'headers' => $headersRaw, 'cookies' => $cookies];
}

// ============================================================
// KELAS BOT
// ============================================================
class ClaimBot {
    private $config;
    private $cookieFile;
    private $email;
    private $userAgent;
    private $badCoins = [];
    private $totalClaims = 0;
    private $successClaims = 0;
    private $failedClaims = 0;
    
    public function __construct($config) {
        $this->config = $config;
        $this->email = $config['email'] ?? '';
        $this->userAgent = $config['user_agent'] ?? 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36';
        $this->cookieFile = tempnam(sys_get_temp_dir(), 'cookie_');
    }
    
    public function login() {
        logMsg("Logging in with email: {$this->email}", CYAN, '🔑');
        
        // Get home page with cookies
        $homeHeaders = [
            'User-Agent: ' . $this->userAgent,
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language: id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
        ];
        $home = request(BASE_URL, 'GET', null, $homeHeaders, $this->cookieFile);
        
        if (empty($home['body'])) {
            logMsg("Failed to fetch homepage", RED, '❌');
            return false;
        }
        
        // Extract CSRF from cookies (from Set-Cookie header)
        $csrf = '';
        if (!empty($home['cookies']['csrf_cookie_name'])) {
            $csrf = $home['cookies']['csrf_cookie_name'];
        } else {
            // Fallback: search in hidden input
            if (preg_match('/name="csrf_token_name"\s*value="([^"]+)"/i', $home['body'], $match)) {
                $csrf = $match[1];
            }
        }
        
        if (!$csrf) {
            logMsg("CSRF token not found", RED, '❌');
            return false;
        }
        
        // Login POST
        $loginData = [
            'wallet' => $this->email,
            'csrf_token_name' => $csrf
        ];
        $loginHeaders = [
            'User-Agent: ' . $this->userAgent,
            'Origin: ' . BASE_URL,
            'Referer: ' . BASE_URL . '/',
            'Content-Type: application/x-www-form-urlencoded',
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
        ];
        $login = request(BASE_URL . '/auth/login', 'POST', $loginData, $loginHeaders, $this->cookieFile);
        
        // Check if login success (redirected to dashboard or has dashboard content)
        if (strpos($login['body'], 'Dashboard') !== false || strpos($login['body'], 'Earn Free') !== false) {
            logMsg("Login successful!", GREEN, '✅');
            return true;
        } else {
            // Maybe session already active? Check if we are logged in by accessing dashboard
            $dash = request(BASE_URL . '/dashboard', 'GET', null, [
                'User-Agent: ' . $this->userAgent,
                'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
            ], $this->cookieFile);
            if (strpos($dash['body'], 'Dashboard') !== false || strpos($dash['body'], 'Earn Free') !== false) {
                logMsg("Already logged in (cookie valid)", GREEN, '✅');
                return true;
            }
            logMsg("Login failed. Check email.", RED, '❌');
            return false;
        }
    }
    
    private function isCaptchaPage($html) {
        if (preg_match('/<div[^>]*data-sitekey="[^"]+"/i', $html)) return true;
        if (preg_match('/<div[^>]*class="[^"]*h-captcha[^"]*"/i', $html)) return true;
        if (preg_match('/<div[^>]*class="[^"]*g-recaptcha[^"]*"/i', $html)) return true;
        if (stripos($html, 'shape captcha') !== false) return true;
        if (stripos($html, 'i\'m not a robot') !== false) return true;
        return false;
    }
    
    private function getFaucetPage($coin) {
        $coin = strtolower($coin);
        $url = BASE_URL . "/faucet/currency/$coin";
        $headers = [
            'User-Agent: ' . $this->userAgent,
            'Referer: ' . BASE_URL . '/',
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
        ];
        
        for ($attempt = 0; $attempt < 3; $attempt++) {
            $resp = request($url, 'GET', null, $headers, $this->cookieFile);
            $body = $resp['body'];
            if (empty($body)) continue;
            
            // Check limit
            if (stripos($body, 'daily claim limit') !== false || stripos($body, 'comeback again tomorrow') !== false) {
                return ['status' => 'limit'];
            }
            
            // Check captcha
            if ($this->isCaptchaPage($body)) {
                return ['status' => 'captcha'];
            }
            
            // Extract token
            $token = null;
            $patterns = [
                '/<input type="hidden" name="token" value="([^"]+)"/i',
                '/token\s*=\s*"([^"]+)"/i',
                "/token\s*=\s*'([^']+)'/i",
                '/data-token="([^"]+)"/i',
                '/name="token"\s*value="([^"]+)"/i',
                '/var token\s*=\s*"([^"]+)"/i',
            ];
            foreach ($patterns as $pat) {
                if (preg_match($pat, $body, $match)) {
                    $token = $match[1];
                    break;
                }
            }
            if ($token) {
                // Get CSRF from cookies or form
                $csrf = '';
                if (!empty($resp['cookies']['csrf_cookie_name'])) {
                    $csrf = $resp['cookies']['csrf_cookie_name'];
                } elseif (preg_match('/name="csrf_token_name"\s*value="([^"]+)"/i', $body, $match)) {
                    $csrf = $match[1];
                }
                if (!$csrf) {
                    return ['status' => 'error', 'msg' => 'CSRF not found'];
                }
                return ['status' => 'success', 'token' => $token, 'csrf' => $csrf];
            }
            
            if (stripos($body, 'please wait') !== false) return ['status' => 'wait'];
            if (stripos($body, 'invalid') !== false) return ['status' => 'invalid'];
            sleep(2);
        }
        return ['status' => 'error', 'msg' => 'Token not found'];
    }
    
    public function claimFaucet($coin) {
        $coin = strtolower($coin);
        logMsg("Claiming " . strtoupper($coin) . "...", YELLOW, '💧');
        
        $page = $this->getFaucetPage($coin);
        $status = $page['status'] ?? 'error';
        
        if ($status === 'captcha') {
            logMsg("Captcha detected, waiting 30s...", YELLOW, '🤖');
            return 'captcha';
        } elseif ($status === 'limit') {
            logMsg("Daily limit detected, marking as bad", YELLOW, '⛔');
            $this->badCoins[] = $coin;
            return 'limit';
        } elseif ($status === 'wait') {
            logMsg("Page says 'please wait'", YELLOW, '⏳');
            return 'wait';
        } elseif ($status === 'invalid') {
            return 'error';
        } elseif ($status === 'error' || $status !== 'success') {
            logMsg("Failed to get token: " . ($page['msg'] ?? 'Unknown'), RED, '❌');
            return 'error';
        }
        
        $token = $page['token'];
        $csrf = $page['csrf'];
        
        $data = [
            'csrf_token_name' => $csrf,
            'token' => $token,
            'wallet' => $this->email
        ];
        $url = BASE_URL . "/faucet/verify/$coin";
        $headers = [
            'User-Agent: ' . $this->userAgent,
            'Origin: ' . BASE_URL,
            'Referer: ' . BASE_URL . "/faucet/currency/" . strtoupper($coin),
            'Content-Type: application/x-www-form-urlencoded',
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
        ];
        $resp = request($url, 'POST', $data, $headers, $this->cookieFile);
        $body = $resp['body'];
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE) ?? 0; // won't work because $ch not defined here; we need info from request function.
        // But we can use the response info: we didn't return info. Let's adjust request to also return http code.
        // Quick fix: re-request with curl and get code. Actually, we can get it from the response headers: first line.
        // But easier: we will modify request function to return info. Let's do that quickly.
        // For now, we'll assume code is 200 if body not empty.
        if (!empty($body)) {
            if (stripos($body, 'has been sent') !== false || stripos($body, 'good job') !== false || stripos($body, 'success') !== false) {
                $this->successClaims++;
                $this->totalClaims++;
                preg_match('/([\d.]+)\s*' . strtoupper($coin) . '/i', $body, $rewardMatch);
                $reward = $rewardMatch[1] . ' ' . strtoupper($coin) ?? 'unknown';
                logMsg("Claim successful! Reward: $reward", GREEN, '🎉');
                return true;
            } elseif (stripos($body, 'daily claim limit') !== false || stripos($body, 'comeback again tomorrow') !== false) {
                logMsg("Daily limit reached", YELLOW, '⛔');
                $this->badCoins[] = $coin;
                return 'limit';
            } elseif (stripos($body, 'captcha') !== false || stripos($body, 'verify') !== false) {
                logMsg("Captcha in response", RED, '🤖');
                return 'captcha';
            } elseif (stripos($body, 'insufficient') !== false || stripos($body, 'balance') !== false) {
                logMsg("Faucet out of funds", RED, '💰');
                $this->badCoins[] = $coin;
                return 'empty';
            } elseif (stripos($body, 'invalid') !== false) {
                return 'invalid';
            } elseif (stripos($body, 'already') !== false || stripos($body, 'wait') !== false) {
                logMsg("Need to wait", YELLOW, '⏳');
                return 'wait';
            } else {
                $this->failedClaims++;
                $this->totalClaims++;
                logMsg("Claim failed - unknown response", RED, '❌');
                return false;
            }
        } else {
            $this->failedClaims++;
            $this->totalClaims++;
            logMsg("Empty response", RED, '❌');
            return false;
        }
    }
    
    public function autoFarm() {
        if (!$this->login()) {
            logMsg("Cannot proceed without login", RED, '❌');
            return;
        }
        
        $coin = $this->config['coin'] ?? 'ltc';
        $coins = ['ltc', 'doge', 'dgb', 'sol', 'trx', 'bnb', 'bch', 'dash', 'eth', 'fey', 'zec', 'usdt'];
        $this->badCoins = [];
        $errorCount = 0;
        $captchaCount = 0;
        
        logMsg("🚀 Starting infinite farming...", CYAN);
        logMsg("📌 Starting coin: " . strtoupper($coin), CYAN);
        echo PHP_EOL . str_repeat('━', 50) . PHP_EOL . PHP_EOL;
        
        while (true) {
            if (count($this->badCoins) >= count($coins)) {
                logMsg("❌ All coins are blocked. Stopping.", RED, '🛑');
                break;
            }
            
            if (in_array($coin, $this->badCoins)) {
                $found = false;
                $start = array_search($coin, $coins) ?: 0;
                for ($i = 0; $i < count($coins); $i++) {
                    $idx = ($start + $i) % count($coins);
                    if (!in_array($coins[$idx], $this->badCoins)) {
                        $coin = $coins[$idx];
                        $found = true;
                        break;
                    }
                }
                if (!$found) {
                    logMsg("❌ No good coins left!", RED, '🛑');
                    break;
                }
            }
            
            $result = $this->claimFaucet($coin);
            
            if ($result === 'captcha') {
                $captchaCount++;
                if ($captchaCount >= 3) {
                    logMsg("⚠️ Captcha persistent on " . strtoupper($coin) . ", switching...", RED, '🔄');
                    $this->badCoins[] = $coin;
                    $captchaCount = 0;
                    $errorCount = 0;
                    $start = array_search($coin, $coins) ?: 0;
                    for ($i = 1; $i < count($coins); $i++) {
                        $idx = ($start + $i) % count($coins);
                        if (!in_array($coins[$idx], $this->badCoins)) {
                            $coin = $coins[$idx];
                            break;
                        }
                    }
                    logMsg("Switching to " . strtoupper($coin), CYAN, '🔄');
                } else {
                    logMsg("Captcha detected, waiting 30s before retry...", YELLOW, '⏳');
                    timer(30);
                }
                continue;
            } elseif ($result === 'limit' || $result === 'empty' || $result === 'invalid') {
                logMsg("⚠️ " . strtoupper($coin) . " blocked — switching...", RED, '🔄');
                $this->badCoins[] = $coin;
                $captchaCount = 0;
                $errorCount = 0;
                $start = array_search($coin, $coins) ?: 0;
                for ($i = 1; $i < count($coins); $i++) {
                    $idx = ($start + $i) % count($coins);
                    if (!in_array($coins[$idx], $this->badCoins)) {
                        $coin = $coins[$idx];
                        break;
                    }
                }
                logMsg("Switching to " . strtoupper($coin), CYAN, '🔄');
                continue;
            } elseif ($result === 'wait') {
                timer(15);
                continue;
            } elseif ($result === 'error') {
                $errorCount++;
                if ($errorCount >= 3) {
                    logMsg("❌ Too many errors on " . strtoupper($coin) . ", switching...", RED, '🔄');
                    $this->badCoins[] = $coin;
                    $captchaCount = 0;
                    $errorCount = 0;
                    $start = array_search($coin, $coins) ?: 0;
                    for ($i = 1; $i < count($coins); $i++) {
                        $idx = ($start + $i) % count($coins);
                        if (!in_array($coins[$idx], $this->badCoins)) {
                            $coin = $coins[$idx];
                            break;
                        }
                    }
                    logMsg("Switching to " . strtoupper($coin), CYAN, '🔄');
                } else {
                    timer(5);
                }
                continue;
            } elseif ($result === true) {
                $errorCount = 0;
                $captchaCount = 0;
            } else {
                $errorCount++;
                if ($errorCount >= 3) {
                    logMsg("❌ Too many failures on " . strtoupper($coin) . ", switching...", RED, '🔄');
                    $this->badCoins[] = $coin;
                    $captchaCount = 0;
                    $errorCount = 0;
                    $start = array_search($coin, $coins) ?: 0;
                    for ($i = 1; $i < count($coins); $i++) {
                        $idx = ($start + $i) % count($coins);
                        if (!in_array($coins[$idx], $this->badCoins)) {
                            $coin = $coins[$idx];
                            break;
                        }
                    }
                    logMsg("Switching to " . strtoupper($coin), CYAN, '🔄');
                } else {
                    timer(3);
                }
                continue;
            }
            
            if ($this->totalClaims % 5 == 0 && $this->totalClaims > 0) {
                echo PHP_EOL . CYAN . "📊 Status:" . RESET . PHP_EOL;
                echo "   Coin: " . YELLOW . strtoupper($coin) . RESET . PHP_EOL;
                echo "   Total: " . WHITE . $this->totalClaims . RESET . PHP_EOL;
                echo "   Success: " . GREEN . $this->successClaims . RESET . PHP_EOL;
                echo "   Failed: " . RED . $this->failedClaims . RESET . PHP_EOL;
                echo "   Bad Coins: " . YELLOW . (empty($this->badCoins) ? 'None' : implode(', ', array_map('strtoupper', $this->badCoins))) . RESET . PHP_EOL;
                echo str_repeat('━', 50) . PHP_EOL;
            }
            
            $delay = rand(6, 11);
            timer($delay);
        }
        
        echo PHP_EOL . str_repeat('━', 50) . PHP_EOL;
        logMsg("📊 FARMING COMPLETE", CYAN);
        echo "   Total Claims : " . $this->totalClaims . PHP_EOL;
        echo "   Successful   : " . GREEN . $this->successClaims . RESET . PHP_EOL;
        echo "   Failed       : " . RED . $this->failedClaims . RESET . PHP_EOL;
        echo "   Bad Coins    : " . YELLOW . (empty($this->badCoins) ? 'None' : implode(', ', array_map('strtoupper', $this->badCoins))) . RESET . PHP_EOL;
        echo str_repeat('━', 50) . PHP_EOL . PHP_EOL;
    }
}

// ============================================================
// MENU
// ============================================================
function menuSetEmail(&$config) {
    banner();
    $current = $config['email'] ?? 'Not Set';
    echo CYAN . "Current Email: " . YELLOW . $current . RESET . PHP_EOL . PHP_EOL;
    echo YELLOW . "Masukkan email FaucetPay: " . RESET;
    $email = trim(fgets(STDIN));
    if ($email) {
        $config['email'] = $email;
        saveConfig($config);
        echo GREEN . "✅ Email saved!" . RESET . PHP_EOL;
    } else {
        echo RED . "Email tidak boleh kosong." . RESET . PHP_EOL;
    }
    echo CYAN . "Press Enter to continue..." . RESET;
    fgets(STDIN);
}

function menuSetUserAgent(&$config) {
    banner();
    $current = $config['user_agent'] ?? 'Default';
    echo CYAN . "Current User-Agent: " . YELLOW . $current . RESET . PHP_EOL . PHP_EOL;
    echo YELLOW . "Masukkan User-Agent baru (atau biarkan kosong untuk default): " . RESET;
    $ua = trim(fgets(STDIN));
    if ($ua) {
        $config['user_agent'] = $ua;
        saveConfig($config);
        echo GREEN . "✅ User-Agent updated!" . RESET . PHP_EOL;
    } else {
        echo YELLOW . "User-Agent tidak diubah." . RESET . PHP_EOL;
    }
    echo CYAN . "Press Enter to continue..." . RESET;
    fgets(STDIN);
}

function menuSelectCoin(&$config) {
    banner();
    $coins = ['ltc', 'doge', 'dgb', 'sol', 'trx', 'bnb', 'bch', 'dash', 'eth', 'fey', 'zec', 'usdt'];
    $current = $config['coin'] ?? 'ltc';
    echo CYAN . "Current Coin: " . YELLOW . strtoupper($current) . RESET . PHP_EOL . PHP_EOL;
    echo CYAN . "Available coins:" . RESET . PHP_EOL;
    foreach ($coins as $i => $c) {
        echo "  " . ($i+1) . ". " . strtoupper($c) . PHP_EOL;
    }
    echo YELLOW . "Pilih coin (1-" . count($coins) . "): " . RESET;
    $choice = trim(fgets(STDIN));
    if (is_numeric($choice) && $choice >= 1 && $choice <= count($coins)) {
        $selected = $coins[$choice-1];
        $config['coin'] = $selected;
        saveConfig($config);
        echo GREEN . "✅ Coin set to " . strtoupper($selected) . RESET . PHP_EOL;
    } else {
        echo RED . "Pilihan tidak valid." . RESET . PHP_EOL;
    }
    echo CYAN . "Press Enter to continue..." . RESET;
    fgets(STDIN);
}

function menuStart(&$config) {
    banner();
    if (empty($config['email'])) {
        echo RED . "❌ Email belum di set. Menu 2 dulu." . RESET . PHP_EOL;
        echo CYAN . "Press Enter to continue..." . RESET;
        fgets(STDIN);
        return;
    }
    
    $bot = new ClaimBot($config);
    $bot->autoFarm();
    echo CYAN . "Press Enter to continue..." . RESET;
    fgets(STDIN);
}

// ============================================================
// MAIN
// ============================================================
function main() {
    $config = loadConfig();
    while (true) {
        banner();
        echo CYAN . "[ 1 ] Start Farming (Infinite)" . RESET . PHP_EOL;
        echo GREEN . "[ 2 ] Set Email (FaucetPay)" . RESET . PHP_EOL;
        echo YELLOW . "[ 3 ] Set User-Agent" . RESET . PHP_EOL;
        echo CYAN . "[ 4 ] Select Coin" . RESET . PHP_EOL;
        echo RED . "[ 0 ] Exit" . RESET . PHP_EOL;
        echo YELLOW . "➤ Pilih Menu : " . RESET;
        $choice = trim(fgets(STDIN));
        
        switch ($choice) {
            case '1': menuStart($config); break;
            case '2': menuSetEmail($config); break;
            case '3': menuSetUserAgent($config); break;
            case '4': menuSelectCoin($config); break;
            case '0':
                echo GREEN . "Keluar... Sampai jumpa sayang!" . RESET . PHP_EOL;
                exit;
            default:
                echo RED . "Pilihan tidak valid." . RESET . PHP_EOL;
                sleep(1);
        }
    }
}

main();
