# Network Topology Widget — VirtualHelpDesk Dashboard

`app.py` / `dashboard.html` / `base.html` を見た上で、既存の構成（Blueprint不使用、`services/device_service.py` の `get_switch_catalog()` / `get_network_topology()` 等をそのまま再利用、静的ファイルは `static/src/css` / `static/src/javascript`）に合わせて作ってあります。

配置場所は **Dashboardの「Operations Center」見出し・サブタイトルの直下、Active Alertsカードの直前** です（Alertより上＝ネットワーク監視が最初に目に入るように）。

まずは `demo/network_diagram_demo.html` をブラウザで直接開いて動作を確認してください（サーバー不要）。

## できること

- NYC（Accounting）と LAX（IT / HR / Marketing / Operations）を、Router → Core L3 Switch → Access Switch → PC群 / Printer群 / File Server というツリーで可視化。中央上に MPLS クラウドを置き、NYCRTR01・LAXRTR01 と接続
- ホバーで機器の詳細（IP、ファームウェア、帯域、遅延、利用率など）をツールチップ表示
- **ダブルクリック**で機器をオフライン化 → 配下は経路を再計算して自動的に「到達不能」表示にカスケード（単純な色替えではなく、実際にBFSで到達性を判定しています）
- **ケーブルをクリック**で断線（severed）扱いに → 同様にカスケード
- フッターの共有フォルダパネルが `network_drive_catalog` の `server` 列と連動し、NYCSERVER01への経路が切れると `\\NYCSERVER01\Accounting Shared` が自動的に「ACCESS DENIED」表示になります
- ズーム／パン、全画面拡大、シミュレーション状態のリセットに対応

PC・プリンタは台数が多い（50台以上）ため部署ごとの集約ノード（台数バッジ付き）として表示しています。タイトル直下という限られたスペースで個別ホスト単位のアイコンを並べると視認性が落ちるための判断です。

## データの不整合について

`network_topology.csv` は NYC/LAX のコアスイッチを `NYCCOREL3-01` / `LAXCOREL3-01`（ハイフンなし）と表記していますが、`switch_catalog.csv` では `NYCCORE-L3-01` / `LAXCORE-L3-01`（ハイフンあり）です。このままだと `source_device`/`destination_device` が `switch_catalog.device_id` と一致せずグラフが繋がらないため、`services/network_topology_service.py` 内の `_norm()` で正規化しています。CSVを直接編集する場合はハイフンありの表記に統一してください。

## ファイル構成

```
app/app.py                          いただいたapp.pyに差分を反映済みの完成形（そのまま置き換え可能）
app/network_topology_service.py     グラフ組み立て + devices テーブルへのカスケード書き込みロジック
static/src/css/network-diagram.css        ウィジェットのスタイル（NOC風ダークテーマ、依存なし）
static/src/javascript/network-diagram.js  描画・インタラクション（vanilla JS、依存なし）
static/src/javascript/network-live-sync.js  Alert/Device Status/Risk表をリロードなしで更新
templates/partials/_network_diagram.html  dashboard.htmlにincludeするパーツ
templates/dashboard.html            配置済みの完成形（include1行 + id属性を数カ所追加した差分）
demo/network_diagram_demo.html      スタンドアロンのプレビュー（ブラウザで直接開けます）
demo/sample_topology.json           デモが読み込むサンプルデータ（アップロードいただいたCSVから生成済み）
build_topology.py                   CSV一式 → topology.json を生成するオフラインスクリプト（デモデータ再生成用。本番では不要）
```

`app/app.py` は元の `app.py` に対して以下だけを足したものです（それ以外は一切変更していません）：
- `from services.network_topology_service import get_network_topology_graph, set_device_override, set_link_override, reset_overrides`
- `/api/network/topology`、`/api/network/device/<id>/status`、`/api/network/link/<id>/status`、`/api/network/reset`、`/api/dashboard/summary` の5ルート

`switch_catalog` / `network_topology` テーブルは既に `db_init.py` / `inventory_import.py` 側で作成・投入済みという前提なので、SQLスキーマやCSV投入スクリプトは含めていません。ウィジェットが新規に使うのは「シミュレーション状態を保存する」ための `network_override` テーブルだけで、これは `network_topology_service.py` が初回アクセス時に自分で `CREATE TABLE IF NOT EXISTS` するので、`db_init.py` を触らなくても動きます（Renderの再デプロイでディスクがリセットされても、次回アクセス時に自動で作り直されます）。

## 組み込み手順

