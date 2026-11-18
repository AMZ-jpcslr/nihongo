![nihongo — あなたのAIをネイティブに。](assets/nihongo-hero.png)

# nihongo

[![v2.2.0](https://img.shields.io/badge/-v2.2.0-D7261E?style=flat-square)](CHANGELOG.md)
[![stars](https://img.shields.io/github/stars/AnIT012/nihongo?style=flat-square&labelColor=111111&color=D7261E)](https://github.com/AnIT012/nihongo/stargazers)
[![license](https://img.shields.io/badge/license-MIT-D7261E?style=flat-square&labelColor=111111&color=D7261E)](LICENSE)
[![works with](https://img.shields.io/badge/works_with-Claude_%7C_ChatGPT_%7C_Codex_%7C_Muse-D7261E?style=flat-square&labelColor=111111&color=D7261E)](#インストール)

実はこのREADME、nihongoを入れたAIが全部書いています。人の手では1文字も直していないので、AIっぽいと感じた所があったらIssueで教えてください！

nihongoは、AIが書く日本語を人が書く文に近づけるエージェントスキルです。書いた文を後から直すだけでなく、メール、お知らせ、Slack、README、ES、意見文などを書く時から使えます。

## まず試す（Claude Code）

```
npx skills add AnIT012/nihongo -g -a claude-code
echo '@~/.claude/skills/nihongo/ALWAYS.md' >> ~/.claude/CLAUDE.md
```

1行目でスキルを入れ、2行目で `CLAUDE.md` の最後に1行足して、Liteが毎回読み込まれるようにします。メールや資料を書く時はFullが自動で使われ、それ以外で使いたい時は「nihongoで直して」と頼むか `/nihongo` と送ります。更新は `npx skills update nihongo -g` です。Codex、Muse、Claude・ChatGPTのアプリでの入れ方は[インストール](#インストール)にあります。

## 特徴

AIの日本語の違和感は、決まった言い回しだけから出るわけではありません。相手との距離に合わない敬語や中身のない前置き、1文ずつは正しいのに続けて読むと細切れになる文章もその一つです。nihongoは禁止語を並べる代わりに、読み手・目的・載せる場所・書き手から、その場にいる人ならどう書くかを判断する手順をまとめています。

- お知らせ・お詫び・目上への文は硬い言葉と定型の敬語を残し、くだけた言い方に崩すのは友達とのやりとりだけにする
- 中身のない言葉（活用、実現、本質的）は普通の動詞に戻し、宣伝文の勢いや本人の気持ちの言葉は残す
- 文を分けるかつなげるかを句点の数ではなく、情報のまとまりと流れで決める
- 読点は、読み違えそうな所と長い前置きの後にだけ打ち、短い文の頭の「今日は、」のような読点は打たない
- 自然な文は無理に直さず、数字・日付・条件・誰が何をするかは変えない
- 依頼に無い感想・理由・約束は書き足さず、足りない所は書いたあとで1つだけ聞く

## 使用例

AIが書いたSlackの投稿です。

```
@channel お疲れさまです！

本日のデプロイについて共有させていただきます🚀

**結論**：本日18時のリリースは予定どおり実施します。

**背景**：昨日発見された決済画面の不具合は、すでに修正済みであり、ステージング環境での検証も完了しております。

**お願い**：18時〜18時30分の間は、本番環境への変更を控えていただけますと幸いです。

ご不明点等ございましたら、お気軽にスレッドにてお知らせください！引き続きよろしくお願いいたします🙏
```

nihongoで直すと、こうなりました。

```
@channel お疲れさまです！
本日18時のリリースは予定どおり実施します🚀

昨日見つかった決済画面の不具合は修正済みで、ステージング環境での検証も完了しています。

**18時〜18時30分は、本番環境への変更を控えてください。**

不明点があればスレッドでお知らせください。よろしくお願いします🙏
```

「結論：」「背景：」のようなラベルを外し、社内のチャットには重すぎる「させていただきます」「いただけますと幸いです」をチームに向けた普通の言い方にしています。日時やお願いの中身は変えていません。

## LiteとFull

nihongoには、毎回読み込む短いLiteと、詳しい手順が入ったFullがあります。両方入れておけば、普段はLiteだけを使い、人に出す文章を書く時だけFullまで読みます。

| | Lite | Full |
|---|---|---|
| ファイル | `nihongo/ALWAYS.md` | `nihongo/SKILL.md` と `references/` |
| 使う場面 | 普段の返事、雑談、短い質問 | メール、お知らせ、ES、資料、README、UIの文言 |
| 読み込まれ方 | 設定に入れておけば毎回 | 人に出す文章を書く時に自動で。名前を出して呼ぶこともできる |
| 増えるトークン（目安） | 約2,000 | 約10,000（使う時だけ） |

## インストール

スキルを入れる手順と、Liteを設定に入れる手順の2つです。スキルを入れただけだと、Fullは必要だとAIが判断した時にしか読まれず、短い返事や雑談ではまず読まれません。

<details>
<summary><b>Claude Code</b></summary>

```
npx skills add AnIT012/nihongo -g -a claude-code
echo '@~/.claude/skills/nihongo/ALWAYS.md' >> ~/.claude/CLAUDE.md
```

1行目は、GitHubからスキルを取ってきて `~/.claude/skills/` に入れるコマンドです。`-g` で自分のユーザー全体に入れ、`-a claude-code` でClaude Codeを入れ先に指定します。`-a` を付けないと途中で入れ先を聞かれるので、一覧の下の方にある Claude Code をスペースキーで選んでください。選ばないと `~/.agents/skills/` にだけ入り、Claude Codeからは見えません。

2行目は、毎回読み込まれる設定ファイル `~/.claude/CLAUDE.md` に、Liteを読み込む1行を足すコマンドです。`-g` を付けずにプロジェクトに入れた場合は、プロジェクトの `CLAUDE.md` に `@.claude/skills/nihongo/ALWAYS.md` と書いてください。

</details>

<details>
<summary><b>Codex</b></summary>

```
npx skills add AnIT012/nihongo -g
```

入れ先を聞かれたら Codex を選びます。Liteを入れるには、`ALWAYS.md` の中身を `~/.codex/AGENTS.md` かプロジェクトの `AGENTS.md` にそのまま貼ってください。

</details>

<details>
<summary><b>Muse</b></summary>

Museは `~/.claude/skills/` や `~/.agents/skills/` のスキルも読むので、上の `npx skills add` で入れたスキルがそのまま見えるはずです。`nihongo/` フォルダをスキルの置き場にそのまま置くと、スキルとして読み込めたと報告をいただきました（Issue #15）。Liteを入れるには、`ALWAYS.md` の中身を会話のたびに読み込まれる `AGENTS.md` に貼ってください。

SKILL.md の形式に対応したほかのエージェント基盤でも、同じようにフォルダを置くと使えることがあります。

</details>

<details>
<summary><b>ClaudeやChatGPTのアプリ</b></summary>

`nihongo/` フォルダをzipにまとめて、スキルの画面からアップロードしてください。ChatGPTでは、Skills の Create から「Upload from your computer」を選びます。Liteを入れるには、`ALWAYS.md` の中身を設定にあるAIへの指示や好みを書く欄にそのまま貼ってください。

</details>

### 使い方と更新

Liteを入れていれば、メールや資料を書く時は自動でFullが使われます。ほかの場面で使いたい時は「nihongoで直して」と頼むか、Claude Codeなら `/nihongo` と送ってください。

```
npx skills update nihongo -g
```

入れたスキルを最新の版にするコマンドです。手元のファイルが何版かは、`ALWAYS.md` の1行目か `SKILL.md` の先頭の `version` で確かめられます。

Pythonが使える環境では、推敲の最後にスクリプトで意味の崩れを照らし、書いた文から要らない読点を外します。Pythonが無くても、スキルはそのまま使えます。

## 自分の書き方に合わせる

`nihongo/references/personal-profile.md` に一人称や口ぐせ、好みの硬さ、避けたい言い回しを書いておくと、LINEやメールなど自分の名前で出す文がその書き方になります。自分で直した文の前と後を表に足していくと、その直し方が一番の基準として使われます。設定の指示やほかの文体のスキル、会話での指定と食い違う所は、ユーザーの書き方の方を優先します。

## 評価

2.2.0を推敲用に作られた別のスキル（最新版）と同じ10題で比べた結果です。判定は別のAIが目隠しで行い、依頼どおりかを最優先に見ました。

| 見た点 | 結果 |
|---|---|
| 依頼どおりか（頼んだ中身がそろい、本人の経験や約束を作っていないか） | 2回の審査とも、LiteとFullの両方でnihongoが勝ち越し |
| 依頼に無い事実を作った案 | nihongoは0件。作ったのは別のスキルだけ |
| 自然さ | 2回の審査とも、別のスキルが勝ち越し |
| 10題を書いた時に増えたトークン | Fullは約1.9万、別のスキルは約4.1万 |

依頼に無いことを書かない点ではnihongoが強く、文の生き生きした感じでは別のスキルが上でした。自然さは次の版で伸ばしていきます。

これまでに目隠しで比べた組は、合わせて約1,400組あります。判定したのは作者1人か同じ会社のAI（書き手はClaude Sonnet 5.5、判定はClaude Opus 5.5）なので、数字は目安として見てください。ChatGPTとCodexのモデルでは、まだ同じ検証をしていません。版ごとの結果と課題の原文は [evaluations/](evaluations/) にあります。

## ファイル構成

| ファイル | 内容 |
|---|---|
| `nihongo/ALWAYS.md` | Lite。普段の返事で毎回守る決まりと、Fullを読む場面 |
| `nihongo/SKILL.md` | Full。判断の優先順位、書く時と直す時の手順、読点と文のリズム |
| `nihongo/references/` | 場面ごとの資料（会話、LINE・Slack、メール、お知らせ、UIの文言、スライド、技術文書、ES、エッセイ、スピーチ、翻訳、敬語など）。その場面の文章を書く時だけ読みます |
| `nihongo/references/personal-profile.md` | 自分の書き方を書き込むひな形 |
| `nihongo/scripts/` | 意味が変わった文だけを原文に戻すスクリプトと、要らない読点を外すスクリプト（どちらも標準ライブラリだけで動く） |
| `tests/` | スクリプトの回帰テスト |
| `evaluations/` | 検証の記録と課題の原文 |
| `CHANGELOG.md` | すべての版の変更点 |
| `CONTRIBUTING.md` | 直した文の実例や不具合の送り方 |

## 変更履歴

- 2.2.0（2026-11-18）：要らない読点を打たずに書けるようになりました。一人称や口ぐせを自分に合わせて書けるようになり、Museでの入れ方をREADMEに追加しました。
- 2.1.4（2026-11-18）：伏字や時刻の変更など、頼まれた直しを戻してしまう所を直しました。
- 2.1.3（2026-11-18）：いただいた報告をもとに、意味の崩れを照らすスクリプトを直しました。

それより前の版と細かい内容は [CHANGELOG.md](CHANGELOG.md) にあります。版の付け方は、使い方が変わる大きな更新が1桁目、決まりの追加や改善が2桁目、細かい直しが3桁目です。

## 注意事項

nihongoの本体はMarkdownの文章で、AIが手順を読んで判断する作りです。そのため、同じ依頼でも毎回まったく同じ文になるとは限りません。`scripts/` のPythonは推敲の後に意味の崩れを確かめるためだけに使います。

内容の正しさまでは保証しないので、数字や日付、固有名詞は送る前に自分の目で確認してください。

## 制作について

Claude（Anthropic）と一緒に作りました。方針を決め、ルールの一部を書き、目隠しの判定で採用するかを決めたのは作者です。

## ライセンス

MIT Licenseで、詳しくは `LICENSE` に書いてあります。
