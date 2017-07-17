---
layout: default
lang: jp
nav_link: User Sync の構成
nav_level: 2
nav_order: 30
---

# User Sync ツールの構成

## このセクションの内容
{:."no_toc"}

* TOC Placeholder
{:toc}

---

[前のセクション](setup_and_installation.md)  \| [次のセクション](command_parameters.md)

---

User Sync ツールの操作は、これらのファイル名を持つ構成ファイルのセットによって制御され、コマンドラインの実行可能ファイルと同じフォルダー（デフォルト）に置かれています。

| 構成ファイル | 目的 |
|:------|:---------|
| user-sync-config.yml | 必須。アドビ製品構成およびユーザーグループへのディレクトリグループのマッピングを定義し、アップデート動作を制御するための構成オプションが含まれます。また、他の構成ファイルへの参照も含まれます。|
| connector&#x2011;umapi.yml&nbsp;&nbsp; | 必須。アドビのユーザー管理 API を呼び出すための資格情報とアクセス情報が含まれます。 |
| connector-ldap.yml | 必須。エンタープライズディレクトリにアクセスするための資格情報とアクセス情報が含まれます。 |
{: .bordertablestyle }

アクセスを付与された他の組織にアドビグループへのアクセスをセットアップする場合、追加の構成ファイルを含めることができます。詳しくは、「[詳細な構成の手順](advanced_configuration.md#他の組織のグループへのアクセス)」を参照してください。

## 構成ファイルのセットアップ

3 つの必須ファイルのサンプルが、リリースアーティファクト `example-configurations.tar.gz` にある `config files - basic` フォルダーに提供されています。

```text
1 user-sync-config.yml
2 connector-umapi.yml
3 connector-ldap.yml
```

独自の構成を作成するには、サンプルファイルを User Sync のルートフォルダーにコピーし、名前を変更します（先頭の番号を削除するため）。コピーした構成ファイルをご使用の環境や使用モデルにカスタマイズするには、プレーン テキストエディターを使用します。例には、利用可能なすべての構成アイテムを示すコメントが含まれています。使用する必要があるアイテムのコメントを解除することができます。

構成ファイルは、[YAML 形式](http://yaml.org/spec/)になっており、`yml` サフィックスを使用します。YAML を編集する場合には、次の重要なルールにご注意ください。

- ファイルのセクションと階層はインデントに基づいています。インデントには空白文字を使用する必要があります。タブ文字は使用しないでください。
- ダッシュ文字（-）は、値のリストを形成するために使用します。次の例では、2つのアイテムが含まれる「adobe\_groups」という名前のリストを定義します。

```YAML
adobe_groups:
  - Photoshop Users
  - Lightroom Users
```

リストにアイテムが 1 つしかないと、わかりづらい場合があります。以下に例を挙げます。

```YAML
adobe_groups:
  - Photoshop Users
```

## 接続構成ファイルの作成と保護

2 つの接続構成ファイルは、Adobe Admin Console およびユーザーの企業の LDAP ディレクトリへのアクセスを User Sync に提供する資格情報を格納します。2 つのシステムへの接続に必要な機密情報を隔離するために、実際の資格情報の詳細はこれら 2 つのファイルに限定されます。本ドキュメントの「[セキュリティの考慮事項](deployment_best_practices.md#セキュリティの考慮事項)」で説明されているように、**それらのファイルは適切に保護する**必要があります。

資格情報を保護するために、User Sync では次の 3 つの方法がサポートされています。


1. 資格情報を connector-umapi.yml および connector-ldap.yml ファイルに直接配置し、ファイルはオペレーティングシステムのアクセスコントロールで保護されます。

2. 資格情報をオペレーティングシステムの安全な資格情報ストアに配置し、2 つの構成ファイルから参照します。

3. 2 つのファイル全体を安全に保管するか暗号化して、そのコンテンツを返すプログラムにメインの構成ファイルから参照します。


サンプルの構成ファイルには、それぞれの方法を説明するエントリが含められています。構成アイテムは 1 セットだけ保持し、残りはコメントを解除するか取り除きます。

### Adobe Admin Console（UMAPI）への接続の構成

Adobe I/O [開発者ポータル](https://www.adobe.io/console/)でユーザー管理へのアクセスを取得して統合をセットアップした後、自分で作成した、または自分の組織に割り当てられた次の構成アイテムをメモしてください。

- 組織 ID
- API キー
- クライアントシークレット
- テクニカルアカウント ID
- プライベート証明書

プレーン テキスト エディターで connector-umapi.yml のコピーを開き、次の値を「enterprise」セクションに入力します。

```YAML
enterprise:
  org_id: "組織 ID をここに入力"
  api_key: "API キーをここに入力"
  client_secret: "クライアントシークレットをここに入力"
  tech_acct: "テクニカルアカウント ID をここに入力"
  priv_key_path: "プライベート証明書へのパスをここに入力"
```

**注：**秘密キーファイルは `priv_key_path` で指定された場所に配置し、ツールを実行するユーザーアカウントに対してのみ読み取り可能であることを確認します。

User Sync 2.1 以降では、秘密キーを別のファイルに格納する以外にも、構成ファイルに直接配置するという代替方法があります。`priv_key_path` キーを使用するのではなく、次のように `priv_key_data` を使用します。

	  priv_key_data: |
	    -----BEGIN RSA PRIVATE KEY-----
	    MIIJKAIBAAKCAge85H76SDKJ8273HHSDKnnfhd88837aWwE2O2LGGz7jLyZWSscH
	    ...
	    Fz2i8y6qhmfhj48dhf84hf3fnGrFP2mX2Bil48BoIVc9tXlXFPstJe1bz8xpo=
	    -----END RSA PRIVATE KEY-----

User Sync 2.2 以降では、接続のタイムアウトと再試行を制御するためのいくつかの追加のパラメーターが用意されています。これらのパラメーターを必ずしも使用する必要はありませんが、不測の事態が発生した場合には、これらを `server` セクションに設定できます。

  server:
    timeout: 120
    retries: 3

`timeout` は、呼び出しが完了するの待つ最大待機時間を設定します（秒単位）。
`retries` は、不特定の問題（サーバーエラー、タイムアウトなど）によって再試行が失敗した場合に、操作を再試行する回数を設定します。

### エンタープライズディレクトリへの接続の構成

プレーンテキストエディターで connector-ldap.yml のコピーを開き、次の値を設定して、エンタープライズディレクトリシステムへのアクセスを有効にします。

```
username: "ユーザーをここに入力"
password: "パスワードをここに入力"
host: "ホストの FQDN"
base_dn: "ディレクトリの base_dn"
```

User Sync バージョン 2.1 以降でパスワードを安全に格納する方法については、[セキュリティの考慮事項](deployment_best_practices.md#security-considerations)を参照してください。

## 構成オプション

メインの構成ファイルである user-sync-config.yml は、 **adobe_users**、 **directory_users**、
**limits**、および  **logging** の主要なセクションに分かれています。

- **adobe_users** セクションは、User Sync ツールがユーザー管理 API を使用して Adobe Admin Console に接続する方法を指定します。アクセスの資格情報を格納する個別の安全な構成ファイルを指す必要があります。これはコネクタフィールドの umapi フィールドで設定されています。
    - adobe_users セクションには、exclude_identity_types、exclude_adobe_groups、および exclude_users を含めることもでき、User Sync の影響を受けるユーザーの範囲を制限します。詳しくは、後述の「[特定のアカウントを User Sync の削除から保護する](advanced_configuration.md#特定のアカウントを-User-Sync-の削除から保護する)」セクションを参照してください。
- **directory_users** サブセクションには、connectors および groups の 2 つのサブセクションが含まれます。
    - **connectors** サブセクションは、エンタープライズディレクトリへのアクセスの資格情報を格納する個別の安全な構成ファイルをポイントします。
    - **groups** セクションは、ディレクトリグループとアドビ製品構成およびユーザーグループとの間のディレクトリのマッピングを定義します。
    - **directory_users** には、既定の国コードや識別タイプを設定するキーを含めることもできます。詳しくは、構成ファイルの例を参照してください。
- **limits** セクションは、指定された値よりも多くのアカウントがアドビ組織に表示されるもののディレクトリには表示されない場合に、User Sync がアドビユーザーアカウントをアップデートまたは削除するのを防ぐために、`max_adobe_only_users` 値を設定します。この制限は、構成ミスや他のエラーによって多数のアカウントが取り除かれるのを防ぎます。このアイテムは必須です。
- **logging** セクションは、監査追跡パスを指定し、ログに書き込まれる情報量を制御します。

### 接続ファイルの構成

メインの User Sync 構成ファイルには、接続の資格情報を実際に含む接続構成ファイルの名前のみが含まれています。これにより、機密情報が隔離されるため、ファイルを保護し、アクセスを制限することができます。

接続構成ファイルへのポインターは
**adobe_users** および  **directory_users** セクションで提供します。

```
adobe_users:
  connectors:
    umapi: connector-umapi.yml

directory_users:
  connectors:
    ldap: connector-ldap.yml
```

### グループマッピングの構成

ユーザーグループと使用権限を同期する前に、前述の「[製品アクセス同期のセットアップ](setup_and_installation.md#製品アクセス同期のセットアップ)」で説明したように、Adobe Admin Console でユーザーグループと製品構成を作成し、エンタープライズディレクトリで対応するグループを作成する必要があります。

**注：**すべてのグループが存在し、両方の側に指定した名前を持っている必要があります。User Sync はいずれの側にもグループを作成することはありません。指定した名前のグループが見つからなかった場合、User Sync はエラーを記録します。

**directory_users** の **groups** セクションには、アドビ製品または製品へのアクセスを示すエンタープライズディレクトリグループごとにエントリを持っている必要があります。グループエントリごとに、そのグループ内のユーザーにアクセスが許可されている製品構成を一覧にします。以下に例を挙げます。

```YAML
groups:
  - directory_group: Acrobat
    adobe_groups:
      - "Default Acrobat Pro DC configuration"
  - directory_group: Photoshop
    adobe_groups:
      - "Default Photoshop CC - 100 GB configuration"
      - "Default All Apps plan - 100 GB configuration"
```

ディレクトリグループは *product configurations* または *user groups* にマッピングすることができます。`adobe_groups` エントリは、いずれの種類のグループも指定できます。

以下に例を挙げます。

```YAML
groups:
  - directory_group: Acrobat
    adobe_groups:
      - Default Acrobat Pro DC configuration
  - directory_group: Acrobat_Accounting
    adobe_groups:
      - Accounting_Department
```

### 構成の制限

対応するユーザーがディレクトリになく、ツールが次のオプションで呼び出されたときに、ユーザーアカウントはアドビシステムから取り除かれます。

- `--adobe-only-user-action delete`
- `--adobe-only-user-action remove`
- `--adobe-only-user-action remove-adobe-groups`

ユーザーの組織でエンタープライズディレクトリに多数のユーザーがいるものの、同期中にユーザー読み取りの数が突然小さい場合、構成ミスまたはエラーが発生した可能性があります。`max_adobe_only_users` 値は、Adobe Admin Console のユーザー数よりもエンタープライズディレクトリ（クエリパラメーターによってフィルター処理）のユーザー数のほうがこの数値だけ少ない場合に、User Sync が既存のアドビアカウントの削除とアップデートを停止して、エラーを報告するためのしきい値です。

現在の値よりもユーザー数が少なくなることが予想される場合はこの値を大きくします。

以下に例を挙げます。

```YAML
limits:
  max_adobe_only_users: 200
```

この構成により、User Sync はアドビに存在するユーザーアカウントのうち、エンタープライズディレクトリ（フィルター処理）で見つからないものが 200 件を超えるかどうか確認し、超えていた場合、既存のアドビアカウントはアップデートされず、エラーメッセージが記録されます。

###  ログ記録の構成

ログエントリは、ツールが呼び出されたコンソールに書き込まれ、オプションでログファイルに書き込まれます。User Sync が実行されるたびに、日時のタイムスタンプを持つ新しいエントリがログに書き込まれます。

**logging** セクションは、ファイルへのログ記録の有効化または無効化を可能にし、ログおよびコンソール出力に書き込まれる情報量を制御します。

```YAML
logging:
  log_to_file: True | False
  file_log_directory: "path to log folder"
  file_log_level: debug | info | warning | error | critical
  console_log_level: debug | info | warning | error | critical
```

log_to_file 値は、ファイルのログ記録をオンまたはオフにします。ログメッセージは、log_to_file の設定に関係なく、必ずコンソールに書き込まれます。

ファイルへのログ記録を有効にした場合、file_log_directory 値は必要です。この値はログエントリが書き込まれるフォルダーを指定します。

- 絶対パスまたはこの構成ファイルを含むフォルダーへの相対パスを入力します。
- ファイルやフォルダーに適切な読み取り/書き込み権限があることを確認します。

ログレベルの値は、どの程度の情報がログファイルまたはコンソールに書き込まれるかを指定します。

- 最も下位レベルである debug では、最も多くの情報が書き込まれ、最も上位のレベルである critical では、最も少ない情報が書き込まれます。
- ファイルとコンソールに対して異なるログレベルの値を定義できます。

WARNING、ERROR、または CRITICAL と記されたログエントリには、そのステータスに関する説明も含まれます。以下に例を挙げます。

> `2017-01-19 12:54:04 7516 WARNING
console.trustee.org1.action - Error requestID: action_5 code: `"error.user.not_found" message: "No valid users were found in the request"`

この例では、2017-01 の 19 12:54:04 に、実行の際に警告メッセージが記録されました。あるアクションがコード "error.user.not_found" のエラーを引き起こしました。エラーコードに関連する説明も含まれています。

requestID 値を使用して、報告されたエラーに関連する厳密なリクエストを検索することもできます。例えば、「action_5」を検索すると次の詳細が返されます。

> `2017-01-19 12:54:04 7516 INFO console.trustee.org1.action -
Added action: {"do":
\[{"add": {"product": \["default adobe enterprise support program configuration"\]}}\],
"requestID": "action_5", "user": "cceuser2@ensemble.ca"}`

警告メッセージを発生させたアクションに関する詳細が入手できます。この場合、User Sync は、ユーザー「cceuser2@ensemble.ca」に「default adobe enterprise support program configuration」を追加しようとしました。ユーザーが見つからなかったため、追加アクションは失敗しました。

## 構成例

次の例では、構成ファイルの構造、および構成値の例を示しています。

### user-sync-config.yml

```YAML
adobe_users:
  connectors:
    umapi: connector-umapi.yml
  exclude_identity_types:
    - adobeID

directory_users:
  user_identity_type: federatedID
  default_country_code: US
  connectors:
    ldap: connector-ldap.yml
  groups:
    - directory_group: Acrobat
      adobe_groups:
        - Default Acrobat Pro DC configuration
    - directory_group: Photoshop
      adobe_groups:
        - "Default Photoshop CC - 100 GB configuration"
        - "Default All Apps plan - 100 GB configuration"
        - "Default Adobe Document Cloud for enterprise configuration"
        - "Default Adobe Enterprise Support Program configuration"

limits:
  max_adobe_only_users: 200

logging:
  log_to_file: True
  file_log_directory: userSyncLog
  file_log_level: debug
  console_log_level: debug
```

### connector-ldap.yml

```YAML
username: "LDAP_username"
password: "LDAP_password"
host: "ldap://LDAP_ host"
base_dn: "base_DN"

group_filter_format: "(&(objectClass=posixGroup)(cn={group}))"
all_users_filter: "(&(objectClass=person)(objectClass=top))"
```

### connector-umapi.yml

```YAML
server:
  # このセクションは、アドビのユーザー管理に使用するサーバーの場所について説明しています。デフォルト：
  # host: usermanagement.adobe.io
  # endpoint: /v2/usermanagement
  # ims_host: ims-na1.adobelogin.com
  # ims_endpoint_jwt: /ims/exchange/jwt

enterprise:
  org_id: "組織 ID をここに入力"
  api_key: "API キーをここに入力"
  client_secret: "クライアントシークレットをここに入力"
  tech_acct: "テクニカルアカウント ID をここに入力"
  priv_key_path: "private.key へのパスをここに入力"
  # priv_key_data: "実際のキーデータをここに入力" # これは priv_key_path の代わり
```

## 構成のテスト

これらのテストケースを使用して、構成が正常に機能していること、また製品構成がエンタープライズディレクトリのセキュリティグループに正しくマッピングされていることを確認します。まずテストモード（-t パラメーターを使用）でツールを実行して、結果を確認してから実稼働します。

次の例では `--users all` を使用してユーザーを選択していますが、`--users mapped` を使用して、構成ファイルに指定されたディレクトリグループのユーザーのみを選択したり、`--users file f.csv` を使用して、特定のファイルに指定されたテストユーザーのより小規模なセットを選択したりすることもできます。

###  ユーザーの作成


1. エンタープライズディレクトリに 1 人以上のテストユーザーを作成します。


2. 1 つ以上の構成済みディレクトリ/セキュリティグループにユーザーを追加します。


3. User Sync をテストモードで実行します。(`./user-sync -t --users all --process-groups --adobe-only-user-action exclude`)


3. User Sync をテストモード以外で実行します。(`./user-sync --users all --process-groups --adobe-only-user-action exclude`)


4. テストユーザーが Adobe Admin Console に作成されたことを確認します。

### ユーザーのアップデート


1. ディレクトリ内の 1 人以上のテストユーザーのグループメンバーシップを変更します。


1. User Sync を実行します。(`./user-sync --users all --process-groups --adobe-only-user-action exclude`)


2. Adobe Admin Console のテストユーザーが、新しい製品構成メンバーシップを反映するようアップデートされていることを確認します。

###  ユーザーの無効化


1. エンタープライズディレクトリで、1 人以上の既存のテストユーザーを取り除くか無効化します。


2. User Sync を実行します。（`./user-sync --users all --process-groups --adobe-only-user-action remove-adobe-groups`）必要に応じて、最初にテストモード（-t）で実行することもできます。


3. Adobe Admin Console で構成済みの製品構成からユーザーが取り除かれていることを確認します。


4. User Sync を実行してユーザーを取り除きます（`./user-sync -t --users all --process-groups --adobe-only-user-action delete`）。その後、-t なしで実行します。注：-t で実行する際、目的のユーザーのみが取り除かれたことを確認します。この実行では（-t なし）、ユーザーが実際に削除されます。


5. Adobe Admin Console からユーザーアカウントが取り除かれたことを確認します。

---

[前のセクション](setup_and_installation.md)  \| [次のセクション](command_parameters.md)
