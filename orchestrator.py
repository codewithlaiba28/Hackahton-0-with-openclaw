#!/usr/bin/env python3
"""
Orchestrator - Manages AI Employee system and watchers.
"""

import time
import logging
import json
from pathlib import Path
from datetime import datetime
import subprocess
import sys
import os # For checking file existence

class Orchestrator:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.setup_directories()
        self.setup_logging()
        
        self.watchers = {}
        self.start_watchers()
        
    def setup_directories(self):
        """Create required directory structure"""
        directories = ['Inbox', 'Needs_Action', 'Done', 'Plans', 'Pending_Approval', 'Approved', 'Rejected', 'Logs']
        for directory in directories:
            (self.vault_path / directory).mkdir(exist_ok=True)
            self.logger.info(f"Ensured directory exists: {directory}")
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = self.vault_path / 'Logs'
        log_file = log_dir / f"orchestrator_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger.info(f"Logging initialized: {log_file}")
    
    def start_watchers(self):
        """Start all watcher processes"""
        watchers_config = [
            {
                'name': 'gmail_watcher',
                'script': 'simple_gmail_watcher.py',
                'description': 'Gmail email monitoring'
            },
            {
                'name': 'filesystem_watcher', 
                'script': 'filesystem_watcher.py',
                'description': 'File system monitoring'
            }
        ]
        
        for watcher_config in watchers_config:
            script_path = self.vault_path / watcher_config['script']
            if not script_path.exists():
                self.logger.error(f"Script not found for {watcher_config['name']}: {watcher_config['script']}")
                continue

            try:
                process = subprocess.Popen(
                    [sys.executable, str(script_path)],
                    cwd=self.vault_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.watchers[watcher_config['name']] = {
                    'process': process,
                    'config': watcher_config,
                    'started': datetime.now()
                }
                self.logger.info(f"Started {watcher_config['description']}: PID {process.pid}")
            except Exception as e:
                self.logger.error(f"Failed to start {watcher_config['name']}: {e}")
    
    def check_needs_action(self):
        """Check for items in Needs_Action folder"""
        needs_action_dir = self.vault_path / 'Needs_Action'
        if not needs_action_dir.exists(): return []
        action_files = list(needs_action_dir.glob("*.md"))
        return action_files
    
    def update_dashboard(self):
        """Update the Dashboard.md with current status"""
        dashboard_path = self.vault_path / 'Dashboard.md'
        needs_action_count = len(list((self.vault_path / 'Needs_Action').glob("*.md")))
        done_count = len(list((self.vault_path / 'Done').glob("*.md")))
        
        recent_files = []
        if needs_action_count > 0:
            action_files = sorted((self.vault_path / 'Needs_Action').glob("*.md"), 
                                key=lambda x: x.stat().st_mtime, reverse=True)
            recent_files = [f.name for f in action_files[:3]]
        
        dashboard_content = f"""---
last_updated: {datetime.now().isoformat()}
status: active
---

## Personal AI Employee Dashboard

### Overview
Your AI Employee is running and monitoring your digital life.

### Recent Activity
"""
        
        if recent_files:
            dashboard_content += "Latest items to process:\n"
            for file in recent_files:
                dashboard_content += f"- {file}\n"
        else:
            dashboard_content += "- No recent activity\n"
        
        # Check if filesystem_watcher.py exists to determine its status
        fs_watcher_exists = (self.vault_path / 'filesystem_watcher.py').exists()
        fs_watcher_status = "Active" if fs_watcher_exists else "Not Found"
        # More robust check would involve checking if the process is running

        dashboard_content += f"""

### System Status
- **Gmail Watcher**: {'Active' if 'gmail_watcher' in self.watchers and self.watchers['gmail_watcher']['process'].poll() is None else 'Inactive'}
- **File System Watcher**: {fs_watcher_status}
- **Claude Code**: Ready

### Quick Stats
- Pending Items: {needs_action_count}
- Completed Today: {done_count}
- Active Projects: 0

### Next Review
- Daily check at 8:00 AM
- Weekly audit on Sunday

---
*Generated by AI Employee v0.1*
"""
        
        dashboard_path.write_text(dashboard_content)
        self.logger.info("Dashboard updated")
    
    def monitor_system(self):
        """Main monitoring loop"""
        self.logger.info("Starting system monitoring")
        
        while True:
            try:
                self.update_dashboard()
                self.check_watchers()
                
                action_files = self.check_needs_action()
                if action_files:
                    self.logger.info(f"Found {len(action_files)} items needing processing")
                
                time.sleep(300) # Sleep for 5 minutes
                
            except KeyboardInterrupt:
                self.logger.info("Received shutdown signal")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60) # Wait before retrying
    
    def check_watchers(self):
        """Check if watchers are still running and restart if necessary"""
        for watcher_name, watcher_info in self.watchers.items():
            if watcher_info['process'].poll() is not None: # Process has exited
                self.logger.warning(f"Watcher {watcher_name} has stopped, attempting to restart...")
                self.restart_watcher(watcher_name)
    
    def restart_watcher(self, watcher_name):
        """Restart a failed watcher"""
        if watcher_name in self.watchers:
            try:
                old_process = self.watchers[watcher_name]['process']
                if old_process.poll() is None: # If it's still running (shouldn't happen often here)
                    old_process.terminate()
                
                script = self.watchers[watcher_name]['config']['script']
                script_path = self.vault_path / script
                
                new_process = subprocess.Popen(
                    [sys.executable, str(script_path)],
                    cwd=self.vault_path,
                    stdout=subprocess.PIPE, # Capture output
                    stderr=subprocess.PIPE  # Capture errors
                )
                self.watchers[watcher_name]['process'] = new_process
                self.watchers[watcher_name]['started'] = datetime.now()
                self.logger.info(f"Restarted {watcher_name}: PID {new_process.pid}")
                
            except FileNotFoundError:
                self.logger.error(f"Script not found for {watcher_name} during restart: {script}")
            except Exception as e:
                self.logger.error(f"Failed to restart {watcher_name}: {e}")
    
    def shutdown(self):
        """Gracefully shutdown the system"""
        self.logger.info("Shutting down orchestrator...")
        for watcher_name, watcher_info in self.watchers.items():
            try:
                if watcher_info['process'].poll() is None: # If process is still running
                    watcher_info['process'].terminate()
                    self.logger.info(f"Terminated {watcher_name} (PID: {watcher_info['process'].pid})")
            except Exception as e:
                self.logger.error(f"Error stopping {watcher_name}: {e}")
        self.logger.info("Shutdown complete.")

def main():
    """Main entry point"""
    vault_path = "."
    
    # Configure basic logging for the orchestrator itself
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger("OrchestratorMain")
    logger.info("Starting AI Employee Orchestrator")
    
    orchestrator = Orchestrator(vault_path)
    
    try:
        orchestrator.monitor_system()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down.")
    finally:
        orchestrator.shutdown()

if __name__ == "__main__":
    main()