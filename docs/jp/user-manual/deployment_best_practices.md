---
layout: default
lang: jp
nav_link: デプロイメントのベストプラクティス
nav_level: 2
nav_order: 70
---


# デプロイメントのベストプラクティス

## このセクションの内容
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[前のセクション](advanced_configuration.md)

---

User Sync ツールは、正しく構成された後、人の操作を全く必要としない、または限定的な状況で実行するよう設計されています。ご使用の環境にあるスケジューラーを使用して、必要な頻度でツールを実行できます。

- User Sync ツールの最初の数回の実行は、Adobe Admin Console に追加されるユーザーの数に応じて、時間がかかる場合もあります。タスクをスケジュール設定して実行する前に、複数のインスタンスが同時に実行されるのを避けるため、初期の実行は手動で実行するようお勧めします。
- その後の実行は通常、必要に応じてユーザーデータをアップデートするだけなので、より迅速に処理されます。User Sync を実行する頻度は、ユーザーのエンタープライズディレクトリが変更する頻度と、アドビ側に変更をどれだけ早く表示するかに依存します。
- User Sync の実行頻度が 2 時間に 1 回を超えることは推奨されていません。

## セキュリティの推奨事項

構成とログファイル内のデータの性質を考えると、サーバーはこのタスク専用にして、業界のベストプラクティスでロックダウンする必要があります。エンタープライズファイアウォールの内側にあるサーバーをアプリケーションのために準備することが勧められています。このマシンには権限を持つユーザーのみアクセスできるようにします。アプリケーションを実行してシステムにログファイルを書き込むことに特化した、権限が制限されたシステムサービスアカウントを作成する必要があります。

アプリケーションは、HTTPS エンドポイントに対して User Management API の GET および POST 要求をおこないます。Admin Console に書き込む必要がある変更を表す JSON データを構築し、User Management API への POST 要求の本文内のデータをアタッチします。

アドビのバックエンドユーザー ID システムの可用性を保護するために、User Management API はデータへのクライアントアクセスを制限します。制限はある期間内に個別のクライアントがおこなえる呼び出しの数に適用され、グローバル制限はある期間内にすべてのクライアントがおこなうアクセスに対して適用されます。User Sync ツールはバックオフと再試行ロジックを導入して、レートの上限に達したときにスクリプトが User Management API を継続的にヒットしないようにします。スクリプトが再度実行しようとする前に一時停止したことを示すメッセージがコンソールに表示されるのは正常です。

User Sync 2.1 から、資格情報の保護に使用できる 2 つの方法が追加されました。1 つ目は、オペレーティングシステムの資格情報ストアを使って個別の構成資格情報の値を格納します。2 つ目は、必要なすべての資格情報を含め、umapi または ldap、あるいはその両方の構成ファイル全体を安全に格納するために提供する必要があるメカニズムを使用します。これらは、次の 2 つの節で取り上げています。

### OS レベルストレージにおける資格情報の格納

Python Keyring OS 資格情報ストアから資格情報を取得するよう User Sync をセットアップするには、connector-umapi.yml および connector-ldap.yml ファイルを次のように設定します。

connector-umapi.yml

	server:
	
	enterprise:
	  org_id: your org id
	  secure_api_key_key: umapi_api_key
	  secure_client_secret_key: umapi_client_secret
	  tech_acct: your tech account@techacct.adobe.com
	  secure_priv_key_data_key: umapi_private_key_data

`api_key`、`client_secret`、および `priv_key_path` がそれぞれ `secure_api_key_key`、`secure_client_secret_key`、および `secure_priv_key_data_key` に変更されることに注目してください。これらの代替の構成値は、実際の資格情報の値を取得するためにユーザーキーチェーン（または他のプラットフォームでそれに相当するサービス）で検索するキーの名前を提供します。この例では、資格情報キー名は `umapi_api_key`、`umapi_client_secret`、および `umapi_private_key_data` です。

秘密キーファイルの内容は、資格情報ストアで `umapi_private_key_data` の値として使用されます。これは、Windows 以外のプラットフォームでのみ実行できます。Windows で秘密キーファイルをセキュリティ保護する方法については、以下を参照してください。

