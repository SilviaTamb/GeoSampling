
#************************************************************************************
# Questo file contiene le funzioni necessarie a importare e modificare i dati
#************************************************************************************

import pandas as pd
import numpy as np

#----------------------------------
# Funzione di data preparation
#----------------------------------

def db_preparation(figures):

    """Standardizzazione del database
    
    Il database di input è un database già importato in Pandas che contiene, tra le varie colonne, 
    la colonna ID_EXT e la colonna GEOM, dove la colonna ID_EXT contiene l'id del poligono, e la colonna GEOM 
    è l'elenco delle coordinate: in particolare, contiene prima alcune tag di GML, e poi le coordinate 
    separate da virgola, e infine le end tag di GML. Questo codice vuole creare un db lungo che contiene 
    la Latitudine e la Longitudine in colonne distinte.
    """

    #TODO: check campi

    # Eliminazione dei tag
    # La colonna 'GEOM_corr' contiene l'elenco di tutte le coordinate di un poligono
    figures['GEOM_corr'] = figures['GEOM'].str.replace('</?gml:(?:[a-zA-z=",\.\s])+>', '', regex = True)
    figures['GEOM_corr'] = figures['GEOM_corr'].str.replace('<.+>', '', regex = True)
    figures['GEOM_corr'] = figures['GEOM_corr'].str.strip() #spazi all'inizio e alla fine

    # Separazione delle coordinate
    # La colonna 'coords' contiene per ciascun punto le coordinate, separate da virgola.
    figures['coords'] = figures['GEOM_corr'].str.split('\s')
    figures = figures.explode('coords', ignore_index = True)
    
    # Separazione delle coordinate in colonne
    # Creo le colonne 'Latitudine e 'Longitudine' in un database diverso.
    df = figures['coords'].str.split(',', expand = True)
    df = df.rename(columns = {0: 'Longitude', 1: 'Latitude'})
    df['Latitude'] = df['Latitude'].astype(float)
    df['Longitude'] = df['Longitude'].astype(float)
    
    # Metto assieme i due database
    figures = pd.merge(figures, df, left_index=True, right_index=True)
    figures = figures.drop(labels = ['GEOM', 'GEOM_corr', 'coords'], axis = 1)
    
    return figures


#--------------------------------------
# Funzione di anonimizzazione dei dati
#--------------------------------------

def anonimization(figura):

    """Funzione di anonimizzazione dei punti
    
    Funzione di anonimizzazione dei punti dati per poter riportare nella tesi alcune immagini relative ai poligoni senza rivelare le coordinate degli impianti effettivi.Questa funzione anonimizza tutto ponendo un punto qualunque a (0,0) e calcolando latitudine e longitudine relativa rispetto a quel punto; e poi aggiunge un rumore bianco gaussiano con media 0 e deviazione standard 1e-5 (per non spostare troppo i punti). 
    """

    # Punto di riferimento
    latref = figura['Latitude'].iloc[0]
    lonref = figura['Longitude'].iloc[0]

    # Anonimizzazione relativa al primo punto
    figura['Latitude'] = figura['Latitude']-latref
    figura['Longitude'] = figura['Longitude']-lonref

    # Rumore bianco
    noise = np.random.normal(0,1e-5,len(figura))
    figura['Latitude'] = figura['Latitude'] + noise
    figura['Longitude'] = figura['Longitude'] + noise

    return figura