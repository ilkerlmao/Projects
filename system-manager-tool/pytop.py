#!/usr/bin/env python3
"""
pytop.py - Advanced Python Terminal System Monitor & Process Manager
Built with Textual & psutil.
"""

from typing import List, Dict, Any
import psutil
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, DataTable, Input, Button, ProgressBar
from textual.binding import Binding
from textual import on


class SystemStatsWidget(Static):
    """Widget displaying global CPU threads and Memory/Swap metrics."""

    def compose(self) -> ComposeResult:
        yield Static("[bold cyan]CPU Core Utilization[/bold cyan]", id="cpu_title")
        yield Vertical(id="cpu_bars_container")
        yield Static("\n[bold cyan]Memory & Swap[/bold cyan]", id="mem_title")
        yield Static("RAM Usage:", classes="stat_label")
        yield ProgressBar(total=100, show_percentage=True, id="ram_bar")
        yield Static("SWAP Usage:", classes="stat_label")
        yield ProgressBar(total=100, show_percentage=True, id="swap_bar")

    def on_mount(self) -> None:
        # Dynamically create progress bars for each CPU thread
        num_cpus = psutil.cpu_count(logical=True) or 1
        container = self.query_one("#cpu_bars_container", Vertical)
        for i in range(num_cpus):
            container.mount(Static(f"CPU {i}:", classes="stat_label"))
            container.mount(ProgressBar(total=100, show_percentage=True, id=f"cpu_bar_{i}"))

    def update_statsq(self) -> None:
        # Update CPU per-core usage
        per_cpu = psutil.cpu_percent(percpu=True)
        for i, val in enumerate(per_cpu):
            try:
                bar = self.query_one(f"#cpu_bar_{i}", ProgressBar)
                bar.progress = val
            except Exception:
                pass

        # Update Memory
        mem = psutil.virtual_memory()
        ram_bar = self.query_one("#ram_bar", ProgressBar)
        ram_bar.progress = mem.percent

        # Update Swap
        swap = psutil.swap_memory()
        swap_bar = self.query_one("#swap_bar", ProgressBar)
        swap_bar.progress = swap.percent


class PyTopApp(App):
    """Advanced Terminal Process Monitor Application."""

    CSS = """
    Screen {
        layout: horizontal;
    }
    #left_panel {
        width: 35%;
        height: 100%;
        border-right: heavy $accent;
        padding: 1;
    }
    #right_panel {
        width: 65%;
        height: 100%;
        padding: 1;
    }
    .stat_label {
        margin-top: 1;
        color: $text-muted;
    }
    #controls_container {
        height: auto;
        margin-bottom: 1;
    }
    #process_table {
        height: 1fr;
    }
    ProgressBar {
        padding: 0;
    }
    """

    TITLE = "PyTop System Monitor"
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh_data", "Force Refresh", show=True),
        Binding("k", "kill_process", "SIGTERM Process", show=True),
        Binding("K", "force_kill_process", "SIGKILL Process", show=True),
        Binding("f", "focus_filter", "Filter Processes", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with VerticalScroll(id="left_panel"):
                yield SystemStatsWidget(id="stats_widget")
            with Vertical(id="right_panel"):
                with Horizontal(id="controls_container"):
                    yield Input(placeholder="Filter processes by name... (Press 'f' to focus)", id="filter_input")
                    yield Button("Kill (SIGTERM)", id="btn_kill", variant="warning")
                    yield Button("Kill (SIGKILL)", id="btn_fkill", variant="error")
                yield DataTable(id="process_table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#process_table", DataTable)
        table.cursor_type = "row"
        table.add_columns("PID", "Name", "User", "CPU %", "MEM %", "Status")

        # Set up recurring timer to update system metrics every 1.5 seconds
        self.set_interval(1.5, self.refresh_data)
        self.refresh_data()

    def get_processes(self) -> List[Dict[str, Any]]:
        filter_text = self.query_one("#filter_input", Input).value.lower().strip()
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                name = pinfo['name'] or ""
                if filter_text and filter_text not in name.lower():
                    continue
                processes.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # Sort by CPU utilization descending
        return sorted(processes, key=lambda x: x['cpu_percent'] or 0.0, reverse=True)

    def refresh_data(self) -> None:
        # Update metrics sidebar
        stats_widget = self.query_one("#stats_widget", SystemStatsWidget)
        stats_widget.update_stats()

        # Update process datatable
        table = self.query_one("#process_table", DataTable)
        
        # Save current selected row key/index if possible
        selected_cell = table.cursor_coordinate

        table.clear()
        processes = self.get_processes()

        for p in processes[:100]:  # Limit display to top 100 processes
            table.add_row(
                str(p['pid']),
                p['name'] or "N/A",
                p['username'] or "N/A",
                f"{p['cpu_percent']:.1f}%" if p['cpu_percent'] is not None else "0.0%",
                f"{p['memory_percent']:.1f}%" if p['memory_percent'] is not None else "0.0%",
                p['status'] or "N/A",
                key=str(p['pid'])
            )

        if selected_cell and selected_cell.row < table.row_count:
            table.cursor_coordinate = selected_cell

    @on(Input.Changed, "#filter_input")
    def on_filter_changed(self) -> None:
        self.refresh_data()

    def action_focus_filter(self) -> None:
        self.query_one("#filter_input", Input).focus()

    def action_refresh_data(self) -> None:
        self.refresh_data()

    def _terminate_selected_process(self, sigkill: bool = False) -> None:
        table = self.query_one("#process_table", DataTable)
        if table.cursor_row is None:
            return

        # Fetch PID from key of the highlighted row
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        if not row_key or not row_key.value:
            return

        pid = int(row_key.value)
        try:
            p = psutil.Process(pid)
            if sigkill:
                p.kill()
                self.notify(f"Sent SIGKILL to PID {pid}", severity="error")
            else:
                p.terminate()
                self.notify(f"Sent SIGTERM to PID {pid}", severity="warning")
            self.refresh_data()
        except psutil.NoSuchProcess:
            self.notify(f"Process {pid} no longer exists.", severity="information")
        except psutil.AccessDenied:
            self.notify(f"Access denied to kill PID {pid}.", severity="error")

    def action_kill_process(self) -> None:
        self._terminate_selected_process(sigkill=False)

    def action_force_kill_process(self) -> None:
        self._terminate_selected_process(sigkill=True)

    @on(Button.Pressed, "#btn_kill")
    def on_btn_kill(self) -> None:
        self._terminate_selected_process(sigkill=False)

    @on(Button.Pressed, "#btn_fkill")
    def on_btn_fkill(self) -> None:
        self._terminate_selected_process(sigkill=True)


if __name__ == "__main__":
    app = PyTopApp()
    app.run()