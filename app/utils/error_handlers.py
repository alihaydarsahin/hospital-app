from flask import render_template, jsonify, request
from werkzeug.exceptions import HTTPException
import traceback

def register_error_handlers(app):
    """Hata işleyicilerini kaydeder"""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """400 Bad Request hatası işleyicisi"""
        if request.is_json:
            return jsonify({
                'error': 'Bad Request',
                'message': str(error)
            }), 400
        return render_template('errors/400.html', error=error), 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """401 Unauthorized hatası işleyicisi"""
        if request.is_json:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Bu işlem için yetkiniz yok'
            }), 401
        return render_template('errors/401.html', error=error), 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """403 Forbidden hatası işleyicisi"""
        if request.is_json:
            return jsonify({
                'error': 'Forbidden',
                'message': 'Bu işlem için yetkiniz yok'
            }), 403
        return render_template('errors/403.html', error=error), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        """404 Not Found hatası işleyicisi"""
        if request.is_json:
            return jsonify({
                'error': 'Not Found',
                'message': 'İstenen kaynak bulunamadı'
            }), 404
        return render_template('errors/404.html', error=error), 404
    
    @app.errorhandler(405)
    def method_not_allowed_error(error):
        """405 Method Not Allowed hatası işleyicisi"""
        if request.is_json:
            return jsonify({
                'error': 'Method Not Allowed',
                'message': 'Bu HTTP metodu bu endpoint için kullanılamaz'
            }), 405
        return render_template('errors/405.html', error=error), 405
    
    @app.errorhandler(429)
    def too_many_requests_error(error):
        """429 Too Many Requests hatası işleyicisi"""
        if request.is_json:
            return jsonify({
                'error': 'Too Many Requests',
                'message': 'Çok fazla istek gönderdiniz. Lütfen biraz bekleyin'
            }), 429
        return render_template('errors/429.html', error=error), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 Internal Server Error hatası işleyicisi"""
        # Hatayı logla
        app.logger.error('Server Error: %s', str(error))
        app.logger.error('Traceback: %s', traceback.format_exc())
        
        if request.is_json:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'Sunucu hatası oluştu'
            }), 500
        return render_template('errors/500.html', error=error), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Yakalanmamış tüm hatalar için genel işleyici"""
        # Hatayı logla
        app.logger.error('Unhandled Exception: %s', str(error))
        app.logger.error('Traceback: %s', traceback.format_exc())
        
        # HTTP hatası ise
        if isinstance(error, HTTPException):
            if request.is_json:
                return jsonify({
                    'error': error.name,
                    'message': error.description
                }), error.code
            return render_template(f'errors/{error.code}.html', error=error), error.code
        
        # Diğer hatalar için 500 döndür
        if request.is_json:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'Beklenmeyen bir hata oluştu'
            }), 500
        return render_template('errors/500.html', error=error), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """413 Request Entity Too Large hatası işleyicisi"""
        if request.is_json:
            return jsonify({
                'error': 'Request Entity Too Large',
                'message': 'Yüklemeye çalıştığınız dosya çok büyük'
            }), 413
        return render_template('errors/413.html', error=error), 413
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """422 Unprocessable Entity hatası işleyicisi"""
        if request.is_json:
            return jsonify({
                'error': 'Unprocessable Entity',
                'message': 'Gönderilen veri işlenemedi',
                'errors': getattr(error, 'data', {}).get('messages', {})
            }), 422
        return render_template('errors/422.html', error=error), 422 