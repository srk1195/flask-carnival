from myapp import  app
from flask import  render_template

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404
@app.errorhandler(500)
def internal_page_error(e):
    return render_template('500.html'),500
@app.errorhandler(403)
def forbidden():
    return render_template('500.html'),403