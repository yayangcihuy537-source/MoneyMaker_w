<?php
error_reporting(0);
date_default_timezone_set('Asia/Jakarta');

$configFile = "configsatvot.json";
$cookieFile = "session/sv_cookievots.txt";
$proxy      = '';

if (!is_dir('session')) mkdir('session', 0777, true);

const R  = "\033[0;31m";
const G  = "\033[0;32m";
const Y  = "\033[0;33m";
const CY = "\033[0;36m";
const W  = "\033[0;37m";
const X  = "\033[0m";

const HOST            = "https://satvoy.com";
const SITEKEY         = "0x4AAAAAAEA7ycZKLPCGQTTH";
const DEF_UA          = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36";
const SCRIPT_NAME     = "SATVOY.COM";

// ==================== SOLVER ENDPOINTS ====================
const TERTUYUL_IN     = "http://api.tertuyul.my.id/in.php";
const TERTUYUL_RES    = "http://api.tertuyul.my.id/res.php";
const WARYONO_IN      = "https://api.waryono.my.id/in.php";
const WARYONO_RES     = "https://api.waryono.my.id/res.php";
const SKIPCHA_IN      = "https://skipcha.online/in.php";
const SKIPCHA_RES     = "https://skipcha.online/res.php";

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
function parseProxy($s){
    if (empty($s)) return null;
    $s = trim($s);
    if (strpos($s,'[')===0){
        if (preg_match('/^\[([^\]]+)\]:(\d+):([^:]+):(.+)$/',$s,$m)) return ['host'=>'['.$m[1].']','port'=>$m[2],'user'=>$m[3],'pass'=>$m[4]];
        if (preg_match('/^\[([^\]]+)\]:(\d+)$/',$s,$m)) return ['host'=>'['.$m[1].']','port'=>$m[2],'user'=>null,'pass'=>null];
        return null;
    }
    $p = explode(':',$s);
    if (count($p)===4) return ['host'=>$p[0],'port'=>$p[1],'user'=>$p[2],'pass'=>$p[3]];
    if (count($p)===2) return ['host'=>$p[0],'port'=>$p[1],'user'=>null,'pass'=>null];
    return null;
}
function applyProxy(&$opts){
    global $proxy;
    if (empty($proxy)) return;
    $p = parseProxy($proxy); if (!$p) return;
    $opts[CURLOPT_PROXY]     = $p['host'].':'.$p['port'];
    $opts[CURLOPT_PROXYTYPE] = CURLPROXY_SOCKS5_HOSTNAME;
    if ($p['user']!==null) $opts[CURLOPT_PROXYUSERPWD] = $p['user'].':'.$p['pass'];
}
function req($url, $method='GET', $data=null, $headers=[], $use_proxy=true, $json=false, $cookiejar=null){
    global $cookieFile;
    $jar = $cookiejar ?: $cookieFile;
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
        CURLOPT_COOKIEFILE     => $jar,
        CURLOPT_COOKIEJAR      => $jar,
    ];
    if ($use_proxy) applyProxy($opts);
    if ($method==='POST'){
        $opts[CURLOPT_POST] = true;
        if ($json){
            $opts[CURLOPT_POSTFIELDS] = is_string($data) ? $data : json_encode($data);
        } else {
            $opts[CURLOPT_POSTFIELDS] = is_array($data) ? http_build_query($data) : $data;
        }
    }
    curl_setopt_array($ch, $opts);
    $resp = curl_exec($ch);
    if ($resp === false){ @curl_close($ch); return null; }
    $hs   = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
    $body = substr($resp, $hs);
    @curl_close($ch);
    return $body;
}
function curl_plain($url, $method='GET', $data=null, $headers=[], $json=false){
    $ch = curl_init();
    $opts = [
        CURLOPT_URL            => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT        => 30,
        CURLOPT_CONNECTTIMEOUT => 15,
    ];
    if (!empty($headers)) $opts[CURLOPT_HTTPHEADER] = $headers;
    if ($method==='POST'){
        $opts[CURLOPT_POST] = true;
        if ($json){
            $opts[CURLOPT_POSTFIELDS] = is_string($data) ? $data : json_encode($data);
        } else {
            $opts[CURLOPT_POSTFIELDS] = is_array($data) ? http_build_query($data) : $data;
        }
    }
    curl_setopt_array($ch, $opts);
    $r = curl_exec($ch); @curl_close($ch); return $r;
}

