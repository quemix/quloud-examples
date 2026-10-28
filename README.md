# Quloud Examples

## 環境構築
HTMLのビルドにはSphinxとRTDテーマを使う。公開用のビルド（GitHub Actions）と同じ版をPython環境にインストールする。
```
python -m pip install -r requirements.txt
```

内部の作業方針や記録は、公開リポジトリに含めず、非公開の
`quloud-examples-meta`リポジトリを隣のディレクトリにチェックアウトして管理する。
初回のみ、`quloud-examples`のルートで次を実行する。

```
git clone git@github.com:quemix/quloud-examples-meta.git ../quloud-examples-meta
make meta-link
make agent-link
```

`meta/`と`AGENTS.md`は`.gitignore`対象。metaの内容や履歴を公開リポジトリへコピーしない。


## GitHub (clone)　→　編集・更新　→　GitHub (push)
更新を行った内容を`main`ブランチにマージすると、GitHub Actions（`.github/workflows/pages.yml`）がHTMLをビルドし、GitHub Pagesで公開する。生成したHTMLはリポジトリにコミットしない。そのため更新は、

- まず適当なブランチ名で本リポジトリにプッシュ
- プッシュしたブランチを`main`ブランチにマージする

という手順で行うようにする。

### クローン ###
自分のPC上で下記のコマンドを実行する。
```
$ git clone git@github.com:quemix/quloud-examples.git
```
そうすると`quloud-examples/`というフォルダができるはずなので、その中で編集作業を行う。ただし、そのままではブランチが`main`になっているので
```
$ git checkout -b 作業用ブランチ名
```
として、適当なブランチの中で作業するようにしておく。

### 編集 ###
`*.rst`というファイルがドキュメントのメインになる。ここに、Sphinxのマークダウン記法で書いていく。Latexのような記法で数式や表を書くこともできる。画像はもちろん、生のHTMLやJavascriptを埋め込むこともできる。

### 更新 ###
`quloud-examples/`下で、
```
$ make html
```
を実行すると、`_build/html/`フォルダにhtmlファイルが生成される。これは手元での確認用で、コミットされない（`.gitignore`対象）。
```
$ make serve
```
を実行してブラウザで http://localhost:8000 を開くと、生成したページを確認できる（Ctrl+Cで終了）。`*.rst`ファイルをまたぐ参照等を追加した場合には、一度全体をクリーン
```
$ make clean
```
してから、改めて`make html`を実行する。

### コミット ###
修正が入ったファイルや新規に追加されたファイル（`*.rst`、図、データなど）をgitに追加＆コミットする
```
$ git add ファイル名
$ git commit
```

### プッシュ ###
コミットした変更をGitHubの方に戻す（プッシュする）
```
$ git push origin 作業用ブランチ名
```
手元で「作業用ブランチ名」という名前をリモート（GitHubリポジトリ上）では別の名前にすることも可能だが、上記のように書けば、手元で作業していたブランチ名のままリモートにプッシュされる。

### メインブランチへのマージ ###
GitHub上の「Pull Request」から、`main`ブランチへのマージを行えば、あとは自動で、GitHub Actionsがビルドして公開する。進み具合や失敗はGitHubの「Actions」タブで確認できる。
