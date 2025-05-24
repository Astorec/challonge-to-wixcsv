import asyncio
import argparse
import logging
import utils.misc as misc
from tournament_monitor import TournamentMonitor
from tournament_service import TournamentService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tournament.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('main')

async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Tournament Tracker Service')
    parser.add_argument('--service', action='store_true', help='Run as a continuous service')
    parser.add_argument('--url', help='Process a specific tournament URL')
    parser.add_argument('--config', default='config/config.json', help='Path to config file')
    args = parser.parse_args()
    
    # Check if we are running in development mode

    if not args.service:
        # Run as a continuous service monitoring all unfinalized tournaments
        logger.info("Starting Tournament Tracker in service mode")
        service = TournamentService(args.config)
        await service.start()
    elif args.url:
        # Process a single tournament
        logger.info(f"Processing single tournament: {args.url}")
        
        # Import necessary modules for single tournament processing
        import json
        import os
        import utils.db_operations.initDB as initDB
        import utils.db_operations.tournament as tournament
        import utils.db_operations.tournamentData as tournamentData
        import utils.db_operations.participants as participants
        import utils.db_operations.player as players
        import utils.db_operations.matches as matches
        import utils.db_operations.top_cut as top_cut
        import utils.db_operations.leaderboard as leaderboard
        import utils.db_operations.region as region
        
        # Load configuration
        if os.path.exists(args.config):
            with open(args.config) as f:
                config = json.load(f)
        else:
            logger.error(f"Config file not found at {args.config}")
            return
            
        # Initialize DB
        db = initDB.initDB(args.config).get_connection()
        
        # Create DB connections
        db_connections = {
            "db": db,
            "tournament": tournament.tournament(db),
            "participants": participants.participants(db),
            "players": players.player(db),
            "matches": matches.matches(db),
            "tournament_data": tournamentData.tournamentData(db),
            "top_cut": top_cut.top_cut(db),
            "leaderboard": leaderboard.leaderboard(db),
            "region": region.region(db)
        }
        
        # Extract tournament ID from URL if needed
        tournament_id = misc.extract_tournament_id(args.url)
        
        # Create and start monitor for this tournament
        monitor = TournamentMonitor(config, db_connections, tournament_id)
        await monitor.start_monitoring()
        
    else:
        logger.error("Either --service or --url must be specified")
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())