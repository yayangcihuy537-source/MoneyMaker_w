#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const https = require('https');
const readline = require('readline');
const { spawn } = require('child_process');

const RED = "\x1b[0;31m"; const GRN = "\x1b[0;32m"; const YEL = "\x1b[0;33m";
const BLU = "\x1b[0;34m"; const MAG = "\x1b[0;35m"; const CYN = "\x1b[0;36m"; const WHT = "\x1b[0;37m";
const RST = "\x1b[0m";
const ORG = "\x1b[38;5;208m";
const CLR = "\r\x1b[2K";

const CONFIG_PATH = path.join(__dirname, 'config.json');
const TMP_EXEC_PY = path.join(__dirname, '.cf_bypass.py');
const HOST = 'https://bigbtc.win';
const PAGE_URL = `${HOST}/faucet`;
const CLAIM_URL = `${HOST}/claimreward`;
const SITEKEY = 'c0a0b0a5-2a3c-4a10-b165-7b93e4e81a00';
const SOLVER_IN = 'https://api.waryono.my.id/in.php';
const SOLVER_RES = 'https://api.waryono.my.id/res.php';
const SOLVER_HOST = 'api.waryono.my.id';
const DEF_UA = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36';

const FATAL_ERRORS = {
  ERROR_KEY_DOES_NOT_EXIST: 'API key kosong / tidak dikirim',
  ERROR_WRONG_USER_KEY: 'API key tidak valid / tidak ditemukan',
  ERROR_ZERO_BALANCE: 'Saldo token habis / tidak cukup',
  ERROR_NO_SUCH_METHOD: 'Method tidak dikenali (bukan hcaptcha)',
  ERROR_BAD_PARAMETERS: 'Parameter tidak lengkap (sitekey/url/domain)',
  ERROR_METHOD_NOT_SPECIFIED: 'Parameter methods tidak diisi',
  ERROR_EMPTY_IMAGE: 'Gambar tidak dikirim (base64 kosong)',
  ERROR_URL_EMPTY: 'URL tidak dikirim',
  ERROR_WRONG_METHOD: 'HTTP Method salah (harus POST)'
};

const RETRYABLE_ERRORS = new Set([
  'ERROR_CAPTCHA_UNSOLVABLE', 'WRONG_CAPTCHA_ID',
  'ERROR_TOO_MANY_REQUESTS', 'ERROR_DATABASE_CONNECTION_FAILED',
  'INTERNAL_SERVER_ERROR', 'ERROR_POLL_TIMEOUT',
  'ERROR_INVALID_JSON', 'ERROR_NO_TASK_ID'
]);

const EXEC_PY_SOURCE = `import time
import sys
import json
import warnings
import os

warnings.filterwarnings('ignore')
os.environ["PYTHONWARNINGS"] = "ignore"

def log(msg):
    print(msg, file=sys.stderr)

def bypass_cf(target):
    log("Seledroid Cloudflare...")

    _stderr_backup = sys.stderr
    _devnull = open(os.devnull, 'w')
    sys.stderr = _devnull

    try:
        from seledroid import webdriver as sd
    except ImportError:
        sys.stderr = _stderr_backup
        _devnull.close()
        log("install Seledroid module and Apk")
        sys.exit(1)
    finally:
        sys.stderr = _stderr_backup
        try:
            _devnull.close()
        except Exception:
            pass

    time.sleep(3)

    try:
        d = sd.Chrome(gui=True, pip_mode=False)
        d.get(target)
        time.sleep(10)

        clr = None
        for _ in range(15):
            clr = d.get_cookie("cf_clearance")
            if clr:
                break
            time.sleep(5)

        try:
            ua = d.user_agent
        except Exception:
            try:
                ua = d.execute_script("return navigator.userAgent;")
            except Exception:
                ua = None

        try:
            d.close()
        except Exception:
            pass

    except Exception as e:
        log(f"Failed ({e})")
        return {"cf_clearance": None, "user_agent": None}

    if not clr:
        log("Failed (no cf_clearance)")
        return {"cf_clearance": None, "user_agent": None}

    tok = clr.split('=', 1)[1] if '=' in clr else clr
    log("Success!")
    return {
        "cf_clearance": tok,
        "user_agent": ua
    }

def usage():
    log("Usage:")
    log("  python exec.py <url>")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()

    TARGET_URL = sys.argv[1]
    result = bypass_cf(TARGET_URL)
    print(json.dumps(result))
`;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const now = () => {
  const d = new Date();
  return [d.getHours(), d.getMinutes(), d.getSeconds()]
    .map((n) => String(n).padStart(2, '0')).join(':');
};

