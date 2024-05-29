from tinydb import TinyDB, Query
import os
import re


class DataBase(TinyDB):
    def __init__(self, url='tinydb.json', path_to_db='./data'):
        super().__init__(os.path.join(path_to_db, url))
        # if not os.path.exists(path_to_db):
        #     print(f"Creating directory {path_to_db}")
        #     os.makedirs(path_to_db)
        # else:
        #     print(f"Directory {path_to_db} already exists")
        # self.db = TinyDB(url)

    # Function to perform case-insensitive search
    def case_insensitive_search(self, field, keywords):
        query = Query()
        results = []
        for keyword in keywords:
            # Add the results of each keyword search to the results list
            results.extend(self.search(query[field].test(lambda value: keyword.lower() in value.lower())))
        return results

    def Query(self):
        return Query()
     
    def get_by_substring(self, substring, field):
        return self.search(Query()[field].matches('.*{}.*'.format(substring), flags=re.IGNORECASE))


class DBMedrXiv(DataBase):
    def __init__(self, url='medrxiv.json', path_to_db='./data'):
        super().__init__(url, path_to_db)
        self.url=url
        print(f"DBMedrXiv: {self.url}")


class DBResearch(DataBase): 
    def __init__(self, url='research.json', path_to_db='./data'):
        super().__init__(url, path_to_db)

    def insert(self, data):
        self.db.insert(data)    

    def get(self, key):
        return self.db.search(Query().key == key)

    def get_all(self):
        return self.db.all()   

    def update(self, key, data):
        self.db.update(data, Query().key == key)

    def upsert(self, key, data):
        self.db.upsert(data, Query().key == key)

    def delete(self, key):  
        self.db.remove(Query().key == key)

    def get_by_substring(self, substring, field):
        return self.db.search(Query()[field].matches('.*{}.*'.format(substring), flags=re.IGNORECASE))

    def close(self):
        self.db.close()