// ==================== SOLVER: TERTUYUL ====================
function solve_tertuyul($apikey, $pageurl){
    $post = ['key'=>$apikey,'method'=>'turnstile','sitekey'=>SITEKEY,'pageurl'=>$pageurl,'json'=>'1'];
    $resp = curl_plain(TERTUYUL_IN,'POST',http_build_query($post));
    $task = json_decode($resp,true);
    if (($task['status']??0)!=1){
        $err = $task['request']??'SUBMIT_ERROR';
        if (in_array($err,['ERROR_WRONG_USER_KEY','ERROR_KEY_DOES_NOT_EXIST','ERROR_ZERO_BALANCE'])){
            echo W."[TERTUYUL] ".R.$err." (FATAL)".X."\n"; exit;
        }
        if (in_array($err,['ERROR_TOO_MANY_REQUESTS','ERROR_SOLVE_PENDING','ERROR_NO_SLOT_AVAILABLE','ERROR_REQUEST_COOLDOWN'])){
            sleep(5); return solve_tertuyul($apikey,$pageurl);
        }
        return null;
    }
    $tid = $task['request'];
    $tries = 0;
    while ($tries < 40){
        $tries++;
        timer(3,"Tertuyul");
        $p = ['key'=>$apikey,'action'=>'get','id'=>$tid,'json'=>'1'];
        $r = curl_plain(TERTUYUL_RES,'POST',http_build_query($p));
        $res = json_decode($r,true);
        if (($res['status']??0)==1) return $res['request'];
        $req = $res['request']??'';
        if ($req === 'CAPCHA_NOT_READY') continue;
        if (in_array($req,['ERROR_TOO_MANY_REQUESTS','ERROR_SOLVE_PENDING','ERROR_NO_SLOT_AVAILABLE','ERROR_REQUEST_COOLDOWN','ERROR_CAPTCHA_UNSOLVABLE','ERROR_INTERNAL_SERVER','ERROR_PROXY_CONNECTION_FAILED'])){
            sleep(3); return solve_tertuyul($apikey,$pageurl);
        }
        if (in_array($req,['ERROR_WRONG_USER_KEY','ERROR_KEY_DOES_NOT_EXIST','ERROR_ZERO_BALANCE'])){
            echo W."[TERTUYUL] ".R.$req." (FATAL)".X."\n"; exit;
        }
        sleep(3); return solve_tertuyul($apikey,$pageurl);
    }
    return null;
}

// ==================== SOLVER: WARYONO (SKIBIDIXXX) ====================
function solve_waryono($apikey, $pageurl){
    $payload = [
        'apikey'  => $apikey,
        'methods' => 'turnstile',
        'domain'  => $pageurl,
        'sitekey' => SITEKEY,
        'action'  => 'login',
        'cdata'   => 'session_'.bin2hex(random_bytes(4)),
    ];
    $resp = curl_plain(WARYONO_IN, 'POST', json_encode($payload),
        ['Content-Type: application/json'], true);

    $task = json_decode($resp, true);
    $taskId = null;

    if (is_array($task) && isset($task['status']) && (int)$task['status'] === 1){
        $taskId = $task['request'];
    } elseif (is_string($resp) && strpos($resp, 'OK|') === 0){
        $taskId = trim(substr($resp, 3));
    }

    if (!$taskId){
        $err = is_array($task) ? ($task['request'] ?? 'SUBMIT_ERROR') : trim($resp);
        if (stripos($err,'balance') !== false || stripos($err,'key') !== false){
            echo W."[WARYONO] ".R.$err." (FATAL)".X."\n"; exit;
        }
        sleep(5); return solve_waryono($apikey,$pageurl);
    }

    $tries = 0;
    while ($tries < 40){
        $tries++;
        timer(3, "Waryono");
        $pollUrl = WARYONO_RES.'?'.http_build_query([
            'key'    => $apikey,
            'action' => 'get',
            'id'     => $taskId,
        ]);
        $r = curl_plain($pollUrl, 'GET');
        $res = json_decode($r, true);

        if (is_array($res) && isset($res['status']) && (int)$res['status'] === 1){
            return $res['request'];
        }
        $msg = is_array($res) ? ($res['request'] ?? '') : trim($r);
        if (stripos($msg, 'NOT_READY') !== false || stripos($msg, 'CAPCHA_NOT_READY') !== false) continue;
        if (stripos($msg,'UNSOLVABLE') !== false || stripos($msg,'ERROR_INTERNAL') !== false){
            sleep(3); return solve_waryono($apikey,$pageurl);
        }
        if (stripos($msg,'balance') !== false || stripos($msg,'WRONG_USER') !== false){
            echo W."[WARYONO] ".R.$msg." (FATAL)".X."\n"; exit;
        }
        sleep(3); return solve_waryono($apikey,$pageurl);
    }
    return null;
}

