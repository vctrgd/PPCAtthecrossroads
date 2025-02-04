import sysv_ipc
import threading
import time
from vehicle import Vehicle
import signal
import lights
import os
import crossRoad
import socket
import random

def send_to_display(vehicle_id, x, y, source, destination,color):
    HOST = 'localhost'
    PORT = 65432
    
    # Format: "id,x,y,source,destination;"
    msg = f"{vehicle_id},{x},{y},{source},{destination},{color};".encode()
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)  # Timeout de 2 secondes
                s.connect((HOST, PORT))
                s.sendall(msg)
                break  # Succès, sortie de la boucle
        except (ConnectionRefusedError, TimeoutError):
            if attempt < max_retries - 1:
                time.sleep(1)  # Attendre avant de réessayer
                continue
            print("Impossible de se connecter au display.")

def send_light_status(lights_dict):
    HOST = 'localhost'
    PORT = 65432
    s= None
    while True:
        try:
            if not s:
                s  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((HOST, PORT))
                          
            msg = f"LIGHT,{lights_dict['northsouth']},{lights_dict['eastwest']};".encode()
            s.sendall(msg)
            time.sleep(0.3)

        except Exception as e:
            print(f"Erreur connexion: {e}")
            if s:
                s.close()
            s = None
            time.sleep(1)

            time.sleep(1)

def generate_random_color():
    """Génère une couleur hexadécimale aléatoire."""
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def process_single_queue(mq, direction, lights_dict, lights_pid):
    """Traite les véhicules d'une file si le feu est vert."""
    traffic_rules = {
        "North": "northsouth",
        "South": "northsouth",
        "East": "eastwest",
        "West": "eastwest"
    }
    vehicleStack = list()
    
    # Connexion socket persistante
    HOST = 'localhost'
    PORT = 65432
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    
    while True:
        try:
            message, _ = mq.receive(block=False)  # Lecture non bloquante
            vehicle_info = message.decode().split(',')   
            vehicle_id, source, destination, is_priority, is_waiting = vehicle_info
            is_priority = is_priority.lower() == "true" if isinstance(is_priority, str) else is_priority
            vehicle = Vehicle(vehicle_id, is_priority, source, destination, is_waiting)
            vehicleStack.append(vehicle) 

            # Logique de priorité
            if vehicle.isPriority==True and traffic_rules[vehicle.source]=="northsouth":
                os.kill(lights_pid, signal.SIGUSR1)
            elif vehicle.isPriority==True and traffic_rules[vehicle.source]=="eastwest":
                os.kill(lights_pid, signal.SIGUSR2)

        except sysv_ipc.BusyError:
            pass  # Pas de véhicule pour l'instant

        if lights_dict[traffic_rules[direction]]:  # Vérifie si le feu est vert
            while vehicleStack:
                currentVehicle = vehicleStack.pop()
                currentVehicle.isWaiting = False
                color = generate_random_color()
                print(f"🚗 Vehicle {currentVehicle.vehicle_id} passed (Source: {currentVehicle.source} ➝ Destination: {currentVehicle.destination})")
                
                # Simulation de mouvement
                source_pos = crossRoad.ENTRY_POINTS[currentVehicle.source]
                dest_pos = crossRoad.DESTINATION_POINTS[currentVehicle.destination]
                center = (400, 300)  # Centre du carrefour
                steps = 20

                for step in range(steps):
                    if step < steps // 2:
                        progress = step / (steps // 2 - 1)
                        x = source_pos[0] + (center[0] - source_pos[0]) * progress
                        y = source_pos[1] + (center[1] - source_pos[1]) * progress
                    else:
                        progress = (step - steps // 2) / (steps // 2 - 1)
                        x = center[0] + (dest_pos[0] - center[0]) * progress
                        y = center[1] + (dest_pos[1] - center[1]) * progress
                
                    # Utilisation du socket persistant
                    msg = f"{currentVehicle.vehicle_id},{x},{y},{currentVehicle.source},{currentVehicle.destination},{color};".encode()
                    try:
                        s.sendall(msg)
                    except (BrokenPipeError, ConnectionResetError):
                        s.close()
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((HOST, PORT))
                        s.sendall(msg)
                
                
                    time.sleep(0.03)  


def coordinate(mqList, lights_dict, lights_pid):
    """Lance un thread pour chaque file de message."""
    roads = ["North", "South", "East", "West"]
    threads = []
    

    threading.Thread(target=send_light_status, args=(lights_dict,)).start()
  

    for mq, road in zip(mqList, roads):
        thread = threading.Thread(target=process_single_queue, args=(mq, road, lights_dict, lights_pid))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()  # Attend la fin des threads (en pratique, ne s'arrête jamais)