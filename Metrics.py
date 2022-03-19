#******************************************************************************************
# Questo script contiene le metriche per confrontare le semplificazioni tra di loro.
#******************************************************************************************

import numpy as np
import pandas as pd
from numpy.linalg import norm
import math
from shapely.geometry import Polygon

from GeoSampling import Periodics as pc

#---------------------------------------------------------
# CALCULATE AREA OF A POLYGON
#---------------------------------------------------------

def PolyArea(dati):

    """Calcola l'area di un poligono"""

    x = list(dati['Latitude'])
    y = list(dati['Longitude'])
    pgon = Polygon(zip(x, y))
    Area = pgon.area

    return Area

#------------------------------------------------------
# Gruppi di punti tolti consecutivi
#------------------------------------------------------

def diffPoints(orig, sampled):

    """Gruppi di punti tolti consecutivi

    Dato il poligono originale (orig, non resettato) e quello ottenuto 
    a seguito del sampling (sampled), questa funzione mi calcola un dataframe che contiene
    i gruppi di punti tolti consecutivi, basandosi sul fatto che tutti i punti di sampled
    stanno in orig, e in orig ci sono dei punti in più.
    """
    
    # Reset dei punti originali
    orig = pc.reset_data(orig)

    # Punti mancanti
    allpoints = list(orig.index.values)
    remaining = list(sampled.index.values)
    lostpoints = np.array([item for item in allpoints if item not in remaining])

    if len(lostpoints) == 0:
        df = pd.DataFrame(columns=['LostPoints','Difference','id_period'])
        return df

    # Identifico i gruppi di punti consecutivi tramite due passaggi:
    # - Prima faccio le differenze tra [i] e [i+1]; (diffpoints)
    # - In base alle differenze, assegno un id consecutivo identico per tutti i gruppi di punti.

    diffpoints = np.insert(np.diff(lostpoints), 0, 0)

    df = pd.DataFrame({
        'LostPoints': pd.Series(lostpoints),
        'Difference': pd.Series(diffpoints)
    })

    df['id_period'] = pd.Series(1 + np.cumsum(df['Difference'] > 1))
    
    return df

#------------------------------------------------------
# Valore assoluto della differenza di area
#------------------------------------------------------

def diffAbsArea(orig, sampled):

    """Differenza in area tra orig (dati origiinali) e sampled (dati campionati)
    
    Questa funzione calcola la differenza in aria tra il poligono originale (orig)
    e il poligono ottenuto a seguito del sampling (sampled). 
    Questa funzione è scritta basandosi sul fatto che tutti i punti di sampled stiano in orig,
    e in più in orig ci sono dei punti in più; e calcola la differenza di area in "valore assoluto".
    -- cioè, se sampled aggiunge un pezzo o ne toglie, è indifferente.

    NOTA: ho dovuto calcolarla così la differenza di area perché non posso semplicemente 
    calcolare l'area di orig, l'area di sampled e fare la differenza, perché
    se le due aree sono circa uguali perché sampled, da orig, ha tolto un pezzo e ne ha aggiunto
    un altro di area circa identica, l'area è circa la stessa.
    """

    # Dataframe dei poligoni dei punti consecutivi
    df = diffPoints(orig, sampled)

    # Bisogna aver tolto qualche punto! Altrimenti, la differenza di area è 0.
    if len(df) == 0:
        return 0

    # Per ognuno dei gruppi di punti consecutivi:
    # - Aggiungo *il punto prima* e *il punto dopo*;
    # - Calcolo l'area formata da questo insieme di punti.
    # - La aggiungo al totale.

    totalArea = 0
    orig = pc.PC(orig) #Condizioni al contorno periodiche (per prendere lowlimit e uplimit)

    # Per ogni gruppo di punti non consecutivi:
    for i in range(1, df['id_period'].max()+1):

        # Prendo gli indici del punto prima e del punto dopo
        lowlimit = df[df['id_period'] == i]['LostPoints'].min() - 1 #Indice del punto prima
        uplimit = df[df['id_period'] == i]['LostPoints'].max() + 1 #Indice del punto dopo

        # Considero la lista di indici
        indexes = list(df[df['id_period'] == i]['LostPoints']) #Elenco di indici
        indexes = np.insert(indexes, 0, lowlimit) #Inserisci lowlimit prima della posizione 0
        indexes = np.append(indexes, uplimit) #Inserisci uplimit alla fine.
        indexes = list(indexes)

        # Calcolo l'area
        resetted = orig.loc[indexes]
        Area = abs(PolyArea(resetted))
        totalArea = abs(totalArea) + abs(Area)

    return totalArea


