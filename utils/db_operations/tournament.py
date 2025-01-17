from utils.db_operations.initDB import initDB

class tournament:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()
    
    # Create new tournament if it doesn't exist
    def create_tournament(self, tournament_name, url, participants, is_side_event=False, state='upcoming'):
    # Check if tournament already exists
        self.cursor.execute(
            "SELECT * FROM tblTournaments WHERE name=%s AND url=%s",
            (tournament_name, url)
        )
        result = self.cursor.fetchone()
        # if the results are not empty, return the current data
        if result:
            return result
        
        self.cursor.execute(
            "INSERT INTO tblTournaments (name, url, participants, is_side_event, state) VALUES (%s, %s, %s, %s, %s)",
            (tournament_name, url, participants, is_side_event, state)
        )
        self.db.commit()
        
        # return the newly created tournament
        self.cursor.execute(
            "SELECT * FROM tblTournaments WHERE name=%s AND url=%s",
            (tournament_name, url)
        )
        return self.cursor.fetchone()
    
    # Update participant count
    def update_participant_count(self, tournament_id, participants):
        self.cursor.execute(
            "UPDATE tblTournaments SET participants=%s WHERE id=%s",
            (participants, tournament_id)
        )
        self.db.commit()
        
        self.cursor.execute(
            "SELECT * FROM tblTournaments WHERE id=%s",
            (tournament_id,)
        )
        return self.cursor.fetchone()
        
    
    # Update State
    def update_state(self, tournament_id, state):
        self.cursor.execute(
            "UPDATE tblTournaments SET state=%s WHERE id=%s",
            (state, tournament_id)
        )
        self.db.commit()

        self.cursor.execute(
            "SELECT * FROM tblTournaments WHERE id=%s",
            (tournament_id,)
        )
        return self.cursor.fetchone()
    
    def get_tournament_by_id(self, tournament_id):
        self.cursor.execute(
            "SELECT * FROM tblTournaments WHERE id=%s",
            (tournament_id,)
        )
        return self.cursor.fetchone()
    
    def get_tournament_by_url(self, url):
        # Clear out any previous queries
        self.cursor.fetchall()
        
        self.cursor.execute(
            "SELECT * FROM tblTournaments WHERE url=%s",
            (url,)
        )
        return self.cursor.fetchone()   
    
    def set_attendance_id(self, tournament_id, attendance_id):
        self.cursor.execute(
            "UPDATE tblTournaments SET attendance_id=%s WHERE id=%s",
            (attendance_id, tournament_id)
        )
        self.db.commit()
        
        self.cursor.execute(
            "SELECT * FROM tblTournaments WHERE id=%s",
            (tournament_id,)
        )
        return self.cursor.fetchone()
    
    def set_finalized(self, tournament_id):
        self.cursor.execute(
            "UPDATE tblTournaments SET finalized=1 WHERE id=%s",
            (tournament_id,)
        )
        self.db.commit()
        
        self.cursor.execute(
            "SELECT * FROM tblTournaments WHERE id=%s",
            (tournament_id,)
        )
        return self.cursor.fetchone()
    
    def get_finalized_status(self, tournament_id):
        self.cursor.execute(
            "SELECT finalized FROM tblTournaments WHERE id=%s OR url=%s",
            (tournament_id, tournament_id,)
        )
        return self.cursor.fetchone()