1. **ファイルをコピー**
   - `app/app.py` → プロジェクト直下の `app.py` をこれで置き換え（いただいた最新の `app.py` に差分を反映済みです）
   - `app/network_topology_service.py` → `services/network_topology_service.py`
   - `static/src/css/network-diagram.css` → 既存の `static/src/css/` 配下
   - `static/src/javascript/network-diagram.js` → 既存の `static/src/javascript/` 配下
   - `static/src/javascript/network-live-sync.js` → 既存の `static/src/javascript/` 配下
   - `templates/partials/_network_diagram.html` → `templates/partials/` 配下（`partials/` フォルダが無ければ作成）

2. **`dashboard.html`**
   同梱の `templates/dashboard.html` は、元のファイルに以下の1行を足しただけです（差分はこれだけなので、既存ファイルへの反映も手動で十分です）:
   ```jinja
   <h2>Operations Center</h2>
   <p>Real-time Endpoint Monitoring & Compliance Dashboard</p>

   {% include "partials/_network_diagram.html" %}

   <div class="alert-wrapper">
   ```

3. `demo/network_diagram_demo.html` で先に見た目を確認してから本組み込みするのがおすすめです。

## レイアウトについて

ノード座標は `network_topology_service.py` 内の `POSITIONS` に手動で定義した固定レイアウトです（force-directedだと毎回揺れて見た目が安定しないため、NOC図らしく決め打ちにしています）。将来デバイスが増えたら、この dict に座標を追加してください。

## デザイン・実装メモ

- CSS変数（`--nd-*`）で色を一元管理しているので、既存のダーク/ライトテーマ切り替え機構に合わせて上書きしたい場合はそこだけ触れば済みます。
- `<link>` と `<script>` を `_network_diagram.html` 内に直接置いていて、`base.html` の `extra_css` / `extra_js` ブロックは使っていません（部品として独立させたかったため）。気になる場合は `dashboard.html` の `extra_css`/`extra_js` ブロック側に移してもらってもそのまま動きます。
- `network-diagram.js` は依存ライブラリなしの素のJSです。Chart.jsなど他のJSと衝突しません。

## ダッシュボード本体（Active Alerts / Risk Devices / Device Status）との連動

`dashboard_service.py` と `alertboard_service.py` を見た結果、どちらも `devices.status` を直接SQLで参照しているだけだったので、**ネットワーク図のトグルが実際に `devices` テーブルを書き換える**ようにしました。`dashboard_service.py` / `alertboard_service.py` 側のコードは一切変更していません。

### 仕組み

1. スイッチやケーブルをオフライン/断線にすると、`network_topology_service.py` がサーバー側でも同じ到達性判定（BFS）を行い、その結果「到達不能」になった部署のPC群を特定します
2. 該当する `devices.hostname` の**元の `status` 値を `device_status_backup` テーブルに退避**した上で、`devices.status` を `'Offline'` に書き換えます
3. スイッチ/ケーブルを元に戻すと、`device_status_backup` から元の値を復元し、退避テーブルの該当行を削除します
4. `dashboard_service.py` の `get_dashboard_summary()` / `get_risk_devices()` / `get_device_status_summary()` は毎リクエストで `devices` テーブルを再SELECTしているだけなので、これだけで Active Alerts・Risk Devices・Device Status チャートすべてに自動で反映されます

実際のデータを一時的に上書きしますが、退避テーブルのおかげで元の値を失うことはありません（Renderの再デプロイでリセットされた場合も、`network_override` テーブルと同様に自動で作り直されます）。

### リロード不要のライブ更新

- `GET /api/dashboard/summary` を追加しました。`/dashboard` ルートが描画時に使っているのと同じ関数（`get_dashboard_summary()` / `generate_alertboard()` / `get_risk_devices()` / `get_device_status_summary()`）を呼んで、JSONで返すだけです
- `static/src/javascript/network-live-sync.js` の `refreshDashboardLive()` が、この結果を使ってDOMを直接書き換えます:
  - Active Alertsの数値
  - Alert Breakdownのメッセージ一覧
  - Managed Devicesの数値
  - `complianceChart` / `riskBreakdownChart` / `deviceStatusChart` の3つのChart.jsグラフ(`Chart.getChart(canvas)` というChart.js標準のレジストリ機能でインスタンスを取得しているので、`dashboard.js` の中身を一切知らなくても更新できます)
  - Risk Devicesテーブルの行
- ネットワーク図でダブルクリック/ケーブルクリックする → `/api/network/device(or link)/.../status` へPOST → 保存が終わったタイミングで自動的に `refreshDashboardLive()` が呼ばれる、という流れなので、**ページをリロードしなくても即座に反映されます**

これで動かない/対象外にしたい部分がある場合(例: Patch Trend系の3グラフは今回意図的に対象外にしています。パッチ適用状況は本来ネットワーク到達性と無関係なデータのため)、`network-live-sync.js` の `updateChart(...)` 呼び出しを増減してください。
