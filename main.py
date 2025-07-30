import os
import sys
import pygame
import cv2

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

TEXT_PADDING_R = 50

font_sizes = [150, 120]
padding_by_font_size = {150: 80, 120: 100}

pygame.init()

function_buttons = [[1073742083, 44], [1073742082, 46]]

size = (1480, 320)
if len(sys.argv) > 1 and sys.argv[1] == "debug":
    screen = pygame.display.set_mode(size)
else:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.mouse.set_visible(False) # Hide cursor here


video = cv2.VideoCapture("aos.mp4")
success, video_image = video.read()
fps = video.get(cv2.CAP_PROP_FPS)
clock = pygame.time.Clock()


name_options = [
    "Solvent",
    "Mx Mouse",
    "Aralia",
    "Untoppable"
]

name_index = 0
name_text = name_options[name_index]

# def read_name():
#     with open("display.txt", "r") as namefile:
#         return namefile.read()

def update_name():
    global name_text
    name_text = read_name()
    print(f"Updating name to {name_text}")

def get_font_size():
    global name_text
    font_size = font_sizes[0]
    if len(name_text) > 10:
        font_size = font_sizes[1]
    return font_size

def get_text_surface():
    font_size = get_font_size()

    font = pygame.font.Font("Bank Gothic Medium BT.ttf", font_size)
    text_surface = font.render(name_text, True, WHITE)

    return text_surface


done = False
# UPDATE_NAME_EVENT = pygame.USEREVENT + 1

MODE_SCROLL = 0
MODE_ENTER = 1
mode = MODE_SCROLL

def main():
    global done, name_index, name_text, mode
    
    clock.tick(fps)
    # pygame.time.set_timer(UPDATE_NAME_EVENT, 2000)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            # elif event.type == UPDATE_NAME_EVENT:
            #     print("Update name event!")
            #     update_name()
            
            # elif mode == MODE_SCROLL and event.type == pygame.MOUSEWHEEL:
            #     print(event.y)

            elif event.type == pygame.KEYDOWN:
                print(event.key)
                
                inc = 0
                if mode == MODE_SCROLL:
                    if event.key in function_buttons[0]:
                        print("-1!")
                        inc = -1
                    elif event.key in function_buttons[1]:
                        print("+1!")
                        inc = 1

                    # inc = 1 if event.y > 0 else -1
                    name_index = name_index + inc
                    
                    if name_index == len(name_options):
                        name_index = len(name_options) - 1
                    if name_index < 0:
                        name_index = 0
                    name_text = name_options[name_index]
                
                    if event.key == pygame.K_RETURN:
                        print("enter")
                        mode = MODE_ENTER
                        name_text = ""
                    elif mode == MODE_ENTER:
                        if event.key == pygame.K_RETURN:
                            print("scroll")
                            print(f"entering {name_text}")
                            mode = MODE_SCROLL
                            name_options.append(name_text)
                            name_index = len(name_options) - 1
                            print(name_options, name_index)
                        elif event.key == pygame.K_BACKSPACE:
                            name_text = name_text[:-1]
                        else:
                            name_text += chr(event.key)

                if event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    print("Shutting down!")
                    os.system("shutdown -h now")



        success, video_image = video.read()
        if success:
            video_surf = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
            # video_surf = pygame.transform.rotate(video_surf, 90)
            # video_surf = pygame.transform.scale_by(video_surf, (0.8, 0.5))
            screen.blit(video_surf, (0, 0))
        else:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # screen.fill(WHITE)
        text_surface = get_text_surface()
        text_size = text_surface.get_size()
        # surface = pygame.transform.rotate(text_surface, 90)

        screen.blit(text_surface, (1480 - text_size[0] - TEXT_PADDING_R, padding_by_font_size[get_font_size()]))

        pygame.display.flip()


if __name__ == "__main__":
    main()