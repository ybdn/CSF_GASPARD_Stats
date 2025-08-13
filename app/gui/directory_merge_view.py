#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFileDialog, QComboBox, QGroupBox, QGridLayout, QMessageBox,
                            QTableView, QLineEdit, QCheckBox,
                            QListWidget, QListWidgetItem, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import pandas as pd
import os
from utils.file_handlers import import_csv

class DirectoryMergeView(QWidget):
    """Vue de fusion de fichiers CSV pour créer un annuaire."""
    
    def __init__(self, directory_manager):
        super().__init__()
        self.directory_manager = directory_manager
        self.file1_path = None
        self.file2_path = None
        self.file1_data = None
        self.file2_data = None
        self._setup_ui()
        
    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # En-tête
        header_label = QLabel("Interface de fusion de fichiers CSV pour créer un annuaire intégré")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(header_label)
        
        # Section d'importation des fichiers
        import_group = QGroupBox("Importation des fichiers CSV")
        import_layout = QGridLayout()
        import_layout.setSpacing(10)
        import_layout.setContentsMargins(10, 15, 10, 15)
        
        # Configurer l'étirement des colonnes
        import_layout.setColumnStretch(0, 0) # Labels : taille fixe
        import_layout.setColumnStretch(1, 1) # Champs de saisie / listes : s'étire
        import_layout.setColumnStretch(2, 0) # Boutons : taille fixe

        # Premier fichier
        import_layout.addWidget(QLabel("Annuaire GN .CSV"), 0, 0)
        self.file1_label = QLabel("Aucun fichier sélectionné")
        self.file1_label.setWordWrap(True) # Permettre le retour à la ligne si nécessaire
        import_layout.addWidget(self.file1_label, 0, 1)
        self.file1_button = QPushButton("Parcourir...")
        self.file1_button.clicked.connect(self._import_file1)
        import_layout.addWidget(self.file1_button, 0, 2)
        
        # Clé Fichier 1
        import_layout.addWidget(QLabel("Selectionner la colonne 'Code Unité' dans le fichier n°1 :"), 1, 0)
        self.key1_combo = QComboBox()
        self.key1_combo.setEnabled(False)
        import_layout.addWidget(self.key1_combo, 1, 1, 1, 2)
        
        # Colonnes à supprimer Fichier 1
        import_layout.addWidget(QLabel("Cocher les colonnes inutiles pour la fusion :"), 2, 0)
        self.columns_to_delete_list1 = QListWidget()
        # self.columns_to_delete_list1.setFixedHeight(100) # Remplacé par minimum/politique
        self.columns_to_delete_list1.setMinimumHeight(80)
        self.columns_to_delete_list1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding) # Permet expansion verticale
        self.columns_to_delete_list1.setEnabled(False)
        import_layout.addWidget(self.columns_to_delete_list1, 2, 1, 1, 2)
        
        # Deuxième fichier
        import_layout.addWidget(QLabel("Annuaire des matériels de saisie .CSV:"), 3, 0)
        self.file2_label = QLabel("Aucun fichier sélectionné")
        self.file2_label.setWordWrap(True) # Permettre le retour à la ligne si nécessaire
        import_layout.addWidget(self.file2_label, 3, 1)
        self.file2_button = QPushButton("Parcourir...")
        self.file2_button.clicked.connect(self._import_file2)
        import_layout.addWidget(self.file2_button, 3, 2)
        
        # Clé Fichier 2
        import_layout.addWidget(QLabel("Sélectionner la colonne 'Code Unité' dans le fichier n°2:"), 4, 0)
        self.key2_combo = QComboBox()
        self.key2_combo.setEnabled(False)
        import_layout.addWidget(self.key2_combo, 4, 1, 1, 2)
        
        # Colonnes à supprimer Fichier 2
        import_layout.addWidget(QLabel("Cocher les colonnes inutiles pour la fusion :"), 5, 0)
        self.columns_to_delete_list2 = QListWidget()
        # self.columns_to_delete_list2.setFixedHeight(100) # Remplacé par minimum/politique
        self.columns_to_delete_list2.setMinimumHeight(80)
        self.columns_to_delete_list2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding) # Permet expansion verticale
        self.columns_to_delete_list2.setEnabled(False)
        import_layout.addWidget(self.columns_to_delete_list2, 5, 1, 1, 2)
        
        import_group.setLayout(import_layout)
        main_layout.addWidget(import_group)
        
        # Section de configuration de la fusion
        merge_config_group = QGroupBox("Configuration de la fusion")
        merge_config_layout = QGridLayout()
        merge_config_layout.setSpacing(10)
        merge_config_layout.setContentsMargins(10, 15, 10, 15)
        
        # Type de fusion
        merge_config_layout.addWidget(QLabel("Type de fusion:"), 0, 0)
        self.merge_type_combo = QComboBox()
        self.merge_type_combo.addItems(["outer (conserve toutes les lignes)", 
                                       "inner (uniquement les lignes communes)", 
                                       "left (priorité au premier fichier)",
                                       "right (priorité au deuxième fichier)"])
        merge_config_layout.addWidget(self.merge_type_combo, 0, 1)
        
        # Nom de fichier pour l'annuaire fusionné
        merge_config_layout.addWidget(QLabel("Nom du fichier annuaire cible:"), 1, 0)
        self.output_file_edit = QLineEdit("directory.csv")
        merge_config_layout.addWidget(self.output_file_edit, 1, 1)
        
        # Info sur le formatage/combinaison automatique
        info_label = QLabel("Note: Les clés (Code Unité) seront formatées (GN+8 chiffres) et les doublons combinés automatiquement.")
        info_label.setStyleSheet("font-style: italic; color: grey;")
        merge_config_layout.addWidget(info_label, 2, 0, 1, 2)

        merge_config_group.setLayout(merge_config_layout)
        main_layout.addWidget(merge_config_group)
        
        # Bouton de fusion
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.merge_button = QPushButton("  Fusionner les fichiers  ")
        self.merge_button.clicked.connect(self._merge_files)
        self.merge_button.setEnabled(False)
        button_layout.addWidget(self.merge_button)
        main_layout.addLayout(button_layout)
        
    def _import_file1(self):
        """Importe le premier fichier CSV."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importer le premier fichier CSV", "", 
            "Fichiers CSV (*.csv);;Tous les fichiers (*)"
        )
        
        if file_path:
            try:
                # Importer le fichier
                self.file1_data = import_csv(file_path)
                self.file1_path = file_path
                
                # Mettre à jour l'interface
                self.file1_label.setText(os.path.basename(file_path))
                self._update_key1_combo()
                self._update_merge_button()
                self._populate_columns_list1()
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'importation", f"Impossible d'importer le fichier: {str(e)}")
    
    def _import_file2(self):
        """Importe le deuxième fichier CSV."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importer le deuxième fichier CSV", "", 
            "Fichiers CSV (*.csv);;Tous les fichiers (*)"
        )
        
        if file_path:
            try:
                # Importer le fichier
                self.file2_data = import_csv(file_path)
                self.file2_path = file_path
                
                # Mettre à jour l'interface
                self.file2_label.setText(os.path.basename(file_path))
                self._update_key2_combo()
                self._update_merge_button()
                self._populate_columns_list2()
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'importation", f"Impossible d'importer le fichier: {str(e)}")
    
    def _update_key1_combo(self):
        """Met à jour le combo box des colonnes clés du premier fichier."""
        self.key1_combo.clear()
        if self.file1_data is not None and not self.file1_data.empty:
            self.key1_combo.addItems(list(self.file1_data.columns))
            self.key1_combo.setEnabled(True)
            # Sélectionner la première colonne par défaut
            self.key1_combo.setCurrentIndex(0)
            self.columns_to_delete_list1.setEnabled(True)
    
    def _update_key2_combo(self):
        """Met à jour le combo box des colonnes clés du deuxième fichier."""
        self.key2_combo.clear()
        if self.file2_data is not None and not self.file2_data.empty:
            self.key2_combo.addItems(list(self.file2_data.columns))
            self.key2_combo.setEnabled(True)
            # Sélectionner la première colonne par défaut
            self.key2_combo.setCurrentIndex(0)
            self.columns_to_delete_list2.setEnabled(True)
    
    def _update_merge_button(self):
        """Met à jour l'état du bouton de fusion."""
        self.merge_button.setEnabled(
            self.file1_data is not None and not self.file1_data.empty and
            self.file2_data is not None and not self.file2_data.empty
        )
    
    def _merge_files(self):
        """Lance la fusion réelle des fichiers."""
        # Vérifications préliminaires
        if (self.file1_path is None or self.file2_path is None or
            self.key1_combo.currentText() == "" or self.key2_combo.currentText() == ""):
            QMessageBox.warning(self, "Informations manquantes", 
                                "Veuillez sélectionner les deux fichiers et leurs colonnes clés.")
            return

        # --- Récupérer les configurations --- 
        file1 = self.file1_path
        file2 = self.file2_path
        key1 = self.key1_combo.currentText()
        key2 = self.key2_combo.currentText()
        how = self.merge_type_combo.currentText().split(' ')[0]
        output_filename = self.output_file_edit.text()
        output_path = os.path.join('app', 'resources', 'directory', output_filename) # Chemin de sauvegarde

        # Récupérer les colonnes à supprimer
        cols_to_delete1 = []
        for i in range(self.columns_to_delete_list1.count()):
            item = self.columns_to_delete_list1.item(i)
            if item.checkState() == Qt.Checked:
                cols_to_delete1.append(item.text())
        
        cols_to_delete2 = []
        for i in range(self.columns_to_delete_list2.count()):
            item = self.columns_to_delete_list2.item(i)
            if item.checkState() == Qt.Checked:
                cols_to_delete2.append(item.text())

        # --- Mettre à jour le chemin de l'annuaire dans DirectoryManager --- 
        # Pour que la sauvegarde se fasse au bon endroit
        self.directory_manager.directory_path = output_path

        try:
            # --- Lancer la fusion via DirectoryManager ---
            success = self.directory_manager.merge_directories(
                file_path1=file1,
                file_path2=file2,
                key_column1=key1,
                key_column2=key2,
                how=how,
                columns_to_delete1=cols_to_delete1, # Passer la liste
                columns_to_delete2=cols_to_delete2  # Passer la liste
            )
            
            if success:
                QMessageBox.information(self, "Fusion réussie", 
                                        f"L'annuaire a été créé/mis à jour avec succès dans {output_path}")
            else:
                QMessageBox.critical(self, "Erreur de fusion", 
                                     "La fusion a échoué. Vérifiez la console pour plus de détails.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur de fusion", f"Impossible de fusionner les fichiers: {str(e)}")
    
    def _populate_columns_list1(self):
        """Remplit la liste des colonnes à supprimer pour le fichier 1."""
        self.columns_to_delete_list1.clear()
        if self.file1_data is not None and not self.file1_data.empty:
            for col_name in self.file1_data.columns:
                item = QListWidgetItem(col_name)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.columns_to_delete_list1.addItem(item)

    def _populate_columns_list2(self):
        """Remplit la liste des colonnes à supprimer pour le fichier 2."""
        self.columns_to_delete_list2.clear()
        if self.file2_data is not None and not self.file2_data.empty:
            for col_name in self.file2_data.columns:
                item = QListWidgetItem(col_name)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.columns_to_delete_list2.addItem(item) 