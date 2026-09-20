<?php
/**
 * CryptoFuture Auto Claim — Souu Engine v1.0.4
 * Author: @MoneyMaker_w
 */

define("RED","\033[0;31m"); define("GRN","\033[0;32m");
define("YEL","\033[0;33m"); define("BLU","\033[0;34m");
define("MAG","\033[0;35m"); define("CYN","\033[0;36m");
define("WHT","\033[0;37m"); define("RST","\033[0m");
define("BOLD","\033[1m");

const SITE   = "https://cryptofuture.co.in";
const HOME   = SITE . "/";
const LOGIN  = SITE . "/auth/login";
const EARN   = SITE . "/faucet/earn";
const DASH   = SITE . "/dashboard";

const COOKIE = "cryptofuture.txt";
const CFG    = "cryptofuture.json";

const SOLVER_IN  = "https://api.waryono.my.id/in.php";
const SOLVER_RES = "https://api.waryono.my.id/res.php";

const UA     = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36";

const TOOL_NAME = "AUTO CLAIM";
const DEVELOPER = "@MoneyMaker_w";
const VERSION   = "v1.0.4";
const TELEGRAM  = "t.me/ScriptyXSouu";

const BOX_W = 54;

$STATE = [
    'apikey'  => '',
    'wallet'  => '',
    'balance' => 0.0,
    'next_at' => 0,
    'success' => 0,
    'failed'  => 0,
    'started' => 0,
];

// ═══════════════════════════════════════════════════════════
//  HELPERS
// ═══════════════════════════════════════════════════════════
function vlen($s){ return strlen(preg_replace('/\x1b\[[0-9;]*m/','',$s)); }
function pad($s,$w,$align='left'){
    $p=max(0,$w-vlen($s));
    if($align==='right')  return str_repeat(' ',$p).$s;
    if($align==='center'){ $l=intdiv($p,2); $r=$p-$l; return str_repeat(' ',$l).$s.str_repeat(' ',$r); }
    return $s.str_repeat(' ',$p);
}
function boxTop($title='',$w=BOX_W){
    if($title==='') return CYN.'╭'.str_repeat('─',$w+2).'╮'.RST;
    $t=' '.CYN.BOLD.$title.RST.' ';
    $rest=$w+2-vlen($t);
    return CYN.'╭─'.RST.$t.CYN.str_repeat('─',max(0,$rest)).'╮'.RST;
}
function boxMid($w=BOX_W){ return CYN.'├'.str_repeat('─',$w+2).'┤'.RST; }
function boxBot($w=BOX_W){ return CYN.'╰'.str_repeat('─',$w+2).'╯'.RST; }
function boxRow($c,$w=BOX_W){ $c='  '.$c; return CYN.'│'.RST.pad($c,$w).CYN.'│'.RST; }
function boxRowCenter($c,$w=BOX_W){ return CYN.'│'.RST.pad($c,$w).CYN.'│'.RST; }

function clear_screen(){ echo (strtoupper(substr(PHP_OS,0,3))==='WIN')?system('cls'):system('clear'); }
function ask($p){ echo WHT.$p.RST; return trim(fgets(STDIN)); }

function mask($s){
    if(!$s) return '?';
    $p=strpos($s,'@'); if($p===false) return $s;
    $l=substr($s,0,$p); $d=substr($s,$p);
    if(strlen($l)<6) return $s;
    return substr($l,0,3).str_repeat('*',strlen($l)-3).$d;
}
function fmt($s){
    $s=(int)$s; if($s<=0) return '0s';
    if($s>=3600) return floor($s/3600).'h '.floor(($s%3600)/60).'m '.($s%60).'s';
    if($s>=60)   return floor($s/60).'m '.($s%60).'s';
    return $s.'s';
}

$GLOBALS['LOG_BUFFER']=[];
function log_line($msg,$tag='i'){
    $ic=['i'=>CYN.'›'.RST,'ok'=>GRN.'✓'.RST,'er'=>RED.'✗'.RST,'wr'=>YEL.'!'.RST,'in'=>BLU.'●'.RST,'bi'=>GRN.'₹'.RST];
    $line=WHT.'['.date('H:i:s').']'.RST.' '.($ic[$tag]??CYN.'›'.RST).' '.$msg;
    $GLOBALS['LOG_BUFFER'][]=$line;
    if(count($GLOBALS['LOG_BUFFER'])>8) array_shift($GLOBALS['LOG_BUFFER']);
    echo $line."\n"; flush();
}

