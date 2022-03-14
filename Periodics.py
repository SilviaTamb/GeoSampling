#***********************************************************************
# Questo file serve a definire le funzioni per le condizioni al contorno
#***********************************************************************

import pandas as pd

#-----------------------------------------------------
# RESET DATA
#-----------------------------------------------------

def reset_data(dati):

    """Reset dei dati (dai dati originali)
    
    A partire da un dataframe di Pandas di N+1 righe, indicizzate come 0...N,
    che rappresenta però un poligono con N punti distinti, 
    dove la riga 0 è uguale alla riga N, e l'ultimo "vero" punto è la riga N-1, 
    elimino l'ultima riga così che l'ultimo vero punto sia nell'ultima riga.
    """

    dati = dati.iloc[0:len(dati)-1]
    return dati


#-----------------------------------------------------
# CONDIZIONI PERIODICHE
#-----------------------------------------------------

def PC(dati):

    """Condizioni periodiche (da dati resettati)
    
    A partire da un dataframe di Pandas di N righe, indicizzate come 0...N-1,
    che rappresentano un poligono con N punti,
    creo un dataframe di N+2 righe, indicizzate come -1, 0..., N,
    in cui le righe 0...N-1 sono uguali al dataframe di partenza, e in più
    la riga -1 è uguale alla riga N-1 e la riga N è uguale alla riga 0.
    """

    # Dataset originale:
    #---------------------
    
    # Indice della prima riga: 0
    # Indice dell'ultima riga: len(dati)-1

    # Riga -1: deve essere uguale alla riga N-1
    add_top = pd.DataFrame([[dati.iloc[len(dati)-1]['Latitude'],
                            dati.iloc[len(dati)-1]['Longitude']]],
                            columns = ["Latitude", "Longitude"],
                            index = [-1])

    # Riga N: deve essere uguale alla riga 0
    add_bottom = pd.DataFrame([[dati.iloc[0]['Latitude'],
                            dati.iloc[0]['Longitude']]],
                            columns = ["Latitude", "Longitude"],
                            index = [len(dati)])

    # Aggiunta delle righe al dataframe
    dati = pd.concat([add_top, dati, add_bottom])

    return dati


#-------------------------------------------------------
# ELIMINAZIONE CONDIZIONI PERIODICHE
#-------------------------------------------------------

def RC(dati):

    """Rimuove le condizioni al contorno periodiche
    
    A partire da un dataframe di Pandas di N+2 righe, indicizzate come -1, 0, ..., N-1, N,
    che rappresenta però un poligono di N punti, in cui la riga -1 è uguale alla riga N-1 e
    la riga N è uguale alla riga 0, creo un dataframe di Pandas di N righe con le righe
    indicizzate come 0, N-1, eliminando la prima e l'ultima riga.
    """

    dati = dati.iloc[1:len(dati)-1, :]
    return dati