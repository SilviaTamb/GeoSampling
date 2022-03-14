# **********************************************************************************************
# Questo file contiene due funzioni che ho scritto per rimuovere i punti:
# rem_median, che rimuove i punti se sono sulla media degli altri due;
# rem_buffer, che rimuove i punti se sono nel buffer degli altri due.
# ***********************************************************************************************

from shapely.geometry import LineString, Point
import math

#-----------------------------------------------------------------------
# Funzione per rimuovere i punti se sono sulla media degli altri due
#-----------------------------------------------------------------------

def rem_median(dati, acc = 4):

    """Rimuove un punto se è sulla media degli altri due.
    
    A partire da un dataframe di Pandas per cui c'è una colonna che si chiama 'Latitude' e una che si chiama 
    'Longitude', questa funzione considera i punti a tre a tre (A, B, C): se B è la media degli altri due, 
    lo si rimuove. Il primo argomento sono i dati nel formato sopra, poi acc indica entro quante cifre 
    decimali la media deve essere uguale,infine inplace indica se i punti vanno rimossi 'in place', 
    oppure a parte in seguito.
    Valori consigliati per l'accuratezza: 4 (valore predefinito).
    NOTA: condizioni al contorno necessarie, da porre FUORI dal dataset.
    """

    i = 0
    end = len(dati)-2
    
    while i < end:
        
        values = dati[i:i+3]

        if len(values) < 3:
            return dati
        
        # Calcolo latitudine e longitudine media
        medLat = (values.iloc[0]['Latitude'] + values.iloc[2]['Latitude'])/2
        medLong = (values.iloc[0]['Longitude'] + values.iloc[2]['Longitude'])/2

        # Latitudine e longitudine da confrontare
        testLat = values.iloc[1]['Latitude']
        testLong = values.iloc[1]['Longitude']
            
        if round(medLat, acc) == round(testLat,acc) and round(medLong, acc) == round(testLong, acc):
            dati = dati.drop(values.iloc[1].name, axis = 0)
            end = end - 1
        else:
            i = i+1

    return dati


#---------------------------------------------------------------------
# Funzione per rimuovere i punti se sono nel buffer degli altri due
#---------------------------------------------------------------------

def rem_buffer(dati, tol_meter = 10):

    """Rimuove un punto se è sul buffer degli altri due.
    
    A partire da un dataframe di Pandas per cui c'è una colonna che si chiama 'Latitude' e una che si chiama 'Longitude', 
    questa funzione considera i punti a tre a tre (A, B, C): se B si trova nel buffer degli altri due, lo si rimuove. 
    "Trovarsi nel buffer" significa che traccio la linea tra A e C, e considero un buffer geometrico attorno a questa linea;
    se B si trova all'interno di questo buffer, "si trova nel buffer" e quindi verrà eliminato.
    Il primo argomento sono i dati nel formato sopra, poi tol indica quanto deve essere grande il buffer,
    infine inplace indica se i punti vanno rimossi 'in place', oppure a parte in seguito.
    Valori consigliati per la tolleranza: 10m (valore predefinito). 
    NOTA: condizioni al contorno periodiche necessarie, da porre FUORI dal dataset.
    """

    # Da metri a gradi
    radius = 6371000
    tol = 360*tol_meter/(2*math.pi*radius)

    i = 0
    end = len(dati)-2
    
    while i < end:
        
        values = dati[i:i+3]

        if len(values) < 3:
            return(dati)
        
        # Calcolo linea e punto corrispondente
        line = LineString([
            (values.iloc[0]['Latitude'], values.iloc[0]['Longitude']), 
            (values.iloc[2]['Latitude'], values.iloc[2]['Longitude'])
        ])
        point = Point(values.iloc[1]['Latitude'], values.iloc[1]['Longitude'])
        
        # Estendo la linea
        line = line.buffer(tol)    
            
        if point.within(line):
            dati = dati.drop(values.iloc[1].name, axis = 0)
            end = end - 1
        else:
            i = i+1
        
    return dati