// ═══════════════════════════════════════════════════════════
//  HTTP
// ═══════════════════════════════════════════════════════════
function request($url,$method='GET',$data=null,$debug=false,$headers=[]){
    $ch=curl_init();
    $def=[
        "User-Agent: ".UA,
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language: id-ID,id;q=0.9,en;q=0.8",
        "Upgrade-Insecure-Requests: 1",
        "Referer: ".HOME,
    ];
    if($method==='POST') $def[]="Content-Type: application/x-www-form-urlencoded";

    curl_setopt_array($ch,[
        CURLOPT_URL=>$url,
        CURLOPT_RETURNTRANSFER=>true,
        CURLOPT_HEADER=>true,
        CURLOPT_FOLLOWLOCATION=>true,
        CURLOPT_MAXREDIRS=>5,
        CURLOPT_SSL_VERIFYPEER=>false,
        CURLOPT_SSL_VERIFYHOST=>false,
        CURLOPT_COOKIEFILE=>COOKIE,
        CURLOPT_COOKIEJAR=>COOKIE,
        CURLOPT_USERAGENT=>UA,
        CURLOPT_TIMEOUT=>30,
        CURLOPT_CONNECTTIMEOUT=>15,
        CURLOPT_ENCODING=>"",
        CURLOPT_HTTP_VERSION=>CURL_HTTP_VERSION_2TLS,
        CURLOPT_HTTPHEADER=>array_merge($def,$headers),
    ]);
    if($method==='POST'){
        curl_setopt($ch,CURLOPT_POST,true);
        if($data!==null) curl_setopt($ch,CURLOPT_POSTFIELDS,$data);
    }

    $response=curl_exec($ch);
    if($response===false){
        $err=curl_error($ch);
        if($debug) printf("[cURL ERROR] %s\n",$err);
        return ['body'=>'','code'=>0,'url'=>$url,'error'=>$err];
    }
    $info=curl_getinfo($ch);
    $headerSize=$info['header_size'];
    $body=substr($response,$headerSize);

    if($debug){
        echo YEL."  ┌─ debug ─────────────────────────────".RST."\n";
        printf("  │ URL    : %s\n",$info['url']);
        printf("  │ METHOD : %s\n",$method);
        printf("  │ HTTP   : ".CYN."%d".RST."\n",$info['http_code']);
        printf("  │ SIZE   : %d bytes\n",strlen($body));
        if(preg_match('/<title>([^<]+)<\/title>/i',$body,$m)) printf("  │ TITLE  : %s\n",trim($m[1]));
        echo YEL."  └─────────────────────────────────────".RST."\n";
    }

    return ['body'=>$body,'code'=>$info['http_code'],'url'=>$info['url'],'error'=>''];
}

// ═══════════════════════════════════════════════════════════
//  LOGIN
// ═══════════════════════════════════════════════════════════
function login($wallet){
    log_line("logging in...","in");
    if(file_exists(COOKIE)) @unlink(COOKIE);

    $r=request(HOME);
    if($r['code']!==200) return ['ok'=>false,'msg'=>"GET home http {$r['code']}"];
    $html=$r['body'];

    $csrf='';
    if(preg_match('/name=["\']?csrf_token_name["\']?[^>]*value=["\']([^"\']+)["\']/i',$html,$m)) $csrf=$m[1];
    elseif(preg_match('/value=["\']([^"\']+)["\'][^>]*name=["\']?csrf_token_name["\']?/i',$html,$m)) $csrf=$m[1];
    elseif(preg_match('/id=["\']token["\'][^>]*value=["\']([^"\']+)["\']/i',$html,$m)) $csrf=$m[1];

    if($csrf===''){
        if(stripos($html,'Just a moment')!==false||stripos($html,'cf-challenge')!==false)
            return ['ok'=>false,'msg'=>'Cloudflare challenge — butuh cf_clearance'];
        return ['ok'=>false,'msg'=>'CSRF tidak ditemukan'];
    }

    $device="dev_".substr(md5(uniqid(mt_rand(),true)),0,20);
    $post=http_build_query([
        'wallet'=>$wallet,
        'csrf_token_name'=>$csrf,
        'device_token'=>$device,
    ]);
    request(LOGIN,'POST',$post);

    $r3=request(DASH);
    if(stripos($r3['body'],'auth/logout')!==false||stripos($r3['body'],'Logout')!==false)
        return ['ok'=>true,'msg'=>'login ok'];
    return ['ok'=>false,'msg'=>'cookie tidak diterima'];
}