資格情報の値が、ユーザー名の値として org_id を使用して、またキー名として構成ファイル内のキー名を使用して、安全なストアで参照されます。

この方法のバリエーションとして、（User Sync バージョン 2.1.1 以降で）秘密キー用の標準的な RSA 暗号化表現を使用して、秘密キーファイルを暗号化できます（通称：PKCS#8 形式）。この方法は、Windows で使用する必要があります。これは、Windows の安全なストアでは、秘密キーでの使用を避けるために、512 バイトを超える文字列を格納することができないためです。この方法は、必要に応じて、他のプラットフォームでも使用することができます。

秘密キー暗号化された形式で格納するには、次の操作を実行します。まず、秘密キーファイルの暗号化されたバージョンを作成します。パスフレーズを選択し、秘密キーファイルを暗号化します。

    openssl pkcs8 -in private.key -topk8 -v2 des3 -out private-encrypted.key

Windows で Cygwin または他のプロバイダーの openssl を実行する必要があります。これは、標準の Windows 配布には含まれていません。

次に、connector-umapi.yml で次の構成アイテムを使用します。以下の最後の 2 つのアイテムではそれぞれ、暗号化解除パスフレーズが安全な資格情報ストアから取得され、暗号化された秘密キーファイルが参照されます。

	server:
	
	enterprise:
	  org_id: your org id
	  secure_api_key_key: umapi_api_key
	  secure_client_secret_key: umapi_client_secret
	  tech_acct: your tech account@techacct.adobe.com
	  secure_priv_pass_key: umapi_private_key_passphrase
	  priv_key_path: private-encrypted.key

最後に、エントリとして組織 ID にユーザー名または url を、`secure_priv_pass_key` 構成ファイルエントリと一致させるように `umapi_private_key_passphrase` としてキー名を使用して安全なストアにパスフレーズ、およびパスフレーズとしての値を追加します。（`priv_key_path` を使用する代わりに、キー `priv_key_data` 下の connector-umapi.yml ファイルにデータを配置することで、暗号化された秘密キーをインライン表示することもできます。

RSA 秘密キーの暗号化を使用したバリエーションの説明は以上です。

connector-ldap.yml

	username："ldap アカウントユーザー名"
	secure_password_key: ldap_password
	host："ldap://ldap サーバー名"
	base_dn："DC=ドメイン名、DC=com"

LDAP アクセスパスワードは指定したキー名
（この例では `ldap_password`）を使用して検索され、ユーザーは指定されたユーザー名構成値となります。

資格情報は、基盤となるオペレーティングシステムの安全なストアに保存されます。具体的なストレージシステムは、オペレーティングシステムによって異なります。

| OS | 資格情報ストア |
|------------|--------------|
| Windows | Windows Credential Vault |
| Mac OS X | Keychain |
| Linux | Freedesktop Secret Service or KWallet |
{: .bordertablestyle }

Linux では、OS ベンダーによって安全なストレージアプリケーションがインストールおよび構成されているはずです。

資格情報は、OS の安全なストレージに追加され、資格情報を指定するのに使用するユーザー名と資格情報 ID が付与されます。umapi の資格情報では、ユーザー名は組織 ID です。LDAP パスワード資格情報では、ユーザー名は LDAP ユーザー名です。特定の資格情報には任意の識別子を選択することができます。資格情報ストアにあるものと、構成ファイルで使用されている名前が一致する必要があります。推奨されるキー名の値は上の例に示されています。


### 外部管理システムにおける資格情報ファイルの格納

ローカルの資格情報ストアに資格情報を格納する代わりに、User Sync を他のシステムまたは暗号化メカニズムに統合することが可能です。このような統合をサポートするために、他のシステムや形式で umapi および ldap の構成ファイル全体を外部に保存することが可能です。

これをおこなうには、出力が umapi または ldap 構成ファイルのコンテンツとして使用される実行コマンドを、メインの User Sync 構成ファイルで指定します。提供するコマンドは、構成ファイルに含まれたはずのものと一致するよう、構成情報を取得して yaml 形式で標準出力に送信する必要があります。

