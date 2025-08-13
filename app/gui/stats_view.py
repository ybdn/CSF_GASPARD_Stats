#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy
# import matplotlib.pyplot as plt # Plus nécessaire pour l'affichage principal
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas # Plus nécessaire
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar # Plus nécessaire
import pandas as pd

class StatsView(QWidget):
    """Vue d'affichage des statistiques combinées (globales et SM) sous forme de tableau."""

    def __init__(self, data_processor):
        super().__init__()
        self.data_processor = data_processor
        self._setup_ui()

    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # En-tête
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 5)
        self.status_label = QLabel("Aucune statistique disponible")
        header_layout.addWidget(self.status_label)
        header_layout.addStretch()

        # Bouton d'export
        self.export_button = QPushButton("Exporter Tableau Combiné")
        self.export_button.setMinimumWidth(200)
        self.export_button.clicked.connect(self._export_stats)
        self.export_button.setEnabled(False)
        header_layout.addWidget(self.export_button)

        main_layout.addLayout(header_layout)

        # Création du tableau
        self.stats_table = QTableWidget()
        self.stats_table.setEditTriggers(QTableWidget.NoEditTriggers) # Lecture seule
        self.stats_table.setAlternatingRowColors(True)
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Étirer les colonnes
        self.stats_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        main_layout.addWidget(self.stats_table, 1)

    def update_view(self):
        """Met à jour la vue avec les données actuelles."""
        self.stats_table.setRowCount(0) # Vider le tableau
        self.stats_table.setColumnCount(0)
        
        stats_data = self.data_processor.get_stats()
        self.combined_df = pd.DataFrame() # Initialiser le df combiné pour l'export

        # Vérifier si des données statistiques existent
        if stats_data:
            global_df = stats_data.get('global_summary_table')
            sm_df = stats_data.get('sm_summary_table')
            global_error = stats_data.get('global_error')
            sm_error = stats_data.get('sm_error')
            
            error_messages = []
            if global_error: error_messages.append(f"Erreur Globale: {global_error}")
            if sm_error: error_messages.append(f"Erreur SM: {sm_error}")

            valid_dfs = []
            if isinstance(global_df, pd.DataFrame) and not global_df.empty:
                global_df_copy = global_df.copy()
                global_df_copy['Type Statistique'] = 'Globale'
                valid_dfs.append(global_df_copy)
            
            if isinstance(sm_df, pd.DataFrame) and not sm_df.empty:
                sm_df_copy = sm_df.copy()
                sm_df_copy['Type Statistique'] = 'SM'
                valid_dfs.append(sm_df_copy)

            if valid_dfs:
                # Concaténer les dataframes valides
                self.combined_df = pd.concat(valid_dfs, ignore_index=True)
                
                # S'assurer que la colonne 'Type Statistique' est la première
                cols = ['Type Statistique'] + [col for col in self.combined_df.columns if col != 'Type Statistique']
                self.combined_df = self.combined_df[cols]

                self.status_label.setText(f"Statistiques agrégées ({len(self.combined_df)} lignes). " + " ".join(error_messages))
                self.export_button.setEnabled(True)
                
                # Configurer le tableau
                self.stats_table.setRowCount(len(self.combined_df))
                self.stats_table.setColumnCount(len(self.combined_df.columns))
                self.stats_table.setHorizontalHeaderLabels(self.combined_df.columns)
                
                # Remplir le tableau
                for i, row in self.combined_df.iterrows():
                    for j, value in enumerate(row):
                        item_value = str(value) if not pd.isna(value) else ""
                        item = QTableWidgetItem(item_value)
                        self.stats_table.setItem(i, j, item)
                
                self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
                # Redimensionner la colonne 'Type Statistique' en dernier si besoin
                try:
                    type_col_index = self.combined_df.columns.get_loc('Type Statistique')
                    self.stats_table.horizontalHeader().setSectionResizeMode(type_col_index, QHeaderView.ResizeToContents)
                except KeyError:
                    pass # Au cas où la colonne ne serait pas là
            
            elif error_messages: # S'il n'y a que des erreurs
                 self.status_label.setText(" ".join(error_messages))
                 self.export_button.setEnabled(False)
                 self.stats_table.setColumnCount(1)
                 self.stats_table.setHorizontalHeaderLabels(['Erreurs'])
                 self.stats_table.setRowCount(len(error_messages))
                 for i, msg in enumerate(error_messages):
                      self.stats_table.setItem(i, 0, QTableWidgetItem(msg))
                 self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            else: # Aucune donnée valide et aucune erreur spécifique
                self.status_label.setText("Aucune statistique à afficher.")
                self.export_button.setEnabled(False)
        else:
            self.status_label.setText("Aucune statistique disponible")
            self.export_button.setEnabled(False)
    
    # Suppression de _update_chart car les graphiques ne sont plus l'affichage principal
    # def _update_chart(self):
    #     ...
    
    def _export_stats(self):
        """Exporte les statistiques combinées affichées dans le tableau."""
        
        # Utiliser le dataframe combiné stocké lors de l'update_view
        if hasattr(self, 'combined_df') and not self.combined_df.empty:
            df_to_export = self.combined_df
            
            # Proposer un nom de fichier par défaut
            default_filename = "statistiques_combinees.csv"
            # Définir les filtres de fichiers
            file_filter = "Fichiers CSV (*.csv);;Fichiers Excel (*.xlsx)"
            
            # Ouvrir la boîte de dialogue "Enregistrer sous"
            file_path, selected_filter = QFileDialog.getSaveFileName(self, 
                                                     "Exporter Tableau Combiné",
                                                     default_filename, 
                                                     file_filter)

            if file_path:
                try:
                    # Déterminer le format basé sur l'extension ou le filtre sélectionné
                    if file_path.lower().endswith('.xlsx') or "*.xlsx" in selected_filter:
                        df_to_export.to_excel(file_path, index=False)
                        format_used = "Excel"
                    else: # Par défaut ou si .csv est choisi
                        # Assurer l'extension .csv si non présente
                        if not file_path.lower().endswith('.csv'):
                            file_path += '.csv'
                        df_to_export.to_csv(file_path, index=False, sep=';', encoding='utf-8-sig') # Utiliser ; et encodage pour Excel FR
                        format_used = "CSV"
                    
                    self.status_label.setText(f"Tableau combiné exporté en {format_used} vers {file_path}")
                    QMessageBox.information(self, "Export Réussi", f"Le tableau combiné a été exporté avec succès au format {format_used}.")
                except Exception as e:
                    error_msg = f"Erreur lors de l'exportation: {str(e)}"
                    self.status_label.setText(error_msg)
                    QMessageBox.critical(self, "Erreur d'Exportation", error_msg)
            # else: L'utilisateur a annulé

        else:
            self.status_label.setText("Aucun tableau combiné à exporter.")
            QMessageBox.warning(self, "Export Impossible", "Aucun tableau de statistiques combinées à exporter.") 