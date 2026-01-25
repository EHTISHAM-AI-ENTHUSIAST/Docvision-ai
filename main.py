"""
Document Vision AI - Main CLI Entry Point

A command-line tool for extracting structured data from documents
using OpenAI's Vision API.

Usage:
    python main.py --input invoice.pdf --output results/
    python main.py --input documents/ --output results/ --batch

Author: Ehtisham Ashraf
Email: kingehtsham0@gmail.com
"""

import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

from extractor import DocumentExtractor
from utils.export import export_to_excel, export_to_json


# Initialize CLI app and console
app = typer.Typer(
    name="docvision",
    help="Extract structured data from documents using AI Vision"
)
console = Console()


def validate_input_path(path: str) -> Path:
    """Validate that input path exists."""
    input_path = Path(path)
    if not input_path.exists():
        console.print(f"[red]Error:[/red] Input path '{path}' does not exist")
        raise typer.Exit(code=1)
    return input_path


def get_supported_files(path: Path) -> list:
    """Get list of supported document files from path."""
    supported_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.webp', '.gif'}
    
    if path.is_file():
        if path.suffix.lower() in supported_extensions:
            return [path]
        else:
            console.print(f"[yellow]Warning:[/yellow] Unsupported file type: {path.suffix}")
            return []
    
    # If directory, find all supported files
    files = []
    for ext in supported_extensions:
        files.extend(path.glob(f"*{ext}"))
        files.extend(path.glob(f"*{ext.upper()}"))
    
    return sorted(files)


def display_results_table(results: list):
    """Display extracted data in a formatted table."""
    if not results:
        console.print("[yellow]No data extracted[/yellow]")
        return
    
    table = Table(title="Extracted Document Data", show_header=True)
    
    # Add columns based on first result
    first_result = results[0]
    for key in first_result.keys():
        if key != 'line_items':  # Skip nested data for display
            table.add_column(key.replace('_', ' ').title())
    
    # Add rows
    for result in results:
        row = []
        for key in first_result.keys():
            if key != 'line_items':
                value = result.get(key, 'N/A')
                if isinstance(value, (int, float)):
                    row.append(f"${value:,.2f}" if 'amount' in key else str(value))
                else:
                    row.append(str(value) if value else 'N/A')
        table.add_row(*row)
    
    console.print(table)


@app.command()
def extract(
    input_path: str = typer.Argument(
        ...,
        help="Path to document file or directory containing documents"
    ),
    output_dir: str = typer.Option(
        "./output",
        "--output", "-o",
        help="Output directory for exported files"
    ),
    document_type: str = typer.Option(
        "auto",
        "--type", "-t",
        help="Document type: invoice, receipt, salary_slip, or auto"
    ),
    export_format: str = typer.Option(
        "excel",
        "--format", "-f",
        help="Export format: excel, json, or both"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show detailed extraction information"
    )
):
    """
    Extract structured data from documents using AI Vision.
    
    Supports invoices, receipts, salary slips, and other documents.
    Automatically detects document type if not specified.
    """
    # Print header
    console.print(Panel.fit(
        "[bold cyan]Document Vision AI[/bold cyan]\n"
        "Intelligent Document Data Extraction",
        border_style="cyan"
    ))
    
    # Validate input
    input_path = validate_input_path(input_path)
    files = get_supported_files(input_path)
    
    if not files:
        console.print("[red]No supported documents found[/red]")
        raise typer.Exit(code=1)
    
    console.print(f"\n[green]Found {len(files)} document(s) to process[/green]\n")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize extractor
    try:
        extractor = DocumentExtractor()
    except ValueError as e:
        console.print(f"[red]Configuration Error:[/red] {str(e)}")
        console.print("[yellow]Tip:[/yellow] Make sure OPENAI_API_KEY is set in .env file")
        raise typer.Exit(code=1)
    
    # Process documents
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Processing documents...", total=len(files))
        
        for file in files:
            progress.update(task, description=f"Processing: {file.name}")
            
            try:
                # Extract data from document
                doc_type = None if document_type == "auto" else document_type
                data = extractor.extract(str(file), document_type=doc_type)
                
                if data:
                    data['source_file'] = file.name
                    results.append(data)
                    
                    if verbose:
                        console.print(f"  [green]✓[/green] {file.name}: Extracted successfully")
                else:
                    if verbose:
                        console.print(f"  [yellow]⚠[/yellow] {file.name}: No data extracted")
                        
            except Exception as e:
                console.print(f"  [red]✗[/red] {file.name}: {str(e)}")
            
            progress.advance(task)
    
    # Display results
    console.print("\n")
    display_results_table(results)
    
    # Export results
    if results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if export_format in ("excel", "both"):
            excel_file = output_path / f"extracted_data_{timestamp}.xlsx"
            export_to_excel(results, str(excel_file))
            console.print(f"\n[green]✓[/green] Exported to: {excel_file}")
        
        if export_format in ("json", "both"):
            json_file = output_path / f"extracted_data_{timestamp}.json"
            export_to_json(results, str(json_file))
            console.print(f"[green]✓[/green] Exported to: {json_file}")
    
    # Summary
    console.print(Panel.fit(
        f"[bold]Summary[/bold]\n"
        f"Documents Processed: {len(files)}\n"
        f"Successful Extractions: {len(results)}\n"
        f"Failed: {len(files) - len(results)}",
        border_style="green" if len(results) == len(files) else "yellow"
    ))


@app.command()
def test():
    """Test the extractor with a sample document."""
    console.print("[cyan]Running extraction test...[/cyan]\n")
    
    # Check for API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Error:[/red] OPENAI_API_KEY not found in environment")
        console.print("[yellow]Tip:[/yellow] Copy .env.example to .env and add your API key")
        raise typer.Exit(code=1)
    
    console.print("[green]✓[/green] API key configured")
    console.print("[green]✓[/green] Ready to extract documents\n")
    console.print("Run: [cyan]python main.py extract <file_or_folder>[/cyan]")


if __name__ == "__main__":
    app()
