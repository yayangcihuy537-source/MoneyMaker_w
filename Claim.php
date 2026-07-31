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

function clearScreen() { system('clear'); }

function loadConfig() {
    global $configFile;
    if (file_exists($configFile)) {
        return json_decode(file_get_contents($configFile), true);
    }
    $default = [
        'cookie' => '',
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

function timer($seconds, $prefix = "⏳ Please wait") {
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
            echo WHITE . $prefix . GREEN . " $time_formatted " . WHITE . $spinner . "\r";
            usleep($frame_delay * 1000000);
            $current_frame = ($current_frame + 1) % $frame_count;
            if ((microtime(true) - $start_time) >= 1) break;
        }
        $wait_time--;
    }
    echo "\r" . str_repeat(' ', 50) . "\r";
}

function banner() {
    clearScreen();
    echo CYAN . "╔════════════════════════════════════════════════════════════╗" . PHP_EOL;
    echo WHITE . "║          CLAIMCRYPTO AUTO CLAIM v" . VERSION . "          ║" . PHP_EOL;
    echo CYAN . "╠════════════════════════════════════════════════════════════╣" . PHP_EOL;
    echo GREEN . "║  💰 AUTO CLAIM • COOKIE LOGIN • SMART DETECT            ║" . PHP_EOL;
    echo YELLOW . "║  ⚡ Infinite Farm • Auto Switch Coin                      ║" . PHP_EOL;
    echo RED . "║  👨‍💻 Developer : @MoneyMaker_w                             ║" . PHP_EOL;
    echo CYAN . "╚════════════════════════════════════════════════════════════╝" . RESET . PHP_EOL . PHP_EOL;
}

