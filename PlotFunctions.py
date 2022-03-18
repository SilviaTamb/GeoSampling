# **********************************************************************************************
# Questo file contiene le funzioni di plotting
# plot_polygon, per plottare il poligono
# ***********************************************************************************************

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from shapely.geometry import Point
import math
from numpy.linalg import norm
import seaborn as sns

from GeoSampling import DBSCANsampling as DBsamp

#---------------------------------------
# Funzione per plottare i poligoni dati
#---------------------------------------

def plot_polygon(dati, titolo = 'Poligono', s = 1):

    """Plot a polygon from coordinates.

    A partire da un dataframe di Pandas per cui c'è una colonna che si chiama 'Latitude' e una che si chiama 'Longitude', 
    questa funzione plotta il poligono risultante su un grafico di Matplotlib, usando la funzione Polygon e disegnando anche
    i singoli punti. Il primo argomento sono i dati nel formato sopra, il secondo argomento è il titolo del grafico, che
    deve essere una stringa.
    """
    
    if (not isinstance(titolo, str)):
        raise Exception("L'argomento 'Titolo' deve essere una stringa")
    
    # List of points from data structure
    points = list((zip(list(dati['Latitude']), list(dati['Longitude']))))
    
    fig, ax = plt.subplots(figsize = (6*s, 4*s))

    # Plot polygon
    poly = Polygon(points, ec="k")
    ax.add_patch(poly)

    # Plot points
    ax.scatter(dati.Latitude, dati.Longitude, color="k", alpha=0.5, zorder=1)

    # Plot original labels
    indexes = list(dati.index) #Indici originali
    dati = dati.reset_index() #Per poter fare dati.Latitude[i] senza che dia errore
    
    for i, txt in enumerate(indexes):
        ax.annotate(txt, (dati.Latitude[i], dati.Longitude[i]))

    # Visualization options
    ax.set_title(titolo)
    ax.margins(0.1)
    ax.relim()
    ax.autoscale_view()

#-------------------------------------
# Plot del buffer per ciascun punto
#-------------------------------------

def plot_zoom(dati, d_meter = 10, s=1):

    """Plot dei punti 'zoomati': prequel della funzione.
    
    A partire da un dataframe "preparato" (condizioni al contorno resettate) in cui una colonna si chiama 'Latitude'
    e una colonna si chiama 'Longitude', genera e plotta i punti "zoomati", così che ogni punto abbia in realtà un
    diametro pari a d (in metri). Questa funzione è una sorta di 'prequel' allo zoom vero e proprio, 
    e mi fa vedere quanto considererei grandi i punti, e quindi quali si intersecheranno e diventeranno un singolo punto.
    Parametri di input: dati, diametro del punto (in metri), 
    s (parametro che ingrandisce la tela in cui il grafico viene stampato)
    """

    radius = 6371000
    d = 360*d_meter/(2*math.pi*radius)
    
    points = []
    
    for index, row in dati.iterrows():
        point = Point(row['Latitude'], row['Longitude'])
        point = point.buffer(d/2)
        points.append(point)

    fig, axes = plt.subplots(figsize = (6*s, 4*s))
    for elem in points:
        x,y = elem.exterior.xy
        plt.plot(x,y)
    plt.show()


#------------------------------------------
# Plot istogramma lunghezze segmenti
#-------------------------------------------

def plot_length(dati):

    """Plot dell'istogramma con le lunghezze dei segmenti che compongono il poligono
    
    Questo plot produce l'istogramma con le lunghezze dei segmenti che compongono il poligono. 
    L'istogramma viene prodotto grazie a Seaborn.
    """

    distances = []

    for i in range(0, len(dati)-2):
        A = dati.iloc[i].to_numpy()
        B = dati.iloc[i+1].to_numpy()
        distance = norm(A-B)
        radius = 6371000
        distance_meter = 2*math.pi*radius*distance/360 #Distanze in metri
        distances.append(distance_meter)

    sns.displot(distances)


#------------------------------------------------
# Funzione per plottare i risultati del DBSCAN
#------------------------------------------------

def plot_DBSCAN(orig_dati, eps_meter = 10, titolo = 'DBSCAN model', s=1):

    """Plot dei risultati del DBSCAN

    A partire dai dati, plot di come i punti vengono clusterizzati dal DBSCAN, dato l'eps indicato.
    """
    
    # Risultati del DBSCAN calcolati
    dati = DBsamp.DBSCANmodel(orig_dati, eps_meter)

    # Lista di punti
    points = list((zip(list(dati['Latitude']), list(dati['Longitude']))))
    
    fig, ax = plt.subplots(figsize = (6*s, 4*s))

    # Plot polygon
    poly = Polygon(points, ec="k")
    ax.add_patch(poly)

    # Plot points
    ax.scatter(dati.Latitude, dati.Longitude, s = 200, c=dati.Labels, alpha=0.5, zorder=1)

    # Plot original labels
    indexes = list(dati.index) #Indici originali
    dati = dati.reset_index() #Per poter fare dati.Latitude[i] senza che dia errore
    
    for i, txt in enumerate(indexes):
        ax.annotate(txt, (dati.Latitude[i], dati.Longitude[i]))

    # Visualization options
    ax.set_title(titolo)
    ax.margins(0.1)
    ax.relim()
    ax.autoscale_view()