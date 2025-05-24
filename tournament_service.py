import asyncio
import time
import json
import os
import logging
import signal
import utils.db_operations.initDB as initDB
import utils.db_operations.tournament as tournament
import utils.db_operations.tournamentData as tournamentData
import utils.db_operations.participants as participants
import utils.db_operations.player as players
import utils.db_operations.matches as matches
import utils.db_operations.top_cut as top_cut
import utils.db_operations.leaderboard as leaderboard
import utils.db_operations.region as region
import utils.misc as misc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tournament_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('tournament_service')

class TournamentService:
    def __init__(self, config_path='config/config.json'):
        self.config = None
        self.db = None
        self.active_monitors = {}  # Maps tournament_id -> TournamentMonitor
        self.running = True
        
        # Import TournamentMonitor here to avoid circular imports
        from tournament_monitor import TournamentMonitor
        self.TournamentMonitor = TournamentMonitor
        
        # Load configuration
        if os.path.exists(config_path):
            with open(config_path) as f:
                self.config = json.load(f)
        else:
            logger.error(f"Config file not found at {config_path}")
            raise FileNotFoundError("Config file not found")
        
        # Initialize DB
        self.db = initDB.initDB(config_path).get_connection()
        
        # Initialize DB managers
        self.modif_tournament = tournament.tournament(self.db)
        self.modif_participants = participants.participants(self.db)
        self.modif_players = players.player(self.db)
        self.modif_matches = matches.matches(self.db)
        self.modif_tournament_data = tournamentData.tournamentData(self.db)
        self.get_top_cut = top_cut.top_cut(self.db)
        self.leaderboard = leaderboard.leaderboard(self.db)
        self.region = region.region(self.db)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)
        
    def _handle_exit(self, signum, frame):
        """Handle termination signals gracefully"""
        # Only handle the signal if we haven't already started shutting down
        if self.running:
            logger.info(f"Received signal {signum}, shutting down...")
            self.running = False
            # Create a task but don't wait for it, allowing the signal handler to return quickly
            asyncio.create_task(self.shutdown())
        else:
            # If we get another signal during shutdown, force exit
            logger.warning(f"Received second interrupt signal {signum}, forcing exit...")
            import sys
            sys.exit(1)
    
    async def start(self):
        """Start the tournament service"""
        logger.info("Starting Tournament Service")
        
        # Main service loop
        while self.running:
            try:
                # Fetch unfinalized tournaments from DB
                unfinalized_tournaments = self.modif_tournament.get_unfinalized_tournaments()
                
                if not unfinalized_tournaments:
                    logger.info("No unfinalized tournaments found. Checking again in 1 hour.")
                    await asyncio.sleep(3600)  # Check every hour if no tournaments
                    continue
                
                # Process each unfinalized tournament
                for tournament_data in unfinalized_tournaments:
                    tournament_id = tournament_data[2]  # URL/ID field
                    
                    # Skip if already being monitored
                    if tournament_id in self.active_monitors:
                        continue
                    
                    logger.info(f"Found unfinalized tournament: {tournament_data[1]} (ID: {tournament_id})")
                    
                    # Create DB connections for the monitor
                    db_connections = {
                        "db": self.db,
                        "tournament": self.modif_tournament,
                        "participants": self.modif_participants,
                        "players": self.modif_players,
                        "matches": self.modif_matches,
                        "tournament_data": self.modif_tournament_data,
                        "top_cut": self.get_top_cut,
                        "leaderboard": self.leaderboard,
                        "region": self.region
                    }
                    
                    # Create and start monitor for this tournament
                    monitor = self.TournamentMonitor(self.config, db_connections, tournament_id)
                    self.active_monitors[tournament_id] = monitor
                    
                    # Start monitoring in a separate task
                    asyncio.create_task(self._run_monitor(tournament_id, monitor))
                
                # Wait before checking again
                await asyncio.sleep(600)  # Check for new tournaments every 10 minutes
                
            except Exception as e:
                logger.exception(f"Error in main service loop: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying
    
    async def _run_monitor(self, tournament_id, monitor):
        """Run a tournament monitor until completion"""
        try:
            # Start the monitor
            await monitor.start_monitoring()
            
            # Check if tournament is now finalized
            if self.modif_tournament.get_finalized_status(tournament_id) == 1:
                logger.info(f"Tournament {tournament_id} has been finalized.")
            else:
                logger.warning(f"Monitor for tournament {tournament_id} stopped without finalizing.")
                
        except Exception as e:
            logger.exception(f"Error monitoring tournament {tournament_id}: {e}")
        finally:
            # Clean up
            if tournament_id in self.active_monitors:
                del self.active_monitors[tournament_id]
    
    async def shutdown(self):
        """Gracefully shut down the service"""
        logger.info("Shutting down Tournament Service...")
        
        try:
            # Stop all active monitors
            shutdown_tasks = []
            for tournament_id, monitor in list(self.active_monitors.items()):
                logger.info(f"Stopping monitor for tournament {tournament_id}")
                # Just mark monitors to stop rather than waiting for them
                monitor.stop_monitor = True
                
            # Give monitors a moment to process the stop signal
            await asyncio.sleep(1)
            
            # Clear the active monitors dictionary
            self.active_monitors.clear()
            logger.info("Tournament Service shutdown complete")
        except Exception as e:
            logger.exception(f"Error during shutdown: {e}")
            # Ensure we still complete shutdown even with errors
            self.active_monitors.clear()
            logger.info("Tournament Service shutdown completed with errors")

async def main():
    """Main entry point for the service"""
    service = TournamentService()
    await service.start()

if __name__ == "__main__":
    asyncio.run(main())