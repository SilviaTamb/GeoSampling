# Removing points
from GeoSampling import ObjFunZoom as z
from GeoSampling import RemovingPoints as rp
from GeoSampling import RemovingLength as rl

# Help modules
from GeoSampling import Periodics as pcs
from GeoSampling import PlotFunctions as pl

# New modules
import math
import numpy as np
from numpy.linalg import norm
import seaborn as sns

#------------------------------------------------
# Funzione di sampling
#-------------------------------------------------

def Sampling(dati, detail = 10, par_identity = False,
        par_buffer = 0.5, par_length = 2,
        finelength = True, minPoints = 4, analysis = False, 
        ifzoom = False, par_zoomed = 0.5):

    """Funzione di sampling di un poligono.

    Funzione che, dato un set di dati rappresentanti un poligono, 
    effettua un sampling dei suoi punti con l'obiettivo di ridurre il numero di punti
    con una perdita accettabile in termini di area e di scarto massimo. 
    """

    # Reset dei dati (per le successive funzioni)
    orig_dati = pcs.reset_data(dati)

    #------------------------------------------------------
    # Rimozione dei punti sovrapposti
    # Sì condizioni al contorno (metto prima, tolgo dopo)
    #------------------------------------------------------
    dati_overlap = pcs.PC(orig_dati)
    dati_overlap = rp.rem_overlap(dati_overlap, par_identity)
    dati_overlap = pcs.RC(dati_overlap)

    if analysis:
        analysisFunction(dati_overlap, 'Metodo dei punti sovrapposti')

    if len(dati_overlap) < minPoints:
        dati_overlap = orig_dati
    
    #----------------------------------------------------
    # FACOLTATIVO: Metodo della funzione di zoom (lungo)
    # No condizioni al contorno
    #----------------------------------------------------

    if ifzoom:

        zoomed = z.ObjFunZoom(dati_overlap, d_meter = par_zoomed*detail)

        if analysis:
            analysisFunction(zoomed, 'Metoto dello zoom')

        if len(zoomed) < minPoints:
            zoomed = orig_dati

    else:
        zoomed = dati_overlap

    #------------------------------------------------------
    # Metodo della media (soglia fissa)
    # Sì condizioni al contorno (metto prima, tolgo dopo)
    #------------------------------------------------------

    dati_media = pcs.PC(zoomed)
    dati_media = rp.rem_median(dati_media)
    dati_media = pcs.RC(dati_media)

    if analysis:
        analysisFunction(dati_media, 'Metodo della media')

    if len(dati_media) < minPoints:
        dati_media = orig_dati

    #----------------------------------------------------------
    # Metodo del buffer (soglia dipendente dal dettaglio)
    # Sì condizioni al contorno (metto prima, tolgo dopo)
    #-----------------------------------------------------------

    dati_buffer = pcs.PC(dati_media)
    dati_buffer = rp.rem_buffer(dati_buffer, tol_meter = detail*par_buffer)
    dati_buffer = pcs.RC(dati_buffer)

    if analysis:
        analysisFunction(dati_buffer, 'Metodo del buffer')

    # Pochi punti: ignoro lo step
    if len(dati_buffer) < minPoints:
        dati_buffer = dati_media
    
    #---------------------------------------------------------------
    # Metodo dei segmenti corti (soglia dipendente dal dettaglio)
    # Sì condizioni al contorno (metto prima, tolgo dopo)
    #---------------------------------------------------------------

    dati_corti = pcs.PC(dati_buffer)

    if finelength:
        dati_corti = rl.rem_finelength(dati_corti, lenmin_meter = par_length*detail)
    else:
        dati_corti = rl.rem_length(dati_corti, lenmin_meter = par_length*detail)

    dati_corti = pcs.RC(dati_corti)

    if analysis:
        analysisFunction(dati_corti, 'Metodo della lunghezza dei segmenti')

    if len(dati_corti) < minPoints:
        dati_corti = dati_buffer

    #---------------------------------------------------------------
    # Correzione: ulteriore applicazione del metodo del buffer
    #---------------------------------------------------------------

    dati_buffer_2 = pcs.PC(dati_corti)
    dati_buffer_2 = rp.rem_buffer(dati_buffer_2, tol_meter = detail*par_buffer)
    dati_buffer_2 = pcs.RC(dati_buffer_2)

    if analysis:
        analysisFunction(dati_buffer_2, 'Metodo del buffer: seconda applicazione')

    if len(dati_buffer_2) < minPoints:
        dati_buffer_2 = dati_corti

    #----------------------------------
    # Fine sampling
    #-----------------------------------

    return dati_buffer_2


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