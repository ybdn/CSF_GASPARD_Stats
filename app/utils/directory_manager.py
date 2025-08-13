#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import json
import re
from utils.file_handlers import import_csv
# from core.data_model import DirectoryEntry # Suppression de l'import
from typing import Optional, List

class DirectoryManager:
    """Gestionnaire de l'annuaire de l'application."""
    
    def __init__(self, directory_path=None):
        """Initialise le gestionnaire d'annuaire.
        
        Args:
            directory_path (str, optional): Chemin vers le fichier d'annuaire
        """
        self.directory_path = directory_path or os.path.join('app', 'resources', 'directory', 'directory.csv')
        self.directory_data = None
        self._load_directory()
    
    def _load_directory(self):
        """Charge l'annuaire depuis le fichier."""
        # Vider les données existantes au début
        self.directory_data = None 
        
        if not os.path.exists(self.directory_path):
            print(f"Fichier annuaire non trouvé: {self.directory_path}. L'annuaire sera vide jusqu'à la fusion.")
            # Initialiser avec une structure minimale (juste la clé)
            self.directory_data = pd.DataFrame(columns=['key'])
            return # Pas besoin d'essayer de lire ou créer un fichier défaut ici
        
        try:
            # Déterminer le format du fichier
            _, ext = os.path.splitext(self.directory_path)
            ext = ext.lower()
            
            if ext == '.csv':
                self.directory_data = pd.read_csv(self.directory_path)
            elif ext == '.json':
                with open(self.directory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Conversion en DataFrame
                    if isinstance(data, list):
                        self.directory_data = pd.DataFrame(data)
            else:
                print(f"Format d'annuaire non supporté: {ext}. L'annuaire sera considéré comme vide.")
                self.directory_data = pd.DataFrame(columns=['key']) # Structure minimale
                
        except Exception as e:
            print(f"Erreur lors du chargement de l'annuaire: {str(e)}. L'annuaire sera considéré comme vide.")
            # En cas d'erreur, initialiser avec une structure minimale
            self.directory_data = pd.DataFrame(columns=['key'])
    
    def _create_default_directory(self):
        """Crée un annuaire par défaut."""
        # Créer un DataFrame vide avec la structure attendue
        self.directory_data = pd.DataFrame({
            'key': [],
            'value': [],
            'category': []
        })
        
        # Sauvegarder l'annuaire par défaut
        self._save_directory()
    
    def _save_directory(self):
        """Sauvegarde l'annuaire dans le fichier."""
        try:
            # Créer le répertoire parent si nécessaire
            os.makedirs(os.path.dirname(self.directory_path), exist_ok=True)
            
            # Sauvegarder selon le format
            _, ext = os.path.splitext(self.directory_path)
            ext = ext.lower()
            
            if ext == '.csv':
                self.directory_data.to_csv(self.directory_path, index=False)
            elif ext == '.json':
                with open(self.directory_path, 'w', encoding='utf-8') as f:
                    json.dump(self.directory_data.to_dict(orient='records'), f, indent=4)
            else:
                # Par défaut, sauvegarder en CSV
                csv_path = os.path.splitext(self.directory_path)[0] + '.csv'
                self.directory_data.to_csv(csv_path, index=False)
                self.directory_path = csv_path
                
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'annuaire: {str(e)}")
    
    def get_directory(self):
        """Retourne les données de l'annuaire.
        
        Returns:
            pandas.DataFrame: Données de l'annuaire
        """
        return self.directory_data
    
    def _format_gn_value(self, value):
        """Formate une valeur au format GN + 8 chiffres.
        
        Args:
            value: La valeur à formater
            
        Returns:
            str: La valeur formatée (GN + 8 chiffres)
        """
        # Gérer les None ou valeurs vides
        if value is None or str(value).strip() == "":
            return "GN00000000" # Retourner une valeur par défaut ou selon besoin
            
        str_value = str(value)
        
        # Si déjà au bon format, retourner directement
        if re.match(r'^GN\d{8}$', str_value):
            return str_value

        # Tentative de nettoyage pour les cas comme "123.0"
        cleaned_value = str_value
        try:
            # Si c'est un nombre avec potentiellement .0
            if '.' in cleaned_value:
                num_float = float(cleaned_value)
                # Si c'est effectivement un entier (ex: 123.0)
                if num_float == int(num_float):
                    cleaned_value = str(int(num_float))
        except (ValueError, TypeError):
            # Ignorer les erreurs de conversion, on utilisera re.sub sur la valeur originale
            pass 
            
        # Extraire uniquement les chiffres de la valeur (potentiellement nettoyée)
        digits = re.sub(r'\D', '', cleaned_value) # Utiliser cleaned_value
        
        # Si aucun chiffre n'est trouvé après nettoyage
        if not digits:
            return "GN00000000"
            
        # Si la valeur commence par "GN", s'assurer qu'on a les chiffres
        # (Redondant avec le re.sub mais ne coûte rien)
        # if str_value.startswith('GN'):
        #     digits = re.sub(r'\D', '', str_value)
        
        # Limiter aux 8 derniers chiffres si plus long
        if len(digits) > 8:
            digits = digits[-8:]
            
        # Compléter avec des zéros devant pour faire 8 chiffres
        digits = digits.zfill(8)
            
        # Retourner la valeur formatée
        return f"GN{digits}"
    
    def _combine_duplicate_rows(self, df, key_column='key'):
        """Combine les lignes qui ont la même valeur de clé en une seule ligne.
        
        Args:
            df (pandas.DataFrame): DataFrame à traiter
            key_column (str): Nom de la colonne clé
            
        Returns:
            pandas.DataFrame: DataFrame sans doublons
        """
        if df.empty or key_column not in df.columns:
            return df
            
        # Vérifier s'il y a des doublons
        if not df.duplicated(subset=[key_column], keep=False).any():
            return df
            
        # Créer un DataFrame pour stocker les résultats
        result_df = pd.DataFrame(columns=df.columns)
        
        # Parcourir les valeurs uniques de la clé
        for key_value in df[key_column].unique():
            # Obtenir toutes les lignes pour cette clé
            rows = df[df[key_column] == key_value]
            
            if len(rows) == 1:
                # Si une seule ligne, l'ajouter directement
                result_df = pd.concat([result_df, rows])
            else:
                # Fusionner les lignes
                combined_row = {}
                combined_row[key_column] = key_value
                
                # Pour chaque colonne (sauf la clé)
                for col in df.columns:
                    if col != key_column:
                        # Prendre la première valeur non NaN
                        non_nan_values = rows[col].dropna()
                        if len(non_nan_values) > 0:
                            combined_row[col] = non_nan_values.iloc[0]
                        else:
                            combined_row[col] = None
                
                # Ajouter la ligne combinée au résultat
                result_df = pd.concat([result_df, pd.DataFrame([combined_row])], ignore_index=True)
        
        return result_df
    
    def merge_directories(self, file_path1, file_path2, key_column1=None, key_column2=None, how='outer', 
                          columns_to_delete1: Optional[List[str]] = None,
                          columns_to_delete2: Optional[List[str]] = None):
        """Fusionne deux fichiers CSV pour créer un annuaire.
        
        Args:
            file_path1 (str): Chemin vers le premier fichier CSV
            file_path2 (str): Chemin vers le deuxième fichier CSV
            key_column1 (str, optional): Colonne à utiliser comme clé dans le premier fichier
            key_column2 (str, optional): Colonne à utiliser comme clé dans le deuxième fichier
            how (str, optional): Type de fusion ('inner', 'outer', 'left', 'right')
            columns_to_delete1 (list[str], optional): Liste des colonnes à supprimer du premier fichier avant fusion.
            columns_to_delete2 (list[str], optional): Liste des colonnes à supprimer du deuxième fichier avant fusion.
            
        Returns:
            bool: True si la fusion a réussi, False sinon
        """
        try:
            # Importer les deux fichiers CSV
            df1 = import_csv(file_path1)
            df2 = import_csv(file_path2)
            
            # Si les colonnes clés ne sont pas spécifiées, utiliser la première colonne
            if key_column1 is None and len(df1.columns) > 0:
                key_column1 = df1.columns[0]
            if key_column2 is None and len(df2.columns) > 0:
                key_column2 = df2.columns[0]
            
            # Vérifier la présence des colonnes clés
            if key_column1 not in df1.columns:
                 raise ValueError(f"La colonne clé '{key_column1}' n'existe pas dans le fichier {file_path1}")
            if key_column2 not in df2.columns:
                raise ValueError(f"La colonne clé '{key_column2}' n'existe pas dans le fichier {file_path2}")
            
            # --- Suppression des colonnes sélectionnées par l'utilisateur (AVANT fusion) ---
            if columns_to_delete1:
                # S'assurer de ne pas supprimer la colonne clé
                cols1_safe_to_delete = [col for col in columns_to_delete1 if col in df1.columns and col != key_column1]
                if cols1_safe_to_delete:
                    df1.drop(columns=cols1_safe_to_delete, inplace=True, errors='ignore')
            
            if columns_to_delete2:
                # S'assurer de ne pas supprimer la colonne clé
                cols2_safe_to_delete = [col for col in columns_to_delete2 if col in df2.columns and col != key_column2]
                if cols2_safe_to_delete:
                    df2.drop(columns=cols2_safe_to_delete, inplace=True, errors='ignore')
            
            # --- Formatage obligatoire des valeurs des colonnes clés ---
            # Copier pour éviter SettingWithCopyWarning
            df1 = df1.copy()
            df2 = df2.copy()
            df1[key_column1] = df1[key_column1].apply(self._format_gn_value)
            df2[key_column2] = df2[key_column2].apply(self._format_gn_value)
            
            # --- Fusionner les deux DataFrames ---
            # Utilisation de 'outer' pour conserver toutes les lignes
            # Les clés formatées sont utilisées pour la jointure
            merged_df = pd.merge(
                df1, 
                df2, 
                left_on=key_column1, 
                right_on=key_column2, 
                how=how, # 'outer' est souvent un bon choix par défaut
                suffixes=('_1', '_2') # Suffixes pour colonnes non-clés en double
            )
            
            # --- Gestion de la colonne clé après fusion ---
            # Si les clés étaient différentes, la clé du df1 (key_column1) est conservée.
            # La clé du df2 (key_column2 + suffixe '_2') est supprimée si elle existe.
            if key_column1 != key_column2 and f"{key_column2}_2" in merged_df.columns:
                merged_df.drop(columns=[f"{key_column2}_2"], inplace=True)
            
            # Renommer la colonne clé principale en 'key' pour l'annuaire interne
            # Utiliser key_column1 comme référence car c'est celle conservée
            merged_df.rename(columns={key_column1: 'key'}, inplace=True)
            
            # --- Combiner les lignes qui ont la même clé après la fusion ---
            # Gère les cas où une clé existait dans les deux fichiers ou était dupliquée
            merged_df = self._combine_duplicate_rows(merged_df, 'key')
            
            # Mettre à jour l'annuaire de l'application
            self.directory_data = merged_df
            self._save_directory()
            
            return True
        except Exception as e:
            print(f"Erreur lors de la fusion des annuaires: {str(e)}")
            return False
    
    # --- Méthodes suivantes supprimées car non utilisées --- 
    # def add_entry(self, key, values):
    #     ...
    # 
    # def update_entry(self, key, values):
    #     ...
    # 
    # def delete_entry(self, key):
    #     ...
    # 
    # def search_directory(self, search_term, column='key'):
    #     ... 