// ==================== SOLVER: SKIPCHA ====================
function solve_skipcha($apikey, $pageurl){
    $inUrl = SKIPCHA_IN.'?'.http_build_query([
        'key'     => $apikey,
        'method'  => 'turnstile',
        'sitekey' => SITEKEY,
        'pageurl' => $pageurl,
        'json'    => 1,
    ]);
    $resp = curl_plain($inUrl, 'GET');
    $task = json_decode($resp, true);

    if (!is_array($task) || empty($task['request'])){
        $err = is_array($task) ? ($task['request'] ?? 'SUBMIT_ERROR') : trim($resp);
        if (stripos($err,'balance') !== false || stripos($err,'key') !== false){
            echo W."[SKIPCHA] ".R.$err." (FATAL)".X."\n"; exit;
        }
        sleep(5); return solve_skipcha($apikey,$pageurl);
    }

    $taskId = $task['request'];
    $tries = 0;
    while ($tries < 40){
        $tries++;
        timer(3, "Skipcha");
        $pollUrl = SKIPCHA_RES.'?'.http_build_query([
            'key'    => $apikey,
            'action' => 'get',
            'id'     => $taskId,
            'json'   => 1,
        ]);
        $r = curl_plain($pollUrl, 'GET');
        $res = json_decode($r, true);

        if (is_array($res) && isset($res['status']) && (int)$res['status'] === 1){
            return $res['request'];
        }
        $msg = is_array($res) ? ($res['request'] ?? '') : trim($r);
        if (stripos($msg,'NOT_READY') !== false || stripos($msg,'CAPCHA_NOT_READY') !== false) continue;
        if (stripos($msg,'UNSOLVABLE') !== false || stripos($msg,'ERROR_INTERNAL') !== false){
            sleep(3); return solve_skipcha($apikey,$pageurl);
        }
        if (stripos($msg,'balance') !== false || stripos($msg,'WRONG_USER') !== false){
            echo W."[SKIPCHA] ".R.$msg." (FATAL)".X."\n"; exit;
        }
        sleep(3); return solve_skipcha($apikey,$pageurl);
    }
    return null;
}

// ==================== SOLVER DISPATCHER ====================
function solve_turnstile($apikey, $pageurl){
    global $solver;
    switch ($solver){
        case 'waryono': return solve_waryono($apikey, $pageurl);
        case 'skipcha': return solve_skipcha($apikey, $pageurl);
        case 'tertuyul':
        default:        return solve_tertuyul($apikey, $pageurl);
    }
}

// ==================== HTML PARSERS ====================
function get_meta_csrf($html){
    if (preg_match('/<meta\s+name="csrf-token"\s+content="([^"]+)"/i',$html,$m)) return $m[1];
    return null;
}
function get_form_token($html){
    if (preg_match('/<input\s+type="hidden"\s+name="_token"\s+value="([^"]+)"/i',$html,$m)) return $m[1];
    return null;
}
function is_logged_in($html){
    return strpos($html,'Log out') !== false || strpos($html,'Dashboard | satvoy') !== false;
}
function get_balance_from_page($html){
    if (preg_match('/data-balance[^>]*>([\d.]+)</',$html,$m)) return (float)$m[1];
    return null;
}
function get_ptc_ads($html){
    preg_match_all('#<form\s+method="POST"\s+action="/ptc/(\d+)/open"#i',$html,$m);
    return array_values(array_unique($m[1] ?? []));
}
function get_ptc_view_data($html){
    if (preg_match('/x-data="ptcView\((\d+),\s*\'([^\']+)\',\s*(true|false),\s*\'([^\']*)\'\)"/i',$html,$m)){
        return ['duration'=>(int)$m[1],'token'=>$m[2],'is_frame'=>($m[3]==='true'),'url'=>$m[4]];
    }
    return null;
}
function get_faucet_data($html){
    $data = ['token'=>null,'k'=>null,'amount'=>null,'cooldown'=>0,'ready'=>false];
    if (preg_match('/claimWait\((\d+),\s*(\d+)\)/',$html,$m)){
        $data['cooldown'] = (int)$m[1]; return $data;
    }
    if (preg_match('/claimFlow\(\'([^\']+)\',\s*(\d+)\)/i',$html,$m)){
        $data['token'] = $m[1]; $data['ready'] = true;
    }
    if (preg_match_all('/data-k="([^"]+)"/',$html,$matches)){
        if (!empty($matches[1])) $data['k'] = end($matches[1]);
    }
    if (preg_match('/YOU WILL RECEIVE.*?disp text-\[54px\][^>]*>\s*([\d.]+)/s',$html,$m)) $data['amount'] = (float)$m[1];
    else if (preg_match('/disp text-\[54px\][^>]*>\s*([\d.]+)/',$html,$m)) $data['amount'] = (float)$m[1];
    return $data;
}
function get_mining_ready($html){
    if (preg_match('/READY TO CLAIM.*?disp text-\[38px\][^>]*>\s*([\d.]+)/s',$html,$m)) return (float)$m[1];
    if (preg_match('/READY TO CLAIM.{0,600}?>\s*([\d.]+)\s*</s',$html,$m)) return (float)$m[1];
    return 0.0;
}
function gen_fp(){
    $c='abcdefghijklmnopqrstuvwxyz0123456789';
    $g=function($l) use ($c){ $s=''; for($i=0;$i<$l;$i++) $s.=$c[random_int(0,strlen($c)-1)]; return $s; };
    return ['fp'=>$g(12),'canvas'=>$g(7),'webgl'=>$g(7),'audio'=>$g(6),'font'=>$g(6),
        'signals'=>['ua'=>DEF_UA,'lang'=>'id-ID','langs'=>'id-ID,id,en-US,en','platform'=>'Linux armv81','cores'=>8,'mem'=>8,'touch'=>5,'screen'=>'407x904x24','avail'=>'407x904','dpr'=>2.698957920074463,'tz'=>'Asia/Jakarta','tzoff'=>-420,'plugins'=>0,'gl_vendor'=>'Google Inc. (ARM)','gl_renderer'=>'ANGLE (ARM, Mali-G615 MC6, OpenGL ES 3.2)','fonts'=>7,'cookie'=>1,'dnt'=>'','pdf'=>0],
        'automation'=>[]];
}

