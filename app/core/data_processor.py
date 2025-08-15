#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from utils.directory_manager import DirectoryManager
from typing import Optional, List

class DataProcessor:
    """Classe responsable du traitement des données et des statistiques."""
    
    def __init__(self, directory_manager: DirectoryManager):
        """Initialise le processeur de données.
        
        Args:
            directory_manager (DirectoryManager): L'instance partagée du gestionnaire d'annuaire.
        """
        self.data = None
        self.processed_data = None
        self.stats = None
        self.directory_manager = directory_manager
        self.processing_params = {} # Ajouter pour stocker les paramètres de traitement
    
    def set_data(self, data):
        """Définit les données à traiter.
        
        Args:
            data (pandas.DataFrame): Les données à traiter
        """
        self.data = data
        self.processed_data = None
        self.stats = None
        # Réinitialiser aussi les paramètres
        self.processing_params = {}
    
    def has_data(self):
        """Vérifie si des données sont disponibles.
        
        Returns:
            bool: True si des données sont disponibles, False sinon
        """
        return self.data is not None and not self.data.empty
    
    def get_data(self):
        """Retourne les données actuelles.
        
        Returns:
            pandas.DataFrame: Les données actuelles
        """
        return self.data if self.has_data() else pd.DataFrame()
    
    def process_with_directory(self, directory_column: str, 
                               type_column: Optional[str] = None, 
                               columns_to_delete: Optional[List[str]] = None):
        """Traite les données en utilisant l'annuaire, avec fusion conditionnelle basée sur le type.

        Args:
            directory_column (str): Nom de la colonne contenant la clé pour la fusion.
            type_column (str, optional): Nom de la colonne contenant le type de signalisation (ex: 'SM').
            columns_to_delete (list[str], optional): Colonnes à supprimer des données AVANT fusion.
        """
        if not self.has_data() or directory_column not in self.data.columns:
            print("Erreur: Données manquantes ou colonne clé invalide.")
            return False
        
        # Vérifier si la colonne type existe si elle est fournie
        if type_column and type_column not in self.data.columns:
            print(f"Erreur: La colonne type '{type_column}' n'existe pas dans les données importées.")
            return False

        # Faire une copie des données originales pour le traitement
        data_to_process = self.data.copy()

        # --- Suppression des colonnes (AVANT formatage et fusion) ---
        if columns_to_delete:
            cols_safe_to_delete = [
                col for col in columns_to_delete 
                if col in data_to_process.columns and col != directory_column and col != type_column
            ]
            if cols_safe_to_delete:
                print(f"Suppression des colonnes : {cols_safe_to_delete}")
                data_to_process.drop(columns=cols_safe_to_delete, inplace=True, errors='ignore')

        # --- Récupération et préparation de l'annuaire ---
        directory_data = self.directory_manager.get_directory()
        if directory_data is None or directory_data.empty or 'key' not in directory_data.columns:
            print("Erreur: Annuaire vide ou invalide (colonne 'key' manquante). Traitement annulé.")
            # Ne pas continuer le traitement si l'annuaire est inutilisable
            self.processed_data = None # Assurer que les données traitées sont vides
            self.stats = {'global_error': "Annuaire vide ou invalide", 'sm_error': "Annuaire vide ou invalide"} # Optionnel: définir erreurs
            return False # Indiquer l'échec du traitement

        # --- Formatage de la colonne clé dans les données à traiter ---
        print(f"Formatage de la colonne clé: {directory_column}")
        try:
             # Assurer que la colonne clé est de type string avant le formatage
            data_to_process[directory_column] = data_to_process[directory_column].astype(str)
            data_to_process[directory_column] = data_to_process[directory_column].apply(
                self.directory_manager._format_gn_value
            )
        except Exception as e:
            print(f"Erreur lors du formatage de la colonne clé '{directory_column}': {e}")
            return False

        # --- Logique de fusion conditionnelle ---
        if type_column and type_column in data_to_process.columns:
            print(f"Application de la fusion conditionnelle basée sur la colonne '{type_column}'.")
            
            # Séparer les données en fonction du type 'SM'
            # Assurer que la colonne type est de type string pour la comparaison
            data_to_process[type_column] = data_to_process[type_column].astype(str)
            df_sm = data_to_process[data_to_process[type_column].str.upper() == 'SM'].copy()
            df_other = data_to_process[data_to_process[type_column].str.upper() != 'SM'].copy()
            print(f"Lignes type SM: {len(df_sm)}, Lignes autres types: {len(df_other)}")

            # Préparer l'annuaire pour la fusion partielle (SM)
            directory_cols_for_sm = ['key', 'abrege_unite', 'departement']
            # S'assurer que ces colonnes existent dans l'annuaire
            valid_dir_cols_sm = [col for col in directory_cols_for_sm if col in directory_data.columns]
            directory_sm_subset = directory_data[valid_dir_cols_sm].copy()
            print(f"Colonnes de l'annuaire pour SM : {valid_dir_cols_sm}")

            # Fusion pour les lignes SM (partielle)
            merged_sm = pd.DataFrame() # Initialiser au cas où df_sm est vide
            if not df_sm.empty:
                merged_sm = pd.merge(
                    df_sm,
                    directory_sm_subset,
                    left_on=directory_column,
                    right_on='key',
                    how='left',
                    suffixes=('', '_annuaire')
                )
                print("Fusion partielle pour SM terminée.")

            # Fusion pour les autres lignes (complète)
            merged_other = pd.DataFrame() # Initialiser au cas où df_other est vide
            if not df_other.empty:
                merged_other = pd.merge(
                    df_other,
                    directory_data, # Utiliser l'annuaire complet
                    left_on=directory_column,
                    right_on='key',
                    how='left',
                    suffixes=('', '_annuaire')
                )
                print("Fusion complète pour les autres types terminée.")

            # Combiner les résultats
            self.processed_data = pd.concat([merged_sm, merged_other], ignore_index=True)
            print("Concaténation des résultats SM et autres terminée.")

        else:
            # --- Fusion simple (si pas de colonne type ou invalide) ---
            print("Application de la fusion simple (pas de condition sur le type).")
            self.processed_data = pd.merge(
                data_to_process,
                directory_data,
                left_on=directory_column,
                right_on='key',
                how='left',
                suffixes=('', '_annuaire')
            )
            print("Fusion simple terminée.")

        # --- Nettoyage final des colonnes ---
        # Supprimer la colonne 'key' de l'annuaire si redondante
        if 'key' in self.processed_data.columns and directory_column != 'key':
            print("Suppression de la colonne 'key' redondante.")
            self.processed_data.drop(columns=['key'], inplace=True, errors='ignore')
        
        # Supprimer les colonnes suffixées '_annuaire' si la colonne originale existe
        # (Peut arriver si une colonne existe dans les deux DFs et n'est pas la clé)
        cols_to_drop = [col for col in self.processed_data.columns if col.endswith('_annuaire')]
        if cols_to_drop:
            print(f"Suppression des colonnes suffixées _annuaire: {cols_to_drop}")
            self.processed_data.drop(columns=cols_to_drop, inplace=True, errors='ignore')
            
        print("Traitement terminé avec succès.")
        # Stocker les paramètres utilisés pour le traitement
        self.processing_params = {
            'directory_column': directory_column,
            'type_column': type_column,
            'columns_to_delete': columns_to_delete
        }
        # Générer les statistiques après le traitement
        # Appeler les deux fonctions de génération
        self._generate_global_stats()
        self._generate_sm_stats()
        return True
    
    def _generate_global_stats(self):
        """Génère des statistiques agrégées sur TOUTES les données traitées."""
        if self.processed_data is None or self.processed_data.empty:
            if not isinstance(self.stats, dict):
                self.stats = {}
            self.stats['global_summary_table'] = pd.DataFrame()  # Table vide
            print("Aucune donnée traitée disponible pour générer les statistiques globales.")
            return

        # Colonnes attendues
        dept_col = 'departement'
        unit_col = 'abrege_unite'
        material_col = 'type_materiel'
        terminal_col = 'code_unite_terminal_de_saisie'
        # Résoudre la colonne idpp de manière insensible à la casse
        idpp_col = next((c for c in self.processed_data.columns if c.lower() == 'idpp'), None)

        grouping_cols = [dept_col, unit_col, material_col, terminal_col]
        required_cols = grouping_cols + ([idpp_col] if idpp_col else [])

        missing_cols = [col for col in required_cols if col not in self.processed_data.columns]
        if not idpp_col:
            missing_cols.append('idpp')
        if missing_cols:
            err_msg = f"Colonnes manquantes pour stats globales: {', '.join(missing_cols)}"
            print(f"Attention: {err_msg}")
            if not isinstance(self.stats, dict):
                self.stats = {}
            self.stats['global_error'] = err_msg
            self.stats['global_summary_table'] = pd.DataFrame()
            return

        # Calcul des statistiques globales
        print(f"Génération des statistiques globales par groupe: {grouping_cols}")
        stats_df = self.processed_data.copy()

        # Identification GASPARD (présence d'idpp non vide)
        is_gaspard_col = 'is_gaspard'
        stats_df[is_gaspard_col] = stats_df[idpp_col].notna() & (stats_df[idpp_col].astype(str).str.strip() != '')
        stats_df[is_gaspard_col] = stats_df[is_gaspard_col].astype(int)

        aggregated_stats = stats_df.groupby(grouping_cols).agg(
            nombre_signalisation=(grouping_cols[0], 'size'),
            nombre_signalisation_gaspard=(is_gaspard_col, 'sum')
        ).reset_index()

        aggregated_stats['pourcentage_signalisation_gaspard'] = (
            (aggregated_stats['nombre_signalisation_gaspard'] / aggregated_stats['nombre_signalisation']) * 100
        ).round(2)
        aggregated_stats['pourcentage_signalisation_gaspard'].fillna(0, inplace=True)

        aggregated_stats.rename(columns={
            dept_col: 'Département',
            unit_col: 'Libellé Unité',
            material_col: 'Matériel',
            terminal_col: 'Terminal de saisie',
            'nombre_signalisation': 'Nombre de signalisation',
            'nombre_signalisation_gaspard': 'Nombre de signalisation GASPARD',
            'pourcentage_signalisation_gaspard': 'Pourcentage signalisation GASPARD'
        }, inplace=True)

        # Formatage du département sur 2 chiffres
        dept_col_renamed = 'Département'
        if dept_col_renamed in aggregated_stats.columns:
            aggregated_stats[dept_col_renamed] = aggregated_stats[dept_col_renamed].astype(str).str.zfill(2)

        aggregated_stats.sort_values(by=['Département', 'Libellé Unité'], ascending=[True, True], inplace=True)

        if not isinstance(self.stats, dict):
            self.stats = {}
        self.stats['global_summary_table'] = aggregated_stats
        print(f"Statistiques globales générées avec {len(aggregated_stats)} lignes.")

    def _generate_sm_stats(self):
        """Génère des statistiques agrégées sur les données de type 'SM' uniquement."""
        if not isinstance(self.stats, dict):
            self.stats = {}
        self.stats['sm_summary_table'] = pd.DataFrame()  # Préparer table vide

        if self.processed_data is None or self.processed_data.empty:
            print("Aucune donnée traitée disponible pour générer les statistiques SM.")
            return

        # Colonnes attendues
        dept_col = 'departement'
        unit_col = 'abrege_unite'
        material_col = 'type_materiel'
        terminal_col = 'code_unite_terminal_de_saisie'
        # Résoudre la colonne idpp de manière insensible à la casse
        idpp_col = next((c for c in self.processed_data.columns if c.lower() == 'idpp'), None)
        type_col = self.processing_params.get('type_column')  # Requis pour filtrer SM

        grouping_cols = [dept_col, unit_col, material_col, terminal_col]
        required_cols = grouping_cols + ([idpp_col] if idpp_col else []) + [type_col]

        if not type_col:
            err_msg = "Colonne 'type' non spécifiée pour le traitement."
            print(f"Erreur: {err_msg} Impossible de générer les statistiques SM.")
            self.stats['sm_error'] = err_msg
            return

        missing_cols = [col for col in required_cols if col not in self.processed_data.columns]
        if not idpp_col:
            missing_cols.append('idpp')
        if missing_cols:
            err_msg = f"Colonnes manquantes pour stats SM: {', '.join(missing_cols)}"
            print(f"Attention: {err_msg}")
            self.stats['sm_error'] = err_msg
            return

        # Filtrer SM
        print(f"Filtrage des données pour ne garder que le type 'SM' basé sur la colonne '{type_col}'.")
        sm_data = self.processed_data[
            self.processed_data[type_col].astype(str).str.upper() == 'SM'
        ].copy()

        if sm_data.empty:
            print("Aucune donnée de type 'SM' trouvée après filtrage. Stats SM resteront vides.")
            return
        print(f"{len(sm_data)} lignes de type 'SM' trouvées.")

        # Calcul des statistiques sur SM
        print(f"Génération des statistiques SM par groupe: {grouping_cols}")
        stats_df = sm_data

        is_gaspard_col = 'is_gaspard'
        stats_df[is_gaspard_col] = stats_df[idpp_col].notna() & (stats_df[idpp_col].astype(str).str.strip() != '')
        stats_df[is_gaspard_col] = stats_df[is_gaspard_col].astype(int)
        print(f"Identification des signalisations GASPARD basée sur la présence d'une valeur dans '{idpp_col}' (sur données SM).")

        aggregated_stats = stats_df.groupby(grouping_cols).agg(
            nombre_signalisation=(grouping_cols[0], 'size'),
            nombre_signalisation_gaspard=(is_gaspard_col, 'sum')
        ).reset_index()

        aggregated_stats['pourcentage_signalisation_gaspard'] = (
            (aggregated_stats['nombre_signalisation_gaspard'] / aggregated_stats['nombre_signalisation']) * 100
        ).round(2)
        aggregated_stats['pourcentage_signalisation_gaspard'].fillna(0, inplace=True)

        aggregated_stats.rename(columns={
            dept_col: 'Département',
            unit_col: 'Libellé Unité',
            material_col: 'Matériel',
            terminal_col: 'Terminal de saisie',
            'nombre_signalisation': 'Nombre de signalisation',
            'nombre_signalisation_gaspard': 'Nombre de signalisation GASPARD',
            'pourcentage_signalisation_gaspard': 'Pourcentage signalisation GASPARD'
        }, inplace=True)

        # Lignes de synthèse GGD par département
        dept_summary_list = []
        dept_grouped = stats_df.groupby(dept_col).agg(
            dept_total_signalisations=(dept_col, 'size'),
            dept_gaspard_signalisations=(is_gaspard_col, 'sum')
        )
        for dept_val, row in dept_grouped.iterrows():
            dept_total = row['dept_total_signalisations']
            dept_gaspard = row['dept_gaspard_signalisations']
            dept_percentage = round((dept_gaspard / dept_total) * 100, 2) if dept_total > 0 else 0
            dept_summary_list.append({
                'Département': dept_val,
                'Libellé Unité': f"GGD {dept_val}",
                'Matériel': "NeoDK",
                'Terminal de saisie': pd.NA,
                'Nombre de signalisation': dept_total,
                'Nombre de signalisation GASPARD': dept_gaspard,
                'Pourcentage signalisation GASPARD': dept_percentage
            })
        dept_summary_df = pd.DataFrame(dept_summary_list)

        final_sm_stats_df = pd.concat([aggregated_stats, dept_summary_df], ignore_index=True)

        final_sm_stats_df['is_cic'] = (~final_sm_stats_df['Libellé Unité'].astype(str).str.startswith('CIC', na=False)).astype(int)
        final_sm_stats_df.sort_values(by=['Département', 'is_cic', 'Libellé Unité'], ascending=[True, True, True], inplace=True)
        final_sm_stats_df.drop(columns=['is_cic'], inplace=True)

        self.stats['sm_summary_table'] = final_sm_stats_df
        print(f"Statistiques SM (avec synthèses GGD) générées avec {len(final_sm_stats_df)} lignes.")


    def has_stats(self):
        """Vérifie si au moins un type de statistiques est disponible."""
        # Vérifie si self.stats est un dictionnaire et contient au moins une table de résumé non vide
        return isinstance(self.stats, dict) and (
            ('global_summary_table' in self.stats and not self.stats['global_summary_table'].empty) or
            ('sm_summary_table' in self.stats and not self.stats['sm_summary_table'].empty)
        )
    
    def get_stats(self):
        """Retourne le dictionnaire complet des statistiques actuelles."""
        return self.stats if isinstance(self.stats, dict) else {}