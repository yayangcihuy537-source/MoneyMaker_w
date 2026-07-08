<?php

error_reporting(0);
date_default_timezone_set('Asia/Jakarta');
$configFile = "ptc_config.json";

// ============================================================
// WARNA
// ============================================================
const hitam  = "\033[0;30m";
const merah  = "\033[1;31m";
const hijau  = "\033[1;32m";
const kuning = "\033[1;33m";
const biru   = "\033[1;34m";
const ungu   = "\033[1;35m";
const cyan   = "\033[1;36m";
const putih  = "\033[1;37m";
const reset  = "\033[0m";

const PINK   = "\033[38;5;206m";
const GOLD   = "\033[38;5;220m";
const TEAL   = "\033[38;5;45m";
const LIME   = "\033[38;5;154m";
const PURPLE = "\033[38;5;141m";
const ORANGE = "\033[38;5;214m";
const RED2   = "\033[38;5;196m";
const GREEN2 = "\033[38;5;118m";

const host = "https://ourcoincash.xyz";

// ============================================================
// BANNER
// ============================================================
function banner() {
    echo cyan . "
╔══════════════════════════════════════════════════════════════╗
║                  OURCOINCASH AUTO PTC                       ║
╠══════════════════════════════════════════════════════════════╣
║  👨‍💻 Developer : " . putih . "Moneymaker_w" . cyan . "                               ║
║  🌐 Website   : " . putih . "ourcoincash.xyz" . cyan . "                             ║
║  🐘 Language  : " . putih . "PHP" . cyan . "                                         ║
║  ⚡ Version   : " . putih . "v1.0" . cyan . "                                         ║
║  🟢 Status    : " . hijau . "ONLINE" . cyan . "                                      ║
╚══════════════════════════════════════════════════════════════╝
" . reset . "\n";
}

// ============================================================
// FUNGSI UTILITY
// ============================================================
function clear() {
    (PHP_OS == "Linux") ? system('clear') : pclose(popen('cls', 'w'));
}

function timer($seconds, $prefix = "⏳ Please wait") {
    $wait_time = (int)$seconds;
    while ($wait_time > 0) {
        $hours = floor($wait_time / 3600);
        $minutes = floor(($wait_time % 3600) / 60);
        $seconds_left = $wait_time % 60;
        $time_formatted = sprintf('%02d:%02d:%02d', $hours, $minutes, $seconds_left);
        echo putih . $prefix . hijau . " $time_formatted " . putih . ". . .\r";
        sleep(1);
        $wait_time--;
    }
    echo "\r                                     \r";
}

function requests($url, $method = 'GET', $data = [], $headers = []) {
    $ch = curl_init();
    $options = [
        CURLOPT_URL            => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HEADER         => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_SSL_VERIFYHOST => 1,
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_HTTPHEADER     => $headers,
        CURLOPT_CONNECTTIMEOUT => 30,
        CURLOPT_TIMEOUT        => 60,
        CURLOPT_USERAGENT      => $GLOBALS['ua'] ?? 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36'
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
    }
    curl_close($ch);
    return false;
}

function getConfig() {
    global $configFile;
    if (!file_exists($configFile)) {
        echo putih . "\n";
        echo cyan . "╔═══════════════════════════════════════╗\n";
        echo cyan . "║" . putih . "        " . cyan . "AUTO PTC - FREE MODE" . putih . "         " . cyan . "║\n";
        echo cyan . "╚═══════════════════════════════════════╝\n\n";
        echo putih . "🍪 Cookie    : " . GOLD;
        $coki = trim(fgets(STDIN));
        echo putih . "🌐 User-Agent: " . GOLD;
        $ua = trim(fgets(STDIN));
        
        $data = [
            "cookie"     => $coki,
            "user_agent" => $ua
        ];
        file_put_contents($configFile, json_encode($data, JSON_PRETTY_PRINT));
        echo hijau . "✅ Config saved!\n\n" . reset;
        sleep(2);
        return $data;
    }
    return json_decode(file_get_contents($configFile), true);
}

// ============================================================
// HEADERS - PAKE YANG SAMA KAYA BROWSER
// ============================================================
function allheaders(&$a, &$b, $coki, $ua){
    $a = [
        "Host: ourcoincash.xyz",
        "Upgrade-Insecure-Requests: 1",
        "Cookie: ". $coki,
        "User-Agent: ". $ua,
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language: en-US,en;q=0.9"
    ];

    $b = [
        "Host: ourcoincash.xyz",
        "Content-Type: application/x-www-form-urlencoded",
        "Upgrade-Insecure-Requests: 1",
        "Cookie: ". $coki,
        "User-Agent: ". $ua,
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Referer: " . host . "/ptc/view/",  // Referer dynamic nanti diisi
        "Accept-Language: en-US,en;q=0.9",
        "Origin: " . host
    ];
}

