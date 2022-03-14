#*************************************************************************
# Definizione di funzione obiettivo tramite zoom
#*************************************************************************

import pandas as pd
import itertools
from shapely.geometry import Point
import math
#import matplotlib.pyplot as plt

#-------------------------------------------------
# Dataframe df_points con buffer per ogni punto
# Lista di tutti i buffer
#-------------------------------------------------

def points_with_buffer(dati, d = 2*1e-4):

    """Dataframe con punti 'zoomati'.

    A partire da un dataframe di Pandas "resettato" (condizioni al contorno rimosse) in cui una colonna si chiama
    'Latitude' e una 'Longitude', genera i punti 'zoomati' (i poligoni) per ogni punto, e produce due output:
    una lista con tutti i poligoni, etichettati da un numero progressivo, e un dataframe con tutti i punti, 
    anch'essi etichettati dallo stesso numero progressivo, con associate le coordinate dei poligoni. 
    NOTA: qui il parametro d (diametro del punto) è considerato in GRADI.   
    """
    
    points = []
    
    # Calcolo il buffer per ogni punto
    for index, row in dati.iterrows():
        point = Point(row['Latitude'], row['Longitude'])
        point = point.buffer(d/2)
        points.append((index, point))
        
    # Creo un dataframe con il buffer per ciascun punto
    df_points = pd.DataFrame(points, columns = ['Point_Name', 'Buffer_Point'])

    # Dati originali con coordinate e nome
    new_dati = dati.copy(deep = True)
    new_dati.insert(0, 'Point_Name', range(0, 0 + len(new_dati)))
    
    # Metto assieme i due dataframe
    df_points = df_points.merge(new_dati, on = 'Point_Name')
    
    return df_points, points


#-----------------------------------------------------------------------------------
# Dataset groups: per ogni punto, le sue intersezioni con i punti a lui successivi
#-----------------------------------------------------------------------------------

def dataset_groups(lista):

    """Dataset groups: per ogni poligono, la lista delle sue intersezioni.

    Data una lista di poligoni "ordinati", ciascuno etichettato da un nome, questo produce
    la lista di ogni poligono con le intersezioni a lui successive, elencate in un insieme.
    Per esempio, ho queste intersezioni:

    2: {3, 4, 5}
    3: {4, 5, 6}

    Quindi l'intersezione tra 2 e 3 è inserita nel primo set e non nel secondo. 
    """
    
    #---------------
    # Trova tutte le intersezioni di ogni punto con ogni altro punto (a lui successivo)
    # e mettile nel dataframe 'df'.
    # Non ci sono ripetizioni. ES: (a, b), (a, c), (a, d), (b, c), (b, d), (c, d)
    #---------------
    
    df = pd.DataFrame(columns=['Name_A', 'Buffer A', 'Name_B', 'Buffer B','Intersect'])

    for subset in itertools.combinations(lista, 2):
        
        # subset è una tupla che contiene la combinazione
        # Quindi è una tupla di tuple
        # subset[0] contiene il primo elemento della combinazione, mentre
        # subset[1] contiene il secondo elemento della combinazione.
        # subset[0][0] contiene il primo elemento della tupla (quindi l'indice)
        # subset[0][1] contiene il secondo elemento della tupla (quindi il poligono)
        
        # Check intersection
        first = subset[0][1]
        second = subset[1][1]
        intersect = first.intersects(second)

        # Ottieni il nome
        name_first = subset[0][0]
        name_second = subset[1][0]

        # Add rows to dataframe
        add_row = pd.DataFrame([[name_first, first, name_second, second, intersect]],
                               columns = ['Name_A', "Buffer A", 'Name_B', "Buffer B", "Intersect"])

        df = pd.concat([df, add_row], ignore_index = True)
    
    #------------------------------------
    # Operazioni sul dataframe df
    # perché sia più utilizzabile
    #------------------------------------
    
    df = df.sort_values(by = ['Name_A', 'Name_B'], ascending = True) #Metti in ordine per nome di punto
    df = df[df['Intersect'] == True] #Intersezioni vere
    
    #------------------------------------
    # Ottieni il dataset GROUPS
    #------------------------------------
    
    # Per le intersezioni
    groups = df.groupby('Name_A')['Name_B'].apply(set).reset_index(name='Points')
    
    # Aggiungi gli elementi che non si intersecano con niente
    # Inserendo una riga che contiene l'elemento e un set vuoto
    
    s1 = set(range(0, len(lista))) #Tutti gli elementi
    s2 = set(groups['Name_A'].unique()) #Elementi in GROUPS

    for element in s1.difference(s2):
        row = pd.DataFrame([[element, set()]],
                           columns = ['Name_A', "Points"])
        groups = pd.concat([groups, row])
        
    groups = groups.sort_values('Name_A').reset_index()[['Name_A', 'Points']]
        
    return groups


#---------------------------------------------------------------------------------
# Elenco dei cluster dal dataset groups
#---------------------------------------------------------------------------------

