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