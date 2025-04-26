from imports import *

#　MARK: Welcomeページ 
def termsOfUse(app):
    @app.route('/termsOfUse', methods=['GET', 'POST'])
    def termsOfUse_view():      
        return render_template('termsOfUse.html')