これをセットアップするには、メインの構成ファイルで次のアイテムを使用します。


user-sync-config.yml（一部のファイルのみを表示）

	adobe_users:
	   connectors:
	      # umapi: connector-umapi.yml   # このファイル参照の代わりに次を使用：
	      umapi: $(read_umapi_config_from_s3)
	
	directory_users:
	   connectors:
	      # ldap: connector-ldap.yml # このファイル参照の代わりに次を使用：
	      ldap: $(read_ldap_config_from_server)
 
外部コマンド参照の一般的な形式：

	$(command args)

上記の例では、`read_umapi_config_from_s3` と `read_ldap_config_from_server` という名前のコマンドがすでに提供されていると仮定しています。

コマンドシェルが User Sync によって起動され、コマンドを実行します。コマンドからの標準出力がキャプチャされ、その出力は umapi または ldap 構成ファイルとして使用されます。

コマンドは、構成ファイルを含むディレクトリとして作業ディレクトリとともに実行されます。

コマンドが異常終了した場合、User Sync はエラーによって終了します。

コマンドは、新規または既存のプログラムやスクリプトを参照できます。

注：この手法を connector-umapi.yml ファイルで使用する場合、priv_key_data キーと秘密キーの値を使用して connector-umapi-yml を秘密キーに直接埋め込むようにします。priv_key_path および秘密キーを含むファイル名を使用する場合、秘密キーを安全な場所に格納し、ファイル参照でそれを取得するコマンドを容易する必要があります。

## スケジュール設定されたタスクの例

オペレーティングシステムが提供するスケジューラーを使用して、企業の要件に応じて、User Sync を定期的に実行することができます。次の例では、Unix と Windows のスケジューラーを構成する方法を示しています。

特定のパラメーターで UserSync を実行し、ログ概要を抽出して同期プロセスの監視担当者にそれを送信するようなコマンドファイルをセットアップするようにします。次の例は、コンソールログレベルが INFO に設定されている場合に最適に機能します。

```YAML
logging:
  console_log_level: info
```

### Windows でログ分析とともに実行

次の例では、バッチファイル `run_sync.bat` を Windows に設定する方法について示しています。

```sh
python C:\\...\\user-sync.pex --users file users-file.csv --process-groups | findstr /I "WARNING ERROR CRITICAL ---- ==== Number" > temp.file.txt
rem email the contents of temp.file.txt to the user sync administration
sendmail -s “Adobe User Sync Report for today” UserSyncAdmins@example.com < temp.file.txt
```

*注*：この例では `sendmail` の使用について示していますが、Windows には標準の電子メールのコマンドラインツールはありません。商業的に入手することができます。

### Unix プラットフォームでログ分析とともに実行

次の例は、シェルファイル `run_sync.sh` を Linux または MAC OS X でセットアップする方法について示しています。

```sh
user-sync --users file users-file.csv --process-groups | grep "CRITICAL\|WARNING\|ERROR\|=====\|-----\|number of\|Number of" | mail -s “Adobe User Sync Report for `date +%F-%a`” UserSyncAdmins@example.com
```

### UserSync タスクのスケジュール設定

#### Cron

Unix crontab の次のエントリは User Sync ツールを毎日 4:00 AM に実行します。

```text
0 4 * * * /path/to/run_sync.sh
```

cron では、特定のユーザーまたはメーリングリストに結果を電子メール送信するようにセットアップすることもできます。詳細については、ご使用のシステムの cron のドキュメントを参照してください。

#### Windows タスクスケジューラー

このコマンドでは Windows タスクスケジューラーを使用して、User Sync ツールを毎日 4:00 PM から実行します。

```text
schtasks /create /tn "Adobe User Sync" /tr C:\path\to\run_sync.bat /sc DAILY /st 16:00
```

詳細については、Windows タスクスケジューラーのドキュメント（`help schtasks`）を参照してください。

Windows スケジュールタスクを管理する GUI もあります。タスクスケジューラーは、Windows の管理コントロールパネルにあります。

---

[前のセクション](advanced_configuration.md)