function clear() {
  process.stdout.write('\x1b[2J\x1b[3J\x1b[H');
}

function log(msg, tag = 'i') {
  const icons = { i: `${CYN}»${RST}`, ok: `${GRN}✓${RST}`, er: `${RED}✗${RST}`,
                  wr: `${YEL}⚠${RST}`, in: `${BLU}●${RST}`, bi: `${GRN}₹${RST}`,
                  dbg: `${MAG}⚙${RST}`, or: `${ORG}●${RST}` };
  const icon = icons[tag] || `${CYN}»${RST}`;
  process.stdout.write(CLR + `${WHT}[${now()}]${RST} ${icon} ${msg}\n`);
}

const SYMBOLS  = ['🌘','🌗','🌖','🌕','🌔','🌓','🌒','🌑'];
const SPINNERS = ['⣾⣽','⣽⣻','⣻⢿','⢿⡿','⡿⣟','⣟⣯','⣯⣷','⣷⣾'];
const SPINNERS1 = ['▁⣾','▂⣽','▃⣻','▄⢿','▅⡿','▆⣟','▇⣯','█⣷','▇⣾','▆⣽','▅⣻','▄⢿','▃⡿','▂⣟','▁⣯'];
const DOTS = ['▪', '▪▪', '▪▪▪', '▪▪▪▪'];

function startSpinner(label, timeout) {
  const start = Date.now();
  let i = 0;
  const id = setInterval(() => {
    const elapsed = Math.floor((Date.now() - start) / 1000);
    const pct = timeout ? Math.round((elapsed / timeout) * 100) : 0;
    const sym = SYMBOLS[i % SYMBOLS.length];
    const sp  = SPINNERS[i % SPINNERS.length];
    const sp1 = SPINNERS1[i % SPINNERS1.length];
    const dot = DOTS[elapsed % DOTS.length];
    i++;
    const c1 = 1 + Math.floor(Math.random() * 7);
    const c2 = 1 + Math.floor(Math.random() * 7);
    const mm = String(Math.floor(elapsed / 60)).padStart(2, '0');
    const ss = String(elapsed % 60).padStart(2, '0');
    process.stdout.write(
      `${CLR} \x1b[1;3${c1}m ${sp}\x1b[1;37m ${label} ` +
      `\x1b[1;31m${mm}:${ss}\x1b[1;3${c2}m ${sym} ${sp1}` +
      `\x1b[1;37m ${pct}%\x1b[1;33m ${dot}`
    );
  }, 100);
  return () => {
    clearInterval(id);
    process.stdout.write(CLR);
  };
}

async function tmr(seconds, label = 'Waiting...') {
  const total = Math.floor(seconds);
  if (total < 1) return;
  const start = Date.now();
  let i = 0;
  while (true) {
    const elapsed = Math.floor((Date.now() - start) / 1000);
    const remaining = Math.max(0, total - elapsed);
    const pct = Math.round(((total - remaining) / total) * 100);
    const mm = String(Math.floor(remaining / 60)).padStart(2, '0');
    const ss = String(remaining % 60).padStart(2, '0');
    const sym = SYMBOLS[i % SYMBOLS.length];
    const sp  = SPINNERS[i % SPINNERS.length];
    const sp1 = SPINNERS1[i % SPINNERS1.length];
    const dot = DOTS[elapsed % DOTS.length];
    i++;
    const c1 = 1 + Math.floor(Math.random() * 7);
    const c2 = 1 + Math.floor(Math.random() * 7);
    process.stdout.write(
      `${CLR} \x1b[1;3${c1}m ${sp}\x1b[1;37m ${label} ` +
      `\x1b[1;31m${mm}:${ss}\x1b[1;3${c2}m ${sym} ${sp1}` +
      `\x1b[1;37m ${pct}%\x1b[1;33m ${dot}`
    );
    if (remaining <= 0) break;
    await sleep(100);
  }
  process.stdout.write(CLR);
}

