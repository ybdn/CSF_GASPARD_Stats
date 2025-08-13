#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import csv

def import_data(file_path):
    """Importe des données depuis un fichier.
    
    Args:
        file_path (str): Chemin vers le fichier à importer
        
    Returns:
        pandas.DataFrame: Les données importées
        
    Raises:
        ValueError: Si le fichier ne peut pas être importé
    """
    if not os.path.exists(file_path):
        raise ValueError(f"Le fichier {file_path} n'existe pas")
    
    # Déterminer le type de fichier par son extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    try:
        # Importer selon le type de fichier
        if ext in ['.xlsx', '.xls']:
            return _import_excel(file_path)
        elif ext == '.csv':
            return import_csv(file_path)
        else:
            raise ValueError(f"Format de fichier non supporté: {ext}")
    except Exception as e:
        raise ValueError(f"Erreur lors de l'importation: {str(e)}")

def _import_excel(file_path):
    """Importe un fichier Excel.
    
    Args:
        file_path (str): Chemin vers le fichier Excel
        
    Returns:
        pandas.DataFrame: Les données du fichier Excel
    """
    try:
        # Lecture avec pandas
        return pd.read_excel(file_path)
    except Exception as e:
        raise ValueError(f"Erreur lors de l'importation Excel: {str(e)}")

def import_csv(file_path):
    """Importe un fichier CSV.
    
    Args:
        file_path (str): Chemin vers le fichier CSV
        
    Returns:
        pandas.DataFrame: Les données du fichier CSV
    """
    try:
        # Détection automatique du délimiteur
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            dialect = csv.Sniffer().sniff(f.read(4096))
            f.seek(0)
        
        # Lecture avec pandas en utilisant le délimiteur détecté
        return pd.read_csv(file_path, sep=dialect.delimiter)
    except Exception as e:
        # Fallback sur la lecture standard
        try:
            return pd.read_csv(file_path)
        except:
            raise ValueError(f"Erreur lors de l'importation CSV: {str(e)}")

def export_data(data, file_path, format_type='csv'):
    """Exporte des données vers un fichier.
    
    Args:
        data (pandas.DataFrame): Les données à exporter
        file_path (str): Chemin du fichier de destination
        format_type (str, optional): Format d'export ('csv' ou 'excel')
        
    Returns:
        bool: True si l'export a réussi, False sinon
    """
    try:
        # Créer le répertoire parent si nécessaire
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Exporter selon le format
        if format_type.lower() == 'excel':
            data.to_excel(file_path, index=False)
        else:
            # Standardiser l'export CSV avec point-virgule et encodage utf-8-sig
            data.to_csv(file_path, index=False, sep=';', encoding='utf-8-sig')
        
        return True
    except Exception as e:
        print(f"Erreur lors de l'export: {str(e)}")
        return False 