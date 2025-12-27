"""Archive manager for organizing output files."""

import shutil
from pathlib import Path
from datetime import datetime
import logging

class ArchiveManager:
    """Manages archiving of old analysis runs."""
    
    def __init__(self, outputs_dir: str = "outputs"):
        self.outputs_dir = Path(outputs_dir)
        self.reports_dir = self.outputs_dir / "reports"
        self.viz_dir = self.outputs_dir / "visualizations"
        self.archives_dir = self.outputs_dir / "archives"
        self.logger = logging.getLogger('ArchiveManager')
        
        # Ensure directories exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.viz_dir.mkdir(parents=True, exist_ok=True)
        self.archives_dir.mkdir(parents=True, exist_ok=True)
    
    def archive_previous_run(self, run_timestamp: str = None):
        """
        Move all existing output files to a timestamped archive folder.
        
        Args:
            run_timestamp: Timestamp for the archive folder name (optional)
        """
        # Generate timestamp for archive folder if not provided
        if run_timestamp is None:
            run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        archive_folder = self.archives_dir / f"run_{run_timestamp}"
        
        # Check if there are any files to archive
        reports = list(self.reports_dir.glob("*.json"))
        visualizations = list(self.viz_dir.glob("*.png"))
        
        if not reports and not visualizations:
            self.logger.info("No previous files to archive")
            return None
        
        # Create archive folder structure
        archive_folder.mkdir(parents=True, exist_ok=True)
        archive_reports = archive_folder / "reports"
        archive_viz = archive_folder / "visualizations"
        archive_reports.mkdir(exist_ok=True)
        archive_viz.mkdir(exist_ok=True)
        
        # Move reports
        moved_count = 0
        for report_file in reports:
            dest = archive_reports / report_file.name
            shutil.move(str(report_file), str(dest))
            moved_count += 1
            self.logger.debug(f"Archived: {report_file.name}")
        
        # Move visualizations
        for viz_file in visualizations:
            dest = archive_viz / viz_file.name
            shutil.move(str(viz_file), str(dest))
            moved_count += 1
            self.logger.debug(f"Archived: {viz_file.name}")
        
        self.logger.info(f"✅ Archived {moved_count} files to {archive_folder}")
        return archive_folder
    
    def clean_old_archives(self, keep_last_n: int = 10):
        """
        Keep only the last N archive runs, delete older ones.
        
        Args:
            keep_last_n: Number of recent archives to keep
        """
        archive_runs = sorted(self.archives_dir.glob("run_*"))
        
        if len(archive_runs) <= keep_last_n:
            self.logger.info(f"Have {len(archive_runs)} archives, keeping all (limit: {keep_last_n})")
            return
        
        # Delete old archives
        to_delete = archive_runs[:-keep_last_n]
        for old_archive in to_delete:
            shutil.rmtree(old_archive)
            self.logger.info(f"Deleted old archive: {old_archive.name}")
        
        self.logger.info(f"Cleaned archives: kept {keep_last_n} most recent runs")
    
    def list_archives(self):
        """List all archived runs."""
        archives = sorted(self.archives_dir.glob("run_*"))
        return [archive.name for archive in archives]
    
    def get_archive_info(self, archive_name: str):
        """Get information about a specific archive."""
        archive_path = self.archives_dir / archive_name
        
        if not archive_path.exists():
            return None
        
        reports = list((archive_path / "reports").glob("*.json"))
        viz = list((archive_path / "visualizations").glob("*.png"))
        
        return {
            "name": archive_name,
            "path": str(archive_path),
            "reports_count": len(reports),
            "visualizations_count": len(viz),
            "total_files": len(reports) + len(viz)
        }