// ═══════════════════════════════════════════════════════════
//  PARSE
// ═══════════════════════════════════════════════════════════
function parse_earn($html){
    $out=[
        'csrf'=>'','token'=>'','ticket'=>'','wallet'=>'',
        'captcha'=>'smartcaptcha','wait'=>0,'balance'=>null,
        'antibot'=>[],'has_form'=>false,
    ];

    if(preg_match('/<form[^>]+id="fauform"[^>]*>(.*?)<\/form>/si',$html,$fm)){
        $out['has_form']=true;
        $inner=$fm[1];
        if(preg_match('/name="csrf_token_name"[^>]*value="([^"]*)"/i',$inner,$m)) $out['csrf']=$m[1];
        if(preg_match('/name="token"[^>]*value="([^"]*)"/i',$inner,$m)) $out['token']=$m[1];
        if(preg_match('/name="earn_ticket"[^>]*value="([^"]*)"/i',$inner,$m)) $out['ticket']=$m[1];
        if(preg_match('/name="wallet"[^>]*value="([^"]*)"/i',$inner,$m)) $out['wallet']=html_entity_decode($m[1]);
        if(preg_match('/name="captcha"[^>]*value="([^"]*)"/i',$inner,$m)) $out['captcha']=$m[1];
    }
    if(preg_match('/let\s+wait\s*=\s*(\d+)/i',$html,$m)) $out['wait']=(int)$m[1];
    if(preg_match('/balance-amount[^>]*>\s*([0-9.,]+)/i',$html,$m)) $out['balance']=(float)str_replace(',','',$m[1]);

    // antibotlinks (kalau ada)
    if(preg_match_all('/<span[^>]*class="antibotlinks"[^>]*>(.*?)<\/span>/si',$html,$all)){
        foreach($all[1] as $chunk){
            if(preg_match_all('/<img[^>]+src=["\']([^"\']+)["\']/i',$chunk,$im))
                foreach($im[1] as $src) $out['antibot'][]=$src;
            if(preg_match_all('/data:image\/[^;]+;base64,([A-Za-z0-9+\/=]+)/i',$chunk,$bm))
                foreach($bm[1] as $b64) $out['antibot'][]=$b64;
            $t=trim(strip_tags($chunk));
            if($t!==''&&strlen($t)<64) $out['antibot'][]='TEXT:'.$t;
        }
    }
    if(preg_match_all('/<img[^>]+(?:class|id)=["\'][^"\']*(?:antibot|captcha_img)[^"\']*["\'][^>]+src=["\']([^"\']+)["\']/i',$html,$m))
        foreach($m[1] as $src) $out['antibot'][]=$src;

    return $out;
}

