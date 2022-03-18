#**************************************************************
# Funzioni per fare un sampling basato sul DBSCAN
#**************************************************************

from GeoSampling import ObjFunZoom as objz

from sklearn.cluster import DBSCAN
import math

#-------------------------------------------------------
# Applicazione del metodo di clustering DBSCAN ai dati
#-------------------------------------------------------

def DBSCANmodel(dati, eps_meter = 10):

    """Applicazione del metodo DBSCAN
    
    Applico il metodo DBSCAN per raggruppare i punti in cluster, per poi sost
    """

    # Conversione da metri a gradi del valore di eps
    radius = 6371000
    eps = 360*eps_meter/(2*math.pi*radius)

    # Applicazione modello DBSCAN
    model = DBSCAN(eps, min_samples=2).fit(dati)

    # Aggiunta label
    # Il DBSCAN mette -1 per tutti i punti separati dal clustering
    dati['Labels'] = model.labels_

    return dati

#----------------------------------------------------------
# Correzione alle label del DBSCAN
#----------------------------------------------------------

def DBSCANlabels(dati):

    """Correzione delle label del DBSCAN
    
    A partire da un dataset che ha le label come vengono restituite dal DBSCAN su Scikit-Learn (quindi con -1 nei noise points), assegniamo le label come me le aspetto -- quindi, ogni noise point costituisce un cluster a se stante.
    """

    # Prendo i dati con label = -1
    # e aggiungo come label un numero progressivo per ogni punto
    my_dati = dati[dati['Labels'] == -1]
    maximum = max(dati['Labels'])+1 #Primo valore ammissibile dalla label
    my_dati.insert(3, 'Prog_Number', range(maximum, maximum + len(my_dati)))
    my_dati = my_dati['Prog_Number']

    # Metto assieme le label che ho appena creato per i dati con label = -1
    # Con le label già assegnate dal clustering
    dati_joined = dati.merge(my_dati, how = 'outer', left_index = True, right_index = True)
    dati_joined['Prog_Number'] = dati_joined['Prog_Number'].fillna(dati_joined['Labels'])
    dati_joined = dati_joined[['Latitude', 'Longitude', 'Prog_Number']]
    dati_joined = dati_joined.rename({'Prog_Number': 'Label'}, axis = 1)

    # Aggiungo la colonna 'Point Name' (che mi serve per applicare la funzione di ObjFunZoom)
    dati_joined['Point_Name'] = dati_joined.index

    return dati_joined

#------------------------------------------------------------
# Metodo di sampling basato sul clustering DBSCAN
#--------------------------------------------------------------

def DBSCANsampling(dati, eps_meter = 10):

    """Utilizzo del modello di DBSCAN come funzione di sampling
    
    Applicazione del modello di clustering DBSCAN come funzione di sampling, come alternativa alla mia funzione di sampling.
    """

    # Applicazione del modello DBSCAN
    sampled = DBSCANmodel(dati, eps_meter)

    # Correzione alle label
    sampled = DBSCANlabels(sampled)

    # Sostituzione di ogni punto con il suo centroide
    sampled = objz.add_centroids(sampled)

    # Trasformo i nomi dei punti in indici
    sampled = sampled.sort_values('Point_Name')
    sampled = sampled.set_index('Point_Name')

    return sampled