#----------------------------------------------------------
# Differenza di area relativa
#----------------------------------------------------------

def diffArea(orig, sampled):

    """Differenza di area relativa tra orig e sampled.

    Questa funzione calcola la differenza in area tra il poligono originale (orig) e il poligono ottenuto a
    seguito del sampling (sampled), entrambi nel formato di dataframe di Pandas per cui una colonna si chiama
    'Latitude' e una colonna si chiama 'Longitude'.
    NOTA: questa differenza è una differenza tra due aree in gradi al quadrato, ma non conta perché è una
    differenza relativa.
    """

    orig_area = abs(PolyArea(orig))
    diff_area = abs(diffAbsArea(orig, sampled))

    return diff_area/orig_area


#----------------------------------------------------
# Scarto massimo tra i punti
#----------------------------------------------------
# La formula della distanza tra un punto e una retta è questa:
# https://stackoverflow.com/questions/39840030/distance-between-point-and-a-line-from-two-points

# Ed è spiegata bene qui:
# https://www.nagwa.com/en/explainers/939127418581/
#---------------------------------------------------

def maxDistance(orig, sampled):

    """Scarto massimo tra orig e sampled.

    Dato il poligono originale (orig, formato input) e il poligono campionato (sampled, senza periodiche),
    entrambi nel formato di Pandas con una colonna che si chiama 'Latitude' e una che si chiama 'Longitude', 
    calcolo lo scarto massimo tra i due, considerando anche in questo caso scarti sempre positivi.
    """

    # Dataframe dei poligoni dei punti consecutivi
    df = diffPoints(orig, sampled)

    # Bisogna aver tolto qualche punto! 
    # Altrimenti, lo scarto massimo è zero
    if len(df) == 0:
        return 0

    # Per ognuno dei gruppi di punti consecutivi:
    # - Aggiungo il punto prima del primo (A) e il punto dopo l'ultimo (B);
    # - Considero il vettore AB
    # - Calcolo la distanza tra ogni punto sottratto e il vettore AB (distanza punto-retta)
    # - Prendo il massimo
    # - Prendo il massimo di ogni ciclo

    totalmax = 0
    orig = pc.PC(orig) #Condizioni al contorno periodiche (per prendere lowlimit e uplimit)

    for i in range(1, df['id_period'].max()+1):

        # Punto prima e punto dopo
        lowlimit = df[df['id_period'] == i]['LostPoints'].min() - 1
        uplimit = df[df['id_period'] == i]['LostPoints'].max() + 1

        # Lista di punti
        indexes = list(df[df['id_period'] == i]['LostPoints'])
        indexes = np.insert(indexes, 0, lowlimit) #Inserisci lowlimit prima della posizione 0
        indexes = np.append(indexes, uplimit) #Inserisci uplimit alla fine.
        indexes = list(indexes)

        # Poligono con quei punti
        pol = orig.loc[indexes]

        # Base del poligono (vettore AB)
        baseA = pol.iloc[0].to_numpy()
        baseB = pol.iloc[len(pol)-1].to_numpy()
        base = baseB - baseA

        # Punti eliminati
        points = pol.iloc[1:len(pol)-1].to_numpy()

        # Distanze tra ogni punto e la base
        distances = np.abs(np.cross(base, points-baseA)/norm(base))

        # Prendo il massimo
        localmax = distances.max() # Massimo locale nel vettore delle distanze
        totalmax = max(localmax, totalmax) # Massimo globale nel ciclo

    # Conversione in metri
    radius = 6371000
    totalmax_meter = (2*math.pi*radius)*totalmax/360

    return totalmax_meter


#------------------------------------------------
# Scarto massimo relativo al dettaglio
#------------------------------------------------

def relativeDistance(orig, sampled, detail):

    """Scarto massimo relativo al dettaglio"""

    scarto = maxDistance(orig, sampled) #Dettaglio massimo
    relative = scarto/detail

    return relative