function bannerMain() {
  console.log(`${WHT}═══════════════════════════════════════════════${RST}`);
  console.log(`${YEL}              BOT bigbtc.win${RST}`);
  console.log(`${WHT}═══════════════════════════════════════════════${RST}`);
}

function parseCookieString(str) {
  const out = {};
  if (!str) return out;
  for (const part of str.split(';')) {
    const t = part.trim();
    if (!t) continue;
    const idx = t.indexOf('=');
    if (idx === -1) continue;
    const k = t.slice(0, idx).trim();
    const v = t.slice(idx + 1).trim();
    if (k) out[k] = v;
  }
  return out;
}

class Jar {
  constructor() { this.cookies = new Map(); }
  set(name, value) { this.cookies.set(name, value); }
  get(name) { return this.cookies.get(name); }
  toHeader() {
    if (this.cookies.size === 0) return '';
    return Array.from(this.cookies.entries()).map(([k, v]) => `${k}=${v}`).join('; ');
  }
  loadFromString(str) {
    const parsed = parseCookieString(str);
    for (const [k, v] of Object.entries(parsed)) this.cookies.set(k, v);
    return parsed;
  }
  absorbSetCookie(arr) {
    if (!arr) return;
    for (const raw of arr) {
      const [pair] = raw.split(';');
      const idx = pair.indexOf('=');
      if (idx === -1) continue;
      const name = pair.slice(0, idx).trim();
      const value = pair.slice(idx + 1).trim();
      if (name) this.cookies.set(name, value);
    }
  }
}

function request(opts) {
  return new Promise((resolve, reject) => {
    const req = https.request(opts, (res) => {
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => {
        resolve({
          status: res.statusCode,
          headers: res.headers,
          body: Buffer.concat(chunks).toString('utf-8')
        });
      });
    });
    req.on('error', reject);
    req.setTimeout(45000, () => req.destroy(new Error('Request timeout')));
    if (opts.body) req.write(opts.body);
    req.end();
  });
}

function makeClient(cfg, jar) {
  const baseHeaders = {
    'User-Agent': cfg.userAgent || DEF_UA,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
    'Sec-Ch-Ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?1',
    'Sec-Ch-Ua-Platform': '"Android"',
    'Upgrade-Insecure-Requests': '1'
  };

  async function doRequest(method, urlStr, options = {}) {
    const url = new URL(urlStr);
    const headers = { ...baseHeaders, ...(options.headers || {}) };
    const cookie = jar.toHeader();
    if (cookie) headers['Cookie'] = cookie;

    const body = options.body || null;
    if (body) headers['Content-Length'] = Buffer.byteLength(body);

    const res = await request({
      hostname: url.hostname, port: 443,
      path: url.pathname + url.search, method, headers, body
    });

    if (res.headers['set-cookie']) jar.absorbSetCookie(res.headers['set-cookie']);

    if ([301, 302, 303, 307, 308].includes(res.status) && res.headers.location && (options.maxRedirects ?? 5) > 0) {
      const next = new URL(res.headers.location, urlStr).toString();
      return doRequest(options.redirectMethod || 'GET', next, {
        ...options,
        body: options.redirectMethod === 'POST' ? options.body : null,
        maxRedirects: (options.maxRedirects ?? 5) - 1
      });
    }
    return res;
  }

  return {
    get: (url, opts = {}) => doRequest('GET', url, opts),
    post: (url, body, opts = {}) => doRequest('POST', url, { ...opts, body })
  };
}

