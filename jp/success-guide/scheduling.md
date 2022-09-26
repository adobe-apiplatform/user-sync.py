---
layout: default
lang: jp
nav_link: スケジューリング
nav_level: 2
nav_order: 320
parent: success-guide
page_id: scheduling
---

# User Sync を継続実行するスケジュールのセットアップ


[前の節](command_line_options.md) \| [目次に戻る](index.md)

## Windows でのスケジュール実行のセットアップ

まず、user-sync を起動してスキャンにパイプで渡し、まとめのために関連するログエントリを引き出すバッチファイルを作成します。このために、次のような内容を含むファイル run_sync.bat を作成します。

	cd user-sync-directory
	python user-sync.pex --users file example.users-file.csv --process-groups | findstr /I "==== ----- WARNING ERROR CRITICAL Number" > temp.file.txt
	rem email the contents of temp.file.txt to the user sync administration
	your-mail-tool –send file temp.file.txt


Windows には電子メールのための標準コマンドラインツールはありませんが、市販のツールがいくつかあります。
特定のコマンドラインオプションを入力する必要があります。

このコードでは Windows タスクスケジューラーを使用して、User Sync ツールを毎日 4:00 PM から実行します。

	C:\> schtasks /create /tn "Adobe User Sync" /tr path_to_bat_file/run_sync.bat /sc DAILY /st 16:00

詳細については、Windows タスクスケジューラーのドキュメント（help schtasks）を参照してください。

スケジュール設定されたタスクをセットアップする際によく発生するのは、コマンドラインで機能するコマンドが、現在のディレクトリまたはユーザー ID が異なるために、スケジュール設定されたタスクでは機能しないという問題です。スケジュール設定されたタスクを最初に試行するときは、テストモードコマンドの 1 つを実行することをお勧めします（「テスト実行」の節を参照）。


## Unix ベースのシステムでのスケジュール実行のセットアップ

まず、user-sync を起動してスキャンにパイプで渡し、まとめのために関連するログエントリを引き出すシェルスクリプトを作成します。このために、次のような内容を含むファイル run_sync.sh を作成します。

	cd user-sync-directory
	./user-sync --users file example.users-file.csv --process-groups |  grep "CRITICAL\\|WARNING\\|ERROR\\|=====\\|-----\\|number of\\|Number of" | mail -s “Adobe User Sync Report for `date +%F-%a`” 
    Your_admin_mailing_list@example.com


特定の User Sync コマンドラインオプションと、レポートの送信先の電子メールアドレスを入力する必要があります。

Unix crontab の次のエントリは User Sync ツールを毎日 4 AM に実行します。

	0 4 * * *  path_to_Sync_shell_command/run_sync.sh

cron では、特定のユーザーまたはメーリングリストに結果を電子メール送信するようにセットアップすることもできます。詳細については、ご使用の Unix システムの cron のドキュメントを参照してください。

スケジュール設定されたタスクをセットアップする際によく発生するのは、コマンドラインで機能するコマンドが、現在のディレクトリまたはユーザー ID が異なるために、スケジュール設定されたタスクでは機能しないという問題です。スケジュール設定されたタスクを最初に試行するときは、テストモードコマンドの 1 つを実行することをお勧めします（「テスト実行」の節を参照）。


[前の節](command_line_options.md) \| [目次に戻る](index.md)