def find_clusters(groups):

    """Elenco di clusters, a partire dal dataset groups.

    A partire da un dataset di punti "ordinati" che per ogni punto mi elenca le intersezioni con i punti successivi,
    determino i cluster di punti che si intersecano, in modo tale che i punti A e B fanno parte dello stesso cluster
    se A si interseca con B, oppure se A si interseca con C che si interseca con B, oppure se A si interseca con C
    che si interseca con D che si interseca con B, e via così (con tutti i livelli possibili).
    """
    
    clusters = [] # Conterrà i clusters
    index_p = 0 # L'indice scorre sulle righe di groups
    
    while index_p < len(groups):

        my_set = set()

        # Prendo il punto e punti che lo intersecano
        point = groups.iloc[index_p]['Name_A']
        my_set = groups.loc[index_p]['Points']

        if(len(my_set) == 0): # Il punto non si interseca con niente

            # Il cluster deve contenere solo il punto 
            my_set = my_set.union({point})
            clusters.append(my_set)

        else: # Il punto si interseca con qualcosa

            # Il cluster deve contenere tutti i punti con cui si interseca
            # e anche tutti i punti con cui si intersecano quei punti

            previous_set = 0
            while(previous_set != my_set):

                # Salvo il set precedente
                previous_set = my_set

                # Aggiorno il nuovo set:
                # Per ogni elemento, ci aggiungo tutti gli elementi che si intersecano con lui
                for elem in my_set:
                    sets = groups[groups['Name_A'] == elem].iat[0,1]
                    my_set = my_set.union(sets)

            my_set = my_set.union({point})
            clusters.append(my_set)

        index_p = max(my_set) + 1
        
    return clusters

#--------------------------------------------------
# Add labels
#--------------------------------------------------

def add_labels(df_points, clusters):

    """Aggiungi le etichette ai punti

    Dato il dataframe di punti (df_points) e la lista di cluster (clusters) ottenuta da find_clusters, la funzione
    assegna a ogni punto il cluster a cui appartiene.
    """
    
    # Dataframe 'LABELS': per ogni nome di punto, la sua label
    labels = pd.DataFrame(clusters)
    labels.insert(0, 'Label', range(0, 0 + len(labels)))
    labels = labels.melt(id_vars = ['Label'], var_name = 'set', value_name = 'Point_Name').dropna().sort_values(by='Point_Name')[['Point_Name', 'Label']]
    
    points_with_labels = df_points.merge(labels, on = 'Point_Name')
    return points_with_labels


#------------------------------------------------------
# Final objective function
#------------------------------------------------------

def ObjFunZoom(dati, d_meter = 10, return_originals = False):

    """Objective function finale.

    Dati i dati di origine e il livello di dettaglio, che corrisponde al diametro di ciascun punto (dato in metri), 
    ogni punto dei dati di origine viene 'zoomato' al livello di dettaglio indicato
    (che fa da diametro), e poi se più punti si intersecano tra loro, sono considerati come 'da raggruppare' in un
    unico punto. Questa funzione genera i 'nuovi punti' che derivano da questa operazione (che sono i punti più
    vicini ai centroidi dei cluster risultanti). il loro numero mi indica quanti punti 'dovrebbero esserci' 
    se avessi ingrandito a quel livello di dettaglio. 
    NOTA: qui il parametro d (diametro del punto) è considerato in METRI.
    """

    # Conversione da metri a gradi
    radius = 6371000
    d = 360*d_meter/(2*math.pi*radius)

    # Genero i punti con i buffer
    df_points, lista = points_with_buffer(dati, d)

    # Genero le intersezioni di ciascun punto con i successivi
    groups = dataset_groups(lista)

    # Cluster dalle intersezioni
    clusters = find_clusters(groups)

    # Etichette ai punti
    points_with_labels = add_labels(df_points, clusters)

    # Centroidi dei cluster e merge con i punti originali
    new_points = points_with_labels.groupby('Label').mean().reset_index()[['Label', 'Latitude', 'Longitude']]
    new_points = new_points.rename({'Latitude': 'Latitude_mean', 'Longitude': 'Longitude_mean'}, axis = 1)
    points_with_labels = points_with_labels.merge(new_points, on = 'Label')

    # Distanza di ogni punto dal centroide del suo cluster
    points_with_labels['Distance'] = points_with_labels.apply(
        lambda x: math.sqrt(pow((x['Latitude'] - x['Latitude_mean']),2) + pow((x['Longitude'] - x['Longitude_mean']),2)),
    axis = 1)

    # Punti più vicini al centroide del cluster e merge con i punti originali
    nearest = points_with_labels.loc[points_with_labels.groupby('Label')['Distance'].idxmin()]
    nearest['Flag_nearest'] = True
    nearest = nearest[['Point_Name', 'Flag_nearest']]
    points_with_labels = points_with_labels.merge(nearest, on='Point_Name', how = 'left').fillna(value = False)

    # Selezione dei punti più vicini al cluster
    new_points = points_with_labels[points_with_labels['Flag_nearest'] == True].reset_index(drop = True)

    if return_originals:
        return points_with_labels

    else: 
        return new_points[['Latitude', 'Longitude', 'Point_Name']]



#-------------------------------------
# Plot del buffer per ciascun punto
#-------------------------------------

# def plot_zoom(dati, d_meter = 10, s=1):

#     """Plot dei punti 'zoomati': prequel della funzione.
    
#     A partire da un dataframe "preparato" (condizioni al contorno resettate) in cui una colonna si chiama 'Latitude'
#     e una colonna si chiama 'Longitude', genera e plotta i punti "zoomati", così che ogni punto abbia in realtà un
#     diametro pari a d (in metri). Questa funzione è una sorta di 'prequel' allo zoom vero e proprio, 
#     e mi fa vedere quanto considererei grandi i punti, e quindi quali si intersecheranno e diventeranno un singolo punto.
#     Parametri di input: dati, diametro del punto (in metri), 
#     s (parametro che ingrandisce la tela in cui il grafico viene stampato)
#     """

#     radius = 6371000
#     d = 360*d_meter/(2*math.pi*radius)
    
#     points = []
    
#     for index, row in dati.iterrows():
#         point = Point(row['Latitude'], row['Longitude'])
#         point = point.buffer(d/2)
#         points.append(point)

#     fig, axes = plt.subplots(figsize = (6*s, 4*s))
#     for elem in points:
#         x,y = elem.exterior.xy
#         plt.plot(x,y)
#     plt.show()