// ==================== LOGIN ====================
function do_login($email, $password, $apikey){
    global $solver;
    log_msg("Login: ".maskEmail($email)." [solver: $solver]",'info');
    $h0 = ["user-agent:".DEF_UA,"accept-language:id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"];
    $html = req(HOST.'/login','GET',null,$h0);
    if (!$html){ log_msg("Gagal load /login",'error'); return false; }
    $token = get_form_token($html);
    if (!$token){ log_msg("_token tidak ketemu",'error'); return false; }

    $ts = null;
    for ($i=1;$i<=5;$i++){ $ts = solve_turnstile($apikey, HOST.'/login'); if ($ts) break; sleep(3); }
    if (!$ts){ log_msg("Turnstile gagal",'error'); return false; }

    $body = ['_token'=>$token,'email'=>$email,'password'=>$password,'remember'=>'on','cf-turnstile-response'=>$ts];
    $h = array_merge($h0,["content-type:application/x-www-form-urlencoded","origin:".HOST,"referer:".HOST."/login"]);
    $resp = req(HOST.'/login','POST',$body,$h);
    if (!$resp){ log_msg("Login gagal",'error'); return false; }

    if (is_logged_in($resp)){ log_msg("Login OK!",'success'); return $resp; }
    $dash = req(HOST.'/dashboard','GET',null,$h0);
    if ($dash && is_logged_in($dash)){ log_msg("Login OK!",'success'); return $dash; }
    log_msg("Login gagal",'error'); return false;
}

function get_balance($csrf){
    $h = ["user-agent:".DEF_UA,"accept:application/json","referer:".HOST."/dashboard","x-csrf-token:".$csrf];
    $r = req(HOST.'/bal','GET',null,$h);
    if ($r){ $j=json_decode($r,true); if (isset($j['c'])) return (float)$j['c']; }
    $dash = req(HOST.'/dashboard','GET',null,["user-agent:".DEF_UA]);
    return get_balance_from_page($dash);
}