// ============================================================
// CURL REQUEST WITH COOKIE
// ============================================================
function request($url, $method = 'GET', $data = null, $headers = [], $cookieString = null) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($ch, CURLOPT_HEADER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    
    if ($cookieString) {
        curl_setopt($ch, CURLOPT_COOKIE, $cookieString);
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
    $body = substr($response, $headerSize);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    return ['body' => $body, 'http_code' => $httpCode];
}

// ============================================================
// KELAS BOT
// ============================================================
class ClaimBot {
    private $config;
    private $cookie;
    private $userAgent;
    private $badCoins = [];
    private $totalClaims = 0;
    private $successClaims = 0;
    private $failedClaims = 0;
    private $errorCount = 0;
    private $captchaCount = 0;
    
    public function __construct($config) {
        $this->config = $config;
        $this->cookie = $config['cookie'] ?? '';
        $this->userAgent = $config['user_agent'] ?? 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36';
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
            'Cookie: ' . $this->cookie,
            'Referer: ' . BASE_URL . '/',
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
        ];
        
        for ($attempt = 0; $attempt < 3; $attempt++) {
            $resp = request($url, 'GET', null, $headers);
            $body = $resp['body'];
            if (empty($body)) continue;
            
            if (stripos($body, 'daily claim limit') !== false || stripos($body, 'comeback again tomorrow') !== false) {
                return ['status' => 'limit'];
            }
            if ($this->isCaptchaPage($body)) {
                return ['status' => 'captcha'];
            }
            
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
                $csrf = '';
                if (preg_match('/csrf_cookie_name=([^;]+)/', $this->cookie, $match)) {
                    $csrf = $match[1];
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
            logMsg("Captcha detected", YELLOW, '🤖');
            return 'captcha';
        } elseif ($status === 'limit') {
            logMsg("Daily limit detected", YELLOW, '⛔');
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
        $data = ['csrf_token_name' => $csrf, 'token' => $token];
        $url = BASE_URL . "/faucet/verify/$coin";
        $headers = [
            'User-Agent: ' . $this->userAgent,
            'Cookie: ' . $this->cookie,
            'Origin: ' . BASE_URL,
            'Referer: ' . BASE_URL . "/faucet/currency/" . strtoupper($coin),
            'Content-Type: application/x-www-form-urlencoded',
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
        ];
        $resp = request($url, 'POST', $data, $headers);
        $body = $resp['body'];
        $code = $resp['http_code'];
        
        if ($code == 200) {
            if (stripos($body, 'has been sent') !== false || stripos($body, 'good job') !== false || stripos($body, 'success') !== false) {
                $this->successClaims++;
                $this->totalClaims++;
                preg_match('/([\d.]+)\s*' . strtoupper($coin) . '/i', $body, $rewardMatch);
                $reward = $rewardMatch[1] . ' ' . strtoupper($coin);
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
            logMsg("HTTP $code", RED, '❌');
            return false;
        }
    }
    
    public function autoFarm() {
        if (empty($this->cookie)) {
            logMsg("Cookie not set. Please set cookie first.", RED, '❌');
            return;
        }
        
        $coin = $this->config['coin'] ?? 'ltc';
        $coins = ['ltc', 'doge', 'dgb', 'sol', 'trx', 'bnb', 'bch', 'dash', 'eth', 'fey', 'zec', 'usdt'];
        $this->badCoins = [];
        $this->errorCount = 0;
        $this->captchaCount = 0;
        
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
                $this->captchaCount++;
                if ($this->captchaCount >= 3) {
                    logMsg("⚠️ Captcha persistent on " . strtoupper($coin) . ", switching...", RED, '🔄');
                    $this->badCoins[] = $coin;
                    $this->captchaCount = 0;
                    $this->errorCount = 0;
                    $this->switchCoin($coin, $coins);
                } else {
                    logMsg("Captcha detected, waiting 30s...", YELLOW, '⏳');
                    timer(30);
                }
                continue;
            } elseif ($result === 'limit' || $result === 'empty' || $result === 'invalid') {
                logMsg("⚠️ " . strtoupper($coin) . " blocked — switching...", RED, '🔄');
                $this->badCoins[] = $coin;
                $this->captchaCount = 0;
                $this->errorCount = 0;
                $coin = $this->switchCoin($coin, $coins);
                continue;
            } elseif ($result === 'wait') {
                timer(15);
                continue;
            } elseif ($result === 'error') {
                $this->errorCount++;
                if ($this->errorCount >= 3) {
                    logMsg("❌ Too many errors on " . strtoupper($coin) . ", switching...", RED, '🔄');
                    $this->badCoins[] = $coin;
                    $this->captchaCount = 0;
                    $this->errorCount = 0;
                    $coin = $this->switchCoin($coin, $coins);
                } else {
                    timer(5);
                }
                continue;
            } elseif ($result === true) {
                $this->errorCount = 0;
                $this->captchaCount = 0;
            } else {
                $this->errorCount++;
                if ($this->errorCount >= 3) {
                    logMsg("❌ Too many failures on " . strtoupper($coin) . ", switching...", RED, '🔄');
                    $this->badCoins[] = $coin;
                    $this->captchaCount = 0;
                    $this->errorCount = 0;
                    $coin = $this->switchCoin($coin, $coins);
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
    
    private function switchCoin(&$coin, $coins) {
        $start = array_search($coin, $coins) ?: 0;
        for ($i = 1; $i < count($coins); $i++) {
            $idx = ($start + $i) % count($coins);
            if (!in_array($coins[$idx], $this->badCoins)) {
                $coin = $coins[$idx];
                logMsg("Switching to " . strtoupper($coin), CYAN, '🔄');
                return $coin;
            }
        }
        logMsg("❌ All coins blocked!", RED, '🛑');
        return $coin;
    }
}

// ============================================================
// MENU
// ============================================================
function menuSetCookie(&$config) {
    banner();
    $current = $config['cookie'] ?? 'Not Set';
    echo CYAN . "Current Cookie: " . YELLOW . ($current ? substr($current, 0, 50) . '...' : 'Not Set') . RESET . PHP_EOL . PHP_EOL;
    echo WHITE . "Cara ambil cookie:" . PHP_EOL;
    echo "  1. Login ke claimcrypto.in via browser." . PHP_EOL;
    echo "  2. Buka Dev Tools (F12) → Application → Cookies." . PHP_EOL;
    echo "  3. Copy semua cookie dalam format: nama1=nilai1; nama2=nilai2; ..." . PHP_EOL . PHP_EOL;
    echo YELLOW . "Masukkan Cookie: " . RESET;
    $cookie = trim(fgets(STDIN));
    if ($cookie) {
        $config['cookie'] = $cookie;
        saveConfig($config);
        echo GREEN . "✅ Cookie saved!" . RESET . PHP_EOL;
    } else {
        echo RED . "Cookie tidak boleh kosong." . RESET . PHP_EOL;
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
    if (empty($config['cookie'])) {
        echo RED . "❌ Cookie belum di set. Menu 2 dulu." . RESET . PHP_EOL;
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
        echo GREEN . "[ 2 ] Set Cookie" . RESET . PHP_EOL;
        echo YELLOW . "[ 3 ] Set User-Agent" . RESET . PHP_EOL;
        echo CYAN . "[ 4 ] Select Coin" . RESET . PHP_EOL;
        echo RED . "[ 0 ] Exit" . RESET . PHP_EOL;
        echo YELLOW . "➤ Pilih Menu : " . RESET;
        $choice = trim(fgets(STDIN));
        switch ($choice) {
            case '1': menuStart($config); break;
            case '2': menuSetCookie($config); break;
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
