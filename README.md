ロゴの筆の色
#46A0DC
レスポンシブ
960pxと570px

インストール手順

	↓これをターミナルに記述してインストールされているライブラリをテキスト化
	pip freeze > requirements.txt

	↓これをターミナルに記述してインストール
	pip install -r requirements.txt


データベース
	データベースはデフォルトで[azure database for MySQL フレキシブルサーバー]に接続しているのでローカルでテーブルの中身を確認することはできません。
	もしデータベースの接続をローカルに切り替えたい場合は[Piction > .env]の2行目をコメントアウトして1行目のコメントアウトを解除してください。

テーブル
	user 					: ユーザー情報
	sale 					: 商品情報
	category 				: カテゴリー
	saleCategoryAssociation : saleテーブルとcategoryテーブルの仲介テーブル
	bid 					: 入札情報
	winningBid 				: 落札情報
	paymentWay 				: 支払い方法
	payment 				: 支払い情報
	like 					: いいね情報
	inquiryKind 			: 問い合わせ種類
	inquiry 				: 問い合わせ情報


	
