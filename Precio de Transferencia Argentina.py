import pandas as pd
import numpy as np
import os
import warnings

# Ignorar los warnings
warnings.filterwarnings("ignore")


# Crear un DataFrame vacío
Exportaciones = pd.DataFrame()

# Cargar en una lista los nombres de los archivos dentro de la carpeta 'Exportaciones'
archivos = os.listdir("Exportaciones")

# Agregar 'Exportaciones/' a la lista de archivos para que el path sea correcto
archivos = ["Exportaciones/" + archivo for archivo in archivos]

#Crear carpeta Generado si no existe
if not os.path.exists("Generado"):
    os.makedirs("Generado")

# Cargar los archivos en el DataFrame
for archivo in archivos:
    df = pd.read_excel(archivo, sheet_name="Detalle", engine="openpyxl")
    # Eliminar las columnas 'Estado' , 'Tipo de Dato' , 'Fecha Cargado' , 'Destinación' , 'Flete U$S' , 'Seguro' , 'Marca - Sufijos' , 'Cantidad' , 'Unitario Divisa' , 'FOB Divisa' , 'Moneda Divisa' , 'Condición de Venta' , 'Marca o Descripcion'
    df = df.drop(
        [   "Estado",
            "Tipo de Dato",
            "Fecha Cargado",
            "Destinación",
            "Flete U$S",
            "Seguro",
            "Marca - Sufijos",
            "Cantidad",
            "Unitario Divisa",
            "FOB Divisa",
            "Moneda Divisa",
            "Condición de Venta",
            "Marca o Descripcion"],
        axis=1)
    Exportaciones = pd.concat([Exportaciones, df])

Exportaciones.to_excel("Generado/Exportaciones.xlsx", index=False)

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

# Cambiar los sufijos '_x' y '_y' de las columnas '25%' y '50%' por '_NCM-SIM' y '_Descripcion Arancelaria'
Exportaciones = Exportaciones.rename(
    columns={
        "25%_x": "25%_NCM-SIM",
        "50%_x": "50%_NCM-SIM",
        "25%_y": "25%_Descripcion Arancelaria",
        "50%_y": "50%_Descripcion Arancelaria"})

Exportaciones = Exportaciones.round(decimals=6)

# Exportar las 'Exportaciones', 'Exp_SIM', 'Exp_DescripcionArancelaria' a Excel
Exp_SIM.to_excel(
    "Generado/Exp_SIM.xlsx",
    sheet_name="Exp_SIM",
    index=False)

Exp_DescripcionArancelaria.to_excel(
    "Generado/Exp_DescripcionArancelaria.xlsx",
    sheet_name="Exp_DescripcionArancelaria",
    index=False)

Exportaciones.to_excel(
    "Generado/Exportaciones Procesadas.xlsx",
    sheet_name="Exportaciones",
    index=False)