// ═══════════════════════════════════════════════════════════
//  ANTIBOT SOLVER
// ═══════════════════════════════════════════════════════════
function solve_antibot($b64){
    $apikey=$GLOBALS['STATE']['apikey'];
    if(empty($apikey)) return ['ok'=>false,'msg'=>'apikey kosong'];

    $payload=json_encode(['apikey'=>$apikey,'methods'=>'antibot','main'=>$b64,'json'=>1]);
    $r=request(SOLVER_IN,'POST',$payload,false,['Content-Type: application/json','Referer: '.SOLVER_IN]);
    $j=json_decode($r['body'],true);
    if(!is_array($j)||empty($j['request'])||(int)($j['status']??0)!==1)
        return ['ok'=>false,'msg'=>'submit solver gagal'];
    $id=$j['request'];

    for($i=0;$i<40;$i++){
        $q=http_build_query(['apikey'=>$apikey,'id'=>$id,'action'=>'get','json'=>1]);
        $r2=request(SOLVER_RES."?".$q,'GET',null,false,['Referer: '.SOLVER_RES]);
        $body=trim($r2['body']);

        if(stripos($body,'OK|')===0) return ['ok'=>true,'token'=>substr($body,3)];
        $j2=json_decode($body,true);
        if(is_array($j2)){
            if((int)($j2['status']??0)===1) return ['ok'=>true,'token'=>$j2['request']??$j2['token']??''];
            if(($j2['request']??'')==='CAPCHA_NOT_READY'){ echo CYN.".".RST; flush(); sleep(3); continue; }
            if(stripos($j2['request']??'','ERROR')!==false) return ['ok'=>false,'msg'=>$j2['request']];
        }
        if(stripos($body,'CAPCHA_NOT_READY')!==false){ echo CYN.".".RST; flush(); sleep(3); continue; }
        sleep(3);
    }
    return ['ok'=>false,'msg'=>'timeout'];
}

// ═══════════════════════════════════════════════════════════
//  CLAIM
// ═══════════════════════════════════════════════════════════
function claim(){
    $r=request(EARN,'GET',null,false,['Referer: '.DASH]);
    $html=$r['body'];

    if(strpos($html,'id="fauform"')===false){
        if(stripos($html,'auth/login')!==false||stripos($html,'Sign in')!==false)
            return ['status'=>'session_invalid'];
        $p=parse_earn($html);
        if($p['wait']>0) return ['status'=>'cooldown','wait'=>$p['wait']];
        if($p['balance']!==null) return ['status'=>'cooldown','wait'=>60,'balance'=>$p['balance']];
        return ['status'=>'error','msg'=>'form faucet tidak ada'];
    }

    $info=parse_earn($html);
    if($info['balance']!==null) $GLOBALS['STATE']['balance']=$info['balance'];

    log_line("bal: ".number_format($GLOBALS['STATE']['balance'],4)." Coins",'bi');

    if($info['wait']>0) return ['status'=>'cooldown','wait'=>$info['wait']];
    if(empty($info['ticket'])||empty($info['token'])) return ['status'=>'error','msg'=>'token/ticket kosong'];

    // kalau ada antibotlinks → solve; kalau nggak ada → langsung gas
    if(!empty($info['antibot'])){
        log_line("antibot detected: ".count($info['antibot'])." item(s)",'in');
        foreach($info['antibot'] as $src){
            if(strpos($src,'TEXT:')===0) continue;
            $b64=$src;
            if(!preg_match('#^[A-Za-z0-9+/=]+$#',$src)){
                if(strpos($src,'http')!==0) $src=SITE.(strpos($src,'/')===0?'':'/').$src;
                $img=request($src,'GET',null,false,['Referer: '.EARN]);
                if(empty($img['body'])) continue;
                $b64=base64_encode($img['body']);
            }
            echo CYN."  ◇ solving antibot".RST;
            $sol=solve_antibot($b64);
            echo "\n";
            if(!$sol['ok']) return ['status'=>'captcha_failed','msg'=>$sol['msg']];
            log_line("antibot → ".substr($sol['token'],0,20),'ok');
        }
    }

    sleep(rand(2,4));

    $smart=base64_encode(json_encode([
        'ts'=>(int)(microtime(true)*1000),
        'cpu'=>8,'mem'=>8,'w'=>384,'h'=>832,
        'touch'=>5,'moves'=>rand(0,3),
    ]));
    $fp=hash('sha256',UA.'384x832');

    $post=http_build_query([
        'csrf_token_name'=>$info['csrf'],
        'token'=>$info['token'],
        'earn_ticket'=>$info['ticket'],
        'fp_hash'=>$fp,
        'confirm_wallet'=>'',
        'wallet'=>$info['wallet'],
        'smart_token'=>$smart,
        'captcha'=>$info['captcha'],
    ]);

    $r2=request(EARN,'POST',$post,false,['Referer: '.EARN,'Origin: '.SITE]);
    $respHtml=$r2['body'];

    $p2=parse_earn($respHtml);
    if($p2['balance']!==null) $GLOBALS['STATE']['balance']=$p2['balance'];

    if(preg_match('/Success!.*?([0-9.]+)\s+Coins/i',$respHtml,$m)) return ['status'=>'success','amount'=>(float)$m[1]];
    if(stripos($respHtml,'has been added to your account balance')!==false) return ['status'=>'success','amount'=>0];
    if(preg_match("/Swal\.fire\(\{[^}]*html:\s*'([^']+)'/i",$respHtml,$m)){
        $msg=strip_tags($m[1]);
        if(stripos($msg,'success')!==false) return ['status'=>'success','amount'=>0];
        if(stripos($msg,'wait')!==false||stripos($msg,'limit')!==false)
            return ['status'=>'cooldown','wait'=>$p2['wait']?:60];
        return ['status'=>'error','msg'=>$msg];
    }
    if(stripos($respHtml,'cheat_detected')!==false) return ['status'=>'banned'];
    return ['status'=>'unknown','msg'=>'response tidak dikenali'];
}

