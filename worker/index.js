/* wwwx.red 官網的部署載體。
 *
 * website/index.html 是**打包時當成文字模組 import 進來的**（Wrangler 對
 * *.html 內建就有 Text 規則），所以整個專案只有一份 index.html，線上跑的
 * 就是它，不存在「編譯後的版本」。改用 static assets 的話得先把檔案複製到
 * 另一個目錄，那份複本遲早會和本尊不一致。
 *
 * 路徑不做判斷：這個 worker 只掛在 wwwx.red 自己的路由下，進得來的請求
 * 就是要看這一頁。路徑規則寫在 wrangler.toml，不要在程式裡再寫死一次。
 * **主機名要判斷**：www 一律轉正，理由見下。
 */
import html from '../website/index.html';

// 正式主機名。www 那個只負責把人送過來，不自己出內容
const CANONICAL = 'wwwx.red';

export default {
  fetch(request) {
    const url = new URL(request.url);

    /* www.wwwx.red → wwwx.red，帶著原本的路徑與查詢字串。
       用 301 不用 302：這是永久決定，讓瀏覽器和搜尋引擎都記起來，
       同一份內容也才不會有兩個網址在互相稀釋。 */
    if (url.hostname === 'www.' + CANONICAL) {
      url.hostname = CANONICAL;
      return Response.redirect(url.toString(), 301);
    }

    return new Response(html, {
      headers: {
        'content-type': 'text/html; charset=utf-8',
        // 五分鐘：改版後不必等太久，也不會每次都回源
        'cache-control': 'public, max-age=300',
      },
    });
  },
};
