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
                for step in range(10):
                    x = source_pos[0] + (dest_pos[0] - source_pos[0]) * (step/9)
                    y = source_pos[1] + (dest_pos[1] - source_pos[1]) * (step/9)
                    send_to_display(currentVehicle.vehicle_id, x, y, currentVehicle.source, currentVehicle.destination,color)
                    time.sleep(0.05)

def coordinate(mqList, lights_dict, lights_pid):
    """Lance un thread pour chaque file de message."""
    roads = ["North", "South", "East", "West"]
    threads = []
    for mq, road in zip(mqList, roads):
        thread = threading.Thread(target=process_single_queue, args=(mq, road, lights_dict, lights_pid))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()  # Attend la fin des threads (en pratique, ne s'arrête jamais)