// ═══════════════════════════════════════════════════════════
//  UI
// ═══════════════════════════════════════════════════════════
function banner(){
    $st=&$GLOBALS['STATE'];
    $statusTxt=$st['wallet']?GRN.BOLD."● ACTIVE".RST:YEL.BOLD."○ IDLE".RST;

    echo CYN.'╭'.str_repeat('─',BOX_W+2).'╮'.RST."\n";
    echo boxRowCenter(MAG.BOLD."⚡ AUTO CLAIM ENGINE ⚡".RST)."\n";
    echo boxMid()."\n";
    echo boxRow(CYN.'◆'.RST.' Tool       : '.WHT.BOLD.TOOL_NAME.RST)."\n";
    echo boxRow(CYN.'◆'.RST.' Developer  : '.MAG.BOLD.DEVELOPER.RST)."\n";
    echo boxRow(CYN.'◆'.RST.' Version    : '.WHT.VERSION.RST)."\n";
    echo boxRow(CYN.'◆'.RST.' Status     : '.$statusTxt)."\n";
    echo boxRow(CYN.'◆'.RST.' Telegram   : '.BLU.TELEGRAM.RST)."\n";
    echo boxBot()."\n";
    echo "\n  ".GRN.BOLD."✓ Souu Engine Ready!".RST."\n";
    echo "  ".CYN.str_repeat('─',BOX_W).RST."\n";
}

function account_panel(){
    $st=&$GLOBALS['STATE'];
    $w=$st['wallet']?mask($st['wallet']):YEL.'(belum login)'.RST;
    $bal=number_format($st['balance'],4)." Coins";

    echo "\n".boxTop("ACCOUNT")."\n";
    echo boxRow(WHT.'Accounts Loaded '.RST.': '.CYN.BOLD.($st['wallet']?'1':'0').RST)."\n";
    echo boxRow(WHT.'Wallet          '.RST.': '.CYN.$w.RST)."\n";
    echo boxRow(WHT.'Balance         '.RST.': '.GRN.BOLD.$bal.RST)."\n";
    echo boxBot()."\n";
}

function menu_panel(){
    echo "\n".boxTop("MENU")."\n";
    echo boxRow(GRN.'[1]'.RST.' 🚀 Start Farming')."\n";
    echo boxRow(YEL.'[2]'.RST.' ✉  Config Email')."\n";
    echo boxRow(BLU.'[3]'.RST.' 🔑 Config Apikey')."\n";
    echo boxRow(RED.'[4]'.RST.' ❌ Exit')."\n";
    echo boxBot()."\n";
}

function stats_panel(){
    $st=&$GLOBALS['STATE'];
    $up=$st['started']?(time()-$st['started']):0;
    $upt=sprintf('%02d:%02d:%02d',floor($up/3600),floor(($up%3600)/60),$up%60);
    $next=$st['next_at']>time()
        ?YEL.'⏳ Next Claim : '.BOLD.fmt($st['next_at']-time()).RST
        :GRN.'⚡ Ready to claim'.RST;

    echo "\n".boxTop("STATS")."\n";
    echo boxRow(GRN.'✓ Success'.RST.' : '.pad((string)$st['success'],6).'  '.RED.'✗ Failed'.RST.' : '.$st['failed'])."\n";
    echo boxRow(BLU.'⏱ Uptime '.RST.' : '.pad($upt,22))."\n";
    echo boxRow($next)."\n";
    echo boxBot()."\n";
}

