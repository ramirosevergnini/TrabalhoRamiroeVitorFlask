# run.py
from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    print(">>> Servidor subindo em http://127.0.0.1:5000 (Ctrl+C para parar)")
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
