"""
Web API module for SFTP Sync
Provides FastAPI endpoints for web management interface
"""

import os
import logging
import json
import paramiko
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .config import Config
from .syncer import SFTPSyncer

logger = logging.getLogger(__name__)


# Pydantic models for API requests/responses
class SyncConfigModel(BaseModel):
    """Sync configuration model"""
    host: str = Field(..., description="Remote host")
    port: int = Field(22, description="SSH port")
    username: str = Field(..., description="SSH username")
    password: Optional[str] = Field(None, description="SSH password")
    private_key: Optional[str] = Field(None, description="Path to private key")
    private_key_password: Optional[str] = Field(None, description="Private key password")
    local_dir: str = Field(".", description="Local directory")
    remote_dir: str = Field(".", description="Remote directory")
    include_patterns: List[str] = Field(["*"], description="Include patterns")
    exclude_patterns: List[str] = Field([], description="Exclude patterns")
    delete_remote: bool = Field(False, description="Delete remote files")
    preserve_permissions: bool = Field(True, description="Preserve permissions")
    auto_add_host_key: bool = Field(False, description="Auto add host key")
    dry_run: bool = Field(False, description="Dry run mode")
    verbose: bool = Field(False, description="Verbose mode")
    follow_symlinks: bool = Field(False, description="Follow symlinks")
    backup_remote: bool = Field(False, description="Backup remote files")


class SyncResponse(BaseModel):
    """Sync operation response"""
    task_id: str
    status: str
    message: str


class SyncStatus(BaseModel):
    """Sync status model"""
    task_id: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    stats: Optional[Dict] = None
    error: Optional[str] = None


class ConfigFile(BaseModel):
    """Configuration file model"""
    name: str
    path: str
    modified_at: str


# Global task storage (in production, use a database)
sync_tasks: Dict[str, SyncStatus] = {}
config_storage_dir = os.path.expanduser("~/.sftp_sync/configs")


def ensure_config_dir():
    """Ensure configuration directory exists"""
    os.makedirs(config_storage_dir, exist_ok=True)


# Create FastAPI app
app = FastAPI(
    title="SFTP Sync Web API",
    description="Web API for SFTP synchronization management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api")
async def root():
    """API root endpoint"""
    return {
        "name": "SFTP Sync Web API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/sync/start", response_model=SyncResponse)
async def start_sync(config: SyncConfigModel, background_tasks: BackgroundTasks):
    """
    Start a synchronization task
    """
    # Generate task ID
    task_id = f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create sync status
    sync_tasks[task_id] = SyncStatus(
        task_id=task_id,
        status="pending",
        started_at=datetime.now().isoformat()
    )
    
    # Run sync in background
    background_tasks.add_task(run_sync_task, task_id, config)
    
    return SyncResponse(
        task_id=task_id,
        status="started",
        message="Sync task started successfully"
    )


def run_sync_task(task_id: str, config_model: SyncConfigModel):
    """
    Run synchronization task in background
    """
    try:
        # Update status to running
        sync_tasks[task_id].status = "running"
        
        # Create config object
        config = Config(config_model.model_dump())
        
        # Validate config
        errors = config.validate()
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        # Create syncer and run sync
        syncer = SFTPSyncer(config)
        syncer.sync()
        
        # Update status to completed
        sync_tasks[task_id].status = "completed"
        sync_tasks[task_id].completed_at = datetime.now().isoformat()
        sync_tasks[task_id].stats = syncer.stats
        
    except Exception as e:
        logger.error(f"Sync task {task_id} failed: {e}")
        sync_tasks[task_id].status = "failed"
        sync_tasks[task_id].completed_at = datetime.now().isoformat()
        sync_tasks[task_id].error = str(e)


@app.get("/api/sync/status/{task_id}", response_model=SyncStatus)
async def get_sync_status(task_id: str):
    """
    Get status of a sync task
    """
    if task_id not in sync_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return sync_tasks[task_id]


@app.get("/api/sync/tasks", response_model=List[SyncStatus])
async def list_sync_tasks():
    """
    List all sync tasks
    """
    return list(sync_tasks.values())


