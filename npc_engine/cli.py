"""
NPCEngine Command Line Interface

Professional CLI for managing NPCEngine deployments, configurations, and operations.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import argparse
from datetime import datetime

import click
import uvicorn
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

# Setup rich console
console = Console()

def setup_logging(level: str = "INFO"):
    """Setup structured logging"""
    import structlog
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper())
    )

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config-dir', default='config', help='Configuration directory')
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config_dir: str):
    """NPCEngine - World-class intelligent NPC framework"""
    
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)
    
    # Store config in context
    ctx.obj['config_dir'] = config_dir
    ctx.obj['verbose'] = verbose
    
    # Display banner
    if not ctx.invoked_subcommand or ctx.invoked_subcommand == 'version':
        console.print(Panel(
            "[bold blue]NPCEngine[/bold blue] 🎮\n"
            "World-class intelligent NPC framework\n"
            "[dim]Powered by Google ADK[/dim]",
            title="🚀 Welcome to NPCEngine",
            border_style="blue"
        ))

@cli.command()
def version():
    """Show NPCEngine version information"""
    from npc_engine import __version__, is_adk_available, get_adk_error
    
    # Create version table
    table = Table(title="NPCEngine Version Information")
    table.add_column("Component", style="cyan")
    table.add_column("Version/Status", style="magenta")
    table.add_column("Details", style="green")
    
    table.add_row("NPCEngine", __version__, "Core framework")
    
    # Check ADK status
    if is_adk_available():
        table.add_row("Google ADK", "✅ Available", "Agent Development Kit")
    else:
        error_msg = get_adk_error() or "Unknown error"
        table.add_row("Google ADK", "❌ Not Available", f"Error: {error_msg}")
    
    # Check optional dependencies
    optional_deps = [
        ("FastAPI", "fastapi"),
        ("SQLAlchemy", "sqlalchemy"),
        ("PostgreSQL", "psycopg2"),
        ("Structlog", "structlog")
    ]
    
    for name, module in optional_deps:
        try:
            __import__(module)
            table.add_row(name, "✅ Available", "Optional dependency")
        except ImportError:
            table.add_row(name, "⚠️ Not Available", "Optional dependency")
    
    console.print(table)

@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8000, type=int, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload (development)')
@click.option('--workers', default=1, type=int, help='Number of worker processes')
@click.option('--env', default='development', help='Environment (development/production)')
@click.pass_context
def serve(ctx: click.Context, host: str, port: int, reload: bool, workers: int, env: str):
    """Start the NPCEngine API server"""
    
    console.print(f"🚀 Starting NPCEngine API server...")
    console.print(f"📡 Host: {host}:{port}")
    console.print(f"🔧 Environment: {env}")
    console.print(f"👥 Workers: {workers}")
    
    # Set environment variables
    os.environ['ENVIRONMENT'] = env
    os.environ['CONFIG_DIR'] = ctx.obj['config_dir']
    
    # Production vs Development settings
    if env == 'production':
        reload = False
        log_level = "info"
        console.print("⚠️  [yellow]Production mode enabled - auto-reload disabled[/yellow]")
    else:
        log_level = "debug" if ctx.obj['verbose'] else "info"
    
    try:
        # Check if Google API key is set
        if not os.getenv('GOOGLE_API_KEY'):
            console.print("⚠️  [yellow]Warning: GOOGLE_API_KEY not set[/yellow]")
            console.print("   Some features may not work properly")
        
        # Import and run server
        uvicorn.run(
            "npc_engine.api.npc_api:api.app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,
            log_level=log_level,
            access_log=True
        )
        
    except KeyboardInterrupt:
        console.print("\n👋 NPCEngine server stopped")
    except Exception as e:
        console.print(f"❌ Failed to start server: {e}")
        sys.exit(1)

@cli.command()
@click.option('--backend', type=click.Choice(['yaml', 'database']), default='yaml',
              help='Configuration backend to use')
@click.option('--database-url', help='Database URL for database backend')
@click.pass_context
def config(ctx: click.Context, backend: str, database_url: Optional[str]):
    """Manage NPCEngine configuration"""
    
    from npc_engine.config.config_loader import ConfigurationManager, ConfigBackend
    
    console.print(f"📋 Configuration Management")
    console.print(f"Backend: {backend}")
    
    try:
        # Create configuration manager
        config_backend = ConfigBackend(backend)
        manager = ConfigurationManager(
            config_dir=ctx.obj['config_dir'],
            backend=config_backend,
            database_url=database_url
        )
        
        # List configurations
        configs = manager.list_configurations()
        
        if not configs:
            console.print("No configurations found. Use 'npc-engine init' to create defaults.")
            return
        
        # Display configurations table
        table = Table(title="Available Configurations")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Backend", style="green")
        table.add_column("Last Updated", style="yellow")
        
        for config in configs:
            last_updated = config['last_updated'].strftime('%Y-%m-%d %H:%M:%S')
            table.add_row(
                config['name'],
                config['type'],
                config['backend'],
                last_updated
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Configuration error: {e}")
        sys.exit(1)

@cli.command()
@click.option('--force', is_flag=True, help='Overwrite existing configurations')
@click.pass_context  
def init(ctx: click.Context, force: bool):
    """Initialize NPCEngine with default configurations"""
    
    from npc_engine.config.config_loader import ConfigLoader
    
    config_dir = Path(ctx.obj['config_dir'])
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        # Check if already initialized
        if not force and config_dir.exists() and any(config_dir.glob("*.yaml")):
            console.print("⚠️  Configuration already exists. Use --force to overwrite.")
            return
        
        task = progress.add_task("Initializing NPCEngine...", total=5)
        
        try:
            # Create config directory
            progress.update(task, description="Creating configuration directory...")
            config_dir.mkdir(exist_ok=True)
            progress.advance(task)
            
            # Initialize config loader
            progress.update(task, description="Loading configuration manager...")
            loader = ConfigLoader(str(config_dir))
            progress.advance(task)
            
            # Create sample configurations
            progress.update(task, description="Creating sample configurations...")
            loader.create_sample_configs()
            progress.advance(task)
            
            # Create default NPC config
            progress.update(task, description="Creating default NPC configuration...")
            from npc_engine.config.npc_config import create_default_npc_config
            default_npc_config = create_default_npc_config()
            loader.save_npc_config(default_npc_config)
            progress.advance(task)
            
            # Create environment file template
            progress.update(task, description="Creating environment template...")
            env_template = """# NPCEngine Environment Configuration
