from datetime import date, datetime, timedelta
import sqlite3
import os
from typing import Any, TypedDict, NotRequired
from enum import Enum

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
    date_id: int
    text_used: str
    image_url: str

class DBDay(TypedDict):
    id: NotRequired[int]
    date: date

class Manager:

    _article_table_command: str = '''
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        publication_date DATE NOT NULL,
        url TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        content TEXT,
        day_id INTEGER NOT NULL UNIQUE,
        FOREIGN KEY (day_id) REFERENCES day(id) ON DELETE CASCADE
    '''

    _prompt_table_command: str = '''
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text_used TEXT NOT NULL,
        image_url TEXT,
        day_id INTEGER NOT NULL,
        FOREIGN KEY (day_id) REFERENCES day(id) ON DELETE CASCADE
    '''

    _day_table_command: str = '''
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL
    '''

    def __init__(self, db_name: str):
        self.db_name: str = db_name
        self.db_file: str = f'{self.db_name}.db'
        self.db_folder: str = os.path.join(os.path.dirname(__file__), '..', 'database')
        self.db_path: str = os.path.join(self.db_folder, self.db_file)
        self.connection: sqlite3.Connection
        self.cursor: sqlite3.Cursor
        self._create_database()
        self.create_table(DBTables.ARTICLE, self._article_table_command)
        self.create_table(DBTables.PROMPT, self._prompt_table_command)
        self.create_table(DBTables.DAY, self._day_table_command)

    def _create_database(self):
        """Crée le dossier ../database si nécessaire et la base de données."""

        # Définir le chemin complet vers la base de données
        if not os.path.exists(self.db_folder):
            os.makedirs(self.db_folder)
            print(f"Dossier {self.db_folder} créé.")

        # # Connexion à la base de données
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        print(f"Connexion à la base de données {self.db_name} établie.")

    def create_table(self, table_name: DBTables, schema):
        """Crée une table avec un schéma spécifié."""
        query = f"CREATE TABLE IF NOT EXISTS {table_name.value} ({schema})"
        self.cursor.execute(query)
        self.connection.commit()
        print(f"Table {table_name.value} créée ou déjà existante.")

    def insert_data(self, table_name: DBTables, data: DBArticle | DBPrompt | DBDay) -> int:
        """
        Insère des données dans la table spécifiée.
        """

        # ----- TO FIX -----
        # if not (
        #     (table_name == 'article' and type(data) is DBArticle)
        #     or (table_name == 'prompt' and type(data) is DBPrompt)
        # ):
        #     print("La table et le format de données à y insérer ne correspondent pas.")
        #     return

        columns = list(data.keys())
        values = list(data.values())
        
        query = f"INSERT INTO {table_name.value} ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(values))})"
        
        self.cursor.execute(query, values)
        self.connection.commit()
        print(f"Données insérées dans {table_name.value}.")

        inserted_id = int(self.cursor.lastrowid) if self.cursor.lastrowid else -1
        return inserted_id

    def get_data(self, table_name: DBTables, columns="*"):
        """Récupère les données d'une table."""
        query = f"SELECT {columns} FROM {table_name.value}"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_article_by_date(self, id_day:int) -> list[DBArticle]:
        """
        Récupère les articles de la date spécifiée avant 9h00,
        ainsi que ceux de la veille 9h00, qui ne sont pas 
        déjà présents dans la table 'day'.
        
        :param date: Date pour laquelle récupérer les articles.
        :return: Liste des articles correspondant aux critères.
        """
        
        # Construire la requête SQL
        query = f"""
            SELECT a.*
            FROM {DBTables.ARTICLE.value} a
            LEFT JOIN {DBTables.DAY.value} d ON a.day_id = d.id
            WHERE d.id = ?
        """
        
        # Exécuter la requête avec les plages de dates et heures
        self.cursor.execute(
            query,
            (id_day,)  # Articles de la veille après l'heure
        )

        rows = self.cursor.fetchall()
        return self._cast_db_rows_as_DBArticle(rows)
    
    def get_all_articles(self) -> list[DBArticle]:
        """
        Récupère tous les articles de la base de données.
        
        :return: Liste des articles sous forme de dictionnaires.
        """
        query = f"SELECT * FROM {DBTables.ARTICLE.value}"

        # Exécuter la requête et récupérer les résultats
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return self._cast_db_rows_as_DBArticle(rows)     
    
    def _cast_db_rows_as_DBArticle(self, rows: list[Any]) -> list[DBArticle]:
        # Récupérer les noms des colonnes pour créer des dictionnaires
        column_names = [desc[0] for desc in self.cursor.description]
        
        articles: list[DBArticle] = []
        
        for row in rows:
            article_dict = dict(zip(column_names, row))
            
            # Convertir la chaîne de date en objet datetime.date
            article_dict['publication_date'] = datetime.strptime(
                article_dict['publication_date'], "%Y-%m-%d %H:%M:%S.%f"
            ).date()
            
            # Convertir le dictionnaire en DBArticle
            articles.append(DBArticle(**article_dict))
        
        return articles

    def _cast_db_rows_as_DBDay(self, rows: list[Any]) -> list[DBDay]:
        # Récupérer les noms des colonnes pour créer des dictionnaires
        column_names = [desc[0] for desc in self.cursor.description]
        
        days: list[DBDay] = []
        
        for row in rows:
            article_dict = dict(zip(column_names, row))
            
            # Convertir la chaîne de date en objet datetime.date
            article_dict['date'] = datetime.strptime(
                article_dict['date'], "%Y-%m-%d"
            ).date()
            
            # Convertir le dictionnaire en DBArticle
            days.append(DBDay(**article_dict))
        
        return days
    
    def close(self):
        """Ferme la connexion à la base de données."""
        if self.connection:
            self.connection.close()
            print("Connexion à la base de données fermée.")
            
    def get_article_by_url(self, url: str) -> list[DBArticle]:
        """
        Vérifie si l'url rentré en paramètre est déjà enregistré dans 
        la base de donné
        
        :param url: URL de l'article à vérifier.
        """
        
        # Construire la requête SQL
        query = f"""
            SELECT a.*
            FROM {DBTables.ARTICLE.value} a
            WHERE a.url = ?
        """
        
        # Exécuter la requête avec les plages de dates et heures
        self.cursor.execute(query, (url,))
        rows = self.cursor.fetchall()
        return self._cast_db_rows_as_DBArticle(rows)
    
    def get_day_id_by_date(self, date:date) -> int:
        query = f"""
            SELECT a.*
            FROM {DBTables.DAY.value} a
            WHERE a.date = ?
        """
        
        # Exécuter la requête avec les plages de dates et heures
        self.cursor.execute(query, (date,))
        rows = self.cursor.fetchall()
        if (rows != []):
            return self._cast_db_rows_as_DBDay(rows)[0]["id"]
        else :
            return(self.insert_data(DBTables.DAY, DBDay(date=date)))
        #return self._cast_db_rows_as_DBArticle(rows)