function log_panel(){
    echo "\n".boxTop("LOG")."\n";
    if(empty($GLOBALS['LOG_BUFFER'])){
        echo boxRow(WHT.'(belum ada log)'.RST)."\n";
    } else {
        foreach($GLOBALS['LOG_BUFFER'] as $ln){
            if(vlen($ln)>BOX_W-2){
                $plain=preg_replace('/\x1b\[[0-9;]*m/','',$ln);
                $ln=WHT.substr($plain,0,BOX_W-5).'...'.RST;
            }
            echo boxRow($ln)."\n";
        }
    }
    echo boxBot()."\n";
}

function refresh(){ clear_screen(); banner(); account_panel(); menu_panel(); stats_panel(); log_panel(); }

// ═══════════════════════════════════════════════════════════
//  CONFIG
// ═══════════════════════════════════════════════════════════
function cfg_load(){
    if(!file_exists(CFG)) return;
    $d=json_decode(file_get_contents(CFG),true);
    if(!is_array($d)) return;
    foreach($d as $k=>$v) if(array_key_exists($k,$GLOBALS['STATE'])) $GLOBALS['STATE'][$k]=$v;
}
function cfg_save(){
    file_put_contents(CFG,json_encode($GLOBALS['STATE'],JSON_PRETTY_PRINT|JSON_UNESCAPED_SLASHES));
}

// ═══════════════════════════════════════════════════════════
//  ACTIONS
// ═══════════════════════════════════════════════════════════
function act_config_email(){
    echo "\n".CYN."── Config Email ──".RST."\n";
    $w=ask("FaucetPay email: ");
    if(!$w){ log_line('kosong','er'); return; }
    $r=login($w);
    if(!$r['ok']){ log_line('gagal: '.$r['msg'],'er'); return; }
    $GLOBALS['STATE']['wallet']=$w;
    cfg_save();
    log_line('login ok — '.mask($w),'ok');
}

function act_config_apikey(){
    echo "\n".CYN."── Config Apikey ──".RST."\n";
    $cur=$GLOBALS['STATE']['apikey'];
    if($cur) echo "  ".GRN."current: ".substr($cur,0,12)."...".RST."\n";
    $k=ask("Waryono API key (Enter cancel): ");
    if(!$k){ log_line('cancel','wr'); return; }
    $GLOBALS['STATE']['apikey']=$k;
    cfg_save();
    log_line('saved','ok');
}

function summary(){
    $st=&$GLOBALS['STATE'];
    $up=$st['started']?(time()-$st['started']):0;
    $upt=sprintf('%02d:%02d:%02d',floor($up/3600),floor(($up%3600)/60),$up%60);

    echo "\n".CYN.'╔'.str_repeat('═',BOX_W+2).'╗'.RST."\n";
    echo CYN.'║'.RST.pad(MAG.BOLD.'FINAL SUMMARY'.RST,BOX_W,'center').CYN.'║'.RST."\n";
    echo CYN.'╠'.str_repeat('═',BOX_W+2).'╣'.RST."\n";
    echo CYN.'║'.RST.pad('  Wallet   : '.CYN.mask($st['wallet']).RST,BOX_W).CYN.'║'.RST."\n";
    echo CYN.'║'.RST.pad('  Uptime   : '.BLU.$upt.RST,BOX_W).CYN.'║'.RST."\n";
    echo CYN.'║'.RST.pad('  Success  : '.GRN.$st['success'].RST,BOX_W).CYN.'║'.RST."\n";
    echo CYN.'║'.RST.pad('  Failed   : '.RED.$st['failed'].RST,BOX_W).CYN.'║'.RST."\n";
    echo CYN.'║'.RST.pad('  Balance  : '.GRN.BOLD.number_format($st['balance'],4).' Coins'.RST,BOX_W).CYN.'║'.RST."\n";
    echo CYN.'╚'.str_repeat('═',BOX_W+2).'╝'.RST."\n";
    echo WHT.'  ~ '.MAG.BOLD.DEVELOPER.RST.WHT.' | '.BLU.TELEGRAM.RST."\n\n";
}