function solverRequest(pathname, params = {}, method = 'POST', bodyObj = null) {
  return new Promise((resolve, reject) => {
    const query = new URLSearchParams(params).toString();
    const fullPath = query ? `${pathname}?${query}` : pathname;
    const body = bodyObj ? JSON.stringify(bodyObj) : null;
    const headers = { 'User-Agent': DEF_UA, 'Accept': 'application/json' };
    if (body) {
      headers['Content-Type'] = 'application/json';
      headers['Content-Length'] = Buffer.byteLength(body);
    }

    const req = https.request({
      hostname: SOLVER_HOST, port: 443, path: fullPath, method, headers
    }, (res) => {
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => {
        const text = Buffer.concat(chunks).toString('utf-8');
        try { resolve({ http: res.statusCode, data: JSON.parse(text) }); }
        catch { resolve({ http: res.statusCode, data: { status: 0, request: text } }); }
      });
    });
    req.on('error', reject);
    req.setTimeout(30000, () => req.destroy(new Error('Solver timeout')));
    if (body) req.write(body);
    req.end();
  });
}

function classifySolverStatus(statusCode, statusMsg) {
  if ([401, 402, 400, 405].includes(statusCode)) return 'fatal';
  if (FATAL_ERRORS[statusMsg]) return 'fatal';
  if (statusMsg === 'ERROR_TOO_MANY_REQUESTS') return 'rate';
  if (statusCode === 429 || statusCode >= 500) return 'server';
  if (RETRYABLE_ERRORS.has(statusMsg)) return 'retry';
  if (statusMsg === 'CAPCHA_NOT_READY') return 'polling';
  return 'unknown';
}

async function solveHcaptcha(apikey, timeout = 300) {
  const payload = {
    apikey,
    methods: 'hcaptcha',
    domain: HOST,
    sitekey: SITEKEY,
    json: 1
  };

  const stop = startSpinner('[hCaptcha]', timeout);

  try {
    let submit;
    try {
      submit = await solverRequest('/in.php', {}, 'POST', payload);
    } catch (e) {
      stop();
      return ['retry', `ERROR_INVALID_JSON:${e.message}`];
    }

    const task = submit.data || {};
    if (task.status !== 1) {
      const errMsg = String(task.error || task.request || 'UNKNOWN');
      const kind = classifySolverStatus(submit.http, errMsg);
      stop();
      if (kind === 'fatal') {
        log(FATAL_ERRORS[errMsg] || errMsg, 'er');
        return ['fatal', errMsg];
      }
      return [kind, errMsg];
    }

    const taskId = task.request || '';
    if (!taskId) { stop(); return ['retry', 'ERROR_NO_TASK_ID']; }

    const pStart = Date.now();
    let last = 0;

    while (true) {
      const pElapsed = (Date.now() - pStart) / 1000;
      if (pElapsed > timeout) { stop(); return ['retry', 'ERROR_POLL_TIMEOUT']; }

      if (pElapsed >= last + 3) {
        last = pElapsed;
        let poll;
        try {
          poll = await solverRequest('/res.php', {
            apikey, action: 'get', id: taskId, json: 1
          }, 'GET');
        } catch {
          await sleep(1000);
          continue;
        }

        const d = poll.data || {};
        if (d.status === 1) {
          stop();
          return d.request || '';
        }

        const reqStatus = String(d.request || d.error || '');
        if (reqStatus === 'CAPCHA_NOT_READY') {
        } else if (reqStatus.startsWith('ERROR_') || reqStatus === 'WRONG_CAPTCHA_ID') {
          stop();
          const kind = classifySolverStatus(200, reqStatus);
          if (kind === 'fatal') {
            log(FATAL_ERRORS[reqStatus] || reqStatus, 'er');
            return ['fatal', reqStatus];
          }
          return [kind, reqStatus];
        }
      }
      await sleep(300);
    }
  } catch (e) {
    stop();
    return ['retry', `ERROR_INVALID_JSON:${e.message}`];
  }
}

function isLoggedIn(html) {
  if (!html) return false;
  return html.includes('id="btcaddress"') && html.toLowerCase().includes('logout');
}

