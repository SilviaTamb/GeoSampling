
#************************************************************************************************
# Questo file contiene le funzioni che rimuovono i punti se il segmento creato è troppo piccolo.
# ***********************************************************************************************

from shapely.geometry import LineString
import math

#--------------------------------------------------------------
# Rimozione dei punti che formano segmenti troppo corti
#--------------------------------------------------------------

def rem_length(dati, lenmin_meter = 100):

    """Rimozione dei punti che formano segmenti troppo corti. 

    A partire da un dataframe di Pandas per cui c'è una colonna che si chiama 'Latitude' e una che si chiama 'Longitude', 
    questa funzione considera la lunghezza del segmento tra due punti (AB), e se è più lunga di una certa lunghezza soglia,
    elimina B e considera AC (dove C è il punto sucessivo); altrimenti, considera B e ricomincia.
    Il primo argomento sono i dati nel formato sopra, il secondo argomento è la lunghezza minima del segmento.
    Valori consigliati per la lunghezza minima: 100m (valore predefinito)
    NOTA: condizioni al contorno necessarie, da porre FUORI dalla funzione.
    """

    # Da metri a gradi
    radius = 6371000
    lenmin = 360*lenmin_meter/(2*math.pi*radius)

    i = 0
    end = len(dati) - 1

    while i < end:
        
        values = dati[i:i+2]

        # Condizione di uscita dovuta alla rimozione dei punti in-place.
        if len(values) < 2:
            return dati
        
        # Definisco AB
        AB = LineString([
            (dati.iloc[i]['Latitude'], dati.iloc[i]['Longitude']), 
            (dati.iloc[i+1]['Latitude'], dati.iloc[i+1]['Longitude'])
        ])
        
        if AB.length > lenmin:
            i = i + 1
            
        else:
            dati = dati.drop(dati.iloc[i+1].name, axis = 0)
            end = end - 1
            
    return dati



#-------------------------------------------------------------------------------------------------
# Rimozione dei punti che formano segmenti troppo corti (tenendo conto del segmento successivo)
#--------------------------------------------------------------------------------------------------

def rem_finelength(dati, lenmin_meter = 100):

    """Rimozione dei punti che formano segmenti troppo corti (tenendo conto del segmento successivo)

    Questa funzione parte da rem_length e applica una piccola correzione. 
    Consideriamo i punti A, B, C, D, E; e immaginiamo che AB, BC e CD siano corti, e DE sia lungo: 
    se si applica rem_length, devono essere eliminati i punti B, C, D, e ci sarà un unico segmento che 
    connette AE. Ma se quel pezzo formato da tanti piccoli segmentini era importante 
    (perché definiva un "cambio di forma"), la forma viene cambiata molto. Quindi ecco come fare.
    Questa funzione considera tre punti successivi: A, B, C. Parto da A e misuro AB e BC. 
    Se BC supera la lunghezza minima, salto direttamente a considerare C; se invece BC non la supera, 
    allora ho i due casi come sopra: se AB è troppo corto, elimino B
    e al nuovo passo parto da A; altrimenti, tengo B e al nuovo passo parto da B.
    Il primo argomento sono i dati nel formato sopra, il secondo argomento è la lunghezza minima del segmento.
    Valori consigliati per la lunghezza minima: 100m (valore predefinito).
    NOTA: condizioni al contorno necessarie, da porre fuori dalla funzione.
    """

    # TODO: input check controls.

    # Da metri a gradi
    radius = 6371000
    lenmin = 360*lenmin_meter/(2*math.pi*radius)

    i = 0
    end = len(dati) - 2

    while i < end:

        values = dati[i:i+3]

        # Condizione di uscita dovuta alla rimozione dei punti in-place.
        if len(values) < 3:
            return dati
        
        # Definisco AB, BC

        AB = LineString([
            (values.iloc[0]['Latitude'], values.iloc[0]['Longitude']), 
            (values.iloc[1]['Latitude'], values.iloc[1]['Longitude'])
        ])
        
        BC = LineString([
            (values.iloc[1]['Latitude'], values.iloc[1]['Longitude']), 
            (values.iloc[2]['Latitude'], values.iloc[2]['Longitude'])
        ])
        
        # Test

        if BC.length > lenmin:
            i = i + 2
            
        if BC.length < lenmin and AB.length < lenmin:
            dati = dati.drop(values.iloc[1].name, axis = 0)
            end = end - 1
            
        if BC.length < lenmin and AB.length > lenmin:
            i = i + 1
            
    return dati