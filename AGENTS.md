# wwwx.red — 給 AI 代理的專案說明

## 這是什麼

wwwx.red 官方網站。四段捲動：波浪 → 離散球 → 雜訊場 → 粒子寫成「紅品牌策略」。
九萬顆粒子、一個 draw call，全部位移在 vertex shader 裡算完。

原型參考 `C:\9.VibeCoding\TOOLS-DEV\hero-dust`（線上版 https://lab.realvco.com/hero-dust）。

## 唯一的產出檔案

`website/index.html` 是**完全自足的單一檔案** —— shader、樣式、內容全在裡面。
沒有建置步驟、沒有 npm 依賴。

`worker/index.js` 只是把它當文字模組匯入後回傳，所以**線上跑的就是同一份檔案**，
不存在「編譯後的版本」。

改動的細節、可調的旋鈕、綁在一起的數字，全寫在 `website/README.md`。動手前先讀。

## 發布分支與流程

**發布分支是 `main`。** 這個專案只有一個環境，`main` 上的內容就是線上內容。

正式環境：**https://wwwx.red**（`www.wwwx.red` 一律 301 轉正過來）

### 步驟

```bash
git push origin main
npx wrangler deploy
```

`npx wrangler deploy` 就能上線的原因：

- **認證**：wrangler 已在這台機器登入過（OAuth，kimfull@gmail.com）
- **打包**：`worker/index.js` 用 `import html from '../website/index.html'` 把 HTML 當
  **文字模組**吃進去（Wrangler 對 `*.html` 內建 Text 規則）
- **路由**：`wrangler.toml` 的四條 route 把 apex 與 www 都導到這個 worker

**部署完一定要實際開網址驗證，不要只相信部署訊息。** 而且要加查詢字串繞過邊緣快取
（worker 回 `cache-control: public, max-age=300`）：

```bash
curl -sSI "https://wwwx.red/?v=$(git rev-parse --short HEAD)"
```

route 或 DNS 改完到全球生效要幾十秒，中間量到的結果會自相矛盾。等 30 秒再驗。

### DNS 的前提

`wwwx.red` 與 `www.wwwx.red` 各要有一筆**已代理（橘色雲）**的 DNS 記錄，route 才會
被觸發。2026-08-20 之前 apex 是灰雲、指向一個 WordPress 站，所以 route 打不到它 ——
把記錄改成橘雲之後新站才正式上線。**wrangler 管不到 DNS**，那要在 Cloudflare 後台改。

## 驗收基準

改完 shader 或捲動邏輯，至少確認這四項：

| 項目 | 標準 |
|-|-|
| 四個停點的收斂進度 | hero≈0、core≈1、noise≈0、頁尾≈1 |
| GL 錯誤 | 0 |
| draw call | 1 |
| 捲到底 | 形狀剛好完成，內文接著就地淡入，不必再捲 |

除錯用的手把掛在 `window.__dbg`（renderer、uniforms、geometry、setShape 等）。

**注意**：形狀由捲動位置決定、每幀重讀。在主控台呼叫 `setShape()` 之後畫面會被
`readScroll()` 改回去 —— 要測就連 section 的 `data-shape` 一起改。

## 本機預覽

```bash
npx serve website -l 3210
```

`.claude/launch.json` 已設好（名稱 `wwwx-red-website`，port 3210）。

## 其他目錄

- `public/` — 字標與 favicon 的 SVG（已內嵌進 index.html，這裡留原始檔）
- `tools/` — 產生字標 SVG 的 Python 腳本
- `zzArchives/`、`zzTemping/` — favicon 與字標的探索過程，不影響網站
- `github-wwwx-red/` — 同一個 GitHub repo 的另一份工作副本，已在 `.gitignore` 裡