@app.post("/api/config/save")
async def save_config(name: str, config: SyncConfigModel):
    """
    Save a configuration file
    """
    ensure_config_dir()
    
    # Sanitize filename
    safe_name = "".join(c for c in name if c.isalnum() or c in "._- ")
    config_path = os.path.join(config_storage_dir, f"{safe_name}.json")
    
    try:
        with open(config_path, "w") as f:
            json.dump(config.model_dump(), f, indent=2)
        
        return {
            "status": "success",
            "message": f"Configuration '{name}' saved successfully",
            "path": config_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config/load/{name}")
async def load_config(name: str):
    """
    Load a configuration file
    """
    ensure_config_dir()
    
    safe_name = "".join(c for c in name if c.isalnum() or c in "._- ")
    config_path = os.path.join(config_storage_dir, f"{safe_name}.json")
    
    if not os.path.exists(config_path):
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    try:
        with open(config_path, "r") as f:
            config_data = json.load(f)
        return config_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config/list", response_model=List[ConfigFile])
async def list_configs():
    """
    List all saved configuration files
    """
    ensure_config_dir()
    
    configs = []
    for filename in os.listdir(config_storage_dir):
        if filename.endswith(".json"):
            config_path = os.path.join(config_storage_dir, filename)
            stat_info = os.stat(config_path)
            configs.append(ConfigFile(
                name=filename[:-5],  # Remove .json extension
                path=config_path,
                modified_at=datetime.fromtimestamp(stat_info.st_mtime).isoformat()
            ))
    
    return configs


@app.delete("/api/config/delete/{name}")
async def delete_config(name: str):
    """
    Delete a configuration file
    """
    ensure_config_dir()
    
    safe_name = "".join(c for c in name if c.isalnum() or c in "._- ")
    config_path = os.path.join(config_storage_dir, f"{safe_name}.json")
    
    if not os.path.exists(config_path):
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    try:
        os.remove(config_path)
        return {
            "status": "success",
            "message": f"Configuration '{name}' deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/test-connection")
async def test_connection(
    host: str,
    port: int = 22,
    username: str = "",
    password: Optional[str] = None,
    private_key: Optional[str] = None
):
    """
    Test SFTP connection
    Note: Requires host key to be in known_hosts for security.
    Add host key with: ssh-keyscan -H <host> >> ~/.ssh/known_hosts
    """
    try:
        ssh_client = paramiko.SSHClient()
        
        # Load system host keys for verification
        try:
            ssh_client.load_system_host_keys()
            known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")
            if os.path.exists(known_hosts_path):
                ssh_client.load_host_keys(known_hosts_path)
        except Exception:
            pass
        
        # Use RejectPolicy for security - requires host key to be known
        # Users must add host keys manually using ssh-keyscan
        ssh_client.set_missing_host_key_policy(paramiko.RejectPolicy())
        
        # Connect
        if private_key:
            ssh_client.connect(
                hostname=host,
                port=port,
                username=username,
                key_filename=private_key,
                timeout=10
            )
        else:
            ssh_client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=10
            )
        
        # Test SFTP
        sftp = ssh_client.open_sftp()
        sftp.close()
        ssh_client.close()
        
        return {
            "status": "success",
            "message": "Connection successful"
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": str(e)
        }


# Mount static files for production
# Get the path to the web-ui/dist directory
static_dir = os.path.join(os.path.dirname(__file__), "..", "web-ui", "dist")

if os.path.exists(static_dir):
    # Serve static files from the dist directory
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        Serve the Vue.js SPA
        Serves index.html for all non-API routes to support Vue Router
        """
        # Don't intercept API routes, docs, or openapi.json
        if full_path.startswith("api") or full_path in ["docs", "redoc", "openapi.json"]:
            raise HTTPException(status_code=404, detail="Not found")
        
        # Try to serve the requested file
        file_path = os.path.join(static_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Fall back to index.html for SPA routing
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        
        raise HTTPException(status_code=404, detail="Not found")
else:
    logger.warning(f"Static files directory not found: {static_dir}")
    logger.warning("Web UI will not be available. Run 'npm run build' in web-ui directory.")
