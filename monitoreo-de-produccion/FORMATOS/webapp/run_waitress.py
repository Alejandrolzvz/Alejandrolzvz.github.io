import os
import logging
from dotenv import load_dotenv
from waitress import serve
from app import app

# Cargar variables de entorno antes de iniciar el servidor
load_dotenv()

# Configurar el registro de actividad y errores (Logs)
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'errores_app.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(message)s'
)
# Sincronizar logs de flask con nuestro archivo
app.logger.setLevel(logging.INFO)

if __name__ == '__main__':
    msg = "Iniciando servidor de producción con Waitress en el puerto 5000..."
    logging.info(msg)
    print(msg)
    print("Presiona Ctrl+C para salir.")
    # Waitress es un servidor WSGI productivo y multi-hilo
    serve(app, host='0.0.0.0', port=5000)