// ==================== PTC ====================
function claim_ptc($ad_id, $csrf, $apikey){
    $base_h = ["user-agent:".DEF_UA,"accept-language:id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"];
    $open_h = array_merge($base_h,["content-type:application/x-www-form-urlencoded","origin:".HOST,"referer:".HOST."/ptc"]);
    $html = req(HOST."/ptc/{$ad_id}/open",'POST',['_token'=>$csrf],$open_h);
    if (!$html){ log_msg("Ad #$ad_id: gagal buka",'error'); return null; }

    $data = get_ptc_view_data($html);
    if (!$data){ log_msg("Ad #$ad_id: token tidak ketemu",'error'); return null; }

    $duration = $data['duration'];
    $tok = $data['token'];
    $is_frame = $data['is_frame'];
    $csrf2 = get_meta_csrf($html) ?: $csrf;

    log_msg("Ad #$ad_id: durasi {$duration}s",'info');

    $ts = null;
    for ($i=1;$i<=5;$i++){ $ts = solve_turnstile($apikey, HOST."/ptc/{$ad_id}/open"); if ($ts) break; sleep(3); }
    if (!$ts){ log_msg("Ad #$ad_id: turnstile gagal",'error'); return null; }

    $wait = $duration + random_int(1,3);
    timer($wait,"Ad #$ad_id");

    $fp = gen_fp();
    $beat_h = array_merge($base_h,["content-type:application/json","accept:application/json","origin:".HOST,"referer:".HOST."/ptc/{$ad_id}/open","x-csrf-token:".$csrf2]);
    req(HOST.'/ptc/beat','POST',['token'=>$tok,'fp_hash'=>$fp['fp']],$beat_h,true,true);

    $beh = ['page_time_ms'=>($wait*1000)+random_int(200,900),'mouse_moves'=>random_int(2,8),'touch_events'=>random_int(2,6),'key_events'=>0,'scroll_events'=>0,'tab_focused'=>true,'step_gaps'=>[],'jitter'=>0];
    $payload = ['token'=>$tok,'fp'=>$fp,'behavior'=>$beh,'focus_seconds'=>$duration,'mode'=>$is_frame?'iframe':'window','claim_delay_ms'=>random_int(2000,5000),'cf_token'=>$ts];
    $resp = req(HOST.'/ptc/complete','POST',$payload,$beat_h,true,true);
    if (!$resp){ log_msg("Ad #$ad_id: complete gagal",'error'); return null; }

    $j = json_decode($resp,true);
    if ($j && !empty($j['ok'])){
        log_msg("Ad #$ad_id OK: ".($j['message'] ?? '+'.($j['reward'] ?? '?').' coins'),'success');
        return $j;
    }
    log_msg("Ad #$ad_id gagal: ".json_encode($j),'error');
    return null;
}

function handle_task_gate($csrf, $apikey, $max_rounds = 2){
    $h = ["user-agent:".DEF_UA,"accept-language:id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"];
    for ($round = 1; $round <= $max_rounds; $round++){
        log_msg("Task gate: round $round/$max_rounds (PTC only)",'info');
        $ptc_html = req(HOST.'/ptc','GET',null,$h);
        if (!$ptc_html){ log_msg("Task gate: gagal load /ptc",'error'); return false; }
        $ptc_ids = get_ptc_ads($ptc_html);
        log_msg("Task gate: ".count($ptc_ids)." PTC tersedia",'info');
        if (empty($ptc_ids)){
            log_msg("Task gate: tidak ada PTC",'warn');
            if ($round < $max_rounds) timer(8,"Gate CD");
            continue;
        }
        foreach ($ptc_ids as $id){
            $r = claim_ptc($id, $csrf, $apikey);
            if ($r && !empty($r['ok'])){
                log_msg("Task gate: SELESAI via PTC #$id",'success');
                return true;
            }
        }
        if ($round < $max_rounds) timer(8,"Gate CD");
    }
    log_msg("Task gate: gagal semua, skip",'warn');
    return false;
}

