---
layout: default
lang: jp
title: テスト実行
nav_link: テスト実行
nav_level: 2
nav_order: 290
parent: success-guide
page_id: test-run
---

# 構成を確認するためのテスト実行

[前の節](setup_config_files.md) \| [目次に戻る](index.md) \| [次の節](monitoring.md)

User Sync を起動するには：

ウィンドウ:**python user-sync.pex ….**

Unix、OSX：**./user-sync ….**


次のコマンドを試してみてください。

	./user-sync –v            バージョンをレポート
	./user-sync –h            コマンドライン引数に関するヘルプ

&#9744; 上記 2 つのコマンドを試行して、機能していることを確認します（Windows のコマンドは多少異なります）。


![img](images/test_run_screen.png)

&#9744; 次に、1 ユーザーに限定して同期を試行し、テストモードで実行します。ディレクトリの数人のユーザーの名前を知っている必要があります。例えば、ユーザー bart@example.com について次のように試行します。


	./user-sync -t --users all --user-filter bart@example.com --adobe-only-user-action exclude

	./user-sync -t --users all --user-filter bart@example.com --process-groups --adobe-only-user-action exclude

上記の最初のコマンドは、1 ユーザーのみを（ユーザーフィルターによって）同期します。この結果、ユーザーの作成が試行されることになります。テストモード（-t）での実行のため、user-sync の実行でユーザーの作成が試行されるだけで、実際には作成されません。`--adobe-only-user-action exclude` オプションによって、アドビ組織に既に存在するユーザーアカウントの更新はおこなわれません。

上記の 2 番目のコマンド（--process-groups オプション付き）は、ユーザーを作成して、そのディレクトリグループにマップされているグループにユーザーを追加しようとします。ここでも、テストモードのため実際の処理はおこなわれません。既にユーザーが存在し、グループにユーザーが追加された場合には、user-sync はユーザーの削除を試行することがあります。その場合、次のテストはおこなわないでください。また、製品アクセスを管理するためにディレクトリグループを使用しない場合には、--process-groups に関連するテストを省いてください。

&#9744; 次に、1 ユーザーに限定して同期を試行します。テストモードで実行しません。実際にユーザーが作成されてグループに追加されるはずです（マッピングされている場合）。

	./user-sync --users all --user-filter bart@example.com --process-groups --adobe-only-user-action exclude

	./user-sync --users all --user-filter bart@example.com --process-groups --adobe-only-user-action exclude

&#9744; 次に、Adobe Admin Console に移動して、ユーザーが表示され、グループメンバーシップが追加されたかどうかを確認します。

&#9744; 次に、同じコマンドを再実行します。User Sync は、ユーザーの再作成とグループへの再追加をおこなわないはずです。ユーザーが既に存在していて、ユーザーグループまたは PC のメンバーであることを検知するのみです。

これらすべてが予期したとおりに実行された場合は、完全実行（ユーザーフィルターなし）をおこなう準備が整いました。ディレクトリのユーザー数が多すぎない場合は、すぐに試すことができます。数百を超える場合には、長くかかる可能性があるため、コマンドを長時間実行する準備ができるまでは実行しないでください。また、実行する前にこの後の節を読んで、関連するその他のコマンドラインオプションがないか確認してください。




[前の節](setup_config_files.md) \| [目次に戻る](index.md) \| [次の節](monitoring.md)

