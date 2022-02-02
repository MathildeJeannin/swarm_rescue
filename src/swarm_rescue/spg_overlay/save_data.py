import csv
import os
import cv2
import pygame
from datetime import datetime
from time import strftime
from pathlib import Path

from spg_overlay.write_pdf import WritePdf

class SaveData:
    def __init__(self, num_eq):
        self.num_eq = num_eq
        date = datetime.now()
        self.directory = str(Path.home()) + '/Resultats_ChallengeIntelligenceRepartie'
        # self.path = self.directory + '/equipe_{}_{}'.format(str(self.num_eq), date.strftime("%d_%m_%Y_%H_%M_%S"))
        self.path = self.directory + '/equipe_{}_{}'.format(str(self.num_eq), date.strftime("%d_%m_%Y"))
        
        try:
            os.mkdir(self.directory)
            os.mkdir(self.path)
        except:
            try: os.mkdir(self.path)
            except: 
                pass
        fichier = open(self.path + "/eq_{}".format(str(self.num_eq)) + ".csv",'a')
        fichier.close()
        if os.path.getsize(self.path + "/eq_{}".format(str(self.num_eq)) + ".csv") == 0:
            self.add_line([('Group', 'Zone', 'Round', 'Rescued Percent', 'Exploration Score', 
            'Elapsed Time Step', 'Time To Rescue All', 'Time Score', 'Final Score')])

        self.my_pdf = WritePdf()



    def fill_pdf(self):
        self.my_pdf.generate_pdf(self.num_eq, self.path)


    def add_line(self, data):
        fichier = open(self.path + "/eq_{}".format(str(self.num_eq)) + ".csv",'a')
        obj = csv.writer(fichier)
        for element in data:
            obj.writerow(element)
        fichier.close()
          

    def save_images(self, im, im_explo, zone, num_round):
        pygame.image.save(im, self.path + "/screen_{}_rd{}_eq{}.jpg".format(zone, str(num_round), str(self.num_eq)))
        cv2.imwrite(self.path + "/screen_explo_{}_rd{}_eq{}.jpg".format(zone, str(num_round), str(self.num_eq)), im_explo)