// ==================== FAUCET ====================
function claim_faucet($csrf, $apikey, $max_claims = 0, $max_cooldown = 300){
    $h = ["user-agent:".DEF_UA,"accept-language:id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"];
    $total_claimed = 0; $total_coins = 0;

    while (true){
        if ($max_claims > 0 && $total_claimed >= $max_claims) break;

        $html = req(HOST.'/claim','GET',null,$h);
        if (!$html){ log_msg("Faucet: gagal load /claim",'error'); break; }

        $data = get_faucet_data($html);

        if ($data['cooldown'] > 0){
            if ($data['cooldown'] > $max_cooldown){
                log_msg("Faucet: cooldown ".$data['cooldown']."s → TASK GATE (PTC only)",'warn');
                $gate_ok = handle_task_gate($csrf, $apikey, 2);
                if ($gate_ok){
                    $d = req(HOST.'/claim','GET',null,$h);
                    $nc = get_meta_csrf($d); if ($nc) $csrf = $nc;
                    sleep(5); continue;
                }
                break;
            }
            timer($data['cooldown'] + 2, "Faucet CD"); continue;
        }

        if (!$data['ready'] || !$data['token'] || !$data['k']){
            log_msg("Faucet: page tidak ready",'warn'); sleep(3); continue;
        }

        log_msg("Faucet #".($total_claimed+1).": ~".$data['amount']." coins",'info');
        $csrf2 = get_meta_csrf($html) ?: $csrf;
        $h_json = ["user-agent:".DEF_UA,"accept:application/json","content-type:application/json","origin:".HOST,"referer:".HOST."/claim","x-csrf-token:".$csrf2];

        $r = req(HOST.'/claim/adblock','POST',['token'=>$data['token'],'clean'=>true,'methods'=>[],'brave'=>false],$h_json,true,true);
        $j = json_decode($r,true);
        if (empty($j['ok'])){ log_msg("Faucet: adblock gagal",'error'); sleep(3); continue; }

        $ok = true;
        foreach ([1,2,3] as $n){
            sleep(random_int(1,3));
            $r = req(HOST.'/claim/step','POST',['token'=>$data['token'],'n'=>$n],$h_json,true,true);
            $j = json_decode($r,true);
            if (empty($j['ok'])){ log_msg("Faucet: step $n gagal",'error'); $ok=false; break; }
        }
        if (!$ok){ sleep(3); continue; }

        $ts = null;
        for ($i=1;$i<=5;$i++){ $ts = solve_turnstile($apikey, HOST.'/claim'); if ($ts) break; sleep(3); }
        if (!$ts){ log_msg("Faucet: turnstile gagal",'error'); sleep(3); continue; }

        $r = req(HOST.'/claim/captcha','POST',['token'=>$data['token'],'cf_token'=>$ts],$h_json,true,true);
        $j = json_decode($r,true);
        if (empty($j['ok'])){ log_msg("Faucet: captcha gagal",'error'); sleep(3); continue; }

        sleep(random_int(1,2));
        $fp = gen_fp();
        $beh = ['page_time_ms'=>random_int(15000,30000),'mouse_moves'=>random_int(3,10),'touch_events'=>random_int(20,40),'key_events'=>0,'scroll_events'=>random_int(50,120),'tab_focused'=>true,'step_gaps'=>[random_int(1000,2000),random_int(1000,2000),random_int(1000,2000)],'jitter'=>0];
        $payload = ['token'=>$data['token'],'fp'=>$fp,'behavior'=>$beh,'k'=>$data['k'],'cg_id'=>'','cg_taps'=>''];
        $r = req(HOST.'/claim','POST',$payload,$h_json,true,true);
        $j = json_decode($r,true);

        if (!$j){ log_msg("Faucet: response invalid",'error'); sleep(3); continue; }

        if (!empty($j['ok'])){
            $total_claimed++;
            $reward = (float)($data['amount'] ?? 0);
            $total_coins += $reward;
            log_msg("Faucet #$total_claimed OK: +".$reward." coins",'success');
            $nb = get_balance($csrf);
            if ($nb !== null){ log_msg("New balance: ".G.$nb.W." coins",'info'); }
            sleep(random_int(3,6)); continue;
        }

        if (!empty($j['taskGate'])){
            log_msg("Faucet: TASK GATE (PTC only)",'warn');
            $gate_ok = handle_task_gate($csrf, $apikey, 2);
            if ($gate_ok){
                $d = req(HOST.'/claim','GET',null,$h);
                $nc = get_meta_csrf($d); if ($nc) $csrf = $nc;
                sleep(5); continue;
            }
            break;
        }

        log_msg("Faucet gagal: ".json_encode($j),'error');
        sleep(5);
        if ($total_claimed > 0) break;
    }

    echo W."-----------------------------------------------\n";
    echo W."Faucet total : ".G.$total_claimed.W." claim\n";
    echo W."Faucet reward: ".G."+".round($total_coins,2).W." coins\n";
    return ['ok'=>true,'claimed'=>$total_claimed,'coins'=>$total_coins];
}

// ==================== MINING ====================
function claim_mining($csrf){
    $h = ["user-agent:".DEF_UA,"accept-language:id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"];
    $html = req(HOST.'/mining','GET',null,$h);
    if (!$html){ log_msg("Mining: gagal load",'error'); return null; }
    $csrf2 = get_meta_csrf($html) ?: $csrf;
    $ready = get_mining_ready($html);
    if ($ready <= 0){ log_msg("Mining: tidak ada yang bisa di-claim",'warn'); return ['ok'=>false]; }
    log_msg("Mining: ready = ".G.$ready.W." coins",'info');
    $h_post = array_merge($h,["content-type:application/x-www-form-urlencoded","origin:".HOST,"referer:".HOST."/mining"]);
    req(HOST.'/mining/claim','POST',['_token'=>$csrf2],$h_post);
    sleep(2);
    log_msg("Mining OK",'success');
    return ['ok'=>true,'claimed'=>$ready];
}

// ==================== UI ====================
function bannerMain(){
    echo W."===============================================\n";
    echo Y."     BOT ".SCRIPT_NAME." (Single Account)\n";
    echo W."===============================================\n";
}
function bannerAccount($email){
    echo W."===============================================\n";
    echo W."Akun : ".CY.maskEmail($email)."\n";
    global $proxy;
    echo W."Proxy: ".CY.(empty($proxy)?"Direct":$proxy)."\n";
    echo W."-----------------------------------------------\n";
}
function saveConfig($f,$d){ file_put_contents($f,json_encode($d,JSON_PRETTY_PRINT)); }

