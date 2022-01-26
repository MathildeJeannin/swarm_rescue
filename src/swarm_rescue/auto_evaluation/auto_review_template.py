from re import S
from time import strftime
from fpdf import FPDF
import pandas
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


class write_pdf(FPDF):
    def __init__(self):
        self.pdf = FPDF('P', 'mm', 'A4')
        self.pdf.add_page()
        self.data = []
        

    def header(self):
        date = datetime.now()

         # Effective page width, or just epw
        self.epw = self.pdf.w - 2*self.pdf.l_margin

        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 0, 'Challenge Intelligence Répartie', align='C')

        self.pdf.set_font('Arial', '', 11)
        self.th = self.pdf.font_size
        self.pdf.ln(2*self.th)
        self.pdf.cell(0, 0, 'Equipe ' + str(self.num_eq), align = 'C')
        self.pdf.ln(2*self.th)
        self.pdf.cell(0, 0, "Généré le " + date.strftime("%d/%m/%Y - %H:%M"), align = 'C')

        self.pdf.ln(4*self.th)


    def calcul_data(self):
        fichier = pandas.read_csv('auto_evaluation/equipe_{}/equipe_{}.csv'.format(str(self.num_eq), str(self.num_eq)))
        df = pandas.DataFrame(fichier)
        df = df.loc[df["Group"] != "Group"]
        len_row, len_col = df.shape

        for column in df.columns: 
            try: 
                df[column] = df[column].astype(float)
            except:
                pass
        

        ## create df by map
        df_map_easy = df.loc[df["Map"] == "easy"]
        df_map_no_comm_area = df.loc[df["Map"] == "no_comm_area"]
        df_no_gps_area = df.loc[df["Map"] == "no_gps_area"]
        df_kill_area = df.loc[df["Map"] == "kill_area"]

        list_df_map = [df_map_easy, df_map_no_comm_area, df_no_gps_area, df_kill_area]

        ## create data that can be used by fpdf
        self.names_maps = ["Easy", "No comm area", "No GPS area", "Kill area"]
        i = 0
        final_scores = []
        self.data.append(['Environnement', 'Score Exploration', 'Score Sauvetages', 'Score Temps', 'Score Total'])
        for df in list_df_map:
            final_scores.append(df["Final Score"].mean())
            self.data.append([self.names_maps[i], df["Exploration Score"].mean(), df["Rescued Percent"].mean(), df["Time Score"].mean(), df["Final Score"].mean()])
            i+=1

        score_final = 3*final_scores[0] + final_scores[1] + final_scores[2] + final_scores[3] 
        return score_final

    # On veut un tableau avec pour un groupe donné pour chaque carte 
    # (pas pour chaque groupe car on veut le pdf apres avoir fait 
    # tourner la simu): 
    # moyenne explo, 
    # moyenne sauvetage 
    # moyenne temps sauvetage (pas)
    # moyenne score 
    # et le score final sous le tableau (checker ponderation)


    def add_table(self): #data format [['ligne 1 colonne 1', 'ligne 1 colonne 2'], ['ligne 2 colonne 1', 'ligne 2 colonne 2']]
        col_width = self.epw/5 
        # Ici on veut data = [['Round', 'Rescued Number', 
        # 'Exploration Score', 'Elapsed Time Step', 
        # 'Time To Rescue All', 'Final Score'], 
        # ['0', '5', '75%', '4729', '0s', '7.49']
        # ['1', '25', '98%', '5902', '398s', '15.49']
        # ]
        # data = raw_data
        #test

        self.pdf.set_font('Arial', 'B', 11)
        self.pdf.cell(0, 0, 'Performances', align = 'C')
        self.pdf.ln(2*self.th)

        self.pdf.set_font('Arial', '', 10)

        # raw_data[0, :] = ['Round', 'Rescued Number', 'Exploration Score', 
        # 'Elapsed Time Step', 'Time To Rescue All', 'Final Score']

        score_final = self.calcul_data()

        for row in self.data:
            for datum in row:
                if type(datum)!=str: 
                    datum = "%.2f" % datum
                    datum = str(datum)
                # Enter data in colums
                # Notice the use of the function str to coerce any input to the 
                # string type. This is needed
                # since pyFPDF expects a string, not a number.
                self.pdf.cell(col_width, self.th, datum, border=1)
 
            self.pdf.ln(self.th)

        self.pdf.ln(2*self.th)
        self.pdf.set_font('Arial', 'B', 11)
        self.pdf.cell(0, 0, "Score final : %.2f" % (score_final/6))
        self.pdf.ln(2*self.th)
        self.pdf.set_font('Arial', '', 11)
        self.pdf.multi_cell(self.epw, 1.5*self.th, "Avec :\nS(core Total = 0.7*Score Sauvetages + 0.2*Score Exploration + 0.1*Score Temps)*100\nScore Final = (3*Score Total Easy + Score Total No comm area + Score Total No GPS area + Score Totale Kill area)/6")
        self.pdf.ln(3*self.th)



    def add_histo(self): 
        X = self.names_maps
        Y_explo, Y_sauv, Y_score, Y_temps = [],[],[],[]
        legend = ['Exploration', 'Sauvetages', 'Temps', 'Score Total']
        for i in range(1,len(self.data)): 
            Y_explo.append(self.data[i][1])
            Y_sauv.append(self.data[i][2])
            Y_temps.append(self.data[i][3])
            Y_score.append(self.data[i][4]/100)

        width = 0.2  # épaisseur de chaque bâton
        pos = np.arange(len(X))
        Y_scale = np.arange(0, 1.1, 0.1)
        # Création du diagramme en bâtons (bâtons côte à côte)
        plt.bar(pos - 1.5*width, Y_explo, width, color='steelblue')
        plt.bar(pos - 0.5*width, Y_sauv, width, color='firebrick')
        plt.bar(pos + 0.5*width, Y_temps, width, color='darkolivegreen')
        plt.bar(pos + 1.5*width, Y_score, width, color='goldenrod')
        plt.xticks(pos, X)
        plt.yticks(Y_scale)
        plt.ylabel('Taux de réussite')
        plt.xlabel('Map')
        plt.legend(legend,loc=1)
        plt.savefig('auto_evaluation/equipe_{}/histo_performance_eq{}.png'.format(str(self.num_eq), str(self.num_eq)), format='png')

        self.pdf.image('auto_evaluation/equipe_{}/histo_performance_eq{}.png'.format(str(self.num_eq), str(self.num_eq)), h = 100) 
        self.pdf.ln(4*self.th)


    def add_screen(self, num_eq, nb_rounds):
        self.pdf.set_font('Arial', '', 10)
        names_map = ['easy', 'no_comm_area', 'no_gps_area', 'kill_area']
        for name_map in names_map:
            self.pdf.add_page()
            for i in range(nb_rounds):
                try: 
                    self.pdf.cell(0, 0, "Exploration carte {}, round {}".format(name_map, i+1))
                    self.pdf.ln(2*self.th)
                    self.pdf.image("auto_evaluation/equipe_{}/screen_{}_rd{}_eq{}.jpg".format(str(num_eq), name_map, str(i), str(num_eq)), h = 100)
                    self.pdf.ln(4*self.th)
                except:
                    pass

    ## a mettre dans __init__ 
    def generate_pdf(self, num_eq, nb_rounds):
        self.num_eq = num_eq
        self.header()
        self.add_table()
        self.add_histo()
        self.add_screen(num_eq, nb_rounds)
        self.pdf.output('auto_evaluation/equipe_{}/Performance_equipe_{}.pdf'.format(str(self.num_eq), str(self.num_eq)), 'F')



## pour remplir le pdf manuellement si les données ont été sauvées mais pas le PDF 
# num_eq = "a"
# names_map = ['easy', 'no_comm_area', 'no_gps_area', 'kill_area']
# nb_rounds = 2
# for name_map in names_map:
#     if __name__ == "__main__": 
#         pdf = write_pdf()
#         pdf.generate_pdf(num_eq, name_map, nb_rounds) 