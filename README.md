
<div align="center">

# <img src="https://raw.githubusercontent.com/refiaa/WIS_Scraper/main/WIS_Scraper.ico" width="96" height="96"> </img> ***WIS Scraper***

<em><h5 align="center">(Programming Language - Python 3)</h5></em>

[![GitHub release](https://img.shields.io/github/release/refiaa/WIS_Scraper.svg?color=Green)](https://github.com/refiaa/WIS_Scraper/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/refiaa/WIS_Scraper/total?color=6451f1)](https://github.com/refiaa/WIS_Scraper/releases/latest)
[![WIS_Scraper issues](https://img.shields.io/github/issues/refiaa/WIS_Scraper?color=yellow)](https://github.com/refiaa/WIS_Scraper/issues)
[![WIS_Scraper License](https://img.shields.io/github/license/refiaa/WIS_Scraper?color=orange)](#)


WIS_Scraperは国土交通省の水文水質データベースからデータを検索・取得・ダウンロードするためのツールです。</br>
このプログラムはWindowsでの実行を想定しています。Macでの実行は検証されておりません。

## Getting Started

<div align="left">

### プログラムで利用したい方へ

この[ページ](https://github.com/refiaa/WIS_Scraper/releases/latest)からプログラムをダウンロードしてください。 

Virus TotalやWindows Defenderによりウイルス判定され、自動的に削除される場合があります。</br> これはウイルスではなく、Pyinstallerの問題で発生していて、実際のウイルスではありませんので安心してご利用ください。

**Virus Total File Hash Info**

**MD5**</br>
>166a2df4afb01727a8e5a8e5ef99875b</br>

**SHA-1**</br>
>eba0ecd07516f5685251d4dac48029213a4e7e56</br>

**SHA-256**</br>
>de7357cc4e1d1ebd90df7ab8b0fda3cedbd03ab894f1292595300bf71f1170d5</br>


## 
### コードで利用したい方へ

以下の順番に沿ってインストールしてください。

**Clone and Install Script**

```shell script
git clone https://github.com/refiaa/WIS_Scraper.git
cd WIS_Scraper
pip install -r requirements.txt
```
そのあと***WIS_InfoWindow.py***を実行してください。</br>
ファイルのディレクトリ構造は以下のようになります。

**File Tree Structure**
```shell script
WIS_Scraper
├─img
├─json
└─src
```

<div align="center">

## How To Use

<div align="left">

![2024-01-07 132820](https://github.com/refiaa/WIS_Scraper/assets/112306763/a695c404-20e2-40fb-8d12-6c931725464b)

水文水質データベースの使い方と一緒です。条件を選択し、実行することで検索できます。右下の「前」「次」をクリックすることで次・前のページに移動することができます。

![2024-01-07 132912](https://github.com/refiaa/WIS_Scraper/assets/112306763/08e22878-8392-4d19-9663-2962364b30c5)

詳細情報をクリックすると、次のような画面になります。

![2024-01-07 132934](https://github.com/refiaa/WIS_Scraper/assets/112306763/491bdbb0-4d98-4c2f-ac9a-43b1ac60e3e2)

観測情報ウィンドウでは、日付や年度の範囲を決め、Download Dataをクリックすることで、データの自動ダウンロードができます。

現在は雨量だけに対応してます。

## Update Log

### 240107.2146
```
・プログラムがリリース(VER.240107-1305)されました。
・雨量に対する対応作業が終わりました。
・Readmeをアップデートしました。
```