function pickSolver(){
    clear(); bannerMain();
    echo W." PILIH SOLVER CAPTCHA \n";
    echo W."-----------------------------------------------\n";
    echo CY."[1]".W." Tertuyul       (api.tertuyul.my.id)\n";
    echo CY."[2]".W." Waryono        (api.waryono.my.id)\n";
    echo CY."[3]".W." Skipcha.online (skipcha.online)\n";
    echo W."-----------------------------------------------\n";
    echo W."Pilih [1-3]: ".Y;
    $c = trim(fgets(STDIN));
    $map = ['1'=>'tertuyul','2'=>'waryono','3'=>'skipcha'];
    return $map[$c] ?? 'tertuyul';
}

function getConfig($f){
    $d = [];
    if (file_exists($f)) $d = json_decode(file_get_contents($f),true) ?? [];

    $apikey  = $d['apikey']  ?? '';
    $solver  = $d['solver']  ?? '';
    $account = $d['account'] ?? [];

    // Migrasi dari format multi-akun lama
    if (empty($account) && !empty($d['accounts'][0])){
        $account = [
            'email'    => $d['accounts'][0]['email'] ?? '',
            'password' => $d['accounts'][0]['password'] ?? '',
            'proxy'    => $d['accounts'][0]['proxy'] ?? '',
        ];
    }

    if (empty($solver)) $solver = pickSolver();

    if (empty($apikey)){
        clear(); bannerMain();
        echo W."Solver: ".CY.$solver."\n";
        echo W."-----------------------------------------------\n";
        echo W."API Key (untuk solver $solver): ".Y;
        $apikey = trim(fgets(STDIN));
    }

    if (empty($account['email'])){
        clear(); bannerMain();
        echo W."Solver: ".CY.$solver."\n";
        echo W."-----------------------------------------------\n";
        echo W."Email    : ".Y; $e = trim(fgets(STDIN));
        echo W."Password : ".Y; $p = trim(fgets(STDIN));
        echo W."Proxy    : ".Y; $pr = trim(fgets(STDIN));
        $account = ['email'=>$e,'password'=>$p,'proxy'=>$pr];
    }

    $cfg = ['apikey'=>$apikey,'solver'=>$solver,'account'=>$account];
    saveConfig($f,$cfg);
    return $cfg;
}

function editAccount(&$cfg,$f){
    clear(); bannerMain();
    echo W." EDIT AKUN \n\n";
    $a = $cfg['account'];
    echo W."Email baru (Enter = biarkan): ".Y; $e = trim(fgets(STDIN));
    echo W."Password baru (Enter = biarkan): ".Y; $p = trim(fgets(STDIN));
    echo W."Proxy baru (Enter = biarkan, '-' = kosongkan): ".Y; $pr = trim(fgets(STDIN));

    if ($e !== '') $a['email'] = $e;
    if ($p !== '') $a['password'] = $p;
    if ($pr === '-') $a['proxy'] = '';
    elseif ($pr !== '') $a['proxy'] = $pr;

    $cfg['account'] = $a;
    saveConfig($f,$cfg);
    echo G."\n✓ Config disimpan.\n"; sleep(2);
}

function changeSolver(&$cfg,$f){
    $new = pickSolver();
    $cfg['solver'] = $new;
    saveConfig($f,$cfg);
    echo G."\n✓ Solver diubah ke: $new\n"; sleep(2);
}

function changeApiKey(&$cfg,$f){
    clear(); bannerMain();
    echo W."API Key baru (Enter = biarkan): ".Y;
    $k = trim(fgets(STDIN));
    if ($k !== ''){
        $cfg['apikey'] = $k;
        saveConfig($f,$cfg);
        echo G."\n✓ API key disimpan.\n";
    }
    sleep(2);
}

