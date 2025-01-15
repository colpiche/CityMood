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
    publication_date: date
    url: str
    title: str
    description: str
    content: str

class DBPrompt(TypedDict):
    text_used: str
    image_url: str

class DBDay(TypedDict):
    article_id: int
    prompt_id: int
    date: date

class Manager:

    _article_table_command: str = '''
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        publication_date DATE NOT NULL,
        url TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        content TEXT
    '''

    _prompt_table_command: str = '''
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text_used TEXT NOT NULL,
        image_url TEXT
    '''

    _day_table_command: str = '''
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        article_id INTEGER NOT NULL UNIQUE,
        prompt_id INTEGER NOT NULL,
        date DATE NOT NULL,
        FOREIGN KEY (article_id) REFERENCES article(id) ON DELETE CASCADE,
        FOREIGN KEY (prompt_id) REFERENCES prompt(id) ON DELETE CASCADE
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
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        print(f"Connexion à la base de données {self.db_name} établie.")

    def create_table(self, table_name: DBTables, schema):
        """Crée une table avec un schéma spécifié."""
        query = f"CREATE TABLE IF NOT EXISTS {table_name.value} ({schema})"
        self.cursor.execute(query)
        self.connection.commit()
        print(f"Table {table_name.value} créée ou déjà existante.")

    def insert_data(self, table_name: DBTables, data: DBArticle | DBPrompt | DBDay) -> int | None:
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

        inserted_id = self.cursor.lastrowid
        return inserted_id

    def get_data(self, table_name: DBTables, columns="*"):
        """Récupère les données d'une table."""
        query = f"SELECT {columns} FROM {table_name.value}"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_article_by_date(self, date: date, time_of_day: datetime) -> list[DBArticle]:
        """
        Récupère les articles de la date spécifiée avant l'heure donnée,
        ainsi que ceux de la veille après cette heure, qui ne sont pas 
        déjà présents dans la table 'day'.
        
        :param date: Date pour laquelle récupérer les articles.
        :param time_of_day: Heure limite pour séparer les articles.
        :return: Liste des articles correspondant aux critères.
        """
        # Calculer les plages de dates et heures
        end_of_time_of_day = datetime.combine(date, time_of_day.time())
        
        day_before = date - timedelta(days=1)
        start_of_previous_day = datetime.combine(day_before, time_of_day.time())
        
        # Construire la requête SQL
        query = f"""
            SELECT a.*
            FROM {DBTables.ARTICLE.value} a
            LEFT JOIN {DBTables.DAY.value} d ON a.id = d.article_id
            WHERE 
                (
                    (a.publication_date BETWEEN ? AND ?)
                    OR 
                    (a.publication_date BETWEEN ? AND ?)
                )
                AND d.article_id IS NULL
        """
        
        # Exécuter la requête avec les plages de dates et heures
        self.cursor.execute(
            query,
            (datetime.combine(date, datetime.min.time()), end_of_time_of_day,  # Articles du jour avant l'heure
            start_of_previous_day, datetime.combine(day_before, datetime.max.time()))  # Articles de la veille après l'heure
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