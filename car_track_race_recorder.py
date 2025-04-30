# *** put files on a tkinter window to control display 

import serial
import random
import socket
import threading
import math

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind to localhost on port 77777
server_socket.bind(('0.0.0.0', 7777))
# Listen for incoming connections
server_socket.listen(1)
# Accept a connection
conn, addr = server_socket.accept()

try:
    arduino = serial.Serial('COM5', 115200, timeout=.1)
except:
    print("No serial")

current_race = 0
race_happening = False
results = {}
racers_printed = False

def is_client_connected(sock):
    try:
        # Attempt to receive data (non-blocking with MSG_PEEK)
        data = sock.recv(1024, socket.MSG_PEEK)
        if not data:
            # Client disconnected gracefully (received 0 bytes)
            return False
        else:
            # Client is still connected (data available)
            return True
    except ConnectionResetError:
        # Client disconnected abruptly
        return False
    except ConnectionAbortedError:
        return False
    except Exception as e:
        # Handle other potential errors (e.g., socket closed on server side)
        print(f"Error checking connection: {e}")
        return False

def group():
    global group
    choices = ["cubbies", "sparks", "tnt", "trek"]
    group = ""
    while (True):
        group = input("Load(cubbies, sparks, tnt, trek): ").lower()
        if (group == "cubbies" or group == "sparks" or group == "tnt" or group == "trek"):
            break
        else:
            print("invalid input")

def load(current_race, lane, group):
    file = open(f"{group}.txt", "r")
    text = file.readlines()
    lane_car = 0
    car_numbers = ["","","",""]
    for i in range(len(text[current_race])):
        if (text[current_race][i] == ","):
            lane_car += 1
        else:
            if (text[current_race][i] != "\n"):
                car_numbers[lane_car] += text[current_race][i]
    return(int(car_numbers[lane]))

def generate_groups():
    cubbies_amount = int(input("How many Cubbies: "))
    sparks_amount = int(input("How many Sparks: "))
    tnt_amount = int(input("How many Tnt: "))
    trek_amount = int(input("How many Trek: "))
    
    cubbies_f, cubbies_t = fours_threes(cubbies_amount)
    sparks_f, sparks_t = fours_threes(sparks_amount)
    tnt_f, tnt_t = fours_threes(tnt_amount)
    trek_f, trek_t = fours_threes(trek_amount)
    
    cubbies_file = open("cubbies.txt", "a")
    sparks_file = open("sparks.txt", "a")
    tnt_file = open("tnt.txt", "a")
    trek_file = open("trek.txt", "a")

    # generate fours
    for i in range(math.floor(cubbies_f)):
        car = random.randint(0, cubbies_amount-i)
        cubbies_file.write()
    for i in range(math.floor(sparks_f)):
        car = random.randint(0, sparks_amount-i)
        sparks_file.write()
    for i in range(math.floor(tnt_f)):
        car = random.randint(0, tnt_amount-i)
        tnt_file.write()
    for i in range(math.floor(trek_f)):
        car = random.randint(0, trek_amount-i)
        trek_file.write()
    
    # generate extras
    for i in range(cubbies_t):
        car = random.randint(0, cubbies_amount-i - cubbies_f*4)
        cubbies_file.write()
    for i in range(sparks_t):
        car = random.randint(0, sparks_amount-i - sparks_f*4)
        sparks_file.write()
    for i in range(tnt_t):
        car = random.randint(0, tnt_amount-i - tnt_f*4)
        tnt_file.write()
    for i in range(trek_t):
        car = random.randint(0, trek_amount-i - trek_f*4)
        trek_file.write()
    
def fours_threes(n):
    return (n/4, n%4)

def scores(str_data):
    global results, current_race
    car = 0
    current_race_results = {}
    str_value = ""
    for i in range(len(str_data)):
        if (str_data[i] == ","):
            name = load(current_race-1, car, group)
            results.update({name : int(str_value[:-2]) /1000})
            current_race_results.update({name : int(str_value[:-2]) /1000})
            str_value = ""
            car += 1
        if (str_data[i].isdigit()):
            str_value += str_data[i]
    results = dict(sorted(results.items(), key=lambda x: x[1]))
    print(results)
    i = 0
    while(1==1):
        try:
            file = open(f"Race {i}- Race_{current_race}.txt", "r")
        except:
            file = open(f"Race {i}- Race_{current_race}.txt", "w")
            break
        i += 1
    file.write(str(current_race_results))
    file.close()

group()
def main():
    global racers_printed, current_race, racers_printed, conn
    while True:
        if is_client_connected(conn):
            pass
        else:
            conn, addr = server_socket.accept()
        data = arduino.readline()[:-2] #the last bit gets rid of the new-line chars
        str_data = data.decode('utf-8')
        if (racers_printed == False):
            print(f"Racers: {load(current_race, 0, group)},{load(current_race, 1, group)},{load(current_race, 2, group)},{load(current_race, 3, group)}")
            racers_printed = True
        if data:
            print(str_data)
            if (str_data == "Race Started"):
                conn.sendall(b"race started")
                race_happening = True
                current_race += 1
                print(current_race)
            if (str_data == "Race Finished"):
                conn.sendall(b"race finished")
                race_happening = False
                racers_printed = False
            if (str_data[0].isdigit()):
                conn.sendall(str_data.encode('utf-8'))
                scores(str_data)
                print(results)
                Confrim = input("Save Race(y/n): ")
                if (Confrim == "y"):
                    Confrim_extra = input("Are you sure you want to save(y/n): ")
                    if (Confrim_extra == "y"):
                        pass
                    else:
                        Confrim_extra_extra = input("Are you sure you want to reset(y/n): ")
                        if (Confrim_extra == "y"):
                            current_race -= 1
                        else:
                            pass
                else:
                    Confrim_extra = input("Are you sure you want to reset(y/n): ")
                    if (Confrim_extra == "y"):
                        current_race -= 1
                    else:
                        pass

if __name__ == "__main__":
    main()
# Close socket connection 
conn.close()
