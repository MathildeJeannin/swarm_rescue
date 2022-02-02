from re import S
from time import strftime
from fpdf import FPDF
import pandas
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


class WritePdf:
    def __init__(self):
        self.num_eq = None
        self.names_zones = None
        self.th = None
        self.epw = None

        self.pdf = FPDF('P', 'mm', 'A4')
        self.pdf.add_page()
        self.data = []
        

    def _header(self):
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


    def _calcul_data(self, path):
        fichier = pandas.read_csv(path + '/eq_{}.csv'.format(str(self.num_eq), str(self.num_eq)))
        df = pandas.DataFrame(fichier)
        # df = df.loc[df["Group"] != "Group"]

        for column in df.columns: 
            try: 
                df[column] = df[column].astype(float)
            except:
                pass
        
        list_df_zone = []
        ## create df by zone
        self.names_zones = ['classic', 'no_comm_area', 'no_gps_area', 'kill_area']
        for name_zone in self.names_zones:
            list_df_zone.append(df.loc[df["Zone"] == name_zone])

        ## create data that can be used by fpdf
        i = 0
        final_scores = []
        self.data.append(['Environnement', 'Score Exploration', 'Score Sauvetages', 'Score Temps', 'Score Total'])
        for df in list_df_zone:
            final_scores.append(df["Final Score"].mean())
            self.data.append([self.names_zones[i], df["Exploration Score"].mean(), df["Rescued Percent"].mean(), df["Time Score"].mean(), df["Final Score"].mean()])
            i+=1

        score_final = 3*final_scores[0] + final_scores[1] + final_scores[2] + final_scores[3] 
        return score_final, list_df_zone


    def _add_table(self, path): 
        col_width = self.epw/5 

        self.pdf.set_font('Arial', 'B', 11)
        self.pdf.cell(0, 0, 'Performances', align = 'C')
        self.pdf.ln(2*self.th)

        self.pdf.set_font('Arial', '', 10)

        score_final, list_df_zone = self._calcul_data(path)

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
        self.pdf.multi_cell(self.epw, 1.5*self.th, "Avec :\nScore Total = (0.7*Score Sauvetages + 0.2*Score Exploration + 0.1*Score Temps)*100\nScore Final = (3*Score Total Classic + Score Total No comm area + Score Total No GPS area + Score Total Kill area)/6")
        self.pdf.ln(3*self.th)



    def _add_histo(self, path): 
        X = self.names_zones
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
        plt.xlabel('Zone')
        plt.legend(legend,loc=1)
        plt.savefig(path + '/histo_performance_eq{}.png'.format(str(self.num_eq), str(self.num_eq)), format='png')

        self.pdf.image(path + '/histo_performance_eq{}.png'.format(str(self.num_eq), str(self.num_eq)), h = 100) 
        self.pdf.ln(4*self.th)


    def _add_screen(self, num_eq, path):
        self.pdf.set_font('Arial', '', 10)
        score_final, list_df_zone = self._calcul_data(path)
        for i in range(len(self.names_zones)):
            try:
                self.pdf.add_page()
                df = list_df_zone[i]
                max_finale_score = max(df["Final Score"])
                ligne_best_rd = df.loc[df["Final Score"] == max_finale_score]
                best_rd = int(ligne_best_rd["Round"])

                self.pdf.cell(0, 0, "Dernière image de la simulation avec la zone {} active, meilleur round : round {}".format(self.names_zones[i], best_rd))
                self.pdf.ln(2*self.th)
                self.pdf.image(path + "/screen_{}_rd{}_eq{}.jpg".format(str(self.names_zones[i]), str(best_rd), str(num_eq)), h = 70)
                self.pdf.ln(2*self.th)
                self.pdf.cell(0, 0, "Exploration {}, round {}".format(self.names_zones[i], best_rd))
                self.pdf.ln(2*self.th)
                self.pdf.image(path + "/screen_explo_{}_rd{}_eq{}.jpg".format(self.names_zones[i], str(best_rd), str(num_eq)), h = 70)
                self.pdf.ln(4*self.th)
            except: 
                pass


    def generate_pdf(self, num_eq, path):
        self.num_eq = num_eq
        self._header()
        self._add_table(path)
        self._add_histo(path)
        self._add_screen(num_eq, path)
        self.pdf.output(path + '/Performance_equipe_{}.pdf'.format(str(self.num_eq), str(self.num_eq)), 'F')