function fetch_ptc_list($headers) {
    $url = host . "/ptc";
    $html = requests($url, "GET", [], $headers);
    if (!$html) return [];
    
    $ptc_ads = [];
    preg_match_all('/href="https:\/\/ourcoincash\.xyz\/ptc\/view\/(\d+)".*?View Ad/is', $html, $link_matches);
    preg_match_all('/card-title mb-0.*?>(.*?)<\/h5/is', $html, $title_matches);
    preg_match_all('/fa-gift mr-1"><\/i>([\d,\.]+)\s*coins/s', $html, $coin_matches);
    preg_match_all('/fa-stopwatch mr-1"><\/i>(\d+)s/s', $html, $time_matches);

    if (!empty($link_matches[1])) {
        for ($i = 0; $i < count($link_matches[1]); $i++) {
            $ptc_ads[] = [
                'id'    => $link_matches[1][$i],
                'title' => trim($title_matches[1][$i] ?? 'Unknown'),
                'coins' => trim($coin_matches[1][$i] ?? '0'),
                'time'  => (int)($time_matches[1][$i] ?? 10)
            ];
        }
    }
    return $ptc_ads;
}

// ============================================================
// CLAIM PTC - PAKE 1 SESSION UTUH
// ============================================================
function claim_ptc($ad, $a, $b, $config) {
    global $coki, $ua;
    
    // ============================================================
    // STEP 1: BUKA HALAMAN VIEW (bikin session + token)
    // ============================================================
    $view_url = host . "/ptc/view/" . $ad['id'];
    
    // Set referer khusus untuk view
    $b_view = $b;
    $b_view[7] = "Referer: " . host . "/ptc";
    
    $page = requests($view_url, "GET", [], $a);
    
    if (!$page || strpos($page, "Just a moment") !== false) {
        return "CLOUDFLARE";
    }
    
    // Cek sudah di-claim
    if (strpos($page, "Already Claimed") !== false || 
        strpos($page, "already claimed") !== false || 
        strpos($page, "already viewed") !== false) {
        return "CLAIMED";
    }
    
    // Cek shortlink
    if (strpos($page, "view-ads") !== false || strpos($page, "Complete the captcha") !== false) {
        return "SHORTLINK";
    }
    
    // ============================================================
    // STEP 2: EXTRACT TOKEN DARI HALAMAN VIEW
    // ============================================================
    $csrf = '';
    $token = '';
    preg_match('/name="csrf_token_name".*?value="([^"]+)"/', $page, $csrf_match);
    $csrf = $csrf_match[1] ?? '';
    preg_match('/name="token".*?value="([^"]+)"/', $page, $token_match);
    $token = $token_match[1] ?? '';
    
    if (empty($csrf) || empty($token)) {
        // Coba pake regex alternatif
        preg_match('/csrf_token_name" value="([^"]+)"/', $page, $csrf_match2);
        $csrf = $csrf_match2[1] ?? '';
        preg_match('/token" value="([^"]+)"/', $page, $token_match2);
        $token = $token_match2[1] ?? '';
    }
    
    if (empty($csrf) || empty($token)) {
        return "NO_TOKEN";
    }
    
    // ============================================================
    // STEP 3: TUNGGU COUNTDOWN (sesuai waktu iklan)
    // ============================================================
    $wait = $ad['time'];
    echo putih . "[Wait] " . kuning . $wait . " detik...\n" . reset;
    timer($wait, "⏳ PTC wait");
    
    // ============================================================
    // STEP 4: POST VERIFY DENGAN SESSION YANG SAMA
    // ============================================================
    $verify_url = host . "/ptc/verify/" . $ad['id'];
    
    // Set referer ke halaman view
    $b_verify = $b;
    $b_verify[7] = "Referer: " . $view_url;
    
    $post_data = http_build_query([
        'csrf_token_name' => $csrf,
        'token'           => $token,
    ]);
    
    $claim = requests($verify_url, "POST", $post_data, $b_verify);
    
    if (strpos($claim, "Just a moment") !== false) {
        return "CLOUDFLARE";
    }
    
    // ============================================================
    // STEP 5: CEK HASIL
    // ============================================================
    if (preg_match("/title:\s*'Good job!',\s*text:\s*'([^']+)'/is", $claim, $win) ||
        preg_match("/Swal\.fire\('Good job!',\s*'([^']+)'/is", $claim, $win)) {
        return ["success" => $win[1]];
    }
    
    if (preg_match('/alert-danger">.*?<\/i>\s*([^<]+)/s', $claim, $fail)) {
        return ["failed" => trim($fail[1])];
    }
    
    if (strpos($claim, "Successfully") !== false || strpos($claim, "successfully") !== false) {
        return ["success" => "PTC claim berhasil!"];
    }
    
    if (strpos($claim, "Invalid Click") !== false) {
        return "INVALID_CLICK";
    }
    
    return false;
}

// ============================================================
// MAIN
// ============================================================
home:
clear();

banner();

$config = getConfig();
$coki = $config['cookie'];
$ua = $config['user_agent'];

