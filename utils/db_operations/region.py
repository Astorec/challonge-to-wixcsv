class region:
    def  __init__(self, db):
        self.db = db
        self.cursor = db.cursor()
        
    def get_region_by_id(self, region_id):
        self.cursor.execute(
            "SELECT * FROM tblRegions WHERE id=%s",
            (region_id,)
        )
        return self.cursor.fetchone()
    
    def get_region_id_by_name(self, name):
        self.cursor.execute(
            "SELECT id FROM tblRegions WHERE region=%s",
            (name,)
        )
        return self.cursor.fetchone()
    
    def get_region_id_by_short_name(self, short_name):
        self.cursor.execute(
            "SELECT id FROM tblRegions WHERE short=%s",
            (short_name,)
        )
        return self.cursor.fetchone()