function isCfChallenge(html, statusCode) {
  if ([403, 503].includes(statusCode)) return true;
  if (!html) return false;
  const low = html.toLowerCase();
  return low.includes('just a moment') || low.includes('challenges.cloudflare.com') ||
         low.includes('cf-chl') || low.includes('cf-mitigated');
}

function parseCsrf(html) {
  if (!html) return null;
  const patterns = [
    /name=["']csrftoken["']\s+value=["']([^"']+)["']/,
    /value=["']([^"']+)["']\s+name=["']csrftoken["']/,
    /csrftoken\s*[=:]\s*["']([^"']+)["']/,
    /csrf_token\s*[=:]\s*["']([^"']+)["']/
  ];
  for (const p of patterns) {
    const m = html.match(p);
    if (m) return m[1];
  }
  return null;
}

function parseBalance(html) {
  if (!html) return null;
  const m = html.match(/id="account"[^>]*><b>(\d+)<\/b>\s*satoshi/);
  return m ? parseInt(m[1], 10) : null;
}

function parseReward(html) {
  if (!html) return null;
  const m = html.match(/You won\s*<b>(\d+)<\/b>\s*satoshi/i);
  if (m) return `${m[1]} satoshi`;
  const m2 = html.match(/You won\s*([\d.]+)\s*satoshi/i);
  return m2 ? `${m2[1]} satoshi` : null;
}

function parseCooldown(html) {
  if (!html) return null;
  const m = html.match(/countdown\((\d+)\)/);
  return m ? parseInt(m[1], 10) : null;
}

function printReward(rewardText, balance) {
  const ts = now();
  console.log(`${WHT}[${ts}]${RST} ${GRN}${rewardText.toLowerCase()} has been sent to your account!${RST}`);
  if (balance != null) {
    console.log(`${WHT}[${ts}]${RST} ${YEL}» New Balance: ${balance} sats${RST}`);
  }
}

function extractExecPy() { fs.writeFileSync(TMP_EXEC_PY, EXEC_PY_SOURCE, 'utf-8'); }
function cleanupExecPy() { try { if (fs.existsSync(TMP_EXEC_PY)) fs.unlinkSync(TMP_EXEC_PY); } catch {} }

function runCfBypass(target, suppressStderr = false) {
  return new Promise((resolve, reject) => {
    extractExecPy();

    const py = spawn('python', [TMP_EXEC_PY, target], {
      cwd: __dirname, stdio: ['ignore', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    py.stdout.on('data', (d) => { stdout += d.toString(); });

    py.stderr.on('data', (d) => {
      stderr += d.toString();
      if (!suppressStderr) {
        const line = d.toString().trim();
        if (line) process.stdout.write(`   ${MAG}[seledroid]${RST} ${line}\n`);
      }
    });

    py.on('error', (err) => {
      cleanupExecPy();
      reject(new Error(`spawn error: ${err.message}`));
    });

    py.on('close', (code) => {
      cleanupExecPy();
      if (code !== 0) return reject(new Error(stderr.trim() || `exit code ${code}`));
      const lastLine = stdout.trim().split('\n').filter(Boolean).pop();
      if (!lastLine) return reject(new Error('no output'));
      try { resolve(JSON.parse(lastLine)); }
      catch { reject(new Error(`bad JSON: ${lastLine.slice(0, 100)}`)); }
    });
  });
}

function saveConfig(cfg) { fs.writeFileSync(CONFIG_PATH, JSON.stringify(cfg, null, 2)); }

function loadConfig() {
  if (!fs.existsSync(CONFIG_PATH)) return null;
  try {
    const cfg = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
    return (cfg.apikey && cfg.cookie) ? cfg : null;
  } catch { return null; }
}

async function askQuestion(q) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((res) => rl.question(q, (a) => { rl.close(); res(a); }));
}

async function setupWizard() {
  clear();
  bannerMain();
  console.log(`${WHT}  ⚙  BigBTC Configuration Setup${RST}`);
  console.log(`${WHT}  ─────────────────────────────${RST}`);

  const apikey = (await askQuestion(`${WHT}  Skibidixxx Apikey : ${RST}`)).trim();
  const userAgent = (await askQuestion(`${WHT}  User Agent        : ${RST}`)).trim();
  const cookie = (await askQuestion(`${WHT}  Cookie            : ${RST}`)).trim();

  if (!apikey || !cookie) {
    console.log('');
    log('Apikey & Cookie wajib diisi.', 'er');
    process.exit(1);
  }

  const cfg = {
    apikey,
    userAgent: userAgent || DEF_UA,
    cookie,
    minDelaySec: 485,
    maxDelaySec: 490
  };
  saveConfig(cfg);

  clear();
  bannerMain();
  log('Config tersimpan di config.json', 'ok');
  await sleep(1000);
  return cfg;
}

async function promptNewCookie(cfg, jar) {
  console.log('');
  console.log(`${WHT}═══════════════════════════════════════════════${RST}`);
  console.log(`${RED}  ⚠  Cookie Expired / Cloudflare Block!${RST}`);
  console.log(`${WHT}═══════════════════════════════════════════════${RST}`);
  const newCookie = (await askQuestion(`${WHT}  Paste New Cookie : ${RST}`)).trim();
  clear();
  bannerMain();

  if (!newCookie) {
    log('Cookie kosong, batal.', 'er');
    await sleep(1000);
    return false;
  }

  const parsed = jar.loadFromString(newCookie);
  if (!parsed.PHPSESSID) log('Cookie tidak punya PHPSESSID.', 'wr');
  cfg.cookie = newCookie;
  saveConfig(cfg);
  log('Cookie baru disimpan ke config.json', 'ok');
  return true;
}

async function checkSession(cfg, jar) {
  const client = makeClient(cfg, jar);
  const r = await client.get(PAGE_URL);
  if (isCfChallenge(r.body, r.status)) return { status: 'cf', html: r.body, res: r };
  if (!isLoggedIn(r.body)) return { status: 'invalid', html: r.body, res: r };
  return { status: 'ok', html: r.body, res: r };
}

async function handleCfChallenge(cfg, jar) {
  process.stdout.write(
    CLR + `${WHT}[${now()}]${RST} ${ORG}●${RST} Seledroid Cloudflare... `
  );

  try {
    const result = await runCfBypass(HOST, true);

    if (!result.cf_clearance) {
      process.stdout.write(`${RED}Failed${RST}\n`);
      return false;
    }

    jar.set('cf_clearance', result.cf_clearance);

    if (result.user_agent) cfg.userAgent = result.user_agent;

    const parsedCookie = parseCookieString(cfg.cookie || '');
    parsedCookie.cf_clearance = result.cf_clearance;
    cfg.cookie = Object.entries(parsedCookie)
      .map(([k, v]) => `${k}=${v}`).join('; ');
    saveConfig(cfg);

    process.stdout.write(`${GRN}Success!${RST}\n`);
    await sleep(1000);
    return true;
  } catch (e) {
    process.stdout.write(`${RED}Failed (${e.message})${RST}\n`);
    return false;
  }
}

async function runFaucet(cfg, jar) {
  let rejectCount = 0;
  let lastBalance = null;
  let firstRound = true;

  while (true) {
    try {
      if (firstRound) log('Cek status session...', 'i');
      const chk = await checkSession(cfg, jar);

      if (chk.status === 'cf') {
        const ok = await handleCfChallenge(cfg, jar);
        if (!ok) await tmr(15, 'Retry...');
        continue;
      }

      if (chk.status === 'invalid') {
        log('Cookie expired. Input ulang...', 'wr');
        const ok = await promptNewCookie(cfg, jar);
        if (!ok) return;
        continue;
      }

      const html = chk.html;
      const bal = parseBalance(html);
      if (bal != null) lastBalance = bal;
      if (bal != null && firstRound) log(`Session aktif — Balance: ${bal} satoshi`, 'ok');

      firstRound = false;

      const rewardInPage = parseReward(html);
      if (rewardInPage) {
        printReward(rewardInPage, bal);
        const cd = parseCooldown(html) || 480;
        await tmr(cd + 2, 'Waiting...');
        continue;
      }

      const csrf = parseCsrf(html);
      if (!csrf) {
        const cd = parseCooldown(html);
        if (cd) { await tmr(cd + 2, 'Waiting...'); continue; }
        log('csrftoken tidak ditemukan!', 'er');
        await sleep(5000);
        continue;
      }

      const token = await solveHcaptcha(cfg.apikey);
      if (Array.isArray(token)) {
        const [kind, code] = token;
        if (kind === 'fatal') {
          console.log('');
          console.log(`${RED}═══════════════════════════════════════════════${RST}`);
          console.log(`${RED}  FATAL: ${code}${RST}`);
          console.log(`${RED}  ${FATAL_ERRORS[code] || ''}${RST}`);
          console.log(`${RED}═══════════════════════════════════════════════${RST}`);
          return;
        }
        if (kind === 'rate')  { await tmr(10, 'Waiting...'); continue; }
        if (kind === 'server') { await tmr(5, 'Waiting...'); continue; }
        await sleep(2000);
        continue;
      }

      const body = new URLSearchParams({
        csrftoken: csrf,
        claim: 'true',
        'g-recaptcha-response': token,
        'h-captcha-response': token
      }).toString();

      const client = makeClient(cfg, jar);
      let claimRes;
      try {
        claimRes = await client.post(CLAIM_URL, body, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': HOST,
            'Referer': PAGE_URL
          },
          maxRedirects: 5
        });
      } catch (e) {
        log(`Claim error: ${e.message}`, 'er');
        await sleep(5000);
        continue;
      }

      if (isCfChallenge(claimRes.body, claimRes.status)) {
        const ok = await handleCfChallenge(cfg, jar);
        if (!ok) await tmr(15, 'Retry...');
        continue;
      }

      const reward = parseReward(claimRes.body);
      if (reward) {
        rejectCount = 0;
        let newBal = parseBalance(claimRes.body);
        if (newBal == null) newBal = lastBalance;
        else lastBalance = newBal;

        printReward(reward, newBal);
        const wait = parseCooldown(claimRes.body) || 480;
        await tmr(wait + 2, 'Waiting...');
        continue;
      }

      const low = claimRes.body.toLowerCase();
      if (low.includes('invalid') || low.includes('expired') || low.includes('login')) {
        rejectCount++;
        if (rejectCount >= 3) {
          log('Session invalid, input ulang cookie...', 'wr');
          const ok = await promptNewCookie(cfg, jar);
          if (!ok) return;
          rejectCount = 0;
          continue;
        }
        await sleep(3000);
        continue;
      }

      rejectCount++;
      if (rejectCount >= 5) {
        log(`Terlalu banyak reject (${rejectCount}). Retry...`, 'wr');
        await tmr(30, 'Waiting...');
        rejectCount = 0;
        continue;
      }
      await sleep(3000);
    } catch (e) {
      log(`Error: ${e.message}`, 'er');
      await sleep(5000);
    }
  }
}

async function main() {
  let cfg = loadConfig();
  if (!cfg) {
    cfg = await setupWizard();
  } else {
    clear();
    bannerMain();
    log('Config loaded dari config.json', 'ok');
    log(`UA     : ${(cfg.userAgent || '').slice(0, 55)}...`, 'dbg');
    log(`Cookie : ${(cfg.cookie || '').slice(0, 40)}...`, 'dbg');
    await sleep(500);
  }

  const jar = new Jar();
  jar.loadFromString(cfg.cookie);

  process.on('SIGINT', () => {
    cleanupExecPy();
    process.stdout.write('\n');
    console.log(`${YEL}Dihentikan user.${RST}`);
    process.exit(0);
  });
  process.on('exit', cleanupExecPy);

  clear();
  bannerMain();
  console.log(`${WHT}Mode  : ${CYN}Auto Claim${RST}`);
  console.log(`${WHT}───────────────────────────────────────────────${RST}`);

  await runFaucet(cfg, jar);
}

main().catch((e) => {
  cleanupExecPy();
  console.log(`${RED}Fatal: ${e.message}${RST}`);
  process.exit(1);
});
