import pandas as pd
import numpy as np
import os
import warnings

# Ignorar los warnings
warnings.filterwarnings("ignore")


# Leer el archivo de 'Exportaciones'
Exportaciones = pd.read_excel("Exportaciones.xlsx")

# Crear columna de 'Precio' a partir de 'U$S FOB' y 'Kgs. Netos'
Exportaciones["Precio"] = Exportaciones["U$S FOB"] / Exportaciones["Kgs. Netos"]

# Filtrar los que no tengan 'Precio' y no sea = 0
Exportaciones = Exportaciones[Exportaciones["Precio"].notna()]
Exportaciones = Exportaciones[Exportaciones["Precio"] != 0]


# Crear una nueva tabla con los datos estadísticos de cada 'Precio'  para cada 'NCM-SIM'
Exp_SIM = Exportaciones.groupby("NCM-SIM")["Precio"].describe()

# Crear una nueva tabla con los datos estadísticos de cada 'Precio'  para cada 'Descripcion Arancelaria'
Exp_DescripcionArancelaria = Exportaciones.groupby("Descripcion Arancelaria")["Precio"].describe()

#Redondear los datos de las tablas 'Exp_SIM' , 'Exp_DescripcionArancelaria' y 'Exportaciones' a 6 decimales con la libreria 'decimal'
Exp_SIM = Exp_SIM.round(decimals=6)
Exp_DescripcionArancelaria = Exp_DescripcionArancelaria.round(decimals=6)
Exportaciones = Exportaciones.round(decimals=6)

# Merge las 'Exportaciones' con los datos del primer cuartil y la mediana de cada 'NCM-SIM'
Exportaciones = pd.merge(
    Exportaciones, 
    Exp_SIM["25%"], 
    on="NCM-SIM", 
    how="left")

Exportaciones = pd.merge(
    Exportaciones, 
    Exp_SIM["50%"], 
    on="NCM-SIM", 
    how="left")

# Merge las 'Exportaciones' con los datos del primer cuartil y la mediana de cada 'Descripcion Arancelaria'
Exportaciones = pd.merge(
    Exportaciones,
    Exp_DescripcionArancelaria["25%"],
    on="Descripcion Arancelaria",
    how="left")

Exportaciones = pd.merge(
    Exportaciones,
    Exp_DescripcionArancelaria["50%"],
    on="Descripcion Arancelaria",
    how="left")

# Crear una columna que se llame 'Ajuste NCM-SIM' y que sea igual a la multiplicacion de los 'Kgs. Netos' por el '50%' de cada 'NCM-SIM' si el 'Precio' es menor al '25%' de cada 'NCM-SIM'
Exportaciones["Ajuste NCM-SIM"] = np.nan

Exportaciones.loc[
    Exportaciones["Precio"] < Exportaciones["25%_x"], 
    "Ajuste NCM-SIM"] = (Exportaciones["Kgs. Netos"] * Exportaciones["50%_x"])

# Crear una columna que se llame 'Ajuste Descripcion Arancelaria' y que sea igual a la multiplicacion de los 'Kgs. Netos' por el '50%' de cada 'Descripcion Arancelaria' si el 'Precio' es menor al '25%' de cada 'Descripcion Arancelaria'
Exportaciones["Ajuste Descripcion Arancelaria"] = np.nan

Exportaciones.loc[
    Exportaciones["Precio"] < Exportaciones["25%_y"], 
    "Ajuste Descripcion Arancelaria"] = (Exportaciones["Kgs. Netos"] * Exportaciones["50%_y"])

Exportaciones = Exportaciones.round(decimals=6)

#Crear carpeta Generado si no existe
if not os.path.exists("Generado"):
    os.makedirs("Generado")

# Exportar las 'Exportaciones', 'Exp_SIM', 'Exp_DescripcionArancelaria' a CSV con el nombre de 'Exportaciones Procesadas', 'Exp SIM', 'Exp DescripcionArancelaria' con el separador ';' , sin el index , con el encoding 'latin-1' , con separador de miles '.' y con separador de decimales ','
Exportaciones.to_csv(
    "Generado/Exportaciones Procesadas.csv", 
    sep=";", 
    index=False, 
    encoding="latin-1", 
    decimal=",", 
    thousands=".")

Exp_SIM.to_csv(
    "Generado/Exp SIM.csv",
    sep=";",
    index=False,
    encoding="latin-1",
    decimal=",",
    thousands=".")

Exp_DescripcionArancelaria.to_csv(
    "Generado/Exp DescripcionArancelaria.csv",
    sep=";",
    index=False,
    encoding="latin-1",
    decimal=",",
    thousands=".")