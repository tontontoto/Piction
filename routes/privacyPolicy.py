from imports import *

#　MARK: Welcomeページ 
def privacyPolicy(app):
    @app.route('/privacyPolicy', methods=['GET', 'POST'])
    def privacyPolicy_view():      
        return render_template('privacyPolicy.html')