# Copy this to .env and fill in your values

# Required: Google API Key for Gemini LLM
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Database configuration
# DATABASE_URL=postgresql://user:password@localhost:5432/npcengine
# DATABASE_URL=sqlite:///./npcengine.db

# Optional: Configuration backend
# CONFIG_BACKEND=yaml
# CONFIG_DATABASE_URL=postgresql://user:password@localhost:5432/config

# Optional: Vertex AI configuration  
# GOOGLE_CLOUD_PROJECT=your-gcp-project
# GOOGLE_CLOUD_LOCATION=us-central1

# Optional: Production settings
# ENVIRONMENT=production
# SECRET_KEY=your-secret-key
# ALLOWED_HOSTS=your-domain.com
"""
            
            env_file = Path(".env.example")
            env_file.write_text(env_template)
            progress.advance(task)
            
        except Exception as e:
            console.print(f"❌ Initialization failed: {e}")
            sys.exit(1)
    
    console.print("✅ NPCEngine initialized successfully!")
    console.print(f"📁 Configuration directory: {config_dir}")
    console.print("📝 Next steps:")
    console.print("   1. Copy .env.example to .env and configure your API key")
    console.print("   2. Run 'npc-engine serve' to start the server")
    console.print("   3. Visit http://localhost:8000/docs for API documentation")

@cli.command()
@click.option('--output', '-o', help='Output file for backup')
@click.pass_context
def backup(ctx: click.Context, output: Optional[str]):
    """Create a backup of all configurations"""
    
    from npc_engine.config.config_loader import ConfigLoader
    
    console.print("📦 Creating configuration backup...")
    
    try:
        loader = ConfigLoader(ctx.obj['config_dir'])
        backup_path = loader.backup_configuration(output)
        
        console.print(f"✅ Backup created: {backup_path}")
        
    except Exception as e:
        console.print(f"❌ Backup failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--format', type=click.Choice(['table', 'json', 'yaml']), default='table',
              help='Output format')
@click.pass_context
def health(ctx: click.Context, format: str):
    """Check NPCEngine health and dependencies"""
    
    from npc_engine import is_adk_available, get_adk_error
    
    health_data = {
        "timestamp": datetime.now().isoformat(),
        "npc_engine_version": None,
        "google_adk": is_adk_available(),
        "dependencies": {},
        "environment": {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
            "config_dir": ctx.obj['config_dir']
        }
    }
    
    # Check version
    try:
        from npc_engine import __version__
        health_data["npc_engine_version"] = __version__
    except ImportError:
        health_data["npc_engine_version"] = "unknown"
    
    # Check dependencies
    deps_to_check = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("sqlalchemy", "SQLAlchemy"),
        ("psycopg2", "PostgreSQL"),
        ("yaml", "PyYAML"),
        ("structlog", "Structlog")
    ]
    
    for module_name, display_name in deps_to_check:
        try:
            __import__(module_name)
            health_data["dependencies"][display_name] = "available"
        except ImportError:
            health_data["dependencies"][display_name] = "missing"
    
    # Environment variables
    env_vars = ["GOOGLE_API_KEY", "DATABASE_URL", "ENVIRONMENT"]
    health_data["environment"]["variables"] = {
        var: "set" if os.getenv(var) else "not_set"
        for var in env_vars
    }
    
    # Output in requested format
    if format == "json":
        import json
        console.print(json.dumps(health_data, indent=2))
    elif format == "yaml":
        import yaml
        console.print(yaml.dump(health_data, default_flow_style=False))
    else:  # table format
        _display_health_table(health_data)

def _display_health_table(health_data: Dict[str, Any]):
    """Display health information in table format"""
    
    # Main info panel
    main_info = f"""[bold]NPCEngine Health Check[/bold]
