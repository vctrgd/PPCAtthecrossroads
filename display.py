import tkinter as tk
import socket
import threading


class TrafficDisplay:
    def __init__(self, master):
        self.master = master
        master.title("Traffic Simulation")
        self.canvas = tk.Canvas(master, width=800, height=600, bg='lightgray')
        self.canvas.pack()
        
        self.draw_roads()
        self.vehicles = {}  # Dictionnaire des véhicules {id: rectangle}
        
        # Démarrer le serveur socket dans un thread
        self.server_thread = threading.Thread(target=self.start_socket_server, daemon=True)
        self.server_thread.start()

    def start_socket_server(self):
        HOST = 'localhost'
        PORT = 65432
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Réutiliser le port
            s.bind((HOST, PORT))
            s.listen()
            while True:  # Accepter plusieurs connexions
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn,)).start()

    def handle_client(self, conn):
        with conn:
            buffer = ""
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                buffer += data
                while ';' in buffer:
                    msg, buffer = buffer.split(';', 1)
                    self.process_message(msg.strip())
            
        

    def draw_roads(self):
        # Rue horizontale
        self.canvas.create_line(0, 300, 800, 300, width=8, fill='darkgray')
        # Rue verticale
        self.canvas.create_line(400, 0, 400, 600, width=8, fill='darkgray')


    def process_message(self, msg):
        # Format: "id,x,y,source,destination"
        parts = msg.split(',')
        if len(parts) != 6:
            return
        
        vid, x, y, source, dest, color = parts
        x = float(x)
        y = float(y)
        
        # Mise à jour de l'affichage dans le thread principal
        self.master.after(0, self.update_vehicle, vid, x, y, color)

    def update_vehicle(self, vid, x, y,color):
        # Ajustement pour Tkinter (origine en haut à gauche)
        y_tk = 600 - y
        size = 8

        if vid not in self.vehicles:
            self.vehicles[vid] = self.canvas.create_rectangle(
                x-size, y_tk-size, x+size, y_tk+size, fill=color , outline='black', width=2
            )
        else:
            self.canvas.itemconfig(
                self.vehicles[vid], 
                fill=color  
            )
            self.canvas.coords(
                self.vehicles[vid],
                x-size, y_tk-size, x+size, y_tk+size
            )
        self.canvas.update_idletasks()

def run_display():
    root = tk.Tk()
    app = TrafficDisplay(root)
    root.mainloop()