// ==================== PROCESS ====================
function processAccount($acc, $apikey, $mode='ptc'){
    global $proxy, $cookieFile;
    $proxy      = $acc['proxy'] ?? '';
    $cookieFile = "session/sv_cookies.txt";

    $headers = ["user-agent:".DEF_UA];
    bannerAccount($acc['email']);

    $dash = req(HOST.'/dashboard','GET',null,$headers);
    if (!$dash || !is_logged_in($dash)){
        log_msg("Session expired, login ulang…",'warn');
        $dash = do_login($acc['email'],$acc['password'],$apikey);
        if (!$dash){ log_msg("Skip.",'warn'); return; }
    } else { log_msg("Session valid ✓",'success'); }

    $csrf = get_meta_csrf($dash);
    if (!$csrf){
        $p = req(HOST.'/ptc','GET',null,$headers);
        $csrf = get_meta_csrf($p);
    }
    if (!$csrf){ log_msg("CSRF tidak ketemu, skip.",'error'); return; }

    $bal = get_balance($csrf);
    log_msg("Balance: ".(($bal!==null)?G.$bal.W." coins":R."gagal"), 'info');
    if ($mode === 'balance') return;

    if ($mode === 'faucet'){
        log_msg("[MODE] Auto Faucet (+ Task Gate PTC)",'info');
        claim_faucet($csrf, $apikey, 0, 300);
    }
    if ($mode === 'mining'){
        log_msg("[MODE] Mining",'info');
        claim_mining($csrf);
    }
    if ($mode === 'ptc'){
        log_msg("[MODE] PTC Ads",'info');
        $ptc_html = req(HOST.'/ptc','GET',null,$headers);
        if ($ptc_html){
            $ptc_ids = get_ptc_ads($ptc_html);
            $claimed = 0; $failed = 0; $total_reward = 0;

            foreach ($ptc_ids as $id){
                $r = claim_ptc($id,$csrf,$apikey);
                if ($r && !empty($r['ok'])){
                    $claimed++;
                    $reward = (float)($r['reward'] ?? 0);
                    $total_reward += $reward;
                    $nb = get_balance($csrf);
                    if ($nb !== null){ log_msg("New balance: ".G.$nb.W." coins",'info'); }
                    sleep(random_int(2,5));
                    $d = req(HOST.'/dashboard','GET',null,$headers);
                    $nc = get_meta_csrf($d); if ($nc) $csrf = $nc;
                } else { $failed++; sleep(random_int(2,4)); }
            }

            echo W."-----------------------------------------------\n";
            echo W."PTC Claimed : ".G.$claimed.W." ads";
            if ($failed>0) echo W." (".R.$failed.W." gagal)";
            echo "\nPTC Reward  : ".G."+".round($total_reward,3).W." coins\n";

            $bal_end = get_balance($csrf);
            if ($bal_end !== null) echo W."Final balance: ".G.$bal_end.W." coins\n";
        }
    }

    $bal2 = get_balance($csrf);
    echo W."-----------------------------------------------\n";
    echo W."New balance : ".G.($bal2!==null?$bal2.' coins':'?')."\n";
    echo W."-----------------------------------------------\n";
}

// ==================== MAIN ====================
$cfg = getConfig($configFile);
$apikey = $cfg['apikey'];
$solver = $cfg['solver'] ?? 'tertuyul';
$GLOBALS['apikey'] = $apikey;
$GLOBALS['solver'] = $solver;

$solverNames = ['tertuyul'=>'Tertuyul','waryono'=>'Waryono (Skibidixxx)','skipcha'=>'Skipcha.online'];

while (true){
    clear(); bannerMain();
    echo W."Akun  : ".CY.maskEmail($cfg['account']['email'] ?? '-')."\n";
    echo W."Proxy : ".CY.(empty($cfg['account']['proxy'])?"Direct":$cfg['account']['proxy'])."\n";
    echo W."Solver: ".G.($solverNames[$solver] ?? $solver)."\n";
    echo W."-----------------------------------------------\n";
    echo CY."[1]".W." Cek Balance\n";
    echo CY."[2]".W." Claim PTC\n";
    echo CY."[3]".W." Auto Faucet (+ Task Gate PTC)\n";
    echo CY."[4]".W." Claim Mining (1x)\n";
    echo CY."[5]".G." Edit Akun\n";
    echo CY."[6]".Y." Ganti Solver\n";
    echo CY."[7]".Y." Ganti API Key\n";
    echo CY."[0]".R." Keluar\n";
    echo W."-----------------------------------------------\n";
    echo W."Pilih: ".Y;
    $c = trim(fgets(STDIN));

    if ($c==='0'){ echo W."\nBye bro!\n"; exit; }
    elseif ($c==='5') editAccount($cfg,$configFile);
    elseif ($c==='6'){ changeSolver($cfg,$configFile); $solver = $cfg['solver']; $GLOBALS['solver']=$solver; }
    elseif ($c==='7') changeApiKey($cfg,$configFile);
    elseif (in_array($c,['1','2','3','4'])){
        $acc = $cfg['account'] ?? null;
        if (!$acc || empty($acc['email'])){ echo R."\nAkun belum diisi!\n"; sleep(2); continue; }
        $modeMap = ['1'=>'balance','2'=>'ptc','3'=>'faucet','4'=>'mining'];
        $mode = $modeMap[$c];
        echo "\n".W."Mode: ".G.$mode.W." | Solver: ".CY.$solverNames[$solver]."\n";
        sleep(1);
        processAccount($acc, $cfg['apikey'], $mode);
        echo "\n".W."Tekan Enter..."; fgets(STDIN);
    }
}
