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
        self.df = pandas.DataFrame(fichier)
        self.df = self.df.loc[self.df["Group"] != "Group"]

        for column in self.df.columns: 
            try: 
                self.df[column] = self.df[column].astype(float)
            except:
                pass
        
        self.list_df_map = []
        ## create df by map
        self.names_maps = ['easy', 'no_comm_area', 'no_gps_area', 'kill_area']
        for name_map in self.names_maps:
            self.list_df_map.append(self.df.loc[self.df["Map"] == name_map])

        ## create data that can be used by fpdf
        i = 0
        final_scores = []
        self.data.append(['Environnement', 'Score Exploration', 'Score Sauvetages', 'Score Temps', 'Score Total'])
        for df in self.list_df_map:
            final_scores.append(df["Final Score"].mean())
            self.data.append([self.names_maps[i], df["Exploration Score"].mean(), df["Rescued Percent"].mean(), df["Time Score"].mean(), df["Final Score"].mean()])
            i+=1

        score_final = 3*final_scores[0] + final_scores[1] + final_scores[2] + final_scores[3] 
        return score_final


    def add_table(self): #data format [['ligne 1 colonne 1', 'ligne 1 colonne 2'], ['ligne 2 colonne 1', 'ligne 2 colonne 2']]
        col_width = self.epw/5 

        self.pdf.set_font('Arial', 'B', 11)
        self.pdf.cell(0, 0, 'Performances', align = 'C')
        self.pdf.ln(2*self.th)

        self.pdf.set_font('Arial', '', 10)


        score_final = self.calcul_data()

        for row in self.data:
            for datum in row:
                if type(datum)!=str: 
                    datum = "%.2f" % datum
                    datum = str(datum)
        
                self.pdf.cell(col_width, self.th, datum, border=1)
 
            self.pdf.ln(self.th)

        self.pdf.ln(2*self.th)
        self.pdf.set_font('Arial', 'B', 11)
        self.pdf.cell(0, 0, "Score final : %.2f" % (score_final/6))
        self.pdf.ln(2*self.th)
        self.pdf.set_font('Arial', '', 11)
        self.pdf.multi_cell(self.epw, 1.5*self.th, "Avec :\nScore Total = (0.7*Score Sauvetages + 0.2*Score Exploration + 0.1*Score Temps)*100\nScore Final = (3*Score Total Easy + Score Total No comm area + Score Total No GPS area + Score Total Kill area)/6")
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
        for i in range(len(self.names_maps)):
            try:
                self.pdf.add_page()
                df = self.list_df_map[i]
                max_finale_score = max(df["Final Score"])
                ligne_best_rd = df.loc[df["Final Score"] == max_finale_score]
                best_rd = int(ligne_best_rd["Round"])

                self.pdf.cell(0, 0, "Dernière image carte {}, round {}".format(self.names_maps[i], best_rd))
                self.pdf.ln(2*self.th)
                self.pdf.image("auto_evaluation/equipe_{}/screen_{}_rd{}_eq{}.jpg".format(str(num_eq), self.names_maps[i], str(best_rd), str(num_eq)), h = 100)
                self.pdf.ln(2*self.th)
                self.pdf.cell(0, 0, "Exploration carte {}, round {}".format(self.names_maps[i], best_rd))
                self.pdf.ln(2*self.th)
                self.pdf.image("auto_evaluation/equipe_{}/screen_explo_{}_rd{}_eq{}.jpg".format(str(num_eq), self.names_maps[i], str(best_rd), str(num_eq)), h = 100)
                self.pdf.ln(4*self.th)
            except:
                pass

    def generate_pdf(self, num_eq, nb_rounds):
        self.num_eq = num_eq
        self.header()
        self.add_table()
        self.add_histo()
        self.add_screen(num_eq, nb_rounds)
        self.pdf.output('auto_evaluation/equipe_{}/Performance_equipe_{}.pdf'.format(str(self.num_eq), str(self.num_eq)), 'F')