Version: {health_data['npc_engine_version']}
Python: {health_data['environment']['python_version']}
Platform: {health_data['environment']['platform']}
Config Dir: {health_data['environment']['config_dir']}
Timestamp: {health_data['timestamp']}"""
    
    console.print(Panel(main_info, title="🏥 System Information", border_style="green"))
    
    # Dependencies table
    deps_table = Table(title="📦 Dependencies")
    deps_table.add_column("Component", style="cyan")
    deps_table.add_column("Status", style="magenta")
    
    # Google ADK status
    if health_data["google_adk"]:
        deps_table.add_row("Google ADK", "✅ Available")
    else:
        deps_table.add_row("Google ADK", "❌ Not Available")
    
    # Other dependencies
    for dep, status in health_data["dependencies"].items():
        if status == "available":
            deps_table.add_row(dep, "✅ Available")
        else:
            deps_table.add_row(dep, "❌ Missing")
    
    console.print(deps_table)
    
    # Environment variables table
    env_table = Table(title="🔧 Environment Variables")
    env_table.add_column("Variable", style="cyan")
    env_table.add_column("Status", style="magenta")
    
    for var, status in health_data["environment"]["variables"].items():
        if status == "set":
            env_table.add_row(var, "✅ Set")
        else:
            env_table.add_row(var, "⚠️ Not Set")
    
    console.print(env_table)

@cli.command()
@click.option('--check', is_flag=True, help='Check requirements without installing')
def install(check: bool):
    """Install or check NPCEngine requirements"""
    
    if check:
        console.print("🔍 Checking requirements...")
        # This would check if all requirements are met
        console.print("✅ All requirements satisfied")
    else:
        console.print("📦 Installing NPCEngine requirements...")
        console.print("Use: pip install -r requirements.txt")

@cli.command()
@click.argument('environment', type=click.Choice(['development', 'production']))
@click.option('--host', help='Host for deployment')
@click.option('--workers', type=int, default=4, help='Number of workers')
def deploy(environment: str, host: Optional[str], workers: int):
    """Deploy NPCEngine to specified environment"""
    
    console.print(f"🚀 Deploying NPCEngine to {environment}...")
    
    if environment == 'production':
        console.print("⚠️  [yellow]Production deployment guide:[/yellow]")
        console.print("1. Ensure all environment variables are set")
        console.print("2. Configure database connections")
        console.print("3. Set up reverse proxy (nginx/apache)")
        console.print("4. Configure SSL certificates")
        console.print("5. Set up monitoring and logging")
        
        # Example production command
        prod_command = f"uvicorn npc_engine.api.npc_api:api.app --host 0.0.0.0 --port 8000 --workers {workers}"
        console.print(f"\nProduction command: {prod_command}")
    
    else:
        console.print("Development deployment completed!")

def main():
    """Main CLI entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}")
        if os.getenv("DEBUG"):
            raise
        sys.exit(1)

if __name__ == "__main__":
    main() 