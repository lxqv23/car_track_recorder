# *** use sockets to connect to the reace track recorder

# import libraries
import pygame 
import sys
import cv2
import socket
import select
import time
pygame.font.init()
# set up font for pygame
main_font = pygame.font.SysFont('comicsans', 100)
BLACK = (0,0,0)
# Create a TCP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to server
while(1==1):
    try:
        client_socket.connect(('192.168.68.53', 7777))
        break
    except:
        pass

# make window
pygame.init()

# tabs: up next, countdown, during race, after race
tab = 0
players = ["","","",""]
# find monitor
monitor_info = pygame.display.list_modes(display=1)  # Assuming monitor index is 1
if len(monitor_info) > 0:
    width, height = monitor_info[0]
else:
    print("No alternative monitor found!")

Win = pygame.display.set_mode((width, height), pygame.FULLSCREEN, display=1)
pygame.display.set_caption("Race track")

# Import files
finished_race = pygame.image.load('awana_race_pictures.png')
next_race = pygame.image.load('Up_Next.png')
before_race = cv2.VideoCapture("pre_race.mp4")
during_race = cv2.VideoCapture("Car_going_down_track.mp4")


def scores(str_data):
    global players
    index = 0
    values = []
    raw_scores = {}
    hold =""
    for i in range(len(str_data)):
        if str_data[i] == ",":
            index += 1
            values.append((float(hold))/1000)
            hold = ""
        else:
            hold += str(str_data[i])
    for i in range(len(values)):
        raw_scores[players[i]] = values[i]
    sorted_scores = dict(sorted(raw_scores.items(), key=lambda item: item[1]))
    raw_race_scores_list = []
    for key in sorted_scores.keys():
        raw_race_scores_list.append(key)
    print(raw_race_scores_list)
    race_scores_list = [raw_race_scores_list[3],raw_race_scores_list[1],raw_race_scores_list[0],raw_race_scores_list[2]]
    return(race_scores_list)
# send players before match starts
def up_next():
    global players
    Win.blit(next_race, (0,0))
    for i in range(4):
        draw_text = main_font.render(players[i], 1, BLACK)
        Win.blit(draw_text, (839,305+(175*i)))
def race_started():
    ret, during_race_frame = during_race.read()
    if not ret:
        return -1
    during_race_frame = cv2.cvtColor(during_race_frame, cv2.COLOR_BGR2RGB)
    during_race_frame = pygame.surfarray.make_surface(during_race_frame.swapaxes(0, 1))
    Win.blit(during_race_frame, (0, 0))
def pre_race():
    ret, frame = before_race.read()
    if not ret:
        return -1
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    Win.blit(frame, (0, 0))
def race_finished():
    global race_scores
    Win.blit(finished_race, (0,0))
    for i in range(4):
        draw_text = main_font.render(str(race_scores[i]), 1, BLACK)
        Win.blit(draw_text, (384+(360*i),960))

def main():
    global tab, players, race_scores
    Run = True
    while Run:
        # Check if there is incoming data (no blocking)
        ready_to_read, _, _ = select.select([client_socket], [], [], 0)
        if ready_to_read:
            data = client_socket.recv(1024)
            if data:
                message = data.decode()
                if message == "race started":
                    start_time = time.time()
                    tab = 2
                elif message == "race finished":
                    tab = 3
                elif message == "racers":
                    data = client_socket.recv(1024)
                    str_players = data.decode()
                    player = 0
                    players = ["","","",""]
                    for i in range(len(str_players)):
                        if str_players[i] == ",":
                            player += 1
                        else:
                            players[player] += str_players[i]
                elif message =="countdown":
                    tab = 1
                    before_race.set(cv2.CAP_PROP_POS_FRAMES, 0)
                elif message == "up next":
                    tab = 0
                    during_race.set(cv2.CAP_PROP_POS_FRAMES,0)
                else:
                    race_scores = scores(message)
        # tell server your connected
        client_socket.sendall(b'CONNECTED')
        keys_pressed = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        print(mouse_pos)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Close socekt connection
                client_socket.close()
                pygame.quit()
                sys.exit()
                Run = False
        if tab == 0:
            up_next()
        elif tab == 1:
            pre_race()
        elif tab == 2:
            race_started()
        elif tab == 3:
            race_finished()
        #updates display
        pygame.display.flip()

if __name__ == "__main__":
    main()
