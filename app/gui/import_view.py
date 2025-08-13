#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableView, QComboBox, QSizePolicy, QSpacerItem, QFileDialog, QMessageBox, QListWidget, QListWidgetItem, QGroupBox, QAbstractItemView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from utils.file_handlers import import_data, export_data
import os
import datetime

class ImportView(QWidget):
    """Vue d'importation et de visualisation des données."""
    
    def __init__(self, data_processor, stats_view):
        super().__init__()
        self.data_processor = data_processor
        self.stats_view = stats_view
        self._setup_ui()
        
    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # En-tête
        header_layout = QHBoxLayout()
        self.status_label = QLabel("Aucune donnée importée")
        header_layout.addWidget(self.status_label)
        header_layout.addStretch()
        
        # Boutons d'action
        self.import_anfsi_button = QPushButton("Importer Extraction ANFSI")
        self.import_anfsi_button.clicked.connect(self._import_anfsi_data)
        header_layout.addWidget(self.import_anfsi_button)
        
        self.process_button = QPushButton("Traiter les Données")
        self.process_button.clicked.connect(self._process_data)
        self.process_button.setEnabled(False)
        header_layout.addWidget(self.process_button)
        
        main_layout.addLayout(header_layout)
        
        # Table de visualisation des données
        self.data_table = QTableView()
        self.data_model = QStandardItemModel()
        self.data_table.setModel(self.data_model)
        self.data_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.data_table, stretch=3)
        
        # Groupe pour les options de traitement
        options_group = QGroupBox("Options de Traitement et Fusion")
        options_main_layout = QHBoxLayout(options_group)
        
        # Layout vertical pour les sélecteurs Clé/Type et le bouton Traiter
        left_options_layout = QVBoxLayout()
        
        # Sélecteurs Clé et Type
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Colonne Clé (fusion):"))
        self.directory_column = QComboBox()
        self.directory_column.setMinimumWidth(150)
        selector_layout.addWidget(self.directory_column)
        selector_layout.addSpacing(15)
        selector_layout.addWidget(QLabel("Colonne Type (optionnel):"))
        self.type_column = QComboBox()
        self.type_column.setMinimumWidth(150)
        selector_layout.addWidget(self.type_column)
        selector_layout.addStretch()
        left_options_layout.addLayout(selector_layout)
        
        # Bouton Traiter
        self.process_button = QPushButton("Traiter et Exporter")
        self.process_button.clicked.connect(self._process_data)
        self.process_button.setEnabled(False)
        button_hbox = QHBoxLayout()
        button_hbox.addStretch()
        button_hbox.addWidget(self.process_button)
        left_options_layout.addStretch()
        left_options_layout.addLayout(button_hbox)
        
        options_main_layout.addLayout(left_options_layout, stretch=2)
        
        # Layout vertical pour la liste des colonnes à supprimer (à droite)
        delete_layout = QVBoxLayout()
        delete_layout.addWidget(QLabel("Colonnes à supprimer (avant fusion):"))
        self.columns_to_delete_list = QListWidget()
        self.columns_to_delete_list.setSelectionMode(QAbstractItemView.NoSelection)
        delete_layout.addWidget(self.columns_to_delete_list)
        options_main_layout.addLayout(delete_layout, stretch=1)
        
        main_layout.addWidget(options_group, stretch=1)
    
    def update_view(self):
        """Met à jour la vue avec les données actuelles."""
        # Effacer les éléments spécifiques avant de vérifier les données
        self.data_model.clear()
        self.directory_column.clear()
        self.type_column.clear()
        self.columns_to_delete_list.clear()
        self.process_button.setEnabled(False)
        
        if self.data_processor.has_data():
            data = self.data_processor.get_data()
            
            # Mise à jour du statut
            self.status_label.setText(f"Données importées: {len(data)} entrées")
            
            # Remplissage du modèle de tableau
            self._populate_table(data)
            
            # Mise à jour du combobox des colonnes
            self._update_columns_combo(data)
            
            # Mettre à jour la liste de suppression
            self._update_delete_list(data)
            
            # Activation du bouton de traitement
            self.process_button.setEnabled(True)
        else:
            # Réinitialisation si pas de données
            self.status_label.setText("Aucune donnée importée")
    
    def _populate_table(self, data):
        """Remplit le tableau avec les données."""
        self.data_model.clear()
        
        # Configuration des en-têtes
        if not data.empty:
            headers = list(data.columns)
            self.data_model.setHorizontalHeaderLabels(headers)
            
            # Remplissage des données
            for row in range(len(data)):
                items = []
                for col in range(len(headers)):
                    item = QStandardItem(str(data.iloc[row, col]))
                    items.append(item)
                self.data_model.appendRow(items)
    
    def _update_columns_combo(self, data):
        """Met à jour les combo boxes des colonnes disponibles."""
        self.directory_column.clear()
        self.type_column.clear()
        if not data.empty:
            column_names = data.columns.tolist()
            self.directory_column.addItems(column_names)
            self.type_column.addItems(column_names)
    
    def _import_anfsi_data(self):
        """Ouvre une boîte de dialogue pour importer une extraction ANFSI (CSV)."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importer Extraction ANFSI", "", 
            "Fichiers CSV (*.csv);;Tous les fichiers (*)"
        )

        if file_path:
            try:
                data = import_data(file_path)
                self.data_processor.set_data(data)
                self.update_view()

                # --- Suggestion : Pré-sélection de la colonne clé si connue ---
                # expected_key_column = 'code_service' # Remplacer par le vrai nom si connu
                # if expected_key_column in data.columns:
                #     self.directory_column.setCurrentText(expected_key_column)

            except Exception as e:
                QMessageBox.critical(self, "Erreur d'importation", f"Impossible d'importer le fichier: {str(e)}")
    
    def _process_data(self):
        """Traite les données avec les colonnes d'annuaire et de type sélectionnées, puis exporte."""
        if self.data_processor.has_data() and \
           self.directory_column.currentText() and \
           self.type_column.currentText():
            
            directory_col = self.directory_column.currentText()
            type_col = self.type_column.currentText()

            # --- Vérification simple pour éviter de sélectionner la même colonne pour les deux ---
            # Bien qu'il puisse y avoir des cas d'usage, c'est souvent une erreur.
            if directory_col == type_col:
                QMessageBox.warning(self, "Sélection Invalide", 
                                    "La colonne clé et la colonne type ne peuvent pas être identiques.")
                return
            # -------------------------------------------------------------------------------------

            # --- Récupérer les colonnes à supprimer ---
            columns_to_delete = []
            # Vérifier que self.columns_to_delete_list existe bien
            if hasattr(self, 'columns_to_delete_list'):
                for i in range(self.columns_to_delete_list.count()):
                    item = self.columns_to_delete_list.item(i)
                    if item.checkState() == Qt.Checked:
                        # Vérifier que la colonne à supprimer n'est pas la clé ou le type
                        col_text = item.text()
                        if col_text != directory_col and col_text != type_col:
                            columns_to_delete.append(col_text)
                        else:
                            # Décocher la case et informer l'utilisateur si la colonne clé/type est cochée
                            item.setCheckState(Qt.Unchecked)
                            QMessageBox.warning(self, "Sélection Ignorée",
                                                f"La colonne '{col_text}' ne peut pas être supprimée car elle est utilisée comme Clé ou Type.")
            # ------------------------------------------

            try:
                # --- 1. Traitement/Fusion avec l'annuaire (passant clé, type et colonnes à supprimer) ---
                print(f"Traitement lancé avec Clé='{directory_col}', Type='{type_col}', Supprimer={columns_to_delete}")
                success = self.data_processor.process_with_directory(
                    directory_col,
                    type_column=type_col,
                    columns_to_delete=columns_to_delete # Passer la liste
                )

                if success and self.data_processor.processed_data is not None:
                    self.status_label.setText(f"Données traitées (Clé='{directory_col}', Type='{type_col}').")
                    
                    # --- Mettre à jour les vues des statistiques MAINTENANT ---
                    if self.stats_view:
                        self.stats_view.update_view()
                    # -----------------------------------------------------

                    # --- 2. Récupération des données fusionnées ---
                    processed_df = self.data_processor.processed_data

                    # --- 3. Génération du nom de fichier d'export ---
                    now = datetime.datetime.now()
                    month_year = now.strftime("%m-%Y") # Format MM-YYYY
                    # Assurer que le répertoire exports existe
                    export_dir = "exports"
                    os.makedirs(export_dir, exist_ok=True)
                    export_filename = os.path.join(export_dir, f"STATS_GASPARD_{month_year}.csv")

                    # --- 4. Exportation des données fusionnées ---
                    if export_data(processed_df, export_filename, format_type='csv'):
                        QMessageBox.information(self, 
                                                "Exportation Réussie", 
                                                f"Les données fusionnées ont été exportées avec succès vers :\n{export_filename}")
                        # Optionnel : Mettre à jour le statut label
                        # self.status_label.setText(f"Données traitées et exportées vers {export_filename}")
                    else:
                         QMessageBox.warning(self, 
                                             "Erreur d'exportation", 
                                             f"La fusion a réussi mais l'exportation vers \n{export_filename}\na échoué.")
                else:
                    QMessageBox.warning(self, "Traitement Échoué", "Le traitement des données avec l'annuaire a échoué.")
                    self.status_label.setText("Échec du traitement des données.")

            except Exception as e:
                QMessageBox.critical(self, "Erreur Critique", f"Une erreur est survenue lors du traitement ou de l'exportation : {str(e)}")
                self.status_label.setText("Erreur lors du traitement.") 

    def _update_delete_list(self, data):
        """Remplit la liste des colonnes à supprimer."""
        self.columns_to_delete_list.clear()
        if not data.empty:
            for col_name in data.columns:
                item = QListWidgetItem(col_name)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.columns_to_delete_list.addItem(item) 