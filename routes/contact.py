from imports import *

# MARK: お問い合わせページ
def contact(app):
    @app.route('/contact', methods=['GET', 'POST'])
    @login_required
    def contact_view():
        if request.method == 'POST':
            try:
                userId = session.get('userId')
                # フォームからデータを取得
                name = request.form.get('name')
                name_kana = request.form.get('name_kana')
                email = request.form.get('mail')
                subject = request.form.get('subject')
                message = request.form.get('message')
                
                # ファイルの処理（もし添付ファイルがある場合）
                file = request.files.get('test')
                file_path = None
                if file and file.filename:
                    # ファイル名を安全に保存
                    filename = secure_filename(file.filename)
                    file_path = os.path.join('uploads', filename)
                    file.save(file_path)
                
                # 新しい問い合わせを作成
                new_inquiry = Inquiry(
                    userId=userId,
                    displayName=name,
                    mailAddress=email,
                    inquiryContent=message,
                    appendFile=file_path
                )
                
                # データベースに保存
                db.session.add(new_inquiry)
                db.session.commit()
                
                flash('お問い合わせを受け付けました。ありがとうございます。', 'success')
                return redirect(url_for('contact'))
                
            except Exception as e:
                print(f"Error お問い合わせ送信失敗: {e}")
                flash('お問い合わせの送信に失敗しました。もう一度お試しください。', 'error')
                db.session.rollback()
                
        return render_template('contact.html')