# normalTrafficGenerator.py
import random
import crossRoad
import sysv_ipc
import time
from vehicle import Vehicle

def normalTrafficGenerator(mq: sysv_ipc.MessageQueue, source, currentId, lock):
    while True:
        time.sleep(random.randint(1, 5))
        vehicle = generateVehicle(source, currentId, lock)
        addVehicleToQueue(mq, vehicle)
        
def addVehicleToQueue(mq: sysv_ipc.MessageQueue, vehicle: Vehicle):
    try:
        vehicle_message = f"{vehicle.vehicle_id},{vehicle.source},{vehicle.destination},{vehicle.isPriority},{vehicle.isWaiting}"
        mq.send(vehicle_message.encode())  # Envoie un message dans la MQ
        # print(f"Vehicle {vehicle.vehicle_id} added to queue from {vehicle.source} to {vehicle.destination}.")
    except Exception as e:
        print(f"Error adding vehicle {vehicle.vehicle_id} to queue: {e}")

def generateVehicle(source, currentId, lock) -> Vehicle:
    possible_destinations = [road for road in crossRoad.roads if road != source]
    destination = random.choice(possible_destinations)
    
    # Acquérir le verrou avant de modifier currentId
    with lock:
        vehicle_id = currentId.value
        currentId.value += 1
    
    vehicle: Vehicle = Vehicle(vehicle_id, False, source, destination, True)
    return vehicle