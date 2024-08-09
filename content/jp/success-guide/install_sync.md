---
weight: 150
title: User Sync のインストール
type: docs
---

# User Sync のインストール

User Sync が実行されるサーバーにアクセスしたら、User Sync をインストールして操作するディレクトリを選択します。

Windows では、Python をインストールする必要があります。この記事の執筆時点では、バージョン 2.7.13 をお勧めします。Windows と Python は 64 ビットバージョンにする必要があります。

Windows では、環境変数 PEX_ROOT を C:\user_sync\.pex に設定することが必要な可能性も非常に高くなります。これは Windows のパス名の長さ制限を回避するために必要です。

最初の手順：

同期をインストールして実行するためのユーザーおよびファイルディレクトリを設定します。例えば、フォルダー /home/user_sync/user_sync_tool とユーザー user_sync を作成します。Windowsでは、C:\Users\user_sync\user_sync_tool のようになります。

Windows のみ：環境変数 **PEX\_ROOT** を **C:\user_sync\.pex** に設定します。

Windowsのみ：python 2.7.13（または 2.7 シリーズではそれ以降）、64 ビットをインストールします。

次のいくつかの節で、インストールプロセスを示します。

最新のリリースを入手するには：ここから開始します：
[https://github.com/adobe-apiplatform/user-sync.py](https://github.com/adobe-apiplatform/user-sync.py "https://github.com/adobe-apiplatform/user-sync.py")

![インストール](/user-sync.py/images/jp/install_finding_releases.png)

「release」を選択します。

![インストール 2](/user-sync.py/images/jp/install_release_screen.png)

example-configurations.tar.gz、User Sync ガイドおよびプラットフォーム、osx、ubuntu、Windows または centos 用のビルドをダウンロードします。

アーカイブから user-sync（または user-sync.pex）ファイルを抽出し、使用している OS 用のファイルをフォルダーに配置します。この例では、これは /home/user_sync/user_sync_tool/user-sync または C:\Users\user_sync\user_sync_tool\user-sync.pex になります。

example-configurations.tar.gz ファイルには、ディレクトリ **config files - basic** があります。このフォルダーから最初の 3 ファイルを抽出し、user_sync_tool フォルダーに配置します。

次に、名前の先頭の「1」、「2」、「3」を削除して、3 つの構成例ファイルの名前を変更します。これらのファイルを編集して、実際の User Sync 構成ファイルを作成します。

![インストール 2](/user-sync.py/images/jp/install_config_files.png)
