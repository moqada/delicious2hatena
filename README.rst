delicious2hatena
================

Deliciousに投稿した内容をメール経由ではてブに投稿します。

追加したタグやコメントもはてブの方に反映されます。

インストール
------------

::

   git clone https://github.com/moqada/delicious2hatena

必要条件
--------

- Python 2.7 以上

使い方
------

適当なディレクトリに配置して適当にPythonで叩くだけです。

ホームディレクトリなどに以下のような設定ファイル(.d2h)を書いて置くと楽になります。

.. code-block:: ini

   [delicious]
   ; deliciousのユーザ名
   username = mokada
   ; deliciousのパスワード
   password = pass

   [mail]
   ; はてブから取得した投稿用メールアドレス
   to_addr = example@hatena.ne.jp
   ; はてブに送信するときの送信元アドレス
   from_addr = hatebu@example.com

   ; メール送信にGmailを利用する場合
   [gmail]
   ; Gmailのユーザ名
   username = gmail@example.com
   ; Gmailのパスワード(2段階認証が有効の場合はアプリケーション固有のパスワード)
   password = pass

   
コマンド例
~~~~~~~~~~

30分前以降にDeliciousに投稿した内容を送信する(~/.d2hが存在する場合)::

   python d2h.py 30


個別に設定ファイルを指定できます::

   python d2h.py 30 --config=/path/to/.d2h


設定ファイルがなくても直接指定できます::

   python d2h.py 30 --delicious-username=mokada --delicious-password=pass --hatebu-address=example@hatena.ne.jp --from-address=hatebu@example.com


crontabに設定しておくと便利です::

   PYTHONIOENCODING=utf-8
   # 1時間に1回Deliciousの投稿をはてブに投稿する
   0 * * * * python /path/to/d2h.py 60
