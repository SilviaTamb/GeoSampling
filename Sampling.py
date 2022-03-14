from GeoSampling import PeriodicConditions as pc
from GeoSampling import Periodics as pcs
from GeoSampling import RemovingPoints as rp
from GeoSampling import ObjFunZoom as z
from GeoSampling import RemovingLength as rl
from GeoSampling import PlotFunctions as pl
import math
import numpy as np
from numpy.linalg import norm
import seaborn as sns

#------------------------------------------------
# Funzione di sampling
#-------------------------------------------------

def Sampling(dati, detail = 10, par_buffer = 0.5, par_length = 2,
        finelength = True, minPoints = 4, analysis = False):

    """Sampling: funzione definitiva.
    Metto assieme: rimozione media, rimozione buffer, rimozione segmenti corti.
    Opzione finelength.
    Condizioni di uscita se ci sono pochi punti.
    Condizioni al contorno: periodics.
    Dettaglio dentro alla funzione di sampling, dettaglio dipendente dal quantile.
    Rendo dei parametri della funzione i fattori moltiplicativi del dettaglio.
    """

    # Reset dei dati (per le successive funzioni)
    orig_dati = pcs.reset_data(dati)

    # Step 2: Metodo della media (soglia fissa)
    # Sì condizioni al contorno (metto prima, tolgo dopo)
    dati_media = pcs.PC(orig_dati)
    dati_media = rp.rem_median(dati_media)
    dati_media = pcs.RC(dati_media)

    if analysis:
        analysisFunction(dati_media, 'Metodo della media')

    # Pochi punti: ignoro lo step
    if len(dati_media) < minPoints:
        dati_media = orig_dati

    # Step 3: metodo del buffer (soglia fissa)
    # La tolleranza dipende dal dettaglio
    # Sì condizioni al contorno (metto prima, tolgo dopo)
    dati_buffer = pcs.PC(dati_media)
    dati_buffer = rp.buffer(dati_buffer, tol_meter = detail*par_buffer)
    dati_buffer = pcs.RC(dati_buffer)

    if analysis:
        analysisFunction(dati_buffer, 'Metodo del buffer')

    # Pochi punti: ignoro lo step
    if len(dati_buffer) < minPoints:
        dati_buffer = dati_media
        
    # Step 4: segmenti corti (soglia fissa)
    # La tolleranza dipende dal dettaglio
    # Sì condizioni al contorno (metto prima, tolgo dopo)

    dati_corti = pcs.PC(dati_buffer)

    if finelength:
        dati_corti = rl.rem_finelength(dati_corti, lenmin_meter = par_length*detail)
    else:
        dati_corti = rl.rem_length(dati_corti, lenmin_meter = par_length*detail)

    dati_corti = pcs.RC(dati_corti)

    if analysis:
        analysisFunction(dati_corti, 'Metodo della lunghezza dei segmenti')

    # Pochi punti: ignoro lo step
    if len(dati_corti) < minPoints:
        dati_corti = dati_buffer

    return dati_corti


#-------------------------------------------------
# Funzione di dettaglio
#-------------------------------------------------

def r_detailq(dati, q = 0.15):

    """Calcolare il dettaglio "buono" a partire da un insieme di dati
    
    Questa funzione calcola il dettaglio "buono" (quello che restituisce una buona approssimazione
    della funzione vera) a partire dai punti. Lo calcolo così: calcolo tutte le distanze, e poi prendo il
    quantile 0.15 della funzione vera.
    """

    # Elenco delle distanze
    
    distances = []

    for i in range(0, len(dati)-2):
        A = dati.iloc[i].to_numpy()
        B = dati.iloc[i+1].to_numpy()
        distance = norm(A-B)
        radius = 6371000
        distance_meter = 2*math.pi*radius*distance/360 #Distanze in metri
        distances.append(distance_meter)

    detail = math.floor(np.quantile(distances, q))

    if detail == 0:
        detail = 0.01
    
    return detail

#----------------------------------------------------
# Funzione per testare i risultati del sampling
#-----------------------------------------------------

def analysisFunction(dati, title):

    """Funzioni di test da aggiungere eventualmente alla provaSampling"""

    print(title, len(dati))
    pl.plot_polygon(dati, title)