allheaders($a, $b, $coki, $ua);

$dash = requests(host . "/dashboard", "GET", [], $a);
if (strpos($dash, "Dashboard | Ourcoincash") === false) {
    echo merah . "❌ Login expired! Hapus config dan login ulang.\n" . reset;
    @unlink($configFile);
    sleep(3);
    goto home;
}

preg_match('/<p class="acc-amount">.*?<\/i>\s*([\d,.]+)/', $dash, $balances);
$balance = $balances[1] ?? '0';
preg_match('/Energy.*?<i class="fas fa-bolt"><\/i>\s*([\d,.]+)/is', $dash, $energy_matches);
$energy = $energy_matches[1] ?? '0';

echo putih . "\n";
echo cyan . "╔═══════════════════════════════════════╗\n";
echo cyan . "║" . putih . "        " . cyan . "AUTO PTC - FREE MODE" . putih . "         " . cyan . "║\n";
echo cyan . "╠═══════════════════════════════════════╣\n";
echo cyan . "║" . putih . "  💰 Balance : " . TEAL . $balance . putih . str_repeat(" ", 15 - strlen($balance)) . cyan . "║\n";
echo cyan . "║" . putih . "  ⚡ Energy  : " . hijau . $energy . putih . str_repeat(" ", 15 - strlen($energy)) . cyan . "║\n";
echo cyan . "╚═══════════════════════════════════════╝\n\n";

echo putih . "  " . hijau . "[1]" . putih . " ▶ Start Auto PTC          " . "\n";
echo putih . "  " . TEAL . "[2]" . putih . " 🔄 Cek Balance            " . "\n";
echo putih . "  " . ORANGE . "[3]" . putih . " 🔄 Reset Config           " . "\n";
echo putih . "  " . RED2 . "[0]" . putih . " ❌ Exit                   " . "\n\n";
echo putih . "❯ Pilih: " . GOLD;
$pilih = trim(fgets(STDIN));

if ($pilih == '3') {
    @unlink($configFile);
    echo hijau . "✅ Config direset!\n" . reset;
    sleep(2);
    goto home;
}
if ($pilih == '2') {
    echo putih . "💰 Balance: " . TEAL . $balance . "\n" . reset;
    echo putih . "⚡ Energy : " . hijau . $energy . "\n" . reset;
    echo putih . "\nTekan Enter...";
    trim(fgets(STDIN));
    goto home;
}
if ($pilih == '0') {
    echo putih . "👋 Bye!\n" . reset;
    exit;
}
if ($pilih != '1') {
    goto home;
}

echo putih . "\n🚀 Starting auto PTC...\n" . reset;
echo putih . "Press Ctrl+C to stop\n\n" . reset;

$cycle = 0;
while (true) {
    $cycle++;
    echo cyan . "╔═══════════════════════════════════════╗\n";
    echo cyan . "║" . putih . "  " . GOLD . "CYCLE #" . $cycle . putih . str_repeat(" ", 30 - strlen($cycle)) . cyan . "║\n";
    echo cyan . "╚═══════════════════════════════════════╝\n";
    
    $ptc_ads = fetch_ptc_list($a);
    if (empty($ptc_ads)) {
        echo kuning . "⚠️ Tidak ada PTC ads tersedia!\n" . reset;
        timer(30);
        continue;
    }
    
    echo putih . "Ditemukan " . hijau . count($ptc_ads) . putih . " PTC ads\n";
    
    foreach ($ptc_ads as $ad) {
        echo putih . "\n[PTC] " . TEAL . $ad['title'] . putih . " (" . hijau . $ad['coins'] . " coins" . putih . ")\n";
        
        $result = claim_ptc($ad, $a, $b, $config);
        
        if ($result === "CLOUDFLARE") {
            echo merah . "☁️ Cloudflare terdeteksi! Skip...\n" . reset;
            sleep(3);
            continue;
        } elseif ($result === "CLAIMED") {
            echo kuning . "⏳ Sudah diklaim sebelumnya\n" . reset;
        } elseif ($result === "SHORTLINK") {
            echo kuning . "🔗 Shortlink/captcha, skip...\n" . reset;
        } elseif ($result === "NO_TOKEN") {
            echo merah . "❌ Gagal extract token!\n" . reset;
        } elseif ($result === "INVALID_CLICK") {
            echo merah . "❌ Invalid Click - Coba lagi nanti...\n" . reset;
        } elseif (is_array($result) && isset($result["success"])) {
            echo hijau . "✅ " . $result["success"] . "\n" . reset;
        } elseif (is_array($result) && isset($result["failed"])) {
            echo merah . "❌ " . $result["failed"] . "\n" . reset;
        } else {
            echo kuning . "⚠️ Unknown response\n" . reset;
        }
        
        sleep(2);
    }
    
    echo putih . "\n✅ Siklus selesai. Menunggu PTC baru...\n" . reset;
    timer(30);
}