import sysv_ipc
import threading
import time
from vehicle import Vehicle
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
            if vehicle.isPriority==True:
                print(vehicle.isPriority)
        except sysv_ipc.BusyError:
            pass  # Pas de véhicule pour l'instant
        if lights_dict[traffic_rules[direction]]:  # Vérifie si le feu est vert
            for vehicle in vehicleStack:
                currentVehicle = vehicleStack.pop()
                currentVehicle.isWaiting = False
                print(f"🚗 Vehicle {currentVehicle.vehicle_id} passed (Source: {currentVehicle.source} ➝ Destination: {currentVehicle.destination})")

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
