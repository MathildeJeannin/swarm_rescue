from re import M
import time
from typing import final
import pygame
from simple_playgrounds.engine import Engine

from spg_overlay.fps_display import FpsDisplay
from spg_overlay.misc_data import MiscData
from spg_overlay.score_manager import ScoreManager

from maps.map_lidar_communication import MyMapLidarCommunication
from maps.map_random import MyMapRandom
from maps.map_compet_01 import MyMapCompet01

from solutions.my_drone_lidar_communication import MyDroneLidarCommunication
from solutions.my_drone_random import MyDroneRandom

## new
from auto_evaluation.auto_review_template import write_pdf

import csv
import time 
import os
import cv2
##

class MyMap(MyMapCompet01):
    pass


class MyDrone(MyDroneLidarCommunication):
    pass


class Launcher:
    def __init__(self):
        self.display = True
        self.nb_rounds = 5
        self.rescued_number = 0
        self.score_exploration = 0
        self.total_time = 0
        self.mean_time = 0

        self.my_map = MyMap()
        self.with_com = True

        self.score_manager = ScoreManager(number_drones=self.my_map.number_drones,
                                          time_step_limit=self.my_map.time_step_limit,
                                          real_time_limit=self.my_map.real_time_limit,
                                          total_number_wounded_persons=self.my_map.number_wounded_persons)

        # BUILD DRONES
        misc_data = MiscData(size_area=self.my_map.size_area,
                             number_drones=self.my_map.number_drones)
        drones = [MyDrone(identifier=i, misc_data=misc_data)
                  for i in
                  range(self.my_map.number_drones)]

        self.my_map.set_drones(drones)

        ## new ##
        self.my_pdf = write_pdf()
        self.num_eq = 'x'
        self.name_map = input("Map (easy, no_comm_area, no_gps_area, kill_area): ")        
        self.wounded = self.my_map.number_wounded_persons
        ##

    def reset(self):
        self.rescued_number = 0
        self.score_exploration = 0
        self.mean_time = 0

        self.my_map = MyMap()
        self.with_com = True

        self.score_manager = ScoreManager(number_drones=self.my_map.number_drones,
                                          time_step_limit=self.my_map.time_step_limit,
                                          real_time_limit=self.my_map.real_time_limit,
                                          total_number_wounded_persons=self.my_map.number_wounded_persons,
                                          )

        # BUILD DRONES
        misc_data = MiscData(size_area=self.my_map.size_area)
        drones = [MyDrone(identifier=i, misc_data=misc_data)
                  for i in
                  range(self.my_map.number_drones)]

        self.my_map.set_drones(drones)

    def define_all_messages(self):
        messages = []
        number_drones = len(self.my_map.drones)
        for i in range(0, number_drones):
            if self.with_com:
                msg_data = self.my_map.drones[i].define_message()
                one_message = (self.my_map.drones[i].communication, msg_data, None)
                messages.append(one_message)
        return messages

    def one_round(self):
        self.reset()
        my_drones = self.my_map.drones
        my_playground = self.my_map.playground

        engine = Engine(playground=my_playground, time_limit=self.my_map.time_step_limit, screen=self.display)

        fps_display = FpsDisplay(period_display=0.5)

        self.rescued_number = 0
        time_rescued_all = 0
        self.my_map.explored_map.reset()

        start_real_time = time.time()

        while engine.game_on:

            # print("time=", engine.elapsed_time)
            if self.display:
                engine.update_screen()

            engine.update_observations(grasped_invisible=True)

            self.my_map.explored_map.update(my_drones)

            # COMPUTE ALL THE MESSAGES
            messages = self.define_all_messages()

            # COMPUTE ACTIONS
            actions = {}
            for i in range(0, self.my_map.number_drones):
                actions[my_drones[i]] = my_drones[i].control()

            my_drones[0].display()

            terminate = engine.step(actions, messages)

            # REWARDS
            new_reward = 0
            for i in range(0, self.my_map.number_drones):
                new_reward += my_drones[i].reward

            if new_reward != 0:
                self.rescued_number += new_reward

            # if display:
            #     time.sleep(0.002)

            if self.rescued_number == self.my_map.number_wounded_persons and time_rescued_all == 0:
                time_rescued_all = engine.elapsed_time

            end_real_time = time.time()
            real_time_elapsed = (end_real_time - start_real_time)
            if real_time_elapsed > self.my_map.real_time_limit:
                print("The real time limit is reached !...")
                terminate = True

            if terminate:
                engine.game_on = False

            # fps_display.update()

        ## new
        im = engine._screen
        pygame.image.save(im, "auto_evaluation/equipe_{}/screen_{}_rd{}_eq{}.jpg".format(str(self.num_eq), self.name_map, str(self.actual_round), str(self.num_eq)))
        
        im_explo = self.my_map.explored_map._map_exploration
        cv2.imwrite("auto_evaluation/equipe_{}/screen_explo_{}_rd{}_eq{}.jpg".format(str(self.num_eq), self.name_map, str(self.actual_round), str(self.num_eq)), im_explo)
        ##

        engine.terminate()

        self.score_exploration = self.my_map.explored_map.score()
        # self.my_map.explored_map.display()

        return engine.elapsed_time, time_rescued_all, self.score_exploration, self.rescued_number
    

    ## new
    def fill_csv(self, data):
        fichier = open('auto_evaluation/equipe_{}/equipe_{}.csv'.format(str(self.num_eq), str(self.num_eq)),'a')
        obj = csv.writer(fichier)
        for element in data:
            obj.writerow(element)
        fichier.close()
        

    def fill_pdf(self, num_eq, nb_rounds):
        self.my_pdf.generate_pdf(num_eq, nb_rounds)
    ##

    
    def go(self):
        ## new
        try:
            os.mkdir('auto_evaluation/equipe_{}'.format(str(self.num_eq)))
        except:
            pass
        data = []
        data.append(('Group', 'Map', 'Round', 'Rescued Percent', 'Exploration Score', 
        'Elapsed Time Step', 'Time To Rescue All', 'Time Score', 'Final Score'))
        ##


        for i in range(0, self.nb_rounds):
            ## new
            self.actual_round = i 
            ##

            elapsed_time_step, time_rescued_all, score_exploration, rescued_number = self.one_round()

            self.total_time += elapsed_time_step
            self.mean_time = self.total_time / (i + 1)
            final_score = self.score_manager.compute_score(rescued_number, score_exploration, time_rescued_all)
            print("*** Round", i,
                  ", rescued number =", rescued_number,
                  ", exploration score =", "{:.2f}".format(score_exploration),
                  ", elapse time step =", elapsed_time_step,
                  ", time to rescue all =", time_rescued_all,
                  ", final score = ", "{:.2f}".format(final_score)
                  )

            ## new
            percent_rescued = self.score_manager.percentage_rescue
            score_time_step = self.score_manager.score_time_step
            ## percent rescued to have comparable data in table/figure
            data.append((str(self.num_eq), str(self.name_map), str(self.actual_round), str(percent_rescued), "%.2f" % score_exploration, 
                        str(elapsed_time_step), str(time_rescued_all), str(score_time_step) , "%.2f" % final_score ))
        
        
        self.fill_csv(data)
        self.fill_pdf(self.num_eq, self.nb_rounds)
        ##


if __name__ == "__main__":
    launcher = Launcher()
    launcher.go()