// ═══════════════════════════════════════════════════════════
//  BOOT
// ═══════════════════════════════════════════════════════════
if(function_exists('pcntl_signal')){
    pcntl_async_signals(true);
    pcntl_signal(SIGINT,function(){ summary(); exit(0); });
}

clear_screen();
cfg_load();
refresh();

$start_farm=false;
while(true){
    echo "\n  ".WHT."Select option ".CYN."➜".RST." ";
    $c=trim(fgets(STDIN));

    if($c==='1'){
        if(empty($GLOBALS['STATE']['wallet'])){ log_line('email belum diset (menu 2)','er'); refresh(); continue; }
        if(empty($GLOBALS['STATE']['apikey'])){ log_line('apikey belum diset (menu 3)','er'); refresh(); continue; }
        $start_farm=true;
        break;
    } elseif($c==='2'){ act_config_email(); }
    elseif($c==='3'){ act_config_apikey(); }
    elseif($c==='4'){ summary(); exit(0); }
    else { log_line('invalid option','er'); }

    echo "\n";
    refresh();
}

if(!$start_farm){ summary(); exit(0); }

log_line('validating session...','in');
$r=request(EARN,'GET',null,false,['Referer: '.DASH]);
if(strpos($r['body'],'id="fauform"')===false){
    log_line('session expired, re-login...','wr');
    $lr=login($GLOBALS['STATE']['wallet']);
    if(!$lr['ok']){ log_line('gagal login: '.$lr['msg'],'er'); exit(1); }
    log_line('login ok','ok');
} else {
    log_line('session ok','ok');
}

$GLOBALS['STATE']['started']=time();
refresh();

$round=0;
while(true){
    $round++;
    $st=&$GLOBALS['STATE'];

    if($st['next_at']>time()){
        $w=$st['next_at']-time();
        refresh();
        echo "\n  ".YEL."⏳ Next claim in ".BOLD.fmt($w).RST."\n";
        sleep(min($w,30));
        continue;
    }

    refresh();
    echo "\n".MAG."  ╭─ ".RST.WHT."Round #$round".RST.MAG." ─────────────────────────────╮".RST."\n";

    $res=claim();

    switch($res['status']){
        case 'success':
            $st['success']++;
            $amt=(float)($res['amount']??0);
            echo GRN."  │  ✓ CLAIMED +$amt Coins".RST."\n";
            echo GRN."  │  Balance: ".BOLD.number_format($st['balance'],4)." Coins".RST."\n";
            echo GRN."  ╰──────────────────────────────────────╯".RST."\n";
            log_line("+$amt Coins | bal: ".number_format($st['balance'],4),'ok');
            $st['next_at']=time()+65;
            break;

        case 'cooldown':
            $w=(int)($res['wait']??60);
            if(isset($res['balance'])) $st['balance']=$res['balance'];
            $st['next_at']=time()+$w+3;
            log_line("cooldown ".fmt($w)." → skip",'wr');
            break;

        case 'session_invalid':
            log_line('session expired, re-login...','wr');
            $lr=login($st['wallet']);
            if($lr['ok']){ log_line('login ok','ok'); $st['next_at']=time()+10; }
            else { log_line('gagal: '.$lr['msg'],'er'); $st['next_at']=time()+600; }
            break;

        case 'banned':
            log_line('BANNED / cheat detected','er');
            $st['next_at']=time()+86400;
            break;

        case 'captcha_failed':
            $st['failed']++;
            log_line('captcha failed: '.($res['msg']??'?'),'er');
            $st['next_at']=time()+rand(30,60);
            break;

        default:
            $st['failed']++;
            log_line(($res['status']??'?').': '.substr($res['msg']??'?',0,80),'er');
            $st['next_at']=time()+rand(20,45);
    }

    cfg_save();
    refresh();
    sleep(2);
}

summary();
