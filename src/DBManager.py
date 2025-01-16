from datetime import date
import pyodbc
import os
from typing import Any, TypedDict, NotRequired
from enum import Enum
import logging

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

class DBTables(Enum):
    ARTICLE = 'article'
    PROMPT = 'prompt'
    DAY = 'day'

class DBArticle(TypedDict):
    id: NotRequired[int]
    day_id: int
    publication_date: date
    url: str
    title: str
    description: str
    content: str

class DBPrompt(TypedDict):
    id: NotRequired[int]
    day_id: int
    text_used: str
    image_url: str

class DBDay(TypedDict):
    id: NotRequired[int]
    date: date

class DBManager:

    # Commandes SQL pour créer les tables
    _article_table_command: str = '''
        id INT IDENTITY(1,1) PRIMARY KEY,
        publication_date DATE NOT NULL,
        url NVARCHAR(MAX) NOT NULL,
        title NVARCHAR(MAX) NOT NULL,
        description NVARCHAR(MAX),
        content NVARCHAR(MAX),
        day_id INT NOT NULL,
        FOREIGN KEY (day_id) REFERENCES day(id) ON DELETE CASCADE
    '''

    _prompt_table_command: str = '''
        id INT IDENTITY(1,1) PRIMARY KEY,
        text_used NVARCHAR(MAX) NOT NULL,
        image_url NVARCHAR(MAX) NOT NULL,
        day_id INT NOT NULL,
        FOREIGN KEY (day_id) REFERENCES day(id) ON DELETE CASCADE
    '''

    _day_table_command: str = '''
        id INT IDENTITY(1,1) PRIMARY KEY,
        date DATE NOT NULL
    '''

    def __init__(self, db_name: str):
        """
        Initialise le gestionnaire de base de données.
        :param db_name: Nom de la base de données.
        """
        try:
            self.db_name: str = db_name
            self.db_file: str = f'{self.db_name}.db'
            self.db_folder: str = os.path.join(os.path.dirname(__file__), '..', 'database')
            self.db_path: str = os.path.join(self.db_folder, self.db_file)
            self.connection: pyodbc.Connection
            self.cursor: pyodbc.Cursor
            self.connecion_string: str = str(os.getenv("SQL_CONNECTION_STRING"))
            
            # Connexion et création des tables
            self.connect()
            self.create_table(DBTables.DAY, self._day_table_command)
            self.create_table(DBTables.ARTICLE, self._article_table_command)
            self.create_table(DBTables.PROMPT, self._prompt_table_command)
            self.close()
            logging.info("Initialisation de la base de données réussie.")
        except Exception as e:
            logging.error(f"Erreur lors de l'initialisation de la base de données : {e}")
            raise

    def connect(self):
        """
        Établit une connexion à la base de données.
        """
        try:
            self.connection = pyodbc.connect(self.connecion_string)
            self.cursor = self.connection.cursor()
            logging.info(f"Connexion à la base de données {self.db_name} établie.")
        except Exception as e:
            logging.error(f"Erreur lors de la connexion à la base de données : {e}")
            raise

    def create_table(self, table_name: DBTables, schema):
        """
        Crée une table avec un schéma spécifié, si elle n'existe pas.
        :param table_name: Nom de la table.
        :param schema: Définition SQL de la structure de la table.
        """
        try:
            query = f"""
                IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name.value}')
                BEGIN
                    CREATE TABLE {table_name.value} ({schema});
                END
            """
            self.cursor.execute(query)
            self.connection.commit()
            logging.info(f"Table {table_name.value} créée ou déjà existante.")
        except Exception as e:
            logging.error(f"Erreur lors de la création de la table {table_name.value} : {e}")
            raise

    def insert_data(self, table_name: DBTables, data: DBArticle | DBPrompt | DBDay) -> int:
        """
        Insère des données dans la table spécifiée.
        :param table_name: Nom de la table.
        :param data: Données à insérer sous forme de dictionnaire.
        :return: ID de la ligne insérée.
        """
        try:
            self.connect()

            # Conversion des données en colonnes et valeurs
            columns = list(data.keys())
            values = list(data.values())

            # Construction de la requête SQL avec des marqueurs de paramètres "?"
            query = f"""
                INSERT INTO {table_name.value} ({', '.join(columns)})
                OUTPUT INSERTED.id
                VALUES ({', '.join(['?' for _ in values])});
            """

            # Exécution de la requête avec les paramètres
            self.cursor.execute(query, values)

            # Récupérer l'ID de la ligne insérée
            inserted_id = self.cursor.fetchone()
            self.connection.commit()
            logging.info(f"Données insérées dans {table_name.value} avec succès.")
            
            self.close()
            if inserted_id is None:
                logging.error("Aucun ID renvoyé après insertion.")
                return -1

            return inserted_id[0]
        except Exception as e:
            logging.error(f"Erreur lors de l'insertion dans la table {table_name.value} : {e}")
            raise

    def get_data(self, table_name: DBTables, columns="*"):
        """
        Récupère toutes les données d'une table.
        :param table_name: Nom de la table.
        :param columns: Colonnes à récupérer, par défaut toutes les colonnes.
        :return: Résultats de la requête.
        """
        try:
            self.connect()
            query = f"SELECT {columns} FROM {table_name.value}"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            logging.info(f"Données récupérées depuis {table_name.value}.")
            return rows
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des données de {table_name.value} : {e}")
            raise
        finally:
            self.close()
    
    def get_article_by_date(self, id_day: int) -> list[DBArticle]:
        """
        Récupère les articles correspondant à un jour spécifique.
        :param id_day: ID du jour.
        :return: Liste d'articles.
        """
        try:
            self.connect()
            query = f"""
                SELECT a.*
                FROM {DBTables.ARTICLE.value} a
                LEFT JOIN {DBTables.DAY.value} d ON a.day_id = d.id
                WHERE d.id = ?
            """
            self.cursor.execute(query, (id_day,))
            rows = self.cursor.fetchall()
            logging.info(f"Articles récupérés pour le jour ID {id_day}.")
            return self._cast_db_rows_as_DBArticle(rows)
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des articles pour le jour ID {id_day} : {e}")
            raise
        finally:
            self.close()

    def get_all_articles(self) -> list[DBArticle]:
        """
        Récupère tous les articles de la base de données.
        :return: Liste de tous les articles sous forme de dictionnaires.
        """
        try:
            self.connect()
            query = f"SELECT * FROM {DBTables.ARTICLE.value}"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            logging.info("Tous les articles ont été récupérés.")
            return self._cast_db_rows_as_DBArticle(rows)
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de tous les articles : {e}")
            raise
        finally:
            self.close()


    def _cast_db_rows_as_DBArticle(self, rows: list[Any]) -> list[DBArticle]:
        """
        Convertit les lignes récupérées de la base de données en une liste de dictionnaires
        correspondant au format DBArticle.
        :param rows: Lignes de la base de données à convertir.
        :return: Liste d'articles sous forme de dictionnaires DBArticle.
        """
        try:
            # Récupération des noms des colonnes depuis la description du curseur
            column_names = [desc[0] for desc in self.cursor.description]
            # Conversion des lignes en une liste de dictionnaires DBArticle
            return [DBArticle(**dict(zip(column_names, row))) for row in rows]
        except Exception as e:
            logging.error(f"Erreur lors de la conversion des lignes de la base de données en DBArticle : {e}")
            raise

    def _cast_db_rows_as_DBDay(self, rows: list[Any]) -> list[DBDay]:
        """
        Convertit les lignes récupérées de la base de données en une liste de dictionnaires
        correspondant au format DBDay.
        :param rows: Lignes de la base de données à convertir.
        :return: Liste de jours sous forme de dictionnaires DBDay.
        """
        # Récupérer les noms des colonnes pour créer des dictionnaires
        column_names = [desc[0] for desc in self.cursor.description]
        
        days: list[DBDay] = []
        
        for row in rows:
            # Créer un dictionnaire à partir des valeurs de la ligne et des noms de colonnes
            article_dict = dict(zip(column_names, row))
            
            # Convertir le dictionnaire en DBDay et l'ajouter à la liste
            days.append(DBDay(**article_dict))
        
        return days

    def close(self):
        """
        Ferme la connexion à la base de données si elle est ouverte.
        """
        try:
            # Vérification que la connexion n'est pas déjà fermée
            if not self.connection.closed:
                # Fermeture de la connexion
                self.connection.close()
                logging.info("Connexion à la base de données fermée.")
        except Exception as e:
            logging.error(f"Erreur lors de la fermeture de la connexion : {e}")
            raise

    def get_article_by_url(self, url: str) -> list[DBArticle]:
        """
        Récupère les articles correspondant à une URL spécifique depuis la base de données.
        Vérifie si l'URL existe déjà dans la base de données.

        :param url: URL de l'article à vérifier.
        :return: Liste d'articles correspondant à l'URL.
        """
        # Connexion à la base de données
        self.connect()
        
        # Construire la requête SQL pour vérifier l'URL
        query = f"""
            SELECT a.*
            FROM {DBTables.ARTICLE.value} a
            WHERE a.url = ?
        """

        # Exécuter la requête avec l'URL comme paramètre
        self.cursor.execute(query, (url,))
        rows = self.cursor.fetchall()

        # Fermeture de la connexion
        self.close()

        # Retourner les articles sous forme de DBArticle
        return self._cast_db_rows_as_DBArticle(rows)
    
    def get_day_id_by_date(self, date: date) -> int:
        """
        Récupère l'ID du jour correspondant à une date spécifique depuis la base de données.
        Si la date n'existe pas, une nouvelle entrée est ajoutée.

        :param date: Date du jour à rechercher.
        :return: L'ID du jour.
        """
        # Connexion à la base de données
        self.connect()

        # Construire la requête SQL pour vérifier la date
        query = f"""
            SELECT a.*
            FROM {DBTables.DAY.value} a
            WHERE a.date = ?
        """

        # Exécuter la requête avec la date comme paramètre
        self.cursor.execute(query, (date,))
        rows = self.cursor.fetchall()
        
        # Fermeture de la connexion
        self.close()
        
        # Si la date existe, retourner l'ID du jour, sinon insérer une nouvelle ligne
        if rows:
            return self._cast_db_rows_as_DBDay(rows)[0]["id"]
        else:
            return self.insert_data(DBTables.DAY, DBDay(date=date))
