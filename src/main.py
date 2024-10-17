import pygame
from components.Game import Game
from flask import Flask, render_template, request
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    action = request.json.get('action')
    if action:
        game.process_action(action)  # Asegúrate de tener este método en tu Game
    return {"status": "success"}

def run_flask():
    app.run(host='0.0.0.0', port=3002)

def main():
    global game
    pygame.init()
    pygame.mixer.init()
    game = Game()
    
    threading.Thread(target=run_flask).start()
    
    game.run() 
    print("el juego debería correr ahora") 
    pygame.quit()

if __name__ == "__main__":
    main()
