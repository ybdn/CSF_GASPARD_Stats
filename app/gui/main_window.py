#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMenuBar, QMenu, QAction, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from gui.import_view import ImportView
from gui.stats_view import StatsView
from gui.directory_merge_view import DirectoryMergeView
from core.data_processor import DataProcessor
from utils.file_handlers import import_data
from utils.directory_manager import DirectoryManager

class MainWindow(QMainWindow):
    """Fenêtre principale de l'application."""
    
    def __init__(self):
        super().__init__()
        
        # Configuration de base
        self.setWindowTitle("Traitement de Données")
        self.setMinimumSize(1024, 700)
        
        # Initialisation des composants principaux
        self.directory_manager = DirectoryManager()
        self.data_processor = DataProcessor(self.directory_manager)
        
        # Configuration de l'interface
        self._setup_ui()
        self._setup_menu()
        
    def _setup_ui(self):
        """Configure les éléments d'interface principaux."""
        # Création du widget central avec onglets
        self.tabs = QTabWidget()
        
        # Création des vues
        self.stats_view = StatsView(self.data_processor)
        self.import_view = ImportView(self.data_processor, self.stats_view)
        self.directory_merge_view = DirectoryMergeView(self.directory_manager)
        
        # Ajout des onglets avec icônes
        self.tabs.addTab(self.import_view, QIcon.fromTheme("document-open", QIcon("resources/icons/import.png")), "Import de Données")
        self.tabs.addTab(self.stats_view, QIcon.fromTheme("view-statistics", QIcon("resources/icons/stats.png")), "Statistiques Combinées")
        self.tabs.addTab(self.directory_merge_view, QIcon.fromTheme("folder-sync", QIcon("resources/icons/merge.png")), "Gestion de l'annuaire intégré")
        
        # Définition du widget central
        self.setCentralWidget(self.tabs)
        
    def _setup_menu(self):
        """Configure la barre de menu de l'application."""
        # Création de la barre de menu
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        
        # Menu Fichier
        file_menu = QMenu("Fichier", self)
        menu_bar.addMenu(file_menu)
        
        # Actions du menu Fichier
        import_action = QAction(QIcon.fromTheme("document-open", QIcon("resources/icons/import.png")), "Importer des données...", self)
        import_action.triggered.connect(self._import_data)
        file_menu.addAction(import_action)
        
        # Ajout d'une séparation
        file_menu.addSeparator()
        
        # Action pour fusionner des fichiers CSV
        merge_action = QAction(QIcon.fromTheme("folder-sync", QIcon("resources/icons/merge.png")), "Fusionner des fichiers CSV...", self)
        merge_action.triggered.connect(self._show_merge_tab)
        file_menu.addAction(merge_action)
        
        # Ajout d'une séparation
        file_menu.addSeparator()
        
        exit_action = QAction(QIcon.fromTheme("application-exit", QIcon("resources/icons/exit.png")), "Quitter", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Aide
        help_menu = QMenu("Aide", self)
        menu_bar.addMenu(help_menu)
        
        about_action = QAction(QIcon.fromTheme("help-about", QIcon("resources/icons/about.png")), "À propos", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _import_data(self):
        """Ouvre une boîte de dialogue pour importer des données."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importer des données", "", 
            "Fichiers Excel (*.xlsx *.xls);;Fichiers CSV (*.csv);;Tous les fichiers (*)"
        )
        
        if file_path:
            try:
                data = import_data(file_path)
                self.data_processor.set_data(data)
                self.import_view.update_view()
                self.stats_view.update_view()
                self.tabs.setCurrentIndex(0)  # Affiche l'onglet d'import
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'importation", f"Impossible d'importer le fichier: {str(e)}")
    
    def _show_merge_tab(self):
        """Affiche l'onglet de fusion d'annuaires."""
        self.tabs.setCurrentWidget(self.directory_merge_view)
    
    def _show_about(self):
        """Affiche la boîte de dialogue À propos."""
        QMessageBox.about(
            self, 
            "À propos de l'Application",
            "Application de Traitement de Données\n\n"
            "Version 1.0\n"
            "© 2023 Tous droits réservés"
        ) 