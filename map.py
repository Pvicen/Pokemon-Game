from .combat import pokemon_combat  # type: ignore
from .models import Pokemon, EvolvedPokemon  # type: ignore

import readchar
import os
import random
def map():
    
    POSITION_X = 0
    POSITION_Y = 1
    
    obstacle_definition = """\
####################################################################################################
#                                                                                                  #
#    ########        ########       #######      #####        #######       #######        ######  #
#    #      #        #      #       #     #      #   #        #     #       #     #        #    #  #
#    #      ##########      ########     ########   ##########     #########     ##########    #   #
#    #                                                                                        #    #
#    ##########   #######   ####################   #############   ##################   ########   #
#          #      #     #   #               ##     #           #   ##                #       ##    #
#   ####   #      #     #####   #########   ##     #####   #####   ##   #########    ##########    #
#   #  #   ########     #   #   #       #          #   #   #   #        #       #    #             #
#   #  ###########      #   #####       ############   #####   ############       ####     #########
#   #                                        #                           #                     #   #
#   #########################################   #######################   ###################  #   #
#                                                                                    #             #
#   ####################   ###################   #######################   #########################
#   #                  #   #                 #   #                     #   #                       #
#   #   #############  #####   ###########   #####   ##########   ######   #######   #######    ####
#   #   #                                                             #                         #  #
#   #####   ############################################################   ####################### #
#         #                                                                                        #
####################################################################################################\
"""
    obstacle_definition = [list(row) for row in obstacle_definition.split("\n")]
    
    MAP_WITHD = len(obstacle_definition[0])
    MAP_HEIGHT = len(obstacle_definition)
    TRAINERS_IN_MAP = 8
    
    end_game = False
    died = False
    
    my_position = [2, 2]
    map_objets = []
    
    # Generate random objets on the map
    while len(map_objets) < TRAINERS_IN_MAP: 
        new_position = [random.randint(0, MAP_WITHD - 1), random.randint(0, MAP_HEIGHT - 1)]
                
        if new_position not in map_objets and new_position != my_position and obstacle_definition[new_position[POSITION_Y]][new_position[POSITION_X]] != "#":
            map_objets.append(new_position)
        
    #Main loop
    while not end_game:
        
        os.system("cls")
        
        #Drawing the map
        print(" " + "_" * MAP_WITHD * 2 + " ")
        
        for coordinate_y in range(MAP_HEIGHT):
            print("|", end="")	
        
            for coordinate_x in range(MAP_WITHD):
                char_to_draw = "  "
                object_in_cell = None
                
                
                for map_objet in map_objets:
                    if map_objet[POSITION_X] == coordinate_x and map_objet[POSITION_Y] == coordinate_y:  
                        char_to_draw = " $"
                        object_in_cell = map_objet
                        
                if my_position[POSITION_X] == coordinate_x and my_position[POSITION_Y] == coordinate_y:
                    char_to_draw = " @"
                    
                    if object_in_cell:
                        pokemon_combat(player_pokemon=None, enemy_pokemon=None)
                        map_objets.remove(object_in_cell)
                        
                    
                if obstacle_definition[coordinate_y][coordinate_x] == "#":
                    char_to_draw = "##"

                print(char_to_draw, end="")
            print("|")
   
        print(" " + "_" * MAP_WITHD * 2 + " ")
    
        #User movement
        
        direction = readchar.readchar()
        
        if direction == "w":
            new_position = [my_position[POSITION_X], (my_position[POSITION_Y] - 1) % MAP_WITHD]
            
        elif direction == "s":
            new_position = [my_position[POSITION_X], (my_position[POSITION_Y] + 1) % MAP_WITHD]
            
        elif direction == "a":
            new_position = [(my_position[POSITION_X] - 1) % MAP_WITHD, my_position[POSITION_Y]]
            
        elif direction == "d":
            new_position = [(my_position[POSITION_X] + 1) % MAP_WITHD, my_position[POSITION_Y]]
            
        elif direction == "q":
            end_game = True
            
        if new_position:
            if obstacle_definition[new_position[POSITION_Y]][new_position[POSITION_X]] != "#":
                my_position = new_position
            
        os.system("cls")
        
    if died:
        print("Has muerto")