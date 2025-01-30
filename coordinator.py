import sysv_ipc
import threading
import time

def process_single_queue(mq, direction, lights_dict):
    """Traite les véhicules d'une file si le feu est vert."""
    traffic_rules = {
        "North": "northsouth",
        "South": "northsouth",
        "East": "eastwest",
        "West": "eastwest"
    }

    while True:
        if lights_dict[traffic_rules[direction]]:  # Vérifie si le feu est vert
            try:
                message, _ = mq.receive(block=False)  # Lecture non bloquante
                vehicle_info = message.decode().split(',')
                
                vehicle_id, source, destination, is_priority, is_waiting = vehicle_info
                print(f"🚗 Vehicle {vehicle_id} passed (Source: {source} ➝ Destination: {destination})")
            
            except sysv_ipc.BusyError:
                pass  # Pas de véhicule pour l'instant

def coordinate(mqList, lights_dict):
    """Lance un thread pour chaque file de message."""
    roads = ["North", "South", "East", "West"]
    threads = []

    for mq, road in zip(mqList, roads):
        thread = threading.Thread(target=process_single_queue, args=(mq, road, lights_dict))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()  # Attend la fin des threads (en pratique, ne s'arrête jamais)
